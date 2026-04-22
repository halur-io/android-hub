package com.sumo.printhub.ui.settings

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import com.sumo.printhub.data.local.ConfigCache
import com.sumo.printhub.data.local.SecurePrefs
import com.sumo.printhub.data.repository.PrintHubRepository
import com.sumo.printhub.service.PrintHubService
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject

@HiltViewModel
class SettingsViewModel @Inject constructor(
    application: Application,
    private val prefs: SecurePrefs,
    private val cache: ConfigCache,
    private val repository: PrintHubRepository
) : AndroidViewModel(application) {

    val serverUrl = MutableStateFlow(prefs.getServerUrl())
    val branchId = MutableStateFlow(prefs.getBranchId())
    val deviceName = MutableStateFlow(prefs.getDeviceName())
    val deviceId = MutableStateFlow(prefs.getOrCreateDeviceId())
    val deviceDbId = MutableStateFlow(prefs.getDeviceDbId())

    val config: StateFlow<com.sumo.printhub.data.model.DeviceConfig?> = repository.config

    fun unregister() {
        repository.stop()
        PrintHubService.stop(getApplication())
        prefs.clear()
        cache.clear()
    }
}
