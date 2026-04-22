# SUMO Print Hub — Android Native App — Complete Build Prompt

## ⚠️ THE #1 BUG THAT CAUSES GIBBERISH — READ THIS FIRST

Android's default string encoding is UTF-8. Hebrew in UTF-8 is 2 bytes per character (e.g. א = 0xD7 0x90). But the thermal printer expects CP862 encoding where Hebrew is 1 byte per character (e.g. א = 0x80). If you send UTF-8 bytes to the printer, it prints garbage — random symbols.

**YOU MUST NEVER DO THIS:**
```kotlin
// WRONG — sends UTF-8 bytes, printer prints garbage
val bytes = "המבורגר".toByteArray()
outputStream.write(bytes)

// WRONG — CP862 charset doesn't exist on Android
val bytes = "המבורגר".toByteArray(Charset.forName("cp862"))

// WRONG — any Charset/String encoding method
val bytes = text.encodeToByteArray()
```

**YOU MUST DO THIS INSTEAD — convert each character manually using the map from the API:**
```kotlin
fun encodeHebrew(text: String, cp862Map: Map<Char, Int>): ByteArray {
    val reversed = text.reversed()  // MUST reverse for RTL
    val bytes = mutableListOf<Byte>()
    for (ch in reversed) {
        val mapped = cp862Map[ch]
        if (mapped != null) {
            bytes.add(mapped.toByte())  // Hebrew char → 1 byte from map
        } else {
            bytes.add(ch.code.toByte())  // ASCII passthrough
        }
    }
    return bytes.toByteArray()
}
```

### VERIFICATION TEST — Use This to Confirm Encoding is Correct

Call this API endpoint:
```
GET /ops/api/print/test-bytes?key=sumo-print-2024-secure
```

It returns the exact byte array for printing "המבורגר קלאסי". The app must produce IDENTICAL bytes:

```
Expected bytes (decimal): 27 64 27 116 36 27 97 1 137 145 128 140 151 32 152 130 152 133 129 142 132 10
```

Breakdown:
- `27 64` = ESC @ (init printer)
- `27 116 36` = ESC t 36 (select CP862 Hebrew codepage)
- `27 97 1` = ESC a 1 (center align)
- `137 145 128 140 151 32 152 130 152 133 129 142 132` = "יסאלק רגרובמה" (reversed Hebrew, each char = 1 byte from cp862 map)
- `10` = newline

If your app's encodeHebrew("המבורגר קלאסי") does NOT produce `[137, 145, 128, 140, 151, 32, 152, 130, 152, 133, 129, 142, 132]`, then the encoding is wrong.

Add this log to your app to verify:
```kotlin
val testText = "המבורגר קלאסי"
val encoded = encodeHebrew(testText, cp862Map)
Log.d("PRINT", "Encoded bytes: ${encoded.map { it.toInt() and 0xFF }}")
// Must print: [137, 145, 128, 140, 151, 32, 152, 130, 152, 133, 129, 142, 132]
```

---

## Server API

**Base URL:** `https://cad2a536-a2eb-41a8-a0a3-6f4a608fee70-00-2gvg9dtirvl7z.picard.replit.dev`

**Authentication:** Every request must include the API key as a query parameter:
`?key=sumo-print-2024-secure`

### Endpoints

#### 1. Get Printers & Hebrew Config
```
GET /ops/api/branch/{branch_id}/printers?key=sumo-print-2024-secure
```

Response:
```json
{
  "ok": true,
  "branch_id": 1,
  "branch_name": "ראמה",
  "rtl": true,
  "cp862_hebrew_map": {
    "א": 128, "ב": 129, "ג": 130, "ד": 131, "ה": 132,
    "ו": 133, "ז": 134, "ח": 135, "ט": 136, "י": 137,
    "ך": 138, "כ": 139, "ל": 140, "ם": 141, "מ": 142,
    "ן": 143, "נ": 144, "ס": 145, "ע": 146, "ף": 147,
    "פ": 148, "ץ": 149, "צ": 150, "ק": 151, "ר": 152,
    "ש": 153, "ת": 154
  },
  "printers": [
    {
      "id": 3,
      "name": "מדפסת ראשית",
      "ip_address": "10.0.0.1",
      "port": 9100,
      "encoding": "cp862",
      "codepage_num": 36,
      "printer_type": "epson-tm",
      "is_default": true,
      "stations": ["kitchen"],
      "checker_copies": 2,
      "payment_copies": 1,
      "cut_feed_lines": 6
    }
  ]
}
```

