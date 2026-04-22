# Standalone Food Ordering Service — API Reference

## URL Prefixes

| Blueprint | URL Prefix | Description |
|---|---|---|
| `order_page` | `/order` | Public-facing ordering |
| `order_dashboard` | `/order-dashboard` | KDS / staff dashboard |

---

## Public Ordering Endpoints (`order_page`)

### `GET /order/`
**Order Page** — Displays the menu with categories, items, cart UI.

**Context Variables:**
- `categories` — List of `MenuCategory` objects with `._order_items` (filtered by availability)
- `delivery_zones` — Active `DeliveryZone` list
- `ordering_disabled`, `ordering_paused`, `ordering_outside_hours` — Status flags
- `ordering_status_message` — Message for blocked/paused state
- `delivery_fee`, `free_delivery_threshold`, `estimated_delivery_time`
- `enable_delivery`, `enable_pickup`
- `settings` — SiteSettings object

**Availability Filtering:**
- Items filtered by `is_available`, `available_days` (7-char bitmask, index 0 = Sunday), `available_from_time`/`available_to_time`
- Each item gets `._order_available` (bool) and `._unavailable_reason` (str or None)

---

### `GET /order/menu-image/<item_id>`
**Menu Item Image** — Serves dish image from database binary storage.

**Response:** Raw image bytes with auto-detected `Content-Type` (JPEG, PNG, WebP, GIF). Returns 404 if item has no `image_data`. Cached for 24 hours via `Cache-Control: public, max-age=86400`.

---

### `POST /order/start-checkout`
**Save Cart & Redirect to Checkout**

**Form Fields:**
| Field | Type | Required | Description |
|---|---|---|---|
| `cart_json` | JSON string | Yes | Array of cart items |
| `order_type` | string | No | `delivery` or `pickup` (default: `delivery`) |
| `utm_source` | string | No | UTM source for attribution |
| `utm_medium` | string | No | UTM medium |
| `utm_campaign` | string | No | UTM campaign |
| `referrer` | string | No | Page referrer URL |

**Cart Item Format:**
```json
{
  "id": 42,
  "name_he": "שווארמה",
  "name_en": "Shawarma",
  "price": 45.0,
  "base_price": 45.0,
  "qty": 2,
  "options": [
    {
      "group_id": 1,
      "group_name_he": "תוספות",
      "choice_id": 5,
      "choice_name_he": "חומוס",
      "price_modifier": 3.0
    }
  ],
  "combo_selections": [
    {
      "slot_index": 0,
      "menu_item_id": 43,
      "item_name_he": "צ'יפס",
      "price_modifier": 0
    }
  ]
}
```

**Response:** 302 redirect to `GET /order/checkout`

---

### `GET /order/checkout`
**Checkout Page** — Shows order summary, delivery/pickup toggle, address input, payment options.

**Requires:** Cart in session (set by `/order/start-checkout`)

**Context Variables:**
- `cart_items`, `cart_json` — Cart data
- `order_type` — `delivery` or `pickup`
- `delivery_zones` — Active zones for city selection
- `subtotal`, `delivery_fee`, `total` — Price calculation
- `time_slots` — Available pickup times (30-min intervals)
- `card_available`, `hyp_sandbox_mode` — Payment availability
- `enable_delivery`, `enable_pickup` — Toggles
- `settings` — SiteSettings object

---

### `POST /order/place`
**Place Order** — Validates cart, creates `FoodOrder` + `FoodOrderItem` records, routes to payment or sends notifications.

**Form Fields:**
| Field | Type | Required | Description |
|---|---|---|---|
| `cart_json` | JSON string | Yes | Cart items array |
| `order_type` | string | Yes | `delivery` or `pickup` |
| `customer_first_name` | string | Yes | First name |
| `customer_last_name` | string | Yes | Last name |
| `customer_phone` | string | Yes | Phone (9-15 digits) |
| `customer_email` | string | No | Email |
| `delivery_address` | string | Delivery | Street + house number |
| `delivery_city` | string | No | City name |
| `delivery_zone_id` | int | No | Selected delivery zone ID |
| `delivery_notes` | string | No | Floor/entry instructions |
| `pickup_time` | string | No | Requested pickup time |
| `customer_notes` | string | No | Allergies, requests |
| `payment_method` | string | No | `cash` (default) or `card` |
| `utm_source` | string | No | UTM tracking |
| `utm_medium` | string | No | UTM tracking |
| `utm_campaign` | string | No | UTM tracking |
| `referrer` | string | No | Referrer URL |

