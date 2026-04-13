# SUMO Print Hub — Android Native App — Complete Build Prompt

  ## What This App Does
  A native Android app (Kotlin) that runs on a tablet at each restaurant branch. It connects to the SUMO server API to receive new orders, then prints them on a local thermal printer (ESC/POS) via TCP socket over the local network. The app must handle Hebrew text correctly using CP862 encoding.

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
    "branch_id": 2,
    "branch_name": "כרמיאל",
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
        "id": 2,
        "name": "קופה",
        "ip_address": "10.100.10.234",
        "port": 9100,
        "encoding": "cp862",
        "codepage_num": 36,
        "printer_type": "snbc-btp-r880npv",
        "is_default": true,
        "stations": ["kitchen"],
        "checker_copies": 2,
        "payment_copies": 1,
        "cut_feed_lines": 6
      }
    ],
    "default_printer": { ... },
    "station_map": { "kitchen": { ... } }
  }
  ```

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
              "ip_address": "10.100.10.234",
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

  ---

  ## Printing — ESC/POS Over TCP Socket

  The app connects to the printer via TCP socket at the IP and port from the API (`ip_address:port`).

  ### The Exact Byte Sequence to Send

  ```
  STEP 1 — INITIALIZE PRINTER
    Bytes: 0x1B 0x40
    (ESC @ — resets printer to default state)

  STEP 2 — SELECT HEBREW CODEPAGE (CP862)
    Bytes: 0x1B 0x74 {codepage_num}
    codepage_num comes from the API (field: printer.codepage_num)
    Currently = 36 for all printers, so: 0x1B 0x74 0x24
    (ESC t 36 — tells the printer to interpret bytes 0x80-0x9A as Hebrew letters)

  STEP 3 — PRINT EACH LINE
    For each line of text, convert and send bytes (see encoding section below)
    End each line with 0x0A (newline)

  STEP 4 — FEED AND CUT
    Feed lines: send N times 0x0A (N = printer.cut_feed_lines, default 6)
    Cut: 0x1D 0x56 0x00
    (GS V 0 — full cut)
  ```

  ### Formatting Commands (send before the text bytes of a line)

  | Effect | Bytes | Notes |
  |--------|-------|-------|
  | Align center | 0x1B 0x61 0x01 | For headers |
  | Align right | 0x1B 0x61 0x02 | For Hebrew body text |
  | Align left | 0x1B 0x61 0x00 | For numbers/totals |
  | Bold ON | 0x1B 0x45 0x01 | |
  | Bold OFF | 0x1B 0x45 0x00 | |
  | Double height | 0x1B 0x21 0x10 | For order number |
  | Double width | 0x1B 0x21 0x20 | |
  | Double both | 0x1B 0x21 0x30 | |
  | Normal size | 0x1B 0x21 0x00 | Reset to normal |
  | Separator line | Send 32 times 0x2D then 0x0A | "--------------------------------" |

  ---

  ## Hebrew Text Encoding — CRITICAL

  Android does NOT support CP862 encoding natively. `Charset.forName("cp862")` does NOT work on Android. You MUST use the `cp862_hebrew_map` from the API to manually convert each character.

  ### Encoding Rules

  For each character in the string:
  1. If the character exists in `cp862_hebrew_map` → use the byte value from the map
  2. If the character is ASCII (English letters, digits, punctuation, space) → use its normal ASCII byte value
  3. The ₪ (shekel sign, U+20AA) is NOT in CP862 → replace with the ASCII text "NIS" or "₪" approximation

  ### RTL Text Reversal — CRITICAL

  ESC/POS printers ONLY print left-to-right. They have ZERO RTL support. You MUST reverse Hebrew text before encoding.

  **Pure Hebrew line:**
  ```
  Input:    "המבורגר קלאסי"
  Reversed: "יסאלק רגרובמה"
  Then encode the reversed string using the cp862 map.
  ```

  **Mixed Hebrew + Numbers (like prices):**
  For a line like `"המבורגר ₪59"`:
  1. The number and symbol should appear on the LEFT side of the printed line
  2. The Hebrew should appear on the RIGHT side
  3. Result after reversal: `"59₪ רגרובמה"`
  4. Then encode this reversed string

  **Simple approach for mixed lines:** Format the bon so that Hebrew text and numbers are on separate lines, or use fixed-width formatting where numbers are left-padded and Hebrew is right-aligned. This avoids complex BiDi logic.

  ### Kotlin Implementation

  ```kotlin
  class HebrewPrinter(
      private val cp862Map: Map<Char, Int>,
      private val codepageNum: Int
  ) {
      // Convert a Hebrew/mixed string to CP862 bytes (already reversed for RTL)
      fun encodeText(text: String): ByteArray {
          val reversed = text.reversed()
          val bytes = mutableListOf<Byte>()
          for (ch in reversed) {
              val mapped = cp862Map[ch]
              if (mapped != null) {
                  bytes.add(mapped.toByte())
              } else {
                  bytes.add(ch.code.toByte())
              }
          }
          return bytes.toByteArray()
      }

      // Build the init sequence
      fun initBytes(): ByteArray {
          return byteArrayOf(
              0x1B, 0x40,                       // ESC @ (init)
              0x1B, 0x74, codepageNum.toByte()  // ESC t n (select codepage)
          )
      }

      // Encode a full line (reversed + newline)
      fun encodeLine(text: String): ByteArray {
          return encodeText(text) + byteArrayOf(0x0A)
      }

      // Cut command
      fun cutBytes(feedLines: Int = 6): ByteArray {
          val feed = ByteArray(feedLines) { 0x0A }
          return feed + byteArrayOf(0x1D, 0x56, 0x00)
      }

      // Formatting helpers
      fun centerAlign() = byteArrayOf(0x1B, 0x61, 0x01)
      fun rightAlign() = byteArrayOf(0x1B, 0x61, 0x02)
      fun leftAlign() = byteArrayOf(0x1B, 0x61, 0x00)
      fun boldOn() = byteArrayOf(0x1B, 0x45, 0x01)
      fun boldOff() = byteArrayOf(0x1B, 0x45, 0x00)
      fun doubleSize() = byteArrayOf(0x1B, 0x21, 0x30)
      fun normalSize() = byteArrayOf(0x1B, 0x21, 0x00)
      fun separator() = "--------------------------------".toByteArray() + byteArrayOf(0x0A)
  }

  // Build the map from API response
  fun buildCp862Map(apiMap: Map<String, Int>): Map<Char, Int> {
      return apiMap.mapKeys { it.key[0] }
  }
  ```

  ### Kotlin — Full Print Flow Example

  ```kotlin
  suspend fun printOrder(order: OrderData, printer: PrinterConfig, cp862Map: Map<Char, Int>) {
      val hp = HebrewPrinter(cp862Map, printer.codepageNum)

      // Build the full bon as a byte buffer
      val buffer = ByteArrayOutputStream()

      // Init printer + select codepage
      buffer.write(hp.initBytes())

      // Header: Order number (big, centered)
      buffer.write(hp.centerAlign())
      buffer.write(hp.doubleSize())
      buffer.write(hp.encodeLine("הזמנה #${order.orderNumber}"))
      buffer.write(hp.normalSize())

      // Order type
      buffer.write(hp.encodeLine(order.orderType))
      buffer.write(hp.separator())

      // Items (right-aligned for Hebrew)
      buffer.write(hp.rightAlign())
      for (item in order.items) {
          buffer.write(hp.boldOn())
          buffer.write(hp.encodeLine("${item.quantity}x ${item.nameHe}"))
          buffer.write(hp.boldOff())

          // Extras
          for (extra in item.extras) {
              buffer.write(hp.encodeLine("  + $extra"))
          }

          // Notes
          if (item.notes.isNotEmpty()) {
              buffer.write(hp.encodeLine("  * ${item.notes}"))
          }
      }

      buffer.write(hp.separator())

      // Customer info
      buffer.write(hp.encodeLine(order.customerName))
      buffer.write(hp.encodeLine(order.customerPhone))

      // Cut
      buffer.write(hp.cutBytes(printer.cutFeedLines))

      // Send to printer via TCP socket
      val socket = Socket(printer.ipAddress, printer.port)
      socket.getOutputStream().write(buffer.toByteArray())
      socket.getOutputStream().flush()
      socket.close()
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
  - Connects to SSE stream for real-time order events.
  - Falls back to polling `/ops/api/orders/unprinted` every 15 seconds if SSE disconnects.
  - On receiving an order: print it, then call `/ops/api/orders/mark-printed`.
  - Handle multiple copies: `print_jobs[].copies` tells you how many times to print each bon.

  ### Error Handling
  - If TCP socket to printer fails: retry 3 times with 2-second delay.
  - If printer is unreachable: show alert on screen + play error sound.
  - If SSE disconnects: auto-reconnect after 5 seconds, fall back to polling.
  - Log all print attempts (success/fail) with timestamps.

  ### Dependencies
  ```gradle
  implementation("com.squareup.okhttp3:okhttp:4.12.0")      // HTTP + SSE
  implementation("com.squareup.okhttp3:okhttp-sse:4.12.0")   // SSE support
  implementation("com.google.code.gson:gson:2.10.1")         // JSON parsing
  ```

  ---

  ## Summary of Critical Rules

  1. **DO NOT** use `Charset.forName("cp862")` — it does not work on Android
  2. **DO** use the `cp862_hebrew_map` from the API to convert Hebrew chars to bytes
  3. **DO** send `ESC t {codepage_num}` before any text (codepage_num from API, currently 36)
  4. **DO** reverse all Hebrew text before encoding (printer is LTR only)
  5. **DO** send `ESC @` (init) at the start of every print job
  6. **DO** call `/ops/api/orders/mark-printed` after successful printing
  7. **DO** respect `copies` count in each print_job
  8. Numbers and English characters use their normal ASCII byte values — only Hebrew needs the map
  