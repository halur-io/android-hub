from database import db
from datetime import datetime

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
    ordering_status = db.Column(db.String(20), default='open', nullable=False)
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
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    custom_price = db.Column(db.Float, nullable=True)
    display_order = db.Column(db.Integer, default=0)
    print_station = db.Column(db.String(50), nullable=True)

    menu_item = db.relationship('MenuItem', backref='branch_overrides')


class WorkingHours(db.Model):
    __tablename__ = 'working_hours'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)
    open_time = db.Column(db.String(5))
    close_time = db.Column(db.String(5))
    is_closed = db.Column(db.Boolean, default=False)
