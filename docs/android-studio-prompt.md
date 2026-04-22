# Android Studio AI Prompt — SUMO Print Hub App

Copy this entire prompt into Android Studio's AI assistant (Gemini / ChatGPT plugin) or use it as the system prompt when generating the app.

---

## PROMPT START

Build me a complete Android tablet application called **"SUMO Print Hub"** in **Kotlin** with **Jetpack Compose** UI. The app runs on Android tablets in restaurants and acts as a print hub — it receives online food orders from a server via SSE (Server-Sent Events) and prints thermal receipts (bons) to ESC/POS printers on the local network via raw TCP sockets.

### Tech Stack
- **Language**: Kotlin
- **Min SDK**: 26 (Android 8.0)
- **Target SDK**: 34
- **UI**: Jetpack Compose with Material 3
- **Networking**: OkHttp + okhttp-sse for SSE, Retrofit for REST APIs
- **Architecture**: MVVM with Repository pattern
- **DI**: Hilt
- **Local storage**: DataStore (EncryptedSharedPreferences for API key)
- **Background**: Foreground Service for SSE + heartbeat (must survive screen off)
- **Notifications**: Android notification channel for new orders

### Core Principle: ZERO HARDCODING

The app hardcodes **nothing** except the server URL entered on first setup. Everything else (printer IPs, poll intervals, branch assignment, sound prefs, encoding, station mapping) comes from the server config API. The admin can remotely reconfigure the device from the dashboard without touching the tablet.

### Server API

Base URL: `https://<server>/ops`

All endpoints require header `X-Print-Key: <api-key>` (except SSE which uses `?key=<api-key>` query param).

**Endpoints:**

1. `POST /ops/api/devices/register` — Register device
   - Body: `{"device_id": "android-<UUID>", "branch_id": 1, "device_name": "Tablet 1"}`
   - Response: `{"ok": true, "device": {"id": 5, ...}}`

2. `POST /ops/api/devices/heartbeat` — Send heartbeat every 30s (configurable)
   - Body: `{"device_id": "android-<UUID>"}`
   - Response: `{"ok": true, "server_time": "..."}`

3. `GET /ops/api/devices/<id>/config` — Fetch full config (printers, stations, settings)
   - Response includes: `poll_interval_seconds`, `sse_reconnect_delay_ms`, `heartbeat_interval_seconds`, `sound_enabled`, `notification_enabled`, `encoding`, `codepage_num`, `default_printer`, `station_map`, `printers`

4. `GET /ops/api/orders/stream?key=<key>&branch_id=<id>` — SSE stream
   - Events: `{"type":"connected"}`, `{"type":"new_order","id":42,"order_number":"ORD-...","order_type":"delivery","branch_id":1,"customer_name":"...","total_amount":135,"items_count":3,"created_at":"..."}`
   - Keepalive: `: keepalive` every ~25s

5. `GET /ops/api/orders/unprinted?branch_id=<id>` — Polling fallback
   - Response: `{"ok": true, "orders": [...]}`
   - Each order has: `id`, `order_number`, `order_type`, `status`, `branch_id`, `customer_name`, `customer_phone`, `delivery_address`, `delivery_city`, `delivery_notes`, `customer_notes`, `subtotal`, `delivery_fee`, `discount_amount`, `total_amount`, `payment_method`, `coupon_code`, `created_at`, `items` (array with `name_he`, `print_name`, `qty`, `price`, `options`, `excluded_ingredients`), `items_by_station` (dict of station→items)

6. `POST /ops/api/orders/<id>/ack` — Acknowledge receipt before printing
   - Body: `{"device_id": "android-<UUID>"}`

7. `POST /ops/api/orders/mark-printed` — Mark orders as printed
   - Body: `{"order_ids": [42, 43]}`

### App Screens

**Screen 1: Setup (first launch only)**
- Text field: Server URL (e.g. `https://sumo.example.com`)
- Text field: API Key
- Dropdown: Select branch (fetch branches after connecting)
- Text field: Device name (default: "Tablet 1")
- Button: "Connect & Register"
- On success → save to encrypted storage → go to Main screen

**Screen 2: Main Dashboard**
- Top bar: Device name, connection status indicator (green dot = SSE connected, yellow = polling, red = disconnected), branch name
- Center: Large order counter showing unprinted orders count
- Recent orders list (last 20) showing: order number, customer name, type (delivery/pickup), total, status (received/printing/printed/failed)
- Bottom bar: "Reprint Last" button, "Settings" button

**Screen 3: Settings**
- Show current config from server (read-only display)
- Printer test button (send test print to each configured printer)
- Re-register device button
- Clear data & reset button
- Version info

### ESC/POS Printing

The app prints 3 types of bons per order via raw TCP sockets (port 9100):

**Byte constants:**
```
INIT = 0x1B, 0x40
CUT  = 0x1D, 0x56, 0x00
ALIGN_LEFT = 0x1B, 0x61, 0x00
ALIGN_CENTER = 0x1B, 0x61, 0x01
ALIGN_RIGHT = 0x1B, 0x61, 0x02
FONT_NORMAL = 0x1B, 0x21, 0x00
FONT_DOUBLE_H = 0x1B, 0x21, 0x10
FONT_DOUBLE = 0x1B, 0x21, 0x30
BOLD_ON = 0x1B, 0x45, 0x01
BOLD_OFF = 0x1B, 0x45, 0x00
INVERT_ON = 0x1D, 0x42, 0x01
INVERT_OFF = 0x1D, 0x42, 0x00
CODEPAGE_CMD = 0x1B, 0x74, <codepage_num from config>
```

