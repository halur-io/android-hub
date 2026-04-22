from database import db
from datetime import datetime

menu_item_dietary_properties = db.Table('menu_item_dietary_properties',
    db.Column('menu_item_id', db.Integer, db.ForeignKey('menu_items.id'), primary_key=True),
    db.Column('dietary_property_id', db.Integer, db.ForeignKey('dietary_properties.id'), primary_key=True)
)

class MenuCategory(db.Model):
    __tablename__ = 'menu_categories'
    id = db.Column(db.Integer, primary_key=True)
    name_he = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    description_he = db.Column(db.Text)
    description_en = db.Column(db.Text)
    footer_text_he = db.Column(db.Text)
    footer_text_en = db.Column(db.Text)
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    show_in_menu = db.Column(db.Boolean, default=True)
    show_in_order = db.Column(db.Boolean, default=True)
    featured = db.Column(db.Boolean, default=False)
    icon = db.Column(db.String(50))
    color = db.Column(db.String(7))
    image_path = db.Column(db.String(255))
    parent_id = db.Column(db.Integer, db.ForeignKey('menu_categories.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    menu_items = db.relationship('MenuItem', backref='category', lazy=True, cascade='all, delete-orphan')
    subcategories = db.relationship('MenuCategory', backref=db.backref('parent', remote_side='MenuCategory.id'), lazy=True)

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('menu_categories.id'), nullable=False)
    name_he = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200), nullable=False)
    description_he = db.Column(db.Text)
    description_en = db.Column(db.Text)
    short_description_he = db.Column(db.String(255))
    short_description_en = db.Column(db.String(255))
    ingredients_he = db.Column(db.Text)
    ingredients_en = db.Column(db.Text)
    base_price = db.Column(db.Float)
    image_path = db.Column(db.String(500))
    image_hero_path = db.Column(db.String(500))
    gallery_images = db.Column(db.Text)
    is_vegetarian = db.Column(db.Boolean, default=False)
    is_vegan = db.Column(db.Boolean, default=False)
    is_gluten_free = db.Column(db.Boolean, default=False)
    is_dairy_free = db.Column(db.Boolean, default=False)
    is_nut_free = db.Column(db.Boolean, default=False)
    is_spicy = db.Column(db.Boolean, default=False)
    is_halal = db.Column(db.Boolean, default=False)
    is_kosher = db.Column(db.Boolean, default=False)
    is_organic = db.Column(db.Boolean, default=False)
    is_signature = db.Column(db.Boolean, default=False)
    is_new = db.Column(db.Boolean, default=False)
    is_popular = db.Column(db.Boolean, default=False)
    is_available = db.Column(db.Boolean, default=True)
    allow_takeaway = db.Column(db.Boolean, default=True)
    allow_delivery = db.Column(db.Boolean, default=True)
    prep_time_minutes = db.Column(db.Integer)
    print_station = db.Column(db.String(50))
    print_name = db.Column(db.String(100))
    calories = db.Column(db.Integer)
    spice_level = db.Column(db.Integer, default=0)
    allergens = db.Column(db.Text)
    show_in_order = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    featured_until = db.Column(db.DateTime)
    discount_percentage = db.Column(db.Float, default=0)
    special_offer_text_he = db.Column(db.String(255))
    special_offer_text_en = db.Column(db.String(255))
    available_days = db.Column(db.String(20), default='1111111')
    available_from_time = db.Column(db.String(5))
    available_to_time = db.Column(db.String(5))
    custom_tags = db.Column(db.Text)
    is_combo = db.Column(db.Boolean, default=False)
    combo_items_json = db.Column(db.Text)
    image_data = db.Column(db.LargeBinary)
    price_options = db.relationship('MenuItemPrice', backref='menu_item', lazy=True, cascade='all, delete-orphan')
    option_groups = db.relationship('MenuItemOptionGroup', backref='menu_item', lazy=True, cascade='all, delete-orphan', order_by='MenuItemOptionGroup.display_order')
    variations = db.relationship('MenuItemVariation', backref='menu_item', lazy=True, cascade='all, delete-orphan')
    dietary_properties = db.relationship('DietaryProperty', secondary=menu_item_dietary_properties, backref='menu_items')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MenuItemPrice(db.Model):
    __tablename__ = 'menu_item_prices'
    id = db.Column(db.Integer, primary_key=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    size_name_he = db.Column(db.String(50), nullable=False)
    size_name_en = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)

class MenuItemIngredient(db.Model):
    __tablename__ = 'menu_item_ingredients'
    id = db.Column(db.Integer, primary_key=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    stock_item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    menu_item = db.relationship('MenuItem', backref='ingredients')
    stock_item = db.relationship('StockItem', backref='menu_usage')

class MenuItemVariation(db.Model):
    __tablename__ = 'menu_item_variations'
    id = db.Column(db.Integer, primary_key=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    variation_type = db.Column(db.String(50))
    name_he = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    price_modifier = db.Column(db.Float, default=0)
    is_default = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)

class DietaryProperty(db.Model):
    __tablename__ = 'dietary_properties'
    id = db.Column(db.Integer, primary_key=True)
    name_he = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(50))
    color = db.Column(db.String(7))
    description_he = db.Column(db.String(255))
    description_en = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MenuSettings(db.Model):
    __tablename__ = 'menu_settings'
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text)
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
