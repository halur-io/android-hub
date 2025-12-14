# Popup System Microservice

A complete, production-ready popup system with lead collection, analytics, and mobile optimization.

## Features

- **Fully Customizable Popups** - Colors, fonts, sizes, positions, animations
- **Lead Collection Forms** - Name, email, phone with consent checkboxes
- **Mobile Optimized** - Uses Visual Viewport API for real device compatibility
- **Analytics Tracking** - Impressions, clicks, closes with rate limiting
- **Display Control** - Timing, frequency, device targeting, page targeting
- **Admin Panel** - Full CRUD for popups with live preview

## Files Included

```
popup_microservice/
├── README.md           # This documentation
├── popup_system.js     # Frontend JavaScript (drop into static/js/)
├── popup_models.py     # Database models (add to your models.py)
├── popup_routes.py     # API routes (add to your routes.py)
└── popup_admin.py      # Admin routes (optional, for admin panel)
```

## Quick Setup (5 Steps)

### Step 1: Copy the Frontend JS

Copy `popup_system.js` to your `static/js/` folder.

### Step 2: Add Database Models

Add the contents of `popup_models.py` to your `models.py` file. Then run your database migrations.

### Step 3: Add API Routes

Add the contents of `popup_routes.py` to your `routes.py` file.

### Step 4: Include the Script in Your HTML

Add this to your base template (before `</body>`):

```html
<script src="{{ url_for('static', filename='js/popup_system.js') }}"></script>
<script>
  fetch('/api/popups/active')
    .then(r => r.json())
    .then(popups => {
      if (popups && popups.length) {
        SitePopup.init(popups);
      }
    });
</script>
```

### Step 5: Create Your First Popup

Insert a popup record into your database:

```sql
INSERT INTO popups (
  name, 
  title_he, 
  title_en, 
  content_he, 
  content_en,
  button_text_he,
  button_text_en,
  button_url,
  is_active,
  trigger_type,
  show_delay_seconds
) VALUES (
  'Welcome Popup',
  'שלום!',
  'Hello!',
  'ברוכים הבאים לאתר שלנו',
  'Welcome to our website',
  'המשך',
  'Continue',
  '/',
  true,
  'time_delay',
  3
);
```

## Configuration Options

### Popup Settings

| Field | Type | Description |
|-------|------|-------------|
| `name` | String | Internal name for admin reference |
| `title_he/en` | String | Popup title (Hebrew/English) |
| `content_he/en` | Text | Popup body text |
| `button_text_he/en` | String | CTA button text |
| `button_url` | String | Button click destination |
| `button_action` | String | `link`, `new_tab`, `close` |
| `image_path` | String | Path to popup image |
| `popup_size` | String | `small`, `medium`, `large` |
| `popup_position` | String | `center`, `top-left`, `top-right`, `bottom-left`, `bottom-right` |

### Design Settings

| Field | Type | Default |
|-------|------|---------|
| `background_color` | String | `#ffffff` |
| `title_color` | String | `#1B2951` |
| `text_color` | String | `#333333` |
| `button_bg_color` | String | `#C75450` |
| `button_text_color` | String | `#ffffff` |
| `border_radius` | Integer | `12` |
| `has_shadow` | Boolean | `true` |

### Timing & Triggers

| Field | Type | Description |
|-------|------|-------------|
| `trigger_type` | String | `time_delay`, `scroll`, `exit_intent`, `immediate` |
| `show_delay_seconds` | Integer | Seconds to wait (for time_delay) |
| `scroll_percentage` | Integer | % scrolled to trigger (for scroll) |
| `start_date` | DateTime | Don't show before this date |
| `end_date` | DateTime | Don't show after this date |

### Frequency Control

| Field | Type | Description |
|-------|------|-------------|
| `show_frequency` | String | `always`, `once_per_session`, `once_ever`, `once_per_day`, `every_x_days` |
| `show_every_x_days` | Integer | Days between shows (for every_x_days) |

### Device Targeting

| Field | Type | Default |
|-------|------|---------|
| `show_on_desktop` | Boolean | `true` |
| `show_on_mobile` | Boolean | `true` |
| `show_on_tablet` | Boolean | `true` |

### Form Collection

| Field | Type | Description |
|-------|------|-------------|
| `enable_form` | Boolean | Show lead collection form |
| `collect_email` | Boolean | Show email field |
| `collect_name` | Boolean | Show name field |
| `collect_phone` | Boolean | Show phone field |
| `show_newsletter_consent` | Boolean | Newsletter checkbox |
| `show_terms_consent` | Boolean | Terms checkbox |
| `show_marketing_consent` | Boolean | Marketing checkbox |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/popups/active` | GET | Get all active popups |
| `/api/popup/<id>/impression` | POST | Track popup view |
| `/api/popup/<id>/click` | POST | Track button click |
| `/api/popup/<id>/close` | POST | Track popup close |
| `/api/popup/<id>/submit` | POST | Submit lead form |

## Mobile Optimization

The popup system uses the **Visual Viewport API** to correctly size popups on real mobile devices, accounting for:

- Browser address bar height
- Bottom navigation bar
- Dynamic browser chrome that changes on scroll

This ensures popups fit properly on real devices, not just in emulators.

## Dependencies

- Flask + Flask-SQLAlchemy (for backend)
- PostgreSQL database (recommended)
- No frontend framework required (vanilla JavaScript)

## Google Tag Manager Integration

The popup system automatically pushes events to GTM dataLayer:

- `popup_impression` - When popup is shown
- `popup_click` - When CTA is clicked
- `popup_close` - When popup is closed
- `popup_form_submit` - When form is submitted

## License

Free to use in any project.
