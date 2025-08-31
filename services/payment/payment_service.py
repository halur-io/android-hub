"""
Payment Service - MAX gateway integration for Israeli payment methods
"""
from flask import Blueprint, request, jsonify
from database import db
from datetime import datetime
import json
import hashlib
import requests
import os

payment_bp = Blueprint('payment', __name__, url_prefix='/api/payment')

class PaymentTransaction(db.Model):
    """Payment transactions"""
    __tablename__ = 'payment_transactions'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    
    # Transaction Info
    transaction_id = db.Column(db.String(100), unique=True)
    gateway_reference = db.Column(db.String(100))
    
    # Amount
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='ILS')
    
    # Payment Method
    payment_method = db.Column(db.String(30))  # credit_card, bit, apple_pay, google_pay
    card_last_four = db.Column(db.String(4))
    card_brand = db.Column(db.String(20))  # Visa, Mastercard, Amex, etc.
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, processing, success, failed, refunded
    error_code = db.Column(db.String(20))
    error_message = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    # Response Data
    gateway_response = db.Column(db.Text)  # Full JSON response

class PaymentConfig(db.Model):
    """Payment gateway configuration"""
    __tablename__ = 'payment_configs'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    
    # MAX Gateway Settings
    merchant_id = db.Column(db.String(100))
    terminal_id = db.Column(db.String(100))
    api_key = db.Column(db.String(200))
    api_secret = db.Column(db.String(200))
    
    # Environment
    environment = db.Column(db.String(20), default='sandbox')  # sandbox, production
    gateway_url = db.Column(db.String(200))
    
    # Payment Methods
    enable_credit_card = db.Column(db.Boolean, default=True)
    enable_bit = db.Column(db.Boolean, default=True)
    enable_apple_pay = db.Column(db.Boolean, default=True)
    enable_google_pay = db.Column(db.Boolean, default=True)
    enable_cash = db.Column(db.Boolean, default=True)
    
    # Settings
    auto_capture = db.Column(db.Boolean, default=True)
    save_cards = db.Column(db.Boolean, default=False)
    require_cvv = db.Column(db.Boolean, default=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)

class MAXGateway:
    """MAX Payment Gateway integration for Israeli market"""
    
    def __init__(self, config):
        self.config = config
        self.base_url = config.gateway_url or 'https://api.max.co.il/v1'
        if config.environment == 'sandbox':
            self.base_url = 'https://sandbox.max.co.il/v1'
    
    def generate_signature(self, data):
        """Generate signature for API requests"""
        # MAX uses HMAC-SHA256 for request signing
        message = json.dumps(data, sort_keys=True)
        signature = hashlib.sha256(
            f"{message}{self.config.api_secret}".encode()
        ).hexdigest()
        return signature
    
    def process_payment(self, payment_data):
        """Process payment through MAX gateway"""
        try:
            # Prepare request
            request_data = {
                'merchantId': self.config.merchant_id,
                'terminalId': self.config.terminal_id,
                'amount': payment_data['amount'],
                'currency': 'ILS',
                'orderId': payment_data['order_id'],
                'customerName': payment_data['customer_name'],
                'customerPhone': payment_data['customer_phone'],
                'paymentMethod': payment_data['payment_method']
            }
            
            # Add payment method specific data
            if payment_data['payment_method'] == 'credit_card':
                request_data.update({
                    'cardNumber': payment_data.get('card_number'),
                    'expiryMonth': payment_data.get('expiry_month'),
                    'expiryYear': payment_data.get('expiry_year'),
                    'cvv': payment_data.get('cvv'),
                    'installments': payment_data.get('installments', 1)
                })
            elif payment_data['payment_method'] == 'bit':
                request_data.update({
                    'phoneNumber': payment_data['customer_phone'],
                    'bitReference': payment_data.get('bit_reference')
                })
            elif payment_data['payment_method'] in ['apple_pay', 'google_pay']:
                request_data.update({
                    'walletToken': payment_data.get('wallet_token')
                })
            
            # Add signature
            request_data['signature'] = self.generate_signature(request_data)
            
            # Send request
            headers = {
                'Content-Type': 'application/json',
                'X-API-Key': self.config.api_key
            }
            
            response = requests.post(
                f"{self.base_url}/payments/process",
                json=request_data,
                headers=headers,
                timeout=30
            )
            
            result = response.json()
            
            return {
                'success': result.get('status') == 'success',
                'transaction_id': result.get('transactionId'),
                'gateway_reference': result.get('referenceNumber'),
                'error_code': result.get('errorCode'),
                'error_message': result.get('errorMessage'),
                'response': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error_message': str(e)
            }
    
    def refund_payment(self, transaction_id, amount=None):
        """Refund a payment"""
        try:
            request_data = {
                'merchantId': self.config.merchant_id,
                'terminalId': self.config.terminal_id,
                'transactionId': transaction_id
            }
            
            if amount:
                request_data['amount'] = amount  # Partial refund
            
            request_data['signature'] = self.generate_signature(request_data)
            
            headers = {
                'Content-Type': 'application/json',
                'X-API-Key': self.config.api_key
            }
            
            response = requests.post(
                f"{self.base_url}/payments/refund",
                json=request_data,
                headers=headers,
                timeout=30
            )
            
            result = response.json()
            
            return {
                'success': result.get('status') == 'success',
                'refund_id': result.get('refundId'),
                'error_message': result.get('errorMessage')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error_message': str(e)
            }
    
    def check_status(self, transaction_id):
        """Check payment status"""
        try:
            params = {
                'merchantId': self.config.merchant_id,
                'transactionId': transaction_id
            }
            
            headers = {
                'X-API-Key': self.config.api_key
            }
            
            response = requests.get(
                f"{self.base_url}/payments/status",
                params=params,
                headers=headers,
                timeout=30
            )
            
            return response.json()
            
        except Exception as e:
            return {'error': str(e)}

