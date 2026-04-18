from database import db
from datetime import datetime

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
    payment_url = db.Column(db.String(500), nullable=True)
    payment_callback_token = db.Column(db.String(64), nullable=True)
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
    bon_print_options = db.Column(db.Text, nullable=True)
    void_log = db.Column(db.Text, nullable=True)
    source = db.Column(db.String(20), default='online')
    created_by_name = db.Column(db.String(120), nullable=True)
    table_number = db.Column(db.String(20), nullable=True)
    dine_in_session_id = db.Column(db.Integer, db.ForeignKey('dine_in_sessions.id'), nullable=True)
    display_number = db.Column(db.String(20), nullable=True, index=True)
    operating_day_id = db.Column(db.Integer, nullable=True, index=True)
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
        mapping = {
            'delivery': 'משלוח',
            'pickup': 'איסוף עצמי',
            'dine_in': 'ישיבה',
        }
        return mapping.get(self.order_type, 'איסוף עצמי')

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


class OperatingDay(db.Model):
    __tablename__ = 'operating_days'
    __table_args__ = (
        db.Index('idx_operating_days_branch_status', 'branch_id', 'status'),
    )
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True, index=True)
    status = db.Column(db.String(10), default='open', nullable=False)
    opened_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    closed_at = db.Column(db.DateTime, nullable=True)
    opened_by_pin_id = db.Column(db.Integer, nullable=True)
    opened_by_name = db.Column(db.String(120), nullable=True)
    closed_by_pin_id = db.Column(db.Integer, nullable=True)
    closed_by_name = db.Column(db.String(120), nullable=True)
    pickup_count = db.Column(db.Integer, default=0)
    delivery_count = db.Column(db.Integer, default=0)
    dine_in_count = db.Column(db.Integer, default=0)
    total_revenue = db.Column(db.Float, default=0)
    total_cash = db.Column(db.Float, default=0)


class DailyCounter(db.Model):
    __tablename__ = 'daily_counters'
    __table_args__ = (
        db.UniqueConstraint('operating_day_id', 'order_type', name='uq_daily_counter'),
    )
    id = db.Column(db.Integer, primary_key=True)
    operating_day_id = db.Column(db.Integer, db.ForeignKey('operating_days.id'), nullable=False, index=True)
    order_type = db.Column(db.String(20), nullable=False)
    next_seq = db.Column(db.Integer, default=1, nullable=False)


class ReleasedDisplayNumber(db.Model):
    __tablename__ = 'released_display_numbers'
    __table_args__ = (
        db.Index('idx_released_disp', 'operating_day_id', 'order_type', 'display_seq'),
    )
    id = db.Column(db.Integer, primary_key=True)
    operating_day_id = db.Column(db.Integer, db.ForeignKey('operating_days.id'), nullable=False)
    branch_id = db.Column(db.Integer, nullable=True)
    order_type = db.Column(db.String(20), nullable=False)
    display_seq = db.Column(db.Integer, nullable=False)
    released_at = db.Column(db.DateTime, default=datetime.utcnow)
