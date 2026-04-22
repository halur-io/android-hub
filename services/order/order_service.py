"""
Order Service - Core ordering functionality with branch selection
"""
from flask import Blueprint, request, jsonify
from database import db
from datetime import datetime, timedelta
import json
import uuid

order_bp = Blueprint('order', __name__, url_prefix='/api/orders')

class Order(db.Model):
    """Main order table"""
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    
    # Order Type
    order_type = db.Column(db.String(20), nullable=False)  # delivery, pickup
    
    # Status Management
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, preparing, ready, out_for_delivery, delivered, cancelled
    status_history = db.Column(db.Text)  # JSON array of status changes
    
    # Customer Info (for guest orders)
    customer_name = db.Column(db.String(100))
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_email = db.Column(db.String(120))
    
    # Delivery Info
    delivery_address = db.Column(db.Text)  # JSON object
    delivery_zone_id = db.Column(db.Integer, db.ForeignKey('delivery_zones.id'))
    delivery_fee = db.Column(db.Float, default=0)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'))
    
    # Pickup Info
    pickup_time = db.Column(db.DateTime)
    
    # Pricing
    subtotal = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, default=0)
    discount_amount = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, nullable=False)
    
    # Payment
    payment_method = db.Column(db.String(30))  # credit_card, cash, bit, apple_pay, google_pay
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed, refunded
    transaction_id = db.Column(db.String(100))
    
    # Timing
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime)
    preparing_at = db.Column(db.DateTime)
    ready_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    estimated_time = db.Column(db.DateTime)
    
    # Notes
    customer_notes = db.Column(db.Text)
    kitchen_notes = db.Column(db.Text)
    driver_notes = db.Column(db.Text)
    
    # Metadata
    source = db.Column(db.String(20), default='website')  # website, app, phone, pos
    device_info = db.Column(db.Text)  # JSON object with browser/device details
    
    # Relations
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def generate_order_number(self):
        """Generate unique order number"""
        timestamp = datetime.now().strftime('%y%m%d')
        random_part = str(uuid.uuid4())[:4].upper()
        return f"{timestamp}-{random_part}"
    
    def update_status(self, new_status, notes=None):
        """Update order status with history tracking"""
        history = json.loads(self.status_history or '[]')
        history.append({
            'status': new_status,
            'timestamp': datetime.utcnow().isoformat(),
            'notes': notes
        })
        self.status_history = json.dumps(history)
        self.status = new_status
        
        # Update timestamps
        if new_status == 'confirmed':
            self.confirmed_at = datetime.utcnow()
        elif new_status == 'preparing':
            self.preparing_at = datetime.utcnow()
        elif new_status == 'ready':
            self.ready_at = datetime.utcnow()
        elif new_status == 'delivered':
            self.delivered_at = datetime.utcnow()

class OrderItem(db.Model):
    """Order items with customizations"""
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    
    # Item Details
    item_name = db.Column(db.String(200), nullable=False)  # Snapshot at order time
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    
    # Customizations
    customizations = db.Column(db.Text)  # JSON object with modifications
    special_instructions = db.Column(db.Text)
    
    # For combo/deals
    is_combo_item = db.Column(db.Boolean, default=False)
    combo_id = db.Column(db.Integer)

class DeliveryZone(db.Model):
    """Delivery zones with different fees"""
    __tablename__ = 'delivery_zones'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)  # Optional - can be restaurant-wide
    
    # Zone Information
    city_name = db.Column(db.String(100), nullable=False)  # e.g., "Karmiel", "Sakhnin", "Acre"
    name = db.Column(db.String(100))  # Optional custom zone name
    description = db.Column(db.Text)
    
    # Zone Definition (polygon coordinates or city names)
    zone_data = db.Column(db.Text)  # JSON object for advanced features
    
    # Pricing
    delivery_fee = db.Column(db.Float, default=0)
    minimum_order = db.Column(db.Float, default=0)
    free_delivery_above = db.Column(db.Float)
    
    # Time
    estimated_minutes = db.Column(db.Integer, default=30)
    estimated_delivery_time = db.Column(db.String(50))  # e.g., "30-45 דקות"
    
    # Settings
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<DeliveryZone {self.city_name}: {self.delivery_fee}₪>'

