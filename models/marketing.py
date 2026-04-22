from database import db
from datetime import datetime

class Popup(db.Model):
    __tablename__ = 'popups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    title_he = db.Column(db.String(200))
    title_en = db.Column(db.String(200))
    content_he = db.Column(db.Text)
    content_en = db.Column(db.Text)
    button_text_he = db.Column(db.String(100))
    button_text_en = db.Column(db.String(100))
    button_url = db.Column(db.String(500))
    button_action = db.Column(db.String(50), default='link')
    image_path = db.Column(db.String(500))
    image_display_type = db.Column(db.String(20), default='inline')
    video_url = db.Column(db.String(500))
    popup_type = db.Column(db.String(50), default='modal')
    popup_size = db.Column(db.String(20), default='medium')
    popup_position = db.Column(db.String(50), default='center')
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
    title_font_size = db.Column(db.Integer, default=24)
    content_font_size = db.Column(db.Integer, default=16)
    border_radius = db.Column(db.Integer, default=12)
    has_shadow = db.Column(db.Boolean, default=True)
    border_color = db.Column(db.String(20))
    border_width = db.Column(db.Integer, default=0)
    element_positions = db.Column(db.JSON, default=dict)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    show_delay_seconds = db.Column(db.Integer, default=3)
    show_frequency = db.Column(db.String(50), default='once_per_session')
    show_every_x_days = db.Column(db.Integer, default=1)
    max_impressions_per_user = db.Column(db.Integer)
    trigger_type = db.Column(db.String(50), default='time_delay')
    scroll_percentage = db.Column(db.Integer, default=50)
    exit_intent = db.Column(db.Boolean, default=False)
    show_on_all_pages = db.Column(db.Boolean, default=True)
    target_pages = db.Column(db.JSON)
    exclude_pages = db.Column(db.JSON)
    show_on_desktop = db.Column(db.Boolean, default=True)
    show_on_mobile = db.Column(db.Boolean, default=True)
    show_on_tablet = db.Column(db.Boolean, default=True)
    animation_in = db.Column(db.String(50), default='fadeIn')
    animation_out = db.Column(db.String(50), default='fadeOut')
    animation_duration = db.Column(db.Integer, default=300)
    show_close_button = db.Column(db.Boolean, default=True)
    close_button_position = db.Column(db.String(20), default='top-right')
    allow_backdrop_close = db.Column(db.Boolean, default=True)
    auto_close_seconds = db.Column(db.Integer)
    enable_form = db.Column(db.Boolean, default=False)
    form_submit_text_he = db.Column(db.String(100), default='שלח')
    form_submit_text_en = db.Column(db.String(100), default='Submit')
    form_success_message_he = db.Column(db.Text, default='תודה! קיבלנו את הפרטים שלך')
    form_success_message_en = db.Column(db.Text, default='Thank you! We received your details')
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
    associated_coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'), nullable=True)
    send_coupon_on_submit = db.Column(db.Boolean, default=False)
    coupon_email_subject_he = db.Column(db.String(255), default='הקופון שלך מגיע!')
    coupon_email_subject_en = db.Column(db.String(255), default='Your coupon has arrived!')
    is_active = db.Column(db.Boolean, default=False)
    priority = db.Column(db.Integer, default=0)
    total_impressions = db.Column(db.Integer, default=0)
    total_closes = db.Column(db.Integer, default=0)
    total_cta_clicks = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    creator = db.relationship('AdminUser', backref='created_popups')
    associated_coupon = db.relationship('Coupon', foreign_keys=[associated_coupon_id], backref='associated_popups')

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
            'send_coupon_on_submit': self.send_coupon_on_submit,
            'show_on_desktop': self.show_on_desktop if self.show_on_desktop is not None else True,
            'show_on_mobile': self.show_on_mobile if self.show_on_mobile is not None else True,
            'show_on_tablet': self.show_on_tablet if self.show_on_tablet is not None else True,
            'show_every_x_days': self.show_every_x_days
        }


