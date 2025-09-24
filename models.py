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
    
    # Relationships
    supplier = db.relationship('Supplier', backref='receipts')
    branch = db.relationship('Branch', backref='receipts')
    verifier = db.relationship('AdminUser', backref='verified_receipts')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Receipt {self.receipt_number} - {self.supplier.name if self.supplier else "Unknown"}>'

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
