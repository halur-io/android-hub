# SUMO Android Print Hub — API & Architecture Specification

> **Version**: 1.1  
> **Last Updated**: 2026-04-08  
> **Audience**: Android Studio developer or AI agent building the SUMO restaurant tablet print app

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Zero-Hardcoding Principle](#2-zero-hardcoding-principle)
3. [Authentication](#3-authentication)
4. [Device Lifecycle](#4-device-lifecycle)
5. [API Reference](#5-api-reference)
6. [Server-Sent Events (SSE) — Real-Time Order Stream](#6-server-sent-events-sse--real-time-order-stream)
7. [ESC/POS Printing Reference](#7-escpos-printing-reference)
8. [Bon Building Logic](#8-bon-building-logic)
9. [TCP/IP Socket Printing Workflow](#9-tcpip-socket-printing-workflow)
10. [Print Routing Logic](#10-print-routing-logic)
11. [Notification & Sound Behavior](#11-notification--sound-behavior)
12. [Hebrew/RTL Text Encoding](#12-hebrewrtl-text-encoding)
13. [First-Launch Setup Flow](#13-first-launch-setup-flow)
14. [Sample Data Payloads](#14-sample-data-payloads)

---

## 1. Architecture Overview

```
┌─────────────────┐         HTTPS/SSE          ┌──────────────────┐
│  Android Tablet  │ ◄──────────────────────►  │   SUMO Server    │
│  (Print Hub App) │                            │  (Flask/Python)  │
└────────┬────────┘                            └──────────────────┘
         │
         │  TCP/IP raw bytes (port 9100)
         ▼
┌─────────────────┐
│  Thermal Printer │  (ESC/POS, 80mm, e.g. HSPOS HS-C830ULWB)
│  on local LAN    │
└─────────────────┘
```

The Android tablet app acts as a **print hub** — it connects to the SUMO server over HTTPS to receive orders, then sends ESC/POS byte sequences to thermal printers over the local network via raw TCP sockets.

**Key flows:**
1. **SSE stream** — The app maintains a persistent SSE connection to receive new orders in real time.
2. **Polling fallback** — If SSE drops, the app polls `/ops/api/orders/unprinted` every N seconds (configurable from server).
3. **Print** — On receiving an order, the app builds ESC/POS byte sequences and sends them to the assigned printer(s) via TCP.
4. **Acknowledge** — The app calls `/ops/api/orders/<id>/ack` to confirm receipt, then `/ops/api/orders/mark-printed` after successful printing.
5. **Heartbeat** — Every 30 seconds (configurable), the app sends a heartbeat so the admin dashboard knows the tablet is online.

---

## 2. Zero-Hardcoding Principle

**The Android app hardcodes NOTHING except the initial server URL entered on first setup.**

Everything else comes from the server via the config API:

| Setting | Source |
|---|---|
| Branch assignment | Server (device registration + config API) |
| Printer IPs and ports | Server (`/ops/api/devices/<id>/config`) |
| Poll interval | Server config (`poll_interval_seconds`) |
| SSE reconnect delay | Server config (`sse_reconnect_delay_ms`) |
| Heartbeat interval | Server config (`heartbeat_interval_seconds`) |
| Sound preferences | Server config (`sound_enabled`, `sound_file`) |
| Notification preferences | Server config (`notification_enabled`) |
| Text encoding | Server config (`encoding`) |
| ESC/POS codepage number | Server config (`codepage_num`) |
| Station-to-printer mapping | Server config (`station_map`) |
| Checker/payment bon copies | Server config (per printer in `printers` array) |
| Default printer | Server config (`default_printer`) |

**The admin can remotely reconfigure any device from the dashboard without touching the tablet.** The app periodically re-fetches its config (recommended: every 5 minutes or on SSE reconnect).

---

## 3. Authentication

All API endpoints use the `X-Print-Key` header for authentication.

```
X-Print-Key: <your-api-key>
```

The API key is a shared secret configured as the `PRINT_AGENT_KEY` environment variable on the server. The same key is used by the legacy Python print agent and the new Android app.

**Alternative**: The key can also be passed as a query parameter `?key=<your-api-key>` (useful for SSE connections where custom headers may be difficult).

**Important**: Store the API key securely on the device (Android Keystore or EncryptedSharedPreferences). Never expose it in logs or UI.

---

## 4. Device Lifecycle

### 4.1 First Launch — Registration

1. User opens the app for the first time.
2. User enters the **server URL** (e.g., `https://sumo.example.com`) and **API key**.
3. The app generates a unique `device_id` (e.g., `android-<UUID>`).
4. The app calls `POST /ops/api/devices/register` with `device_id`, `branch_id`, and `device_name`.
5. Server responds with the device record including `id` (database ID).
6. The app calls `GET /ops/api/devices/<id>/config` to fetch its full configuration.
7. The app stores all settings locally and is ready to operate.

### 4.2 Normal Operation

```
┌─────────┐
│  Start   │
└────┬────┘
     ▼
┌──────────────────┐
│ Fetch config     │◄──────── every 5 minutes
│ from server      │          or on SSE reconnect
└────┬─────────────┘
     ▼
┌──────────────────┐
│ Open SSE stream  │◄──────── reconnect on drop
│ /ops/api/orders/ │          with configured delay
│ stream           │
└────┬─────────────┘
     ▼
┌──────────────────┐
│ On new order:    │
│ 1. Play sound    │
│ 2. Show notif    │
│ 3. Build bons    │
│ 4. Print via TCP │
│ 5. ACK order     │
│ 6. Mark printed  │
└──────────────────┘
     ▼
┌──────────────────┐
│ Heartbeat loop   │◄──────── every 30 seconds
│ POST heartbeat   │
└──────────────────┘
```

### 4.3 Heartbeat

- The app sends `POST /ops/api/devices/heartbeat` every 30 seconds (configurable via `heartbeat_interval_seconds`).
- If the server receives no heartbeat for 2 minutes, it marks the device as offline.
- The admin dashboard shows device online/offline status in real time.

### 4.4 Config Refresh

- On SSE reconnect, fetch config again.
- Periodically (every 5 minutes), re-fetch config to pick up any admin changes (new printer, changed station mapping, etc.).

---

## 5. API Reference

**Base URL**: `https://<your-server-domain>/ops`

All endpoints return JSON. All require the `X-Print-Key` header unless noted otherwise.

---

### 5.1 `GET /ops/api/orders/unprinted`

Fetch all unprinted orders (polling fallback).

**Query Parameters:**
| Param | Type | Required | Description |
|---|---|---|---|
| `branch_id` | integer | No | Filter by branch |

**Response:**
```json
{
  "ok": true,
  "orders": [
    {
      "id": 42,
      "order_number": "ORD-260407-1234",
      "order_type": "delivery",
      "status": "pending",
      "branch_id": 1,
      "customer_name": "ישראל ישראלי",
      "customer_phone": "0501234567",
      "delivery_address": "רחוב הרצל 5",
      "delivery_city": "תל אביב",
      "delivery_notes": "קומה 3",
      "customer_notes": "בלי בצל",
      "subtotal": 120,
      "delivery_fee": 15,
      "discount_amount": 0,
      "total_amount": 135,
      "payment_method": "cash",
      "coupon_code": "",
      "created_at": "07/04/2026 14:30",
      "items": [
        {
          "menu_item_id": 10,
          "name_he": "פאד תאי",
          "print_name": "פאד תאי עוף",
          "qty": 2,
          "price": 52,
          "options": [
            {"choice_name_he": "חריף"}
          ],
          "excluded_ingredients": ["בוטנים"]
        }
      ],
      "items_by_station": {
        "ווק": [
          {"name_he": "פאד תאי", "print_name": "פאד תאי עוף", "qty": 2, "options": [...], "excluded_ingredients": [...]}
        ],
        "סושי": [
          {"name_he": "סלמון רול", "qty": 1, "options": []}
        ]
      }
    }
  ]
}
```

---

### 5.2 `POST /ops/api/orders/mark-printed`

Mark orders as printed after successful printing.

**Request Body:**
```json
{
  "order_ids": [42, 43, 44]
}
```

**Response:**
```json
{
  "ok": true,
  "message": "3 orders marked as printed"
}
```

---

### 5.3 `GET /ops/api/branch/<branch_id>/printers`

Fetch printer configuration for a branch.

**Response:**
```json
{
  "ok": true,
  "branch_id": 1,
  "branch_name": "סומו ראשון",
  "default_printer": {
    "id": 1,
    "name": "Main Printer",
    "ip_address": "192.168.1.100",
    "port": 9100,
    "encoding": "iso-8859-8",
    "codepage_num": 36,
    "cut_feed_lines": 6,
    "checker_copies": 2,
    "payment_copies": 1,
    "is_default": true,
    "stations": []
  },
  "station_map": {
    "ווק": {"id": 2, "name": "Wok Printer", "ip_address": "192.168.1.101", "port": 9100, ...},
    "סושי": {"id": 3, "name": "Sushi Printer", "ip_address": "192.168.1.102", "port": 9100, ...}
  },
  "printers": [...]
}
```

---

### 5.4 `GET /ops/api/orders/stream` (SSE)

Server-Sent Events stream for real-time order notifications.

**Query Parameters:**
| Param | Type | Required | Description |
|---|---|---|---|
| `key` | string | Yes | API key (since SSE doesn't easily support custom headers) |
| `branch_id` | integer | No | Filter events by branch |

**Connection:**
```
GET /ops/api/orders/stream?key=<api-key>&branch_id=1
Accept: text/event-stream
```

**Events:**

Connection established:
```
data: {"type":"connected"}
```

New order:
```
data: {"type":"new_order","id":42,"order_number":"ORD-260407-1234","order_type":"delivery","branch_id":1,"customer_name":"ישראל ישראלי","total_amount":135,"items_count":3,"created_at":"2026-04-07T11:30:00Z"}
```

Order status changed (sent when any order status is updated via Ops or KDS):
```
data: {"type":"order_status_changed","id":42,"order_number":"ORD-260407-1234","order_type":"delivery","branch_id":1,"old_status":"pending","new_status":"confirmed","customer_name":"ישראל ישראלי","total_amount":135,"updated_at":"2026-04-07T11:35:00Z"}
```

Possible status values: `pending`, `confirmed`, `preparing`, `ready`, `delivered`, `pickedup`, `cancelled`

Keepalive (every ~25 seconds):
```
: keepalive
```

**Reconnection behavior:**
- On disconnect, wait `sse_reconnect_delay_ms` (default 3000ms) then reconnect.
- On reconnect, re-fetch config and poll `/ops/api/orders/unprinted` to catch any missed orders.

---

### 5.5 `POST /ops/api/devices/register`

Register a new device or update an existing registration.

**Request Body:**
```json
{
  "device_id": "android-a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "branch_id": 1,
  "device_name": "Tablet Cashier 1"
}
```

**Response:**
```json
{
  "ok": true,
  "device": {
    "id": 5,
    "device_id": "android-a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "branch_id": 1,
    "device_name": "Tablet Cashier 1",
    "last_heartbeat": "2026-04-07T11:30:00Z",
    "is_online": true,
    "registered_at": "2026-04-07T11:30:00Z",
    "config": {}
  }
}
```

---

### 5.6 `POST /ops/api/devices/heartbeat`

Send periodic heartbeat to keep device marked as online.

**Request Body:**
```json
{
  "device_id": "android-a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Response:**
```json
{
  "ok": true,
  "server_time": "2026-04-07T11:30:30Z"
}
```

---

### 5.7 `GET /ops/api/devices`

List all registered print devices (admin view). Also accepts ops session auth.

**Response:**
```json
{
  "ok": true,
  "devices": [
    {
      "id": 5,
      "device_id": "android-a1b2c3d4...",
      "branch_id": 1,
      "device_name": "Tablet Cashier 1",
      "last_heartbeat": "2026-04-07T11:30:00Z",
      "is_online": true,
      "registered_at": "2026-04-07T11:00:00Z",
      "config": {"sound_enabled": true, "poll_interval_seconds": 5}
    }
  ]
}
```

---

### 5.8 `GET /ops/api/devices/<id>/config`

Fetch full configuration for a device. The device uses its database `id` (returned from registration).

**Response:**
```json
{
  "ok": true,
  "config": {
    "device_id": "android-a1b2c3d4...",
    "device_db_id": 5,
    "branch_id": 1,
    "branch_name": "סומו ראשון",
    "poll_interval_seconds": 5,
    "sse_reconnect_delay_ms": 3000,
    "heartbeat_interval_seconds": 30,
    "sound_enabled": true,
    "sound_file": "new_order.mp3",
    "notification_enabled": true,
    "encoding": "iso-8859-8",
    "codepage_num": 32,
    "default_printer": {
      "id": 1,
      "name": "Main Printer",
      "ip_address": "192.168.1.100",
      "port": 9100,
      "encoding": "iso-8859-8",
      "codepage_num": 36,
      "cut_feed_lines": 6,
      "checker_copies": 2,
      "payment_copies": 1,
      "is_default": true,
      "stations": []
    },
    "station_map": {
      "ווק": {"id": 2, "name": "Wok Printer", "ip_address": "192.168.1.101", "port": 9100, ...},
      "סושי": {"id": 3, "name": "Sushi Printer", "ip_address": "192.168.1.102", "port": 9100, ...}
    },
    "printers": [...]
  }
}
```

---

### 5.9 `PUT /ops/api/devices/<id>/config`

Update device configuration remotely (admin operation). Accepts API key or ops session auth.

**Request Body:**
```json
{
  "device_name": "Kitchen Tablet",
  "branch_id": 2,
  "config": {
    "poll_interval_seconds": 10,
    "sound_enabled": false,
    "notification_enabled": true,
    "sse_reconnect_delay_ms": 5000
  }
}
```

**Response:**
```json
{
  "ok": true,
  "device": { ... }
}
```

---

### 5.10 `POST /ops/api/orders/<id>/ack`

Acknowledge receipt of an order (before printing). This lets the dashboard show "received by tablet" as a distinct state from "printed". The server records `bon_acked_at` timestamp and `bon_acked_device_id` on the order record for structured querying.

**Request Body (optional):**
```json
{
  "device_id": "android-a1b2c3d4..."
}
```

**Response:**
```json
{
  "ok": true,
  "message": "Order 42 acknowledged"
}
```

---

### 5.11 `POST /ops/api/orders/<id>/print-status`

Report the print result for an order. The app calls this **after** attempting to print — whether it succeeded, partially succeeded, or failed. This is the primary mechanism for the server to know the print outcome.

**Request Body:**
```json
{
  "status": "success",
  "device_id": "android-a1b2c3d4...",
  "stations_printed": ["סושי", "ווק"],
  "stations_failed": [],
  "error": ""
}
```

**Possible `status` values:**

| Status | Meaning | Server Behavior |
|---|---|---|
| `success` | All stations printed OK | Sets `bon_printed=true`, clears errors |
| `partial` | Some stations printed, some failed | Sets `bon_printed=true`, records error details |
| `error` | Complete print failure | Keeps `bon_printed=false`, records error |

**Response:**
```json
{
  "ok": true,
  "message": "Print status recorded for order 42",
  "bon_printed": true,
  "attempts": 1
}
```

**Example — Error:**
```json
{
  "status": "error",
  "device_id": "android-a1b2c3d4...",
  "error": "Printer 192.168.1.100:9100 connection refused"
}
```

**Example — Partial:**
```json
{
  "status": "partial",
  "device_id": "android-a1b2c3d4...",
  "stations_printed": ["סושי"],
  "stations_failed": ["ווק"],
  "error": "Wok printer timeout after 5s"
}
```

---

### 5.12 `GET /ops/api/orders/<id>/detail`

Fetch full detail for a single order, including print status. Useful when the app receives a new-order SSE event and needs the complete order data.

**Response:**
```json
{
  "ok": true,
  "order": {
    "id": 42,
    "order_number": "ORD-260407-1234",
    "order_type": "delivery",
    "status": "confirmed",
    "branch_id": 1,
    "customer_name": "ישראל ישראלי",
    "customer_phone": "0501234567",
    "delivery_address": "רחוב הרצל 5",
    "delivery_city": "תל אביב",
    "delivery_notes": "קומה 3",
    "customer_notes": "בלי בצל",
    "subtotal": 120,
    "delivery_fee": 15,
    "discount_amount": 0,
    "total_amount": 135,
    "payment_method": "cash",
    "coupon_code": "",
    "created_at": "07/04 14:30",
    "items": [...],
    "items_by_station": {
      "סושי": [...],
      "ווק": [...]
    },
    "bon_printed": false,
    "bon_printed_at": null,
    "bon_acked_at": null,
    "bon_acked_device_id": "",
    "bon_print_error": "",
    "bon_print_attempts": 0
  }
}
```

---

### 5.13 `POST /ops/api/device/log-error`

Report a device-level error to the server (not tied to a specific print attempt). Use for connection errors, app crashes, config issues, etc. Errors are logged server-side and optionally attached to an order.

**Request Body:**
```json
{
  "device_id": "android-a1b2c3d4...",
  "error_type": "printer_connection",
  "error_message": "Cannot reach 192.168.1.100:9100 — Connection refused",
  "order_id": 42,
  "extra": {
    "printer_ip": "192.168.1.100",
    "retry_count": 3
  }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `device_id` | string | Yes | The device identifier |
| `error_type` | string | Yes | Category: `printer_connection`, `sse_disconnect`, `config_fetch`, `general` |
| `error_message` | string | Yes | Human-readable error description |
| `order_id` | integer | No | If error is related to a specific order |
| `extra` | object | No | Any additional context data |

**Response:**
```json
{
  "ok": true,
  "message": "error logged"
}
```

---

## Complete Order Lifecycle (Android App)

The full lifecycle for an order from the app's perspective:

```
1. RECEIVE      →  SSE event: {"type":"new_order", "id": 42, ...}
2. FETCH        →  GET /ops/api/orders/42/detail  (get full order data)
3. ACK          →  POST /ops/api/orders/42/ack     (mark as received by tablet)
4. PRINT        →  Build ESC/POS bons, send to printers via TCP
5. REPORT       →  POST /ops/api/orders/42/print-status
                    status: "success" | "partial" | "error"
6. MARK PRINTED →  POST /ops/api/orders/mark-printed  {"order_ids": [42]}
                    (only if status was "success" or "partial")
```

If step 4 fails completely, the order stays unprinted and will appear again on the next poll of `/ops/api/orders/unprinted`. The app can retry printing and report again.

---

## 6. Server-Sent Events (SSE) — Real-Time Order Stream

### Android Implementation

Use `OkHttp` or `okhttp-sse` library for SSE on Android:

```kotlin
// Pseudocode — Android Kotlin
val url = "$serverUrl/ops/api/orders/stream?key=$apiKey&branch_id=$branchId"
val request = Request.Builder().url(url).build()

val sseListener = object : EventSourceListener() {
    override fun onEvent(eventSource: EventSource, id: String?, type: String?, data: String) {
        val json = JSONObject(data)
        when (json.optString("type")) {
            "connected" -> Log.d("SSE", "Connected to order stream")
            "new_order" -> {
                val orderId = json.getInt("id")
                val orderNumber = json.getString("order_number")
                // 1. Play notification sound
                // 2. Show Android notification
                // 3. Fetch full order from /ops/api/orders/<id>/detail
                // 4. Build and print bons
                // 5. ACK and mark printed
            }
            "order_status_changed" -> {
                val orderId = json.getInt("id")
                val oldStatus = json.getString("old_status")
                val newStatus = json.getString("new_status")
                // Update local order state
                // Show notification if relevant (e.g., cancelled)
            }
        }
    }

    override fun onFailure(eventSource: EventSource, t: Throwable?, response: Response?) {
        // Wait sse_reconnect_delay_ms then reconnect
        // Also poll /ops/api/orders/unprinted to catch missed orders
    }
}

val eventSource = EventSources.createFactory(client)
    .newEventSource(request, sseListener)
```

### Fallback Polling

If SSE is unavailable or drops, poll `GET /ops/api/orders/unprinted?branch_id=<id>` at the interval specified by `poll_interval_seconds` from config.

---

## 7. ESC/POS Printing Reference

### 7.1 Control Codes

All byte sequences used by the SUMO print system:

| Name | Bytes (hex) | Description |
|---|---|---|
| `ESC` | `0x1B` | Escape character |
| `GS` | `0x1D` | Group separator |
| `INIT` | `0x1B 0x40` | Initialize printer (reset) |
| `CUT_FULL` | `0x1D 0x56 0x00` | Full paper cut |
| `ALIGN_LEFT` | `0x1B 0x61 0x00` | Left alignment |
| `ALIGN_CENTER` | `0x1B 0x61 0x01` | Center alignment |
| `ALIGN_RIGHT` | `0x1B 0x61 0x02` | Right alignment |
| `FONT_NORMAL` | `0x1B 0x21 0x00` | Normal font size |
| `FONT_DOUBLE_H` | `0x1B 0x21 0x10` | Double height |
| `FONT_DOUBLE_W` | `0x1B 0x21 0x20` | Double width |
| `FONT_DOUBLE` | `0x1B 0x21 0x30` | Double width + height |
| `BOLD_ON` | `0x1B 0x45 0x01` | Bold on |
| `BOLD_OFF` | `0x1B 0x45 0x00` | Bold off |
| `UNDERLINE_ON` | `0x1B 0x2D 0x01` | Underline on |
| `UNDERLINE_OFF` | `0x1B 0x2D 0x00` | Underline off |
| `INVERT_ON` | `0x1D 0x42 0x01` | White on black |
| `INVERT_OFF` | `0x1D 0x42 0x00` | Normal (black on white) |

### 7.2 Codepage Setup

Set the character codepage for Hebrew text:

```
ESC 't' <codepage_number>
→  0x1B 0x74 <n>
```

- Codepage **32** = ISO-8859-8 (Hebrew) on HSPOS printers
- Codepage **36** = ISO-8859-8 on SNBC printers
- The exact codepage number comes from the printer config (`codepage_num` field)

### 7.3 Text Encoding

All text must be encoded as **ISO-8859-8** bytes before sending to the printer. See [Section 12](#12-hebrewrtl-text-encoding) for details.

### 7.4 Paper Cut Sequence

Before cutting, feed N blank lines (configurable via `cut_feed_lines`, default 6):

```
<N newlines>  +  GS V 0x00
```

---

## 8. Bon Building Logic

The system prints three types of bons (receipts) per order:

### 8.1 Checker Bon (Main Order Receipt)

Printed on the **default printer**. Number of copies controlled by `checker_copies` (default: 2).

**Layout (right-aligned for Hebrew RTL):**

```
[ALIGN_RIGHT][FONT_NORMAL]
{phone}  :טלפון
SUMO
──────────────────────────────────────────
[ALIGN_RIGHT][FONT_NORMAL][BOLD]
{customer_name} - הזמנה {order_number}
[BOLD_OFF]
{created_at}

[If customer_notes:][BOLD]
הערות: {customer_notes}
[BOLD_OFF]
[If delivery_notes:][BOLD]
הערות משלוח: {delivery_notes}
[BOLD_OFF]
──────────────────────────────────────────
[For each item:]
  [ALIGN_RIGHT][FONT_DOUBLE_H][BOLD]
  {item_name} {qty}
  [BOLD_OFF][FONT_NORMAL]
  [For each option:]
    {option_name}
  [For each excluded_ingredient:]
    [BOLD]ללא {ingredient}[BOLD_OFF]
  ──────────────────────────────────────────

[If delivery_address:]
  [ALIGN_RIGHT][FONT_NORMAL]
  כתובת: {address}, {city}
  ──────────────────────────────────────────

[ALIGN_CENTER][FONT_DOUBLE][INVERT]
 SUMO - {order_number} 
[INVERT_OFF][FONT_NORMAL]

[ALIGN_CENTER][FONT_DOUBLE][BOLD]
*** {order_type_he} ***
[BOLD_OFF][FONT_NORMAL]

[ALIGN_CENTER]
SUMO - {order_number}
{phone}
--- CUT ---
```

**Field mapping:**
- `order_type_he`: `"משלוח"` for delivery, `"איסוף עצמי"` for pickup
- `item_name`: Use `print_name` → `name_he` → `item_name_he` → `name` (first non-empty)
- `qty`: Use `qty` → `quantity` (default 1)

### 8.2 Payment Bon

Printed on the **default printer**. Number of copies controlled by `payment_copies` (default: 1).

**Layout:**

```
[ALIGN_RIGHT][FONT_NORMAL]
{phone}  :טלפון
SUMO - בון תשלום
──────────────────────────────────────────
[ALIGN_RIGHT][BOLD]
{customer_name} - הזמנה {order_number}
[BOLD_OFF]
{order_type_he} | {created_at}
──────────────────────────────────────────
[For each item:]
  [ALIGN_RIGHT][BOLD]
  {total}  {item_name} {qty}
  [BOLD_OFF]
──────────────────────────────────────────
[ALIGN_RIGHT]
{subtotal} :סכום
[If delivery_fee > 0:]
  {delivery_fee} :משלוח
[If discount_amount > 0:]
  {discount_amount}- :הנחה
══════════════════════════════════════════
[FONT_DOUBLE][BOLD]
{total_amount} :לתשלום
[BOLD_OFF][FONT_NORMAL]

[ALIGN_CENTER]
תשלום: {payment_method}
{current_time HH:MM}
--- CUT ---
```

### 8.3 Station Bon (Kitchen/Prep Station)

Printed on the **station-specific printer** (from `station_map`). One bon per station that has items in the order.

**Layout:**

```
[ALIGN_CENTER][FONT_DOUBLE][BOLD]
{station_name}
[BOLD_OFF][FONT_NORMAL]
{order_number} | {created_at}
──────────────────────────────────────────
[If customer_notes:]
  [ALIGN_RIGHT][BOLD]
  הערות: {customer_notes}
  [BOLD_OFF]

[For each item in this station:]
  [ALIGN_RIGHT][FONT_DOUBLE_H][BOLD]
  {item_name} {qty}
  [BOLD_OFF][FONT_NORMAL]
  [For each option:]
    {option_name}
  [For each excluded_ingredient:]
    [BOLD]ללא {ingredient}[BOLD_OFF]

──────────────────────────────────────────
[ALIGN_CENTER][FONT_DOUBLE][BOLD]
*** {order_type_he} ***
[BOLD_OFF][FONT_NORMAL]
{order_number} | {station_name} | {current_time HH:MM}
--- CUT ---
```

### 8.4 Printing Order

For each order:
1. On the **default printer**: print `checker_copies` checker bons, then `payment_copies` payment bons — all in a single TCP connection (concatenate the byte buffers).
2. For **station bons**: group items by station → find the printer for each station → for each printer, concatenate all station bons destined for it → send in a single TCP connection.

---

## 9. TCP/IP Socket Printing Workflow

### Connection Flow

```
1. Create TCP socket
2. Set timeout to 5 seconds
3. Connect to printer_ip:printer_port (default port 9100)
4. Send all ESC/POS bytes via sendAll()
5. Close socket
```

### Android Kotlin Pseudocode

```kotlin
fun sendToPrinter(data: ByteArray, ip: String, port: Int): Boolean {
    return try {
        val socket = Socket()
        socket.soTimeout = 5000
        socket.connect(InetSocketAddress(ip, port), 5000)
        socket.getOutputStream().write(data)
        socket.getOutputStream().flush()
        socket.close()
        true
    } catch (e: Exception) {
        Log.e("PRINTER", "Error printing to $ip:$port: ${e.message}")
        false
    }
}
```

### Important Notes

- The printer port is almost always **9100** but is configurable per printer in the config.
- The socket connection is a simple raw TCP connection — no protocol negotiation, no HTTP.
- Send the entire byte buffer in one `write()` call for reliability.
- If the connection fails, the app should retry once after a short delay, then mark the print as failed and alert the user.
- Android requires network operations on a background thread (use Coroutines or a background executor).

---

## 10. Print Routing Logic

### Station Map

Each menu item is assigned to a **print station** (e.g., "ווק", "סושי", "ברים", "כללי"). The server provides `items_by_station` in the order data, which groups items by their station name.

### Printer Resolution

For each station name, look up the printer in `station_map` from the config:

```
station_map["ווק"]  → Wok Printer (192.168.1.101:9100)
station_map["סושי"] → Sushi Printer (192.168.1.102:9100)
```

If a station name is not in the map, fall back to the **default printer**.

If no default printer is configured and the station has no mapped printer, the items **will not print** — log a warning.

### Aggregation

Multiple stations may map to the same physical printer. Group all station bons destined for the same printer IP:port and send them in a single TCP connection.

---

## 11. Notification & Sound Behavior

### On New Order (SSE event or poll result)

1. **Play notification sound**:
   - Only if `sound_enabled` is `true` in config.
   - Use the sound file specified by `sound_file` in config (default: `new_order.mp3`).
   - Play at maximum volume. Use `AudioManager` to ensure media volume is at max.
   - Use `MediaPlayer` or `SoundPool` for playback.

2. **Show Android notification**:
   - Only if `notification_enabled` is `true` in config.
   - Use a high-priority notification channel with sound and vibration.
   - Title: `"הזמנה חדשה #{order_number}"`
   - Body: `"{customer_name} — {order_type_he} — ₪{total_amount}"`
   - Auto-cancel after 30 seconds or on tap.

3. **Wake screen**: If the tablet is sleeping, use a wake lock to turn on the screen briefly.

### Vibration Pattern

```kotlin
val pattern = longArrayOf(0, 500, 200, 500, 200, 500)
vibrator.vibrate(VibrationEffect.createWaveform(pattern, -1))
```

---

## 12. Hebrew/RTL Text Encoding

### Encoding

All Hebrew text must be encoded as **ISO-8859-8** before sending to the printer.

```kotlin
fun encodeText(text: String): ByteArray {
    val charset = Charset.forName("ISO-8859-8")
    val encoder = charset.newEncoder()
    val sb = StringBuilder()
    for (ch in text) {
        if (encoder.canEncode(ch)) {
            sb.append(ch)
        } else {
            sb.append('?')
        }
    }
    return sb.toString().toByteArray(charset)
}
```

### Codepage Command

Before printing any text, send the codepage setup command:

```kotlin
val codepageCmd = byteArrayOf(0x1B, 0x74, codepageNum.toByte())
```

Where `codepageNum` comes from the printer config (typically 32 for HSPOS, 36 for SNBC).

### RTL Notes

- ESC/POS printers with Hebrew codepages handle RTL text natively.
- Text alignment commands (`ALIGN_RIGHT`) position the text correctly.
- Numbers and Latin characters within Hebrew text are handled by the printer's bidirectional algorithm.
- The `print_name` field from the server is already in the correct display form.

---

## 13. First-Launch Setup Flow

### UI Flow

```
┌─────────────────────────────────┐
│     SUMO Print Hub Setup        │
│                                 │
│  Server URL:                    │
│  ┌───────────────────────────┐  │
│  │ https://sumo.example.com  │  │
│  └───────────────────────────┘  │
│                                 │
│  API Key:                       │
│  ┌───────────────────────────┐  │
│  │ ••••••••••••••••••••      │  │
│  └───────────────────────────┘  │
│                                 │
│  Branch:                        │
│  ┌───────────────────────────┐  │
│  │ ▼ סומו ראשון             │  │
│  └───────────────────────────┘  │
│                                 │
│  Device Name:                   │
│  ┌───────────────────────────┐  │
│  │ Tablet Cashier 1          │  │
│  └───────────────────────────┘  │
│                                 │
│  ┌───────────────────────────┐  │
│  │       Connect & Setup     │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

### Steps

1. User enters **Server URL** and **API Key**.
2. App validates by calling `GET /ops/api/branch/1/printers` (or any authenticated endpoint) to verify connectivity.
3. App fetches branch list via `GET /api/branches` (public endpoint, no auth needed).
4. User selects **branch** and enters a **device name**.
5. App generates a UUID-based `device_id`.
6. App calls `POST /ops/api/devices/register`.
7. App receives `device.id` (database ID) and stores it.
8. App calls `GET /ops/api/devices/<id>/config` to fetch full config.
9. App stores everything in local storage (EncryptedSharedPreferences).
10. App transitions to the main screen and begins the SSE connection + heartbeat loop.

### Stored Settings (on device)

| Key | Example |
|---|---|
| `server_url` | `https://sumo.example.com` |
| `api_key` | `sumo-print-2024-secure` |
| `device_id` | `android-a1b2c3d4-...` |
| `device_db_id` | `5` |
| `branch_id` | `1` |
| `device_name` | `Tablet Cashier 1` |

Everything else comes from the config API and is refreshed periodically.

---

## 14. Sample Data Payloads

### 14.1 Full Unprinted Order

```json
{
  "id": 42,
  "order_number": "ORD-260407-1234",
  "order_type": "delivery",
  "status": "pending",
  "branch_id": 1,
  "customer_name": "ישראל ישראלי",
  "customer_phone": "0501234567",
  "delivery_address": "רחוב הרצל 5",
  "delivery_city": "תל אביב",
  "delivery_notes": "קומה 3, דלת שמאל",
  "customer_notes": "בלי בצל בכל המנות",
  "subtotal": 156,
  "delivery_fee": 15,
  "discount_amount": 10,
  "total_amount": 161,
  "payment_method": "credit_card",
  "coupon_code": "WELCOME10",
  "created_at": "07/04/2026 14:30",
  "items": [
    {
      "menu_item_id": 10,
      "name_he": "פאד תאי",
      "name_en": "Pad Thai",
      "print_name": "פאד תאי עוף",
      "qty": 2,
      "price": 52,
      "options": [
        {"choice_name_he": "חריף", "name": "Spicy"}
      ],
      "excluded_ingredients": ["בוטנים"]
    },
    {
      "menu_item_id": 15,
      "name_he": "סלמון רול",
      "name_en": "Salmon Roll",
      "print_name": "סלמון רול 8",
      "qty": 1,
      "price": 52,
      "options": [],
      "excluded_ingredients": []
    }
  ],
  "items_by_station": {
    "ווק": [
      {
        "menu_item_id": 10,
        "name_he": "פאד תאי",
        "print_name": "פאד תאי עוף",
        "qty": 2,
        "price": 52,
        "options": [{"choice_name_he": "חריף"}],
        "excluded_ingredients": ["בוטנים"]
      }
    ],
    "סושי": [
      {
        "menu_item_id": 15,
        "name_he": "סלמון רול",
        "print_name": "סלמון רול 8",
        "qty": 1,
        "price": 52,
        "options": [],
        "excluded_ingredients": []
      }
    ]
  }
}
```

### 14.2 SSE New Order Event

```json
{
  "type": "new_order",
  "id": 42,
  "order_number": "ORD-260407-1234",
  "order_type": "delivery",
  "branch_id": 1,
  "customer_name": "ישראל ישראלי",
  "total_amount": 161,
  "items_count": 2,
  "created_at": "2026-04-07T11:30:00Z"
}
```

### 14.3 Device Registration Request

```json
{
  "device_id": "android-a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "branch_id": 1,
  "device_name": "Tablet Cashier 1"
}
```

### 14.4 Full Config Response

```json
{
  "ok": true,
  "config": {
    "device_id": "android-a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "device_db_id": 5,
    "branch_id": 1,
    "branch_name": "סומו ראשון",
    "poll_interval_seconds": 5,
    "sse_reconnect_delay_ms": 3000,
    "heartbeat_interval_seconds": 30,
    "sound_enabled": true,
    "sound_file": "new_order.mp3",
    "notification_enabled": true,
    "encoding": "iso-8859-8",
    "codepage_num": 32,
    "default_printer": {
      "id": 1,
      "name": "Main Printer",
      "printer_type": "snbc-btp-r880npv",
      "branch_id": 1,
      "ip_address": "192.168.1.100",
      "port": 9100,
      "encoding": "iso-8859-8",
      "codepage_num": 36,
      "cut_feed_lines": 6,
      "is_active": true,
      "display_order": 0,
      "checker_copies": 2,
      "payment_copies": 1,
      "is_default": true,
      "stations": []
    },
    "station_map": {
      "ווק": {
        "id": 2,
        "name": "Wok Printer",
        "printer_type": "escpos",
        "branch_id": 1,
        "ip_address": "192.168.1.101",
        "port": 9100,
        "encoding": "iso-8859-8",
        "codepage_num": 36,
        "cut_feed_lines": 6,
        "is_active": true,
        "display_order": 1,
        "checker_copies": 2,
        "payment_copies": 1,
        "is_default": false,
        "stations": ["ווק"]
      },
      "סושי": {
        "id": 3,
        "name": "Sushi Printer",
        "printer_type": "escpos",
        "branch_id": 1,
        "ip_address": "192.168.1.102",
        "port": 9100,
        "encoding": "iso-8859-8",
        "codepage_num": 36,
        "cut_feed_lines": 6,
        "is_active": true,
        "display_order": 2,
        "checker_copies": 2,
        "payment_copies": 1,
        "is_default": false,
        "stations": ["סושי"]
      }
    },
    "printers": [
      {
        "id": 1,
        "name": "Main Printer",
        "ip_address": "192.168.1.100",
        "port": 9100,
        "is_default": true,
        "stations": []
      },
      {
        "id": 2,
        "name": "Wok Printer",
        "ip_address": "192.168.1.101",
        "port": 9100,
        "is_default": false,
        "stations": ["ווק"]
      },
      {
        "id": 3,
        "name": "Sushi Printer",
        "ip_address": "192.168.1.102",
        "port": 9100,
        "is_default": false,
        "stations": ["סושי"]
      }
    ]
  }
}
```

### 14.5 Heartbeat Request/Response

**Request:**
```json
{"device_id": "android-a1b2c3d4-e5f6-7890-abcd-ef1234567890"}
```

**Response:**
```json
{"ok": true, "server_time": "2026-04-07T11:30:30Z"}
```

### 14.6 Order Acknowledgment

**Request:**
```json
{"device_id": "android-a1b2c3d4-e5f6-7890-abcd-ef1234567890"}
```

**Response:**
```json
{"ok": true, "message": "Order 42 acknowledged"}
```

### 14.7 Mark Printed

**Request:**
```json
{"order_ids": [42, 43]}
```

**Response:**
```json
{"ok": true, "message": "2 orders marked as printed"}
```

---

## Error Handling

All endpoints return a consistent error format:

```json
{
  "ok": false,
  "error": "description of what went wrong"
}
```

**HTTP Status Codes:**
| Code | Meaning |
|---|---|
| 200 | Success |
| 400 | Bad request (missing required fields) |
| 401 | Unauthorized (invalid or missing API key) |
| 404 | Resource not found |
| 500 | Server error |

**Android app should:**
- Retry on 5xx errors with exponential backoff (1s, 2s, 4s, max 30s).
- On 401, prompt user to re-enter API key.
- On 404 for device endpoints, re-register the device.
- Log all errors for debugging.