class Coupon(db.Model):
    __tablename__ = 'coupons'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description_he = db.Column(db.Text)
    description_en = db.Column(db.Text)
    discount_type = db.Column(db.String(20), default='percentage')
    discount_value = db.Column(db.Float, default=0)
    minimum_order_amount = db.Column(db.Float, default=0)
    maximum_discount_amount = db.Column(db.Float)
    max_total_uses = db.Column(db.Integer)
    max_uses_per_email = db.Column(db.Integer, default=1)
    current_uses = db.Column(db.Integer, default=0)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    qr_code_path = db.Column(db.String(500))
    qr_code_data = db.Column(db.Text)
    popup_id = db.Column(db.Integer, db.ForeignKey('popups.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    popup = db.relationship('Popup', foreign_keys=[popup_id], backref='coupons')
    creator = db.relationship('AdminUser', backref='created_coupons')
    usages = db.relationship('CouponUsage', backref='coupon', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Coupon {self.code}>'

    def is_valid(self):
        if not self.is_active:
            return False
        now = datetime.utcnow()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        if self.max_total_uses and self.current_uses >= self.max_total_uses:
            return False
        return True

    def can_be_used_by_email(self, email):
        if not self.is_valid():
            return False
        if self.max_uses_per_email is None:
            return True
        normalized_email = email.lower().strip()
        usage_count = CouponUsage.query.filter_by(
            coupon_id=self.id,
            email=normalized_email
        ).count()
        return usage_count < self.max_uses_per_email

    def get_usage_count(self):
        return self.usages.count()

    def record_usage(self, email, lead_id=None):
        normalized_email = email.lower().strip()
        usage = CouponUsage(
            coupon_id=self.id,
            email=normalized_email,
            lead_id=lead_id
        )
        self.current_uses = self.get_usage_count() + 1
        db.session.add(usage)
        return usage

    def generate_qr_code(self, base_url=None):
        import qrcode
        import os
        from io import BytesIO
        import base64

        upload_dir = 'static/uploads/qrcodes'
        os.makedirs(upload_dir, exist_ok=True)

        qr_data = self.code
        if base_url:
            qr_data = f"{base_url}?coupon={self.code}"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        filename = f"coupon_qr_{self.id}_{self.code}.png"
        filepath = os.path.join(upload_dir, filename)
        img.save(filepath)

        self.qr_code_path = f"/static/uploads/qrcodes/{filename}"
        self.qr_code_data = qr_data

        return self.qr_code_path

    def get_qr_code_base64(self):
        import qrcode
        from io import BytesIO
        import base64

        qr_data = self.qr_code_data or self.code

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        return base64.b64encode(buffer.getvalue()).decode('utf-8')


class CouponUsage(db.Model):
    __tablename__ = 'coupon_usages'
    id = db.Column(db.Integer, primary_key=True)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'), nullable=False, index=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('popup_leads.id'), nullable=True)
    used_at = db.Column(db.DateTime, default=datetime.utcnow)
    order_amount = db.Column(db.Float)
    discount_applied = db.Column(db.Float)
    __table_args__ = (
        db.Index('idx_coupon_email', 'coupon_id', 'email'),
    )

    def __repr__(self):
        return f'<CouponUsage {self.coupon_id} - {self.email}>'


class Deal(db.Model):
    __tablename__ = 'deals'
    id = db.Column(db.Integer, primary_key=True)
    name_he = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200))
    description_he = db.Column(db.Text)
    description_en = db.Column(db.Text)
    included_items = db.Column(db.JSON, default=list)
    deal_price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float)
    deal_type = db.Column(db.String(20), default='fixed')
    source_category_id = db.Column(db.Integer, db.ForeignKey('menu_categories.id', ondelete='SET NULL'), nullable=True)
    source_category_ids = db.Column(db.JSON, default=list)
    pick_count = db.Column(db.Integer, default=0)

    @property
    def effective_category_ids(self):
        ids = self.source_category_ids or []
        if not ids and self.source_category_id:
            ids = [self.source_category_id]
        return [int(x) for x in ids if x]

    image_path = db.Column(db.String(500))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def is_valid(self):
        if not self.is_active:
            return False
        now = datetime.utcnow()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True

    def __repr__(self):
        return f'<Deal {self.name_he}>'


class UpsellRule(db.Model):
    __tablename__ = 'upsell_rules'
    id = db.Column(db.Integer, primary_key=True)
    trigger_type = db.Column(db.String(20), nullable=False, default='category')
    trigger_id = db.Column(db.Integer, nullable=False)
    suggested_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    message_he = db.Column(db.String(300))
    message_en = db.Column(db.String(300))
    discounted_price = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    suggested_item = db.relationship('MenuItem', foreign_keys=[suggested_item_id])

    def __repr__(self):
        return f'<UpsellRule {self.id} -> item {self.suggested_item_id}>'


class PopupLead(db.Model):
    __tablename__ = 'popup_leads'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    popup_id = db.Column(db.Integer, db.ForeignKey('popups.id'), nullable=True)
    source_page = db.Column(db.String(500))
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'), nullable=True)
    coupon_code_sent = db.Column(db.String(50))
    coupon_sent_at = db.Column(db.DateTime)
    email_verified = db.Column(db.Boolean, default=False)
    is_subscribed = db.Column(db.Boolean, default=True)
    utm_source = db.Column(db.String(100))
    utm_medium = db.Column(db.String(100))
    utm_campaign = db.Column(db.String(100))
    user_agent = db.Column(db.String(500))
    ip_address = db.Column(db.String(45))
    device_type = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    popup = db.relationship('Popup', backref='leads')
    coupon = db.relationship('Coupon', backref='leads')
    consents = db.relationship('CustomerConsent', backref='lead', lazy='dynamic', cascade='all, delete-orphan')
    coupon_usages = db.relationship('CouponUsage', backref='lead', lazy='dynamic')

    def __repr__(self):
        return f'<PopupLead {self.email}>'


class CustomerConsent(db.Model):
    __tablename__ = 'customer_consents'
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('popup_leads.id'), nullable=False, index=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    consent_type = db.Column(db.String(50), nullable=False)
    is_granted = db.Column(db.Boolean, default=False)
    consent_text = db.Column(db.Text)
    consent_version = db.Column(db.String(20), default='1.0')
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    source_page = db.Column(db.String(500))
    popup_id = db.Column(db.Integer, db.ForeignKey('popups.id'), nullable=True)
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)
    revoked_at = db.Column(db.DateTime)
    popup = db.relationship('Popup', backref='consents')

    def __repr__(self):
        return f'<CustomerConsent {self.email} - {self.consent_type}>'

    def revoke(self):
        self.is_granted = False
        self.revoked_at = datetime.utcnow()
