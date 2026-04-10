from database import db
from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Association table for menu items and dietary properties (define before classes)
menu_item_dietary_properties = db.Table('menu_item_dietary_properties',
    db.Column('menu_item_id', db.Integer, db.ForeignKey('menu_items.id'), primary_key=True),
    db.Column('dietary_property_id', db.Integer, db.ForeignKey('dietary_properties.id'), primary_key=True)
)

# Admin User Model
# Association Tables for Many-to-Many Relationships
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('admin_users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)

role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
)

# Role Model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    is_system_role = db.Column(db.Boolean, default=False)  # Cannot be deleted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    permissions = db.relationship('Permission', secondary=role_permissions, lazy='subquery', backref=db.backref('roles', lazy=True))
    
    def __repr__(self):
        return f'<Role {self.name}>'
    
    def has_permission(self, permission_name):
        """Check if role has a specific permission"""
        return any(p.name == permission_name for p in self.permissions)

# Permission Model
class Permission(db.Model):
    __tablename__ = 'permissions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)  # e.g., 'users.create'
    display_name = db.Column(db.String(100), nullable=False)  # e.g., 'Create Users'
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)  # e.g., 'users', 'orders', 'kitchen'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Permission {self.name}>'

class AdminUser(UserMixin, db.Model):
    __tablename__ = 'admin_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_active = db.Column(db.Boolean, default=True)
    is_superadmin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    roles = db.relationship('Role', secondary=user_roles, lazy='subquery', backref=db.backref('users', lazy=True))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role_name):
        """Check if user has a specific role"""
        return any(r.name == role_name for r in self.roles)
    
    def has_permission(self, permission_name):
        """Check if user has a specific permission through their roles"""
        if self.is_superadmin:
            return True  # Superadmin has all permissions
        
        for role in self.roles:
            if role.has_permission(permission_name):
                return True
        return False
    
    def get_permissions(self):
        """Get all permissions for this user"""
        if self.is_superadmin:
            return Permission.query.all()  # Superadmin gets all permissions
        
        permissions = set()
        for role in self.roles:
            permissions.update(role.permissions)
        return list(permissions)
    
    def add_role(self, role):
        """Add a role to the user"""
        if not self.has_role(role.name):
            self.roles.append(role)
    
    def remove_role(self, role):
        """Remove a role from the user"""
        if self.has_role(role.name):
            self.roles.remove(role)

# Website Settings
class SiteSettings(db.Model):
    __tablename__ = 'site_settings'
    id = db.Column(db.Integer, primary_key=True)
    site_name_he = db.Column(db.String(100), default='סומו')
    site_name_en = db.Column(db.String(100), default='SUMO')
    hero_title_he = db.Column(db.String(200), default='סומו')
    hero_title_en = db.Column(db.String(200), default='SUMO')
    hero_subtitle_he = db.Column(db.String(200), default='מטבח אסייתי אותנטי')
    hero_subtitle_en = db.Column(db.String(200), default='Authentic Asian Kitchen')
    hero_description_he = db.Column(db.Text, default='חוויה קולינרית ייחודית של טעמי אסיה')
    hero_description_en = db.Column(db.Text, default='A unique culinary experience of Asian flavors')
    about_title_he = db.Column(db.String(200))
    about_title_en = db.Column(db.String(200))
    about_content_he = db.Column(db.Text)
    about_content_en = db.Column(db.Text)
    facebook_url = db.Column(db.String(255))
    instagram_url = db.Column(db.String(255))
    whatsapp_number = db.Column(db.String(20))
    
    # Branding & Media Settings
    hero_desktop_image = db.Column(db.String(255))  # Desktop hero background image
    logo_image = db.Column(db.String(255))  # Main logo
    favicon_image = db.Column(db.String(255))  # Browser favicon
    primary_color = db.Column(db.String(20), default='#1a3a6e')  # Navy blue
    accent_color = db.Column(db.String(20), default='#dc3545')  # Red
    
    # Feature Toggles
    enable_online_ordering = db.Column(db.Boolean, default=True)
    enable_english_language = db.Column(db.Boolean, default=True)
    enable_delivery = db.Column(db.Boolean, default=True)
    enable_pickup = db.Column(db.Boolean, default=True)
    enable_menu_display = db.Column(db.Boolean, default=True)
    enable_gallery = db.Column(db.Boolean, default=True)
    enable_gallery_section = db.Column(db.Boolean, default=True)  # Show gallery section on homepage
    enable_contact_form = db.Column(db.Boolean, default=True)
    enable_table_reservations = db.Column(db.Boolean, default=True)
    
    # Gallery Section Settings
    gallery_section_title_he = db.Column(db.String(200), default='גלריה')
    gallery_section_title_en = db.Column(db.String(200), default='Gallery')
    gallery_section_subtitle_he = db.Column(db.String(500))
    gallery_section_subtitle_en = db.Column(db.String(500))
    gallery_max_photos = db.Column(db.Integer, default=8)  # Maximum photos to display
    
    # Mobile App Settings
    enable_app_download = db.Column(db.Boolean, default=True)
    app_store_url = db.Column(db.String(500))  # iOS App Store URL
    google_play_url = db.Column(db.String(500))  # Google Play Store URL
    app_promo_text_he = db.Column(db.String(200), default='הורידו את האפליקציה שלנו!')
    app_promo_text_en = db.Column(db.String(200), default='Download our app!')
    app_discount_text_he = db.Column(db.String(200), default='קבלו 10% הנחה בהזמנה הראשונה באפליקציה')
    app_discount_text_en = db.Column(db.String(200), default='Get 10% off your first app order')
    show_app_banner = db.Column(db.Boolean, default=True)  # Show smart banner on mobile
    app_banner_title_he = db.Column(db.String(200), default='הזמנות רק באפליקציה')
    app_banner_title_en = db.Column(db.String(200), default='Order via App')
    app_banner_subtitle_he = db.Column(db.String(200), default='הורידו עכשיו')
    app_banner_subtitle_en = db.Column(db.String(200), default='Download Now')
    
    # Order Settings
    minimum_order_amount = db.Column(db.Float, default=50)
    tax_rate = db.Column(db.Float, default=0.17)  # 17% VAT in Israel
    
    # Delivery & Order Settings
    delivery_fee = db.Column(db.Float, default=15.0)  # Fixed delivery fee
    free_delivery_threshold = db.Column(db.Float, default=100.0)  # Free delivery over this amount
    estimated_delivery_time = db.Column(db.String(100), default='45-60')  # Minutes
    service_fee_percentage = db.Column(db.Float, default=0.0)  # Service fee %
    currency_symbol = db.Column(db.String(10), default='₪')
    
    # Form Email Configuration - Where form messages are sent
    contact_form_email = db.Column(db.String(255), default='info@sumo-restaurant.co.il')  # Contact form recipient
    catering_form_email = db.Column(db.String(255), default='info@sumo-restaurant.co.il')  # Catering form recipient
    careers_form_email = db.Column(db.String(255), default='info@sumo-restaurant.co.il')  # Careers form recipient
    
    # Email Subject Configuration - Custom subjects for notification emails
    contact_email_subject = db.Column(db.String(255), default='הודעה חדשה מהאתר')
    catering_email_subject = db.Column(db.String(255), default='פנייה חדשה לקייטרינג')
    careers_email_subject = db.Column(db.String(255), default='מועמדות חדשה לעבודה')
    
    # Catering & Special Events Settings (Homepage Section)
    enable_catering_section = db.Column(db.Boolean, default=True)
    catering_title_he = db.Column(db.String(200), default='קייטרינג ואירועים מיוחדים')
    catering_title_en = db.Column(db.String(200), default='Catering & Special Events')
    catering_subtitle_he = db.Column(db.Text, default='הביאו את הטעמים האסיאתיים האותנטיים לחגיגה הבאה שלכם. אנו מציעים תפריטי קייטרינג מותאמים אישית לחתונות, ימי הולדת ואירועי חברה.')
    catering_subtitle_en = db.Column(db.Text, default='Bring authentic Asian flavors to your next celebration. We offer custom catering menus for weddings, birthdays, and corporate events.')
    catering_image = db.Column(db.String(255))  # Catering section background/feature image
    
    # Catering Page Settings
    enable_catering_page = db.Column(db.Boolean, default=True)
    catering_page_hero_title_he = db.Column(db.String(200), default='קייטרינג ואירועים מיוחדים')
    catering_page_hero_title_en = db.Column(db.String(200), default='Catering & Special Events')
    catering_page_hero_subtitle_he = db.Column(db.Text, default='הפכו את האירוע שלכם לבלתי נשכח עם המטבח האסייתי האותנטי שלנו')
    catering_page_hero_subtitle_en = db.Column(db.Text, default='Make your event unforgettable with our authentic Asian cuisine')
    catering_page_gallery_title_he = db.Column(db.String(200), default='גלריה')
    catering_page_gallery_title_en = db.Column(db.String(200), default='Gallery')
    catering_page_gallery_subtitle_he = db.Column(db.String(500), default='צפו בתמונות מאירועים קודמים')
    catering_page_gallery_subtitle_en = db.Column(db.String(500), default='View photos from previous events')
    catering_page_cta_title_he = db.Column(db.String(200), default='מוכנים להפוך את האירוע שלכם למיוחד?')
    catering_page_cta_title_en = db.Column(db.String(200), default='Ready to Make Your Event Special?')
    catering_page_cta_subtitle_he = db.Column(db.String(500), default='צרו קשר עכשיו לייעוץ חינם ותפריט מותאם אישית')
    catering_page_cta_subtitle_en = db.Column(db.String(500), default='Contact us now for a free consultation and custom menu')
    
    # Careers Section (Homepage Preview)
    enable_careers_section = db.Column(db.Boolean, default=True)
    careers_title_he = db.Column(db.String(200), default='הצטרפו לצוות שלנו')
    careers_title_en = db.Column(db.String(200), default='Join Our Team')
    careers_subtitle_he = db.Column(db.Text, default='מחפשים אנשי מקצוע מוכשרים להצטרף למשפחת סומו. גלו הזדמנויות קריירה מרגשות במטבח האסייתי המוביל.')
    careers_subtitle_en = db.Column(db.Text, default='Looking for talented professionals to join the SUMO family. Discover exciting career opportunities at the leading Asian kitchen.')
    careers_image = db.Column(db.String(255))  # Careers section background/feature image
    
    # Careers Page Settings
    careers_page_hero_title_he = db.Column(db.String(200), default='הצטרפו לצוות שלנו')
    careers_page_hero_title_en = db.Column(db.String(200), default='Join Our Team')
    careers_page_hero_subtitle_he = db.Column(db.Text, default='בואו להיות חלק ממשפחת סומו - מקום שבו כישרון פוגש תשוקה')
    careers_page_hero_subtitle_en = db.Column(db.Text, default='Be part of the SUMO family - where talent meets passion')
    careers_page_positions_title_he = db.Column(db.String(200), default='משרות פתוחות')
    careers_page_positions_title_en = db.Column(db.String(200), default='Open Positions')
    careers_page_positions_subtitle_he = db.Column(db.String(500), default='מצאו את המשרה המושלמת עבורכם')
    careers_page_positions_subtitle_en = db.Column(db.String(500), default='Find the perfect position for you')
    careers_page_cta_title_he = db.Column(db.String(200), default='מעוניינים להצטרף?')
    careers_page_cta_title_en = db.Column(db.String(200), default='Interested in Joining?')
    careers_page_cta_subtitle_he = db.Column(db.String(500), default='שלחו לנו את פרטיכם ונחזור אליכם בהקדם')
    careers_page_cta_subtitle_en = db.Column(db.String(500), default='Send us your details and we will get back to you soon')
    
    # Advanced Features
    google_analytics_id = db.Column(db.String(50))  # GA tracking ID
    google_tag_manager_id = db.Column(db.String(50))  # GTM container ID (GTM-XXXXXXX)
    facebook_pixel_id = db.Column(db.String(50))  # FB Pixel ID
    maintenance_mode = db.Column(db.Boolean, default=False)  # Show maintenance page
    announcement_text_he = db.Column(db.String(500))  # Top banner announcement
    announcement_text_en = db.Column(db.String(500))
    announcement_enabled = db.Column(db.Boolean, default=False)
    announcement_bg_color = db.Column(db.String(20), default='#ffc107')
    
    # Online Ordering Settings
    enable_order_onboarding = db.Column(db.Boolean, default=True)
    ordering_paused = db.Column(db.Boolean, default=False)
    ordering_paused_message = db.Column(db.String(500))
    ordering_closed_message = db.Column(db.String(500))
    ordering_outside_hours_message = db.Column(db.String(500))
    enforce_ordering_hours = db.Column(db.Boolean, default=False)
    contact_phone = db.Column(db.String(20))
    admin_phone = db.Column(db.String(20))
    send_order_tracking_link = db.Column(db.Boolean, default=True)
    
    # HYP Payment Gateway
    hyp_enabled = db.Column(db.Boolean, default=False)
    hyp_sandbox_mode = db.Column(db.Boolean, default=True)
    hyp_terminal = db.Column(db.String(50))
    hyp_api_key = db.Column(db.String(200))
    hyp_passp = db.Column(db.String(200))
    
    # Telegram Notifications
    telegram_bot_token = db.Column(db.String(200))
    telegram_chat_id = db.Column(db.String(100))
    telegram_channel_id = db.Column(db.String(100))
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Custom Sections (Dynamic Sections for Homepage)
class CustomSection(db.Model):
    __tablename__ = 'custom_sections'
    id = db.Column(db.Integer, primary_key=True)
    title_he = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200), nullable=False)
    content_he = db.Column(db.Text)
    content_en = db.Column(db.Text)
    section_type = db.Column(db.String(50), default='text')  # text, html, embed
    embed_code = db.Column(db.Text)  # For iframe or external embeds
    background_color = db.Column(db.String(20), default='#ffffff')
    text_color = db.Column(db.String(20), default='#333333')
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    show_on_homepage = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Reservation Settings
class ReservationSettings(db.Model):
    __tablename__ = 'reservation_settings'
    id = db.Column(db.Integer, primary_key=True)
    enable_reservations = db.Column(db.Boolean, default=True)
    reservation_system_url = db.Column(db.String(500))  # External reservation system URL
    reservation_button_text_he = db.Column(db.String(100), default='הזמינו שולחן')
    reservation_button_text_en = db.Column(db.String(100), default='Reserve a Table')
    section_title_he = db.Column(db.String(200), default='הזמנת שולחן')
    section_title_en = db.Column(db.String(200), default='Table Reservation')
    section_description_he = db.Column(db.Text, default='הזמינו שולחן מראש ותיהנו מחוויה מושלמת')
    section_description_en = db.Column(db.Text, default='Reserve a table in advance and enjoy the perfect experience')
    show_on_homepage = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=5)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Media Files
