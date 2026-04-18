package com.sumo.printhub.ui.dashboard

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sumo.printhub.data.local.SecurePrefs
import com.sumo.printhub.data.repository.PrintHubRepository
import dagger.hilt.android.lifecycle.HiltViewModel
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
    val ordersPrintedToday = repository.ordersPrintedToday
    val lastError = repository.lastError

    fun refreshConfig() {
        viewModelScope.launch { repository.refreshConfigOnce() }
    }

    fun reprint(orderId: Int) {
        // Reprint requires fetching the full order. The repository already
        // re-fetches via /unprinted; for a printed order we reuse the print log
        // entry to surface to the user, but we don't currently store the full
        // order body. This stub demonstrates intent — wire to a /detail call
        // when the server supports it for printed orders.
        viewModelScope.launch { repository.refreshConfigOnce() }
    }
}