**Server-Side Validation:**
- Verifies each item exists in DB and is currently available
- Recalculates all prices from database (ignores client-sent prices)
- Validates option choices exist, are available, and recalculates price modifiers
- Validates combo selections against combo definition (min/max per slot)
- Enforces minimum order amount for delivery zones
- Checks day-of-week and time-of-day availability for each item

**Response:**
- Card payment → Renders HYP redirect template with payment iframe
- Cash payment → Sends admin + customer notifications → 302 to confirmation

---

### `GET /order/confirm/<order_number>`
**Confirmation Page** — Shows order status and details.

**Context:** `order` (FoodOrder), `settings`

---

### `GET /order/status/<order_number>`
**Live Status (JSON)** — AJAX endpoint for polling order status.

**Response:**
```json
{
  "status": "preparing",
  "status_he": "בהכנה",
  "badge_class": "primary",
  "confirmed_at": "14:30",
  "preparing_at": "14:35",
  "ready_at": null,
  "estimated_ready_at": "15:00",
  "ready_by_time": "15:00"
}
```

---

### `GET /order/track/<token>`
**Customer Tracking Page** — Public tracking accessed via SMS link.

- Token: 24-char URL-safe random string (generated on order creation)
- Expires 48 hours after order completion/cancellation
- Shows real-time status with estimated ready time (rounded to nearest 5 minutes)

---

### `GET /order/payment-success`
**HYP Payment Success Callback**

**Query Params (set by HYP):**
| Param | Description |
|---|---|
| `Order` | Order number |
| `CCode` | Response code (`0` = success) |
| `Id` | Transaction ID |
| `Sign` | HMAC signature |
| `Amount` | Charged amount |
| `Hesh` | Approval number |
| `L4digit` | Last 4 card digits |
| `Brand` | Card brand |

**Behavior:**
1. Verifies HMAC signature against API key
2. Marks order `payment_status='paid'`, `status='confirmed'`
3. Sends admin + customer notifications
4. 302 redirects to confirmation page

---

### `GET /order/payment-failed`
**HYP Payment Failure Callback**

Marks order `payment_status='failed'`, flashes error, redirects to confirmation.

---

### `GET /order/api/streets?city=<city_name>`
**Israeli Streets Autocomplete** — Proxies data.gov.il streets API.

**Query Params:** `city` (Hebrew city name, min 2 chars)

**Response:**
```json
{
  "streets": ["הרצל", "רוטשילד", "ויצמן"],
  "city": "תל אביב",
  "count": 3
}
```

---

## KDS Dashboard Endpoints (`order_dashboard`)

All endpoints except login/auth/logout require PIN authentication via session.

### Authentication

#### `GET /order-dashboard/`
**Root** — Redirects to `/order-dashboard/orders` (authenticated) or `/order-dashboard/login`.

#### `GET /order-dashboard/login`
**Login Page** — Shows staff list and PIN input.

**Context:** `staff_members` (list of active ManagerPIN records)

#### `POST /order-dashboard/auth`
**Authenticate** — Verifies PIN against `ManagerPIN` model.

**Form Fields:** `pin_id` (int), `pin` (string)

**Response:**
```json
{"success": true, "redirect": "/order-dashboard/orders"}
```
```json
{"success": false, "message": "קוד PIN שגוי"}
```

#### `GET /order-dashboard/logout`
**Logout** — Clears KDS session keys, redirects to login.

---

### Order Management

#### `GET /order-dashboard/orders`
**Orders List** — KDS kanban view with status columns and auto-refresh.

**Query Params:**
| Param | Default | Description |
|---|---|---|
| `status` | `active` | Filter: `active`, `all`, or specific status name |
| `date` | today | `YYYY-MM-DD` date to view |

**Context:** `orders`, `all_today`, `new_orders`, `prep_orders`, `ready_orders`, `done_orders`, `status_filter`, `selected_date`, `today`, `prev_date`, `next_date`, `now_ts`, `total_today`, `pending_count`, `active_count`, `revenue_today`, `settings`, `ordering_paused`, `staff_name`

#### `GET /order-dashboard/orders/<order_id>`
**Order Detail** — Full order view with items, timeline, notes, and SMS.

