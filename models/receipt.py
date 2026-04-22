from database import db
from datetime import datetime

class Receipt(db.Model):
    __tablename__ = 'receipts'
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(500), nullable=False)
    original_filename = db.Column(db.String(255))
    file_size = db.Column(db.Integer)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    receipt_date = db.Column(db.Date)
    receipt_number = db.Column(db.String(100))
    total_amount = db.Column(db.Float)
    tax_amount = db.Column(db.Float)
    currency = db.Column(db.String(3), default='ILS')
    ocr_status = db.Column(db.String(20), default='pending')
    ocr_data = db.Column(db.JSON)
    ocr_confidence = db.Column(db.Float)
    is_verified = db.Column(db.Boolean, default=False)
    verified_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    verified_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    processing_errors = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    processed_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    supplier = db.relationship('Supplier', backref='receipts')
    branch = db.relationship('Branch', backref='receipts')
    creator = db.relationship('AdminUser', foreign_keys=[created_by], backref='created_receipts')
    processor = db.relationship('AdminUser', foreign_keys=[processed_by], backref='processed_receipts')
    verifier = db.relationship('AdminUser', foreign_keys=[verified_by], backref='verified_receipts')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Receipt {self.receipt_number} - {self.supplier.name if self.supplier else "Unknown"}>'

class ReceiptImport(db.Model):
    __tablename__ = 'receipt_imports'
    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    status = db.Column(db.String(20), default='pending')
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    suggested_supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    supplier_confidence = db.Column(db.Float)
    candidate_supplier_ids = db.Column(db.JSON)
    receipt_date = db.Column(db.Date)
    total_amount = db.Column(db.Float)
    ai_raw_response = db.Column(db.JSON)
    ai_errors = db.Column(db.Text)
    approved_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    approved_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    shopping_list_id = db.Column(db.Integer, db.ForeignKey('shopping_lists.id'))
    stock_transaction_batch = db.Column(db.String(100))
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    receipt = db.relationship('Receipt', backref='imports')
    branch = db.relationship('Branch', backref='receipt_imports')
    supplier = db.relationship('Supplier', foreign_keys=[supplier_id], backref='receipt_imports')
    suggested_supplier = db.relationship('Supplier', foreign_keys=[suggested_supplier_id])
    shopping_list = db.relationship('ShoppingList', backref='receipt_imports')
    creator = db.relationship('AdminUser', foreign_keys=[created_by], backref='created_receipt_imports')
    approver = db.relationship('AdminUser', foreign_keys=[approved_by], backref='approved_receipt_imports')

    def __repr__(self):
        return f'<ReceiptImport {self.id} - {self.status}>'

class ReceiptImportItem(db.Model):
    __tablename__ = 'receipt_import_items'
    id = db.Column(db.Integer, primary_key=True)
    receipt_import_id = db.Column(db.Integer, db.ForeignKey('receipt_imports.id'), nullable=False)
    extracted_text = db.Column(db.String(500))
    product_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float)
    total_price = db.Column(db.Float)
    unit_of_measure = db.Column(db.String(20))
    stock_item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'))
    suggested_stock_item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'))
    supplier_item_id = db.Column(db.Integer, db.ForeignKey('supplier_items.id'))
    match_confidence = db.Column(db.Float)
    is_new_item = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    resolution_status = db.Column(db.String(20), default='pending')
    notes = db.Column(db.Text)
    line_number = db.Column(db.Integer)
    receipt_import = db.relationship('ReceiptImport', backref='line_items')
    stock_item = db.relationship('StockItem', foreign_keys=[stock_item_id], backref='receipt_import_items')
    suggested_stock_item = db.relationship('StockItem', foreign_keys=[suggested_stock_item_id])
    supplier_item = db.relationship('SupplierItem', backref='receipt_import_items')

    def __repr__(self):
        return f'<ReceiptImportItem {self.product_name}: {self.quantity}>'

class CostCategory(db.Model):
    __tablename__ = 'cost_categories'
    id = db.Column(db.Integer, primary_key=True)
    name_he = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    description_he = db.Column(db.Text)
    description_en = db.Column(db.Text)
    icon = db.Column(db.String(50))
    color = db.Column(db.String(7))
    parent_category_id = db.Column(db.Integer, db.ForeignKey('cost_categories.id'))
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    parent_category = db.relationship('CostCategory', remote_side=[id], backref='subcategories')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CostCategory {self.name_he}>'

