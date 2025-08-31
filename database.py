import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

def init_db(app):
    """Initialize database with the Flask app"""
    # Configure database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'
    
    with app.app_context():
        # Import models to create tables
        import models
        
        # Import microservices models
        from services.config.config_service import SystemConfig, BranchConfig
        from services.auth.auth_service import Customer, CustomerAddress, PhoneVerification
        from services.order.order_service import Order, OrderItem, DeliveryZone
        from services.delivery.delivery_service import Driver, DeliveryAssignment, DriverShift
        from services.kitchen.kitchen_service import KitchenStation, KitchenQueue, PrinterConfig
        from services.payment.payment_service import PaymentTransaction, PaymentConfig
        
        db.create_all()
        
        # Create default admin user if not exists
        from models import AdminUser, SiteSettings
        
        admin = AdminUser.query.filter_by(username='admin').first()
        if not admin:
            admin = AdminUser(
                username='admin',
                email='admin@sumo.com',
                is_superadmin=True
            )
            admin.set_password('admin123')  # Default password
            db.session.add(admin)
            db.session.commit()
            print("Created default admin user: admin / admin123")
        
        # Create default site settings if not exists
        settings = SiteSettings.query.first()
        if not settings:
            settings = SiteSettings()
            db.session.add(settings)
            db.session.commit()
            print("Created default site settings")

@login_manager.user_loader
def load_user(user_id):
    from models import AdminUser
    return AdminUser.query.get(int(user_id))