class MediaFile(db.Model):
    __tablename__ = 'media_files'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50))  # image, video
    section = db.Column(db.String(100))  # hero, gallery, about, etc.
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    caption_he = db.Column(db.String(255))
    caption_en = db.Column(db.String(255))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

# Task Groups
class TaskGroup(db.Model):
    __tablename__ = 'task_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    shift_type = db.Column(db.String(50), nullable=False)  # morning, evening, closing, night
    category = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(20), default='#007bff')  # Group color for visual distinction
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<TaskGroup {self.name}>'

# Checklist Tasks
class ChecklistTask(db.Model):
    __tablename__ = 'checklist_tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    shift_type = db.Column(db.String(50))  # morning, evening, closing, night
    category = db.Column(db.String(50))  # kitchen, cleaning, service, inventory, safety
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    frequency = db.Column(db.String(20), default='daily')  # daily, weekly, monthly
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    
    # Group relationship
    group_id = db.Column(db.Integer, db.ForeignKey('task_groups.id'), nullable=True)
    group = db.relationship('TaskGroup', backref='tasks')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Generated Checklists
class GeneratedChecklist(db.Model):
    __tablename__ = 'generated_checklists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    shift_type = db.Column(db.String(50))
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    manager_name = db.Column(db.String(100))
    tasks_json = db.Column(db.Text)  # JSON string of tasks included
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    branch = db.relationship('Branch', backref='checklists')

class TaskTemplate(db.Model):
    __tablename__ = 'task_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text)
    shift_type = db.Column(db.String(50), nullable=False)  # morning, evening, closing, night
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)  # Required branch
    is_default = db.Column(db.Boolean, default=False)
    
    # JSON field to store task configuration
    tasks_config = db.Column(db.JSON)  # Will store array of task objects
    # JSON field to store assigned group IDs
    assigned_groups = db.Column(db.JSON)  # Will store array of group IDs
    
    # Relationship
    branch = db.relationship('Branch', backref='templates')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<TaskTemplate {self.name}>'

# Branches
class Branch(db.Model):
    __tablename__ = 'branches'
    id = db.Column(db.Integer, primary_key=True)
    name_he = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    address_he = db.Column(db.String(255))
    address_en = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    waze_link = db.Column(db.String(500))
    google_maps_link = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    enable_delivery = db.Column(db.Boolean, default=True)
    enable_pickup = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    payment_provider = db.Column(db.String(20), default='hyp')
    hyp_terminal = db.Column(db.String(100))
    hyp_api_key = db.Column(db.String(255))
    hyp_passp = db.Column(db.String(255))
    max_api_url = db.Column(db.String(500))
    max_api_key = db.Column(db.String(255))
    max_merchant_id = db.Column(db.String(100))
    working_hours = db.relationship('WorkingHours', backref='branch', lazy=True, cascade='all, delete-orphan')
    branch_menu_items = db.relationship('BranchMenuItem', backref='branch', lazy=True, cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def has_payment_config(self):
        if self.payment_provider == 'max':
            return bool(self.max_api_key and self.max_merchant_id)
        return bool(self.hyp_terminal and self.hyp_api_key and self.hyp_passp)


class BranchMenuItem(db.Model):
    __tablename__ = 'branch_menu_items'
    __table_args__ = (
        db.UniqueConstraint('branch_id', 'menu_item_id', name='uq_branch_menu_item'),
    )
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='CASCADE'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id', ondelete='CASCADE'), nullable=False)
    custom_price = db.Column(db.Float, nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    print_station = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    menu_item = db.relationship('MenuItem', backref=db.backref('branch_overrides', lazy=True))


# Working Hours
class WorkingHours(db.Model):
    __tablename__ = 'working_hours'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    day_of_week = db.Column(db.Integer)  # 0=Sunday, 6=Saturday
    day_name_he = db.Column(db.String(20))
    day_name_en = db.Column(db.String(20))
    open_time = db.Column(db.String(5))  # HH:MM format
    close_time = db.Column(db.String(5))  # HH:MM format
    is_closed = db.Column(db.Boolean, default=False)

# Menu Categories
class MenuCategory(db.Model):
    __tablename__ = 'menu_categories'
    id = db.Column(db.Integer, primary_key=True)
    name_he = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    description_he = db.Column(db.Text)
    description_en = db.Column(db.Text)
    footer_text_he = db.Column(db.Text)  # Text displayed at bottom of category
    footer_text_en = db.Column(db.Text)  # Text displayed at bottom of category
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)  # Overall active status
    show_in_menu = db.Column(db.Boolean, default=True)  # Show in menu page
    show_in_order = db.Column(db.Boolean, default=True)  # Show in order page
    featured = db.Column(db.Boolean, default=False)  # Featured category
    icon = db.Column(db.String(50))  # FontAwesome icon name
    color = db.Column(db.String(7))  # Hex color code
    image_path = db.Column(db.String(255))  # Category background image
    menu_items = db.relationship('MenuItem', backref='category', lazy=True, cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Menu Items - Enhanced
class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('menu_categories.id'), nullable=False)
    name_he = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200), nullable=False)
    description_he = db.Column(db.Text)
    description_en = db.Column(db.Text)
    short_description_he = db.Column(db.String(255))  # For cards/previews
    short_description_en = db.Column(db.String(255))
    ingredients_he = db.Column(db.Text)  # List of ingredients
    ingredients_en = db.Column(db.Text)
    base_price = db.Column(db.Float)  # Base price
    image_path = db.Column(db.String(500))
    image_hero_path = db.Column(db.String(500))  # Hero-size processed image for detail views
    gallery_images = db.Column(db.Text)  # JSON array of additional images
    
    # Dietary & Special Properties
    is_vegetarian = db.Column(db.Boolean, default=False)
    is_vegan = db.Column(db.Boolean, default=False)
    is_gluten_free = db.Column(db.Boolean, default=False)
    is_dairy_free = db.Column(db.Boolean, default=False)
    is_nut_free = db.Column(db.Boolean, default=False)
    is_spicy = db.Column(db.Boolean, default=False)
    is_halal = db.Column(db.Boolean, default=False)
    is_kosher = db.Column(db.Boolean, default=False)
    is_organic = db.Column(db.Boolean, default=False)
    is_signature = db.Column(db.Boolean, default=False)  # Chef's special
    is_new = db.Column(db.Boolean, default=False)
    is_popular = db.Column(db.Boolean, default=False)
    
    # Restaurant Operations
    is_available = db.Column(db.Boolean, default=True)
    allow_takeaway = db.Column(db.Boolean, default=True)  # Can be ordered for takeaway
    allow_delivery = db.Column(db.Boolean, default=True)  # Can be ordered for delivery
    prep_time_minutes = db.Column(db.Integer)  # Preparation time
    print_station = db.Column(db.String(50))  # Print station/route for bon printing (e.g. kitchen, bar, sushi)
    print_name = db.Column(db.String(100))  # Custom short name for bon printing (different language/code)
    calories = db.Column(db.Integer)  # Nutritional info
    spice_level = db.Column(db.Integer, default=0)  # 0-5 scale
    allergens = db.Column(db.Text)  # JSON array of allergens
    
    show_in_order = db.Column(db.Boolean, default=True)
    
    # Display & Ordering
    display_order = db.Column(db.Integer, default=0)
    featured_until = db.Column(db.DateTime)  # For limited time offers
    discount_percentage = db.Column(db.Float, default=0)
    special_offer_text_he = db.Column(db.String(255))
    special_offer_text_en = db.Column(db.String(255))
    
    # Availability Schedule
    available_days = db.Column(db.String(20), default='1111111')  # 7 chars for days of week
    available_from_time = db.Column(db.String(5))  # HH:MM
    available_to_time = db.Column(db.String(5))  # HH:MM
    
    # Custom Labels/Tags
    custom_tags = db.Column(db.Text)  # JSON array of custom tags
    
    # Combo & Image Data (for order system)
    is_combo = db.Column(db.Boolean, default=False)
    combo_items_json = db.Column(db.Text)
    image_data = db.Column(db.LargeBinary)
    
    # Relationships
    price_options = db.relationship('MenuItemPrice', backref='menu_item', lazy=True, cascade='all, delete-orphan')
    option_groups = db.relationship('MenuItemOptionGroup', backref='menu_item', lazy=True, cascade='all, delete-orphan', order_by='MenuItemOptionGroup.display_order')
    variations = db.relationship('MenuItemVariation', backref='menu_item', lazy=True, cascade='all, delete-orphan')
    dietary_properties = db.relationship('DietaryProperty', secondary=menu_item_dietary_properties, backref='menu_items')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Menu Item Pricing Options (Different sizes/portions)
class MenuItemPrice(db.Model):
    __tablename__ = 'menu_item_prices'
    id = db.Column(db.Integer, primary_key=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    size_name_he = db.Column(db.String(50), nullable=False)  # קטן, בינוני, גדול
    size_name_en = db.Column(db.String(50), nullable=False)  # Small, Medium, Large
    price = db.Column(db.Float, nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)

# Menu Item Ingredients - Links menu items to stock items for cost calculation
class MenuItemIngredient(db.Model):
    __tablename__ = 'menu_item_ingredients'
    id = db.Column(db.Integer, primary_key=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    stock_item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)  # Quantity of ingredient used
    unit = db.Column(db.String(20))  # Override unit if needed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    menu_item = db.relationship('MenuItem', backref='ingredients')
    stock_item = db.relationship('StockItem', backref='menu_usage')

# Menu Item Variations (Spice levels, cooking styles, etc.)
class MenuItemVariation(db.Model):
    __tablename__ = 'menu_item_variations'
    id = db.Column(db.Integer, primary_key=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    variation_type = db.Column(db.String(50))  # spice_level, cooking_style, etc.
    name_he = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    price_modifier = db.Column(db.Float, default=0)  # Additional cost
    is_default = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)

# Customizable Dietary Properties
class DietaryProperty(db.Model):
    __tablename__ = 'dietary_properties'
    id = db.Column(db.Integer, primary_key=True)
    name_he = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(50))  # FontAwesome icon
    color = db.Column(db.String(7))  # Hex color
    description_he = db.Column(db.String(255))
    description_en = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Menu Display Settings
