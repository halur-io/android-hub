from database import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Admin User Model
class AdminUser(UserMixin, db.Model):
    __tablename__ = 'admin_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_superadmin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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
    display_order = db.Column(db.Integer, default=0)
    working_hours = db.relationship('WorkingHours', backref='branch', lazy=True, cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    menu_items = db.relationship('MenuItem', backref='category', lazy=True, cascade='all, delete-orphan')

# Menu Items
class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('menu_categories.id'), nullable=False)
    name_he = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200), nullable=False)
    description_he = db.Column(db.Text)
    description_en = db.Column(db.Text)
    price = db.Column(db.Float)
    image_path = db.Column(db.String(500))
    is_vegetarian = db.Column(db.Boolean, default=False)
    is_vegan = db.Column(db.Boolean, default=False)
    is_gluten_free = db.Column(db.Boolean, default=False)
    is_spicy = db.Column(db.Boolean, default=False)
    is_available = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
