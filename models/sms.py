from database import db
from datetime import datetime

class SMSLog(db.Model):
    __tablename__ = 'sms_logs'
    __table_args__ = (
        db.Index('idx_sms_log_order', 'order_id'),
        db.Index('idx_sms_log_created', 'created_at'),
    )

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('food_orders.id', ondelete='SET NULL'), nullable=True)
    recipient_phone = db.Column(db.String(30), nullable=False)
    message_type = db.Column(db.String(50), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    provider = db.Column(db.String(30), default='sms4free')
    status = db.Column(db.String(20), default='sent')
    error_message = db.Column(db.Text)
    staff_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship('FoodOrder', backref=db.backref('sms_logs', lazy='dynamic', order_by='SMSLog.created_at.desc()'))

    def __repr__(self):
        return f'<SMSLog {self.message_type} to {self.recipient_phone}>'


class SMSTemplate(db.Model):
    __tablename__ = 'sms_templates'
    id = db.Column(db.Integer, primary_key=True)
    name_he = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100))
    content_he = db.Column(db.Text, nullable=False)
    content_en = db.Column(db.Text)
    description = db.Column(db.Text)
    template_type = db.Column(db.String(30), default='order_update')
    available_variables = db.Column(db.Text)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='SET NULL'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    branch = db.relationship('Branch', backref=db.backref('sms_templates', lazy='dynamic'))

    CATEGORIES = [
        ('order_update', 'עדכון הזמנה'),
        ('marketing', 'שיווק'),
        ('custom', 'מותאם אישית'),
    ]

    PLACEHOLDERS = [
        ('{customer_name}', 'שם הלקוח'),
        ('{order_number}', 'מספר הזמנה'),
        ('{branch_name}', 'שם הסניף'),
        ('{total_amount}', 'סכום הזמנה'),
        ('{order_type}', 'סוג הזמנה'),
        ('{estimated_time}', 'זמן מוערך'),
    ]

    def render(self, order=None, branch=None):
        text = self.content_he or ''
        if order:
            text = text.replace('{customer_name}', order.customer_name or '')
            text = text.replace('{order_number}', order.order_number or '')
            text = text.replace('{total_amount}', f'{order.total_amount:.0f}' if order.total_amount else '0')
            type_he = 'משלוח' if order.order_type == 'delivery' else 'איסוף עצמי'
            text = text.replace('{order_type}', type_he)
            est = ''
            if order.estimated_ready_at:
                est = order.estimated_ready_at.strftime('%H:%M')
            text = text.replace('{estimated_time}', est)
        if branch:
            text = text.replace('{branch_name}', branch.name_he or '')
        else:
            text = text.replace('{branch_name}', '')
        return text

    @staticmethod
    def seed_defaults():
        if SMSTemplate.query.first():
            return
        defaults = [
            SMSTemplate(
                name_he='הזמנה מוכנה לאיסוף',
                content_he='שלום {customer_name}! הזמנתך #{order_number} מוכנה לאיסוף. מחכים לך! 🎉',
                template_type='order_update',
                available_variables='{customer_name},{order_number},{branch_name},{total_amount},{order_type},{estimated_time}',
            ),
            SMSTemplate(
                name_he='הזמנה יצאה למשלוח',
                content_he='שלום {customer_name}! הזמנתך #{order_number} בדרך אליך. שליח יגיע בקרוב 🛵',
                template_type='order_update',
                available_variables='{customer_name},{order_number},{branch_name},{total_amount},{order_type},{estimated_time}',
            ),
            SMSTemplate(
                name_he='הזמנה אושרה',
                content_he='שלום {customer_name}! הזמנתך #{order_number} אושרה ונמצאת בהכנה. זמן מוערך: {estimated_time} ⏰',
                template_type='order_update',
                available_variables='{customer_name},{order_number},{branch_name},{total_amount},{order_type},{estimated_time}',
            ),
            SMSTemplate(
                name_he='הזמנה בוטלה',
                content_he='שלום {customer_name}, הזמנתך #{order_number} בוטלה. לפרטים ניתן להתקשר אלינו.',
                template_type='order_update',
                available_variables='{customer_name},{order_number},{branch_name},{total_amount},{order_type},{estimated_time}',
            ),
        ]
        for t in defaults:
            db.session.add(t)
        db.session.commit()

    def __repr__(self):
        return f'<SMSTemplate {self.name_he}>'


class SMSAutoTrigger(db.Model):
    __tablename__ = 'sms_auto_triggers'
    id = db.Column(db.Integer, primary_key=True)
    order_status = db.Column(db.String(30), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('sms_templates.id', ondelete='CASCADE'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='CASCADE'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    template = db.relationship('SMSTemplate', backref=db.backref('triggers', lazy='dynamic'))
    branch = db.relationship('Branch', backref=db.backref('sms_triggers', lazy='dynamic'))

    ORDER_STATUSES = [
        ('confirmed', 'אושרה'),
        ('preparing', 'בהכנה'),
        ('ready', 'מוכנה'),
        ('delivered', 'נמסרה'),
        ('pickedup', 'נאספה'),
        ('cancelled', 'בוטלה'),
    ]

    def __repr__(self):
        return f'<SMSAutoTrigger {self.order_status} → template={self.template_id}>'
