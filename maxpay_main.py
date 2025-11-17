"""
MAX PAY Payment Integration API
Flask REST API server for Max Pay payment processing
"""
from flask import Flask, request, jsonify
import logging
from config import Config
from services.maxpay import MaxPayService
from utils.security import verify_signature, extract_signature_from_header

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Max Pay service
maxpay_service = MaxPayService()


@app.route('/')
def index():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'service': 'Max Pay Integration API',
        'version': '1.0.0'
    })


@app.route('/create-payment', methods=['POST'])
def create_payment():
    """
    Create a new payment with Max Pay
    
    Request Body:
    {
        "order_id": "12345",
        "amount": 129.90
    }
    
    Response:
    {
        "payment_url": "https://..."
    }
    
    Or on error:
    {
        "error": true,
        "message": "..."
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            logger.warning("No JSON data received in /create-payment request")
            return jsonify({
                'error': True,
                'message': 'No JSON data provided'
            }), 400
        
        # Extract and validate parameters
        order_id = data.get('order_id')
        amount = data.get('amount')
        
        if not order_id:
            return jsonify({
                'error': True,
                'message': 'Missing required field: order_id'
            }), 400
        
        if not amount:
            return jsonify({
                'error': True,
                'message': 'Missing required field: amount'
            }), 400
        
        # Validate amount is a number
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return jsonify({
                'error': True,
                'message': 'Invalid amount. Must be a number.'
            }), 400
        
        logger.info(f"Processing payment creation request for order {order_id}")
        
        # Create payment with Max Pay
        result = maxpay_service.create_payment(order_id, amount)
        
        # Check if there was an error
        if result.get('error'):
            status_code = 500
            return jsonify(result), status_code
        
        # Return success response
        return jsonify({
            'payment_url': result.get('payment_url'),
            'order_id': result.get('order_id'),
            'amount': result.get('amount'),
            'transaction_id': result.get('transaction_id')
        }), 200
        
    except Exception as e:
        logger.error(f"Unexpected error in /create-payment: {str(e)}")
        return jsonify({
            'error': True,
            'message': f'Internal server error: {str(e)}'
        }), 500


@app.route('/webhook/max', methods=['POST'])
def webhook_max():
    """
    Handle webhooks from Max Pay
    
    Expected payload:
    {
        "orderId": "...",
        "transactionId": "...",
        "status": "approved" | "declined" | "error",
        "amount": 129.90
    }
    
    Max Pay should send a signature in headers for verification.
    Common header names: X-Max-Signature, X-Signature, Signature
    """
    try:
        # Get raw request body for signature verification
        raw_body = request.get_data()
        
        # Get signature from headers (try multiple header names)
        signature = (
            request.headers.get('X-Max-Signature') or
            request.headers.get('X-Signature') or
            request.headers.get('Signature') or
            request.headers.get('Max-Signature')
        )
        
        # Extract signature if it has a prefix like "sha256="
        if signature:
            signature = extract_signature_from_header(signature)
        
        # Verify signature if present
        if signature:
            is_valid = verify_signature(
                raw_body,
                signature,
                Config.MAX_WEBHOOK_SECRET
            )
            
            if not is_valid:
                logger.warning("Invalid webhook signature received")
                return jsonify({
                    'error': 'Invalid signature'
                }), 401
            
            logger.info("Webhook signature verified successfully")
        else:
            logger.warning("No signature found in webhook headers - proceeding without verification")
        
        # Parse JSON payload
        data = request.get_json()
        
        if not data:
            logger.error("No JSON data in webhook")
            return jsonify({
                'error': 'No JSON data'
            }), 400
        
        # Extract webhook data
        order_id = data.get('orderId') or data.get('order_id')
        transaction_id = data.get('transactionId') or data.get('transaction_id')
        status = data.get('status')
        amount = data.get('amount')
        
        logger.info(f"Webhook received - Order: {order_id}, Transaction: {transaction_id}, Status: {status}")
        
        # Process based on status
        if status == 'approved':
            logger.info(f"✓ ORDER PAID - Order ID: {order_id}, Amount: {amount} ILS")
            print(f"ORDER PAID - {order_id}")
            
            # Here you would typically:
            # 1. Update order status in database
            # 2. Send confirmation email
            # 3. Trigger fulfillment process
            # Example:
            # update_order_status(order_id, 'paid', transaction_id)
            
        elif status == 'declined':
            logger.warning(f"✗ ORDER FAILED - Order ID: {order_id}, Reason: Payment declined")
            print(f"ORDER FAILED - {order_id}")
            
            # Here you would typically:
            # 1. Update order status to failed
            # 2. Notify customer of payment failure
            # Example:
            # update_order_status(order_id, 'failed', transaction_id)
            
        elif status == 'error':
            logger.error(f"✗ ORDER ERROR - Order ID: {order_id}, Payment processing error")
            print(f"ORDER FAILED - {order_id}")
            
            # Handle error status
            # update_order_status(order_id, 'error', transaction_id)
            
        else:
            logger.warning(f"Unknown webhook status: {status} for order {order_id}")
        
        # Always return 200 OK to acknowledge receipt
        return jsonify({
            'status': 'received',
            'order_id': order_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        # Still return 200 to prevent Max Pay from retrying
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': True,
        'message': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'error': True,
        'message': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # Validate configuration
    try:
        Config.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        logger.warning("Some environment variables are missing. Please set them before production use.")
    
    # Run Flask app
    logger.info("Starting Max Pay Integration API on port 5000...")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG
    )
