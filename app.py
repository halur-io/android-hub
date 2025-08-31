import os
import logging
from flask import Flask
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

# Initialize database
init_db(app)

# Import routes  
from routes import *

# Register admin blueprint
try:
    from admin_routes import admin_bp
    app.register_blueprint(admin_bp)
except Exception as e:
    print(f"Error registering admin blueprint: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
