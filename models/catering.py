from database import db
from datetime import datetime

class CateringPackage(db.Model):
    __tablename__ = 'catering_packages'
    id = db.Column(db.Integer, primary_key=True)
    name_he = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200), nullable=False)
    description_he = db.Column(db.Text, nullable=False)
    description_en = db.Column(db.Text, nullable=False)
    price_range_he = db.Column(db.String(100))
    price_range_en = db.Column(db.String(100))
    min_guests = db.Column(db.Integer)
    max_guests = db.Column(db.Integer)
    features_he = db.Column(db.Text)
    features_en = db.Column(db.Text)
    image_path = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<CateringPackage {self.name_en}>'

class CateringHighlight(db.Model):
    __tablename__ = 'catering_highlights'
    id = db.Column(db.Integer, primary_key=True)
    title_he = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200), nullable=False)
    description_he = db.Column(db.Text)
    description_en = db.Column(db.Text)
    icon = db.Column(db.String(100), default='fa-star')
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<CateringHighlight {self.title_en}>'

class CateringGalleryImage(db.Model):
    __tablename__ = 'catering_gallery_images'
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(500), nullable=False)
    caption_he = db.Column(db.String(255))
    caption_en = db.Column(db.String(255))
    alt_text_he = db.Column(db.String(255))
    alt_text_en = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CateringGalleryImage {self.id}>'