class CostEntry(db.Model):
    __tablename__ = 'cost_entries'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='ILS')
    entry_date = db.Column(db.Date, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('cost_categories.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.id'))
    file_import_id = db.Column(db.Integer, db.ForeignKey('file_imports.id'))
    entry_type = db.Column(db.String(20), default='manual')
    is_approved = db.Column(db.Boolean, default=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    approved_at = db.Column(db.DateTime)
    reference_number = db.Column(db.String(100))
    payment_method = db.Column(db.String(50))
    tags = db.Column(db.JSON)
    notes = db.Column(db.Text)
    category = db.relationship('CostCategory', backref='cost_entries')
    supplier = db.relationship('Supplier', backref='cost_entries')
    branch = db.relationship('Branch', backref='cost_entries')
    receipt = db.relationship('Receipt', backref='cost_entries')
    approver = db.relationship('AdminUser', backref='approved_costs')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<CostEntry {self.description} - ₪{self.amount}>'

class ReceiptItem(db.Model):
    __tablename__ = 'receipt_items'
    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.id'), nullable=False)
    item_description = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Float)
    unit_price = db.Column(db.Float)
    total_price = db.Column(db.Float)
    stock_item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'))
    mapping_confidence = db.Column(db.Float)
    is_mapped = db.Column(db.Boolean, default=False)
    is_processed = db.Column(db.Boolean, default=False)
    item_code = db.Column(db.String(100))
    unit = db.Column(db.String(50))
    notes = db.Column(db.Text)
    receipt = db.relationship('Receipt', backref='items')
    stock_item = db.relationship('StockItem', backref='receipt_items')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ReceiptItem {self.item_description}>'

class CustomFieldDefinition(db.Model):
    __tablename__ = 'custom_field_definitions'
    id = db.Column(db.Integer, primary_key=True)
    field_name = db.Column(db.String(100), nullable=False)
    field_key = db.Column(db.String(100), nullable=False, unique=True)
    field_type = db.Column(db.String(20), nullable=False)
    dropdown_options = db.Column(db.JSON)
    number_min = db.Column(db.Float)
    number_max = db.Column(db.Float)
    text_regex = db.Column(db.String(255))
    text_max_length = db.Column(db.Integer)
    date_min = db.Column(db.Date)
    date_max = db.Column(db.Date)
    is_required = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_system = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)
    default_value = db.Column(db.String(255))
    help_text = db.Column(db.String(255))
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (
        db.Index('idx_field_active_order', 'field_type', 'is_active', 'display_order'),
    )

    def __repr__(self):
        return f'<CustomFieldDefinition {self.field_name} ({self.field_type})>'

class CustomFieldAssignment(db.Model):
    __tablename__ = 'custom_field_assignments'
    id = db.Column(db.Integer, primary_key=True)
    field_definition_id = db.Column(db.Integer, db.ForeignKey('custom_field_definitions.id'), nullable=False)
    scope_type = db.Column(db.String(20))
    scope_id = db.Column(db.Integer)
    field_definition = db.relationship('CustomFieldDefinition', backref='assignments')
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('field_definition_id', 'scope_type', 'scope_id', name='unique_field_scope'),)

    def __repr__(self):
        return f'<CustomFieldAssignment field={self.field_definition_id} scope={self.scope_type}:{self.scope_id}>'

class ReceiptCustomFieldValue(db.Model):
    __tablename__ = 'receipt_custom_field_values'
    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.id'), nullable=False)
    field_definition_id = db.Column(db.Integer, db.ForeignKey('custom_field_definitions.id'), nullable=False)
    value_text = db.Column(db.Text)
    value_number = db.Column(db.Float)
    value_date = db.Column(db.Date)
    value_boolean = db.Column(db.Boolean)
    receipt = db.relationship('Receipt', backref='custom_field_values')
    field_definition = db.relationship('CustomFieldDefinition', backref='values')
    updated_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (
        db.UniqueConstraint('receipt_id', 'field_definition_id', name='unique_receipt_field'),
        db.Index('idx_receipt_field', 'receipt_id', 'field_definition_id'),
    )

    def __repr__(self):
        return f'<ReceiptCustomFieldValue receipt={self.receipt_id} field={self.field_definition_id}>'

class ReceiptCustomFieldAudit(db.Model):
    __tablename__ = 'receipt_custom_field_audit'
    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.id'), nullable=False)
    field_definition_id = db.Column(db.Integer, db.ForeignKey('custom_field_definitions.id'), nullable=False)
    old_value = db.Column(db.JSON)
    new_value = db.Column(db.JSON)
    changed_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    receipt = db.relationship('Receipt', backref='field_audit_log')
    field_definition = db.relationship('CustomFieldDefinition', backref='audit_log')
    user = db.relationship('AdminUser', backref='field_changes')

    def __repr__(self):
        return f'<ReceiptCustomFieldAudit receipt={self.receipt_id} field={self.field_definition_id} by={self.changed_by}>'

class FileImport(db.Model):
    __tablename__ = 'file_imports'
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(20))
    import_type = db.Column(db.String(50), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    status = db.Column(db.String(20), default='pending')
    total_rows = db.Column(db.Integer)
    processed_rows = db.Column(db.Integer, default=0)
    successful_rows = db.Column(db.Integer, default=0)
    failed_rows = db.Column(db.Integer, default=0)
    field_mapping = db.Column(db.JSON)
    processing_log = db.Column(db.Text)
    error_details = db.Column(db.JSON)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    branch = db.relationship('Branch', backref='file_imports')
    uploader = db.relationship('AdminUser', backref='file_imports')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<FileImport {self.original_filename} - {self.status}>'
