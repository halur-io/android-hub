from database import db
from datetime import datetime

class PaymentConfiguration(db.Model):
    __tablename__ = 'payment_configuration'
    id = db.Column(db.Integer, primary_key=True)
    provider_name = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    display_name_he = db.Column(db.String(100))
    display_name_en = db.Column(db.String(100))
    display_order = db.Column(db.Integer, default=0)
    api_key = db.Column(db.String(500))
    api_secret = db.Column(db.String(500))
    merchant_id = db.Column(db.String(200))
    additional_config = db.Column(db.JSON)
    test_mode = db.Column(db.Boolean, default=True)
    webhook_url = db.Column(db.String(500))
    webhook_secret = db.Column(db.String(500))
    min_order_amount = db.Column(db.Float, default=0)
    max_order_amount = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<PaymentConfiguration {self.provider_name}>'
