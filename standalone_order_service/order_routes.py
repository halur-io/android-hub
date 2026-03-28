"""
Public-facing Food Order Routes (Blueprint).

Register this blueprint in your Flask app::

    from standalone_order_service.order_routes import create_order_blueprint
    order_bp = create_order_blueprint(db, models, notifier, hyp)
    app.register_blueprint(order_bp)

All templates live in ``standalone_order_service/templates/order/``.
"""

import json
import logging
import math
import re
import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, jsonify, session, abort,
)


def create_order_blueprint(db, models, notifier=None, hyp_payment=None, get_settings=None):
    """
    Factory that returns a configured Blueprint.

    Parameters
    ----------
    db : flask_sqlalchemy.SQLAlchemy
    models : dict
        Model classes returned by ``register_models(db)``.
    notifier : OrderNotifier, optional
    hyp_payment : HYPPayment, optional
    get_settings : callable, optional
        Returns a settings object with ordering-related fields.
    """
    bp = Blueprint(
        'order_page',
        __name__,
        template_folder='templates/order',
        static_folder='static',
        url_prefix='/order',
    )

    MenuItem = models['MenuItem']
    MenuCategory = models['MenuCategory']
    MenuItemOptionGroup = models['MenuItemOptionGroup']
    MenuItemOptionChoice = models['MenuItemOptionChoice']
    MenuItemPrice = models['MenuItemPrice']
    BranchMenuItem = models.get('BranchMenuItem')
    FoodOrder = models['FoodOrder']
    FoodOrderItem = models['FoodOrderItem']
    DeliveryZone = models['DeliveryZone']
    WorkingHours = models['WorkingHours']
    Branch = models['Branch']

    def _settings():
        if get_settings:
            return get_settings()
        return None

    def _get_language():
        if 'lang' in request.args:
            session['language'] = request.args.get('lang')
        return session.get('language', 'he')

    @bp.context_processor
    def inject_language():
        return {'language': _get_language()}

    def _get_branches():
        return Branch.query.filter_by(is_active=True).order_by(Branch.display_order).all()

    def _get_selected_branch():
        branch_id = request.args.get('branch_id') or session.get('order_branch_id')
        if branch_id:
            try:
                branch = Branch.query.filter_by(id=int(branch_id), is_active=True).first()
                if branch:
                    session['order_branch_id'] = branch.id
                    return branch
            except (ValueError, TypeError):
                pass
        branches = _get_branches()
        if len(branches) == 1:
            session['order_branch_id'] = branches[0].id
            return branches[0]
        return None

    def _get_branch_price(item, branch_id):
        if not BranchMenuItem or not branch_id:
            return item.base_price
        override = BranchMenuItem.query.filter_by(
            branch_id=branch_id, menu_item_id=item.id
        ).first()
        if override and override.custom_price is not None:
            return override.custom_price
        return item.base_price

    def _is_item_available_for_branch(item_id, branch_id):
        if not BranchMenuItem or not branch_id:
            return True
        override = BranchMenuItem.query.filter_by(
            branch_id=branch_id, menu_item_id=item_id
        ).first()
        if override is not None:
            return override.is_available
        return True

    @bp.route('/select-branch', methods=['POST'])
    def select_branch():
        branch_id = request.form.get('branch_id', '').strip()
        if branch_id:
            try:
                branch = Branch.query.filter_by(id=int(branch_id), is_active=True).first()
                if branch:
                    session['order_branch_id'] = branch.id
            except (ValueError, TypeError):
                pass
        return redirect(url_for('order_page.order_page'))

    @bp.route('/clear-branch')
    def clear_branch():
        session.pop('order_branch_id', None)
        session.pop('order_cart', None)
        return redirect(url_for('order_page.order_page'))

    def _check_outside_ordering_hours(branch=None):
        settings = _settings()
        if not settings or not getattr(settings, 'enforce_ordering_hours', False):
            return False
        try:
            from zoneinfo import ZoneInfo
            now = datetime.now(ZoneInfo('Asia/Jerusalem'))
        except Exception:
            now = datetime.now()
        db_dow = (now.weekday() + 1) % 7
        branch_id = branch.id if branch else None
        if not branch_id:
            branches = Branch.query.filter_by(is_active=True).all()
            branch_id = branches[0].id if branches else None
        wh_q = WorkingHours.query.filter_by(day_of_week=db_dow, is_closed=False)
        if branch_id:
            wh_q = wh_q.filter_by(branch_id=branch_id)
        wh = wh_q.first()
        if not wh or not wh.open_time or not wh.close_time:
            return True
        current_time = now.strftime('%H:%M')
        return current_time < wh.open_time or current_time > wh.close_time

    # ── Menu item image ────────────────────────────────────────────────

    @bp.route('/menu-image/<int:item_id>')
    def menu_image(item_id):
        """Serve menu item image from database storage."""
        item = MenuItem.query.get(item_id)
        if not item or not getattr(item, 'image_data', None):
            abort(404)
        data = item.image_data
        if isinstance(data, memoryview):
            data = bytes(data)
        content_type = 'image/jpeg'
        if data[:8] == b'\x89PNG\r\n\x1a\n':
            content_type = 'image/png'
        elif data[:4] == b'RIFF' and data[8:12] == b'WEBP':
            content_type = 'image/webp'
        elif data[:3] == b'GIF':
            content_type = 'image/gif'
        from flask import make_response
        response = make_response(data)
        response.headers['Content-Type'] = content_type
        response.headers['Cache-Control'] = 'public, max-age=86400'
        return response

    # ── Order page ────────────────────────────────────────────────────

    @bp.route('/')
    def order_page():
        settings = _settings()
        if not settings or not getattr(settings, 'enable_online_ordering', False):
            closed_msg = getattr(settings, 'ordering_closed_message', None) or 'מערכת ההזמנות אינה פעילה כרגע.'
            return render_template('order_page.html', ordering_disabled=True, categories=[],
                                   ordering_status_message=closed_msg, settings=settings,
                                   branches=[], selected_branch=None)

        branches = _get_branches()
        selected_branch = _get_selected_branch()
        multi_branch = len(branches) > 1
        need_branch_selection = multi_branch and not selected_branch

        ordering_paused = getattr(settings, 'ordering_paused', False)
        paused_message = getattr(settings, 'ordering_paused_message', None) or 'עסוקים כרגע — ניקח הזמנות בעוד כמה דקות'
        ordering_outside_hours = False
        outside_hours_message = getattr(settings, 'ordering_outside_hours_message', None) or 'ההזמנות פתוחות בשעות הפעילות בלבד.'
        if getattr(settings, 'enforce_ordering_hours', False):
            ordering_outside_hours = _check_outside_ordering_hours(branch=selected_branch)

        from sqlalchemy.orm import joinedload
        categories = MenuCategory.query.filter_by(is_active=True).order_by(MenuCategory.display_order).all()

        try:
            from zoneinfo import ZoneInfo
            now_il = datetime.now(ZoneInfo('Asia/Jerusalem'))
        except Exception:
            now_il = datetime.now()
        current_dow = (now_il.weekday() + 1) % 7
        current_time_str = now_il.strftime('%H:%M')

        sel_branch_id = selected_branch.id if selected_branch else None

        available_categories = []
        for cat in categories:
            items = MenuItem.query.filter(
                MenuItem.category_id == cat.id,
                db.or_(MenuItem.show_in_order == True, MenuItem.show_in_order.is_(None))
            ).options(
                joinedload(MenuItem.option_groups).joinedload(MenuItemOptionGroup.choices),
                joinedload(MenuItem.price_options)
            ).order_by(MenuItem.display_order).all()

            filtered_items = []
            for item in items:
                if sel_branch_id and not _is_item_available_for_branch(item.id, sel_branch_id):
                    continue

                if sel_branch_id:
                    item._branch_price = _get_branch_price(item, sel_branch_id)
                    if BranchMenuItem:
                        bmi = BranchMenuItem.query.filter_by(
                            branch_id=sel_branch_id, menu_item_id=item.id
                        ).first()
                        item._branch_display_order = bmi.display_order if bmi and bmi.display_order is not None else item.display_order
                    else:
                        item._branch_display_order = item.display_order
                else:
                    item._branch_price = item.base_price
                    item._branch_display_order = item.display_order

                item._order_available = True
                item._unavailable_reason = None
                if not item.is_available:
                    item._order_available = False
                    item._unavailable_reason = 'לא זמין כרגע'
                elif item.available_days and item.available_days != '1111111' and len(item.available_days) == 7:
                    if item.available_days[current_dow] == '0':
                        item._order_available = False
                        day_names = ['א׳', 'ב׳', 'ג׳', 'ד׳', 'ה׳', 'ו׳', 'ש׳']
                        avail_days = [day_names[i] for i in range(7) if item.available_days[i] == '1']
                        item._unavailable_reason = f"מוגש בימים: {', '.join(avail_days)}"
                if item._order_available and (item.available_from_time or item.available_to_time):
                    from_t = item.available_from_time
                    to_t = item.available_to_time
                    if from_t and to_t:
                        if current_time_str < from_t or current_time_str > to_t:
                            item._order_available = False
                            item._unavailable_reason = f"זמין בשעות {from_t}–{to_t}"
                    elif from_t and not to_t:
                        if current_time_str < from_t:
                            item._order_available = False
                            item._unavailable_reason = f"זמין מהשעה {from_t}"
                    elif to_t and not from_t:
                        if current_time_str > to_t:
                            item._order_available = False
                            item._unavailable_reason = f"זמין עד השעה {to_t}"
                filtered_items.append(item)

            if filtered_items:
                filtered_items.sort(key=lambda x: x._branch_display_order or 0)
                cat._order_items = filtered_items
                available_categories.append(cat)

        dz_query = DeliveryZone.query.filter_by(is_active=True)
        if sel_branch_id and multi_branch:
            dz_query = dz_query.filter(DeliveryZone.branch_id == sel_branch_id)
        elif sel_branch_id:
            dz_query = dz_query.filter(
                db.or_(DeliveryZone.branch_id == sel_branch_id, DeliveryZone.branch_id.is_(None))
            )
        delivery_zones = dz_query.order_by(DeliveryZone.display_order).all()

        return render_template('order_page.html',
                               ordering_disabled=False,
                               ordering_paused=ordering_paused,
                               ordering_outside_hours=ordering_outside_hours,
                               ordering_status_message=paused_message if ordering_paused else (outside_hours_message if ordering_outside_hours else ''),
                               categories=available_categories,
                               delivery_zones=delivery_zones,
                               delivery_fee=getattr(settings, 'delivery_fee', 15),
                               free_delivery_threshold=getattr(settings, 'free_delivery_threshold', 100),
                               estimated_delivery_time=getattr(settings, 'estimated_delivery_time', '45-60'),
                               enable_delivery=getattr(settings, 'enable_delivery', True),
                               enable_pickup=getattr(settings, 'enable_pickup', True),
                               branches=branches,
                               selected_branch=selected_branch,
                               multi_branch=multi_branch,
                               need_branch_selection=need_branch_selection,
                               settings=settings)

    # ── Start checkout ────────────────────────────────────────────────

    @bp.route('/start-checkout', methods=['POST'])
    def order_start_checkout():
        cart_json = request.form.get('cart_json', '[]')
        order_type = request.form.get('order_type', 'delivery')
        try:
            cart = json.loads(cart_json)
        except Exception:
            cart = []
        if not cart:
            flash('הסל ריק.', 'warning')
            return redirect(url_for('order_page.order_page'))
        session['order_cart'] = cart
        session['order_type'] = order_type
        session['order_utm_source'] = request.form.get('utm_source', '').strip()[:200]
        session['order_utm_medium'] = request.form.get('utm_medium', '').strip()[:200]
        session['order_utm_campaign'] = request.form.get('utm_campaign', '').strip()[:200]
        session['order_referrer'] = request.form.get('referrer', '').strip()[:500]
        branch_id = request.form.get('branch_id') or session.get('order_branch_id')
        if branch_id:
            try:
                session['order_branch_id'] = int(branch_id)
            except (ValueError, TypeError):
                pass
        return redirect(url_for('order_page.order_checkout_page'))

    # ── Checkout page ─────────────────────────────────────────────────

    @bp.route('/checkout', methods=['GET'])
    def order_checkout_page():
        cart = session.get('order_cart', [])
        if not cart:
            flash('הסל ריק.', 'warning')
            return redirect(url_for('order_page.order_page'))
        order_type = session.get('order_type', 'delivery')
        settings = _settings()
        if not settings or not getattr(settings, 'enable_online_ordering', False):
            flash('מערכת ההזמנות אינה פעילה כרגע.', 'danger')
            return redirect(url_for('order_page.order_page'))
        if getattr(settings, 'ordering_paused', False):
            flash(getattr(settings, 'ordering_paused_message', None) or 'עסוקים כרגע', 'warning')
            return redirect(url_for('order_page.order_page'))

        selected_branch = _get_selected_branch()
        multi_branch = len(_get_branches()) > 1
        if multi_branch and not selected_branch:
            flash('נא לבחור סניף לפני ביצוע הזמנה.', 'warning')
            return redirect(url_for('order_page.order_page'))
        if _check_outside_ordering_hours(branch=selected_branch):
            flash('ההזמנות פתוחות בשעות הפעילות בלבד.', 'warning')
            return redirect(url_for('order_page.order_page'))

        sel_branch_id = selected_branch.id if selected_branch else None
        dz_query = DeliveryZone.query.filter_by(is_active=True)
        if sel_branch_id and multi_branch:
            dz_query = dz_query.filter(DeliveryZone.branch_id == sel_branch_id)
        elif sel_branch_id:
            dz_query = dz_query.filter(
                db.or_(DeliveryZone.branch_id == sel_branch_id, DeliveryZone.branch_id.is_(None))
            )
        delivery_zones = dz_query.order_by(DeliveryZone.display_order).all()
        subtotal = sum(item.get('qty', 1) * item.get('price', 0) for item in cart)
        delivery_fee = getattr(settings, 'delivery_fee', 15.0)
        total = subtotal + (delivery_fee if order_type == 'delivery' else 0)

        time_slots = []
        try:
            now = datetime.now()
            db_dow = (now.weekday() + 1) % 7
            branch_id = sel_branch_id
            if not branch_id:
                branches = Branch.query.filter_by(is_active=True).all()
                branch_id = branches[0].id if branches else None
            wh_q = WorkingHours.query.filter_by(day_of_week=db_dow, is_closed=False)
            if branch_id:
                wh_q = wh_q.filter_by(branch_id=branch_id)
            wh = wh_q.first()
            if wh and wh.open_time and wh.close_time:
                close_h, close_m = map(int, wh.close_time.split(':'))
                close_dt = now.replace(hour=close_h, minute=close_m, second=0, microsecond=0)
                earliest = now + timedelta(minutes=45)
                extra = earliest.minute % 30
                if extra != 0:
                    earliest += timedelta(minutes=(30 - extra))
                earliest = earliest.replace(second=0, microsecond=0)
                current = earliest
                while current <= close_dt - timedelta(minutes=30):
                    time_slots.append(current.strftime('%H:%M'))
                    current += timedelta(minutes=30)
        except Exception:
            time_slots = []

        hyp_enabled = getattr(settings, 'hyp_enabled', False)
        hyp_sandbox_mode = getattr(settings, 'hyp_sandbox_mode', True)
        card_available = False
        if hyp_enabled and hyp_payment:
            try:
                hyp_payment._load_credentials(settings)
                card_available = hyp_payment.is_configured
            except Exception:
                card_available = False

        return render_template('order_checkout.html',
                               cart_items=cart,
                               cart_json=json.dumps(cart),
                               order_type=order_type,
                               delivery_zones=delivery_zones,
                               subtotal=subtotal,
                               delivery_fee=delivery_fee,
                               total=total,
                               selected_city='',
                               time_slots=time_slots,
                               hyp_enabled=hyp_enabled,
                               hyp_sandbox_mode=hyp_sandbox_mode,
                               card_available=card_available,
                               enable_delivery=getattr(settings, 'enable_delivery', True),
                               enable_pickup=getattr(settings, 'enable_pickup', True),
                               settings=settings)

    # ── Place order ───────────────────────────────────────────────────

    @bp.route('/place', methods=['POST'])
    def order_checkout():
        settings = _settings()
        if not settings or not getattr(settings, 'enable_online_ordering', False):
            flash('מערכת ההזמנות אינה פעילה כרגע.', 'danger')
            return redirect(url_for('order_page.order_page'))
        if getattr(settings, 'ordering_paused', False):
            flash('עסוקים כרגע', 'warning')
            return redirect(url_for('order_page.order_page'))
        selected_branch = _get_selected_branch()
        sel_branch_id = selected_branch.id if selected_branch else None
        multi_branch = len(_get_branches()) > 1
        if multi_branch and not selected_branch:
            flash('נא לבחור סניף לפני ביצוע הזמנה.', 'warning')
            return redirect(url_for('order_page.order_page'))

        if _check_outside_ordering_hours(branch=selected_branch):
            flash('ההזמנות פתוחות בשעות הפעילות בלבד.', 'warning')
            return redirect(url_for('order_page.order_page'))

        cart_json = request.form.get('cart_json', '[]')
        try:
            cart = json.loads(cart_json)
        except Exception:
            cart = []
        if not cart:
            flash('סל ריק.', 'warning')
            return redirect(url_for('order_page.order_checkout_page'))

        order_type = request.form.get('order_type', 'delivery')
        first_name = request.form.get('customer_first_name', '').strip()
        last_name = request.form.get('customer_last_name', '').strip()
        customer_name = f"{first_name} {last_name}".strip() if (first_name or last_name) else request.form.get('customer_name', '').strip()
        customer_phone = request.form.get('customer_phone', '').strip()
        customer_email = request.form.get('customer_email', '').strip()
        delivery_address = request.form.get('delivery_address', '').strip()
        delivery_city = request.form.get('delivery_city', '').strip()
        delivery_notes = request.form.get('delivery_notes', '').strip()
        pickup_time = request.form.get('pickup_time', '').strip()
        customer_notes = request.form.get('customer_notes', '').strip()
        payment_method = request.form.get('payment_method', 'cash')

        customer_name = customer_name[:120]
        customer_phone = re.sub(r'[^\d+\-() ]', '', customer_phone)[:20]
        delivery_address = delivery_address[:300]
        delivery_city = delivery_city[:100]
        delivery_notes = delivery_notes[:500]
        customer_notes = customer_notes[:500]

        if not customer_name or not customer_phone:
            flash('נא למלא שם וטלפון.', 'danger')
            return redirect(url_for('order_page.order_checkout_page'))

        phone_digits = re.sub(r'\D', '', customer_phone)
        if len(phone_digits) < 9 or len(phone_digits) > 15:
            flash('מספר טלפון לא תקין.', 'danger')
            return redirect(url_for('order_page.order_checkout_page'))

        if order_type == 'delivery' and not delivery_address:
            flash('נא למלא כתובת למשלוח.', 'danger')
            return redirect(url_for('order_page.order_checkout_page'))

        delivery_zone_id = request.form.get('delivery_zone_id', '').strip()
        delivery_zone = None
        verified_subtotal_cart = 0.0
        valid_cart = []
        for ci in cart:
            ci_id = ci.get('id')
            if not ci_id:
                continue
            try:
                db_ci = MenuItem.query.get(int(ci_id))
            except (ValueError, TypeError):
                continue
            if not db_ci:
                continue
            if sel_branch_id and not _is_item_available_for_branch(db_ci.id, sel_branch_id):
                continue
            qty = max(1, min(99, int(ci.get('qty', 1))))
            ci['qty'] = qty
            item_price = _get_branch_price(db_ci, sel_branch_id)
            ci['price'] = float(item_price)
            verified_subtotal_cart += item_price * qty
            valid_cart.append(ci)
        cart = valid_cart
        if not cart:
            flash('סל ריק או פריטים לא תקינים.', 'warning')
            return redirect(url_for('order_page.order_page'))
        subtotal = verified_subtotal_cart

        delivery_fee = 0.0
        if order_type == 'delivery':
            if delivery_zone_id:
                try:
                    dz_q = DeliveryZone.query.filter_by(id=int(delivery_zone_id), is_active=True)
                    if sel_branch_id and multi_branch:
                        dz_q = dz_q.filter(DeliveryZone.branch_id == sel_branch_id)
                    elif sel_branch_id:
                        dz_q = dz_q.filter(
                            db.or_(DeliveryZone.branch_id == sel_branch_id, DeliveryZone.branch_id.is_(None))
                        )
                    delivery_zone = dz_q.first()
                except (ValueError, TypeError):
                    delivery_zone = None
            if delivery_zone:
                min_order = delivery_zone.minimum_order or 0
                if subtotal < min_order:
                    flash(f"הזמנה מינימלית ל{delivery_zone.city_name} היא ₪{int(min_order)}.", 'warning')
                    return redirect(url_for('order_page.order_checkout_page'))
                free_above = delivery_zone.free_delivery_above or 0
                delivery_fee = 0.0 if (free_above > 0 and subtotal >= free_above) else delivery_zone.delivery_fee
            else:
                delivery_fee_setting = getattr(settings, 'delivery_fee', 15.0)
                free_threshold = getattr(settings, 'free_delivery_threshold', 100.0)
                delivery_fee = 0.0 if subtotal >= free_threshold else delivery_fee_setting
        total_amount = subtotal + delivery_fee

        order = FoodOrder()
        order.set_order_number()
        order.tracking_token = secrets.token_urlsafe(24)
        if selected_branch:
            order.branch_id = selected_branch.id
            order.branch_name = selected_branch.name_he
        order.order_type = order_type
        order.customer_name = customer_name
        order.customer_phone = customer_phone
        order.customer_email = customer_email
        order.delivery_address = delivery_address
        order.delivery_city = delivery_city or (delivery_zone.city_name if delivery_zone else '')
        order.delivery_notes = delivery_notes
        order.pickup_time = pickup_time
        order.customer_notes = customer_notes
        order.payment_method = payment_method
        order.subtotal = subtotal
        order.delivery_fee = delivery_fee
        order.total_amount = total_amount
        order.status = 'pending'
        order.payment_status = 'pending' if payment_method == 'card' else 'cash'
        order.items_json = json.dumps(cart)

        order.utm_source = request.form.get('utm_source', '').strip()[:200] or session.get('order_utm_source', '')[:200] or None
        order.utm_medium = request.form.get('utm_medium', '').strip()[:200] or session.get('order_utm_medium', '')[:200] or None
        order.utm_campaign = request.form.get('utm_campaign', '').strip()[:200] or session.get('order_utm_campaign', '')[:200] or None
        order.referrer = request.form.get('referrer', '').strip()[:500] or session.get('order_referrer', '')[:500] or None

        cust_id = session.get('customer_id')
        if cust_id:
            order.customer_account_id = cust_id

        db.session.add(order)
        db.session.flush()

        verified_subtotal = 0.0
        for item in cart:
            oi = FoodOrderItem()
            oi.order_id = order.id
            menu_item_id = item.get('id')
            oi.menu_item_id = menu_item_id
            oi.item_name_he = item.get('name_he', item.get('name', ''))
            oi.item_name_en = item.get('name_en', '')
            oi.quantity = int(item.get('qty', 1))
            db_item = MenuItem.query.get(int(menu_item_id)) if menu_item_id else None
            if db_item and not db_item.is_available:
                continue
            if db_item and sel_branch_id and not _is_item_available_for_branch(db_item.id, sel_branch_id):
                continue
            if db_item and getattr(db_item, 'available_days', None) and len(db_item.available_days) == 7:
                today_idx = (datetime.now().weekday() + 1) % 7
                if db_item.available_days[today_idx] == '0':
                    continue
            base_price = _get_branch_price(db_item, sel_branch_id) if db_item else float(item.get('base_price', item.get('price', 0)))
            options_extra = 0.0
            item_options = item.get('options')
            combo_selections = item.get('combo_selections')
            if item_options and db_item:
                choice_ids = [o.get('choice_id') for o in item_options if o.get('choice_id')]
                if choice_ids:
                    db_choices = MenuItemOptionChoice.query.filter(MenuItemOptionChoice.id.in_(choice_ids), MenuItemOptionChoice.is_available == True).all()
                    db_choice_map = {c.id: c for c in db_choices}
                    verified_options = []
                    for o in item_options:
                        cid = o.get('choice_id')
                        dbc = db_choice_map.get(cid)
                        if dbc:
                            verified_options.append({
                                'group_id': o.get('group_id'),
                                'group_name_he': o.get('group_name_he', ''),
                                'group_name_en': o.get('group_name_en', ''),
                                'choice_id': cid,
                                'choice_name_he': dbc.name_he,
                                'choice_name_en': dbc.name_en,
                                'price_modifier': dbc.price_modifier
                            })
                            options_extra += dbc.price_modifier
                    item_options = verified_options
            if combo_selections and db_item and getattr(db_item, 'is_combo', False) and db_item.combo_items_json:
                try:
                    combo_def = json.loads(db_item.combo_items_json)
                except (json.JSONDecodeError, TypeError):
                    combo_selections = None
                    combo_def = []
                slot_maps = {}
                for si, slot in enumerate(combo_def):
                    slot_maps[si] = {}
                    for ci in slot.get('items', []):
                        slot_maps[si][ci['menu_item_id']] = ci.get('price_modifier', 0)
                sels_by_slot = {}
                if combo_selections:
                    for sel in combo_selections:
                        si = sel.get('slot_index', 0)
                        sels_by_slot.setdefault(si, []).append(sel)
                verified_combo = []
                combo_valid = True
                for si, slot in enumerate(combo_def):
                    slot_sels = sels_by_slot.get(si, [])
                    min_sel = int(slot.get('min_select', 1))
                    max_sel = int(slot.get('max_select', 1))
                    count = 0
                    for sel in slot_sels:
                        mid = sel.get('menu_item_id')
                        if mid in slot_maps.get(si, {}):
                            db_pm = slot_maps[si][mid]
                            options_extra += db_pm
                            verified_combo.append({
                                'slot_index': si,
                                'slot_name_he': slot.get('slot_name_he', ''),
                                'slot_name_en': slot.get('slot_name_en', ''),
                                'menu_item_id': mid,
                                'item_name_he': sel.get('item_name_he', ''),
                                'item_name_en': sel.get('item_name_en', ''),
                                'price_modifier': db_pm
                            })
                            count += 1
                    if count < min_sel or count > max_sel:
                        combo_valid = False
                if not combo_valid:
                    continue
                combo_selections = verified_combo
            oi.unit_price = base_price + options_extra
            oi.total_price = oi.quantity * oi.unit_price
            oi.special_instructions = item.get('notes', '')
            combined_json = {}
            if item_options:
                combined_json['options'] = item_options
            if combo_selections:
                combined_json['combo_selections'] = combo_selections
            if combined_json:
                oi.options_json = json.dumps(combined_json if combo_selections else item_options, ensure_ascii=False)
            verified_subtotal += oi.total_price
            db.session.add(oi)

        if verified_subtotal <= 0:
            db.session.rollback()
            flash('הפריטים שבחרת אינם זמינים כרגע.', 'warning')
            return redirect(url_for('order_page.order_page'))

        order.subtotal = verified_subtotal
        order.total_amount = verified_subtotal + delivery_fee
        db.session.commit()

        if payment_method == 'card' and hyp_payment:
            try:
                hyp_payment._load_credentials(settings)
                success_url = url_for('order_page.payment_success', _external=True) + f'?order={order.order_number}'
                failure_url = url_for('order_page.payment_failure', _external=True) + f'?order={order.order_number}'
                hesh_items = []
                for oi_item in order.items:
                    name = oi_item.item_name_he or oi_item.item_name_en or 'פריט'
                    hesh_items.append(f'[0~{name}~{oi_item.quantity}~{oi_item.unit_price}]')
                if order.delivery_fee and order.delivery_fee > 0:
                    hesh_items.append(f'[0~משלוח~1~{order.delivery_fee}]')
                extra_params = {}
                if hesh_items:
                    extra_params['heshDesc'] = ''.join(hesh_items)
                    extra_params['Pritim'] = 'True'
                payment_url = hyp_payment.create_payment_url(
                    amount=order.total_amount,
                    order_id=order.order_number,
                    description=f'הזמנה {order.order_number}',
                    success_url=success_url,
                    failure_url=failure_url,
                    customer_name=customer_name,
                    customer_email=customer_email,
                    customer_phone=customer_phone,
                    additional_params=extra_params if extra_params else None
                )
                if payment_url:
                    order.hyp_order_ref = order.order_number
                    db.session.commit()
                    return render_template('hyp_redirect.html', payment_url=payment_url, order=order)
            except Exception as e:
                logging.error(f"HYP payment failed for #{order.order_number}: {e}")

        if notifier:
            try:
                notifier.notify_new_order(order, settings)
            except Exception as e:
                logging.warning(f"Notification failed for #{order.order_number}: {e}")
            try:
                notifier.send_customer_confirmation(order, settings)
            except Exception as e:
                logging.warning(f"Customer SMS failed for #{order.order_number}: {e}")

        return redirect(url_for('order_page.order_confirmation', order_number=order.order_number))

    # ── Confirmation ──────────────────────────────────────────────────

    @bp.route('/confirm/<order_number>')
    def order_confirmation(order_number):
        settings = _settings()
        order = FoodOrder.query.filter_by(order_number=order_number).first_or_404()
        return render_template('order_confirmation.html', order=order, settings=settings)

    # ── AJAX status ───────────────────────────────────────────────────

    @bp.route('/status/<order_number>')
    def order_status(order_number):
        order = FoodOrder.query.filter_by(order_number=order_number).first_or_404()
        ready_by_time = None
        if order.estimated_ready_at and order.status in ('confirmed', 'preparing'):
            try:
                import pytz
                utc = pytz.utc
                local_tz = pytz.timezone('Asia/Jerusalem')
                ready_local = utc.localize(order.estimated_ready_at).astimezone(local_tz)
            except Exception:
                ready_local = order.estimated_ready_at
            mins = ready_local.minute
            rounded_mins = math.ceil(mins / 5) * 5
            if rounded_mins >= 60:
                ready_local = ready_local.replace(minute=0) + timedelta(hours=1)
            else:
                ready_local = ready_local.replace(minute=rounded_mins)
            ready_by_time = ready_local.strftime('%H:%M')
        return jsonify({
            'status': order.status,
            'status_he': order.status_display_he,
            'badge_class': order.status_badge_class,
            'confirmed_at': order.confirmed_at.strftime('%H:%M') if order.confirmed_at else None,
            'ready_at': order.ready_at.strftime('%H:%M') if order.ready_at else None,
            'preparing_at': order.preparing_at.strftime('%H:%M') if order.preparing_at else None,
            'estimated_ready_at': order.estimated_ready_at.strftime('%H:%M') if order.estimated_ready_at else None,
            'ready_by_time': ready_by_time,
        })

    # ── Tracking page ─────────────────────────────────────────────────

    @bp.route('/track/<token>')
    def order_track(token):
        if not token or len(token) > 64:
            abort(404)
        order = FoodOrder.query.filter_by(tracking_token=token).first_or_404()
        if order.status in ('delivered', 'pickedup', 'cancelled'):
            final_time = order.completed_at or order.cancelled_at or order.ready_at or order.created_at
            if final_time and (datetime.utcnow() - final_time).total_seconds() > 48 * 3600:
                abort(404)
        return render_template('order_track.html', order=order, items=order.get_items())

    # ── Payment callbacks ─────────────────────────────────────────────

    @bp.route('/payment-success')
    def payment_success():
        order_number = request.args.get('Order') or request.args.get('order') or ''
        settings = _settings()
        if order_number:
            order = FoodOrder.query.filter_by(order_number=order_number).first()
            if order:
                if order.payment_status == 'paid':
                    return redirect(url_for('order_page.order_confirmation', order_number=order_number))
                if hyp_payment:
                    verification = hyp_payment.verify_payment_response(
                        dict(request.args),
                        expected_order_id=order.hyp_order_ref or order.order_number,
                        expected_amount=order.total_amount,
                    )
                    if verification.get('verified') and verification.get('success'):
                        order.payment_status = 'paid'
                        order.hyp_transaction_id = verification.get('transaction_id') or request.args.get('Id')
                        if order.status == 'pending':
                            order.status = 'confirmed'
                            order.confirmed_at = datetime.utcnow()
                        db.session.commit()
                        if notifier:
                            try:
                                notifier.notify_new_order(order, settings)
                            except Exception:
                                pass
                            try:
                                notifier.send_customer_confirmation(order, settings)
                            except Exception:
                                pass
                        return redirect(url_for('order_page.order_confirmation', order_number=order_number))
                    else:
                        order.payment_status = 'failed'
                        db.session.commit()
                        return redirect(url_for('order_page.payment_failure') + f'?order={order_number}')
        return redirect(url_for('order_page.order_page'))

    @bp.route('/payment-failed')
    def payment_failure():
        order_number = request.args.get('Order') or request.args.get('order') or ''
        if order_number:
            order = FoodOrder.query.filter_by(order_number=order_number).first()
            if order:
                order.payment_status = 'failed'
                db.session.commit()
        flash('התשלום נכשל. ניתן לנסות שנית או לשלם במזומן.', 'danger')
        return redirect(url_for('order_page.order_confirmation', order_number=order_number) if order_number else url_for('order_page.order_page'))

    # ── Streets API proxy ─────────────────────────────────────────────

    @bp.route('/api/streets')
    def api_streets():
        import urllib.request
        import urllib.parse
        city = request.args.get('city', '').strip()
        if not city or len(city) < 2:
            return jsonify({'streets': [], 'error': 'city required'})
        try:
            params = urllib.parse.urlencode({
                'resource_id': '9ad3862c-8391-4b2f-84a4-2d4c68625f4b',
                'q': city, 'limit': 500,
                'fields': 'שם_ישוב,שם_רחוב'
            })
            url = f'https://data.gov.il/api/3/action/datastore_search?{params}'
            req = urllib.request.Request(url, headers={'User-Agent': 'RestaurantApp/1.0'})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read())
            records = data.get('result', {}).get('records', [])
            city_norm = city.strip()
            streets = sorted(set(
                r.get('שם_רחוב', '').strip()
                for r in records
                if r.get('שם_ישוב', '').strip() == city_norm
                and r.get('שם_רחוב', '').strip()
                and r.get('שם_רחוב', '').strip() != city_norm
            ))
            return jsonify({'streets': streets, 'city': city_norm, 'count': len(streets)})
        except Exception as e:
            logging.warning(f"Streets API error for '{city}': {e}")
            return jsonify({'streets': [], 'error': 'API unavailable'})

    return bp