class MenuSettings(db.Model):
    __tablename__ = 'menu_settings'
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text)
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Gallery Photos
class GalleryPhoto(db.Model):
    __tablename__ = 'gallery_photos'
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(500), nullable=False)
    caption_he = db.Column(db.String(255))
    caption_en = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

# Contact Messages
class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ContactMessage {self.name}>'

# Catering Contact Messages
class CateringContact(db.Model):
    __tablename__ = 'catering_contacts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    event_date = db.Column(db.String(50), nullable=True)  # Preferred event date
    event_type = db.Column(db.String(100), nullable=True)  # Wedding, Corporate, Birthday, etc.
    guest_count = db.Column(db.Integer, nullable=True)  # Estimated number of guests
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CateringContact {self.name} - {self.event_type}>'

# Careers Models
class CareerPosition(db.Model):
    __tablename__ = 'career_positions'
    id = db.Column(db.Integer, primary_key=True)
    
    # Position Information
    title_he = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200), nullable=False)
    description_he = db.Column(db.Text)
    description_en = db.Column(db.Text)
    requirements_he = db.Column(db.Text)  # Job requirements
    requirements_en = db.Column(db.Text)
    
    # Position Details
    location_he = db.Column(db.String(100))  # e.g., "כרמיאל"
    location_en = db.Column(db.String(100))  # e.g., "Karmiel"
    employment_type_he = db.Column(db.String(50))  # Full-time, Part-time, etc.
    employment_type_en = db.Column(db.String(50))
    
    # Display Settings
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CareerPosition {self.title_en}>'

class CareerContact(db.Model):
    __tablename__ = 'career_contacts'
    id = db.Column(db.Integer, primary_key=True)
    
    # Contact Information
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    
    # Position Applied For
    position_id = db.Column(db.Integer, db.ForeignKey('career_positions.id'), nullable=True)
    position = db.relationship('CareerPosition', backref='applications')
    position_other = db.Column(db.String(200))  # For "Other" position
    
    # Application Details
    message = db.Column(db.Text, nullable=False)  # Cover letter / message
    resume_path = db.Column(db.String(500))  # Path to uploaded resume (optional)
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CareerContact {self.name}>'

# Newsletter Subscribers
class NewsletterSubscriber(db.Model):
    __tablename__ = 'newsletter_subscribers'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True, default=None)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    unsubscribed_at = db.Column(db.DateTime, nullable=True, default=None)
    source = db.Column(db.String(50), default='website', nullable=False)  # website, order_page, footer, etc.
    
    def __repr__(self):
        return f'<NewsletterSubscriber {self.email}>'

# Reservations
class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    customer_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    guests = db.Column(db.Integer, nullable=False)
    special_requests = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Reservation {self.customer_name} - {self.date}>'

# ===== PDF MENU PARSING MODELS =====

# PDF Menu Uploads - Track uploaded PDF menus and their processing status
class PDFMenuUpload(db.Model):
    __tablename__ = 'pdf_menu_uploads'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    
    # Processing status
    status = db.Column(db.String(50), default='uploaded')  # uploaded, processing, completed, failed
    processing_progress = db.Column(db.Integer, default=0)  # 0-100 percentage
    error_message = db.Column(db.Text)
    
    # Extraction results
    extracted_items_count = db.Column(db.Integer, default=0)
    items_added_to_menu = db.Column(db.Integer, default=0)
    raw_extraction_data = db.Column(db.JSON)  # Store raw OpenAI response
    
    # User tracking
    uploaded_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    processed_at = db.Column(db.DateTime)
    
    # Relationships
    branch = db.relationship('Branch', backref='pdf_menu_uploads')
    uploader = db.relationship('AdminUser', backref='pdf_uploads')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PDFMenuUpload {self.filename}>'

# ===== STOCK MANAGEMENT MICROSERVICE MODELS =====

# Stock Item Categories
class StockCategory(db.Model):
    __tablename__ = 'stock_categories'
    id = db.Column(db.Integer, primary_key=True)
    name_he = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    description_he = db.Column(db.Text)
    description_en = db.Column(db.Text)
    icon = db.Column(db.String(50))  # FontAwesome icon
    color = db.Column(db.String(7))  # Hex color
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<StockCategory {self.name_he}>'

# Suppliers
class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    delivery_days = db.Column(db.String(20), default='1111111')  # 7 chars for days of week
    delivery_time = db.Column(db.String(100))  # e.g., "Morning 9-11 AM"
    minimum_order = db.Column(db.Float, default=0)  # Minimum order amount
    payment_terms = db.Column(db.String(100))
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Supplier {self.name}>'

# Stock Items (ingredients, finished products, supplies)
class StockItem(db.Model):
    __tablename__ = 'stock_items'
    id = db.Column(db.Integer, primary_key=True)
    name_he = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200), nullable=False)
    description_he = db.Column(db.Text)
    description_en = db.Column(db.Text)
    sku = db.Column(db.String(50), unique=True)  # Stock Keeping Unit
    barcode = db.Column(db.String(100))
    
    # Categorization
    category_id = db.Column(db.Integer, db.ForeignKey('stock_categories.id'))
    item_type = db.Column(db.String(50), nullable=False)  # ingredient, finished_product, supply
    
    # Supplier information
    primary_supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    supplier_item_code = db.Column(db.String(100))  # Supplier's code for this item
    
    # Units and measurements
    unit_he = db.Column(db.String(50))  # יחידה, ק"ג, ליטר, חבילה
    unit_en = db.Column(db.String(50))  # piece, kg, liter, package
    unit_size = db.Column(db.Float, default=1)  # Size per unit (e.g., 500 for 500g package)
    
    # Cost and pricing
    cost_per_unit = db.Column(db.Float)  # Cost price
    selling_price = db.Column(db.Float)  # For finished products
    
    # Stock management
    minimum_stock = db.Column(db.Float, default=0)  # Alert threshold
    maximum_stock = db.Column(db.Float)  # Maximum storage capacity
    reorder_quantity = db.Column(db.Float)  # Suggested reorder amount
    
    # Expiration tracking
    has_expiration = db.Column(db.Boolean, default=False)
    shelf_life_days = db.Column(db.Integer)  # Days until expiration
    
    # Storage requirements
    storage_location = db.Column(db.String(100))  # Freezer, fridge, pantry, etc.
    storage_temperature = db.Column(db.String(50))
    
    # Relationships
    category = db.relationship('StockCategory', backref='items')
    primary_supplier = db.relationship('Supplier', backref='items')
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<StockItem {self.name_he}>'

# Stock Levels by Branch
class StockLevel(db.Model):
    __tablename__ = 'stock_levels'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    
    # Current stock
    current_quantity = db.Column(db.Float, default=0)
    reserved_quantity = db.Column(db.Float, default=0)  # Reserved for orders
    available_quantity = db.Column(db.Float, default=0)  # current - reserved
    
    # Tracking
    last_counted = db.Column(db.DateTime)  # Last physical count
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    item = db.relationship('StockItem', backref='stock_levels')
    branch = db.relationship('Branch', backref='stock_levels')
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('item_id', 'branch_id', name='unique_item_branch'),)
    
    def __repr__(self):
        return f'<StockLevel {self.item.name_he} @ {self.branch.name_he}: {self.current_quantity}>'

# Stock Transactions (all movements in/out)
class StockTransaction(db.Model):
    __tablename__ = 'stock_transactions'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    
    # Transaction details
    transaction_type = db.Column(db.String(50), nullable=False)  # delivery, usage, waste, adjustment, return
    quantity = db.Column(db.Float, nullable=False)  # Positive for in, negative for out
    unit_cost = db.Column(db.Float)
    total_cost = db.Column(db.Float)
    
    # Reference information
    reference_number = db.Column(db.String(100))  # Invoice number, order number, etc.
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    
    # Expiration tracking
    expiration_date = db.Column(db.Date)
    batch_number = db.Column(db.String(100))
    
    # User and notes
    user_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    notes = db.Column(db.Text)
    
    # Timestamp
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    item = db.relationship('StockItem', backref='transactions')
    branch = db.relationship('Branch', backref='stock_transactions')
    supplier = db.relationship('Supplier', backref='transactions')
    user = db.relationship('AdminUser', backref='stock_transactions')
    
    def __repr__(self):
        return f'<StockTransaction {self.transaction_type}: {self.quantity} {self.item.name_he}>'

# Stock Alerts
class StockAlert(db.Model):
    __tablename__ = 'stock_alerts'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    
    # Alert details
    alert_type = db.Column(db.String(50), nullable=False)  # low_stock, expiring_soon, out_of_stock
    message_he = db.Column(db.Text)
    message_en = db.Column(db.Text)
    severity = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    is_resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    item = db.relationship('StockItem', backref='alerts')
    branch = db.relationship('Branch', backref='stock_alerts')
    resolved_by_user = db.relationship('AdminUser', backref='resolved_stock_alerts')
    
    def __repr__(self):
        return f'<StockAlert {self.alert_type}: {self.item.name_he}>'

# Shopping Lists
class ShoppingList(db.Model):
    __tablename__ = 'shopping_lists'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    
    # List details
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='draft')  # draft, sent, ordered, received
    
    # Generation details
    auto_generated = db.Column(db.Boolean, default=False)
    generation_criteria = db.Column(db.JSON)  # Criteria used for auto-generation
    
    # Order details
    order_date = db.Column(db.Date)
    expected_delivery = db.Column(db.Date)
    total_estimated_cost = db.Column(db.Float, default=0)
    
    # User tracking
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    sent_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime)
    
    # Relationships
    branch = db.relationship('Branch', backref='shopping_lists')
    supplier = db.relationship('Supplier', backref='shopping_lists')
    created_by_user = db.relationship('AdminUser', foreign_keys=[created_by], backref='created_shopping_lists')
    sent_by_user = db.relationship('AdminUser', foreign_keys=[sent_by], backref='sent_shopping_lists')
    
    def __repr__(self):
        return f'<ShoppingList {self.name}>'

# Shopping List Items
class ShoppingListItem(db.Model):
    __tablename__ = 'shopping_list_items'
    id = db.Column(db.Integer, primary_key=True)
    shopping_list_id = db.Column(db.Integer, db.ForeignKey('shopping_lists.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'), nullable=False)
    
    # Quantity and pricing
    requested_quantity = db.Column(db.Float, nullable=False)
    estimated_unit_cost = db.Column(db.Float)
    estimated_total_cost = db.Column(db.Float)
    
    # Actual received (after delivery)
    received_quantity = db.Column(db.Float, default=0)
    actual_unit_cost = db.Column(db.Float)
    actual_total_cost = db.Column(db.Float)
    
    # Status
    status = db.Column(db.String(50), default='pending')  # pending, ordered, received, cancelled
    notes = db.Column(db.Text)
    
    # Relationships
    shopping_list = db.relationship('ShoppingList', backref='items')
    item = db.relationship('StockItem', backref='shopping_list_items')
    
    def __repr__(self):
        return f'<ShoppingListItem {self.item.name_he}: {self.requested_quantity}>'

