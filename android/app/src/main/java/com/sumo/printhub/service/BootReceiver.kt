package com.sumo.printhub.service

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import com.sumo.printhub.data.local.SecurePrefs
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

/**
 * Restarts the print service when the device boots so the kitchen never has
 * to remember to open the app after a reboot.
 */
@AndroidEntryPoint
class BootReceiver : BroadcastReceiver() {

    @Inject lateinit var prefs: SecurePrefs

    override fun onReceive(context: Context, intent: Intent?) {
        val action = intent?.action ?: return
        if (action != Intent.ACTION_BOOT_COMPLETED && action != Intent.ACTION_LOCKED_BOOT_COMPLETED) return
        if (!prefs.isRegistered()) return
        PrintHubService.start(context)
    }
}
