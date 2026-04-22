package com.sumo.printhub.ui.setup

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.sumo.printhub.data.api.PrintHubApi
import com.sumo.printhub.data.local.SecurePrefs
import com.sumo.printhub.data.repository.PrintHubRepository
import com.sumo.printhub.service.PrintHubService
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class SetupUiState(
    val serverUrl: String = "",
    val apiKey: String = "",
    val branchId: String = "",
    val deviceName: String = "",
    val submitting: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class SetupViewModel @Inject constructor(
    application: Application,
    private val prefs: SecurePrefs,
    private val api: PrintHubApi,
    private val repository: PrintHubRepository
) : AndroidViewModel(application) {

    private val _state = MutableStateFlow(
        SetupUiState(
            serverUrl = prefs.getServerUrl(),
            apiKey = prefs.getApiKey(),
            branchId = prefs.getBranchId().takeIf { it > 0 }?.toString().orEmpty(),
            deviceName = prefs.getDeviceName().ifBlank { android.os.Build.MODEL ?: "Tablet" }
        )
    )
    val state: StateFlow<SetupUiState> = _state.asStateFlow()

    private val _isRegistered = MutableStateFlow(prefs.isRegistered())
    val isRegistered: StateFlow<Boolean> = _isRegistered.asStateFlow()

    fun update(transform: (SetupUiState) -> SetupUiState) {
        _state.value = transform(_state.value)
    }

    fun submit(onSuccess: () -> Unit) {
        val s = _state.value
        val branch = s.branchId.toIntOrNull()
        if (s.serverUrl.isBlank() || s.apiKey.isBlank() || branch == null || branch <= 0 || s.deviceName.isBlank()) {
            _state.value = s.copy(error = "Please fill all fields (branch must be a positive number).")
            return
        }
        _state.value = s.copy(submitting = true, error = null)

        // Persist locally before the network call so the API helper picks them up.
        prefs.setServerUrl(s.serverUrl)
        prefs.setApiKey(s.apiKey)
        prefs.setBranchId(branch)
        prefs.setDeviceName(s.deviceName)

        viewModelScope.launch {
            val resp = api.register(branch, s.deviceName)
            if (!resp.ok || resp.device == null) {
                _state.value = _state.value.copy(submitting = false, error = resp.error ?: "Registration failed")
                return@launch
            }
            prefs.setDeviceDbId(resp.device.id)

            // Pull config so the dashboard has it instantly.
            repository.refreshConfigOnce()

            _isRegistered.value = true
            _state.value = _state.value.copy(submitting = false)
            PrintHubService.start(getApplication())
            onSuccess()
        }
    }
}
