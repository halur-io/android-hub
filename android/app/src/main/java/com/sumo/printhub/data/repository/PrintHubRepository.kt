package com.sumo.printhub.data.repository

import android.util.Log
import com.sumo.printhub.data.api.PrintHubApi
import com.sumo.printhub.data.api.SseClient
import com.sumo.printhub.data.api.SseStreamEvent
import com.sumo.printhub.data.local.ConfigCache
import com.sumo.printhub.data.local.SecurePrefs
import com.sumo.printhub.data.model.DeviceConfig
import com.sumo.printhub.data.model.Order
import com.sumo.printhub.data.model.PrintAttemptResult
import com.sumo.printhub.data.model.PrintStatusRequest
import com.sumo.printhub.print.PrintOrchestrator
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
 *   - Order printing pipeline (ack -> build -> print -> report)
 */
@Singleton
class PrintHubRepository @Inject constructor(
    private val api: PrintHubApi,
    private val sse: SseClient,
    private val prefs: SecurePrefs,
    private val cache: ConfigCache,
    private val orchestrator: PrintOrchestrator
) {

    enum class ConnectionStatus { Disconnected, Connecting, Online, Polling, Offline }

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
        // First refresh fast, then every 5 minutes.
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

    /**
     * Maintains a single SSE connection. On failure, reports Polling status,
     * starts the polling loop, and reconnects after the configured delay.
     */
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
                            // Catch any orders we missed while disconnected.
                            scope.launch { drainUnprintedOrders() }
                        }
                        is SseStreamEvent.Message -> {
                            val type = evt.event.type
                            if (type == "new_order" && evt.event.id != null) {
                                scope.launch { handleNewOrderById(evt.event.id) }
                            }
                            // order_status_changed is informational for the dashboard;
                            // printing only happens for new_order.
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

            // Drop into polling fallback while we wait to reconnect.
            _status.value = ConnectionStatus.Polling
            startPollingLoop(scope)

            val delayMs = (_config.value?.sseReconnectDelayMs ?: 3000).coerceAtLeast(1000).toLong()
            if (!sawOpen) {
                // First attempt failed; back off slightly more.
                delay(delayMs * 2)
            } else {
                delay(delayMs)
            }
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
        // Pull from /unprinted to get the full record.
        val branch = prefs.getBranchId()
        if (branch <= 0) return
        val resp = runCatching { api.fetchUnprinted(branch) }.getOrNull() ?: return
        if (!resp.ok) return
        resp.orders.firstOrNull { it.id == id }?.let { handleOrder(it) }
    }

    private suspend fun handleOrder(order: Order) {
        // Per-id dedupe with TTL so a flapping SSE/poll combo can't double-print.
        val now = System.currentTimeMillis()
        processedMutex.withLock {
            processedIds.entries.removeAll { now - it.value > DEDUPE_TTL_MS }
            if (processedIds.containsKey(order.id)) return
            processedIds[order.id] = now
        }

        _newOrderEvents.tryEmit(order)

        val cfg = _config.value
        if (cfg == null) {
            Log.w(TAG, "No config loaded; cannot print order ${order.id}")
            return
        }

        // Acknowledge first so the dashboard turns blue.
        runCatching { api.ackOrder(order.id) }

        printMutex.withLock {
            val result = orchestrator.print(order, cfg)
            recordPrintLog(order, result)
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

    /** Manual reprint from the dashboard (e.g. last failed order). */
    suspend fun reprintOrder(order: Order): PrintAttemptResult {
        val cfg = _config.value ?: return PrintAttemptResult(false, emptyList(), emptyList(), "No config")
        val result = printMutex.withLock { orchestrator.print(order, cfg) }
        recordPrintLog(order, result)
        return result
    }
}
