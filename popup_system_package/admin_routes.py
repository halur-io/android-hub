# Admin Popup Routes
# Add these routes to your admin blueprint

import os
from datetime import datetime
from io import BytesIO
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from models import Popup, PopupLead, CustomerConsent

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@admin_bp.route('/popups')
@login_required
def popups():
    """List all popups with stats"""
    popups = Popup.query.order_by(Popup.priority.desc(), Popup.created_at.desc()).all()
    total_leads = PopupLead.query.count()
    return render_template('admin/popups.html', popups=popups, total_leads=total_leads)


@admin_bp.route('/popup-leads')
@login_required
def popup_leads():
    """View collected leads with pagination"""
    page = request.args.get('page', 1, type=int)
    leads = PopupLead.query.order_by(PopupLead.created_at.desc()).paginate(page=page, per_page=50)
    
    # Get popup names for display
    popup_ids = list(set(l.popup_id for l in leads.items if l.popup_id))
    popup_names = {}
    if popup_ids:
        popups = Popup.query.filter(Popup.id.in_(popup_ids)).all()
        popup_names = {p.id: p.name for p in popups}
    
    # Get consents for each lead
    lead_ids = [l.id for l in leads.items]
    consents = CustomerConsent.query.filter(CustomerConsent.lead_id.in_(lead_ids)).all()
    lead_consents = {}
    for consent in consents:
        if consent.lead_id not in lead_consents:
            lead_consents[consent.lead_id] = {}
        lead_consents[consent.lead_id][consent.consent_type] = consent.is_granted
    
    return render_template('admin/popup_leads.html', 
                         leads=leads, 
                         popup_names=popup_names,
                         lead_consents=lead_consents)


