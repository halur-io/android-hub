"""
Delivery Service - Driver management, tracking, and zone configuration
"""
from flask import Blueprint, request, jsonify
from database import db
from datetime import datetime, timedelta
import json

delivery_bp = Blueprint('delivery', __name__, url_prefix='/api/delivery')

class Driver(db.Model):
    """Delivery drivers"""
    __tablename__ = 'drivers'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    
    # Driver Info
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120))
    photo_url = db.Column(db.String(500))
    
    # Vehicle Info
    vehicle_type = db.Column(db.String(20))  # bicycle, motorcycle, car
    vehicle_number = db.Column(db.String(20))
    license_number = db.Column(db.String(30))
    
    # Status
    status = db.Column(db.String(20), default='offline')  # offline, available, busy, break
    current_location = db.Column(db.Text)  # JSON with lat/lng
    last_location_update = db.Column(db.DateTime)
    
    # Performance
    total_deliveries = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=5.0)
    
    # Authentication
    auth_token = db.Column(db.String(100), unique=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Current orders
    active_orders = db.relationship('Order', backref='driver', lazy=True)

class DeliveryAssignment(db.Model):
    """Track delivery assignments"""
    __tablename__ = 'delivery_assignments'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    
    # Assignment Info
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    accepted_at = db.Column(db.DateTime)
    picked_up_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected, picked_up, delivered, cancelled
    
    # Tracking
    route = db.Column(db.Text)  # JSON array of location points
    distance_km = db.Column(db.Float)
    duration_minutes = db.Column(db.Integer)
    
    # Notes
    driver_notes = db.Column(db.Text)
    customer_feedback = db.Column(db.Text)
    rating = db.Column(db.Integer)  # 1-5 stars

class DriverShift(db.Model):
    """Driver shift management"""
    __tablename__ = 'driver_shifts'
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    
    # Shift Times
    scheduled_start = db.Column(db.DateTime)
    scheduled_end = db.Column(db.DateTime)
    actual_start = db.Column(db.DateTime)
    actual_end = db.Column(db.DateTime)
    
    # Stats
    deliveries_completed = db.Column(db.Integer, default=0)
    total_distance_km = db.Column(db.Float, default=0)
    total_tips = db.Column(db.Float, default=0)
    
    # Status
    status = db.Column(db.String(20), default='scheduled')  # scheduled, active, completed, cancelled

@delivery_bp.route('/drivers', methods=['GET'])
def get_drivers():
    """Get all drivers or filter by branch/status"""
    try:
        branch_id = request.args.get('branch_id')
        status = request.args.get('status')
        
        query = Driver.query.filter_by(is_active=True)
        
        if branch_id:
            query = query.filter_by(branch_id=branch_id)
        if status:
            query = query.filter_by(status=status)
        
        drivers = query.all()
        
        result = []
        for driver in drivers:
            result.append({
                'id': driver.id,
                'name': f"{driver.first_name} {driver.last_name}",
                'phone': driver.phone,
                'status': driver.status,
                'vehicle': driver.vehicle_type,
                'rating': driver.rating,
                'total_deliveries': driver.total_deliveries,
                'current_location': json.loads(driver.current_location or '{}'),
                'active_orders': len(driver.active_orders)
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@delivery_bp.route('/drivers/<int:driver_id>/status', methods=['PUT'])
def update_driver_status(driver_id):
    """Update driver status and location"""
    try:
        driver = Driver.query.get_or_404(driver_id)
        data = request.json
        
        # Verify auth token
        if request.headers.get('X-Driver-Token') != driver.auth_token:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Update status
        if 'status' in data:
            driver.status = data['status']
            driver.last_active = datetime.utcnow()
        
        # Update location
        if 'location' in data:
            driver.current_location = json.dumps(data['location'])
            driver.last_location_update = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'status': driver.status})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@delivery_bp.route('/assign', methods=['POST'])
def assign_delivery():
    """Assign order to driver"""
    try:
        data = request.json
        order_id = data['order_id']
        driver_id = data.get('driver_id')
        
        # Auto-assign if no driver specified
        if not driver_id:
            # Find nearest available driver
            drivers = Driver.query.filter_by(
                status='available',
                is_active=True
            ).all()
            
            if not drivers:
                return jsonify({'error': 'No available drivers'}), 400
            
            # TODO: Calculate distances and find nearest
            driver_id = drivers[0].id
        
        # Create assignment
        assignment = DeliveryAssignment(
            order_id=order_id,
            driver_id=driver_id
        )
        db.session.add(assignment)
        
        # Update driver status
        driver = Driver.query.get(driver_id)
        driver.status = 'busy'
        
        # Update order
        from services.order.order_service import Order
        order = Order.query.get(order_id)
        order.driver_id = driver_id
        order.update_status('assigned', f'Assigned to {driver.first_name}')
        
        db.session.commit()
        
        # TODO: Send notification to driver
        
        return jsonify({
            'success': True,
            'assignment_id': assignment.id,
            'driver': {
                'id': driver.id,
                'name': f"{driver.first_name} {driver.last_name}",
                'phone': driver.phone
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@delivery_bp.route('/zones', methods=['GET'])
def get_delivery_zones():
    """Get delivery zones for a branch"""
    try:
        branch_id = request.args.get('branch_id')
        
        if not branch_id:
            return jsonify({'error': 'Branch ID required'}), 400
        
        from services.order.order_service import DeliveryZone
        zones = DeliveryZone.query.filter_by(
            branch_id=branch_id,
            is_active=True
        ).all()
        
        result = []
        for zone in zones:
            result.append({
                'id': zone.id,
                'name': zone.name,
                'description': zone.description,
                'delivery_fee': zone.delivery_fee,
                'minimum_order': zone.minimum_order,
                'free_delivery_above': zone.free_delivery_above,
                'estimated_minutes': zone.estimated_minutes,
                'zone_data': json.loads(zone.zone_data or '{}')
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@delivery_bp.route('/zones', methods=['POST'])
def create_delivery_zone():
    """Create new delivery zone"""
    try:
        data = request.json
        
        from services.order.order_service import DeliveryZone
        zone = DeliveryZone(
            branch_id=data['branch_id'],
            name=data['name'],
            description=data.get('description'),
            zone_data=json.dumps(data.get('zone_data', {})),
            delivery_fee=data.get('delivery_fee', 0),
            minimum_order=data.get('minimum_order', 0),
            free_delivery_above=data.get('free_delivery_above'),
            estimated_minutes=data.get('estimated_minutes', 30)
        )
        
        db.session.add(zone)
        db.session.commit()
        
        return jsonify({'success': True, 'zone_id': zone.id})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@delivery_bp.route('/track/<int:order_id>', methods=['GET'])
def track_delivery(order_id):
    """Track delivery status and location"""
    try:
        assignment = DeliveryAssignment.query.filter_by(order_id=order_id).first()
        
        if not assignment:
            return jsonify({'error': 'No delivery assigned'}), 404
        
        driver = Driver.query.get(assignment.driver_id)
        
        return jsonify({
            'status': assignment.status,
            'driver': {
                'name': f"{driver.first_name} {driver.last_name}",
                'phone': driver.phone,
                'photo': driver.photo_url,
                'vehicle': driver.vehicle_type,
                'rating': driver.rating
            },
            'location': json.loads(driver.current_location or '{}'),
            'last_update': driver.last_location_update.isoformat() if driver.last_location_update else None,
            'timeline': {
                'assigned': assignment.assigned_at.isoformat(),
                'accepted': assignment.accepted_at.isoformat() if assignment.accepted_at else None,
                'picked_up': assignment.picked_up_at.isoformat() if assignment.picked_up_at else None,
                'delivered': assignment.delivered_at.isoformat() if assignment.delivered_at else None
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500