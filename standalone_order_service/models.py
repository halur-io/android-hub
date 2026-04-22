"""
Database Models for the Food Ordering Service.

All models use Flask-SQLAlchemy. The `db` instance must be provided by
the host application (see setup instructions in INTEGRATION_GUIDE.md).

Models included:
  - MenuCategory, MenuItem, MenuItemPrice, MenuItemOptionGroup, MenuItemOptionChoice
  - FoodOrder, FoodOrderItem
  - DeliveryZone
  - ManagerPIN  (used by the KDS dashboard for staff authentication)
  - WorkingHours, Branch  (used for ordering-hours enforcement)
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


def register_models(db):
    """
    Call once at app startup after creating the SQLAlchemy ``db`` instance.
    Returns a dict of all model classes keyed by name so the host app can
    reference them easily::

        from standalone_order_service.models import register_models
        models = register_models(db)
        FoodOrder = models['FoodOrder']
    """

    # ── Branch & Working Hours ────────────────────────────────────────────

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
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    class WorkingHours(db.Model):
        __tablename__ = 'working_hours'
        id = db.Column(db.Integer, primary_key=True)
        branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
        day_of_week = db.Column(db.Integer)
        day_name_he = db.Column(db.String(20))
        day_name_en = db.Column(db.String(20))
        open_time = db.Column(db.String(5))
        close_time = db.Column(db.String(5))
        is_closed = db.Column(db.Boolean, default=False)

    # ── Menu ──────────────────────────────────────────────────────────────

    class MenuCategory(db.Model):
        __tablename__ = 'menu_categories'
        id = db.Column(db.Integer, primary_key=True)
        menu_id = db.Column(db.Integer, nullable=True)
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
        menu_items = db.relationship('MenuItem', backref='category', lazy=True, cascade='all, delete-orphan')
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
        image_data = db.Column(db.LargeBinary)
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
        price_options = db.relationship('MenuItemPrice', backref='menu_item', lazy=True, cascade='all, delete-orphan')
        option_groups = db.relationship('MenuItemOptionGroup', backref='menu_item', lazy=True, cascade='all, delete-orphan', order_by='MenuItemOptionGroup.display_order')
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

    # ── Delivery Zones ────────────────────────────────────────────────────

    class DeliveryZone(db.Model):
        __tablename__ = 'delivery_zones'
        id = db.Column(db.Integer, primary_key=True)
        branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
        city_name = db.Column(db.String(100), nullable=False)
        name = db.Column(db.String(100))
        description = db.Column(db.Text)
        zone_data = db.Column(db.Text)
        delivery_fee = db.Column(db.Float, default=0)
        minimum_order = db.Column(db.Float, default=0)
        free_delivery_above = db.Column(db.Float)
        estimated_minutes = db.Column(db.Integer, default=30)
        estimated_delivery_time = db.Column(db.String(50))
        is_active = db.Column(db.Boolean, default=True)
        display_order = db.Column(db.Integer, default=0)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        def __repr__(self):
            return f'<DeliveryZone {self.city_name}: {self.delivery_fee}₪>'

    # ── Food Orders ───────────────────────────────────────────────────────

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
        customer_account_id = db.Column(db.Integer, nullable=True)
        items_json = db.Column(db.Text)
        items = db.relationship('FoodOrderItem', backref='food_order', lazy=True, cascade='all, delete-orphan')

        def set_order_number(self):
            import datetime as _dt, random as _rand
            ts = _dt.datetime.now().strftime('%y%m%d')
            suffix = ''.join([str(_rand.randint(0, 9)) for _ in range(4)])
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
            import json
            if self.items_json:
                try:
                    items = json.loads(self.items_json)
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

    # ── Manager PINs (KDS auth) ──────────────────────────────────────────

    class ManagerPIN(db.Model):
        __tablename__ = 'manager_pins'
        id = db.Column(db.Integer, primary_key=True)
        pin_hash = db.Column(db.String(256), nullable=False)
        pin_plain = db.Column(db.String(10), nullable=True)
        name = db.Column(db.String(100), nullable=False)
        description = db.Column(db.Text)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        last_used_at = db.Column(db.DateTime)

        def set_pin(self, pin):
            self.pin_hash = generate_password_hash(pin)

        def check_pin(self, pin):
            return check_password_hash(self.pin_hash, pin)

        def __repr__(self):
            return f'<ManagerPIN {self.name}>'

    # ── Site Settings (ordering-related fields) ──────────────────────

    class SiteSettings(db.Model):
        __tablename__ = 'site_settings'
        id = db.Column(db.Integer, primary_key=True)
        site_name_he = db.Column(db.String(200), default='המסעדה שלי')
        site_name_en = db.Column(db.String(200), default='My Restaurant')
        contact_phone = db.Column(db.String(20))
        admin_phone = db.Column(db.String(20))
        enable_online_ordering = db.Column(db.Boolean, default=False)
        ordering_paused = db.Column(db.Boolean, default=False)
        ordering_paused_message = db.Column(db.String(500))
        ordering_closed_message = db.Column(db.String(500))
        ordering_outside_hours_message = db.Column(db.String(500))
        enforce_ordering_hours = db.Column(db.Boolean, default=False)
        enable_delivery = db.Column(db.Boolean, default=True)
        enable_pickup = db.Column(db.Boolean, default=True)
        delivery_fee = db.Column(db.Float, default=15.0)
        free_delivery_threshold = db.Column(db.Float, default=100.0)
        estimated_delivery_time = db.Column(db.String(50), default='45-60')
        hyp_enabled = db.Column(db.Boolean, default=False)
        hyp_sandbox_mode = db.Column(db.Boolean, default=True)
        hyp_terminal = db.Column(db.String(50))
        hyp_api_key = db.Column(db.String(200))
        hyp_passp = db.Column(db.String(200))
        telegram_bot_token = db.Column(db.String(200))
        telegram_chat_id = db.Column(db.String(100))
        telegram_channel_id = db.Column(db.String(100))
        send_order_tracking_link = db.Column(db.Boolean, default=True)

        def __repr__(self):
            return f'<SiteSettings {self.site_name_he}>'

    return {
        'Branch': Branch,
        'BranchMenuItem': BranchMenuItem,
        'WorkingHours': WorkingHours,
        'MenuCategory': MenuCategory,
        'MenuItem': MenuItem,
        'MenuItemPrice': MenuItemPrice,
        'MenuItemOptionGroup': MenuItemOptionGroup,
        'MenuItemOptionChoice': MenuItemOptionChoice,
        'DeliveryZone': DeliveryZone,
        'FoodOrder': FoodOrder,
        'FoodOrderItem': FoodOrderItem,
        'ManagerPIN': ManagerPIN,
        'SiteSettings': SiteSettings,
    }
