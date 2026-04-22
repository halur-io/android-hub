# Popup System Models
# Add these models to your existing models.py file

from datetime import datetime
from app import db

class Popup(db.Model):
    __tablename__ = 'popups'
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    name = db.Column(db.String(100), nullable=False)
    
    # Content
    title_he = db.Column(db.String(200))
    title_en = db.Column(db.String(200))
    content_he = db.Column(db.Text)
    content_en = db.Column(db.Text)
    
    # Call to Action Button
    button_text_he = db.Column(db.String(100))
    button_text_en = db.Column(db.String(100))
    button_url = db.Column(db.String(500))
    button_action = db.Column(db.String(50), default='link')  # 'link', 'new_tab', 'close'
    
    # Media
    image_path = db.Column(db.String(500))
    image_display_type = db.Column(db.String(20), default='inline')  # 'inline', 'background', 'background_cover'
    video_url = db.Column(db.String(500))
    
    # Design Settings
    popup_type = db.Column(db.String(50), default='modal')
    popup_size = db.Column(db.String(20), default='medium')  # 'small', 'medium', 'large', 'fullscreen'
    popup_position = db.Column(db.String(50), default='center')
    
    # Colors
    background_color = db.Column(db.String(20), default='#ffffff')
    title_color = db.Column(db.String(20), default='#1B2951')
    text_color = db.Column(db.String(20), default='#333333')
    text_bg_color = db.Column(db.String(20), default='#000000')
    text_bg_opacity = db.Column(db.Integer, default=0)
    title_bg_color = db.Column(db.String(20), default='#000000')
    title_bg_opacity = db.Column(db.Integer, default=0)
    button_bg_color = db.Column(db.String(20), default='#C75450')
    button_bg_opacity = db.Column(db.Integer, default=100)
    button_text_color = db.Column(db.String(20), default='#ffffff')
    overlay_color = db.Column(db.String(20), default='rgba(0,0,0,0.5)')
    
    # Typography
    title_font_size = db.Column(db.Integer, default=24)
    content_font_size = db.Column(db.Integer, default=16)
    
    # Border & Shadow
    border_radius = db.Column(db.Integer, default=12)
    has_shadow = db.Column(db.Boolean, default=True)
    border_color = db.Column(db.String(20))
    border_width = db.Column(db.Integer, default=0)
    
    # Element Positions (for drag-and-drop designer)
    element_positions = db.Column(db.JSON, default=dict)
    
    # Timing Controls
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    show_delay_seconds = db.Column(db.Integer, default=3)
    
    # Display Frequency
    show_frequency = db.Column(db.String(50), default='once_per_session')
    show_every_x_days = db.Column(db.Integer, default=1)
    max_impressions_per_user = db.Column(db.Integer)
    
    # Trigger Options
    trigger_type = db.Column(db.String(50), default='time_delay')
    scroll_percentage = db.Column(db.Integer, default=50)
    exit_intent = db.Column(db.Boolean, default=False)
    
    # Page Targeting
    show_on_all_pages = db.Column(db.Boolean, default=True)
    target_pages = db.Column(db.JSON)
    exclude_pages = db.Column(db.JSON)
    
    # Device Targeting
    show_on_desktop = db.Column(db.Boolean, default=True)
    show_on_mobile = db.Column(db.Boolean, default=True)
    show_on_tablet = db.Column(db.Boolean, default=True)
    
    # Animation
    animation_in = db.Column(db.String(50), default='fadeIn')
    animation_out = db.Column(db.String(50), default='fadeOut')
    animation_duration = db.Column(db.Integer, default=300)
    
    # Close Button
    show_close_button = db.Column(db.Boolean, default=True)
    close_button_position = db.Column(db.String(20), default='top-right')
    allow_backdrop_close = db.Column(db.Boolean, default=True)
    auto_close_seconds = db.Column(db.Integer)
    
    # Form Collection Settings
    enable_form = db.Column(db.Boolean, default=False)
    form_submit_text_he = db.Column(db.String(100), default='שלח')
    form_submit_text_en = db.Column(db.String(100), default='Submit')
    form_success_message_he = db.Column(db.Text, default='תודה! קיבלנו את הפרטים שלך')
    form_success_message_en = db.Column(db.Text, default='Thank you! We received your details')
    
    # Form Fields Configuration
    collect_email = db.Column(db.Boolean, default=True)
    email_required = db.Column(db.Boolean, default=True)
    email_placeholder_he = db.Column(db.String(100), default='הזן את האימייל שלך')
    email_placeholder_en = db.Column(db.String(100), default='Enter your email')
    
    collect_name = db.Column(db.Boolean, default=False)
    name_required = db.Column(db.Boolean, default=False)
    name_placeholder_he = db.Column(db.String(100), default='הזן את שמך')
    name_placeholder_en = db.Column(db.String(100), default='Enter your name')
    
    collect_phone = db.Column(db.Boolean, default=False)
    phone_required = db.Column(db.Boolean, default=False)
    phone_placeholder_he = db.Column(db.String(100), default='הזן מספר טלפון')
    phone_placeholder_en = db.Column(db.String(100), default='Enter your phone number')
    
    # Consent Checkboxes
    show_newsletter_consent = db.Column(db.Boolean, default=True)
    newsletter_consent_text_he = db.Column(db.String(255), default='אני מסכים/ה לקבל עדכונים ומבצעים במייל')
    newsletter_consent_text_en = db.Column(db.String(255), default='I agree to receive updates and promotions by email')
    newsletter_default_checked = db.Column(db.Boolean, default=True)
    
    show_terms_consent = db.Column(db.Boolean, default=False)
    terms_consent_text_he = db.Column(db.String(255), default='אני מסכים/ה לתנאי השימוש')
    terms_consent_text_en = db.Column(db.String(255), default='I agree to the terms of service')
    terms_consent_required = db.Column(db.Boolean, default=False)
    terms_link = db.Column(db.String(500))
    
    show_marketing_consent = db.Column(db.Boolean, default=False)
    marketing_consent_text_he = db.Column(db.String(255), default='אני מסכים/ה לקבל הודעות שיווקיות')
    marketing_consent_text_en = db.Column(db.String(255), default='I agree to receive marketing messages')
    marketing_default_checked = db.Column(db.Boolean, default=False)
    
    # Status
    is_active = db.Column(db.Boolean, default=False)
    priority = db.Column(db.Integer, default=0)
    
    # Analytics
    total_impressions = db.Column(db.Integer, default=0)
    total_closes = db.Column(db.Integer, default=0)
    total_cta_clicks = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Popup {self.name}>'
    
    def is_currently_active(self):
        if not self.is_active:
            return False
        now = datetime.utcnow()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True
    
    def to_frontend_config(self):
        return {
            'id': self.id,
            'title_he': self.title_he,
            'title_en': self.title_en,
            'content_he': self.content_he,
            'content_en': self.content_en,
            'button_text_he': self.button_text_he,
            'button_text_en': self.button_text_en,
            'button_url': self.button_url,
            'button_action': self.button_action,
            'image_path': self.image_path,
            'image_display_type': self.image_display_type or 'inline',
            'video_url': self.video_url,
            'popup_type': self.popup_type,
            'popup_size': self.popup_size,
            'popup_position': self.popup_position,
            'background_color': self.background_color,
            'title_color': self.title_color,
            'text_color': self.text_color,
            'text_bg_color': self.text_bg_color,
            'text_bg_opacity': self.text_bg_opacity,
            'title_bg_color': self.title_bg_color,
            'title_bg_opacity': self.title_bg_opacity,
            'button_bg_color': self.button_bg_color,
            'button_bg_opacity': self.button_bg_opacity,
            'button_text_color': self.button_text_color,
            'overlay_color': self.overlay_color,
            'title_font_size': self.title_font_size,
            'content_font_size': self.content_font_size,
            'border_radius': self.border_radius,
            'has_shadow': self.has_shadow,
            'border_color': self.border_color,
            'border_width': self.border_width,
            'show_delay_seconds': self.show_delay_seconds,
            'show_frequency': self.show_frequency,
            'trigger_type': self.trigger_type,
            'scroll_percentage': self.scroll_percentage,
            'exit_intent': self.exit_intent,
            'animation_in': self.animation_in,
            'animation_out': self.animation_out,
            'animation_duration': self.animation_duration,
            'show_close_button': self.show_close_button,
            'close_button_position': self.close_button_position,
            'allow_backdrop_close': self.allow_backdrop_close,
            'auto_close_seconds': self.auto_close_seconds,
            'priority': self.priority,
            'enable_form': self.enable_form,
            'form_submit_text_he': self.form_submit_text_he,
            'form_submit_text_en': self.form_submit_text_en,
            'form_success_message_he': self.form_success_message_he,
            'form_success_message_en': self.form_success_message_en,
            'collect_email': self.collect_email,
            'email_required': self.email_required,
            'email_placeholder_he': self.email_placeholder_he,
            'email_placeholder_en': self.email_placeholder_en,
            'collect_name': self.collect_name,
            'name_required': self.name_required,
            'name_placeholder_he': self.name_placeholder_he,
            'name_placeholder_en': self.name_placeholder_en,
            'collect_phone': self.collect_phone,
            'phone_required': self.phone_required,
            'phone_placeholder_he': self.phone_placeholder_he,
            'phone_placeholder_en': self.phone_placeholder_en,
            'show_newsletter_consent': self.show_newsletter_consent,
            'newsletter_consent_text_he': self.newsletter_consent_text_he,
            'newsletter_consent_text_en': self.newsletter_consent_text_en,
            'newsletter_default_checked': self.newsletter_default_checked,
            'show_terms_consent': self.show_terms_consent,
            'terms_consent_text_he': self.terms_consent_text_he,
            'terms_consent_text_en': self.terms_consent_text_en,
            'terms_consent_required': self.terms_consent_required,
            'terms_link': self.terms_link,
            'show_marketing_consent': self.show_marketing_consent,
            'marketing_consent_text_he': self.marketing_consent_text_he,
            'marketing_consent_text_en': self.marketing_consent_text_en,
            'marketing_default_checked': self.marketing_default_checked,
            'show_on_desktop': self.show_on_desktop if self.show_on_desktop is not None else True,
            'show_on_mobile': self.show_on_mobile if self.show_on_mobile is not None else True,
            'show_on_tablet': self.show_on_tablet if self.show_on_tablet is not None else True,
            'show_every_x_days': self.show_every_x_days
        }


