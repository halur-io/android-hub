package com.sumo.printhub.print

import com.sumo.printhub.data.model.DeviceConfig
import com.sumo.printhub.data.model.Order
import com.sumo.printhub.data.model.OrderItem
import com.sumo.printhub.data.model.PrintAttemptResult
import com.sumo.printhub.data.model.PrinterInfo
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Decides which printer prints what for a single order, then dispatches the
 * bytes via [TcpPrinter]. Mirrors the Python agent's routing rules:
 *   1. The default printer prints `checker_copies` checker bons + `payment_copies` payment bons.
 *   2. Any items grouped under `items_by_station` are routed to that station's printer
 *      (falling back to the default printer if no station printer is mapped).
 */
@Singleton
class PrintOrchestrator @Inject constructor(
    private val tcp: TcpPrinter
) {

    suspend fun print(order: Order, config: DeviceConfig): PrintAttemptResult {
        val printersOk = mutableListOf<String>()
        val printersFailed = mutableListOf<String>()
        var anyAttempted = false
        var firstError: String? = null

        // ── Default printer: checker + payment bons ──
        val default = config.defaultPrinter
        if (default != null) {
            anyAttempted = true
            val combined = ByteArrayOutput()
            repeat(default.checkerCopies.coerceAtLeast(0)) {
                combined.write(BonBuilder.buildChecker(order, default))
            }
            repeat(default.paymentCopies.coerceAtLeast(0)) {
                combined.write(BonBuilder.buildPayment(order, default))
            }
            if (combined.size() > 0) {
                val res = tcp.send(default.ipAddress, default.port, combined.bytes())
                val tag = "${default.name}@${default.ipAddress}"
                if (res.ok) printersOk.add(tag)
                else {
                    printersFailed.add(tag)
                    firstError = firstError ?: res.error
                }
            }
        }

        // ── Station bons ──
        if (order.itemsByStation.isNotEmpty()) {
            val grouped = groupByPrinter(order.itemsByStation, config)
            for ((printer, stations) in grouped) {
                anyAttempted = true
                val combined = ByteArrayOutput()
                for ((stationName, items) in stations) {
                    combined.write(BonBuilder.buildStation(order, stationName, items, printer))
                }
                val res = tcp.send(printer.ipAddress, printer.port, combined.bytes())
                val tag = "${printer.name}@${printer.ipAddress}"
                if (res.ok) printersOk.add(tag)
                else {
                    printersFailed.add(tag)
                    firstError = firstError ?: res.error
                }
            }
        }

        if (!anyAttempted) {
            return PrintAttemptResult(
                success = false,
                printersOk = emptyList(),
                printersFailed = emptyList(),
                error = "No printers configured"
            )
        }

        return PrintAttemptResult(
            success = printersFailed.isEmpty(),
            printersOk = printersOk,
            printersFailed = printersFailed,
            error = firstError
        )
    }

    /**
     * Returns: printer -> (stationName -> items). Items destined for the same
     * physical printer are coalesced so we only open one TCP connection per
     * printer per order.
     */
    private fun groupByPrinter(
        itemsByStation: Map<String, List<OrderItem>>,
        config: DeviceConfig
    ): Map<PrinterInfo, Map<String, List<OrderItem>>> {
        val acc = LinkedHashMap<PrinterInfo, LinkedHashMap<String, List<OrderItem>>>()
        for ((station, items) in itemsByStation) {
            if (items.isEmpty()) continue
            val printer = config.stationMap[station] ?: config.defaultPrinter ?: continue
            val map = acc.getOrPut(printer) { LinkedHashMap() }
            map[station] = items
        }
        return acc
    }

    private class ByteArrayOutput {
        private val out = java.io.ByteArrayOutputStream()
        fun write(bytes: ByteArray) { out.write(bytes) }
        fun bytes(): ByteArray = out.toByteArray()
        fun size(): Int = out.size()
    }
}
