from flask import jsonify, request
from api.v1 import api_v1
from models import MenuCategory, MenuItem, MenuSettings, DietaryProperty
import logging

logger = logging.getLogger(__name__)


@api_v1.route('/menu/categories', methods=['GET'])
def get_categories():
    branch_id = request.args.get('branch_id', type=int)
    categories = MenuCategory.query.filter_by(is_active=True).order_by(MenuCategory.display_order).all()
    result = []
    for cat in categories:
        result.append({
            'id': cat.id,
            'name_he': cat.name_he,
            'name_en': cat.name_en,
            'description_he': cat.description_he,
            'description_en': cat.description_en,
            'icon': cat.icon,
            'image_path': cat.image_path,
            'display_order': cat.display_order,
            'show_in_order': cat.show_in_order,
        })
    return jsonify({'categories': result})


@api_v1.route('/menu/items', methods=['GET'])
def get_items():
    category_id = request.args.get('category_id', type=int)
    query = MenuItem.query.filter_by(is_available=True)
    if category_id:
        query = query.filter_by(category_id=category_id)
    items = query.order_by(MenuItem.display_order).all()
    result = []
    for item in items:
        result.append({
            'id': item.id,
            'category_id': item.category_id,
            'name_he': item.name_he,
            'name_en': item.name_en,
            'description_he': item.description_he,
            'description_en': item.description_en,
            'base_price': item.base_price,
            'image_path': item.image_path,
            'is_vegetarian': item.is_vegetarian,
            'is_vegan': item.is_vegan,
            'is_gluten_free': item.is_gluten_free,
            'is_spicy': item.is_spicy,
            'spice_level': item.spice_level,
            'is_new': item.is_new,
            'is_popular': item.is_popular,
            'is_signature': item.is_signature,
            'show_in_order': item.show_in_order,
            'display_order': item.display_order,
        })
    return jsonify({'items': result})


@api_v1.route('/menu/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    option_groups = []
    for og in item.option_groups:
        if not og.is_active:
            continue
        choices = []
        for c in og.choices:
            if not c.is_available:
                continue
            choices.append({
                'id': c.id,
                'name_he': c.name_he,
                'name_en': c.name_en,
                'price_modifier': c.price_modifier,
                'is_default': c.is_default,
            })
        option_groups.append({
            'id': og.id,
            'name_he': og.name_he,
            'name_en': og.name_en,
            'selection_type': og.selection_type,
            'is_required': og.is_required,
            'min_selections': og.min_selections,
            'max_selections': og.max_selections,
            'choices': choices,
        })
    return jsonify({
        'id': item.id,
        'category_id': item.category_id,
        'name_he': item.name_he,
        'name_en': item.name_en,
        'description_he': item.description_he,
        'description_en': item.description_en,
        'base_price': item.base_price,
        'image_path': item.image_path,
        'option_groups': option_groups,
    })
