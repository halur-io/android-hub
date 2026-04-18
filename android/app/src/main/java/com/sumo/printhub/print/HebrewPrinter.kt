package com.sumo.printhub.print

import java.nio.charset.Charset

/**
 * Encodes Hebrew text for thermal printers that expect ISO-8859-8 (Hebrew)
 * with the matching ESC/POS codepage selected (commonly 32 or 36 on
 * HSPOS/Xprinter/Bixolon-style hardware).
 *
 * Behaviour matches the legacy Python print agent's `encode_text` helper:
 * any character that cannot be represented in the chosen encoding is
 * replaced with '?' so a single bad char never aborts a print job.
 */
object HebrewPrinter {

    fun encode(text: String, encodingName: String): ByteArray {
        val charset: Charset = runCatching { Charset.forName(encodingName) }
            .getOrElse { Charset.forName("ISO-8859-8") }
        return try {
            text.toByteArray(charset)
        } catch (_: Throwable) {
            // Per-char fallback so we still send most of the line.
            val sb = StringBuilder(text.length)
            for (ch in text) {
                val s = ch.toString()
                val ok = runCatching { s.toByteArray(charset) }.isSuccess
                sb.append(if (ok) ch else '?')
            }
            sb.toString().toByteArray(charset)
        }
    }
}
