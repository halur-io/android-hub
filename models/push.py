from database import db
from datetime import datetime


class OpsPushSubscription(db.Model):
    __tablename__ = 'ops_push_subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('enrolled_devices.id'), nullable=True, index=True)
    endpoint = db.Column(db.Text, nullable=False, unique=True)
    p256dh = db.Column(db.String(255), nullable=False)
    auth = db.Column(db.String(255), nullable=False)
    user_agent = db.Column(db.String(500))
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    last_used_at = db.Column(db.DateTime)
    failure_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class OpsPushVAPID(db.Model):
    __tablename__ = 'ops_push_vapid'
    id = db.Column(db.Integer, primary_key=True)
    public_key = db.Column(db.Text, nullable=False)
    private_key = db.Column(db.Text, nullable=False)
    subject = db.Column(db.String(255), nullable=False, default='mailto:admin@sumo-restaurant.co.il')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
