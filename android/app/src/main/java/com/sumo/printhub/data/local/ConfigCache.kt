package com.sumo.printhub.data.local

import android.content.Context
import com.sumo.printhub.data.model.DeviceConfig
import kotlinx.serialization.json.Json
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Caches the latest device config so the app keeps working through brief
 * server outages or while offline.
 */
@Singleton
class ConfigCache @Inject constructor(
    private val ctx: Context,
    private val json: Json
) {
    private val prefs = ctx.getSharedPreferences("sumo_config_cache", Context.MODE_PRIVATE)

    fun load(): DeviceConfig? {
        val raw = prefs.getString(KEY_CONFIG, null) ?: return null
        return runCatching { json.decodeFromString(DeviceConfig.serializer(), raw) }.getOrNull()
    }

    fun save(config: DeviceConfig) {
        val raw = json.encodeToString(DeviceConfig.serializer(), config)
        prefs.edit().putString(KEY_CONFIG, raw).putLong(KEY_SAVED_AT, System.currentTimeMillis()).apply()
    }

    fun lastUpdatedMs(): Long = prefs.getLong(KEY_SAVED_AT, 0L)

    fun clear() = prefs.edit().clear().apply()

    private companion object {
        const val KEY_CONFIG = "config_json"
        const val KEY_SAVED_AT = "saved_at"
    }
}