# Stock Settings (toggleable features)
class StockSettings(db.Model):
    __tablename__ = 'stock_settings'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))  # NULL for global settings
    
    # Feature toggles
    enable_expiration_tracking = db.Column(db.Boolean, default=True)
    enable_automatic_alerts = db.Column(db.Boolean, default=True)
    enable_auto_shopping_lists = db.Column(db.Boolean, default=True)
    enable_cost_tracking = db.Column(db.Boolean, default=True)
    enable_batch_tracking = db.Column(db.Boolean, default=False)
    
    # Alert settings
    low_stock_alert_days = db.Column(db.Integer, default=3)  # Days before running out
    expiration_alert_days = db.Column(db.Integer, default=7)  # Days before expiration
    
    # Shopping list settings
    auto_generate_frequency = db.Column(db.String(20), default='weekly')  # daily, weekly, monthly
    auto_generate_day = db.Column(db.String(20), default='sunday')
    
    # Relationships
    branch = db.relationship('Branch', backref='stock_settings')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<StockSettings for {self.branch.name_he if self.branch else "Global"}>'

# ===== ENHANCED SUPPLIER & COST MANAGEMENT =====

# Receipt Storage and Processing
class Receipt(db.Model):
    __tablename__ = 'receipts'
    id = db.Column(db.Integer, primary_key=True)
    
    # File storage
    image_path = db.Column(db.String(500), nullable=False)  # Path to uploaded image
    original_filename = db.Column(db.String(255))
    file_size = db.Column(db.Integer)  # File size in bytes
    
    # Receipt metadata
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    receipt_date = db.Column(db.Date)
    receipt_number = db.Column(db.String(100))
    
    # Financial data
    total_amount = db.Column(db.Float)
    tax_amount = db.Column(db.Float)
    currency = db.Column(db.String(3), default='ILS')
    
    # OCR processing status
    ocr_status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    ocr_data = db.Column(db.JSON)  # Raw OCR extracted data
    ocr_confidence = db.Column(db.Float)  # OCR confidence score
    
    # Manual verification
    is_verified = db.Column(db.Boolean, default=False)
    verified_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    verified_at = db.Column(db.DateTime)
    
    # Processing notes
    notes = db.Column(db.Text)
    processing_errors = db.Column(db.Text)
    
    # User tracking
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    processed_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))  # Who processed the receipt
    
    # Relationships
    supplier = db.relationship('Supplier', backref='receipts')
    branch = db.relationship('Branch', backref='receipts')
    creator = db.relationship('AdminUser', foreign_keys=[created_by], backref='created_receipts')
    processor = db.relationship('AdminUser', foreign_keys=[processed_by], backref='processed_receipts')
    verifier = db.relationship('AdminUser', foreign_keys=[verified_by], backref='verified_receipts')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Receipt {self.receipt_number} - {self.supplier.name if self.supplier else "Unknown"}>'

# Receipt Import (for approval workflow)
class ReceiptImport(db.Model):
    __tablename__ = 'receipt_imports'
    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    
    # Import details
    status = db.Column(db.String(20), default='pending')  # pending, extracted, needs_review, approved, rejected
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    suggested_supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))  # AI suggestion
    supplier_confidence = db.Column(db.Float)  # AI confidence score
    candidate_supplier_ids = db.Column(db.JSON)  # All AI-suggested supplier matches
    
    # Extracted metadata
    receipt_date = db.Column(db.Date)
    total_amount = db.Column(db.Float)
    
    # Raw AI output
    ai_raw_response = db.Column(db.JSON)  # Complete AI response for audit
    ai_errors = db.Column(db.Text)  # Any errors during AI processing
    
    # Approval workflow
    approved_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    approved_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    
    # Post-approval traceability
    shopping_list_id = db.Column(db.Integer, db.ForeignKey('shopping_lists.id'))  # Created PO
    stock_transaction_batch = db.Column(db.String(100))  # Batch ID for related transactions
    
    # Processing
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    receipt = db.relationship('Receipt', backref='imports')
    branch = db.relationship('Branch', backref='receipt_imports')
    supplier = db.relationship('Supplier', foreign_keys=[supplier_id], backref='receipt_imports')
    suggested_supplier = db.relationship('Supplier', foreign_keys=[suggested_supplier_id])
    shopping_list = db.relationship('ShoppingList', backref='receipt_imports')
    creator = db.relationship('AdminUser', foreign_keys=[created_by], backref='created_receipt_imports')
    approver = db.relationship('AdminUser', foreign_keys=[approved_by], backref='approved_receipt_imports')
    
    def __repr__(self):
        return f'<ReceiptImport {self.id} - {self.status}>'

# Receipt Import Line Items
class ReceiptImportItem(db.Model):
    __tablename__ = 'receipt_import_items'
    id = db.Column(db.Integer, primary_key=True)
    receipt_import_id = db.Column(db.Integer, db.ForeignKey('receipt_imports.id'), nullable=False)
    
    # Extracted product info (raw from AI)
    extracted_text = db.Column(db.String(500))  # Original SKU/product text from receipt
    product_name = db.Column(db.String(200), nullable=False)  # Normalized product name
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float)
    total_price = db.Column(db.Float)
    unit_of_measure = db.Column(db.String(20))  # kg, liters, pieces, etc.
    
    # Matching to existing items
    stock_item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'))  # Final matched item
    suggested_stock_item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'))  # AI suggestion
    supplier_item_id = db.Column(db.Integer, db.ForeignKey('supplier_items.id'))  # Supplier's SKU
    match_confidence = db.Column(db.Float)  # AI confidence score (0-1)
    is_new_item = db.Column(db.Boolean, default=False)  # Create new stock item if True
    
    # Status and audit
    is_verified = db.Column(db.Boolean, default=False)  # User reviewed this line
    resolution_status = db.Column(db.String(20), default='pending')  # pending, matched, manual, skipped
    notes = db.Column(db.Text)
    
    # Line ordering
    line_number = db.Column(db.Integer)  # Order in receipt
    
    # Relationships
    receipt_import = db.relationship('ReceiptImport', backref='line_items')
    stock_item = db.relationship('StockItem', foreign_keys=[stock_item_id], backref='receipt_import_items')
    suggested_stock_item = db.relationship('StockItem', foreign_keys=[suggested_stock_item_id])
    supplier_item = db.relationship('SupplierItem', backref='receipt_import_items')
    
    def __repr__(self):
        return f'<ReceiptImportItem {self.product_name}: {self.quantity}>'

# Cost Categories for expense tracking
class CostCategory(db.Model):
    __tablename__ = 'cost_categories'
    id = db.Column(db.Integer, primary_key=True)
    name_he = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    description_he = db.Column(db.Text)
    description_en = db.Column(db.Text)
    icon = db.Column(db.String(50))  # FontAwesome icon
    color = db.Column(db.String(7))  # Hex color
    parent_category_id = db.Column(db.Integer, db.ForeignKey('cost_categories.id'))  # For subcategories
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    
    # Relationships
    parent_category = db.relationship('CostCategory', remote_side=[id], backref='subcategories')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CostCategory {self.name_he}>'

# Cost Entry for expense tracking
class CostEntry(db.Model):
    __tablename__ = 'cost_entries'
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic information
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='ILS')
    entry_date = db.Column(db.Date, nullable=False)
    
    # Categorization
    category_id = db.Column(db.Integer, db.ForeignKey('cost_categories.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    
    # Source tracking
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.id'))  # If from receipt
    file_import_id = db.Column(db.Integer, db.ForeignKey('file_imports.id'))  # If from file import
    entry_type = db.Column(db.String(20), default='manual')  # manual, receipt, import
    
    # Approval workflow
    is_approved = db.Column(db.Boolean, default=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    approved_at = db.Column(db.DateTime)
    
    # Additional metadata
    reference_number = db.Column(db.String(100))  # Invoice/receipt number
    payment_method = db.Column(db.String(50))  # cash, card, transfer, etc.
    tags = db.Column(db.JSON)  # Array of custom tags
    notes = db.Column(db.Text)
    
    # Relationships
    category = db.relationship('CostCategory', backref='cost_entries')
    supplier = db.relationship('Supplier', backref='cost_entries')
    branch = db.relationship('Branch', backref='cost_entries')
    receipt = db.relationship('Receipt', backref='cost_entries')
    approver = db.relationship('AdminUser', backref='approved_costs')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CostEntry {self.description} - ₪{self.amount}>'

# Receipt Items (extracted from OCR or manually entered)
class ReceiptItem(db.Model):
    __tablename__ = 'receipt_items'
    id = db.Column(db.Integer, primary_key=True)
    
    # Receipt connection
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.id'), nullable=False)
    
    # Item information
    item_description = db.Column(db.String(255), nullable=False)  # As written on receipt
    quantity = db.Column(db.Float)
    unit_price = db.Column(db.Float)
    total_price = db.Column(db.Float)
    
    # Stock item mapping
    stock_item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'))  # Mapped stock item
    mapping_confidence = db.Column(db.Float)  # AI confidence in mapping
    
    # Processing status
    is_mapped = db.Column(db.Boolean, default=False)  # Whether mapped to stock item
    is_processed = db.Column(db.Boolean, default=False)  # Whether stock was updated
    
    # Additional data
    item_code = db.Column(db.String(100))  # Supplier item code if available
    unit = db.Column(db.String(50))  # Unit from receipt
    notes = db.Column(db.Text)
    
    # Relationships
    receipt = db.relationship('Receipt', backref='items')
    stock_item = db.relationship('StockItem', backref='receipt_items')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ReceiptItem {self.item_description}>'

# Custom Fields System for Receipts
class CustomFieldDefinition(db.Model):
    """Defines custom fields that can be added to receipts"""
    __tablename__ = 'custom_field_definitions'
    id = db.Column(db.Integer, primary_key=True)
    
    # Field configuration
    field_name = db.Column(db.String(100), nullable=False)  # e.g., "Status", "Priority"
    field_key = db.Column(db.String(100), nullable=False, unique=True)  # e.g., "status", "priority"
    field_type = db.Column(db.String(20), nullable=False)  # text, number, dropdown, date, checkbox
    
    # For dropdown fields
    dropdown_options = db.Column(db.JSON)  # List of options: ["New", "In Progress", "Completed"]
    
    # Validation rules
    number_min = db.Column(db.Float)  # Minimum value for number fields
    number_max = db.Column(db.Float)  # Maximum value for number fields
    text_regex = db.Column(db.String(255))  # Regex pattern for text validation
    text_max_length = db.Column(db.Integer)  # Max length for text fields
    date_min = db.Column(db.Date)  # Minimum date
    date_max = db.Column(db.Date)  # Maximum date
    
    # Display configuration
    is_required = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_system = db.Column(db.Boolean, default=False)  # System-default fields (can't be deleted)
    display_order = db.Column(db.Integer, default=0)
    
    # Metadata
    default_value = db.Column(db.String(255))
    help_text = db.Column(db.String(255))
    
    # Tracking
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_field_active_order', 'field_type', 'is_active', 'display_order'),
    )
    
    def __repr__(self):
        return f'<CustomFieldDefinition {self.field_name} ({self.field_type})>'

class CustomFieldAssignment(db.Model):
    """Defines which custom fields apply to which receipts (scoping)"""
    __tablename__ = 'custom_field_assignments'
    id = db.Column(db.Integer, primary_key=True)
    
    field_definition_id = db.Column(db.Integer, db.ForeignKey('custom_field_definitions.id'), nullable=False)
    
    # Scoping: null = applies to all, or specific branch/supplier
    scope_type = db.Column(db.String(20))  # null, 'branch', 'supplier'
    scope_id = db.Column(db.Integer)  # branch_id or supplier_id
    
    # Relationships
    field_definition = db.relationship('CustomFieldDefinition', backref='assignments')
    
    # Tracking
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('field_definition_id', 'scope_type', 'scope_id', name='unique_field_scope'),)
    
    def __repr__(self):
        return f'<CustomFieldAssignment field={self.field_definition_id} scope={self.scope_type}:{self.scope_id}>'

class ReceiptCustomFieldValue(db.Model):
    """Stores custom field values for each receipt"""
    __tablename__ = 'receipt_custom_field_values'
    id = db.Column(db.Integer, primary_key=True)
    
    # Relationships
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.id'), nullable=False)
    field_definition_id = db.Column(db.Integer, db.ForeignKey('custom_field_definitions.id'), nullable=False)
    
    # Value storage (only one will be populated based on field_type)
    value_text = db.Column(db.Text)
    value_number = db.Column(db.Float)
    value_date = db.Column(db.Date)
    value_boolean = db.Column(db.Boolean)
    
    # Relationships
    receipt = db.relationship('Receipt', backref='custom_field_values')
    field_definition = db.relationship('CustomFieldDefinition', backref='values')
    
    # Tracking
    updated_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        db.UniqueConstraint('receipt_id', 'field_definition_id', name='unique_receipt_field'),
        db.Index('idx_receipt_field', 'receipt_id', 'field_definition_id'),
    )
    
    def __repr__(self):
        return f'<ReceiptCustomFieldValue receipt={self.receipt_id} field={self.field_definition_id}>'

