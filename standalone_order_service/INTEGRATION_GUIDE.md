# Standalone Food Ordering Service — Integration Guide

## Overview

A complete, self-contained food ordering system for Israeli restaurants. Includes:

- **Public ordering page** — Mobile-first menu browsing, cart, checkout, delivery zones
- **KDS dashboard** — iPad-optimized kitchen display with real-time order management
- **HYP (Yaad Pay) payments** — Credit card processing with APISign flow
- **SMS & Telegram notifications** — SMS4Free provider with logging
- **Combo meals & dish options** — Full customization support
- **Availability scheduling** — Per-dish day/time restrictions
- **UTM & referrer tracking** — Built-in conversion attribution
- **Statistics dashboard** — 7-day charts, 30-day KPIs, top items

## Requirements

### Python Packages (tested versions)

```
Flask==3.1.1
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.41
requests==2.32.3
Werkzeug==3.1.3
pytz==2025.1
```

### Optional Packages

```
Flask-WTF==1.2.2        # CSRF protection (recommended)
twilio==9.6.1           # For Twilio SMS
gunicorn==23.0.0        # Production WSGI server
psycopg2-binary==2.9.10 # PostgreSQL driver
```

Newer compatible versions should also work. Minimum supported: Flask 2.3+, SQLAlchemy 2.0+, Python 3.10+.

**CSRF note:** Templates include CSRF token fields that work automatically when Flask-WTF is installed. Without Flask-WTF, forms will render with empty CSRF tokens and still function — but CSRF protection will not be enforced. For production use, install Flask-WTF and call `CSRFProtect(app)` (exempt the KDS blueprint as shown in step 5).

### Database

PostgreSQL is recommended. SQLite works for development but is not suitable for production due to concurrent write limitations. The package manages 12 tables:

| Table | Purpose |
|---|---|
| `site_settings` | Ordering configuration, payment credentials |
| `branches` | Restaurant branch locations |
| `working_hours` | Per-branch operating hours |
| `menu_categories` | Menu category groups |
| `menu_items` | Individual menu items |
| `menu_item_prices` | Size/price variants per item |
| `menu_item_option_groups` | Option groups (toppings, size, etc.) |
| `menu_item_option_choices` | Individual option choices |
| `delivery_zones` | City-based delivery zones with fees |
| `food_orders` | Customer orders |
| `food_order_items` | Individual items within orders |
| `manager_pins` | Staff PIN authentication for KDS |

## Quick Start

### 1. Install

Copy the `standalone_order_service/` directory into your project root.

```
your_project/
├── app.py
├── standalone_order_service/
│   ├── __init__.py
│   ├── models.py
│   ├── order_routes.py
│   ├── kds_routes.py
│   ├── hyp_payment.py
│   ├── notifications.py
│   ├── sms_helpers.py
│   ├── templates/
│   │   ├── order/          (6 templates)
│   │   └── order_dashboard/ (5 templates)
│   ├── static/
│   │   ├── dish-placeholder.png
│   │   └── order-hero-bg.png
│   ├── INTEGRATION_GUIDE.md
│   └── API_REFERENCE.md
└── ...
```

### 2. Register Models

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@host/dbname'
db = SQLAlchemy(app)

from standalone_order_service.models import register_models
order_models = register_models(db)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# Access individual models
FoodOrder = order_models['FoodOrder']
MenuItem = order_models['MenuItem']
SiteSettings = order_models['SiteSettings']
```

**Existing tables:** If your app already has these tables (e.g., `menu_items`, `food_orders`), the models will bind to the existing tables — no migration needed. The `SiteSettings` model includes only ordering-related fields; if your `site_settings` table has additional columns they will be ignored by SQLAlchemy (not deleted).

**New database setup:** After calling `db.create_all()`, seed initial data:

```python
with app.app_context():
    # Create initial settings
    settings = SiteSettings(
        site_name_he='המסעדה שלי',
        site_name_en='My Restaurant',
        enable_online_ordering=True,
        enable_delivery=True,
        enable_pickup=True,
    )
    db.session.add(settings)

    # Create a branch (required for working hours)
    Branch = order_models['Branch']
    branch = Branch(name_he='סניף ראשי', name_en='Main Branch', is_active=True)
    db.session.add(branch)

    # Create a manager PIN for KDS access
    ManagerPIN = order_models['ManagerPIN']
    pin = ManagerPIN(name='מנהל')
    pin.set_pin('1234')
    db.session.add(pin)

    db.session.commit()
```

### 3. Set Up SMS (Using Built-in Helpers)

The package includes ready-to-use SMS sender factories for Twilio and SMS4Free:

```python
from standalone_order_service.sms_helpers import (
    create_twilio_sender,
    create_sms4free_sender,
    create_failover_sender,
    create_sender_from_env,  # auto-detect from env vars
)