**IMPORTANT:** The `cp862_hebrew_map` is the ONLY way to encode Hebrew on Android. Parse it on app startup and use it for ALL text encoding. Do NOT try any other encoding method.

#### 2. Poll for Unprinted Orders
```
GET /ops/api/orders/unprinted?branch_id={branch_id}&key=sumo-print-2024-secure
```

Response:
```json
{
  "ok": true,
  "orders": [
    {
      "id": 123,
      "order_number": 45,
      "status": "preparing",
      "order_type": "delivery",
      "customer_name": "חליל",
      "customer_phone": "0526647778",
      "items": [
        {
          "name_he": "המבורגר קלאסי",
          "quantity": 2,
          "price": 59.0,
          "extras": ["תוספת גבינה", "ללא בצל"],
          "notes": "אש חזקה"
        }
      ],
      "total_amount": 118.0,
      "print_jobs": [
        {
          "bon_type": "checker",
          "copies": 2,
          "printer": {
            "ip_address": "10.0.0.1",
            "port": 9100,
            "encoding": "cp862",
            "codepage_num": 36
          },
          "items": [...]
        }
      ]
    }
  ]
}
```

#### 3. Real-Time SSE Stream (listen for new orders)
```
GET /ops/api/orders/stream?branch_id={branch_id}&key=sumo-print-2024-secure
```
Server-Sent Events. Listen for event type `print_order`. The data payload is the same order JSON as the unprinted endpoint above.

#### 4. Mark Order as Printed
```
POST /ops/api/orders/mark-printed?key=sumo-print-2024-secure
Content-Type: application/json

{"order_ids": [123, 456]}
```

#### 5. Diagnostic: Get Expected Bytes for Test Print
```
GET /ops/api/print/test-bytes?key=sumo-print-2024-secure
```
Returns the exact raw byte array that should be sent to the printer for a test string. Use this to verify your encoding matches the server's expected output.

---

## Printing — ESC/POS Over TCP Socket

The app connects to the printer via raw TCP socket at `ip_address:port` from the API.

### The Exact Byte Sequence to Send

```
STEP 1 — INITIALIZE PRINTER
  Send bytes: [0x1B, 0x40]
  This is ESC @ — resets printer to default state
  MUST be sent at the start of every print job

STEP 2 — SELECT HEBREW CODEPAGE (CP862)
  Send bytes: [0x1B, 0x74, codepage_num]
  codepage_num = 36 (from API field: printer.codepage_num)
  So send: [0x1B, 0x74, 0x24]
  This tells the printer: "interpret bytes 0x80-0x9A as Hebrew letters"
  MUST be sent ONCE, right after init, before any text

STEP 3 — FOR EACH LINE OF TEXT
  a. Send formatting command (optional, see table below)
  b. Reverse the text string (Hebrew is RTL, printer is LTR)
  c. Convert each character to a byte using cp862_hebrew_map
  d. Send the bytes + 0x0A (newline)

STEP 4 — FEED AND CUT
  Send 6x 0x0A (feed lines, count from printer.cut_feed_lines)
  Send: [0x1D, 0x56, 0x00] (GS V 0 — full cut)
```

### Formatting Commands (send before the text bytes of a line)

| Effect | Bytes | Decimal |
|--------|-------|---------|
| Align center | 0x1B 0x61 0x01 | 27 97 1 |
| Align right | 0x1B 0x61 0x02 | 27 97 2 |
| Align left | 0x1B 0x61 0x00 | 27 97 0 |
| Bold ON | 0x1B 0x45 0x01 | 27 69 1 |
| Bold OFF | 0x1B 0x45 0x00 | 27 69 0 |
| Double height | 0x1B 0x21 0x10 | 27 33 16 |
| Double width | 0x1B 0x21 0x20 | 27 33 32 |
| Double both | 0x1B 0x21 0x30 | 27 33 48 |
| Normal size | 0x1B 0x21 0x00 | 27 33 0 |
| Separator line | 32x 0x2D + 0x0A | "--------------------------------\n" |

