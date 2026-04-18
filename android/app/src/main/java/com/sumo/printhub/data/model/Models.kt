package com.sumo.printhub.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonElement

@Serializable
data class OptionEntry(
    @SerialName("choice_name_he") val choiceNameHe: String? = null,
    val name: String? = null
) {
    fun displayName(): String = choiceNameHe ?: name ?: ""
}

@Serializable
data class OrderItem(
    @SerialName("menu_item_id") val menuItemId: Int? = null,
    @SerialName("name_he") val nameHe: String? = null,
    @SerialName("item_name_he") val itemNameHe: String? = null,
    val name: String? = null,
    @SerialName("print_name") val printName: String? = null,
    val qty: Int? = null,
    val quantity: Int? = null,
    val price: Double? = null,
    @SerialName("unit_price") val unitPrice: Double? = null,
    val options: List<OptionEntry> = emptyList(),
    @SerialName("excluded_ingredients") val excludedIngredients: List<String> = emptyList()
) {
    val displayName: String get() = printName ?: nameHe ?: itemNameHe ?: name ?: ""
    val displayQty: Int get() = qty ?: quantity ?: 1
    val displayPrice: Double get() = price ?: unitPrice ?: 0.0
}

@Serializable
data class Order(
    val id: Int,
    @SerialName("order_number") val orderNumber: String,
    @SerialName("display_number") val displayNumber: String? = null,
    @SerialName("order_type") val orderType: String,
    val status: String? = null,
    @SerialName("branch_id") val branchId: Int? = null,
    @SerialName("customer_name") val customerName: String? = "",
    @SerialName("customer_phone") val customerPhone: String? = "",
    @SerialName("delivery_address") val deliveryAddress: String? = "",
    @SerialName("delivery_city") val deliveryCity: String? = "",
    @SerialName("delivery_notes") val deliveryNotes: String? = "",
    @SerialName("customer_notes") val customerNotes: String? = "",
    val subtotal: Double = 0.0,
    @SerialName("delivery_fee") val deliveryFee: Double = 0.0,
    @SerialName("discount_amount") val discountAmount: Double = 0.0,
    @SerialName("total_amount") val totalAmount: Double = 0.0,
    @SerialName("payment_method") val paymentMethod: String? = "",
    @SerialName("coupon_code") val couponCode: String? = "",
    @SerialName("created_at") val createdAt: String? = "",
    val items: List<OrderItem> = emptyList(),
    @SerialName("items_by_station") val itemsByStation: Map<String, List<OrderItem>> = emptyMap()
)

@Serializable
data class UnprintedOrdersResponse(val ok: Boolean = false, val orders: List<Order> = emptyList())

@Serializable
data class DeviceRegisterRequest(
    @SerialName("device_id") val deviceId: String,
    @SerialName("branch_id") val branchId: Int,
    @SerialName("device_name") val deviceName: String
)

@Serializable
data class PrintDeviceDto(
    val id: Int,
    @SerialName("device_id") val deviceId: String,
    @SerialName("branch_id") val branchId: Int,
    @SerialName("device_name") val deviceName: String,
    @SerialName("last_heartbeat") val lastHeartbeat: String? = null,
    @SerialName("is_online") val isOnline: Boolean = false,
    val config: JsonElement? = null
)

@Serializable
data class DeviceRegisterResponse(val ok: Boolean = false, val device: PrintDeviceDto? = null, val error: String? = null)

/**
 * Printer descriptor as returned by the server. Only routing/display fields
 * are kept on the client — encoding, codepage, RTL handling and bon layout
 * are all server-rendered, so the client never needs to know about them.
 */
@Serializable
data class PrinterInfo(
    val id: Int,
    val name: String,
    @SerialName("ip_address") val ipAddress: String,
    val port: Int = 9100,
    @SerialName("is_default") val isDefault: Boolean = false,
    val stations: List<String> = emptyList()
)

