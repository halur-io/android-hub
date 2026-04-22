package com.sumo.printhub.data.repository

import android.util.Base64
import android.util.Log
import com.sumo.printhub.data.api.PrintHubApi
import com.sumo.printhub.data.api.SseClient
import com.sumo.printhub.data.api.SseStreamEvent
import com.sumo.printhub.data.local.ConfigCache
import com.sumo.printhub.data.local.SecurePrefs
import com.sumo.printhub.data.model.DeviceConfig
import com.sumo.printhub.data.model.Order
import com.sumo.printhub.data.model.PrintAttemptResult
import com.sumo.printhub.data.model.PrintJobBytes
import com.sumo.printhub.data.model.PrintStatusRequest
import com.sumo.printhub.print.TcpRelay
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import javax.inject.Inject
import javax.inject.Singleton

private const val TAG = "PrintHubRepo"
private const val DEDUPE_TTL_MS = 120_000L

/**
 * Single source of truth for runtime state. Owns:
 *   - SSE long-lived connection (with reconnect/backoff)
 *   - Polling fallback when SSE is down
 *   - Config refresh
 *   - Heartbeat
 *   - Order printing pipeline (ack -> fetch server-rendered bytes -> relay -> report)
 *
 * NB: This client never builds bons. For each new order it asks the server
 * for `/ops/api/orders/<id>/print-payload`, which returns base64-encoded
 * ESC/POS bytes per printer. The relay just writes them to the printer.
 */