---

## Hebrew Text Encoding — THE CORE LOGIC

### The cp862_hebrew_map (from API)

This is the ONLY lookup table you need. Each Hebrew Unicode character maps to exactly ONE byte:

```
א → 128 (0x80)    ב → 129 (0x81)    ג → 130 (0x82)    ד → 131 (0x83)
ה → 132 (0x84)    ו → 133 (0x85)    ז → 134 (0x86)    ח → 135 (0x87)
ט → 136 (0x88)    י → 137 (0x89)    ך → 138 (0x8A)    כ → 139 (0x8B)
ל → 140 (0x8C)    ם → 141 (0x8D)    מ → 142 (0x8E)    ן → 143 (0x8F)
נ → 144 (0x90)    ס → 145 (0x91)    ע → 146 (0x92)    ף → 147 (0x93)
פ → 148 (0x94)    ץ → 149 (0x95)    צ → 150 (0x96)    ק → 151 (0x97)
ר → 152 (0x98)    ש → 153 (0x99)    ת → 154 (0x9A)
```

### Encoding Algorithm

For every string that contains Hebrew:

1. **REVERSE** the entire string (character order). The printer prints left-to-right only.
2. **CONVERT** each character:
   - Hebrew letter → look up in cp862_hebrew_map → use that single byte
   - Space (0x20), digits (0x30-0x39), English letters, punctuation → use ASCII byte as-is
3. **APPEND** 0x0A (newline) at the end

Example step by step:
```
Original:  "המבורגר קלאסי"
Step 1 reverse: "יסאלק רגרובמה"
Step 2 convert each char:
  י → 137
  ס → 145
  א → 128
  ל → 140
  ק → 151
  (space) → 32
  ר → 152
  ג → 130
  ר → 152
  ו → 133
  ב → 129
  מ → 142
  ה → 132
Step 3: append 10 (newline)
Result bytes: [137, 145, 128, 140, 151, 32, 152, 130, 152, 133, 129, 142, 132, 10]
```

### Complete Kotlin Implementation

```kotlin
class HebrewPrinter(
    private val cp862Map: Map<Char, Int>,
    private val codepageNum: Int
) {
    fun encodeText(text: String): ByteArray {
        val reversed = text.reversed()
        val bytes = mutableListOf<Byte>()
        for (ch in reversed) {
            val mapped = cp862Map[ch]
            if (mapped != null) {
                bytes.add(mapped.toByte())
            } else if (ch.code in 0x20..0x7E) {
                bytes.add(ch.code.toByte())
            }
            // skip any char that's not in the map and not ASCII
        }
        return bytes.toByteArray()
    }

    fun initBytes(): ByteArray {
        return byteArrayOf(
            0x1B, 0x40,                       // ESC @ (init)
            0x1B, 0x74, codepageNum.toByte()  // ESC t n (select CP862)
        )
    }

    fun encodeLine(text: String): ByteArray {
        return encodeText(text) + byteArrayOf(0x0A)
    }

    fun cutBytes(feedLines: Int = 6): ByteArray {
        val feed = ByteArray(feedLines) { 0x0A }
        return feed + byteArrayOf(0x1D, 0x56, 0x00)
    }

    fun centerAlign() = byteArrayOf(0x1B, 0x61, 0x01)
    fun rightAlign() = byteArrayOf(0x1B, 0x61, 0x02)
    fun leftAlign() = byteArrayOf(0x1B, 0x61, 0x00)
    fun boldOn() = byteArrayOf(0x1B, 0x45, 0x01)
    fun boldOff() = byteArrayOf(0x1B, 0x45, 0x00)
    fun doubleSize() = byteArrayOf(0x1B, 0x21, 0x30)
    fun normalSize() = byteArrayOf(0x1B, 0x21, 0x00)
    fun separator() = "--------------------------------".toByteArray(Charsets.US_ASCII) + byteArrayOf(0x0A)
}

// Parse the map from API JSON response
fun buildCp862Map(apiMap: Map<String, Int>): Map<Char, Int> {
    return apiMap.mapKeys { it.key[0] }
}
```

### Full Print Flow — Complete Working Example

