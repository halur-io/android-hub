"""
Popup System API Routes
Add these to your routes.py file
"""

from flask import jsonify, request, session
from app import app, db  # Adjust imports based on your app structure
from models import Popup, PopupLead, CustomerConsent  # Adjust import


# ===== HELPER FUNCTIONS =====

def _validate_popup_request():
    """Basic validation for popup analytics requests"""
    referer = request.headers.get('Referer', '')
    host = request.host
    if referer and host not in referer:
        return False
    return True


def _rate_limit_popup_tracking(popup_id, action):
    """Simple session-based rate limiting for popup tracking"""
    key = f'popup_{action}_{popup_id}'
    if session.get(key):
        return False
    session[key] = True
    return True


# ===== API ROUTES =====

@app.route('/api/popups/active')
def api_active_popups():
    """Get all currently active popups for frontend display"""
    popups = Popup.query.filter_by(is_active=True).order_by(Popup.priority.desc()).all()
    active_popups = [p.to_frontend_config() for p in popups if p.is_currently_active()]
    return jsonify(active_popups)


@app.route('/api/popup/<int:popup_id>/impression', methods=['POST'])
def api_popup_impression(popup_id):
    """Track popup impression with rate limiting"""
    if not _validate_popup_request():
        return jsonify({'success': False}), 403
    if not _rate_limit_popup_tracking(popup_id, 'imp'):
        return jsonify({'success': True})
    popup = Popup.query.get(popup_id)
    if popup:
        popup.total_impressions = (popup.total_impressions or 0) + 1
        db.session.commit()
    return jsonify({'success': True})


@app.route('/api/popup/<int:popup_id>/click', methods=['POST'])
def api_popup_click(popup_id):
    """Track popup CTA button click with rate limiting"""
    if not _validate_popup_request():
        return jsonify({'success': False}), 403
    if not _rate_limit_popup_tracking(popup_id, 'click'):
        return jsonify({'success': True})
    popup = Popup.query.get(popup_id)
    if popup:
        popup.total_cta_clicks = (popup.total_cta_clicks or 0) + 1
        db.session.commit()
    return jsonify({'success': True})


@app.route('/api/popup/<int:popup_id>/close', methods=['POST'])
def api_popup_close(popup_id):
    """Track popup close with rate limiting"""
    if not _validate_popup_request():
        return jsonify({'success': False}), 403
    if not _rate_limit_popup_tracking(popup_id, 'close'):
        return jsonify({'success': True})
    popup = Popup.query.get(popup_id)
    if popup:
        popup.total_closes = (popup.total_closes or 0) + 1
        db.session.commit()
    return jsonify({'success': True})


@app.route('/api/popup/<int:popup_id>/submit', methods=['POST'])
def api_popup_form_submit(popup_id):
    """Handle popup form submission - collect lead, record consents"""
    if not _validate_popup_request():
        return jsonify({'success': False, 'error': 'Invalid request'}), 403
    
    popup = Popup.query.get(popup_id)
    if not popup or not popup.enable_form:
        return jsonify({'success': False, 'error': 'Popup not found or form not enabled'}), 404
    
    try:
        data = request.get_json() or {}
        
        email = (data.get('email') or '').strip().lower()
        name = (data.get('name') or '').strip()
        phone = (data.get('phone') or '').strip()
        source_page = data.get('source_page', '')
        
        newsletter_consent = data.get('newsletter_consent', False)
        terms_consent = data.get('terms_consent', False)
        marketing_consent = data.get('marketing_consent', False)
        
        # Validation
        if popup.collect_email and popup.email_required and not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400
        if popup.collect_name and popup.name_required and not name:
            return jsonify({'success': False, 'error': 'Name is required'}), 400
        if popup.collect_phone and popup.phone_required and not phone:
            return jsonify({'success': False, 'error': 'Phone is required'}), 400
        if popup.show_terms_consent and popup.terms_consent_required and not terms_consent:
            return jsonify({'success': False, 'error': 'Terms consent is required'}), 400
        
        # Device info
        user_agent = request.headers.get('User-Agent', '')[:500]
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip_address and ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()
        
        width = data.get('screen_width', 0)
        device_type = 'desktop'
        if width:
            if width < 768:
                device_type = 'mobile'
            elif width < 1024:
                device_type = 'tablet'
        
        # Create lead
        lead = PopupLead(
            email=email,
            name=name if name else None,
            phone=phone if phone else None,
            popup_id=popup_id,
            source_page=source_page[:500] if source_page else None,
            user_agent=user_agent,
            ip_address=ip_address[:45] if ip_address else None,
            device_type=device_type,
            is_subscribed=newsletter_consent,
            utm_source=data.get('utm_source'),
            utm_medium=data.get('utm_medium'),
            utm_campaign=data.get('utm_campaign')
        )
        db.session.add(lead)
        db.session.flush()
        
        lang = data.get('language', 'he')
        
        # Record consents
        if popup.show_newsletter_consent:
            consent = CustomerConsent(
                lead_id=lead.id,
                email=email,
                consent_type='newsletter',
                is_granted=newsletter_consent,
                consent_text=popup.newsletter_consent_text_he if lang == 'he' else popup.newsletter_consent_text_en,
                ip_address=ip_address,
                user_agent=user_agent,
                source_page=source_page,
                popup_id=popup_id
            )
            db.session.add(consent)
        
        if popup.show_terms_consent:
            consent = CustomerConsent(
                lead_id=lead.id,
                email=email,
                consent_type='terms_of_use',
                is_granted=terms_consent,
                consent_text=popup.terms_consent_text_he if lang == 'he' else popup.terms_consent_text_en,
                ip_address=ip_address,
                user_agent=user_agent,
                source_page=source_page,
                popup_id=popup_id
            )
            db.session.add(consent)
        
        if popup.show_marketing_consent:
            consent = CustomerConsent(
                lead_id=lead.id,
                email=email,
                consent_type='marketing_email',
                is_granted=marketing_consent,
                consent_text=popup.marketing_consent_text_he if lang == 'he' else popup.marketing_consent_text_en,
                ip_address=ip_address,
                user_agent=user_agent,
                source_page=source_page,
                popup_id=popup_id
            )
            db.session.add(consent)
        
        db.session.commit()
        
        success_message = popup.form_success_message_he if lang == 'he' else popup.form_success_message_en
        
        return jsonify({
            'success': True,
            'message': success_message
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
