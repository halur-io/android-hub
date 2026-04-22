package com.sumo.printhub.service

import android.app.Notification
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.media.AudioAttributes
import android.media.MediaPlayer
import android.media.RingtoneManager
import android.os.Build
import android.os.IBinder
import android.os.PowerManager
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import com.sumo.printhub.MainActivity
import com.sumo.printhub.PrintHubApp
import com.sumo.printhub.R
import com.sumo.printhub.data.local.SecurePrefs
import com.sumo.printhub.data.repository.PrintHubRepository
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.MainScope
import kotlinx.coroutines.cancel
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * Foreground service that owns the SSE connection, polling fallback, and
 * print pipeline so the app keeps running while the screen is off or the
 * activity is backgrounded.
 */
@AndroidEntryPoint
class PrintHubService : Service() {

    @Inject lateinit var repository: PrintHubRepository
    @Inject lateinit var prefs: SecurePrefs

    private val scope = MainScope()
    private var wakeLock: PowerManager.WakeLock? = null
    private var observerJob: Job? = null

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        startForeground(NOTIF_ID, buildNotification())
        acquireWakeLock()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (!prefs.isRegistered()) {
            stopSelf()
            return START_NOT_STICKY
        }
        repository.start(scope)
        observeNewOrderEvents(scope)
        return START_STICKY
    }

    private fun observeNewOrderEvents(scope: CoroutineScope) {
        if (observerJob?.isActive == true) return
        observerJob = scope.launch {
            repository.newOrderEvents.collectLatest { order ->
                val cfg = repository.config.value
                if (cfg?.notificationEnabled != false) showOrderAlert(order.displayNumber ?: order.orderNumber)
                if (cfg?.soundEnabled != false) playAlertSound()
                vibrate()
            }
        }
    }

    private fun showOrderAlert(orderNumber: String) {
        val tapIntent = PendingIntent.getActivity(
            this, 0,
            Intent(this, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )
        val notif = NotificationCompat.Builder(this, PrintHubApp.CHANNEL_ALERTS)
            .setContentTitle("הזמנה חדשה")
            .setContentText("הזמנה $orderNumber התקבלה")
            .setSmallIcon(android.R.drawable.ic_dialog_email)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .setContentIntent(tapIntent)
            .build()
        val nm = ContextCompat.getSystemService(this, android.app.NotificationManager::class.java)
        nm?.notify(orderNumber.hashCode(), notif)
    }

    private fun playAlertSound() {
        runCatching {
            val uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)
            val mp = MediaPlayer()
            mp.setAudioAttributes(
                AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_NOTIFICATION)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                    .build()
            )
            mp.setDataSource(this, uri)
            mp.setOnPreparedListener { it.start() }
            mp.setOnCompletionListener { it.release() }
            mp.prepareAsync()
        }
    }

    @Suppress("DEPRECATION")
    private fun vibrate() {
        runCatching {
            val pattern = longArrayOf(0, 200, 100, 200)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                val vm = getSystemService(VibratorManager::class.java)
                vm.defaultVibrator.vibrate(VibrationEffect.createWaveform(pattern, -1))
            } else {
                val v = getSystemService(Context.VIBRATOR_SERVICE) as? Vibrator ?: return
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    v.vibrate(VibrationEffect.createWaveform(pattern, -1))
                } else v.vibrate(pattern, -1)
            }
        }
    }

    private fun buildNotification(): Notification {
        val tapIntent = PendingIntent.getActivity(
            this, 0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )
        return NotificationCompat.Builder(this, PrintHubApp.CHANNEL_SERVICE)
            .setContentTitle(getString(R.string.service_running_title))
            .setContentText(getString(R.string.service_running_text))
            .setSmallIcon(android.R.drawable.stat_sys_data_bluetooth)
            .setOngoing(true)
            .setContentIntent(tapIntent)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }

    private fun acquireWakeLock() {
        runCatching {
            val pm = getSystemService(POWER_SERVICE) as PowerManager
            wakeLock = pm.newWakeLock(
                PowerManager.PARTIAL_WAKE_LOCK,
                "SUMO:PrintHub"
            ).apply { setReferenceCounted(false); acquire() }
        }
    }

    override fun onDestroy() {
        wakeLock?.runCatching { if (isHeld) release() }
        wakeLock = null
        repository.stop()
        scope.cancel()
        super.onDestroy()
    }

    companion object {
        private const val NOTIF_ID = 1001

        fun start(ctx: Context) {
            val intent = Intent(ctx, PrintHubService::class.java)
            ContextCompat.startForegroundService(ctx, intent)
        }

        fun stop(ctx: Context) {
            ctx.stopService(Intent(ctx, PrintHubService::class.java))
        }
    }
}
