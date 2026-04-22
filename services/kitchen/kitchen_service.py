"""
Kitchen Service - Order queue management and SNBC printer integration
"""
from flask import Blueprint, request, jsonify
from database import db
from datetime import datetime, timedelta
import json
import socket

kitchen_bp = Blueprint('kitchen', __name__, url_prefix='/api/kitchen')

class KitchenStation(db.Model):
    """Kitchen stations/screens"""
    __tablename__ = 'kitchen_stations'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)  # Main Kitchen, Sushi Bar, etc.
    station_type = db.Column(db.String(30))  # prep, grill, sushi, drinks, packing
    
    # Printer Settings
    printer_enabled = db.Column(db.Boolean, default=True)
    printer_ip = db.Column(db.String(15))
    printer_port = db.Column(db.Integer, default=9100)
    printer_model = db.Column(db.String(50), default='SNBC-BTP-R880NP')
    printer_width = db.Column(db.Integer, default=80)  # 80mm or 58mm
    
    # Display Settings
    auto_accept = db.Column(db.Boolean, default=True)
    sound_alerts = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_heartbeat = db.Column(db.DateTime)

class KitchenQueue(db.Model):
    """Order queue for kitchen"""
    __tablename__ = 'kitchen_queue'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    station_id = db.Column(db.Integer, db.ForeignKey('kitchen_stations.id'))
    
    # Queue Status
    status = db.Column(db.String(20), default='pending')  # pending, viewed, preparing, ready, served
    priority = db.Column(db.Integer, default=0)  # Higher = more urgent
    
    # Timing
    received_at = db.Column(db.DateTime, default=datetime.utcnow)
    viewed_at = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    estimated_minutes = db.Column(db.Integer, default=15)
    
    # Printing
    printed = db.Column(db.Boolean, default=False)
    printed_at = db.Column(db.DateTime)
    print_count = db.Column(db.Integer, default=0)

class PrinterConfig(db.Model):
    """SNBC Printer configuration"""
    __tablename__ = 'printer_configs'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    
    # Printer Settings
    name = db.Column(db.String(100))
    ip_address = db.Column(db.String(15))
    port = db.Column(db.Integer, default=9100)
    model = db.Column(db.String(50), default='SNBC-BTP-R880NP')
    
    # Paper Settings
    paper_width = db.Column(db.Integer, default=80)  # 80mm, 58mm
    dpi = db.Column(db.Integer, default=203)  # 203 DPI standard
    
    # Print Settings
    font_size_header = db.Column(db.Integer, default=2)  # 1-4 size multiplier
    font_size_body = db.Column(db.Integer, default=1)
    print_logo = db.Column(db.Boolean, default=True)
    logo_path = db.Column(db.String(500))
    
    # Cut Settings
    auto_cut = db.Column(db.Boolean, default=True)
    cut_type = db.Column(db.String(20), default='full')  # full, partial
    
    # Character Encoding
    encoding = db.Column(db.String(20), default='UTF-8')
    rtl_support = db.Column(db.Boolean, default=True)  # For Hebrew
    
    # Template
    receipt_template = db.Column(db.Text)  # Custom template
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_test = db.Column(db.DateTime)