class ReceiptCustomFieldAudit(db.Model):
    """Audit trail for custom field value changes"""
    __tablename__ = 'receipt_custom_field_audit'
    id = db.Column(db.Integer, primary_key=True)
    
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.id'), nullable=False)
    field_definition_id = db.Column(db.Integer, db.ForeignKey('custom_field_definitions.id'), nullable=False)
    
    # Change tracking
    old_value = db.Column(db.JSON)  # Previous value (any type)
    new_value = db.Column(db.JSON)  # New value (any type)
    changed_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    receipt = db.relationship('Receipt', backref='field_audit_log')
    field_definition = db.relationship('CustomFieldDefinition', backref='audit_log')
    user = db.relationship('AdminUser', backref='field_changes')
    
    def __repr__(self):
        return f'<ReceiptCustomFieldAudit receipt={self.receipt_id} field={self.field_definition_id} by={self.changed_by}>'

# File Import tracking
class FileImport(db.Model):
    __tablename__ = 'file_imports'
    id = db.Column(db.Integer, primary_key=True)
    
    # File information
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500))  # Where file is stored
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(20))  # csv, xlsx, xls
    
    # Import metadata
    import_type = db.Column(db.String(50), nullable=False)  # stock_items, cost_entries, suppliers
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    
    # Processing status
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    total_rows = db.Column(db.Integer)
    processed_rows = db.Column(db.Integer, default=0)
    successful_rows = db.Column(db.Integer, default=0)
    failed_rows = db.Column(db.Integer, default=0)
    
    # Field mapping (JSON)
    field_mapping = db.Column(db.JSON)  # Maps file columns to database fields
    
    # Results and errors
    processing_log = db.Column(db.Text)  # Processing details and errors
    error_details = db.Column(db.JSON)  # Detailed error information per row
    
    # User tracking
    uploaded_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    
    # Relationships
    branch = db.relationship('Branch', backref='file_imports')
    uploader = db.relationship('AdminUser', backref='file_imports')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<FileImport {self.original_filename} - {self.status}>'

# Enhanced Supplier-Item relationship (many-to-many)
class SupplierItem(db.Model):
    __tablename__ = 'supplier_items'
    id = db.Column(db.Integer, primary_key=True)
    
    # Core relationship
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    stock_item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'), nullable=False)
    
    # Supplier-specific information
    supplier_item_code = db.Column(db.String(100))  # Supplier's code for this item
    supplier_item_name = db.Column(db.String(255))  # Supplier's name for this item
    
    # Pricing
    cost_per_unit = db.Column(db.Float)
    minimum_order_quantity = db.Column(db.Float)
    unit_package_size = db.Column(db.Float)  # Items per package
    
    # Availability
    is_available = db.Column(db.Boolean, default=True)
    lead_time_days = db.Column(db.Integer)  # Delivery lead time
    
    # Priority (for multiple suppliers)
    priority = db.Column(db.Integer, default=1)  # 1 = primary, 2 = secondary, etc.
    
    # Additional info
    notes = db.Column(db.Text)
    last_order_date = db.Column(db.Date)
    last_order_price = db.Column(db.Float)
    
    # Relationships
    supplier = db.relationship('Supplier', backref='supplier_items')
    stock_item = db.relationship('StockItem', backref='supplier_items')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint to prevent duplicates
    __table_args__ = (db.UniqueConstraint('supplier_id', 'stock_item_id', name='unique_supplier_item'),)
    
    def __repr__(self):
        return f'<SupplierItem {self.supplier.name} - {self.stock_item.name_he}>'

# Comprehensive Audit Log for Stock Management
class AuditLog(db.Model):
    """
    Comprehensive audit trail for all stock management changes.
    Tracks who did what, when, and what changed across all stock entities.
    """
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    
    # Entity information
    entity_type = db.Column(db.String(50), nullable=False)  # stock_item, supplier, stock_category, stock_level, receipt, etc.
    entity_id = db.Column(db.Integer, nullable=False)  # ID of the entity that was changed
    
    # Action tracking
    action = db.Column(db.String(20), nullable=False)  # create, update, delete
    
    # User tracking
    performed_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=True)  # Null for system actions
    performed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Change details (JSONB for PostgreSQL)
    changes = db.Column(db.JSON)  # {field: {old: value, new: value}} or {new_values: {}} for create or {old_values: {}} for delete
    
    # Additional context
    context = db.Column(db.JSON)  # {source: 'web'/'api'/'import', ip_address: '...', user_agent: '...', etc.}
    
    # Relationships
    user = db.relationship('AdminUser', backref='audit_actions')
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_audit_entity', 'entity_type', 'entity_id', 'performed_at'),
        db.Index('idx_audit_user', 'performed_by', 'performed_at'),
        db.Index('idx_audit_date', 'performed_at'),
    )
    
    def __repr__(self):
        return f'<AuditLog {self.action} {self.entity_type}:{self.entity_id} by User {self.performed_by}>'
    
    def get_user_display_name(self):
        """Get the display name of the user who performed the action"""
        if not self.user:
            return 'מערכת' if hasattr(self, '_is_rtl') else 'System'
        return self.user.username
    
    def get_action_display(self, lang='he'):
        """Get localized action name"""
        actions_he = {'create': 'נוצר', 'update': 'עודכן', 'delete': 'נמחק'}
        actions_en = {'create': 'Created', 'update': 'Updated', 'delete': 'Deleted'}
        return actions_he.get(self.action, self.action) if lang == 'he' else actions_en.get(self.action, self.action)

# Print Template for customizable checklist printing
class PrintTemplate(db.Model):
    __tablename__ = 'print_templates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    shift_type = db.Column(db.String(50), nullable=True)  # morning, evening, closing, night, all
    is_default = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # JSON configuration for the template
    config = db.Column(db.JSON, nullable=False, default=lambda: {
        'page': {
            'size': 'A4',
            'margins': {'top': 10, 'right': 10, 'bottom': 10, 'left': 10},
            'rtl': True,
            'rowHeight': 'auto',
            'gridlines': True,
            'headerRepeat': True,
            'fontFamily': 'Arial Hebrew, Arial',
            'fontSize': 12
        },
        'layout': 'table',
        'columns': [
            {
                'id': 'checkbox',
                'key': 'checkbox',
                'label': '',
                'type': 'checkbox',
                'width': {'value': 20, 'unit': 'px'},
                'align': 'center',
                'order': 0,
                'visible': True
            },
            {
                'id': 'taskname',
                'key': 'taskname',
                'label': 'משימה',
                'type': 'text',
                'dataPath': 'name',
                'width': {'value': 'auto', 'unit': 'auto'},
                'align': 'right',
                'order': 1,
                'visible': True
            }
        ]
    })
    
    # Relationships
    branch = db.relationship('Branch', backref='print_templates')
    creator = db.relationship('AdminUser', backref='created_print_templates')

# ===== MENU WIZARD MODELS =====

# Menu Templates for saving menu configurations
class MenuTemplate(db.Model):
    __tablename__ = 'menu_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=True)
    
    # JSON fields for configuration
    categories_config = db.Column(db.JSON)  # Selected categories and their settings
    items_config = db.Column(db.JSON)  # Selected menu items and customizations
    layout_config = db.Column(db.JSON)  # Layout preferences (columns, sections, etc.)
    print_config = db.Column(db.JSON)  # Print-specific settings
    
    # Advanced styling configurations
    style_config = db.Column(db.JSON)  # Typography, colors, spacing, borders
    page_config = db.Column(db.JSON)  # Page breaks, section layout, headers
    icon_config = db.Column(db.JSON)  # Category icons, decorative elements
    
    # Relationships
    branch = db.relationship('Branch', backref='menu_templates')
    creator = db.relationship('AdminUser', backref='created_menu_templates')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<MenuTemplate {self.name}>'

# Generated Menus for tracking created menus
class GeneratedMenu(db.Model):
    __tablename__ = 'generated_menus'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('menu_templates.id'), nullable=True)
    date_created = db.Column(db.Date, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=True)
    
    # Menu content as JSON
    menu_content = db.Column(db.JSON)  # Complete menu structure for printing
    print_settings = db.Column(db.JSON)  # Print configuration used
    
    # Advanced styling (from template or custom)
    style_settings = db.Column(db.JSON)  # Typography, colors, spacing, borders
    page_settings = db.Column(db.JSON)  # Page breaks, section layout, headers
    icon_settings = db.Column(db.JSON)  # Category icons, decorative elements
    
    # Relationships
    branch = db.relationship('Branch', backref='generated_menus')
    template = db.relationship('MenuTemplate', backref='generated_menus')
    creator = db.relationship('AdminUser', backref='created_menus')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    printed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<GeneratedMenu {self.name}>'

# Menu Print Configuration for advanced print settings
class MenuPrintConfiguration(db.Model):
    __tablename__ = 'menu_print_configurations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    is_default = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=True)
    
    # Print configuration as JSON
    config = db.Column(db.JSON, nullable=False, default=lambda: {
        'page': {
            'size': 'A4',
            'orientation': 'portrait',
            'margins': {'top': 15, 'right': 0, 'bottom': 15, 'left': 15},
            'rtl': True,
            'fontFamily': 'Heebo, Arial Hebrew, Arial',
            'fontSize': 12,
            'lineHeight': 1.4
        },
        'header': {
            'show_branch_name': True,
            'show_date': True,
            'show_page_numbers': True,
            'custom_text': '',
            'logo_enabled': False
        },
        'categories': {
            'show_category_titles': True,
            'category_font_size': 16,
            'category_style': 'bold',
            'spacing_after': 10
        },
        'items': {
            'show_descriptions': True,
            'show_prices': True,
            'price_alignment': 'left',
            'description_max_length': 100,
            'item_spacing': 8
        },
        'layout': {
            'columns': 1,
            'column_gap': 20,
            'section_spacing': 25,
            'border_style': 'none'
        }
    })
    
    # Relationships
    branch = db.relationship('Branch', backref='menu_print_configs')
    creator = db.relationship('AdminUser', backref='created_menu_print_configs')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<MenuPrintConfiguration {self.name}>'

# Payment Configuration
class PaymentConfiguration(db.Model):
    __tablename__ = 'payment_configuration'
    id = db.Column(db.Integer, primary_key=True)
    
    # Payment Provider Settings
    provider_name = db.Column(db.String(50), nullable=False)  # stripe, max, bit, etc.
    is_active = db.Column(db.Boolean, default=False)
    display_name_he = db.Column(db.String(100))
    display_name_en = db.Column(db.String(100))
    display_order = db.Column(db.Integer, default=0)
    
    # API Configuration (stored securely)
    api_key = db.Column(db.String(500))
    api_secret = db.Column(db.String(500))
    merchant_id = db.Column(db.String(200))
    additional_config = db.Column(db.JSON)  # Provider-specific settings
    
    # Advanced Settings
    test_mode = db.Column(db.Boolean, default=True)  # Sandbox vs Production
    webhook_url = db.Column(db.String(500))  # Payment notification URL
    webhook_secret = db.Column(db.String(500))  # Webhook signature verification
    
    # Settings
    min_order_amount = db.Column(db.Float, default=0)
    max_order_amount = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PaymentConfiguration {self.provider_name}>'

# Terms of Use / Legal Pages
class TermsOfUse(db.Model):
    __tablename__ = 'terms_of_use'
    id = db.Column(db.Integer, primary_key=True)
    
    # Content in both languages
    content_he = db.Column(db.Text, nullable=False)
    content_en = db.Column(db.Text, nullable=False)
    
    # Metadata
    last_updated_by = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    effective_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<TermsOfUse {self.id}>'

