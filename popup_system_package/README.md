# Popup System for Flask Applications

A comprehensive popup/modal system for Flask websites with admin panel, lead collection, analytics, and more.

## Features

- **Visual Popup Designer** - Live preview while editing with drag-and-drop element ordering
- **Bilingual Support** - Hebrew and English content fields
- **Form Collection** - Collect emails, names, and phone numbers from visitors
- **Consent Management** - Newsletter, terms, and marketing consent checkboxes
- **Analytics** - Track impressions, clicks, and closes with conversion rates
- **Device Targeting** - Show/hide on desktop, tablet, or mobile
- **Trigger Options** - Time delay, scroll percentage, exit intent, or immediate
- **Display Frequency** - Once per session, once ever, every X days, or always
- **Scheduling** - Set start and end dates for campaigns
- **Lead Management** - View and export collected leads to Excel
- **Rate Limiting** - Prevent analytics manipulation

## File Structure

```
popup_system_package/
├── README.md                           # This documentation
├── models.py                           # Database models (Popup, PopupLead, etc.)
├── routes.py                           # Public API routes
├── admin_routes.py                     # Admin panel routes
├── static/
│   └── js/
│       └── popup-system.js             # Frontend popup display logic
└── templates/
    └── admin/
        ├── popups.html                 # Popup list page
        ├── popup_form.html             # Popup editor with live preview
        └── popup_leads.html            # Leads table page
```

## Installation

### 1. Database Models

Add the models from `models.py` to your existing models file:

```python
# In your models.py
from datetime import datetime
from app import db

class Popup(db.Model):
    # ... (copy from models.py)

class PopupLead(db.Model):
    # ... (copy from models.py)

class CustomerConsent(db.Model):
    # ... (copy from models.py)
```

### 2. Create Database Tables

Run migrations or create tables:

```python
# In Flask shell or startup
from app import db
db.create_all()
```

### 3. Admin Routes

Add the admin routes to your admin blueprint:

```python
# In your admin_routes.py or admin blueprint

@admin_bp.route('/popups')
@login_required
def popups():
    popups = Popup.query.order_by(Popup.priority.desc(), Popup.created_at.desc()).all()
    total_leads = PopupLead.query.count()
    return render_template('admin/popups.html', popups=popups, total_leads=total_leads)

@admin_bp.route('/popups/create', methods=['GET', 'POST'])
@login_required
def create_popup():
    if request.method == 'POST':
        # Handle form submission - see admin_routes.py for full code
        pass
    return render_template('admin/popup_form.html', popup=None)

# Add edit_popup, delete_popup, toggle_popup, duplicate_popup routes...
```

### 4. Public API Routes

Add public API endpoints to your routes:

```python
# In your routes.py

@app.route('/api/popups/active')
def api_active_popups():
    popups = Popup.query.filter_by(is_active=True).all()
    active_popups = [p.to_frontend_config() for p in popups if p.is_currently_active()]
    return jsonify(active_popups)

@app.route('/api/popup/<int:popup_id>/impression', methods=['POST'])
def api_popup_impression(popup_id):
    popup = Popup.query.get_or_404(popup_id)
    popup.total_impressions += 1
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/popup/<int:popup_id>/click', methods=['POST'])
def api_popup_click(popup_id):
    popup = Popup.query.get_or_404(popup_id)
    popup.total_cta_clicks += 1
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/popup/<int:popup_id>/close', methods=['POST'])
def api_popup_close(popup_id):
    popup = Popup.query.get_or_404(popup_id)
    popup.total_closes += 1
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/popup/<int:popup_id>/submit', methods=['POST'])
def api_popup_form_submit(popup_id):
    popup = Popup.query.get_or_404(popup_id)
    data = request.get_json()
    
    lead = PopupLead(
        popup_id=popup_id,
        email=data.get('email'),
        name=data.get('name'),
        phone=data.get('phone'),
        is_subscribed=data.get('newsletter_consent', False),
        source_page=request.referrer,
        user_agent=request.user_agent.string,
        ip_address=request.remote_addr
    )
    db.session.add(lead)
    db.session.commit()
    
    return jsonify({'success': True, 'message': popup.form_success_message_he})
```

### 5. Frontend Integration

Add the popup system to your base template:

```html
<!-- In your base.html, before </body> -->

<!-- Popup System -->
<script src="{{ url_for('static', filename='js/popup-system.js') }}"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        fetch('/api/popups/active')
            .then(function(response) { return response.json(); })
            .then(function(popups) {
                if (popups && popups.length > 0) {
                    SitePopup.init(popups);
                }
            })
            .catch(function(err) { console.log('[Popup] Error:', err); });
    });
</script>
```

### 6. Copy Templates

Copy the template files to your templates directory:
- `templates/admin/popups.html` - Popup management list
- `templates/admin/popup_form.html` - Popup editor
- `templates/admin/popup_leads.html` - Leads table

### 7. Copy Static Files

Copy JavaScript files to your static directory:
- `static/js/popup-system.js` - Frontend popup logic

