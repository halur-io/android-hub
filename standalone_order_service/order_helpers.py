import re
from models import MenuItem, BranchMenuItem, Deal, MenuItemOptionChoice


def sanitize_phone(phone_str):
    return re.sub(r'[^\d+\-() ]', '', (phone_str or '').strip())[:20]


def validate_phone_digits(phone_str):
    digits = re.sub(r'\D', '', phone_str)
    return 9 <= len(digits) <= 15


def get_branch_price(item, branch_id):
    if not branch_id:
        return item.base_price
    override = BranchMenuItem.query.filter_by(
        branch_id=branch_id, menu_item_id=item.id
    ).first()
    if override and override.custom_price is not None:
        return override.custom_price
    return item.base_price


def is_item_available_for_branch(item_id, branch_id):
    if not branch_id:
        return True
    override = BranchMenuItem.query.filter_by(
        branch_id=branch_id, menu_item_id=item_id
    ).first()
    if override is not None:
        return override.is_available
    item = MenuItem.query.get(item_id)
    return item.is_available if item else False


def verify_cart_items(cart, branch_id):
    from models import GlobalOptionChoice
    verified_subtotal = 0.0
    valid_cart = []

    for ci in cart:
        ci_id = ci.get('id')
        if not ci_id:
            continue

        if ci.get('is_deal'):
            result = _verify_deal_item(ci, ci_id, branch_id)
            if result:
                verified_subtotal += result['subtotal']
                valid_cart.append(result['item'])
            continue

        try:
            db_item = MenuItem.query.get(int(ci_id))
        except (ValueError, TypeError):
            continue
        if not db_item or not db_item.is_available:
            continue
        if branch_id and not is_item_available_for_branch(db_item.id, branch_id):
            continue

        item_price = get_branch_price(db_item, branch_id)
        qty = max(1, min(99, int(ci.get('qty', 1))))
        ci['qty'] = qty

        options_extra = 0.0
        item_options = ci.get('options', [])
        verified_options = []
        for opt in item_options:
            cid = opt.get('choice_id')
            if cid:
                if str(cid).startswith('g_') or opt.get('is_global'):
                    gc = GlobalOptionChoice.query.get(int(str(cid).replace('g_', '')))
                    if gc and gc.is_available:
                        verified_options.append({
                            'choice_id': gc.id,
                            'choice_name_he': gc.name_he,
                            'price_modifier': gc.price_modifier or 0,
                            'is_global': True,
                        })
                        options_extra += gc.price_modifier or 0
                else:
                    try:
                        ch = MenuItemOptionChoice.query.get(int(cid))
                    except (ValueError, TypeError):
                        continue
                    if ch and ch.is_available:
                        verified_options.append({
                            'choice_id': ch.id,
                            'choice_name_he': ch.name_he,
                            'price_modifier': ch.price_modifier or 0,
                        })
                        options_extra += ch.price_modifier or 0

        ci['options'] = verified_options
        ci['price'] = float(item_price) + options_extra
        ci['base_price'] = float(item_price)
        ci['name_he'] = db_item.name_he
        ci['name_en'] = db_item.name_en or ''
        ci['category_id'] = db_item.category_id
        verified_subtotal += ci['price'] * qty
        valid_cart.append(ci)

    return valid_cart, verified_subtotal


def _verify_deal_item(ci, ci_id, branch_id):
    deal_id_str = str(ci_id).replace('deal_', '')
    try:
        deal_obj = Deal.query.get(int(deal_id_str))
    except (ValueError, TypeError):
        return None
    if not deal_obj or not deal_obj.is_valid():
        return None

    qty = max(1, min(99, int(ci.get('qty', 1))))
    ci['qty'] = qty
    ci['price'] = float(deal_obj.deal_price)
    ci['deal_id'] = deal_obj.id
    ci['name_he'] = deal_obj.name_he
    ci['name_en'] = deal_obj.name_en or ''

    if getattr(deal_obj, 'deal_type', 'fixed') == 'customer_picks':
        ci['deal_type'] = 'customer_picks'
        ci['qty'] = 1
        selected = ci.get('selected_items', [])
        verified_selected = []
        pick_count = getattr(deal_obj, 'pick_count', 0) or 0
        source_cats = getattr(deal_obj, 'effective_category_ids', [])
        if not source_cats:
            source_cat = getattr(deal_obj, 'source_category_id', None)
            source_cats = [source_cat] if source_cat else []
        if pick_count < 1 or not source_cats:
            return None
        total_picked = 0
        for sel in selected:
            sel_id = sel.get('item_id')
            sel_qty = max(1, int(sel.get('qty', 1)))
            if sel_id:
                sel_item = MenuItem.query.get(int(sel_id))
                if sel_item and sel_item.is_available and sel_item.category_id in source_cats:
                    if branch_id and not is_item_available_for_branch(sel_item.id, branch_id):
                        continue
                    verified_selected.append({
                        'item_id': sel_item.id,
                        'qty': sel_qty,
                        'name_he': sel_item.name_he,
                        'name_en': sel_item.name_en or '',
                    })
                    total_picked += sel_qty
        if total_picked != pick_count:
            return None
        ci['selected_items'] = verified_selected
        ci['included_items'] = []
    else:
        ci['included_items'] = deal_obj.included_items or []

    return {
        'item': ci,
        'subtotal': deal_obj.deal_price * ci['qty'],
    }


def calculate_delivery_fee(order_type, subtotal, delivery_zone_id, branch_id, settings):
    from services.order.order_service import DeliveryZone
    delivery_fee = 0.0
    delivery_zone = None
    min_order_error = None

    if order_type != 'delivery':
        return delivery_fee, None

    if delivery_zone_id:
        try:
            dz_q = DeliveryZone.query.filter_by(id=int(delivery_zone_id), is_active=True)
            if branch_id:
                from sqlalchemy import or_
                dz_q = dz_q.filter(
                    or_(DeliveryZone.branch_id == branch_id, DeliveryZone.branch_id.is_(None))
                )
            delivery_zone = dz_q.first()
        except (ValueError, TypeError):
            delivery_zone = None

    if delivery_zone:
        min_order = delivery_zone.minimum_order or 0
        if subtotal < min_order:
            min_order_error = f"הזמנה מינימלית ל{delivery_zone.city_name} היא ₪{int(min_order)}."
            return 0.0, min_order_error
        free_above = delivery_zone.free_delivery_above or 0
        delivery_fee = 0.0 if (free_above > 0 and subtotal >= free_above) else (delivery_zone.delivery_fee or 0)
    else:
        delivery_fee_setting = getattr(settings, 'delivery_fee', 15.0) if settings else 15.0
        free_threshold = getattr(settings, 'free_delivery_threshold', 100.0) if settings else 100.0
        delivery_fee = 0.0 if subtotal >= free_threshold else delivery_fee_setting

    return delivery_fee, None
