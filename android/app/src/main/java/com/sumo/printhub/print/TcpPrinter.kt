package com.sumo.printhub.print

import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.BufferedOutputStream
import java.net.InetSocketAddress
import java.net.Socket
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Sends raw ESC/POS bytes to a thermal printer over TCP/IP (port 9100).
 * Wraps every send in a small retry loop because thermal printers commonly
 * stall while finishing a previous job.
 */
@Singleton
class TcpPrinter @Inject constructor() {

    data class SendResult(val ok: Boolean, val error: String? = null)

    suspend fun send(
        ip: String,
        port: Int,
        bytes: ByteArray,
        connectTimeoutMs: Int = 5_000,
        writeTimeoutMs: Int = 8_000,
        retries: Int = 2
    ): SendResult = withContext(Dispatchers.IO) {
        var lastError: String? = null
        for (attempt in 0..retries) {
            try {
                Socket().use { sock ->
                    sock.soTimeout = writeTimeoutMs
                    sock.tcpNoDelay = true
                    sock.connect(InetSocketAddress(ip, port), connectTimeoutMs)
                    BufferedOutputStream(sock.getOutputStream()).use { os ->
                        os.write(bytes)
                        os.flush()
                    }
                }
                return@withContext SendResult(ok = true)
            } catch (t: Throwable) {
                lastError = "${t.javaClass.simpleName}: ${t.message}"
                Log.w(TAG, "Print attempt ${attempt + 1} to $ip:$port failed: $lastError")
                // Brief backoff between attempts.
                Thread.sleep(400L * (attempt + 1))
            }
        }
        SendResult(ok = false, error = lastError)
    }

    private companion object {
        const val TAG = "TcpPrinter"
    }
}