@payment_bp.route('/process', methods=['POST'])
def process_payment():
    """Process payment for order"""
    try:
        data = request.json
        order_id = data['order_id']
        
        # Get order
        from services.order.order_service import Order
        order = Order.query.get_or_404(order_id)
        
        # Get payment config
        config = PaymentConfig.query.filter_by(
            branch_id=order.branch_id,
            is_active=True
        ).first()
        
        if not config:
            return jsonify({'error': 'Payment not configured'}), 400
        
        # Create transaction record
        transaction = PaymentTransaction(
            order_id=order_id,
            amount=order.total_amount,
            payment_method=data['payment_method'],
            status='processing'
        )
        db.session.add(transaction)
        db.session.commit()
        
        # Process through gateway
        gateway = MAXGateway(config)
        result = gateway.process_payment({
            'amount': order.total_amount,
            'order_id': order.order_number,
            'customer_name': order.customer_name,
            'customer_phone': order.customer_phone,
            'payment_method': data['payment_method'],
            **data.get('payment_details', {})
        })
        
        # Update transaction
        transaction.gateway_response = json.dumps(result.get('response', {}))
        transaction.status = 'success' if result['success'] else 'failed'
        transaction.transaction_id = result.get('transaction_id')
        transaction.gateway_reference = result.get('gateway_reference')
        transaction.error_code = result.get('error_code')
        transaction.error_message = result.get('error_message')
        transaction.processed_at = datetime.utcnow()
        
        # Update order
        if result['success']:
            order.payment_status = 'paid'
            order.transaction_id = transaction.transaction_id
            order.update_status('confirmed', 'Payment received')
        else:
            order.payment_status = 'failed'
        
        db.session.commit()
        
        return jsonify({
            'success': result['success'],
            'transaction_id': transaction.transaction_id,
            'error_message': transaction.error_message
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/methods', methods=['GET'])
def get_payment_methods():
    """Get available payment methods for branch"""
    try:
        branch_id = request.args.get('branch_id')
        
        if not branch_id:
            return jsonify({'error': 'Branch ID required'}), 400
        
        config = PaymentConfig.query.filter_by(
            branch_id=branch_id,
            is_active=True
        ).first()
        
        if not config:
            # Return default methods if not configured
            return jsonify({
                'methods': ['cash'],
                'default': 'cash'
            })
        
        methods = []
        if config.enable_credit_card:
            methods.append({
                'id': 'credit_card',
                'name': 'כרטיס אשראי',
                'icon': 'credit-card'
            })
        if config.enable_bit:
            methods.append({
                'id': 'bit',
                'name': 'Bit',
                'icon': 'mobile'
            })
        if config.enable_apple_pay:
            methods.append({
                'id': 'apple_pay',
                'name': 'Apple Pay',
                'icon': 'apple'
            })
        if config.enable_google_pay:
            methods.append({
                'id': 'google_pay',
                'name': 'Google Pay',
                'icon': 'google'
            })
        if config.enable_cash:
            methods.append({
                'id': 'cash',
                'name': 'מזומן',
                'icon': 'money-bill'
            })
        
        return jsonify({
            'methods': methods,
            'default': 'credit_card' if config.enable_credit_card else 'cash'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/refund', methods=['POST'])
def refund_payment():
    """Refund a payment"""
    try:
        data = request.json
        transaction_id = data['transaction_id']
        amount = data.get('amount')  # Optional for partial refund
        
        # Get transaction
        transaction = PaymentTransaction.query.filter_by(
            transaction_id=transaction_id
        ).first()
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        if transaction.status != 'success':
            return jsonify({'error': 'Cannot refund this transaction'}), 400
        
        # Get config
        from services.order.order_service import Order
        order = Order.query.get(transaction.order_id)
        config = PaymentConfig.query.filter_by(
            branch_id=order.branch_id,
            is_active=True
        ).first()
        
        # Process refund
        gateway = MAXGateway(config)
        result = gateway.refund_payment(transaction_id, amount)
        
        if result['success']:
            transaction.status = 'refunded'
            order.payment_status = 'refunded'
            db.session.commit()
        
        return jsonify(result)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500