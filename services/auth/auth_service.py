"""
Auth Service - Phone verification, user management, JWT tokens
"""
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
import jwt
import random
import string
from datetime import datetime, timedelta
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

class Customer(db.Model):
    """Customer accounts with phone verification"""
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    phone_verified = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(120), unique=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    password_hash = db.Column(db.String(256))
    
    # Profile
    default_branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    language_preference = db.Column(db.String(5), default='he')
    
    # Addresses
    addresses = db.relationship('CustomerAddress', backref='customer', lazy=True, cascade='all, delete-orphan')
    
    # Preferences
    dietary_restrictions = db.Column(db.Text)  # JSON array
    marketing_consent = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_blocked = db.Column(db.Boolean, default=False)
    
    def generate_token(self):
        """Generate JWT token for authentication"""
        payload = {
            'customer_id': self.id,
            'phone': self.phone,
            'exp': datetime.utcnow() + timedelta(days=30)
        }
        return jwt.encode(payload, os.environ.get('JWT_SECRET', 'dev-secret'), algorithm='HS256')

class CustomerAddress(db.Model):
    """Customer delivery addresses"""
    __tablename__ = 'customer_addresses'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    label = db.Column(db.String(50))  # Home, Work, etc.
    street = db.Column(db.String(200), nullable=False)
    building = db.Column(db.String(20))
    apartment = db.Column(db.String(20))
    floor = db.Column(db.String(10))
    city = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PhoneVerification(db.Model):
    """OTP codes for phone verification"""
    __tablename__ = 'phone_verifications'
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.String(20))  # signup, login, password_reset
    attempts = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    verified_at = db.Column(db.DateTime)
    
    def is_valid(self):
        """Check if code is still valid"""
        return (
            self.expires_at > datetime.utcnow() and
            self.attempts < 3 and
            self.verified_at is None
        )

@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    """Send OTP code via SMS"""
    try:
        data = request.json
        phone = data.get('phone')
        purpose = data.get('purpose', 'login')
        
        if not phone:
            return jsonify({'error': 'Phone number required'}), 400
        
        # Generate 6-digit code
        code = ''.join(random.choices(string.digits, k=6))
        
        # Save verification record
        verification = PhoneVerification(
            phone=phone,
            code=code,
            purpose=purpose,
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        db.session.add(verification)
        db.session.commit()
        
        # TODO: Send SMS via Twilio/other provider
        # For now, return code in development mode
        if os.environ.get('ENVIRONMENT') == 'development':
            return jsonify({
                'success': True,
                'message': 'OTP sent',
                'dev_code': code  # Remove in production
            })
        
        return jsonify({'success': True, 'message': 'OTP sent to your phone'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP code and authenticate user"""
    try:
        data = request.json
        phone = data.get('phone')
        code = data.get('code')
        
        if not phone or not code:
            return jsonify({'error': 'Phone and code required'}), 400
        
        # Find latest verification
        verification = PhoneVerification.query.filter_by(
            phone=phone,
            code=code
        ).order_by(PhoneVerification.created_at.desc()).first()
        
        if not verification or not verification.is_valid():
            return jsonify({'error': 'Invalid or expired code'}), 400
        
        # Mark as verified
        verification.verified_at = datetime.utcnow()
        
        # Get or create customer
        customer = Customer.query.filter_by(phone=phone).first()
        if not customer:
            customer = Customer(phone=phone, phone_verified=True)
            db.session.add(customer)
        else:
            customer.phone_verified = True
            customer.last_login = datetime.utcnow()
        
        db.session.commit()
        
        # Generate JWT token
        token = customer.generate_token()
        
        return jsonify({
            'success': True,
            'token': token,
            'customer': {
                'id': customer.id,
                'phone': customer.phone,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'email': customer.email
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get customer profile"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        payload = jwt.decode(token, os.environ.get('JWT_SECRET', 'dev-secret'), algorithms=['HS256'])
        customer = Customer.query.get(payload['customer_id'])
        
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        return jsonify({
            'id': customer.id,
            'phone': customer.phone,
            'email': customer.email,
            'first_name': customer.first_name,
            'last_name': customer.last_name,
            'default_branch_id': customer.default_branch_id,
            'language_preference': customer.language_preference,
            'addresses': [{
                'id': addr.id,
                'label': addr.label,
                'street': addr.street,
                'city': addr.city,
                'is_default': addr.is_default
            } for addr in customer.addresses]
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Update customer profile"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        payload = jwt.decode(token, os.environ.get('JWT_SECRET', 'dev-secret'), algorithms=['HS256'])
        customer = Customer.query.get(payload['customer_id'])
        
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        data = request.json
        customer.first_name = data.get('first_name', customer.first_name)
        customer.last_name = data.get('last_name', customer.last_name)
        customer.email = data.get('email', customer.email)
        customer.default_branch_id = data.get('default_branch_id', customer.default_branch_id)
        customer.language_preference = data.get('language_preference', customer.language_preference)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Profile updated'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/addresses', methods=['POST'])
def add_address():
    """Add new delivery address"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        payload = jwt.decode(token, os.environ.get('JWT_SECRET', 'dev-secret'), algorithms=['HS256'])
        
        data = request.json
        address = CustomerAddress(
            customer_id=payload['customer_id'],
            label=data.get('label'),
            street=data.get('street'),
            building=data.get('building'),
            apartment=data.get('apartment'),
            floor=data.get('floor'),
            city=data.get('city'),
            notes=data.get('notes'),
            is_default=data.get('is_default', False)
        )
        
        # If setting as default, unset other defaults
        if address.is_default:
            CustomerAddress.query.filter_by(
                customer_id=payload['customer_id'],
                is_default=True
            ).update({'is_default': False})
        
        db.session.add(address)
        db.session.commit()
        
        return jsonify({'success': True, 'address_id': address.id})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500