class PopupLead(db.Model):
    """Leads collected through popup forms"""
    __tablename__ = 'popup_leads'
    id = db.Column(db.Integer, primary_key=True)
    
    # Lead Information
    email = db.Column(db.String(255), nullable=False, index=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    
    # Source
    popup_id = db.Column(db.Integer, db.ForeignKey('popups.id'), nullable=True)
    source_page = db.Column(db.String(500))
    
    # Status
    email_verified = db.Column(db.Boolean, default=False)
    is_subscribed = db.Column(db.Boolean, default=True)
    
    # UTM Tracking
    utm_source = db.Column(db.String(100))
    utm_medium = db.Column(db.String(100))
    utm_campaign = db.Column(db.String(100))
    
    # Device/Browser Info
    user_agent = db.Column(db.String(500))
    ip_address = db.Column(db.String(45))
    device_type = db.Column(db.String(20))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    popup = db.relationship('Popup', backref='leads')
    consents = db.relationship('CustomerConsent', backref='lead', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<PopupLead {self.email}>'


class CustomerConsent(db.Model):
    """Track customer consents for GDPR/privacy compliance"""
    __tablename__ = 'customer_consents'
    id = db.Column(db.Integer, primary_key=True)
    
    # Associated Lead
    lead_id = db.Column(db.Integer, db.ForeignKey('popup_leads.id'), nullable=False, index=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    
    # Consent Types: 'marketing_email', 'marketing_sms', 'terms_of_use', 'privacy_policy', 'newsletter'
    consent_type = db.Column(db.String(50), nullable=False)
    
    # Consent Status
    is_granted = db.Column(db.Boolean, default=False)
    consent_text = db.Column(db.Text)
    consent_version = db.Column(db.String(20), default='1.0')
    
    # Tracking
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    source_page = db.Column(db.String(500))
    popup_id = db.Column(db.Integer, db.ForeignKey('popups.id'), nullable=True)
    
    # Timestamps
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)
    revoked_at = db.Column(db.DateTime)
    
    # Relationships
    popup = db.relationship('Popup', backref='consents')
    
    def __repr__(self):
        return f'<CustomerConsent {self.email} - {self.consent_type}>'
    
    def revoke(self):
        """Revoke this consent"""
        self.is_granted = False
        self.revoked_at = datetime.utcnow()
