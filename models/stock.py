from database import db
from datetime import datetime

class StockCategory(db.Model):
    __tablename__ = 'stock_categories'
    id = db.Column(db.Integer, primary_key=True)
    name_he = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    description_he = db.Column(db.Text)
    description_en = db.Column(db.Text)
    icon = db.Column(db.String(50))
    color = db.Column(db.String(7))
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<StockCategory {self.name_he}>'

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    delivery_days = db.Column(db.String(20), default='1111111')
    delivery_time = db.Column(db.String(100))
    minimum_order = db.Column(db.Float, default=0)
    payment_terms = db.Column(db.String(100))
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Supplier {self.name}>'

class StockItem(db.Model):
    __tablename__ = 'stock_items'
    id = db.Column(db.Integer, primary_key=True)
    name_he = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200), nullable=False)
    description_he = db.Column(db.Text)
    description_en = db.Column(db.Text)
    sku = db.Column(db.String(50), unique=True)
    barcode = db.Column(db.String(100))
    category_id = db.Column(db.Integer, db.ForeignKey('stock_categories.id'))
    item_type = db.Column(db.String(50), nullable=False)
    primary_supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    supplier_item_code = db.Column(db.String(100))
    unit_he = db.Column(db.String(50))
    unit_en = db.Column(db.String(50))
    unit_size = db.Column(db.Float, default=1)
    cost_per_unit = db.Column(db.Float)
    selling_price = db.Column(db.Float)
    minimum_stock = db.Column(db.Float, default=0)
    maximum_stock = db.Column(db.Float)
    reorder_quantity = db.Column(db.Float)
    has_expiration = db.Column(db.Boolean, default=False)
    shelf_life_days = db.Column(db.Integer)
    storage_location = db.Column(db.String(100))
    storage_temperature = db.Column(db.String(50))
    category = db.relationship('StockCategory', backref='items')
    primary_supplier = db.relationship('Supplier', backref='items')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<StockItem {self.name_he}>'

class StockLevel(db.Model):
    __tablename__ = 'stock_levels'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    current_quantity = db.Column(db.Float, default=0)
    reserved_quantity = db.Column(db.Float, default=0)
    available_quantity = db.Column(db.Float, default=0)
    last_counted = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    item = db.relationship('StockItem', backref='stock_levels')
    branch = db.relationship('Branch', backref='stock_levels')
    __table_args__ = (db.UniqueConstraint('item_id', 'branch_id', name='unique_item_branch'),)

    def __repr__(self):
        return f'<StockLevel {self.item.name_he} @ {self.branch.name_he}: {self.current_quantity}>'

class StockTransaction(db.Model):
    __tablename__ = 'stock_transactions'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_cost = db.Column(db.Float)
    total_cost = db.Column(db.Float)
    reference_number = db.Column(db.String(100))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    expiration_date = db.Column(db.Date)
    batch_number = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    notes = db.Column(db.Text)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    item = db.relationship('StockItem', backref='transactions')
    branch = db.relationship('Branch', backref='stock_transactions')
    supplier = db.relationship('Supplier', backref='transactions')
    user = db.relationship('AdminUser', backref='stock_transactions')

    def __repr__(self):
        return f'<StockTransaction {self.transaction_type}: {self.quantity} {self.item.name_he}>'

class StockAlert(db.Model):
    __tablename__ = 'stock_alerts'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)
    message_he = db.Column(db.Text)
    message_en = db.Column(db.Text)
    severity = db.Column(db.String(20), default='medium')
    is_read = db.Column(db.Boolean, default=False)
    is_resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    item = db.relationship('StockItem', backref='alerts')
    branch = db.relationship('Branch', backref='stock_alerts')
    resolved_by_user = db.relationship('AdminUser', backref='resolved_stock_alerts')

    def __repr__(self):
        return f'<StockAlert {self.alert_type}: {self.item.name_he}>'

class ShoppingList(db.Model):
    __tablename__ = 'shopping_lists'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='draft')
    auto_generated = db.Column(db.Boolean, default=False)
    generation_criteria = db.Column(db.JSON)
    order_date = db.Column(db.Date)
    expected_delivery = db.Column(db.Date)
    total_estimated_cost = db.Column(db.Float, default=0)
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    sent_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime)
    branch = db.relationship('Branch', backref='shopping_lists')
    supplier = db.relationship('Supplier', backref='shopping_lists')
    created_by_user = db.relationship('AdminUser', foreign_keys=[created_by], backref='created_shopping_lists')
    sent_by_user = db.relationship('AdminUser', foreign_keys=[sent_by], backref='sent_shopping_lists')

    def __repr__(self):
        return f'<ShoppingList {self.name}>'

class ShoppingListItem(db.Model):
    __tablename__ = 'shopping_list_items'
    id = db.Column(db.Integer, primary_key=True)
    shopping_list_id = db.Column(db.Integer, db.ForeignKey('shopping_lists.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'), nullable=False)
    requested_quantity = db.Column(db.Float, nullable=False)
    estimated_unit_cost = db.Column(db.Float)
    estimated_total_cost = db.Column(db.Float)
    received_quantity = db.Column(db.Float, default=0)
    actual_unit_cost = db.Column(db.Float)
    actual_total_cost = db.Column(db.Float)
    status = db.Column(db.String(50), default='pending')
    notes = db.Column(db.Text)
    shopping_list = db.relationship('ShoppingList', backref='items')
    item = db.relationship('StockItem', backref='shopping_list_items')

    def __repr__(self):
        return f'<ShoppingListItem {self.item.name_he}: {self.requested_quantity}>'

class StockSettings(db.Model):
    __tablename__ = 'stock_settings'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    enable_expiration_tracking = db.Column(db.Boolean, default=True)
    enable_automatic_alerts = db.Column(db.Boolean, default=True)
    enable_auto_shopping_lists = db.Column(db.Boolean, default=True)
    enable_cost_tracking = db.Column(db.Boolean, default=True)
    enable_batch_tracking = db.Column(db.Boolean, default=False)
    low_stock_alert_days = db.Column(db.Integer, default=3)
    expiration_alert_days = db.Column(db.Integer, default=7)
    auto_generate_frequency = db.Column(db.String(20), default='weekly')
    auto_generate_day = db.Column(db.String(20), default='sunday')
    branch = db.relationship('Branch', backref='stock_settings')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<StockSettings for {self.branch.name_he if self.branch else "Global"}>'

class SupplierItem(db.Model):
    __tablename__ = 'supplier_items'
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    stock_item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'), nullable=False)
    supplier_item_code = db.Column(db.String(100))
    supplier_item_name = db.Column(db.String(255))
    cost_per_unit = db.Column(db.Float)
    minimum_order_quantity = db.Column(db.Float)
    unit_package_size = db.Column(db.Float)
    is_available = db.Column(db.Boolean, default=True)
    lead_time_days = db.Column(db.Integer)
    priority = db.Column(db.Integer, default=1)
    notes = db.Column(db.Text)
    last_order_date = db.Column(db.Date)
    last_order_price = db.Column(db.Float)
    supplier = db.relationship('Supplier', backref='supplier_items')
    stock_item = db.relationship('StockItem', backref='supplier_items')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('supplier_id', 'stock_item_id', name='unique_supplier_item'),)

    def __repr__(self):
        return f'<SupplierItem {self.supplier.name} - {self.stock_item.name_he}>'
