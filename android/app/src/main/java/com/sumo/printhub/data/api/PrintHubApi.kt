package com.sumo.printhub.data.api

import com.sumo.printhub.data.local.SecurePrefs
import com.sumo.printhub.data.model.DeviceConfigResponse
import com.sumo.printhub.data.model.DeviceRegisterRequest
import com.sumo.printhub.data.model.DeviceRegisterResponse
import com.sumo.printhub.data.model.GenericOk
import com.sumo.printhub.data.model.HeartbeatResponse
import com.sumo.printhub.data.model.PrintStatusRequest
import com.sumo.printhub.data.model.UnprintedOrdersResponse
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.builtins.ListSerializer
import kotlinx.serialization.builtins.serializer
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.put
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import javax.inject.Inject
import javax.inject.Singleton

private val JSON_MEDIA = "application/json; charset=utf-8".toMediaType()

@Singleton
class PrintHubApi @Inject constructor(
    private val http: OkHttpClient,
    private val json: Json,
    private val prefs: SecurePrefs
) {

    private fun base(): String = prefs.getServerUrl()
    private fun authHeader(): String = prefs.getApiKey()

    private fun newRequest(path: String): Request.Builder =
        Request.Builder()
            .url("${base()}$path")
            .header("X-Print-Key", authHeader())
            .header("Accept", "application/json")

    /** Registers (or re-registers) this tablet against the server. */
    suspend fun register(branchId: Int, deviceName: String): DeviceRegisterResponse =
        withContext(Dispatchers.IO) {
            val body = json.encodeToString(
                DeviceRegisterRequest.serializer(),
                DeviceRegisterRequest(prefs.getOrCreateDeviceId(), branchId, deviceName)
            ).toRequestBody(JSON_MEDIA)

            val req = newRequest("/ops/api/devices/register").post(body).build()
            http.newCall(req).execute().use { resp ->
                val text = resp.body?.string().orEmpty()
                if (!resp.isSuccessful) {
                    return@use DeviceRegisterResponse(ok = false, error = "HTTP ${resp.code}: $text")
                }
                runCatching { json.decodeFromString(DeviceRegisterResponse.serializer(), text) }
                    .getOrElse { DeviceRegisterResponse(ok = false, error = it.message) }
            }
        }

    suspend fun fetchConfig(deviceDbId: Int): DeviceConfigResponse =
        withContext(Dispatchers.IO) {
            val req = newRequest("/ops/api/devices/$deviceDbId/config").get().build()
            http.newCall(req).execute().use { resp ->
                val text = resp.body?.string().orEmpty()
                if (!resp.isSuccessful) {
                    return@use DeviceConfigResponse(ok = false, error = "HTTP ${resp.code}")
                }
                runCatching { json.decodeFromString(DeviceConfigResponse.serializer(), text) }
                    .getOrElse { DeviceConfigResponse(ok = false, error = it.message) }
            }
        }

    suspend fun heartbeat(): HeartbeatResponse = withContext(Dispatchers.IO) {
        val body = json.encodeToString(
            JsonObject.serializer(),
            buildJsonObject { put("device_id", prefs.getOrCreateDeviceId()) }
        ).toRequestBody(JSON_MEDIA)
        val req = newRequest("/ops/api/devices/heartbeat").post(body).build()
        http.newCall(req).execute().use { resp ->
            val text = resp.body?.string().orEmpty()
            if (!resp.isSuccessful) HeartbeatResponse(ok = false)
            else runCatching { json.decodeFromString(HeartbeatResponse.serializer(), text) }
                .getOrElse { HeartbeatResponse(ok = false) }
        }
    }

    suspend fun fetchUnprinted(branchId: Int): UnprintedOrdersResponse =
        withContext(Dispatchers.IO) {
            val req = newRequest("/ops/api/orders/unprinted?branch_id=$branchId").get().build()
            http.newCall(req).execute().use { resp ->
                val text = resp.body?.string().orEmpty()
                if (!resp.isSuccessful) UnprintedOrdersResponse(ok = false)
                else runCatching { json.decodeFromString(UnprintedOrdersResponse.serializer(), text) }
                    .getOrElse { UnprintedOrdersResponse(ok = false) }
            }
        }

    suspend fun ackOrder(orderId: Int): GenericOk = withContext(Dispatchers.IO) {
        val body = json.encodeToString(
            JsonObject.serializer(),
            buildJsonObject { put("device_id", prefs.getOrCreateDeviceId()) }
        ).toRequestBody(JSON_MEDIA)
        val req = newRequest("/ops/api/orders/$orderId/ack").post(body).build()
        http.newCall(req).execute().use { resp ->
            val text = resp.body?.string().orEmpty()
            if (!resp.isSuccessful) GenericOk(ok = false, error = "HTTP ${resp.code}")
            else runCatching { json.decodeFromString(GenericOk.serializer(), text) }
                .getOrElse { GenericOk(ok = false, error = it.message) }
        }
    }

    suspend fun reportPrintStatus(orderId: Int, payload: PrintStatusRequest): GenericOk =
        withContext(Dispatchers.IO) {
            val body = json.encodeToString(PrintStatusRequest.serializer(), payload)
                .toRequestBody(JSON_MEDIA)
            val req = newRequest("/ops/api/orders/$orderId/print-status").post(body).build()
            http.newCall(req).execute().use { resp ->
                val text = resp.body?.string().orEmpty()
                if (!resp.isSuccessful) GenericOk(ok = false, error = "HTTP ${resp.code}")
                else runCatching { json.decodeFromString(GenericOk.serializer(), text) }
                    .getOrElse { GenericOk(ok = false, error = it.message) }
            }
        }

    suspend fun markPrinted(orderIds: List<Int>): GenericOk = withContext(Dispatchers.IO) {
        val body = json.encodeToString(
            JsonObject.serializer(),
            buildJsonObject {
                put(
                    "order_ids",
                    json.encodeToJsonElement(
                        ListSerializer(Int.serializer()),
                        orderIds
                    )
                )
            }
        ).toRequestBody(JSON_MEDIA)
        val req = newRequest("/ops/api/orders/mark-printed").post(body).build()
        http.newCall(req).execute().use { resp ->
            val text = resp.body?.string().orEmpty()
            if (!resp.isSuccessful) GenericOk(ok = false, error = "HTTP ${resp.code}")
            else runCatching { json.decodeFromString(GenericOk.serializer(), text) }
                .getOrElse { GenericOk(ok = false, error = it.message) }
        }
    }

    suspend fun logError(errorType: String, message: String, stack: String? = null): GenericOk =
        withContext(Dispatchers.IO) {
            val payload = buildJsonObject {
                put("device_id", JsonPrimitive(prefs.getOrCreateDeviceId()))
                put("error_type", JsonPrimitive(errorType))
                put("error_message", JsonPrimitive(message))
                if (!stack.isNullOrBlank()) put("stack_trace", JsonPrimitive(stack))
            }
            val body = json.encodeToString(JsonObject.serializer(), payload).toRequestBody(JSON_MEDIA)
            val req = newRequest("/ops/api/device/log-error").post(body).build()
            runCatching {
                http.newCall(req).execute().use { resp ->
                    if (resp.isSuccessful) GenericOk(ok = true)
                    else GenericOk(ok = false, error = "HTTP ${resp.code}")
                }
            }.getOrElse { GenericOk(ok = false, error = it.message) }
        }
}
