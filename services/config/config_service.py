"""
Configuration Service - Central settings management for all microservices
No hardcoded business logic - everything is configurable
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required
from database import db
import json
from datetime import datetime

config_bp = Blueprint('config', __name__, url_prefix='/api/config')

class SystemConfig(db.Model):
    """System-wide configuration settings"""
    __tablename__ = 'system_config'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    category = db.Column(db.String(50))  # general, payment, delivery, kitchen, etc.
    description = db.Column(db.Text)
    data_type = db.Column(db.String(20))  # string, number, boolean, json
    is_sensitive = db.Column(db.Boolean, default=False)  # Hide in logs
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.String(100))

class BranchConfig(db.Model):
    """Branch-specific configuration"""
    __tablename__ = 'branch_config'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Text)
    category = db.Column(db.String(50))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('branch_id', 'key'),)

# Default configuration template
DEFAULT_CONFIG = {
    'general': {
        'business_name': {'value': '', 'type': 'string', 'description': 'Business name'},
        'currency': {'value': '₪', 'type': 'string', 'description': 'Currency symbol'},
        'tax_rate': {'value': '17', 'type': 'number', 'description': 'Tax rate percentage'},
        'languages': {'value': '["he", "en"]', 'type': 'json', 'description': 'Supported languages'},
    },
    'order': {
        'auto_accept': {'value': 'true', 'type': 'boolean', 'description': 'Auto-accept orders'},
        'max_advance_days': {'value': '7', 'type': 'number', 'description': 'Max days for advance orders'},
        'order_statuses': {'value': '["received", "preparing", "ready", "delivered"]', 'type': 'json', 'description': 'Order status flow'},
        'cancellation_window': {'value': '5', 'type': 'number', 'description': 'Minutes to allow cancellation'},
    },
    'delivery': {
        'enabled': {'value': 'true', 'type': 'boolean', 'description': 'Enable delivery service'},
        'base_fee': {'value': '15', 'type': 'number', 'description': 'Base delivery fee'},
        'free_delivery_minimum': {'value': '100', 'type': 'number', 'description': 'Minimum for free delivery'},
        'max_distance_km': {'value': '10', 'type': 'number', 'description': 'Maximum delivery distance'},
        'estimated_time_minutes': {'value': '45', 'type': 'number', 'description': 'Default delivery time'},
    },
    'payment': {
        'provider': {'value': 'MAX', 'type': 'string', 'description': 'Payment gateway provider'},
        'methods': {'value': '["credit_card", "bit", "cash", "apple_pay", "google_pay"]', 'type': 'json', 'description': 'Accepted payment methods'},
        'require_prepayment': {'value': 'false', 'type': 'boolean', 'description': 'Require payment before preparation'},
    },
    'kitchen': {
        'auto_print': {'value': 'true', 'type': 'boolean', 'description': 'Auto-print orders'},
        'printer_type': {'value': 'SNBC', 'type': 'string', 'description': 'Printer manufacturer'},
        'prep_time_buffer': {'value': '10', 'type': 'number', 'description': 'Buffer time in minutes'},
        'max_concurrent_orders': {'value': '20', 'type': 'number', 'description': 'Max orders at once'},
    },
    'notification': {
        'sms_enabled': {'value': 'true', 'type': 'boolean', 'description': 'Enable SMS notifications'},
        'sms_provider': {'value': 'sms4free', 'type': 'string', 'description': 'SMS service provider'},
        'whatsapp_enabled': {'value': 'true', 'type': 'boolean', 'description': 'Enable WhatsApp notifications'},
        'email_enabled': {'value': 'true', 'type': 'boolean', 'description': 'Enable email notifications'},
        'real_time_updates': {'value': 'true', 'type': 'boolean', 'description': 'Enable WebSocket updates'},
    }
}

@config_bp.route('/get/<category>', methods=['GET'])
def get_config(category=None):
    """Get configuration by category or all"""
    try:
        if category:
            configs = SystemConfig.query.filter_by(category=category).all()
        else:
            configs = SystemConfig.query.all()
        
        result = {}
        for config in configs:
            if not config.is_sensitive or (config.is_sensitive and request.args.get('include_sensitive') == 'true'):
                value = config.value
                if config.data_type == 'json':
                    value = json.loads(value)
                elif config.data_type == 'number':
                    value = float(value)
                elif config.data_type == 'boolean':
                    value = value.lower() == 'true'
                
                if config.category not in result:
                    result[config.category] = {}
                result[config.category][config.key] = value
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@config_bp.route('/update', methods=['POST'])
@login_required
def update_config():
    """Update configuration settings"""
    try:
        data = request.json
        category = data.get('category')
        key = data.get('key')
        value = data.get('value')
        
        config = SystemConfig.query.filter_by(category=category, key=key).first()
        if not config:
            config = SystemConfig(category=category, key=key)
            db.session.add(config)
        
        # Convert value to string for storage
        if isinstance(value, (dict, list)):
            config.value = json.dumps(value)
            config.data_type = 'json'
        elif isinstance(value, bool):
            config.value = str(value).lower()
            config.data_type = 'boolean'
        elif isinstance(value, (int, float)):
            config.value = str(value)
            config.data_type = 'number'
        else:
            config.value = str(value)
            config.data_type = 'string'
        
        config.updated_at = datetime.utcnow()
        config.updated_by = request.args.get('user', 'system')
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Configuration updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@config_bp.route('/branch/<int:branch_id>', methods=['GET'])
def get_branch_config(branch_id):
    """Get branch-specific configuration"""
    try:
        configs = BranchConfig.query.filter_by(branch_id=branch_id).all()
        result = {}
        for config in configs:
            if config.category not in result:
                result[config.category] = {}
            result[config.category][config.key] = config.value
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@config_bp.route('/initialize', methods=['POST'])
@login_required
def initialize_config():
    """Initialize system with default configuration"""
    try:
        for category, settings in DEFAULT_CONFIG.items():
            for key, details in settings.items():
                existing = SystemConfig.query.filter_by(category=category, key=key).first()
                if not existing:
                    config = SystemConfig(
                        category=category,
                        key=key,
                        value=details['value'],
                        data_type=details['type'],
                        description=details['description']
                    )
                    db.session.add(config)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Configuration initialized'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500