class SNBCPrinter:
    """SNBC Printer driver for BTP-R880NP and similar models"""
    
    # ESC/POS Commands
    ESC = b'\x1b'
    GS = b'\x1d'
    
    # Basic Commands
    INIT = ESC + b'@'  # Initialize printer
    CUT_FULL = GS + b'V\x00'  # Full cut
    CUT_PARTIAL = GS + b'V\x01'  # Partial cut
    
    # Text Formatting
    ALIGN_LEFT = ESC + b'a\x00'
    ALIGN_CENTER = ESC + b'a\x01'
    ALIGN_RIGHT = ESC + b'a\x02'
    
    # Font Size
    FONT_NORMAL = ESC + b'!\x00'
    FONT_DOUBLE_HEIGHT = ESC + b'!\x10'
    FONT_DOUBLE_WIDTH = ESC + b'!\x20'
    FONT_DOUBLE = ESC + b'!\x30'
    
    # Barcode
    BARCODE_HEIGHT = GS + b'h'
    BARCODE_WIDTH = GS + b'w'
    BARCODE_CODE128 = GS + b'k\x08'
    
    def __init__(self, ip, port=9100, encoding='UTF-8'):
        self.ip = ip
        self.port = port
        self.encoding = encoding
        self.socket = None
    
    def connect(self):
        """Connect to printer"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.ip, self.port))
            return True
        except Exception as e:
            print(f"Printer connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from printer"""
        if self.socket:
            self.socket.close()
            self.socket = None
    
    def send(self, data):
        """Send data to printer"""
        if not self.socket:
            if not self.connect():
                return False
        try:
            self.socket.send(data)
            return True
        except Exception as e:
            print(f"Send failed: {e}")
            return False
    
    def print_text(self, text, align='left', size='normal'):
        """Print text with formatting"""
        # Set alignment
        if align == 'center':
            self.send(self.ALIGN_CENTER)
        elif align == 'right':
            self.send(self.ALIGN_RIGHT)
        else:
            self.send(self.ALIGN_LEFT)
        
        # Set size
        if size == 'double':
            self.send(self.FONT_DOUBLE)
        elif size == 'double_height':
            self.send(self.FONT_DOUBLE_HEIGHT)
        elif size == 'double_width':
            self.send(self.FONT_DOUBLE_WIDTH)
        else:
            self.send(self.FONT_NORMAL)
        
        # Send text
        self.send(text.encode(self.encoding))
        self.send(b'\n')
    
    def print_line(self, char='-', width=48):
        """Print separator line"""
        line = char * width
        self.print_text(line)
    
    def cut_paper(self, full=True):
        """Cut paper"""
        if full:
            self.send(self.CUT_FULL)
        else:
            self.send(self.CUT_PARTIAL)
    
    def print_order(self, order_data):
        """Print complete order receipt"""
        try:
            self.connect()
            self.send(self.INIT)  # Initialize
            
            # Header
            self.print_text(order_data.get('business_name', 'Restaurant'), 'center', 'double')
            self.print_text(f"Order #{order_data['order_number']}", 'center', 'double_height')
            self.print_line()
            
            # Order Type
            order_type = 'איסוף עצמי' if order_data['type'] == 'pickup' else 'משלוח'
            self.print_text(f"Type: {order_type}", 'left', 'normal')
            
            # Customer Info
            self.print_text(f"Name: {order_data['customer_name']}", 'left')
            self.print_text(f"Phone: {order_data['customer_phone']}", 'left')
            
            if order_data['type'] == 'delivery' and order_data.get('address'):
                self.print_text(f"Address: {order_data['address']}", 'left')
            
            self.print_line()
            
            # Items
            self.print_text("Items:", 'left', 'double_height')
            for item in order_data['items']:
                # Item name and quantity
                self.print_text(f"{item['quantity']}x {item['name']}", 'left')
                
                # Customizations
                if item.get('customizations'):
                    for custom in item['customizations']:
                        self.print_text(f"  - {custom}", 'left')
                
                # Special instructions
                if item.get('instructions'):
                    self.print_text(f"  Note: {item['instructions']}", 'left')
                
                # Price
                self.print_text(f"  ₪{item['total']:.2f}", 'right')
            
            self.print_line()
            
            # Totals
            self.print_text(f"Subtotal: ₪{order_data['subtotal']:.2f}", 'right')
            if order_data.get('delivery_fee'):
                self.print_text(f"Delivery: ₪{order_data['delivery_fee']:.2f}", 'right')
            self.print_text(f"Tax: ₪{order_data['tax']:.2f}", 'right')
            self.print_line()
            self.print_text(f"TOTAL: ₪{order_data['total']:.2f}", 'right', 'double')
            
            # Footer
            self.print_line()
            self.print_text(datetime.now().strftime('%Y-%m-%d %H:%M'), 'center')
            
            # Cut
            self.send(b'\n\n\n')
            self.cut_paper()
            
            self.disconnect()
            return True
            
        except Exception as e:
            print(f"Print error: {e}")
            self.disconnect()
            return False