class PrivacyPolicy(db.Model):
    __tablename__ = 'privacy_policy'
    id = db.Column(db.Integer, primary_key=True)
    
    # Content in both languages
    content_he = db.Column(db.Text, nullable=False)
    content_en = db.Column(db.Text, nullable=False)
    
    # Metadata
    last_updated_by = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    effective_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PrivacyPolicy {self.id}>'

# Catering Package Model
class CateringPackage(db.Model):
    __tablename__ = 'catering_packages'
    id = db.Column(db.Integer, primary_key=True)
    
    # Package Information
    name_he = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200), nullable=False)
    description_he = db.Column(db.Text, nullable=False)
    description_en = db.Column(db.Text, nullable=False)
    
    # Pricing & Details
    price_range_he = db.Column(db.String(100))  # e.g., "₪150-200 לאורח"
    price_range_en = db.Column(db.String(100))  # e.g., "₪150-200 per person"
    min_guests = db.Column(db.Integer)  # Minimum number of guests
    max_guests = db.Column(db.Integer)  # Maximum number of guests
    
    # Features (stored as JSON-like text, separated by newlines for simplicity)
    features_he = db.Column(db.Text)  # Each feature on a new line
    features_en = db.Column(db.Text)
    
    # Image
    image_path = db.Column(db.String(255))
    
    # Display Settings
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CateringPackage {self.name_en}>'

# Catering Highlight Model (Service Features)
class CateringHighlight(db.Model):
    __tablename__ = 'catering_highlights'
    id = db.Column(db.Integer, primary_key=True)
    
    # Highlight Information
    title_he = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200), nullable=False)
    description_he = db.Column(db.Text)
    description_en = db.Column(db.Text)
    
    # Icon (Font Awesome class name, e.g., "fa-utensils")
    icon = db.Column(db.String(100), default='fa-star')
    
    # Display Settings
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CateringHighlight {self.title_en}>'

# Catering Gallery Image Model
class CateringGalleryImage(db.Model):
    __tablename__ = 'catering_gallery_images'
    id = db.Column(db.Integer, primary_key=True)
    
    # Image Information
    file_path = db.Column(db.String(500), nullable=False)
    caption_he = db.Column(db.String(255))
    caption_en = db.Column(db.String(255))
    alt_text_he = db.Column(db.String(255))  # For accessibility
    alt_text_en = db.Column(db.String(255))
    
    # Display Settings
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    
    # Timestamps
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CateringGalleryImage {self.id}>'


# ===== POPUP SYSTEM =====

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
    button_action = db.Column(db.String(50), default='link')
    
    # Media
    image_path = db.Column(db.String(500))
    image_display_type = db.Column(db.String(20), default='inline')  # 'inline', 'background', 'background_cover'
    video_url = db.Column(db.String(500))
    
    # Design Settings
    popup_type = db.Column(db.String(50), default='modal')
    popup_size = db.Column(db.String(20), default='medium')
    popup_position = db.Column(db.String(50), default='center')
    
    # Colors
    background_color = db.Column(db.String(20), default='#ffffff')
    title_color = db.Column(db.String(20), default='#1B2951')
    text_color = db.Column(db.String(20), default='#333333')
    text_bg_color = db.Column(db.String(20), default='#000000')  # Text background color
    text_bg_opacity = db.Column(db.Integer, default=0)  # Text background opacity (0-100)
    title_bg_color = db.Column(db.String(20), default='#000000')  # Title background color
    title_bg_opacity = db.Column(db.Integer, default=0)  # Title background opacity (0-100)
    button_bg_color = db.Column(db.String(20), default='#C75450')
    button_bg_opacity = db.Column(db.Integer, default=100)  # Button background opacity (0-100)
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
    element_positions = db.Column(db.JSON, default=dict)  # Store element order/positions
    
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
    enable_form = db.Column(db.Boolean, default=False)  # Enable email collection form
    form_submit_text_he = db.Column(db.String(100), default='שלח')  # Submit button text
    form_submit_text_en = db.Column(db.String(100), default='Submit')
    form_success_message_he = db.Column(db.Text, default='תודה! קיבלנו את הפרטים שלך')  # Success message
    form_success_message_en = db.Column(db.Text, default='Thank you! We received your details')
    
    # Form Fields Configuration
    collect_email = db.Column(db.Boolean, default=True)  # Email field (usually required)
    email_required = db.Column(db.Boolean, default=True)
    email_placeholder_he = db.Column(db.String(100), default='הזן את האימייל שלך')
    email_placeholder_en = db.Column(db.String(100), default='Enter your email')
    
    collect_name = db.Column(db.Boolean, default=False)  # Name field
    name_required = db.Column(db.Boolean, default=False)
    name_placeholder_he = db.Column(db.String(100), default='הזן את שמך')
    name_placeholder_en = db.Column(db.String(100), default='Enter your name')
    
    collect_phone = db.Column(db.Boolean, default=False)  # Phone field
    phone_required = db.Column(db.Boolean, default=False)
    phone_placeholder_he = db.Column(db.String(100), default='הזן מספר טלפון')
    phone_placeholder_en = db.Column(db.String(100), default='Enter your phone number')
    
    # Consent Checkboxes
    show_newsletter_consent = db.Column(db.Boolean, default=True)  # Newsletter subscription checkbox
    newsletter_consent_text_he = db.Column(db.String(255), default='אני מסכים/ה לקבל עדכונים ומבצעים במייל')
    newsletter_consent_text_en = db.Column(db.String(255), default='I agree to receive updates and promotions by email')
    newsletter_default_checked = db.Column(db.Boolean, default=True)
    
    show_terms_consent = db.Column(db.Boolean, default=False)  # Terms & conditions checkbox
    terms_consent_text_he = db.Column(db.String(255), default='אני מסכים/ה לתנאי השימוש')
    terms_consent_text_en = db.Column(db.String(255), default='I agree to the terms of service')
    terms_consent_required = db.Column(db.Boolean, default=False)
    terms_link = db.Column(db.String(500))  # Link to terms page
    
    show_marketing_consent = db.Column(db.Boolean, default=False)  # Marketing consent checkbox
    marketing_consent_text_he = db.Column(db.String(255), default='אני מסכים/ה לקבל הודעות שיווקיות')
    marketing_consent_text_en = db.Column(db.String(255), default='I agree to receive marketing messages')
    marketing_default_checked = db.Column(db.Boolean, default=False)
    
    # Coupon Integration
    associated_coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'), nullable=True)
    send_coupon_on_submit = db.Column(db.Boolean, default=False)  # Send coupon after form submission
    coupon_email_subject_he = db.Column(db.String(255), default='הקופון שלך מגיע!')
    coupon_email_subject_en = db.Column(db.String(255), default='Your coupon has arrived!')
    
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
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    
    # Relationships
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


# ===== COUPON SYSTEM =====

class Coupon(db.Model):
    """Coupon/discount codes for promotions"""
    __tablename__ = 'coupons'
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)  # The actual coupon code
    description_he = db.Column(db.Text)
    description_en = db.Column(db.Text)
    
    # Discount Settings
    discount_type = db.Column(db.String(20), default='percentage')  # 'percentage', 'fixed_amount', 'free_item'
    discount_value = db.Column(db.Float, default=0)  # Percentage (0-100) or fixed amount
    minimum_order_amount = db.Column(db.Float, default=0)  # Minimum order to apply coupon
    maximum_discount_amount = db.Column(db.Float)  # Cap for percentage discounts
    
    # Usage Limits
    max_total_uses = db.Column(db.Integer)  # Total uses allowed (null = unlimited)
    max_uses_per_email = db.Column(db.Integer, default=1)  # Uses per email address
    current_uses = db.Column(db.Integer, default=0)  # Track current usage count
    
    # Validity Period
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    
    # QR Code
    qr_code_path = db.Column(db.String(500))  # Path to generated QR code image
    qr_code_data = db.Column(db.Text)  # QR code data/URL
    
    # Popup Association (optional)
    popup_id = db.Column(db.Integer, db.ForeignKey('popups.id'), nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    
    # Relationships
    popup = db.relationship('Popup', foreign_keys=[popup_id], backref='coupons')
    creator = db.relationship('AdminUser', backref='created_coupons')
    usages = db.relationship('CouponUsage', backref='coupon', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Coupon {self.code}>'
    
    def is_valid(self):
        """Check if coupon is currently valid"""
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
        """Check if email can still use this coupon"""
        if not self.is_valid():
            return False
        # If max_uses_per_email is None/NULL, unlimited uses per email are allowed
        if self.max_uses_per_email is None:
            return True
        normalized_email = email.lower().strip()
        usage_count = CouponUsage.query.filter_by(
            coupon_id=self.id,
            email=normalized_email
        ).count()
        return usage_count < self.max_uses_per_email
    
    def get_usage_count(self):
        """Get actual usage count from database (derived, not cached)"""
        return self.usages.count()
    
    def record_usage(self, email, lead_id=None):
        """Record a coupon usage"""
        normalized_email = email.lower().strip()
        usage = CouponUsage(
            coupon_id=self.id,
            email=normalized_email,
            lead_id=lead_id
        )
        # Use derived count for validation, but still track current_uses for quick display
        self.current_uses = self.get_usage_count() + 1
        db.session.add(usage)
        return usage
    
    def generate_qr_code(self, base_url=None):
        """Generate QR code for this coupon"""
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
        """Get QR code as base64 string for embedding in emails"""
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
    """Track individual coupon uses"""
    __tablename__ = 'coupon_usages'
    id = db.Column(db.Integer, primary_key=True)
    
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'), nullable=False, index=True)
    email = db.Column(db.String(255), nullable=False, index=True)  # Indexed for email lookups
    lead_id = db.Column(db.Integer, db.ForeignKey('popup_leads.id'), nullable=True)
    
    # Usage Details
    used_at = db.Column(db.DateTime, default=datetime.utcnow)
    order_amount = db.Column(db.Float)  # Order amount when coupon was used (optional)
    discount_applied = db.Column(db.Float)  # Actual discount given
    
    # Composite index for coupon+email lookups (most common query)
    __table_args__ = (
        db.Index('idx_coupon_email', 'coupon_id', 'email'),
    )
    
    def __repr__(self):
        return f'<CouponUsage {self.coupon_id} - {self.email}>'


# ===== POPUP LEADS SYSTEM =====

class PopupLead(db.Model):
    """Leads collected through popup forms"""
    __tablename__ = 'popup_leads'
    id = db.Column(db.Integer, primary_key=True)
    
    # Lead Information
    email = db.Column(db.String(255), nullable=False, index=True)  # Indexed for lookups
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    
    # Source
    popup_id = db.Column(db.Integer, db.ForeignKey('popups.id'), nullable=True)
    source_page = db.Column(db.String(500))  # URL where popup was shown
    
    # Coupon Association
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'), nullable=True)
    coupon_code_sent = db.Column(db.String(50))  # The actual code that was sent
    coupon_sent_at = db.Column(db.DateTime)  # When coupon email was sent
    
    # Status
    email_verified = db.Column(db.Boolean, default=False)
    is_subscribed = db.Column(db.Boolean, default=True)  # Newsletter subscription
    
    # UTM Tracking
    utm_source = db.Column(db.String(100))
    utm_medium = db.Column(db.String(100))
    utm_campaign = db.Column(db.String(100))
    
    # Device/Browser Info
    user_agent = db.Column(db.String(500))
    ip_address = db.Column(db.String(45))  # IPv6 compatible
    device_type = db.Column(db.String(20))  # desktop, mobile, tablet
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    popup = db.relationship('Popup', backref='leads')
    coupon = db.relationship('Coupon', backref='leads')
    consents = db.relationship('CustomerConsent', backref='lead', lazy='dynamic', cascade='all, delete-orphan')
    coupon_usages = db.relationship('CouponUsage', backref='lead', lazy='dynamic')
    
    def __repr__(self):
        return f'<PopupLead {self.email}>'


# ===== CUSTOMER CONSENT TRACKING =====

class CustomerConsent(db.Model):
    """Track customer consents for GDPR/privacy compliance"""
    __tablename__ = 'customer_consents'
    id = db.Column(db.Integer, primary_key=True)
    
    # Associated Lead
    lead_id = db.Column(db.Integer, db.ForeignKey('popup_leads.id'), nullable=False, index=True)
    email = db.Column(db.String(255), nullable=False, index=True)  # Indexed for quick lookup
    
    # Consent Types
    consent_type = db.Column(db.String(50), nullable=False)
    # Types: 'marketing_email', 'marketing_sms', 'terms_of_use', 
    #        'privacy_policy', 'discount_policy', 'newsletter'
    
    # Consent Status
    is_granted = db.Column(db.Boolean, default=False)
    consent_text = db.Column(db.Text)  # The actual text shown to user
    consent_version = db.Column(db.String(20), default='1.0')  # Version of consent text
    
    # Tracking
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    source_page = db.Column(db.String(500))
    popup_id = db.Column(db.Integer, db.ForeignKey('popups.id'), nullable=True)
    
    # Timestamps
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)
    revoked_at = db.Column(db.DateTime)  # If consent was later revoked
    
    # Relationships
    popup = db.relationship('Popup', backref='consents')
    
    def __repr__(self):
        return f'<CustomerConsent {self.email} - {self.consent_type}>'
    
    def revoke(self):
        """Revoke this consent"""
        self.is_granted = False
        self.revoked_at = datetime.utcnow()


class ConsentSettings(db.Model):
    """Global settings for consent texts and requirements"""
    __tablename__ = 'consent_settings'
    id = db.Column(db.Integer, primary_key=True)
    
    # Consent Type
    consent_type = db.Column(db.String(50), unique=True, nullable=False)
    
    # Display Settings
    display_name_he = db.Column(db.String(100), nullable=False)
    display_name_en = db.Column(db.String(100), nullable=False)
    consent_text_he = db.Column(db.Text, nullable=False)
    consent_text_en = db.Column(db.Text, nullable=False)
    
    # Configuration
    is_required = db.Column(db.Boolean, default=False)  # Must be checked to submit
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    version = db.Column(db.String(20), default='1.0')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ConsentSettings {self.consent_type}>'


class MenuItemOptionGroup(db.Model):
    __tablename__ = 'menu_item_option_groups'
    id = db.Column(db.Integer, primary_key=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id', ondelete='CASCADE'), nullable=False)
    name_he = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    selection_type = db.Column(db.String(20), default='single')
    is_required = db.Column(db.Boolean, default=False)
    min_selections = db.Column(db.Integer, default=0)
    max_selections = db.Column(db.Integer, default=0)
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    choices = db.relationship('MenuItemOptionChoice', backref='option_group', lazy=True, cascade='all, delete-orphan', order_by='MenuItemOptionChoice.display_order')


class MenuItemOptionChoice(db.Model):
    __tablename__ = 'menu_item_option_choices'
    id = db.Column(db.Integer, primary_key=True)
    option_group_id = db.Column(db.Integer, db.ForeignKey('menu_item_option_groups.id', ondelete='CASCADE'), nullable=False)
    name_he = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    price_modifier = db.Column(db.Float, default=0)
    is_default = db.Column(db.Boolean, default=False)
    is_available = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)


class GlobalOptionGroup(db.Model):
    __tablename__ = 'global_option_groups'
    id = db.Column(db.Integer, primary_key=True)
    name_he = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    selection_type = db.Column(db.String(20), default='single')
    is_required = db.Column(db.Boolean, default=False)
    min_selections = db.Column(db.Integer, default=0)
    max_selections = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    choices = db.relationship('GlobalOptionChoice', backref='option_group', lazy=True, cascade='all, delete-orphan', order_by='GlobalOptionChoice.display_order')
    linked_items = db.relationship('GlobalOptionGroupLink', backref='global_group', lazy=True, cascade='all, delete-orphan')


class GlobalOptionChoice(db.Model):
    __tablename__ = 'global_option_choices'
    id = db.Column(db.Integer, primary_key=True)
    global_group_id = db.Column(db.Integer, db.ForeignKey('global_option_groups.id', ondelete='CASCADE'), nullable=False)
    name_he = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    price_modifier = db.Column(db.Float, default=0)
    is_default = db.Column(db.Boolean, default=False)
    is_available = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)


