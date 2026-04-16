from flask import jsonify, request
from api.v1 import api_v1
from models import FoodOrder
import logging

logger = logging.getLogger(__name__)


@api_v1.route('/orders/<tracking_token>/track', methods=['GET'])
def track_order(tracking_token):
    order = FoodOrder.query.filter_by(tracking_token=tracking_token).first_or_404()
    return jsonify({
        'order_number': order.order_number,
        'status': order.status,
        'status_display_he': order.status_display_he,
        'order_type': order.order_type,
        'order_type_display_he': order.order_type_display_he,
        'total_amount': order.total_amount,
        'estimated_ready_at': order.estimated_ready_at.isoformat() if order.estimated_ready_at else None,
        'created_at': order.created_at.isoformat() if order.created_at else None,
    })
