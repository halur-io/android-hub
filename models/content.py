from database import db
from datetime import datetime
from sqlalchemy.orm import validates as _validates
from sanitize_html import sanitize_html as _sanitize_html

class GalleryPhoto(db.Model):
    __tablename__ = 'gallery_photos'
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(500), nullable=False)
    caption_he = db.Column(db.String(255))
    caption_en = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ContactMessage {self.name}>'

class CateringContact(db.Model):
    __tablename__ = 'catering_contacts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    event_date = db.Column(db.String(50), nullable=True)
    event_type = db.Column(db.String(100), nullable=True)
    guest_count = db.Column(db.Integer, nullable=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CateringContact {self.name} - {self.event_type}>'

class CareerPosition(db.Model):
    __tablename__ = 'career_positions'
    id = db.Column(db.Integer, primary_key=True)
    title_he = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200), nullable=False)
    description_he = db.Column(db.Text)
    description_en = db.Column(db.Text)
    requirements_he = db.Column(db.Text)
    requirements_en = db.Column(db.Text)
    location_he = db.Column(db.String(100))
    location_en = db.Column(db.String(100))
    employment_type_he = db.Column(db.String(50))
    employment_type_en = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @_validates('description_he', 'description_en', 'requirements_he', 'requirements_en')
    def _sanitize_content(self, key, value):
        if value:
            return _sanitize_html(value)
        return value

    def __repr__(self):
        return f'<CareerPosition {self.title_en}>'

class CareerContact(db.Model):
    __tablename__ = 'career_contacts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('career_positions.id'), nullable=True)
    position = db.relationship('CareerPosition', backref='applications')
    position_other = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    resume_path = db.Column(db.String(500))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CareerContact {self.name}>'

class NewsletterSubscriber(db.Model):
    __tablename__ = 'newsletter_subscribers'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True, default=None)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    unsubscribed_at = db.Column(db.DateTime, nullable=True, default=None)
    source = db.Column(db.String(50), default='website', nullable=False)

    def __repr__(self):
        return f'<NewsletterSubscriber {self.email}>'

class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    customer_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    guests = db.Column(db.Integer, nullable=False)
    special_requests = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Reservation {self.customer_name} - {self.date}>'

class PDFMenuUpload(db.Model):
    __tablename__ = 'pdf_menu_uploads'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    status = db.Column(db.String(50), default='uploaded')
    processing_progress = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    extracted_items_count = db.Column(db.Integer, default=0)
    items_added_to_menu = db.Column(db.Integer, default=0)
    raw_extraction_data = db.Column(db.JSON)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    processed_at = db.Column(db.DateTime)
    branch = db.relationship('Branch', backref='pdf_menu_uploads')
    uploader = db.relationship('AdminUser', backref='pdf_uploads')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<PDFMenuUpload {self.filename}>'
