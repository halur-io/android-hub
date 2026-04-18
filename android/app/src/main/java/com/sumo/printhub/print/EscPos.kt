package com.sumo.printhub.print

/**
 * ESC/POS byte sequences shared by every printer brand we care about.
 * Mirrors the constants used by the legacy Python print agent so that
 * output bytes are byte-for-byte equivalent.
 */
object EscPos {
    val ESC: Byte = 0x1B
    val GS: Byte = 0x1D

    val INIT = byteArrayOf(ESC, '@'.code.toByte())
    val CUT_FULL = byteArrayOf(GS, 'V'.code.toByte(), 0x00)

    val ALIGN_LEFT = byteArrayOf(ESC, 'a'.code.toByte(), 0x00)
    val ALIGN_CENTER = byteArrayOf(ESC, 'a'.code.toByte(), 0x01)
    val ALIGN_RIGHT = byteArrayOf(ESC, 'a'.code.toByte(), 0x02)

    val FONT_NORMAL = byteArrayOf(ESC, '!'.code.toByte(), 0x00)
    val FONT_DOUBLE_H = byteArrayOf(ESC, '!'.code.toByte(), 0x10)
    val FONT_DOUBLE_W = byteArrayOf(ESC, '!'.code.toByte(), 0x20)
    val FONT_DOUBLE = byteArrayOf(ESC, '!'.code.toByte(), 0x30)

    val BOLD_ON = byteArrayOf(ESC, 'E'.code.toByte(), 0x01)
    val BOLD_OFF = byteArrayOf(ESC, 'E'.code.toByte(), 0x00)
    val UNDERLINE_ON = byteArrayOf(ESC, '-'.code.toByte(), 0x01)
    val UNDERLINE_OFF = byteArrayOf(ESC, '-'.code.toByte(), 0x00)
    val INVERT_ON = byteArrayOf(GS, 'B'.code.toByte(), 0x01)
    val INVERT_OFF = byteArrayOf(GS, 'B'.code.toByte(), 0x00)

    /** ESC t n — selects the printer's character codepage. */
    fun setCodepage(n: Int): ByteArray =
        byteArrayOf(ESC, 't'.code.toByte(), (n and 0xFF).toByte())
}