# Option A: Auto-detect from environment variables
send_sms = create_sender_from_env()

# Option B: Explicit Twilio setup
send_sms = create_twilio_sender(
    account_sid='ACxxxxxxxxx',
    auth_token='xxxxxxxxx',
    from_number='+972500000000',
)

# Option C: SMS4Free
send_sms = create_sms4free_sender(
    api_key='xxxx',
    user='xxxx',
    password='xxxx',
    sender_name='Restaurant',
)

# Option D: Twilio primary, SMS4Free failover
twilio_fn = create_twilio_sender(...)
sms4free_fn = create_sms4free_sender(...)
send_sms = create_failover_sender(twilio_fn, sms4free_fn)
```

### SMS Routing Configuration

The package includes a standalone SMS routing module that replaces the parent project's database-backed `sms_encryption` routing:

```python
from standalone_order_service.sms_routing import SmsRoutingConfig
from standalone_order_service.sms_helpers import (
    create_twilio_sender_from_env,
    create_sms4free_sender_from_env,
)

# Load routing config from environment
routing = SmsRoutingConfig.from_env()

# Build a routed sender with automatic failover
twilio_fn = create_twilio_sender_from_env()
sms4free_fn = create_sms4free_sender_from_env()
send_sms = routing.build_sender(twilio_fn, sms4free_fn)

# Or configure routing explicitly
routing = SmsRoutingConfig(
    primary='twilio',
    failover='sms4free',
    failover_enabled=True,
)
```

**Routing environment variables:**

| Variable | Default | Description |
|---|---|---|
| `SMS_PRIMARY_PROVIDER` | `twilio` | Primary SMS provider (`twilio` or `sms4free`) |
| `SMS_FAILOVER_PROVIDER` | `sms4free` | Failover provider |
| `SMS_FAILOVER_ENABLED` | `true` | Enable automatic failover |
| `SMS_MAX_RETRIES` | `2` | Max retry count |

**Environment variables for SMS provider credentials:**

| Variable | Provider | Description |
|---|---|---|
| `TWILIO_ACCOUNT_SID` | Twilio | Account SID |
| `TWILIO_AUTH_TOKEN` | Twilio | Auth token |
| `TWILIO_PHONE_NUMBER` | Twilio | Sending phone number (E.164) |
| `SMS_SENDER_ID` | Twilio | Alphanumeric sender ID (optional) |
| `SMS4FREE_KEY` | SMS4Free | API key |
| `SMS4FREE_USER` | SMS4Free | Username |
| `SMS4FREE_PASS` | SMS4Free | Password |
| `SMS4FREE_SENDER` | SMS4Free | Sender name (default: Restaurant) |

### 4. Register Blueprints

```python
from standalone_order_service.order_routes import create_order_blueprint
from standalone_order_service.kds_routes import create_kds_blueprint
from standalone_order_service.hyp_payment import HYPPayment
from standalone_order_service.notifications import OrderNotifier

SiteSettings = order_models['SiteSettings']

def get_settings():
    return SiteSettings.query.first()

# Notifications
notifier = OrderNotifier(
    send_sms=send_sms,
    send_telegram=None,  # optional
)

# Payment
hyp = HYPPayment()

# Public ordering blueprint (mounts at /order)
order_bp = create_order_blueprint(
    db=db,
    models=order_models,
    notifier=notifier,
    hyp_payment=hyp,
    get_settings=get_settings,
)
app.register_blueprint(order_bp)