@Singleton
class PrintHubRepository @Inject constructor(
    private val api: PrintHubApi,
    private val sse: SseClient,
    private val prefs: SecurePrefs,
    private val cache: ConfigCache,
    private val relay: TcpRelay
) {

    enum class ConnectionStatus { Disconnected, Connecting, Online, Polling, Offline }

    enum class PrintStatus { Incoming, Printing, Printed, Partial, Failed }

    data class LiveOrderEntry(
        val ts: Long,
        val order: Order,
        val printStatus: PrintStatus,
        val printersOk: List<String> = emptyList(),
        val printersFailed: List<String> = emptyList(),
        val error: String? = null
    ) {
        val displayNumber: String get() = order.displayNumber ?: order.orderNumber
        val customerLabel: String get() = order.customerName?.takeIf { it.isNotBlank() } ?: ""
        val itemCount: Int get() = order.items.size
        val typeLabel: String get() = when (order.orderType) {
            "delivery" -> "Delivery"
            "pickup"   -> "Pickup"
            "dine_in"  -> "Dine-in"
            else       -> order.orderType.replaceFirstChar { it.uppercase() }
        }
    }

    data class PrintLogEntry(
        val ts: Long,
        val orderId: Int,
        val orderNumber: String,
        val displayNumber: String?,
        val outcome: String,
        val printersOk: List<String>,
        val printersFailed: List<String>,
        val error: String? = null
    )

    private val _status = MutableStateFlow(ConnectionStatus.Disconnected)
    val status: StateFlow<ConnectionStatus> = _status.asStateFlow()

    private val _config = MutableStateFlow<DeviceConfig?>(null)
    val config: StateFlow<DeviceConfig?> = _config.asStateFlow()

    private val _newOrderEvents = MutableSharedFlow<Order>(extraBufferCapacity = 32)
    val newOrderEvents: SharedFlow<Order> = _newOrderEvents.asSharedFlow()

    private val _printLog = MutableStateFlow<List<PrintLogEntry>>(emptyList())
    val printLog: StateFlow<List<PrintLogEntry>> = _printLog.asStateFlow()

    private val _liveOrders = MutableStateFlow<List<LiveOrderEntry>>(emptyList())
    val liveOrders: StateFlow<List<LiveOrderEntry>> = _liveOrders.asStateFlow()

    private val _ordersPrintedToday = MutableStateFlow(0)
    val ordersPrintedToday: StateFlow<Int> = _ordersPrintedToday.asStateFlow()

    private val _lastError = MutableStateFlow<String?>(null)
    val lastError: StateFlow<String?> = _lastError.asStateFlow()

    private val processedIds = mutableMapOf<Int, Long>()
    private val processedMutex = Mutex()
    private val printMutex = Mutex()

    private var sseJob: Job? = null
    private var pollJob: Job? = null
    private var heartbeatJob: Job? = null
    private var configJob: Job? = null

    init {
        cache.load()?.let { _config.value = it }
    }

    fun start(scope: CoroutineScope) {
        if (sseJob?.isActive == true) return
        scope.launch(Dispatchers.IO) { configRefreshLoop(this) }
        scope.launch(Dispatchers.IO) { heartbeatLoop(this) }
        scope.launch(Dispatchers.IO) { sseLoop(this) }
    }

    fun stop() {
        sseJob?.cancel(); sseJob = null
        pollJob?.cancel(); pollJob = null
        heartbeatJob?.cancel(); heartbeatJob = null
        configJob?.cancel(); configJob = null
        _status.value = ConnectionStatus.Disconnected
    }

    suspend fun refreshConfigOnce(): DeviceConfig? {
        val deviceId = prefs.getDeviceDbId()
        if (deviceId <= 0) return null
        val resp = api.fetchConfig(deviceId)
        return if (resp.ok && resp.config != null) {
            cache.save(resp.config)
            _config.value = resp.config
            resp.config
        } else {
            _lastError.value = resp.error
            null
        }
    }

    private suspend fun configRefreshLoop(scope: CoroutineScope) {
        refreshConfigOnce()
        while (scope.isActive) {
            delay(5 * 60_000L)
            runCatching { refreshConfigOnce() }
        }
    }

    private suspend fun heartbeatLoop(scope: CoroutineScope) {
        while (scope.isActive) {
            val interval = (_config.value?.heartbeatIntervalSeconds ?: 30).coerceAtLeast(5) * 1000L
            runCatching { api.heartbeat() }
            delay(interval)
        }
    }

    private suspend fun sseLoop(scope: CoroutineScope) {
        val branch = prefs.getBranchId()
        if (branch <= 0) return

        while (scope.isActive) {
            _status.value = ConnectionStatus.Connecting
            var sawOpen = false
            try {
                sse.stream(branch).collect { evt ->
                    when (evt) {
                        SseStreamEvent.Open -> {
                            sawOpen = true
                            _status.value = ConnectionStatus.Online
                            stopPollingLoop()
                            scope.launch { drainUnprintedOrders() }
                        }
                        is SseStreamEvent.Message -> {
                            val type = evt.event.type
                            if (type == "new_order" && evt.event.id != null) {
                                scope.launch { handleNewOrderById(evt.event.id) }
                            }
                        }
                        is SseStreamEvent.Failure -> {
                            Log.w(TAG, "SSE failure: ${evt.code} ${evt.throwable?.message}")
                            throw RuntimeException("SSE failure ${evt.code}", evt.throwable)
                        }
                        SseStreamEvent.Closed -> {
                            throw RuntimeException("SSE closed")
                        }
                    }
                }
            } catch (t: Throwable) {
                if (!scope.isActive) return
                Log.w(TAG, "SSE loop error: ${t.message}")
                _lastError.value = t.message
            }

            _status.value = ConnectionStatus.Polling
            startPollingLoop(scope)

            val delayMs = (_config.value?.sseReconnectDelayMs ?: 3000).coerceAtLeast(1000).toLong()
            if (!sawOpen) delay(delayMs * 2) else delay(delayMs)
        }
    }

    private fun startPollingLoop(scope: CoroutineScope) {
        if (pollJob?.isActive == true) return
        pollJob = scope.launch(Dispatchers.IO) {
            while (isActive) {
                drainUnprintedOrders()
                val interval = (_config.value?.pollIntervalSeconds ?: 5).coerceAtLeast(2) * 1000L
                delay(interval)
            }
        }
    }

    private fun stopPollingLoop() {
        pollJob?.cancel()
        pollJob = null
    }

    private suspend fun drainUnprintedOrders() {
        val branch = prefs.getBranchId()
        if (branch <= 0) return
        val resp = runCatching { api.fetchUnprinted(branch) }.getOrNull() ?: return
        if (!resp.ok) return
        for (order in resp.orders) {
            handleOrder(order)
        }
    }

    private suspend fun handleNewOrderById(id: Int) {
        val branch = prefs.getBranchId()
        if (branch <= 0) return
        val resp = runCatching { api.fetchUnprinted(branch) }.getOrNull() ?: return
        if (!resp.ok) return
        resp.orders.firstOrNull { it.id == id }?.let { handleOrder(it) }
    }

    private fun upsertLiveOrder(entry: LiveOrderEntry) {
        val current = _liveOrders.value.toMutableList()
        val idx = current.indexOfFirst { it.order.id == entry.order.id }
        if (idx >= 0) current[idx] = entry else current.add(0, entry)
        _liveOrders.value = current.take(50)
    }

    private suspend fun handleOrder(order: Order) {
        val now = System.currentTimeMillis()
        processedMutex.withLock {
            processedIds.entries.removeAll { now - it.value > DEDUPE_TTL_MS }
            if (processedIds.containsKey(order.id)) return
            processedIds[order.id] = now
        }

        _newOrderEvents.tryEmit(order)

        // Show as "Incoming" immediately so the operator sees it right away.
        upsertLiveOrder(LiveOrderEntry(ts = now, order = order, printStatus = PrintStatus.Incoming))

        // Acknowledge first so the dashboard turns blue.
        runCatching { api.ackOrder(order.id) }

        // Mark as actively printing.
        upsertLiveOrder(LiveOrderEntry(ts = now, order = order, printStatus = PrintStatus.Printing))

        printMutex.withLock {
            val result = printOrderViaServerPayload(order.id)
            recordPrintLog(order, result)

            // Update live entry with final outcome.
            val finalStatus = when {
                result.success -> PrintStatus.Printed
                result.printersOk.isNotEmpty() -> PrintStatus.Partial
                else -> PrintStatus.Failed
            }
            upsertLiveOrder(
                LiveOrderEntry(
                    ts = now,
                    order = order,
                    printStatus = finalStatus,
                    printersOk = result.printersOk,
                    printersFailed = result.printersFailed,
                    error = result.error
                )
            )

            runCatching {
                api.reportPrintStatus(
                    order.id,
                    PrintStatusRequest(
                        status = result.statusForServer,
                        deviceId = prefs.getOrCreateDeviceId(),
                        printersOk = result.printersOk,
                        printersFailed = result.printersFailed,
                        error = result.error
                    )
                )
            }
            if (result.success) {
                runCatching { api.markPrinted(listOf(order.id)) }
                _ordersPrintedToday.value = _ordersPrintedToday.value + 1
            }
        }
    }

    /**
     * Fetch the server-rendered payload for an order and relay each job to
     * its printer. Jobs targeting the same printer are coalesced into a
     * single TCP send to avoid extra socket churn.
     */
    private suspend fun printOrderViaServerPayload(orderId: Int): PrintAttemptResult {
        val resp = runCatching { api.fetchPrintPayload(orderId) }.getOrNull()
        if (resp == null || !resp.ok) {
            return PrintAttemptResult(
                success = false,
                printersOk = emptyList(),
                printersFailed = emptyList(),
                error = resp?.error ?: "Failed to fetch print payload"
            )
        }
        if (resp.jobs.isEmpty()) {
            return PrintAttemptResult(
                success = false,
                printersOk = emptyList(),
                printersFailed = emptyList(),
                error = "No printers configured for this branch"
            )
        }
        return relayJobs(resp.jobs)
    }

    /** Coalesces jobs by (ip,port) so each printer gets one socket per batch. */
    private suspend fun relayJobs(jobs: List<PrintJobBytes>): PrintAttemptResult {
        val printersOk = mutableListOf<String>()
        val printersFailed = mutableListOf<String>()
        var firstError: String? = null

        val grouped = LinkedHashMap<Pair<String, Int>, Pair<String, java.io.ByteArrayOutputStream>>()
        for (job in jobs) {
            val key = job.printerIp to job.printerPort
            val acc = grouped.getOrPut(key) { job.printerLabel to java.io.ByteArrayOutputStream() }
            try {
                acc.second.write(Base64.decode(job.rawData, Base64.DEFAULT))
            } catch (t: Throwable) {
                Log.e(TAG, "Failed to decode print job for ${job.printerLabel}: ${t.message}")
                firstError = firstError ?: "Decode error: ${t.message}"
            }
        }

        for ((key, value) in grouped) {
            val (label, buf) = value
            val (ip, port) = key
            val res = relay.send(ip, port, buf.toByteArray())
            if (res.ok) printersOk.add(label)
            else {
                printersFailed.add(label)
                firstError = firstError ?: res.error
            }
        }

        return PrintAttemptResult(
            success = printersFailed.isEmpty() && printersOk.isNotEmpty(),
            printersOk = printersOk,
            printersFailed = printersFailed,
            error = firstError
        )
    }

    private fun recordPrintLog(order: Order, result: PrintAttemptResult) {
        val entry = PrintLogEntry(
            ts = System.currentTimeMillis(),
            orderId = order.id,
            orderNumber = order.orderNumber,
            displayNumber = order.displayNumber,
            outcome = result.statusForServer,
            printersOk = result.printersOk,
            printersFailed = result.printersFailed,
            error = result.error
        )
        val updated = (listOf(entry) + _printLog.value).take(100)
        _printLog.value = updated
    }

    /** Manual reprint from the dashboard. */
    suspend fun reprintOrder(order: Order): PrintAttemptResult {
        val result = printMutex.withLock { printOrderViaServerPayload(order.id) }
        recordPrintLog(order, result)
        return result
    }

    /**
     * Trigger a server-rendered test print. Asks the server for a small
     * test envelope and relays it to every printer in the branch. This is
     * the same path a real order takes, so a successful test confirms the
     * end-to-end pipeline (server render → relay → printer).
     */
    suspend fun sendServerTestPrint(): PrintAttemptResult {
        val deviceDbId = prefs.getDeviceDbId()
        if (deviceDbId <= 0) {
            return PrintAttemptResult(false, emptyList(), emptyList(), "Device not registered")
        }
        val resp = runCatching { api.sendTestPrint(deviceDbId) }.getOrNull()
        if (resp == null || !resp.ok) {
            return PrintAttemptResult(false, emptyList(), emptyList(), resp?.error ?: "Server rejected test print")
        }
        if (resp.jobs.isEmpty()) {
            return PrintAttemptResult(false, emptyList(), emptyList(), resp.message ?: "No printers configured")
        }
        val result = printMutex.withLock { relayJobs(resp.jobs) }
        // Surface to the print log so the user can see the result.
        val placeholder = Order(
            id = 0,
            orderNumber = "TEST",
            displayNumber = "TEST",
            orderType = "test"
        )
        recordPrintLog(placeholder, result)
        return result
    }
}
