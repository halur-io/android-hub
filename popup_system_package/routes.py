# Public Popup API Routes
# Add these routes to your main routes.py file

from flask import jsonify, request
from app import app, db
from models import Popup, PopupLead, CustomerConsent


def _rate_limit_popup_tracking(popup_id, action):
    """Basic rate limiting - 10 actions per popup per IP per minute"""
    key = f"popup_{action}_{popup_id}_{request.remote_addr}"
    count = session.get(key, 0)
    if count >= 10:
        return False
    session[key] = count + 1
    return True


@app.route('/api/popups/active')
def api_active_popups():
    """Get all currently active popups for frontend display"""
    popups = Popup.query.filter_by(is_active=True).all()
    active_popups = [p.to_frontend_config() for p in popups if p.is_currently_active()]
    return jsonify(active_popups)


@app.route('/api/popup/<int:popup_id>/impression', methods=['POST'])
def api_popup_impression(popup_id):
    """Track popup impression (when popup is shown)"""
    popup = Popup.query.get_or_404(popup_id)
    if _rate_limit_popup_tracking(popup_id, 'impression'):
        popup.total_impressions += 1
        db.session.commit()
    return jsonify({'success': True})


@app.route('/api/popup/<int:popup_id>/click', methods=['POST'])
def api_popup_click(popup_id):
    """Track CTA button click"""
    popup = Popup.query.get_or_404(popup_id)
    if _rate_limit_popup_tracking(popup_id, 'click'):
        popup.total_cta_clicks += 1
        db.session.commit()
    return jsonify({'success': True})


@app.route('/api/popup/<int:popup_id>/close', methods=['POST'])
def api_popup_close(popup_id):
    """Track popup close"""
    popup = Popup.query.get_or_404(popup_id)
    if _rate_limit_popup_tracking(popup_id, 'close'):
        popup.total_closes += 1
        db.session.commit()
    return jsonify({'success': True})


@app.route('/api/popup/<int:popup_id>/submit', methods=['POST'])
def api_popup_form_submit(popup_id):
    """Handle popup form submission and save lead"""
    popup = Popup.query.get_or_404(popup_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    # Detect device type from user agent
    user_agent = request.user_agent.string.lower()
    if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
        device_type = 'mobile'
    elif 'tablet' in user_agent or 'ipad' in user_agent:
        device_type = 'tablet'
    else:
        device_type = 'desktop'
    
    # Create lead
    lead = PopupLead(
        popup_id=popup_id,
        email=data.get('email', '').strip().lower(),
        name=data.get('name', '').strip() if data.get('name') else None,
        phone=data.get('phone', '').strip() if data.get('phone') else None,
        is_subscribed=data.get('newsletter_consent', False),
        source_page=data.get('source_page') or request.referrer,
        user_agent=request.user_agent.string[:500],
        ip_address=request.remote_addr,
        device_type=device_type
    )
    db.session.add(lead)
    db.session.flush()  # Get lead ID before committing
    
    # Store consents
    consents_to_store = []
    
    if data.get('newsletter_consent'):
        consents_to_store.append(('newsletter', popup.newsletter_consent_text_he))
    
    if data.get('terms_consent'):
        consents_to_store.append(('terms_of_use', popup.terms_consent_text_he))
    
    if data.get('marketing_consent'):
        consents_to_store.append(('marketing_email', popup.marketing_consent_text_he))
    
    for consent_type, consent_text in consents_to_store:
        consent = CustomerConsent(
            lead_id=lead.id,
            email=lead.email,
            consent_type=consent_type,
            is_granted=True,
            consent_text=consent_text,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string[:500],
            source_page=data.get('source_page') or request.referrer,
            popup_id=popup_id
        )
        db.session.add(consent)
    
    db.session.commit()
    
    # Determine language for response
    lang = request.headers.get('Accept-Language', 'he')
    is_hebrew = 'he' in lang
    
    success_message = popup.form_success_message_he if is_hebrew else popup.form_success_message_en
    
    return jsonify({
        'success': True,
        'message': success_message or 'Thank you!'
    })