@kitchen_bp.route('/queue', methods=['GET'])
def get_kitchen_queue():
    """Get current kitchen queue"""
    try:
        branch_id = request.args.get('branch_id')
        station_id = request.args.get('station_id')
        
        query = KitchenQueue.query.filter(
            KitchenQueue.status.in_(['pending', 'viewed', 'preparing'])
        )
        
        if station_id:
            query = query.filter_by(station_id=station_id)
        
        queue_items = query.order_by(
            KitchenQueue.priority.desc(),
            KitchenQueue.received_at
        ).all()
        
        result = []
        for item in queue_items:
            # Get order details
            from services.order.order_service import Order
            order = Order.query.get(item.order_id)
            
            result.append({
                'queue_id': item.id,
                'order_id': order.id,
                'order_number': order.order_number,
                'type': order.order_type,
                'status': item.status,
                'priority': item.priority,
                'items': len(order.items),
                'received': item.received_at.isoformat(),
                'estimated': item.estimated_minutes,
                'elapsed': int((datetime.utcnow() - item.received_at).total_seconds() / 60)
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@kitchen_bp.route('/print/<int:order_id>', methods=['POST'])
def print_order(order_id):
    """Print order to kitchen printer"""
    try:
        # Get order
        from services.order.order_service import Order
        order = Order.query.get_or_404(order_id)
        
        # Get printer config
        config = PrinterConfig.query.filter_by(
            branch_id=order.branch_id,
            is_active=True
        ).first()
        
        if not config:
            return jsonify({'error': 'No printer configured'}), 400
        
        # Prepare order data
        order_data = {
            'order_number': order.order_number,
            'type': order.order_type,
            'customer_name': order.customer_name,
            'customer_phone': order.customer_phone,
            'items': [{
                'name': item.item_name,
                'quantity': item.quantity,
                'total': item.total_price,
                'customizations': json.loads(item.customizations or '{}'),
                'instructions': item.special_instructions
            } for item in order.items],
            'subtotal': order.subtotal,
            'tax': order.tax_amount,
            'delivery_fee': order.delivery_fee,
            'total': order.total_amount
        }
        
        if order.order_type == 'delivery' and order.delivery_address:
            address = json.loads(order.delivery_address)
            order_data['address'] = f"{address.get('street')}, {address.get('city')}"
        
        # Print
        printer = SNBCPrinter(config.ip_address, config.port, config.encoding)
        success = printer.print_order(order_data)
        
        if success:
            # Update queue
            queue_item = KitchenQueue.query.filter_by(order_id=order_id).first()
            if queue_item:
                queue_item.printed = True
                queue_item.printed_at = datetime.utcnow()
                queue_item.print_count += 1
                db.session.commit()
        
        return jsonify({'success': success})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@kitchen_bp.route('/printer/test', methods=['POST'])
def test_printer():
    """Test printer connection"""
    try:
        data = request.json
        ip = data.get('ip')
        port = data.get('port', 9100)
        
        printer = SNBCPrinter(ip, port)
        if printer.connect():
            printer.send(printer.INIT)
            printer.print_text("PRINTER TEST", 'center', 'double')
            printer.print_line()
            printer.print_text("Connection successful!", 'center')
            printer.print_text(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'center')
            printer.send(b'\n\n\n')
            printer.cut_paper()
            printer.disconnect()
            
            return jsonify({'success': True, 'message': 'Test print sent'})
        else:
            return jsonify({'success': False, 'message': 'Connection failed'})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500