**Context:** `order`, `items`, `settings`, `staff_name`

#### `POST /order-dashboard/orders/<order_id>/update-status`
**Update Status** — Changes order status with optional prep time and note.

**Form Fields:**
| Field | Type | Description |
|---|---|---|
| `status` | string | New status (`confirmed`, `preparing`, `ready`, `delivered`, `pickedup`, `cancelled`) |
| `prep_minutes` | int | Estimated prep time in minutes (sets `estimated_ready_at`) |
| `admin_note` | string | Optional timestamped note (max 500 chars) |

**Response:**
```json
{"success": true, "new_status": "confirmed", "status_label": "אושר"}
```

#### `POST /order-dashboard/orders/<order_id>/add-note`
**Add Admin Note** — Appends timestamped note with staff name.

**Form Fields:** `note` (string)

**Response:** 302 redirect to order detail.

#### `POST /order-dashboard/orders/<order_id>/send-sms`
**Send Custom SMS** — Sends free-text SMS to customer via the `send_sms` callable.

**Form Fields:** `message` (string, max 500 chars)

**Response:** 302 redirect to order detail with flash message.

#### `POST /order-dashboard/orders/<order_id>/cancel`
**Cancel Order** — Sets status to `cancelled` with optional reason.

**Form Fields:** `reason` (string, max 500 chars)

**Response:** 302 redirect to orders list.

#### `GET /order-dashboard/orders/feed`
**Live JSON Feed** — Returns today's orders for auto-refresh (30-second polling).

**Response:** Array of order summary objects:
```json
[
  {
    "id": 42,
    "order_number": "ORD-260314-1234",
    "customer_name": "ישראל ישראלי",
    "customer_phone": "0501234567",
    "order_type": "delivery",
    "status": "preparing",
    "status_label": "בהכנה",
    "total_amount": 89.0,
    "pickup_time": "",
    "created_at": "14:30"
  }
]
```

---

### Settings Management

#### `GET /order-dashboard/settings`
**Settings Page** — Toggle ordering, delivery, pickup; manage working hours; manage dishes.

**Context:** `settings`, `today_hours`, `days_list`, `branch_id`, `time_slots`, `order_dishes`, `staff_name`

#### `POST /order-dashboard/settings`
**Update Settings** — Handles multiple actions via `action` field.

| Action | Description | Response |
|---|---|---|
| `toggle_pause` | Pause/unpause ordering | `{"success": true, "paused": true}` |
| `toggle_ordering` | Enable/disable ordering system | `{"success": true, "enabled": true}` |
| `toggle_delivery` | Enable/disable delivery | `{"success": true, "enabled": true}` |
| `toggle_pickup` | Enable/disable pickup | `{"success": true, "enabled": true}` |
| `toggle_enforce_hours` | Enable/disable hours enforcement | `{"success": true, "enabled": true}` |
| `save_messages` | Save pause/closed/outside-hours messages | `{"success": true, "message": "..."}` |
| `update_delivery_time` | Update estimated delivery time | `{"success": true}` |
| `save_working_hours` | Save all 7 days of working hours | `{"success": true, "message": "..."}` |
| `toggle_tracking` | Toggle tracking link in customer SMS | `{"success": true, "enabled": true}` |

---

### Dish Management (from KDS)

#### `POST /order-dashboard/dishes/toggle-availability`
**Toggle Dish Availability**

**Form Fields:** `item_id` (int)

**Response:** `{"success": true, "is_available": false}`

#### `POST /order-dashboard/dishes/update-days`
**Update Availability Days**

**Form Fields:** `item_id` (int), `available_days` (7-char string of `0`/`1`, index 0 = Sunday)

**Response:** `{"success": true}`

#### `POST /order-dashboard/dishes/update-times`
**Update Availability Time Window**

**Form Fields:** `item_id` (int), `available_from_time` (`HH:MM`), `available_to_time` (`HH:MM`)

**Response:** `{"success": true}`

#### `POST /order-dashboard/dishes/update-price`
**Update Base Price**

**Form Fields:** `item_id` (int), `price` (float, >= 0)

**Response:** `{"success": true, "price": 45.0}`

#### `GET /order-dashboard/dishes/<item_id>/detail`
**Dish Detail (JSON)** — Returns full item detail including option groups and price variants.

