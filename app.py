import os
import logging
import time
from flask import Flask, make_response
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from database import init_db

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Configure Flask-Mail
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587'))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@sumo-restaurant.co.il')

# Initialize extensions
mail = Mail(app)
csrf = CSRFProtect(app)
# Exempt admin API endpoints from CSRF
csrf.exempt('admin.toggle_dietary_property')
csrf.exempt('admin.delete_dietary_property')
csrf.exempt('admin.toggle_deal')
csrf.exempt('admin.delete_deal')
csrf.exempt('admin.toggle_upsell_rule')
csrf.exempt('admin.delete_upsell_rule')

# Exempt menu parsing routes from CSRF
csrf.exempt('admin.parse_word_menu')
csrf.exempt('admin.process_menu_selection')
csrf.exempt('admin.parse_word_menu_demo')

# Exempt gallery upload from CSRF (uses custom CSRF handling)
csrf.exempt('admin.upload_single_gallery')
csrf.exempt('admin.upload_media')

# Exempt API blueprint from CSRF
try:
    from api_routes import api_bp
    app.register_blueprint(api_bp)
    csrf.exempt(api_bp)
    logging.info("API blueprint registered and exempted from CSRF")
except Exception as e:
    logging.error(f"Error registering API blueprint: {e}")


# Initialize Flask-Login
from flask_login import LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'admin.login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    from models import AdminUser
    return AdminUser.query.get(int(user_id))

# Initialize database
init_db(app)

# Add cache busting for static files
@app.after_request
def add_cache_control_headers(response):
    # Add cache busting headers for HTML pages to prevent caching
    if response.content_type and 'text/html' in response.content_type:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

# Add version for cache busting
app.config['CACHE_BUSTER'] = str(int(time.time()))

# Make cache buster available in templates
@app.context_processor
def inject_cache_buster():
    return dict(cache_version=app.config['CACHE_BUSTER'])

# Make site settings available in all templates
@app.context_processor
def inject_site_settings():
    from models import SiteSettings
    try:
        settings = SiteSettings.query.first()
        if not settings:
            settings = SiteSettings()
        return dict(site_settings=settings)
    except:
        return dict(site_settings=None)

# Make permission functions available in templates
@app.context_processor
def inject_permissions():
    from permissions import has_permission, has_role, has_any_permission
    return dict(
        has_permission=has_permission,
        has_role=has_role,
        has_any_permission=has_any_permission
    )

# Add custom Jinja2 filters
import json

@app.template_filter('fromjson')
def fromjson_filter(value):
    """Convert JSON string to Python object"""
    if not value or value == '[]' or value == '{}':
        return []
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []

# Import routes  
from routes import *
# Note: Popup API routes are exempted from CSRF using decorators in routes.py

# Register admin blueprint
try:
    from admin_routes import admin_bp
    app.register_blueprint(admin_bp)
    # Exempt quick supplier creation from CSRF (already protected by login/permissions)
    csrf.exempt('admin.quick_create_supplier')
    # Exempt bulk operations from CSRF (protected by login + permissions)
    csrf.exempt('admin.bulk_delete_items')
    csrf.exempt('admin.bulk_delete_suppliers')
    csrf.exempt('admin.bulk_delete_categories')
    csrf.exempt('admin.bulk_edit_items')
    logging.info("Admin bulk operations exempted from CSRF")
except Exception as e:
    print(f"Error registering admin blueprint: {e}")

# Register microservices blueprints
try:
    from services.config.config_service import config_bp
    from services.auth.auth_service import auth_bp
    from services.order.order_service import order_bp as microservice_order_bp
    from services.delivery.delivery_service import delivery_bp
    from services.kitchen.kitchen_service import kitchen_bp
    from services.payment.payment_service import payment_bp
    
    app.register_blueprint(config_bp)
    csrf.exempt(auth_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(microservice_order_bp)
    app.register_blueprint(delivery_bp)
    app.register_blueprint(kitchen_bp)
    app.register_blueprint(payment_bp)
    
    logging.info("All microservices registered successfully")
except Exception as e:
    logging.error(f"Error registering microservices: {e}")

# Register standalone order service (public ordering + KDS dashboard)
try:
    from models import (
        Branch, BranchMenuItem, WorkingHours, MenuCategory, MenuItem, MenuItemPrice,
        MenuItemOptionGroup, MenuItemOptionChoice, FoodOrder, FoodOrderItem,
        ManagerPIN, SiteSettings, Coupon, CouponUsage, Deal, UpsellRule
    )
    from services.order.order_service import DeliveryZone
    from database import db as order_db

    order_models = {
        'Branch': Branch,
        'BranchMenuItem': BranchMenuItem,
        'WorkingHours': WorkingHours,
        'MenuCategory': MenuCategory,
        'MenuItem': MenuItem,
        'MenuItemPrice': MenuItemPrice,
        'MenuItemOptionGroup': MenuItemOptionGroup,
        'MenuItemOptionChoice': MenuItemOptionChoice,
        'DeliveryZone': DeliveryZone,
        'FoodOrder': FoodOrder,
        'FoodOrderItem': FoodOrderItem,
        'ManagerPIN': ManagerPIN,
        'SiteSettings': SiteSettings,
        'Coupon': Coupon,
        'CouponUsage': CouponUsage,
        'Deal': Deal,
        'UpsellRule': UpsellRule,
    }

    def get_site_settings():
        return SiteSettings.query.first()

    from standalone_order_service.sms_helpers import create_sender_from_env
    send_sms_fn = create_sender_from_env()

    from standalone_order_service.notifications import OrderNotifier
    notifier = OrderNotifier(
        send_sms=send_sms_fn,
        send_telegram=None,
    )

    from standalone_order_service.hyp_payment import HYPPayment
    hyp = HYPPayment()

    from standalone_order_service.order_routes import create_order_blueprint
    food_order_bp = create_order_blueprint(
        db=order_db,
        models=order_models,
        notifier=notifier,
        hyp_payment=hyp,
        get_settings=get_site_settings,
    )
    app.register_blueprint(food_order_bp)
    with app.app_context():
        csrf.exempt(app.view_functions.get('order_page.validate_coupon', lambda: None))
        csrf.exempt(app.view_functions.get('order_page.upsell_suggestions', lambda: None))

    from standalone_order_service.kds_routes import create_kds_blueprint
    kds_bp = create_kds_blueprint(
        db=order_db,
        models=order_models,
        send_sms=send_sms_fn,
        get_settings=get_site_settings,
        clear_cache=None,
    )
    app.register_blueprint(kds_bp)
    csrf.exempt(kds_bp)

    logging.info("Standalone order service registered: /order and /order-dashboard")
except Exception as e:
    logging.error(f"Error registering standalone order service: {e}")
    import traceback
    traceback.print_exc()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