@Serializable
data class DeviceConfig(
    @SerialName("device_id") val deviceId: String? = null,
    @SerialName("device_db_id") val deviceDbId: Int? = null,
    @SerialName("branch_id") val branchId: Int? = null,
    @SerialName("branch_name") val branchName: String? = null,
    @SerialName("poll_interval_seconds") val pollIntervalSeconds: Int = 5,
    @SerialName("sse_reconnect_delay_ms") val sseReconnectDelayMs: Int = 3000,
    @SerialName("heartbeat_interval_seconds") val heartbeatIntervalSeconds: Int = 30,
    @SerialName("sound_enabled") val soundEnabled: Boolean = true,
    @SerialName("sound_file") val soundFile: String? = null,
    @SerialName("notification_enabled") val notificationEnabled: Boolean = true,
    @SerialName("default_printer") val defaultPrinter: PrinterInfo? = null,
    @SerialName("station_map") val stationMap: Map<String, PrinterInfo> = emptyMap(),
    val printers: List<PrinterInfo> = emptyList()
)

@Serializable
data class DeviceConfigResponse(val ok: Boolean = false, val config: DeviceConfig? = null, val error: String? = null)

@Serializable
data class HeartbeatResponse(val ok: Boolean = false, @SerialName("server_time") val serverTime: String? = null)

@Serializable
data class GenericOk(val ok: Boolean = false, val error: String? = null, val message: String? = null)

@Serializable
data class PrintStatusRequest(
    val status: String,
    @SerialName("device_id") val deviceId: String? = null,
    @SerialName("printers_ok") val printersOk: List<String> = emptyList(),
    @SerialName("printers_failed") val printersFailed: List<String> = emptyList(),
    val error: String? = null
)

@Serializable
data class SseEvent(
    val type: String,
    val id: Int? = null,
    @SerialName("order_number") val orderNumber: String? = null,
    @SerialName("order_type") val orderType: String? = null,
    @SerialName("branch_id") val branchId: Int? = null,
    @SerialName("customer_name") val customerName: String? = null,
    @SerialName("total_amount") val totalAmount: Double? = null,
    @SerialName("items_count") val itemsCount: Int? = null,
    @SerialName("old_status") val oldStatus: String? = null,
    @SerialName("new_status") val newStatus: String? = null,
    @SerialName("created_at") val createdAt: String? = null,
    @SerialName("updated_at") val updatedAt: String? = null
)

/**
 * A single ready-to-send print job as rendered by the server. `rawData` is
 * the base64-encoded ESC/POS byte buffer — everything (RTL, codepage,
 * encoding) is already baked in. The relay just decodes and writes it.
 */
@Serializable
data class PrintJobBytes(
    @SerialName("bon_type") val bonType: String,
    @SerialName("station_name") val stationName: String? = null,
    @SerialName("printer_id") val printerId: Int? = null,
    @SerialName("printer_name") val printerName: String = "",
    @SerialName("printer_ip") val printerIp: String,
    @SerialName("printer_port") val printerPort: Int = 9100,
    @SerialName("order_id") val orderId: Int = 0,
    @SerialName("order_number") val orderNumber: String? = null,
    @SerialName("display_number") val displayNumber: String? = null,
    @SerialName("raw_data") val rawData: String
) {
    val printerLabel: String get() = if (printerName.isNotBlank()) "$printerName@$printerIp" else printerIp
}

@Serializable
data class OrderPrintEnvelope(
    val ok: Boolean = false,
    val error: String? = null,
    val order: OrderHeader? = null,
    val jobs: List<PrintJobBytes> = emptyList()
)

@Serializable
data class OrderHeader(
    val id: Int = 0,
    @SerialName("order_number") val orderNumber: String? = null,
    @SerialName("display_number") val displayNumber: String? = null,
    @SerialName("order_type") val orderType: String? = null,
    @SerialName("branch_id") val branchId: Int? = null
)

@Serializable
data class TestPrintResponse(
    val ok: Boolean = false,
    val error: String? = null,
    val message: String? = null,
    val jobs: List<PrintJobBytes> = emptyList()
)

data class PrintAttemptResult(
    val success: Boolean,
    val printersOk: List<String>,
    val printersFailed: List<String>,
    val error: String? = null
) {
    val statusForServer: String
        get() = when {
            printersFailed.isEmpty() -> "success"
            printersOk.isEmpty() -> "failed"
            else -> "partial"
        }
}
