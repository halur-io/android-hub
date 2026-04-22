package com.sumo.printhub.data.local

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Encrypted key/value store for credentials & first-launch config.
 * Hardcodes nothing besides the user-entered server URL + API key.
 */
@Singleton
class SecurePrefs @Inject constructor(ctx: Context) {

    private val prefs: SharedPreferences = run {
        val masterKey = MasterKey.Builder(ctx)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
        EncryptedSharedPreferences.create(
            ctx,
            "sumo_secure_prefs",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }

    fun getServerUrl(): String = prefs.getString(KEY_SERVER, "")?.trimEnd('/') ?: ""
    fun setServerUrl(url: String) = prefs.edit().putString(KEY_SERVER, url.trimEnd('/')).apply()

    fun getApiKey(): String = prefs.getString(KEY_API_KEY, "") ?: ""
    fun setApiKey(key: String) = prefs.edit().putString(KEY_API_KEY, key).apply()

    fun getBranchId(): Int = prefs.getInt(KEY_BRANCH, 0)
    fun setBranchId(branch: Int) = prefs.edit().putInt(KEY_BRANCH, branch).apply()

    fun getDeviceName(): String = prefs.getString(KEY_DEVICE_NAME, "") ?: ""
    fun setDeviceName(name: String) = prefs.edit().putString(KEY_DEVICE_NAME, name).apply()

    /** Stable per-installation device id, generated once. */
    fun getOrCreateDeviceId(): String {
        val existing = prefs.getString(KEY_DEVICE_ID, null)
        if (!existing.isNullOrBlank()) return existing
        val generated = "android-${UUID.randomUUID()}"
        prefs.edit().putString(KEY_DEVICE_ID, generated).apply()
        return generated
    }

    fun getDeviceDbId(): Int = prefs.getInt(KEY_DEVICE_DB_ID, 0)
    fun setDeviceDbId(id: Int) = prefs.edit().putInt(KEY_DEVICE_DB_ID, id).apply()

    fun isRegistered(): Boolean =
        getServerUrl().isNotBlank() && getApiKey().isNotBlank() &&
            getBranchId() > 0 && getDeviceDbId() > 0

    fun clear() = prefs.edit().clear().apply()

    companion object {
        private const val KEY_SERVER = "server_url"
        private const val KEY_API_KEY = "api_key"
        private const val KEY_BRANCH = "branch_id"
        private const val KEY_DEVICE_NAME = "device_name"
        private const val KEY_DEVICE_ID = "device_id"
        private const val KEY_DEVICE_DB_ID = "device_db_id"
    }
}
