# SUMO Print Hub — Android Tablet App

Native Android (Kotlin + Jetpack Compose) implementation of the SUMO restaurant
print hub for thermal-printer routing on the kitchen tablet.

This module is **built and run from Android Studio** — Replit cannot host
Android builds. The project is structured as a standard single-module
Gradle (Kotlin DSL) Android Studio project.

## What it does

Connects the in-restaurant tablet to the SUMO Flask server and:

1. Maintains a long-lived SSE connection to `/ops/api/orders/stream` to
   receive new orders in real time.
2. Falls back to polling `/ops/api/orders/unprinted` whenever the SSE
   connection drops.
3. Routes each order's bons to the correct thermal printers over raw
   TCP (port 9100) using ESC/POS bytes, exactly like the legacy Python
   `print_agent.py` does — Hebrew encoded as ISO-8859-8 with the
   matching codepage selected.
4. Acknowledges each order, reports the print outcome, and marks the
   order as printed.
5. Plays an audible alert + vibration + Android notification on every
   new order.
6. Heartbeats every N seconds so the admin dashboard sees the device as
   online.
7. Auto-restarts on device boot.

## Zero hardcoding

Apart from the user-entered server URL + API key + branch ID + device name
on first launch, nothing is hardcoded. All printer IPs, codepages, copy
counts, station mappings, polling intervals, and sound preferences are
fetched from `/ops/api/devices/<id>/config` and refreshed every 5 minutes
(plus immediately after every SSE reconnect).

## Project structure

```
android/
├── settings.gradle.kts
├── build.gradle.kts                 # root, plugin versions
├── gradle.properties
├── gradle/wrapper/gradle-wrapper.properties
└── app/
    ├── build.gradle.kts             # app module
    ├── proguard-rules.pro
    └── src/main/
        ├── AndroidManifest.xml
        ├── res/                     # icons, themes, strings, network config
        └── java/com/sumo/printhub/
            ├── PrintHubApp.kt       # Hilt Application + notification channels
            ├── MainActivity.kt
            ├── di/AppModule.kt      # Hilt singletons
            ├── data/
            │   ├── api/PrintHubApi.kt   # OkHttp REST calls
            │   ├── api/SseClient.kt     # OkHttp SSE wrapper -> Flow
            │   ├── model/Models.kt      # @Serializable DTOs
            │   ├── local/SecurePrefs.kt # EncryptedSharedPreferences
            │   ├── local/ConfigCache.kt # last-known-good config cache
            │   └── repository/PrintHubRepository.kt   # SSE/poll/print pipeline
            ├── print/
            │   ├── EscPos.kt        # raw ESC/POS byte constants
            │   ├── HebrewPrinter.kt # ISO-8859-8 encoding with safe fallback
            │   ├── BonBuilder.kt    # checker + payment + station bons
            │   ├── TcpPrinter.kt    # raw TCP socket sender with retries
            │   └── PrintOrchestrator.kt  # default printer + station routing
            ├── service/
            │   ├── PrintHubService.kt   # foreground service owning SSE + prints
            │   └── BootReceiver.kt      # restarts service on boot
            └── ui/
                ├── theme/Theme.kt
                ├── nav/AppNav.kt
                ├── setup/             # first-launch registration
                ├── dashboard/         # live status + print log
                └── settings/          # config, battery exemption, unregister
```

## How to build

1. Install Android Studio Hedgehog (or newer) with Android SDK 34.
2. Open the `android/` folder in Android Studio.
3. Let Gradle sync. The Gradle wrapper jar is downloaded automatically on
   first sync (`gradle/wrapper/gradle-wrapper.properties` already pins
   the Gradle 8.9 distribution).
4. Plug in your tablet (or use an emulator with API 24+) and Run.

If you need to add a real launcher icon: replace the placeholder
`drawable/ic_launcher_foreground.xml` with the SUMO mark, or generate a
new adaptive icon via Android Studio's Image Asset wizard.

## First-launch flow

1. The app shows the Setup screen.
2. Operator enters: server URL, API key (issued by admin → API Keys page),
   branch ID, device name.
3. App generates a stable `device_id` (`android-<UUID>`) once and stores
   it in EncryptedSharedPreferences so it survives reinstalls of the
   keystore.
4. App calls `POST /ops/api/devices/register` → receives the server-side
   `id` (the `device_db_id`).
5. App fetches `GET /ops/api/devices/<id>/config` and starts the
   foreground service.
6. From then on, the operator sees the live dashboard.

## Server endpoints used

All defined in `docs/android-app-api-spec.md` and `swagger_spec.py`:

- `POST /ops/api/devices/register`
- `POST /ops/api/devices/heartbeat`
- `GET /ops/api/devices/<id>/config`
- `GET /ops/api/orders/stream` (SSE)
- `GET /ops/api/orders/unprinted`
- `POST /ops/api/orders/<id>/ack`
- `POST /ops/api/orders/<id>/print-status`
- `POST /ops/api/orders/mark-printed`
- `POST /ops/api/device/log-error`

## ESC/POS output parity

`BonBuilder.kt` produces byte-for-byte equivalent output to the legacy
`print_agent.py` so kitchens see no visual change after switching from
the Mac-based agent to the Android tablet:

- Same RTL Hebrew layout
- Same checker/payment/station bon sequences
- Same dashed/double-width separators and *** type *** banner
- Same `ESC @ ` init + `ESC t <codepage>` codepage selection
- Same `GS V 0` full-cut after `cut_feed_lines` newlines

## Battery / reliability notes

- The print pipeline runs in a `FOREGROUND_SERVICE_DATA_SYNC` foreground
  service with a low-priority sticky notification.
- A `PARTIAL_WAKE_LOCK` is held while the service runs.
- Settings → "Exempt from battery optimisation" deep-links to the system
  prompt; recommended for any tablet that runs 24/7.
- The service is restarted on `BOOT_COMPLETED` (and
  `LOCKED_BOOT_COMPLETED`) once the device is registered.
- Print operations are serialised through a mutex so concurrent SSE +
  poll deliveries can't double-print, with an additional 120-second
  per-order id de-dupe set.
