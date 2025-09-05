from database import db
from datetime import datetime
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
    is_default = db.Column(db.Boolean, default=False)
    
    # JSON field to store task configuration
    tasks_config = db.Column(db.JSON)  # Will store array of task objects
    # JSON field to store assigned group IDs
    assigned_groups = db.Column(db.JSON)  # Will store array of group IDs
    
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
    icon = db.Column(db.String(50))  # FontAwesome icon name
    color = db.Column(db.String(7))  # Hex color code
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
    prep_time_minutes = db.Column(db.Integer)  # Preparation time
    calories = db.Column(db.Integer)  # Nutritional info
    spice_level = db.Column(db.Integer, default=0)  # 0-5 scale
    allergens = db.Column(db.Text)  # JSON array of allergens
    
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
    
    # Relationships
    price_options = db.relationship('MenuItemPrice', backref='menu_item', lazy=True, cascade='all, delete-orphan')
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