```kotlin
suspend fun printOrder(order: OrderData, printer: PrinterConfig, cp862Map: Map<Char, Int>) {
    val hp = HebrewPrinter(cp862Map, printer.codepageNum)
    val buffer = ByteArrayOutputStream()

    // 1. Init + select codepage (MUST BE FIRST)
    buffer.write(hp.initBytes())

    // 2. Header
    buffer.write(hp.centerAlign())
    buffer.write(hp.doubleSize())
    buffer.write(hp.encodeLine("SUMO"))
    buffer.write(hp.normalSize())
    buffer.write(hp.separator())

    // 3. Order number (big)
    buffer.write(hp.centerAlign())
    buffer.write(hp.doubleSize())
    buffer.write(hp.encodeLine("#${order.orderNumber}"))
    buffer.write(hp.normalSize())

    // 4. Order type
    buffer.write(hp.centerAlign())
    buffer.write(hp.encodeLine(order.orderType))
    buffer.write(hp.separator())

    // 5. Items (right-aligned for Hebrew)
    buffer.write(hp.rightAlign())
    for (item in order.items) {
        buffer.write(hp.boldOn())
        buffer.write(hp.encodeLine("${item.quantity}x ${item.nameHe}"))
        buffer.write(hp.boldOff())
        for (extra in item.extras) {
            buffer.write(hp.encodeLine("  + $extra"))
        }
        if (item.notes.isNotEmpty()) {
            buffer.write(hp.encodeLine("  * ${item.notes}"))
        }
    }

    buffer.write(hp.separator())

    // 6. Customer info
    buffer.write(hp.rightAlign())
    buffer.write(hp.encodeLine(order.customerName))
    buffer.write(hp.leftAlign())
    buffer.write(hp.encodeLine(order.customerPhone))

    // 7. Cut
    buffer.write(hp.cutBytes(printer.cutFeedLines))

    // 8. Send to printer via TCP
    withContext(Dispatchers.IO) {
        val socket = Socket()
        socket.connect(InetSocketAddress(printer.ipAddress, printer.port), 5000)
        socket.getOutputStream().write(buffer.toByteArray())
        socket.getOutputStream().flush()
        socket.close()
    }
}
```

---

## App Architecture

### Screens
1. **Setup Screen** — Enter branch_id, API key. Save to SharedPreferences.
2. **Main Screen** — Shows connection status, last print time, print queue count.
3. **Print Log** — Scrollable list of recently printed orders with timestamps.

### Background Service
- Runs as a foreground service with a persistent notification.
- On startup: call `/ops/api/branch/{id}/printers` and cache the `cp862_hebrew_map` and printer configs.
- Connect to SSE stream `/ops/api/orders/stream` for real-time order events.
- Also poll `/ops/api/orders/unprinted` every 15 seconds as fallback.
- On receiving an order: print it using the HebrewPrinter class above, then call `/ops/api/orders/mark-printed`.
- Handle `print_jobs[].copies` — print each bon the specified number of times.

### Error Handling
- TCP socket to printer fails: retry 3 times with 2-second delay.
- Printer unreachable: show alert on screen + play error sound.
- SSE disconnects: auto-reconnect after 5 seconds, fall back to polling.
- Log all print attempts (success/fail) with timestamps.

### Dependencies
```gradle
implementation("com.squareup.okhttp3:okhttp:4.12.0")
implementation("com.squareup.okhttp3:okhttp-sse:4.12.0")
implementation("com.google.code.gson:gson:2.10.1")
```

---

## Summary of Critical Rules

1. **NEVER** use `.toByteArray()`, `.encodeToByteArray()`, `Charset.forName("cp862")`, or any built-in string encoding for Hebrew text — they ALL produce wrong bytes on Android
2. **ALWAYS** use the `cp862_hebrew_map` from the API to convert Hebrew chars to single bytes
3. **ALWAYS** send `ESC @ (init)` + `ESC t 36 (codepage)` at the start of every print job, before any text
4. **ALWAYS** reverse Hebrew text before encoding (printer is LTR only, Hebrew is RTL)
5. **ALWAYS** call `/ops/api/orders/mark-printed` after successful printing
6. Numbers, English letters, spaces, and punctuation use their normal ASCII byte values — only Hebrew needs the map
7. Add the verification log shown at the top of this document to confirm your encoding produces the correct bytes