## Configuration Options

### Popup Model Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | String | Internal name for identification |
| `title_he/en` | String | Popup title in Hebrew/English |
| `content_he/en` | Text | Main content text |
| `button_text_he/en` | String | CTA button text |
| `button_url` | String | URL for button click |
| `button_action` | String | 'link', 'new_tab', or 'close' |
| `image_path` | String | Path to popup image |
| `popup_size` | String | 'small', 'medium', 'large' |
| `popup_position` | String | 'center', 'top-left', etc. |
| `background_color` | String | Hex color for background |
| `title_color` | String | Hex color for title |
| `text_color` | String | Hex color for content |
| `button_bg_color` | String | Hex color for button |
| `border_radius` | Integer | Border radius in pixels |
| `show_delay_seconds` | Integer | Delay before showing |
| `show_frequency` | String | 'once_per_session', 'once_ever', 'every_x_days', 'always' |
| `trigger_type` | String | 'time_delay', 'scroll', 'exit_intent', 'immediate' |
| `scroll_percentage` | Integer | Scroll % to trigger (0-100) |
| `show_on_desktop` | Boolean | Show on desktop devices |
| `show_on_mobile` | Boolean | Show on mobile devices |
| `show_on_tablet` | Boolean | Show on tablet devices |
| `is_active` | Boolean | Enable/disable popup |
| `priority` | Integer | Higher priority shows first |
| `start_date` | DateTime | Campaign start date |
| `end_date` | DateTime | Campaign end date |

### Form Collection Fields

| Field | Type | Description |
|-------|------|-------------|
| `enable_form` | Boolean | Enable form instead of button |
| `collect_email` | Boolean | Show email field |
| `collect_name` | Boolean | Show name field |
| `collect_phone` | Boolean | Show phone field |
| `email_required` | Boolean | Make email required |
| `name_required` | Boolean | Make name required |
| `phone_required` | Boolean | Make phone required |
| `show_newsletter_consent` | Boolean | Show newsletter checkbox |
| `show_terms_consent` | Boolean | Show terms checkbox |
| `show_marketing_consent` | Boolean | Show marketing checkbox |

## Frontend JavaScript API

### SitePopup Object

```javascript
// Initialize with popup configs from API
SitePopup.init(popupConfigs);

// Check if popup should show
SitePopup.shouldShow(config);

// Check device targeting
SitePopup.checkDevice(config);

// Schedule popup based on trigger type
SitePopup.schedulePopup(config);

// Show popup immediately
SitePopup.showPopup(config);

// Close popup
SitePopup.closePopup(overlay, config);
```

### Events Tracked

- **Impressions** - Counted when popup is shown
- **Clicks** - Counted when CTA button is clicked
- **Closes** - Counted when popup is closed
- **Form Submissions** - Leads are stored in database

### Google Tag Manager Integration

The popup system pushes events to GTM dataLayer:

```javascript
// Events pushed to dataLayer:
{ event: 'popup_impression', popup_id: 123, popup_name: 'Summer Sale' }
{ event: 'popup_click', popup_id: 123, popup_name: 'Summer Sale' }
{ event: 'popup_close', popup_id: 123, popup_name: 'Summer Sale' }
{ event: 'popup_form_submit', popup_id: 123, popup_name: 'Summer Sale' }
```

## Admin Panel Features

### Popup List Page (`/admin/popups`)
- Grid view of all popups with mini previews
- Status badges (active, inactive, scheduled)
- Quick stats (impressions, clicks, conversion rate)
- Actions menu (edit, toggle, duplicate, delete)

### Popup Editor (`/admin/popups/create` or `/admin/popups/edit/<id>`)
- Split-screen design with live preview
- Device preview (desktop, tablet, mobile)
- Collapsible control sections
- Drag-and-drop element ordering
- Real-time preview updates

### Leads Page (`/admin/popup-leads`)
- Table view of all collected leads
- Filter by popup source
- Consent status indicators
- Device type icons
- Export to Excel functionality

## Customization

### Styling

The popup styling is inline for maximum compatibility. To customize:

1. Edit `popup-system.js` and modify the style strings in `showPopup()` function
2. Or override styles with CSS by targeting `.site-popup-overlay` and `.site-popup` classes

### Adding Custom Fields

1. Add new columns to `PopupLead` model
2. Update the form in `popup-system.js` `createForm()` function
3. Update the API endpoint to save new fields
4. Update the leads table template to display new columns

## Rate Limiting

The system includes basic rate limiting to prevent analytics manipulation:

```python
def _rate_limit_popup_tracking(popup_id, action):
    """Limit to 10 actions per popup per IP per minute"""
    key = f"popup_{action}_{popup_id}_{request.remote_addr}"
    # Implementation uses session or cache
```

## Requirements

- Flask
- Flask-SQLAlchemy
- Flask-Login (for admin routes)
- openpyxl (for Excel export)

## License

This popup system is provided for use in your Flask projects. Modify and extend as needed.