# KDS dashboard blueprint (mounts at /order-dashboard)
kds_bp = create_kds_blueprint(
    db=db,
    models=order_models,
    send_sms=send_sms,
    get_settings=get_settings,
    clear_cache=None,  # optional cache invalidation callable
)
app.register_blueprint(kds_bp)
```

### 5. CSRF Exemption for KDS

The KDS dashboard uses AJAX POST calls. If you use Flask-WTF CSRF protection, exempt the KDS blueprint:

```python
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
csrf.exempt(kds_bp)
```

### 6. Session Configuration

Both ordering and KDS require Flask sessions. Configure a secure secret key:

```python
import os
app.secret_key = os.environ.get('SESSION_SECRET', os.urandom(32))
```

---

## Configuration

### Settings Object (SiteSettings Model)

The `SiteSettings` model is included in the package. All fields have sensible defaults:

| Field | Type | Default | Description |
|---|---|---|---|
| `site_name_he` | str | 'המסעדה שלי' | Hebrew restaurant name |
| `site_name_en` | str | 'My Restaurant' | English restaurant name |
| `contact_phone` | str | — | Contact phone (shown on order page) |
| `admin_phone` | str | — | Admin phone for SMS notifications |
| `enable_online_ordering` | bool | False | Master on/off switch |
| `ordering_paused` | bool | False | Temporary pause |
| `ordering_paused_message` | str | — | Message shown when paused |
| `ordering_closed_message` | str | — | Message when ordering is off |
| `enforce_ordering_hours` | bool | False | Only accept orders during working hours |
| `ordering_outside_hours_message` | str | — | Message for off-hours |
| `enable_delivery` | bool | True | Show delivery option |
| `enable_pickup` | bool | True | Show pickup option |
| `delivery_fee` | float | 15.0 | Default delivery fee (₪) |
| `free_delivery_threshold` | float | 100.0 | Free delivery above this subtotal |
| `estimated_delivery_time` | str | '45-60' | Delivery time shown to customers |
| `hyp_enabled` | bool | False | Enable credit card payments |
| `hyp_sandbox_mode` | bool | True | Use HYP test environment |
| `hyp_terminal` | str | — | HYP terminal (Masof) number |
| `hyp_api_key` | str | — | HYP API key |
| `hyp_passp` | str | — | HYP PassP password |
| `telegram_bot_token` | str | — | Telegram bot token |
| `telegram_chat_id` | str | — | Direct Telegram chat ID |
| `telegram_channel_id` | str | — | Telegram channel ID |
| `send_order_tracking_link` | bool | True | Include tracking link in customer SMS |

### HYP Payment Environment Variables (Priority)

| Variable | Description |
|---|---|
| `HYP_TERMINAL` | Terminal (Masof) number |
| `HYP_API_KEY` | API key |
| `HYP_PASSP` | PassP password |

If set, these take priority over `SiteSettings` values.

### Delivery Zones

Create `DeliveryZone` records in the database:

```python
DeliveryZone = order_models['DeliveryZone']
zone = DeliveryZone(
    city_name='כרמיאל',
    delivery_fee=10.0,
    minimum_order=50.0,
    free_delivery_above=150.0,
    estimated_delivery_time='30-45 דקות',
    is_active=True,
    display_order=1,
)
db.session.add(zone)
db.session.commit()
```

### Manager PINs (KDS Access)

```python
ManagerPIN = order_models['ManagerPIN']
pin = ManagerPIN(name='שלומי')
pin.set_pin('1234')
db.session.add(pin)
db.session.commit()
```

---

## Order Lifecycle

```
pending  →  confirmed  →  preparing  →  ready  →  delivered / pickedup
                                                 ↘ cancelled (from any state)