**Text encoding**: All Hebrew text → encode as `ISO-8859-8` bytes. The codepage number comes from the printer config.

**1. Checker Bon** (default printer, `checker_copies` copies):
- Right-aligned Hebrew
- Header: phone + "SUMO"
- Order info: customer name, order number, date, notes
- Items: each with double-height bold name+qty, options, excluded ingredients ("ללא")
- Delivery address if applicable
- Footer: inverted order number, order type in double bold ("משלוח" / "איסוף עצמי")

**2. Payment Bon** (default printer, `payment_copies` copies):
- Similar header
- Items with prices
- Subtotal, delivery fee, discount, total (double bold)
- Payment method

**3. Station Bon** (station-specific printer from `station_map`, 1 copy):
- Station name header (double bold centered)
- Only items for that station
- Order type footer

**Print flow per order:**
1. Default printer: send INIT + all checker bons + all payment bons + CUT in one TCP connection
2. For each station with items: find printer from `station_map` → send INIT + station bon + CUT

**TCP socket**: connect to printer IP:port, 5 second timeout, send all bytes, close. Retry once on failure.

### Foreground Service

Create a foreground service `PrintHubService` that:
- Maintains the SSE connection
- Sends heartbeat every `heartbeat_interval_seconds`
- Re-fetches config every 5 minutes
- Shows persistent notification: "SUMO Print Hub — Connected" with order count
- Survives screen off and app backgrounding
- Auto-starts on device boot (BOOT_COMPLETED receiver)

### Order Processing Flow

```
SSE "new_order" event received
  → Play notification sound (if sound_enabled)
  → Show Android notification
  → Fetch full order from /ops/api/orders/unprinted (filter by order ID)
  → POST /ops/api/orders/<id>/ack (acknowledge receipt)
  → Build ESC/POS bytes for all bons
  → Send to printers via TCP
  → POST /ops/api/orders/mark-printed
  → Update UI
  → On print failure: show error notification, keep in retry queue
```

### Error Handling
- SSE disconnect: wait `sse_reconnect_delay_ms` → reconnect → re-fetch config → poll unprinted to catch missed orders
- Print failure: retry once, then mark as failed in UI, keep in retry queue for manual "Reprint"
- 401 from server: show "Invalid API Key" → go to setup screen
- 404 on device endpoints: re-register device
- Network errors: exponential backoff (1s, 2s, 4s, max 30s)

### Hebrew / RTL
- All printed text is Hebrew, right-aligned
- Encode text as ISO-8859-8 bytes
- Set codepage with ESC 't' <codepage_num> before printing text
- The UI should support RTL layout (add `android:supportsRtl="true"` to manifest)

### Project Structure
```
app/
├── src/main/java/com/sumo/printhub/
│   ├── di/                    # Hilt modules
│   ├── data/
│   │   ├── api/               # Retrofit interfaces
│   │   ├── model/             # Data classes for API responses
│   │   ├── local/             # DataStore, encrypted prefs
│   │   └── repository/        # Repository implementations
│   ├── domain/
│   │   ├── model/             # Domain models
│   │   └── usecase/           # Use cases
│   ├── service/
│   │   ├── PrintHubService.kt # Foreground service
│   │   ├── SseManager.kt      # SSE connection manager
│   │   ├── HeartbeatManager.kt
│   │   └── PrintManager.kt    # ESC/POS builder + TCP sender
│   ├── ui/
│   │   ├── setup/             # Setup screen
│   │   ├── dashboard/         # Main dashboard
│   │   ├── settings/          # Settings screen
│   │   └── theme/             # Material 3 theme
│   └── util/
│       ├── EscPos.kt          # ESC/POS byte constants and helpers
│       └── BonBuilder.kt      # Bon layout builders
├── src/main/res/
│   ├── raw/new_order.mp3      # Notification sound
│   └── values/strings.xml
└── build.gradle.kts
```

### Key Dependencies (build.gradle.kts)
```kotlin
implementation("com.squareup.okhttp3:okhttp:4.12.0")
implementation("com.squareup.okhttp3:okhttp-sse:4.12.0")
implementation("com.squareup.retrofit2:retrofit:2.9.0")
implementation("com.squareup.retrofit2:converter-gson:2.9.0")
implementation("com.google.dagger:hilt-android:2.50")
implementation("androidx.datastore:datastore-preferences:1.0.0")
implementation("androidx.security:security-crypto:1.1.0-alpha06")
implementation("androidx.compose.material3:material3:1.2.0")
implementation("androidx.lifecycle:lifecycle-service:2.7.0")
```

### Important Notes
- The app theme should be dark (restaurant environment), using Material 3 dark color scheme
- Use Hebrew strings for all UI text visible to the user
- The persistent notification must use a proper notification channel
- Handle Android 13+ notification permission (POST_NOTIFICATIONS)
- The app should work in landscape orientation on tablets
- Add INTERNET, FOREGROUND_SERVICE, RECEIVE_BOOT_COMPLETED, POST_NOTIFICATIONS permissions
- WiFi should stay connected even when screen is off (use WifiManager.WifiLock)

Build the complete app with all files. Make sure the ESC/POS printing works correctly with Hebrew text encoded as ISO-8859-8.

## PROMPT END