class GlobalOptionGroupLink(db.Model):
    __tablename__ = 'global_option_group_links'
    id = db.Column(db.Integer, primary_key=True)
    global_group_id = db.Column(db.Integer, db.ForeignKey('global_option_groups.id', ondelete='CASCADE'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id', ondelete='CASCADE'), nullable=False)
    linked_option_group_id = db.Column(db.Integer, db.ForeignKey('menu_item_option_groups.id', ondelete='SET NULL'), nullable=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    menu_item = db.relationship('MenuItem', backref='global_option_links')
    linked_option_group = db.relationship('MenuItemOptionGroup', foreign_keys=[linked_option_group_id])
    __table_args__ = (db.UniqueConstraint('global_group_id', 'menu_item_id', name='uq_global_group_item'),)


class FoodOrder(db.Model):
    __tablename__ = 'food_orders'
    __table_args__ = (
        db.Index('idx_food_order_phone', 'customer_phone'),
        db.Index('idx_food_order_status', 'status'),
        db.Index('idx_food_order_created', 'created_at'),
        db.Index('idx_food_order_number', 'order_number'),
    )

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(30), unique=True, nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    branch_name = db.Column(db.String(100), nullable=True)
    order_type = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(30), default='pending')
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_email = db.Column(db.String(120))
    delivery_address = db.Column(db.String(300))
    delivery_city = db.Column(db.String(100))
    delivery_notes = db.Column(db.String(300))
    pickup_time = db.Column(db.String(50))
    subtotal = db.Column(db.Float, nullable=False, default=0)
    delivery_fee = db.Column(db.Float, default=0)
    discount_amount = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, nullable=False, default=0)
    payment_method = db.Column(db.String(30), default='cash')
    payment_status = db.Column(db.String(20), default='pending')
    payment_provider = db.Column(db.String(20))
    hyp_transaction_id = db.Column(db.String(100))
    hyp_order_ref = db.Column(db.String(100))
    customer_notes = db.Column(db.Text)
    admin_notes = db.Column(db.Text)
    confirmation_sms_sent = db.Column(db.Boolean, default=False)
    ready_sms_sent = db.Column(db.Boolean, default=False)
    telegram_notified = db.Column(db.Boolean, default=False)
    tracking_token = db.Column(db.String(50), unique=True, index=True)
    utm_source = db.Column(db.String(200), nullable=True)
    utm_medium = db.Column(db.String(200), nullable=True)
    utm_campaign = db.Column(db.String(200), nullable=True)
    referrer = db.Column(db.String(500), nullable=True)
    estimated_ready_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime)
    preparing_at = db.Column(db.DateTime)
    ready_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    coupon_code = db.Column(db.String(50), nullable=True)
    coupon_discount = db.Column(db.Float, default=0)
    customer_account_id = db.Column(db.Integer, nullable=True)
    items_json = db.Column(db.Text)
    bon_printed = db.Column(db.Boolean, default=False)
    bon_printed_at = db.Column(db.DateTime, nullable=True)
    bon_acked_at = db.Column(db.DateTime, nullable=True)
    bon_acked_device_id = db.Column(db.String(128), nullable=True)
    bon_print_error = db.Column(db.Text, nullable=True)
    bon_print_attempts = db.Column(db.Integer, default=0)
    source = db.Column(db.String(20), default='online')
    created_by_name = db.Column(db.String(100), nullable=True)
    items = db.relationship('FoodOrderItem', backref='food_order', lazy=True, cascade='all, delete-orphan')

    def set_order_number(self):
        released = ReleasedOrderNumber.query.order_by(ReleasedOrderNumber.order_number.asc()).first()
        if released:
            self.order_number = released.order_number
            db.session.delete(released)
            return

        import random
        ts = datetime.now().strftime('%y%m%d')
        suffix = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        self.order_number = f"ORD-{ts}-{suffix}"

    @property
    def status_display_he(self):
        mapping = {
            'pending': 'ממתין לאישור',
            'confirmed': 'אושר',
            'preparing': 'בהכנה',
            'ready': 'מוכן',
            'delivered': 'נמסר',
            'pickedup': 'נאסף',
            'cancelled': 'בוטל',
        }
        return mapping.get(self.status, self.status)

    @property
    def status_badge_class(self):
        mapping = {
            'pending': 'warning',
            'confirmed': 'info',
            'preparing': 'primary',
            'ready': 'success',
            'delivered': 'secondary',
            'pickedup': 'secondary',
            'cancelled': 'danger',
        }
        return mapping.get(self.status, 'secondary')

    @property
    def order_type_display_he(self):
        return 'משלוח' if self.order_type == 'delivery' else 'איסוף עצמי'

    def get_items(self):
        import json as _json
        if self.items_json:
            try:
                items = _json.loads(self.items_json)
                for item in items:
                    if isinstance(item, dict):
                        if 'price' not in item and 'unit_price' in item:
                            item['price'] = item['unit_price']
                        if 'qty' not in item and 'quantity' in item:
                            item['qty'] = item['quantity']
                        if 'name_he' not in item and 'item_name_he' in item:
                            item['name_he'] = item['item_name_he']
                return items
            except Exception:
                return []
        return []

    def __repr__(self):
        return f'<FoodOrder #{self.order_number} {self.status}>'