**Response:**
```json
{
  "success": true,
  "item": {
    "id": 42,
    "name_he": "שווארמה",
    "name_en": "Shawarma",
    "base_price": 45.0,
    "is_available": true,
    "available_days": "1111111",
    "available_from_time": "",
    "available_to_time": "",
    "image_path": ""
  },
  "option_groups": [
    {
      "id": 1,
      "name_he": "תוספות",
      "name_en": "Extras",
      "selection_type": "multi",
      "is_required": false,
      "min_selections": 0,
      "max_selections": 5,
      "is_active": true,
      "display_order": 0,
      "choices": [
        {
          "id": 5,
          "name_he": "חומוס",
          "name_en": "Hummus",
          "price_modifier": 3.0,
          "is_available": true,
          "is_default": false,
          "display_order": 0
        }
      ]
    }
  ],
  "prices": [
    {
      "id": 1,
      "size_name_he": "רגיל",
      "size_name_en": "Regular",
      "price": 45.0,
      "is_default": true,
      "display_order": 0
    }
  ]
}
```

#### `POST /order-dashboard/dishes/option-group/save`
**Create/Update Option Group** — Accepts JSON body.

**JSON Body:**
```json
{
  "menu_item_id": 42,
  "id": null,
  "name_he": "תוספות",
  "name_en": "Extras",
  "selection_type": "multi",
  "is_required": false,
  "min_selections": 0,
  "max_selections": 5,
  "display_order": 0,
  "is_active": true,
  "choices": [
    {
      "name_he": "חומוס",
      "name_en": "Hummus",
      "price_modifier": 3.0,
      "is_available": true,
      "is_default": false,
      "display_order": 0
    }
  ]
}
```

**Response:** `{"success": true, "group_id": 1}`

#### `POST /order-dashboard/dishes/option-group/<group_id>/delete`
**Delete Option Group** — Cascades to delete all choices.

**Response:** `{"success": true}`

#### `POST /order-dashboard/dishes/price-variant/save`
**Create/Update Price Variant** — Accepts JSON body.

**JSON Body:**
```json
{
  "menu_item_id": 42,
  "id": null,
  "size_name_he": "גדול",
  "size_name_en": "Large",
  "price": 55.0,
  "is_default": false,
  "display_order": 1
}
```

**Response:** `{"success": true, "id": 2}`

#### `POST /order-dashboard/dishes/price-variant/<variant_id>/delete`
**Delete Price Variant**

**Response:** `{"success": true}`

#### `POST /order-dashboard/dishes/toggle-tracking`
**Toggle Tracking Link** — Toggles whether customer SMS includes a tracking link.

**Response:** `{"success": true, "enabled": false}`

---

### Statistics

#### `GET /order-dashboard/statistics`
**Statistics Dashboard** — 7-day order/revenue charts, 30-day KPIs, top items, delivery/pickup and cash/card splits.

**Context:** `days_data`, `month_revenue`, `month_count`, `avg_order`, `top_items`, `delivery_count`, `pickup_count`, `cash_count`, `card_count`, `staff_name`, `today`

---

## Data Models Reference

### FoodOrder

| Column | Type | Description |
|---|---|---|
| `id` | Integer PK | Auto-increment |
| `order_number` | String(30) | Unique, format: `ORD-YYMMDD-NNNN` |
| `order_type` | String(20) | `delivery` or `takeaway` |
| `status` | String(30) | Lifecycle status (see Order Lifecycle) |
| `customer_name` | String(100) | Full name |
| `customer_phone` | String(20) | Phone number |
| `customer_email` | String(120) | Email |
| `delivery_address` | String(300) | Street + house number |
| `delivery_city` | String(100) | City |
| `delivery_notes` | String(300) | Floor/entry instructions |
| `pickup_time` | String(50) | Requested pickup time |
| `subtotal` | Float | Items total before delivery fee |
| `delivery_fee` | Float | Delivery fee charged |
| `discount_amount` | Float | Discount applied |
| `total_amount` | Float | Final total |
| `payment_method` | String(30) | `cash` or `card` |
| `payment_status` | String(20) | `pending`, `paid`, `failed`, `cash` |
| `hyp_transaction_id` | String(100) | HYP transaction ID |
| `hyp_order_ref` | String(100) | HYP order reference |
| `tracking_token` | String(50) | Unique URL-safe token for customer tracking |
| `utm_source` | String(200) | UTM source attribution |
| `utm_medium` | String(200) | UTM medium attribution |
| `utm_campaign` | String(200) | UTM campaign attribution |
| `referrer` | String(500) | HTTP referrer URL |
| `estimated_ready_at` | DateTime | Staff-set estimated ready time |
| `created_at` | DateTime | Order placement timestamp |
| `confirmed_at` | DateTime | Staff confirmation timestamp |
| `preparing_at` | DateTime | Started preparing timestamp |
| `ready_at` | DateTime | Ready for pickup/delivery timestamp |
| `completed_at` | DateTime | Delivered/picked up timestamp |
| `cancelled_at` | DateTime | Cancellation timestamp |
| `items_json` | Text | JSON snapshot of ordered items |
| `admin_notes` | Text | Timestamped staff notes |
| `customer_notes` | Text | Customer special requests |
| `customer_account_id` | Integer | Optional link to customer account |
| `confirmation_sms_sent` | Boolean | Whether confirmation SMS was sent |
| `ready_sms_sent` | Boolean | Whether ready SMS was sent |
| `telegram_notified` | Boolean | Whether Telegram notification was sent |

