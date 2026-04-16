from flask import jsonify, request
from api.v1 import api_v1
from models import Branch, WorkingHours
import logging

logger = logging.getLogger(__name__)


@api_v1.route('/branches', methods=['GET'])
def get_branches():
    branches = Branch.query.filter_by(is_active=True).order_by(Branch.display_order).all()
    result = []
    for b in branches:
        hours = []
        for wh in b.working_hours:
            hours.append({
                'day_of_week': wh.day_of_week,
                'open_time': wh.open_time,
                'close_time': wh.close_time,
                'is_closed': wh.is_closed,
            })
        result.append({
            'id': b.id,
            'name_he': b.name_he,
            'name_en': b.name_en,
            'address_he': b.address_he,
            'address_en': b.address_en,
            'phone': b.phone,
            'email': b.email,
            'waze_link': b.waze_link,
            'google_maps_link': b.google_maps_link,
            'enable_delivery': b.enable_delivery,
            'enable_pickup': b.enable_pickup,
            'ordering_status': b.ordering_status,
            'working_hours': hours,
        })
    return jsonify({'branches': result})


@api_v1.route('/branches/<int:branch_id>', methods=['GET'])
def get_branch(branch_id):
    b = Branch.query.get_or_404(branch_id)
    hours = []
    for wh in b.working_hours:
        hours.append({
            'day_of_week': wh.day_of_week,
            'open_time': wh.open_time,
            'close_time': wh.close_time,
            'is_closed': wh.is_closed,
        })
    return jsonify({
        'id': b.id,
        'name_he': b.name_he,
        'name_en': b.name_en,
        'address_he': b.address_he,
        'address_en': b.address_en,
        'phone': b.phone,
        'email': b.email,
        'waze_link': b.waze_link,
        'google_maps_link': b.google_maps_link,
        'enable_delivery': b.enable_delivery,
        'enable_pickup': b.enable_pickup,
        'ordering_status': b.ordering_status,
        'working_hours': hours,
    })