class FoodOrderItem(db.Model):
    __tablename__ = 'food_order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('food_orders.id', ondelete='CASCADE'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=True)
    item_name_he = db.Column(db.String(200), nullable=False)
    item_name_en = db.Column(db.String(200))
    quantity = db.Column(db.Integer, default=1, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    special_instructions = db.Column(db.String(300))
    options_json = db.Column(db.Text)

    def __repr__(self):
        return f'<FoodOrderItem {self.item_name_he} x{self.quantity}>'


class ManagerPIN(db.Model):
    __tablename__ = 'manager_pins'
    id = db.Column(db.Integer, primary_key=True)
    pin_hash = db.Column(db.String(256), nullable=False)
    pin_plain = db.Column(db.String(10), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime)
    ops_permissions = db.Column(db.JSON, default=list)
    is_ops_superadmin = db.Column(db.Boolean, default=False)

    branch = db.relationship('Branch', foreign_keys=[branch_id])

    OPS_MODULES = ['home', 'orders', 'menu', 'stock', 'deals', 'branches', 'shifts', 'delivery', 'employees', 'history']

    def set_pin(self, pin):
        self.pin_hash = generate_password_hash(pin)

    def check_pin(self, pin):
        return check_password_hash(self.pin_hash, pin)

    def has_ops_permission(self, module):
        if self.is_ops_superadmin:
            return True
        perms = self.ops_permissions or []
        return module in perms

    def get_ops_modules(self):
        if self.is_ops_superadmin:
            return self.OPS_MODULES[:]
        return [m for m in self.OPS_MODULES if m in (self.ops_permissions or [])]

    def __repr__(self):
        return f'<ManagerPIN {self.name}>'


class EnrolledDevice(db.Model):
    __tablename__ = 'enrolled_devices'
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(100), nullable=False)
    device_token = db.Column(db.String(128), unique=True, nullable=False)
    enrollment_code = db.Column(db.String(32), unique=True)
    pending_request_token = db.Column(db.String(64), unique=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    enrolled_at = db.Column(db.DateTime)
    enrolled_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    last_seen = db.Column(db.DateTime)
    user_agent = db.Column(db.String(500))
    last_pin_id = db.Column(db.Integer, db.ForeignKey('manager_pins.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    branch = db.relationship('Branch', backref='enrolled_devices')
    last_pin = db.relationship('ManagerPIN', backref='enrolled_devices')
    enrolled_by_user = db.relationship('AdminUser', backref='enrolled_devices')

    def __repr__(self):
        return f'<EnrolledDevice {self.device_name}>'


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


class OrderActivityLog(db.Model):
    __tablename__ = 'order_activity_logs'
    __table_args__ = (
        db.Index('idx_oal_order_id', 'order_id'),
        db.Index('idx_oal_created', 'created_at'),
    )

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('food_orders.id', ondelete='CASCADE'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    old_value = db.Column(db.String(100))
    new_value = db.Column(db.String(100))
    staff_name = db.Column(db.String(100))
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship('FoodOrder', backref=db.backref('activity_logs', lazy='dynamic', order_by='OrderActivityLog.created_at.desc()'))

    def __repr__(self):
        return f'<OrderActivityLog order={self.order_id} action={self.action}>'


class SMSLog(db.Model):
    __tablename__ = 'sms_logs'
    __table_args__ = (
        db.Index('idx_sms_log_order', 'order_id'),
        db.Index('idx_sms_log_created', 'created_at'),
    )

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('food_orders.id', ondelete='SET NULL'), nullable=True)
    recipient_phone = db.Column(db.String(30), nullable=False)
    message_type = db.Column(db.String(50), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    provider = db.Column(db.String(30), default='sms4free')
    status = db.Column(db.String(20), default='sent')
    error_message = db.Column(db.Text)
    staff_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship('FoodOrder', backref=db.backref('sms_logs', lazy='dynamic', order_by='SMSLog.created_at.desc()'))

    def __repr__(self):
        return f'<SMSLog {self.message_type} to {self.recipient_phone}>'


class Printer(db.Model):
    __tablename__ = 'printers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='CASCADE'), nullable=False)
    printer_type = db.Column(db.String(50), default='snbc-btp-r880npv')
    ip_address = db.Column(db.String(45), nullable=False)
    port = db.Column(db.Integer, default=9100)
    encoding = db.Column(db.String(30), default='iso-8859-8')
    codepage_num = db.Column(db.Integer, default=36)
    cut_feed_lines = db.Column(db.Integer, default=6)
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    checker_copies = db.Column(db.Integer, default=2)
    payment_copies = db.Column(db.Integer, default=1)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    branch = db.relationship('Branch', backref=db.backref('printers', lazy=True, cascade='all, delete-orphan'))
    stations = db.relationship('PrinterStation', backref='printer', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'printer_type': self.printer_type or 'escpos',
            'branch_id': self.branch_id,
            'ip_address': self.ip_address,
            'port': self.port,
            'encoding': self.encoding,
            'codepage_num': self.codepage_num,
            'cut_feed_lines': self.cut_feed_lines,
            'is_active': self.is_active,
            'display_order': self.display_order,
            'checker_copies': self.checker_copies,
            'payment_copies': self.payment_copies,
            'is_default': self.is_default,
            'stations': [s.station_name for s in self.stations],
        }

    def __repr__(self):
        return f'<Printer {self.name} @ {self.ip_address}>'


class PrintStation(db.Model):
    __tablename__ = 'print_stations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PrintStation {self.name}>'


class PrinterStation(db.Model):
    __tablename__ = 'printer_stations'
    __table_args__ = (
        db.UniqueConstraint('printer_id', 'station_name', name='uq_printer_station'),
    )
    id = db.Column(db.Integer, primary_key=True)
    printer_id = db.Column(db.Integer, db.ForeignKey('printers.id', ondelete='CASCADE'), nullable=False)
    station_name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<PrinterStation {self.station_name} -> Printer#{self.printer_id}>'


class TimeLog(db.Model):
    __tablename__ = 'time_logs'
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('manager_pins.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    clock_in = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    clock_out = db.Column(db.DateTime, nullable=True)
    source = db.Column(db.String(20), default='kds')

    worker = db.relationship('ManagerPIN', backref='time_logs', foreign_keys=[worker_id])
    branch = db.relationship('Branch', foreign_keys=[branch_id])

    @property
    def duration_seconds(self):
        end = self.clock_out or datetime.utcnow()
        return max(0, int((end - self.clock_in).total_seconds()))

    @property
    def duration_display(self):
        s = self.duration_seconds
        h, remainder = divmod(s, 3600)
        m, _ = divmod(remainder, 60)
        return f'{h}:{m:02d}'

    @property
    def is_open(self):
        return self.clock_out is None

    def close_shift(self):
        if self.clock_out is None:
            self.clock_out = datetime.utcnow()

    @staticmethod
    def get_auto_close_hours():
        import os
        try:
            return float(os.environ.get('SHIFT_AUTO_CLOSE_HOURS', '12'))
        except (ValueError, TypeError):
            return 12.0

    @staticmethod
    def auto_close_stale(threshold_hours=None):
        if threshold_hours is None:
            threshold_hours = TimeLog.get_auto_close_hours()
        cutoff = datetime.utcnow() - timedelta(hours=threshold_hours)
        stale = TimeLog.query.filter(
            TimeLog.clock_out.is_(None),
            TimeLog.clock_in < cutoff,
        ).all()
        for tl in stale:
            tl.clock_out = tl.clock_in + timedelta(hours=threshold_hours)
        return len(stale)

    def __repr__(self):
        return f'<TimeLog worker={self.worker_id} in={self.clock_in} out={self.clock_out}>'


class SMSTemplate(db.Model):
    __tablename__ = 'sms_templates'
    id = db.Column(db.Integer, primary_key=True)
    name_he = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100))
    content_he = db.Column(db.Text, nullable=False)
    content_en = db.Column(db.Text)
    description = db.Column(db.Text)
    template_type = db.Column(db.String(30), default='order_update')
    available_variables = db.Column(db.Text)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='SET NULL'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    branch = db.relationship('Branch', backref=db.backref('sms_templates', lazy='dynamic'))

    CATEGORIES = [
        ('order_update', 'עדכון הזמנה'),
        ('marketing', 'שיווק'),
        ('custom', 'מותאם אישית'),
    ]

    PLACEHOLDERS = [
        ('{customer_name}', 'שם הלקוח'),
        ('{order_number}', 'מספר הזמנה'),
        ('{branch_name}', 'שם הסניף'),
        ('{total_amount}', 'סכום הזמנה'),
        ('{order_type}', 'סוג הזמנה'),
        ('{estimated_time}', 'זמן מוערך'),
    ]

    def render(self, order=None, branch=None):
        text = self.content_he or ''
        if order:
            text = text.replace('{customer_name}', order.customer_name or '')
            text = text.replace('{order_number}', order.order_number or '')
            text = text.replace('{total_amount}', f'{order.total_amount:.0f}' if order.total_amount else '0')
            type_he = 'משלוח' if order.order_type == 'delivery' else 'איסוף עצמי'
            text = text.replace('{order_type}', type_he)
            est = ''
            if order.estimated_ready_at:
                est = order.estimated_ready_at.strftime('%H:%M')
            text = text.replace('{estimated_time}', est)
        if branch:
            text = text.replace('{branch_name}', branch.name_he or '')
        else:
            text = text.replace('{branch_name}', '')
        return text

    @staticmethod
    def seed_defaults():
        if SMSTemplate.query.first():
            return
        defaults = [
            SMSTemplate(
                name_he='הזמנה מוכנה לאיסוף',
                content_he='שלום {customer_name}! הזמנתך #{order_number} מוכנה לאיסוף. מחכים לך! 🎉',
                template_type='order_update',
                available_variables='{customer_name},{order_number},{branch_name},{total_amount},{order_type},{estimated_time}',
            ),
            SMSTemplate(
                name_he='הזמנה יצאה למשלוח',
                content_he='שלום {customer_name}! הזמנתך #{order_number} בדרך אליך. שליח יגיע בקרוב 🛵',
                template_type='order_update',
                available_variables='{customer_name},{order_number},{branch_name},{total_amount},{order_type},{estimated_time}',
            ),
            SMSTemplate(
                name_he='הזמנה אושרה',
                content_he='שלום {customer_name}! הזמנתך #{order_number} אושרה ונמצאת בהכנה. זמן מוערך: {estimated_time} ⏰',
                template_type='order_update',
                available_variables='{customer_name},{order_number},{branch_name},{total_amount},{order_type},{estimated_time}',
            ),
            SMSTemplate(
                name_he='הזמנה בוטלה',
                content_he='שלום {customer_name}, הזמנתך #{order_number} בוטלה. לפרטים ניתן להתקשר אלינו.',
                template_type='order_update',
                available_variables='{customer_name},{order_number},{branch_name},{total_amount},{order_type},{estimated_time}',
            ),
        ]
        for t in defaults:
            db.session.add(t)
        db.session.commit()

    def __repr__(self):
        return f'<SMSTemplate {self.name_he}>'


class SMSAutoTrigger(db.Model):
    __tablename__ = 'sms_auto_triggers'
    id = db.Column(db.Integer, primary_key=True)
    order_status = db.Column(db.String(30), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('sms_templates.id', ondelete='CASCADE'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='CASCADE'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    template = db.relationship('SMSTemplate', backref=db.backref('triggers', lazy='dynamic'))
    branch = db.relationship('Branch', backref=db.backref('sms_triggers', lazy='dynamic'))

    ORDER_STATUSES = [
        ('confirmed', 'אושרה'),
        ('preparing', 'בהכנה'),
        ('ready', 'מוכנה'),
        ('delivered', 'נמסרה'),
        ('pickedup', 'נאספה'),
        ('cancelled', 'בוטלה'),
    ]

    def __repr__(self):
        return f'<SMSAutoTrigger {self.order_status} → template={self.template_id}>'


class ArchivedOrder(db.Model):
    __tablename__ = 'archived_orders'
    id = db.Column(db.Integer, primary_key=True)
    original_order_id = db.Column(db.Integer, nullable=False)
    order_number = db.Column(db.String(30), nullable=False)
    branch_id = db.Column(db.Integer, nullable=True)
    branch_name = db.Column(db.String(100), nullable=True)
    customer_name = db.Column(db.String(100))
    customer_phone = db.Column(db.String(20))
    customer_email = db.Column(db.String(120))
    order_type = db.Column(db.String(20))
    status = db.Column(db.String(30))
    payment_method = db.Column(db.String(30))
    payment_status = db.Column(db.String(20))
    total_amount = db.Column(db.Float, default=0)
    subtotal = db.Column(db.Float, default=0)
    delivery_fee = db.Column(db.Float, default=0)
    discount_amount = db.Column(db.Float, default=0)
    coupon_code = db.Column(db.String(50), nullable=True)
    items_snapshot = db.Column(db.Text)
    full_order_json = db.Column(db.Text)
    deleted_by = db.Column(db.String(100))
    deleted_at = db.Column(db.DateTime, default=datetime.utcnow)
    deletion_reason = db.Column(db.Text)
    original_created_at = db.Column(db.DateTime)
    restored_at = db.Column(db.DateTime, nullable=True)
    restored_by = db.Column(db.String(100), nullable=True)
    restored_order_id = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<ArchivedOrder #{self.order_number}>'


class ReleasedOrderNumber(db.Model):
    __tablename__ = 'released_order_numbers'
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(30), unique=True, nullable=False)
    released_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ReleasedOrderNumber {self.order_number}>'


class PrintDevice(db.Model):
    __tablename__ = 'print_devices'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(128), unique=True, nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    device_name = db.Column(db.String(100), nullable=False)
    last_heartbeat = db.Column(db.DateTime, nullable=True)
    is_online = db.Column(db.Boolean, default=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    config_json = db.Column(db.Text, nullable=True)

    branch = db.relationship('Branch', backref=db.backref('print_devices', lazy=True))

    def to_dict(self):
        import json as _json
        config = {}
        if self.config_json:
            try:
                config = _json.loads(self.config_json)
            except Exception:
                pass
        return {
            'id': self.id,
            'device_id': self.device_id,
            'branch_id': self.branch_id,
            'device_name': self.device_name,
            'last_heartbeat': self.last_heartbeat.isoformat() + 'Z' if self.last_heartbeat else None,
            'is_online': self.is_online,
            'registered_at': self.registered_at.isoformat() + 'Z' if self.registered_at else None,
            'config': config,
        }

    def __repr__(self):
        return f'<PrintDevice {self.device_name} ({self.device_id})>'


class ApiKey(db.Model):
    __tablename__ = 'api_keys'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    branch = db.relationship('Branch', backref=db.backref('api_keys', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'name': self.name,
            'branch_id': self.branch_id,
            'branch_name': self.branch.name_he if self.branch else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'last_used_at': self.last_used_at.isoformat() + 'Z' if self.last_used_at else None,
            'created_by': self.created_by,
            'notes': self.notes,
        }

    def __repr__(self):
        return f'<ApiKey {self.name} ({"active" if self.is_active else "revoked"})>'
