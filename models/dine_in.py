from database import db
from datetime import datetime

class DineInTable(db.Model):
    __tablename__ = 'dine_in_tables'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    table_number = db.Column(db.String(20), nullable=False)
    capacity = db.Column(db.Integer, default=4)
    area = db.Column(db.String(50), default='')
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    pos_x = db.Column(db.Float, nullable=True)
    pos_y = db.Column(db.Float, nullable=True)
    width = db.Column(db.Float, default=100)
    height = db.Column(db.Float, default=80)
    shape = db.Column(db.String(10), default='rect')

    branch = db.relationship('Branch', backref=db.backref('dine_in_tables', lazy=True))
    sessions = db.relationship('DineInSession', backref='table', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('branch_id', 'table_number', name='uq_branch_table_number'),
    )

    def __repr__(self):
        return f'<DineInTable {self.table_number} branch={self.branch_id}>'


class DineInSession(db.Model):
    __tablename__ = 'dine_in_sessions'
    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey('dine_in_tables.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    status = db.Column(db.String(20), default='open')
    waiter_pin_id = db.Column(db.Integer, db.ForeignKey('manager_pins.id'), nullable=True)
    guests_count = db.Column(db.Integer, default=1)
    discount_type = db.Column(db.String(20), nullable=True)
    discount_value = db.Column(db.Float, default=0)
    notes = db.Column(db.Text, nullable=True)
    payment_url = db.Column(db.String(500), nullable=True)
    payment_callback_token = db.Column(db.String(64), nullable=True)
    pending_void_approvals = db.Column(db.Text, nullable=True)
    tip_amount = db.Column(db.Float, default=0)
    cash_received = db.Column(db.Float, nullable=True)
    cancel_reason = db.Column(db.String(100), nullable=True)
    cancel_note = db.Column(db.Text, nullable=True)
    split_config = db.Column(db.Text, nullable=True)
    opened_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime, nullable=True)

    branch = db.relationship('Branch', backref=db.backref('dine_in_sessions', lazy=True))
    waiter = db.relationship('ManagerPIN', backref=db.backref('dine_in_sessions', lazy=True))
    orders = db.relationship('FoodOrder', backref='dine_in_session', lazy=True)
    payment_splits = db.relationship('DineInPaymentSplit', backref='session', lazy=True, cascade='all, delete-orphan')

    @property
    def status_display_he(self):
        mapping = {
            'open': 'פתוח',
            'awaiting_payment': 'ממתין לתשלום',
            'closed': 'סגור',
            'cancelled': 'בוטל',
        }
        return mapping.get(self.status, self.status)

    @property
    def total_amount(self):
        total = 0
        for order in self.orders:
            if order.status != 'cancelled':
                total += order.total_amount or 0
        if self.discount_type == 'percentage' and self.discount_value:
            total = total * (1 - self.discount_value / 100)
        elif self.discount_type == 'fixed' and self.discount_value:
            total = max(0, total - self.discount_value)
        return round(total, 2)

    @property
    def subtotal_before_discount(self):
        total = 0
        for order in self.orders:
            if order.status != 'cancelled':
                total += order.total_amount or 0
        return round(total, 2)

    @property
    def elapsed_minutes(self):
        if self.opened_at:
            delta = datetime.utcnow() - self.opened_at
            return int(delta.total_seconds() / 60)
        return 0

    def __repr__(self):
        return f'<DineInSession table={self.table_id} status={self.status}>'


class DineInPaymentSplit(db.Model):
    __tablename__ = 'dine_in_payment_splits'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('dine_in_sessions.id'), nullable=False)
    portion_index = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), nullable=True)
    payment_status = db.Column(db.String(20), default='pending')
    payer_label = db.Column(db.String(100), nullable=True)
    tip_amount = db.Column(db.Float, default=0)
    cash_received = db.Column(db.Float, nullable=True)
    paid_at = db.Column(db.DateTime, nullable=True)
    payment_callback_token = db.Column(db.String(64), nullable=True)

    def __repr__(self):
        return f'<DineInPaymentSplit session={self.session_id} portion={self.portion_index} status={self.payment_status}>'