### FoodOrderItem

| Column | Type | Description |
|---|---|---|
| `id` | Integer PK | |
| `order_id` | Integer FK | Links to `food_orders.id` |
| `menu_item_id` | Integer FK | Links to `menu_items.id` |
| `item_name_he` | String(200) | Hebrew name (snapshot at order time) |
| `item_name_en` | String(200) | English name |
| `quantity` | Integer | Item count |
| `unit_price` | Float | Base price + option modifiers |
| `total_price` | Float | quantity × unit_price |
| `special_instructions` | String(300) | Per-item notes |
| `options_json` | Text | JSON of selected options and/or combo selections |

### DeliveryZone

| Column | Type | Description |
|---|---|---|
| `id` | Integer PK | |
| `branch_id` | Integer FK | Optional link to branch |
| `city_name` | String(100) | City name (Hebrew) |
| `name` | String(100) | Custom zone name (optional) |
| `delivery_fee` | Float | Fee for this zone |
| `minimum_order` | Float | Minimum order amount |
| `free_delivery_above` | Float | Free delivery threshold |
| `estimated_minutes` | Integer | Estimated delivery time |
| `estimated_delivery_time` | String(50) | Display text (e.g., "30-45 דקות") |
| `is_active` | Boolean | Zone enabled |
| `display_order` | Integer | Sort order |

### SiteSettings

| Column | Type | Default | Description |
|---|---|---|---|
| `id` | Integer PK | | |
| `site_name_he` | String(200) | 'המסעדה שלי' | Hebrew name |
| `site_name_en` | String(200) | 'My Restaurant' | English name |
| `contact_phone` | String(20) | | Display phone |
| `admin_phone` | String(20) | | Admin notifications phone |
| `enable_online_ordering` | Boolean | False | Master switch |
| `ordering_paused` | Boolean | False | Temporary pause |
| `enable_delivery` | Boolean | True | Delivery toggle |
| `enable_pickup` | Boolean | True | Pickup toggle |
| `delivery_fee` | Float | 15.0 | Default fee |
| `free_delivery_threshold` | Float | 100.0 | Free delivery above |
| `hyp_enabled` | Boolean | False | Card payments |
| `hyp_sandbox_mode` | Boolean | True | HYP sandbox |
| `send_order_tracking_link` | Boolean | True | SMS tracking link |

*(See INTEGRATION_GUIDE.md for full SiteSettings field list)*

---

## HYP Payment Flow

1. Customer selects "Credit Card" at checkout
2. Server calls HYP APISign endpoint with order details, success/failure URLs
3. HYP returns signed parameters as a query string
4. Customer is shown payment iframe embedding the HYP payment page
5. Customer enters card details on the HYP-hosted page
6. After payment, HYP redirects to the success or failure callback URL
7. Server verifies HMAC signature and CCode response
8. On success (`CCode=0`): marks order paid + confirmed, sends notifications
9. On failure: marks payment as failed, shows retry option

**Test Cards (Sandbox Mode):**

| Card Type | Number | CVV | ID |
|---|---|---|---|
| Visa | `4580-0000-0000-0000` | Any 3 digits | `000000000` |

Use any future expiry date. Sandbox mode uses `https://icom.yaad.net/p/` instead of `https://pay.hyp.co.il/p/`.
