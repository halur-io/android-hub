package com.sumo.printhub

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager
import android.os.Build
import androidx.hilt.work.HiltWorkerFactory
import androidx.work.Configuration
import dagger.hilt.android.HiltAndroidApp
import javax.inject.Inject

@HiltAndroidApp
class PrintHubApp : Application(), Configuration.Provider {

    @Inject lateinit var workerFactory: HiltWorkerFactory

    override val workManagerConfiguration: Configuration
        get() = Configuration.Builder()
            .setWorkerFactory(workerFactory)
            .build()

    override fun onCreate() {
        super.onCreate()
        createNotificationChannels()
    }

    private fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return
        val nm = getSystemService(NOTIFICATION_SERVICE) as NotificationManager

        val service = NotificationChannel(
            CHANNEL_SERVICE,
            getString(R.string.service_channel_name),
            NotificationManager.IMPORTANCE_LOW
        ).apply {
            description = getString(R.string.service_channel_desc)
            setShowBadge(false)
        }
        nm.createNotificationChannel(service)

        val alerts = NotificationChannel(
            CHANNEL_ALERTS,
            getString(R.string.alerts_channel_name),
            NotificationManager.IMPORTANCE_HIGH
        ).apply {
            description = getString(R.string.alerts_channel_desc)
            enableVibration(true)
            enableLights(true)
        }
        nm.createNotificationChannel(alerts)
    }

    companion object {
        const val CHANNEL_SERVICE = "sumo_service"
        const val CHANNEL_ALERTS = "sumo_alerts"
    }
}