@admin_bp.route('/popup-leads/export')
@login_required
def export_popup_leads():
    """Export leads to Excel"""
    try:
        from openpyxl import Workbook
    except ImportError:
        flash('openpyxl package required for Excel export', 'error')
        return redirect(url_for('admin.popup_leads'))
    
    leads = PopupLead.query.order_by(PopupLead.created_at.desc()).all()
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Popup Leads"
    
    # Headers
    headers = ['ID', 'Name', 'Email', 'Phone', 'Popup', 'Subscribed', 'Device', 'Date']
    ws.append(headers)
    
    # Get popup names
    popup_ids = list(set(l.popup_id for l in leads if l.popup_id))
    popup_names = {}
    if popup_ids:
        popups = Popup.query.filter(Popup.id.in_(popup_ids)).all()
        popup_names = {p.id: p.name for p in popups}
    
    # Data rows
    for lead in leads:
        ws.append([
            lead.id,
            lead.name or '',
            lead.email,
            lead.phone or '',
            popup_names.get(lead.popup_id, 'Unknown'),
            'Yes' if lead.is_subscribed else 'No',
            lead.device_type or 'desktop',
            lead.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    # Save to BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    filename = f"popup_leads_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    return send_file(output, as_attachment=True, download_name=filename,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@admin_bp.route('/popups/create', methods=['GET', 'POST'])
@login_required
def create_popup():
    """Create new popup"""
    if request.method == 'POST':
        popup = Popup()
        _populate_popup_from_form(popup, request)
        db.session.add(popup)
        db.session.commit()
        flash('Popup created successfully', 'success')
        return redirect(url_for('admin.popups'))
    
    return render_template('admin/popup_form.html', popup=None)


@admin_bp.route('/popups/<int:popup_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_popup(popup_id):
    """Edit existing popup"""
    popup = Popup.query.get_or_404(popup_id)
    
    if request.method == 'POST':
        _populate_popup_from_form(popup, request)
        db.session.commit()
        flash('Popup updated successfully', 'success')
        return redirect(url_for('admin.popups'))
    
    return render_template('admin/popup_form.html', popup=popup)


@admin_bp.route('/popups/<int:popup_id>/delete', methods=['POST'])
@login_required
def delete_popup(popup_id):
    """Delete popup"""
    popup = Popup.query.get_or_404(popup_id)
    db.session.delete(popup)
    db.session.commit()
    flash('Popup deleted', 'success')
    return redirect(url_for('admin.popups'))


@admin_bp.route('/popups/<int:popup_id>/toggle', methods=['POST'])
@login_required
def toggle_popup(popup_id):
    """Toggle popup active status"""
    popup = Popup.query.get_or_404(popup_id)
    popup.is_active = not popup.is_active
    db.session.commit()
    flash(f"Popup {'activated' if popup.is_active else 'deactivated'}", 'success')
    return redirect(url_for('admin.popups'))


@admin_bp.route('/popups/<int:popup_id>/duplicate', methods=['POST'])
@login_required
def duplicate_popup(popup_id):
    """Duplicate popup"""
    original = Popup.query.get_or_404(popup_id)
    
    new_popup = Popup()
    # Copy all fields except id and analytics
    for column in Popup.__table__.columns:
        if column.name not in ['id', 'total_impressions', 'total_closes', 'total_cta_clicks', 'created_at', 'updated_at']:
            setattr(new_popup, column.name, getattr(original, column.name))
    
    new_popup.name = f"{original.name} (copy)"
    new_popup.is_active = False
    new_popup.total_impressions = 0
    new_popup.total_closes = 0
    new_popup.total_cta_clicks = 0
    
    db.session.add(new_popup)
    db.session.commit()
    
    flash('Popup duplicated', 'success')
    return redirect(url_for('admin.popups'))


def _populate_popup_from_form(popup, request):
    """Helper to populate popup from form data"""
    # Basic info
    popup.name = request.form.get('name', '').strip()
    popup.title_he = request.form.get('title_he', '').strip()
    popup.title_en = request.form.get('title_en', '').strip()
    popup.content_he = request.form.get('content_he', '').strip()
    popup.content_en = request.form.get('content_en', '').strip()
    
    # Button
    popup.button_text_he = request.form.get('button_text_he', '').strip()
    popup.button_text_en = request.form.get('button_text_en', '').strip()
    popup.button_url = request.form.get('button_url', '').strip()
    popup.button_action = request.form.get('button_action', 'link')
    
    # Design
    popup.popup_size = request.form.get('popup_size', 'medium')
    popup.popup_position = request.form.get('popup_position', 'center')
    popup.background_color = request.form.get('background_color', '#ffffff')
    popup.title_color = request.form.get('title_color', '#1B2951')
    popup.text_color = request.form.get('text_color', '#333333')
    popup.button_bg_color = request.form.get('button_bg_color', '#C75450')
    popup.button_text_color = request.form.get('button_text_color', '#ffffff')
    popup.overlay_color = request.form.get('overlay_color', 'rgba(0,0,0,0.5)')
    popup.border_radius = int(request.form.get('border_radius', 12))
    popup.has_shadow = request.form.get('has_shadow') == 'on'
    
    # Typography
    popup.title_font_size = int(request.form.get('title_font_size', 24))
    popup.content_font_size = int(request.form.get('content_font_size', 16))
    
    # Timing
    popup.show_delay_seconds = int(request.form.get('show_delay_seconds', 3))
    popup.show_frequency = request.form.get('show_frequency', 'once_per_session')
    popup.show_every_x_days = int(request.form.get('show_every_x_days', 1))
    popup.trigger_type = request.form.get('trigger_type', 'time_delay')
    popup.scroll_percentage = int(request.form.get('scroll_percentage', 50))
    
    # Device targeting
    popup.show_on_desktop = request.form.get('show_on_desktop') == 'on'
    popup.show_on_mobile = request.form.get('show_on_mobile') == 'on'
    popup.show_on_tablet = request.form.get('show_on_tablet') == 'on'
    
    # Close button
    popup.show_close_button = request.form.get('show_close_button') == 'on'
    popup.close_button_position = request.form.get('close_button_position', 'top-right')
    popup.allow_backdrop_close = request.form.get('allow_backdrop_close') == 'on'
    
    # Form settings
    popup.enable_form = request.form.get('enable_form') == 'on'
    popup.collect_email = request.form.get('collect_email') == 'on'
    popup.email_required = request.form.get('email_required') == 'on'
    popup.collect_name = request.form.get('collect_name') == 'on'
    popup.name_required = request.form.get('name_required') == 'on'
    popup.collect_phone = request.form.get('collect_phone') == 'on'
    popup.phone_required = request.form.get('phone_required') == 'on'
    popup.form_submit_text_he = request.form.get('form_submit_text_he', 'שלח')
    popup.form_submit_text_en = request.form.get('form_submit_text_en', 'Submit')
    popup.form_success_message_he = request.form.get('form_success_message_he', '')
    popup.form_success_message_en = request.form.get('form_success_message_en', '')
    
    # Consents
    popup.show_newsletter_consent = request.form.get('show_newsletter_consent') == 'on'
    popup.newsletter_consent_text_he = request.form.get('newsletter_consent_text_he', '')
    popup.newsletter_consent_text_en = request.form.get('newsletter_consent_text_en', '')
    popup.newsletter_default_checked = request.form.get('newsletter_default_checked') == 'on'
    popup.show_terms_consent = request.form.get('show_terms_consent') == 'on'
    popup.terms_consent_text_he = request.form.get('terms_consent_text_he', '')
    popup.terms_consent_text_en = request.form.get('terms_consent_text_en', '')
    popup.terms_consent_required = request.form.get('terms_consent_required') == 'on'
    popup.show_marketing_consent = request.form.get('show_marketing_consent') == 'on'
    popup.marketing_consent_text_he = request.form.get('marketing_consent_text_he', '')
    popup.marketing_consent_text_en = request.form.get('marketing_consent_text_en', '')
    popup.marketing_default_checked = request.form.get('marketing_default_checked') == 'on'
    
    # Status
    popup.is_active = request.form.get('is_active') == 'on'
    popup.priority = int(request.form.get('priority', 0))
    
    # Dates
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    if start_date:
        popup.start_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
    if end_date:
        popup.end_date = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')
    
    # Image upload
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"popup_{timestamp}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            popup.image_path = f"/static/uploads/{filename}"
    
    popup.image_display_type = request.form.get('image_display_type', 'inline')
    
    # Element positions
    import json
    element_positions = request.form.get('element_positions')
    if element_positions:
        try:
            popup.element_positions = json.loads(element_positions)
        except:
            pass
    
    return popup