```

| Status | Description |
|---|---|
| `pending` | Order placed, awaiting staff confirmation |
| `confirmed` | Staff accepted; optional prep time estimate set |
| `preparing` | Kitchen is working on it |
| `ready` | Ready for pickup or delivery |
| `delivered` | Delivery completed |
| `pickedup` | Customer picked up |
| `cancelled` | Order cancelled (optional reason logged) |

---

## Combo Meals

Combos are stored as a JSON definition on `MenuItem.combo_items_json`:

```json
[
  {
    "slot_name_he": "בחר עיקרית",
    "slot_name_en": "Choose main",
    "min_select": 1,
    "max_select": 1,
    "items": [
      {"menu_item_id": 42, "price_modifier": 0},
      {"menu_item_id": 43, "price_modifier": 5.0}
    ]
  }
]
```

The checkout route performs full server-side validation of combo selections against the database definition, including min/max selection enforcement per slot.

---

## Dish Options & Additions

Each `MenuItem` can have multiple `MenuItemOptionGroup` entries (e.g., "Size", "Extras"), each containing `MenuItemOptionChoice` records with individual price modifiers. Supports:

- **Single-select** (`selection_type='single'`): Radio button groups
- **Multi-select** (`selection_type='multi'`): Checkbox groups with min/max limits
- **Required/optional** groups
- **Price modifiers** per choice (added to base price)

The checkout route verifies all selected options against the database and recalculates total pricing server-side.

---

## Templates

The package includes **full production-ready templates** extracted from the original project. All templates use standalone `url_for()` references with blueprint prefixes (`order_page.` and `order_dashboard.`).

### Order templates (`templates/order/`)

| Template | Purpose |
|---|---|
| `base.html` | Minimal RTL base layout (Bootstrap 5) |
| `order_page.html` | Full menu browsing with horizontal carousels, cart, sticky checkout bar |
| `order_checkout.html` | Multi-step checkout with delivery/pickup, address, payment |
| `order_confirmation.html` | Post-order status page with live AJAX polling |
| `order_track.html` | Customer-facing tracking page (accessed via SMS link) |
| `hyp_redirect.html` | HYP payment redirect with branded header and iframe |
| `order_payment_iframe.html` | Alternative payment page layout |

### KDS templates (`templates/order_dashboard/`)

| Template | Purpose |
|---|---|
| `login.html` | Staff PIN authentication |
| `orders.html` | Kanban-style order board with status columns and auto-refresh |
| `order_detail.html` | Full order detail with timeline, items, notes, SMS |
| `settings.html` | Quick toggles, working hours, dish management |
| `statistics.html` | 7-day charts, 30-day KPIs, top items |

### Static Assets

| File | Purpose |
|---|---|
| `static/dish-placeholder.png` | Default dish image placeholder |
| `static/order-hero-bg.png` | Order page hero banner background |

Templates reference static assets via `url_for('order_page.static', filename='...')` and menu item images via `url_for('order_page.menu_image', item_id=...)`. No host-app paths are hardcoded — the package is fully self-contained.

### Customizing the Base Template

The order templates extend `base.html`. To integrate with your app's main layout, edit `templates/order/base.html` to match your site's header, footer, navigation, and CSS.

**Template collision warning:** Flask resolves templates from the app's main template folder first, then from blueprint template folders. If your host app already has a `base.html` in its root templates directory, it will take priority over this package's `base.html`. To avoid this, either: (a) rename the package's base template (e.g., `order_base.html`) and update the `{% extends %}` in all order templates, or (b) ensure your host app does not have a conflicting `base.html` in the root template directory.

### Analytics Integration

Order templates include safe hooks for GA4 and Facebook Pixel tracking (e-commerce funnel events). These are no-ops when analytics are not loaded — they check `typeof gtag === 'function'` and `typeof fbq === 'function'` before calling. To enable tracking, include the GA4 and/or Facebook Pixel scripts in your `base.html`. To remove tracking entirely, delete the `GA4 + FB Pixel` script blocks from the order templates.

---

## Troubleshooting

### Common Issues

**"מערכת ההזמנות אינה פעילה כרגע" (Ordering system is not active)**
- Ensure `SiteSettings.enable_online_ordering = True` in the database.

**KDS login fails**
- Create at least one active `ManagerPIN` record.
- PIN must be hashed via `pin.set_pin('1234')`, not stored as plaintext.

**HYP payment URL returns `None`**
- Check HYP credentials: terminal, API key, PassP.
- Verify `hyp_enabled = True` in settings.
- Check logs for `HYP APISign` error messages.
- For sandbox testing, set `hyp_sandbox_mode = True`.

**SMS not sending**
- Verify `send_sms` callable is not `None`.
- Check phone format: Israeli numbers must be in `972xxxxxxxxx` format.
- The `sms_helpers` module auto-formats numbers; verify credentials are correct.
- Check logs for `[TWILIO]` or `[SMS4FREE]` error messages.

**Templates not found**
- Ensure the package's `templates/` directory is accessible. Blueprint templates are loaded relative to the package directory.
- If using a custom template loader, register the package template path.

**Working hours enforcement not working**
- Ensure `enforce_ordering_hours = True` in settings.
- Create `WorkingHours` records for each day of the week linked to an active `Branch`.
- Day numbering: 0 = Sunday, 6 = Saturday (Israeli convention).

---

## File Structure

```
standalone_order_service/
├── __init__.py                  # Package metadata (v1.0.0)
├── models.py                    # 12 database models (register_models factory)
├── order_routes.py              # Public ordering blueprint (14 endpoints)
├── kds_routes.py                # KDS dashboard blueprint (20+ endpoints)
├── hyp_payment.py               # HYP (Yaad Pay) payment class
├── notifications.py             # OrderNotifier — SMS & Telegram
├── sms_helpers.py               # Twilio/SMS4Free senders with failover
├── sms_routing.py               # SMS provider routing configuration
├── templates/
│   ├── order/                   # 7 public-facing templates
│   │   ├── base.html
│   │   ├── order_page.html
│   │   ├── order_checkout.html
│   │   ├── order_confirmation.html
│   │   ├── order_track.html
│   │   ├── hyp_redirect.html
│   │   └── order_payment_iframe.html
│   └── order_dashboard/         # 5 KDS templates
│       ├── login.html
│       ├── orders.html
│       ├── order_detail.html
│       ├── settings.html
│       └── statistics.html
├── static/
│   ├── dish-placeholder.png
│   └── order-hero-bg.png
├── INTEGRATION_GUIDE.md         # This file
└── API_REFERENCE.md             # Full endpoint documentation
```
