package com.sumo.printhub.print

import com.sumo.printhub.data.model.Order
import com.sumo.printhub.data.model.OrderItem
import com.sumo.printhub.data.model.PrinterInfo
import java.io.ByteArrayOutputStream
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * Builds ESC/POS byte sequences for the three bon types: checker (kitchen),
 * payment (receipt), and station (single-station kitchen ticket).
 *
 * Output format mirrors the legacy Python print agent (print_agent.py)
 * exactly so existing kitchens see no visual difference.
 */
class BonBuilder(
    private val encoding: String = "iso-8859-8",
    private val codepageNum: Int = 32,
    private val cutFeedLines: Int = 6
) {
    private val out = ByteArrayOutputStream(2048)

    fun bytes(): ByteArray = out.toByteArray()

    private fun add(b: ByteArray) { out.write(b) }
    private fun add(s: String) { out.write(HebrewPrinter.encode(s, encoding)) }

    fun init() {
        add(EscPos.INIT)
        add(EscPos.setCodepage(codepageNum))
    }

    fun cut() {
        repeat(cutFeedLines) { out.write('\n'.code) }
        add(EscPos.CUT_FULL)
    }

    fun align(a: Align) = add(when (a) {
        Align.Left -> EscPos.ALIGN_LEFT
        Align.Center -> EscPos.ALIGN_CENTER
        Align.Right -> EscPos.ALIGN_RIGHT
    })

    fun font(f: Font) = add(when (f) {
        Font.Normal -> EscPos.FONT_NORMAL
        Font.Double -> EscPos.FONT_DOUBLE
        Font.DoubleH -> EscPos.FONT_DOUBLE_H
        Font.DoubleW -> EscPos.FONT_DOUBLE_W
    })

    fun bold(on: Boolean) = add(if (on) EscPos.BOLD_ON else EscPos.BOLD_OFF)
    fun invert(on: Boolean) = add(if (on) EscPos.INVERT_ON else EscPos.INVERT_OFF)

    fun text(t: String) {
        add(t)
        out.write('\n'.code)
    }

    fun line(ch: Char = '-', width: Int = 42) {
        text(ch.toString().repeat(width))
    }
    fun dashed() = line('-')
    fun thick() = line('=')
    fun feed(n: Int = 1) { repeat(n) { out.write('\n'.code) } }

    enum class Align { Left, Center, Right }
    enum class Font { Normal, Double, DoubleH, DoubleW }

    companion object {
        private val timeFmt = SimpleDateFormat("HH:mm", Locale.US)
        private fun nowTime(): String = timeFmt.format(Date())

        fun buildChecker(order: Order, printer: PrinterInfo): ByteArray {
            val b = BonBuilder(printer.encoding, printer.codepageNum, printer.cutFeedLines)
            val orderNum = order.displayNumber ?: order.orderNumber
            val typeHe = if (order.orderType == "delivery") "משלוח" else "איסוף עצמי"
            val customer = order.customerName.orEmpty()
            val phone = order.customerPhone.orEmpty()

            b.init()
            b.align(Align.Right)
            b.font(Font.Normal)
            b.text("$phone  :טלפון")
            b.text("SUMO")
            b.dashed()

            b.bold(true)
            b.text("$customer - הזמנה $orderNum")
            b.bold(false)
            b.text(order.createdAt.orEmpty())
            b.feed(1)

            order.customerNotes?.takeIf { it.isNotBlank() }?.let {
                b.bold(true); b.text("הערות: $it"); b.bold(false)
            }
            order.deliveryNotes?.takeIf { it.isNotBlank() }?.let {
                b.bold(true); b.text("הערות משלוח: $it"); b.bold(false)
            }
            b.dashed()

            for (item in order.items) appendChecker(b, item)

            order.deliveryAddress?.takeIf { it.isNotBlank() }?.let { addr ->
                val full = if (!order.deliveryCity.isNullOrBlank()) "$addr, ${order.deliveryCity}" else addr
                b.align(Align.Right); b.font(Font.Normal); b.text("כתובת: $full"); b.dashed()
            }

            b.feed(1)
            b.align(Align.Center)
            b.font(Font.Double)
            b.invert(true)
            b.text(" SUMO - $orderNum ")
            b.invert(false)
            b.font(Font.Normal)

            b.feed(1)
            b.align(Align.Center)
            b.font(Font.Double)
            b.bold(true)
            b.text("*** $typeHe ***")
            b.bold(false)
            b.font(Font.Normal)

            b.feed(1)
            b.align(Align.Center)
            b.text("SUMO - $orderNum")
            b.text(phone)
            b.cut()
            return b.bytes()
        }

        private fun appendChecker(b: BonBuilder, item: OrderItem) {
            val name = item.displayName
            val qty = item.displayQty
            b.align(Align.Right)
            b.font(Font.DoubleH)
            b.bold(true)
            b.text("$name $qty")
            b.bold(false)
            b.font(Font.Normal)
            for (op in item.options) {
                val opName = op.displayName()
                if (opName.isNotBlank()) b.text(opName)
            }
            for (ex in item.excludedIngredients) {
                b.bold(true); b.text("ללא $ex"); b.bold(false)
            }
            b.dashed()
        }

        fun buildPayment(order: Order, printer: PrinterInfo): ByteArray {
            val b = BonBuilder(printer.encoding, printer.codepageNum, printer.cutFeedLines)
            val orderNum = order.displayNumber ?: order.orderNumber
            val typeHe = if (order.orderType == "delivery") "משלוח" else "איסוף עצמי"
            val customer = order.customerName.orEmpty()
            val phone = order.customerPhone.orEmpty()

            b.init()
            b.align(Align.Right)
            b.font(Font.Normal)
            b.text("$phone  :טלפון")
            b.text("SUMO - בון תשלום")
            b.dashed()

            b.bold(true); b.text("$customer - הזמנה $orderNum"); b.bold(false)
            b.text("$typeHe | ${order.createdAt.orEmpty()}")
            b.dashed()

            for (item in order.items) {
                val total = item.displayQty * item.displayPrice
                b.bold(true)
                b.text("${"%.0f".format(total)}  ${item.displayName} ${item.displayQty}")
                b.bold(false)
            }

            b.dashed()
            b.text("${"%.0f".format(order.subtotal)} :סכום")
            if (order.deliveryFee > 0) b.text("${"%.0f".format(order.deliveryFee)} :משלוח")
            if (order.discountAmount > 0) b.text("${"%.0f".format(order.discountAmount)}- :הנחה")
            b.thick()
            b.font(Font.Double); b.bold(true)
            b.text("${"%.0f".format(order.totalAmount)} :לתשלום")
            b.bold(false); b.font(Font.Normal)
            b.feed(1)
            b.align(Align.Center)
            b.text("תשלום: ${order.paymentMethod ?: "-"}")
            b.text(nowTime())
            b.cut()
            return b.bytes()
        }

        fun buildStation(
            order: Order,
            stationName: String,
            stationItems: List<OrderItem>,
            printer: PrinterInfo
        ): ByteArray {
            val b = BonBuilder(printer.encoding, printer.codepageNum, printer.cutFeedLines)
            val orderNum = order.displayNumber ?: order.orderNumber
            val typeHe = if (order.orderType == "delivery") "משלוח" else "איסוף עצמי"

            b.init()
            b.align(Align.Center)
            b.font(Font.Double); b.bold(true)
            b.text(stationName)
            b.bold(false); b.font(Font.Normal)
            b.text("$orderNum | ${order.createdAt.orEmpty()}")
            b.dashed()

            order.customerNotes?.takeIf { it.isNotBlank() }?.let {
                b.align(Align.Right); b.bold(true); b.text("הערות: $it"); b.bold(false)
            }

            for (item in stationItems) appendChecker(b, item)

            b.align(Align.Center)
            b.font(Font.Double); b.bold(true)
            b.text("*** $typeHe ***")
            b.bold(false); b.font(Font.Normal)
            b.text("$orderNum | $stationName | ${nowTime()}")
            b.cut()
            return b.bytes()
        }
    }
}