@order_bp.route('/create', methods=['POST'])
def create_order():
    """Create new order"""
    try:
        data = request.json
        
        # Create order
        order = Order(
            branch_id=data['branch_id'],
            customer_id=data.get('customer_id'),
            order_type=data['order_type'],
            customer_name=data.get('customer_name'),
            customer_phone=data['customer_phone'],
            customer_email=data.get('customer_email'),
            subtotal=0,
            total_amount=0
        )
        
        # Generate order number
        order.order_number = order.generate_order_number()
        
        # Handle delivery address
        if data['order_type'] == 'delivery':
            order.delivery_address = json.dumps(data.get('delivery_address', {}))
            order.delivery_zone_id = data.get('delivery_zone_id')
            
            # Calculate delivery fee
            if order.delivery_zone_id:
                zone = DeliveryZone.query.get(order.delivery_zone_id)
                if zone:
                    order.delivery_fee = zone.delivery_fee
                    order.estimated_time = datetime.utcnow() + timedelta(minutes=zone.estimated_minutes)
        else:
            # Pickup order
            order.pickup_time = datetime.fromisoformat(data.get('pickup_time'))
            order.estimated_time = order.pickup_time
        
        # Add items
        subtotal = 0
        for item_data in data.get('items', []):
            item = OrderItem(
                menu_item_id=item_data['menu_item_id'],
                item_name=item_data['name'],
                quantity=item_data['quantity'],
                unit_price=item_data['price'],
                total_price=item_data['price'] * item_data['quantity'],
                customizations=json.dumps(item_data.get('customizations', {})),
                special_instructions=item_data.get('special_instructions')
            )
            order.items.append(item)
            subtotal += item.total_price
        
        # Calculate totals
        order.subtotal = subtotal
        order.tax_amount = subtotal * 0.17  # Configurable tax rate
        order.total_amount = subtotal + order.tax_amount + order.delivery_fee
        
        # Set payment info
        order.payment_method = data.get('payment_method', 'cash')
        
        # Customer notes
        order.customer_notes = data.get('notes')
        
        # Device info
        order.device_info = json.dumps({
            'user_agent': request.headers.get('User-Agent'),
            'ip': request.remote_addr
        })
        
        db.session.add(order)
        db.session.commit()
        
        # TODO: Send notifications
        # TODO: Print to kitchen if auto_print enabled
        
        return jsonify({
            'success': True,
            'order_id': order.id,
            'order_number': order.order_number,
            'estimated_time': order.estimated_time.isoformat() if order.estimated_time else None,
            'total': order.total_amount
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@order_bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get order details"""
    try:
        order = Order.query.get_or_404(order_id)
        
        return jsonify({
            'id': order.id,
            'order_number': order.order_number,
            'status': order.status,
            'order_type': order.order_type,
            'branch_id': order.branch_id,
            'customer': {
                'name': order.customer_name,
                'phone': order.customer_phone,
                'email': order.customer_email
            },
            'items': [{
                'id': item.id,
                'name': item.item_name,
                'quantity': item.quantity,
                'price': item.unit_price,
                'total': item.total_price,
                'customizations': json.loads(item.customizations or '{}'),
                'instructions': item.special_instructions
            } for item in order.items],
            'pricing': {
                'subtotal': order.subtotal,
                'tax': order.tax_amount,
                'delivery_fee': order.delivery_fee,
                'discount': order.discount_amount,
                'total': order.total_amount
            },
            'payment': {
                'method': order.payment_method,
                'status': order.payment_status
            },
            'timing': {
                'created': order.created_at.isoformat(),
                'estimated': order.estimated_time.isoformat() if order.estimated_time else None
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_bp.route('/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Update order status"""
    try:
        order = Order.query.get_or_404(order_id)
        data = request.json
        
        new_status = data.get('status')
        notes = data.get('notes')
        
        order.update_status(new_status, notes)
        db.session.commit()
        
        # TODO: Send notifications based on status change
        
        return jsonify({'success': True, 'status': order.status})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@order_bp.route('/branch/<int:branch_id>/active', methods=['GET'])
def get_active_orders(branch_id):
    """Get active orders for kitchen display"""
    try:
        active_statuses = ['confirmed', 'preparing', 'ready']
        orders = Order.query.filter(
            Order.branch_id == branch_id,
            Order.status.in_(active_statuses)
        ).order_by(Order.created_at).all()
        
        result = []
        for order in orders:
            result.append({
                'id': order.id,
                'order_number': order.order_number,
                'type': order.order_type,
                'status': order.status,
                'items': len(order.items),
                'total': order.total_amount,
                'created': order.created_at.isoformat(),
                'estimated': order.estimated_time.isoformat() if order.estimated_time else None
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500