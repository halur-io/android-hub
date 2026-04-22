package com.sumo.printhub.ui.dashboard

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sumo.printhub.data.local.SecurePrefs
import com.sumo.printhub.data.repository.PrintHubRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class DashboardViewModel @Inject constructor(
    val repository: PrintHubRepository,
    val prefs: SecurePrefs
) : ViewModel() {

    val status = repository.status
    val config = repository.config
    val printLog = repository.printLog
    val liveOrders = repository.liveOrders
    val ordersPrintedToday = repository.ordersPrintedToday
    val lastError = repository.lastError

    private val _testPrintInProgress = MutableStateFlow(false)
    val testPrintInProgress: StateFlow<Boolean> = _testPrintInProgress.asStateFlow()

    private val _testPrintMessage = MutableStateFlow<String?>(null)
    val testPrintMessage: StateFlow<String?> = _testPrintMessage.asStateFlow()

    fun refreshConfig() {
        viewModelScope.launch { repository.refreshConfigOnce() }
    }

    fun reprint(orderId: Int) {
        viewModelScope.launch { repository.refreshConfigOnce() }
    }

    fun sendTestPrint() {
        if (_testPrintInProgress.value) return
        _testPrintInProgress.value = true
        _testPrintMessage.value = null
        viewModelScope.launch {
            val result = repository.sendServerTestPrint()
            _testPrintMessage.value = when {
                result.success -> "✓ הדפסת בדיקה נשלחה (${result.printersOk.size} מדפסות)"
                result.printersOk.isNotEmpty() -> "⚠ הדפסה חלקית — נכשלו: ${result.printersFailed.joinToString()}"
                else -> "✗ הדפסה נכשלה: ${result.error ?: "לא ידוע"}"
            }
            _testPrintInProgress.value = false
        }
    }

    fun clearTestPrintMessage() { _testPrintMessage.value = null }
}
