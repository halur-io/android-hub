from app import app
from api_routes import api_bp

# Register API Blueprint
app.register_blueprint(api_bp)
