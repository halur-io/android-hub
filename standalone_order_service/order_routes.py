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
    flash, jsonify, session, abort, current_app,
)


def _to_il_hour(dt):
    if dt is None:
        return None
    try:
        from zoneinfo import ZoneInfo
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo('UTC'))
        return dt.astimezone(ZoneInfo('Asia/Jerusalem')).strftime('%H:%M')
    except Exception:
        return (dt + timedelta(hours=3)).strftime('%H:%M')

def create_order_blueprint(db, models, notifier=None, hyp_payment=None, get_settings=None, max_payment=None):
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
    max_payment : MaxPayService, optional
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
    Coupon = models.get('Coupon')
    CouponUsage = models.get('CouponUsage')
    Deal = models.get('Deal')
    UpsellRule = models.get('UpsellRule')
    OrderActivityLog = models.get('OrderActivityLog')

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
        item = MenuItem.query.get(item_id)
        return item.is_available if item else False

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
        for k in ['order_branch_id', 'order_cart', 'order_onboarded',
                   'order_customer', 'order_type', 'otp_code', 'otp_phone',
                   'otp_ts', 'otp_attempts', 'otp_verified']:
            session.pop(k, None)
        return redirect(url_for('order_page.order_page'))

    @bp.route('/reset')
    def reset_order():
        for k in list(session.keys()):
            if k.startswith('order_') or k.startswith('otp_'):
                session.pop(k, None)
        return redirect(url_for('order_page.order_page'))

    @bp.route('/send-otp', methods=['POST'])
    def send_otp():
        data = request.get_json(silent=True) or {}
        phone = re.sub(r'[^\d+\-() ]', '', (data.get('phone') or '').strip())[:20]
        phone_digits = re.sub(r'\D', '', phone)
        if len(phone_digits) < 9 or len(phone_digits) > 15:
            return jsonify({'ok': False, 'error': 'מספר טלפון לא תקין'}), 400
        import random
        code = str(random.randint(1000, 9999))
        session['otp_code'] = code
        session['otp_phone'] = phone
        session['otp_ts'] = datetime.utcnow().isoformat()
        session['otp_attempts'] = 0
        try:
            from standalone_order_service.sms_helpers import create_sender_from_env
            send_sms = create_sender_from_env()
            if send_sms:
                send_sms(phone, f'קוד האימות שלך: {code}')
                logging.info(f"[OTP] Sent to {phone}")
            else:
                logging.warning(f"[OTP] No SMS provider configured. Code: {code}")
        except Exception as e:
            logging.error(f"[OTP] SMS error: {e}")
        return jsonify({'ok': True})

    @bp.route('/verify-otp', methods=['POST'])
    def verify_otp():
        data = request.get_json(silent=True) or {}
        entered = (data.get('code') or '').strip()
        stored = session.get('otp_code')
        otp_ts = session.get('otp_ts')
        attempts = session.get('otp_attempts', 0)
        if attempts >= 5:
            return jsonify({'ok': False, 'error': 'נסיונות רבים מדי. שלח קוד חדש.'}), 429
        session['otp_attempts'] = attempts + 1
        if not stored or not otp_ts:
            return jsonify({'ok': False, 'error': 'לא נשלח קוד. שלח שוב.'}), 400
        try:
            ts = datetime.fromisoformat(otp_ts)
            if (datetime.utcnow() - ts).total_seconds() > 300:
                return jsonify({'ok': False, 'error': 'הקוד פג תוקף. שלח שוב.'}), 400
        except Exception:
            pass
        if entered != stored:
            return jsonify({'ok': False, 'error': 'קוד שגוי'}), 400
        session['otp_verified'] = True
        session.pop('otp_code', None)
        session.pop('otp_ts', None)
        session.pop('otp_attempts', None)
        return jsonify({'ok': True})

    @bp.route('/complete-onboarding', methods=['POST'])
    def complete_onboarding():
        data = request.get_json(silent=True) or {}
        branch_id = data.get('branch_id')
        order_type = data.get('order_type', 'delivery')
        first_name = (data.get('first_name') or '').strip()[:60]
        last_name = (data.get('last_name') or '').strip()[:60]
        phone = (data.get('phone') or '').strip()[:20]
        email = (data.get('email') or '').strip()[:120]
        if not first_name or not last_name or not phone or not email:
            return jsonify({'ok': False, 'error': 'נא למלא את כל השדות'}), 400
        if not session.get('otp_verified'):
            return jsonify({'ok': False, 'error': 'נדרש אימות טלפון'}), 400
        if branch_id:
            try:
                branch = Branch.query.filter_by(id=int(branch_id), is_active=True).first()
                if branch:
                    session['order_branch_id'] = branch.id
            except (ValueError, TypeError):
                pass
        session['order_type'] = order_type
        session['order_customer'] = {
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'email': email,
        }
        session['order_onboarded'] = True
        session['order_onboarded_ts'] = datetime.utcnow().isoformat()
        return jsonify({'ok': True})

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
        onboarding_enabled = getattr(settings, 'enable_order_onboarding', True)
        order_onboarded = session.get('order_onboarded', False)
        if order_onboarded:
            ob_ts = session.get('order_onboarded_ts')
            if ob_ts:
                try:
                    ob_time = datetime.fromisoformat(ob_ts)
                    if (datetime.utcnow() - ob_time).total_seconds() > 7200:
                        for k in ['order_onboarded', 'order_onboarded_ts', 'order_customer',
                                  'order_type', 'order_branch_id', 'order_cart',
                                  'otp_code', 'otp_phone', 'otp_ts', 'otp_attempts', 'otp_verified']:
                            session.pop(k, None)
                        order_onboarded = False
                except Exception:
                    pass
            else:
                for k in ['order_onboarded', 'order_customer', 'order_type',
                           'order_branch_id', 'order_cart']:
                    session.pop(k, None)
                order_onboarded = False
        need_onboarding = onboarding_enabled and not order_onboarded
        need_branch_selection = multi_branch and not selected_branch

        if need_onboarding:
            return render_template('order_page.html',
                                   ordering_disabled=False,
                                   ordering_paused=False,
                                   ordering_outside_hours=False,
                                   ordering_status_message='',
                                   categories=[],
                                   delivery_zones=[],
                                   delivery_fee=0,
                                   free_delivery_threshold=100,
                                   estimated_delivery_time='45-60',
                                   enable_delivery=getattr(settings, 'enable_delivery', True),
                                   enable_pickup=getattr(settings, 'enable_pickup', True),
                                   branches=branches,
                                   selected_branch=None,
                                   multi_branch=multi_branch,
                                   need_branch_selection=False,
                                   need_onboarding=True,
                                   order_onboarded=False,
                                   order_customer={},
                                   deals=[],
                                   settings=settings,
                                   reorder_data=None)

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
                branch_override = None
                if sel_branch_id:
                    branch_override = BranchMenuItem.query.filter_by(
                        branch_id=sel_branch_id, menu_item_id=item.id
                    ).first()
                effective_available = branch_override.is_available if branch_override else item.is_available
                if not effective_available:
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

        active_deals = []
        if Deal:
            active_deals = [d for d in Deal.query.filter_by(is_active=True).order_by(Deal.display_order).all() if d.is_valid()]

        reorder_data = None
        reorder_json_str = session.pop('reorder_data', None)
        if reorder_json_str:
            try:
                import json as _json
                reorder_data = _json.loads(reorder_json_str)
            except Exception:
                reorder_data = None

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
                               need_onboarding=need_onboarding,
                               order_onboarded=order_onboarded,
                               order_customer=session.get('order_customer', {}),
                               deals=active_deals,
                               settings=settings,
                               reorder_data=reorder_data)

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
        branch_provider = getattr(selected_branch, 'payment_provider', 'hyp') if selected_branch else 'hyp'

        def _check_max_available():
            if not max_payment:
                return False
            _u, _k, _m = max_payment._resolve_credentials(branch=selected_branch, settings=settings)
            return bool(_u and _k and _m)

        def _check_hyp_available():
            if not hyp_payment:
                return False
            try:
                from standalone_order_service.hyp_payment import HYPPayment
                _hyp_check = HYPPayment(settings)
                _hyp_check._load_credentials(settings, branch=selected_branch)
                return _hyp_check.is_configured
            except Exception:
                return False

        if branch_provider == 'max':
            card_available = _check_max_available() or _check_hyp_available()
        elif hyp_enabled:
            card_available = _check_hyp_available() or _check_max_available()
        else:
            card_available = _check_hyp_available() or _check_max_available()

        reorder_customer = session.pop('reorder_customer', None)
        onboard_customer = session.get('order_customer', {})
        prefill = {}
        if reorder_customer:
            name_parts = (reorder_customer.get('name') or '').split(' ', 1)
            prefill = {
                'first_name': name_parts[0] if name_parts else '',
                'last_name': name_parts[1] if len(name_parts) > 1 else '',
                'phone': reorder_customer.get('phone', ''),
                'email': reorder_customer.get('email', ''),
                'address': reorder_customer.get('address', ''),
                'city': reorder_customer.get('city', ''),
                'notes': reorder_customer.get('notes', ''),
            }
        elif onboard_customer:
            prefill = {
                'first_name': onboard_customer.get('first_name', ''),
                'last_name': onboard_customer.get('last_name', ''),
                'phone': onboard_customer.get('phone', ''),
                'email': onboard_customer.get('email', ''),
            }

        return render_template('order_checkout.html',
                               cart_items=cart,
                               cart_json=json.dumps(cart),
                               order_type=order_type,
                               delivery_zones=delivery_zones,
                               subtotal=subtotal,
                               delivery_fee=delivery_fee,
                               total=total,
                               selected_city=prefill.get('city', ''),
                               time_slots=time_slots,
                               hyp_enabled=hyp_enabled,
                               hyp_sandbox_mode=hyp_sandbox_mode,
                               card_available=card_available,
                               enable_delivery=getattr(settings, 'enable_delivery', True),
                               enable_pickup=getattr(settings, 'enable_pickup', True),
                               settings=settings,
                               prefill=prefill)

    # ── Coupon validation API ──────────────────────────────────────────

    @bp.route('/validate-coupon', methods=['POST'])
    def validate_coupon():
        if not Coupon:
            return jsonify({'valid': False, 'error': 'קופונים לא מופעלים'})
        data = request.get_json(silent=True) or {}
        code = (data.get('code') or '').strip().upper()
        try:
            subtotal = float(data.get('subtotal', 0))
        except (ValueError, TypeError):
            subtotal = 0.0
        email = (data.get('email') or '').strip().lower()
        if not code:
            return jsonify({'valid': False, 'error': 'נא להזין קוד קופון'})
        coupon = Coupon.query.filter(db.func.upper(Coupon.code) == code).first()
        if not coupon:
            return jsonify({'valid': False, 'error': 'קוד קופון לא נמצא'})
        if not coupon.is_valid():
            return jsonify({'valid': False, 'error': 'הקופון פג תוקף או אינו פעיל'})
        if coupon.max_uses_per_email is not None:
            if not email:
                return jsonify({'valid': False, 'error': 'נדרש אימייל כדי להשתמש בקופון זה'})
            if not coupon.can_be_used_by_email(email):
                return jsonify({'valid': False, 'error': 'הקופון כבר נוצל עבור אימייל זה'})
        if coupon.minimum_order_amount and subtotal < coupon.minimum_order_amount:
            return jsonify({'valid': False, 'error': f'הזמנה מינימלית ₪{int(coupon.minimum_order_amount)} נדרשת'})
        if coupon.discount_type == 'percentage':
            discount = subtotal * (coupon.discount_value / 100.0)
            if coupon.maximum_discount_amount:
                discount = min(discount, coupon.maximum_discount_amount)
            desc = f'{int(coupon.discount_value)}% הנחה'
        elif coupon.discount_type == 'fixed_amount':
            discount = min(coupon.discount_value, subtotal)
            desc = f'₪{int(coupon.discount_value)} הנחה'
        else:
            discount = 0
            desc = 'הנחה'
        return jsonify({
            'valid': True,
            'discount': round(discount, 2),
            'description': desc,
            'coupon_id': coupon.id,
            'code': coupon.code,
        })

    # ── Upsell suggestions API ────────────────────────────────────────

    @bp.route('/deal-picker-items/<int:deal_id>')
    def deal_picker_items(deal_id):
        if not Deal:
            return jsonify({'ok': False, 'error': 'Deals not available'}), 404
        deal = Deal.query.get(deal_id)
        if not deal or not deal.is_valid() or getattr(deal, 'deal_type', 'fixed') != 'customer_picks':
            return jsonify({'ok': False, 'error': 'Deal not found'}), 404
        cat_ids = getattr(deal, 'effective_category_ids', [])
        if not cat_ids:
            cat_id = getattr(deal, 'source_category_id', None)
            cat_ids = [cat_id] if cat_id else []
        if not cat_ids:
            return jsonify({'ok': False, 'error': 'No source category'}), 400
        sel_branch_id = None
        selected_branch = _get_selected_branch()
        if selected_branch:
            sel_branch_id = selected_branch.id
        items_q = MenuItem.query.filter(
            MenuItem.category_id.in_(cat_ids),
            MenuItem.is_available == True,
            db.or_(MenuItem.show_in_order == True, MenuItem.show_in_order.is_(None))
        ).order_by(MenuItem.display_order).all()
        result = []
        for item in items_q:
            if sel_branch_id and not _is_item_available_for_branch(item.id, sel_branch_id):
                continue
            img = ''
            if item.image_data:
                img = url_for('order_page.menu_image', item_id=item.id)
            elif item.image_path:
                img = item.image_path
            result.append({
                'id': item.id,
                'name_he': item.name_he,
                'name_en': item.name_en or '',
                'description_he': item.description_he or '',
                'description_en': item.description_en or '',
                'ingredients_he': item.ingredients_he or '',
                'ingredients_en': item.ingredients_en or '',
                'image': img,
                'price': float(_get_branch_price(item, sel_branch_id)),
            })
        return jsonify({
            'ok': True,
            'items': result,
            'pick_count': getattr(deal, 'pick_count', 0),
            'deal_name_he': deal.name_he,
            'deal_name_en': deal.name_en or deal.name_he,
            'deal_price': float(deal.deal_price),
        })

    @bp.route('/upsell-suggestions', methods=['POST'])
    def upsell_suggestions():
        if not UpsellRule:
            return jsonify({'suggestions': []})
        data = request.get_json(silent=True) or {}
        cart_items = data.get('cart', [])
        cart_item_ids = set()
        cart_category_ids = set()
        for ci in cart_items:
            ci_id = ci.get('id')
            if not ci_id or ci.get('is_deal'):
                continue
            try:
                numeric_id = int(ci_id)
            except (ValueError, TypeError):
                continue
            cart_item_ids.add(numeric_id)
            mi = MenuItem.query.get(numeric_id)
            if mi and mi.category_id:
                cart_category_ids.add(mi.category_id)
        rules = UpsellRule.query.filter_by(is_active=True).order_by(UpsellRule.display_order).all()
        suggestions = []
        seen_items = set()
        sel_branch_id = None
        selected_branch = _get_selected_branch()
        if selected_branch:
            sel_branch_id = selected_branch.id
        for rule in rules:
            if rule.suggested_item_id in cart_item_ids:
                continue
            if rule.suggested_item_id in seen_items:
                continue
            matched = False
            if rule.trigger_type == 'item' and rule.trigger_id in cart_item_ids:
                matched = True
            elif rule.trigger_type == 'category' and rule.trigger_id in cart_category_ids:
                matched = True
            if not matched:
                continue
            item = rule.suggested_item
            if not item or not item.is_available:
                continue
            if sel_branch_id and not _is_item_available_for_branch(item.id, sel_branch_id):
                continue
            price = rule.discounted_price if rule.discounted_price else _get_branch_price(item, sel_branch_id)
            original = _get_branch_price(item, sel_branch_id)
            suggestions.append({
                'rule_id': rule.id,
                'item_id': item.id,
                'name_he': item.name_he,
                'name_en': item.name_en or '',
                'image': item.image_path or '',
                'price': float(price),
                'original_price': float(original) if rule.discounted_price else None,
                'message_he': rule.message_he or '',
                'message_en': rule.message_en or '',
            })
            seen_items.add(rule.suggested_item_id)
            if len(suggestions) >= 3:
                break
        return jsonify({'suggestions': suggestions})

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
            if ci.get('is_deal') and Deal:
                deal_id_str = str(ci_id).replace('deal_', '')
                try:
                    deal_obj = Deal.query.get(int(deal_id_str))
                except (ValueError, TypeError):
                    continue
                if not deal_obj or not deal_obj.is_valid():
                    continue
                qty = max(1, min(99, int(ci.get('qty', 1))))
                ci['qty'] = qty
                ci['price'] = float(deal_obj.deal_price)
                ci['deal_id'] = deal_obj.id
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
                        continue
                    total_picked = 0
                    for sel in selected:
                        sel_id = sel.get('item_id')
                        sel_qty = max(1, int(sel.get('qty', 1)))
                        if sel_id:
                            sel_item = MenuItem.query.get(int(sel_id))
                            if sel_item and sel_item.is_available and sel_item.category_id in source_cats and (not sel_branch_id or _is_item_available_for_branch(sel_item.id, sel_branch_id)):
                                verified_selected.append({
                                    'item_id': sel_item.id,
                                    'qty': sel_qty,
                                    'name_he': sel_item.name_he,
                                    'name_en': sel_item.name_en or '',
                                })
                                total_picked += sel_qty
                    if total_picked != pick_count:
                        continue
                    ci['selected_items'] = verified_selected
                    ci['included_items'] = []
                else:
                    ci['included_items'] = deal_obj.included_items or []
                verified_subtotal_cart += deal_obj.deal_price * ci['qty']
                valid_cart.append(ci)
                continue
            if ci.get('upsell') and UpsellRule:
                rule_id = ci.get('upsell_rule_id')
                if rule_id:
                    try:
                        rule = UpsellRule.query.get(int(rule_id))
                    except (ValueError, TypeError):
                        rule = None
                    if (rule and rule.is_active and rule.discounted_price is not None
                            and rule.suggested_item_id == int(ci_id)):
                        try:
                            db_ci = MenuItem.query.get(int(ci_id))
                        except (ValueError, TypeError):
                            continue
                        if db_ci and db_ci.is_available:
                            if sel_branch_id and not _is_item_available_for_branch(db_ci.id, sel_branch_id):
                                continue
                            qty = max(1, min(99, int(ci.get('qty', 1))))
                            ci['qty'] = qty
                            ci['price'] = float(rule.discounted_price)
                            verified_subtotal_cart += rule.discounted_price * qty
                            valid_cart.append(ci)
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
        for ci in cart:
            raw_ex = ci.get('excluded_ingredients', [])
            if isinstance(raw_ex, list):
                ci['excluded_ingredients'] = [str(e).strip()[:100] for e in raw_ex if isinstance(e, str) and e.strip()][:20]
            else:
                ci.pop('excluded_ingredients', None)
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
            if item.get('is_deal'):
                oi.menu_item_id = None
                oi.item_name_he = item.get('name_he', item.get('name', ''))
                oi.item_name_en = item.get('name_en', '')
                oi.quantity = int(item.get('qty', 1))
                oi.unit_price = float(item.get('price', 0))
                oi.total_price = oi.quantity * oi.unit_price
                oi.special_instructions = item.get('notes', '')
                deal_data = {'is_deal': True, 'deal_id': item.get('deal_id')}
                if item.get('deal_type') == 'customer_picks':
                    deal_data['deal_type'] = 'customer_picks'
                    selected = item.get('selected_items', [])
                    selected_names = []
                    for sel in selected:
                        sel_id = sel.get('item_id')
                        if sel_id:
                            sel_item = MenuItem.query.get(int(sel_id))
                            if sel_item:
                                selected_names.append({'id': sel_item.id, 'name_he': sel_item.name_he, 'name_en': sel_item.name_en or '', 'qty': sel.get('qty', 1)})
                    deal_data['selected_items'] = selected_names
                    deal_data['included_items'] = []
                else:
                    included = item.get('included_items', [])
                    included_names = []
                    for inc in included:
                        inc_id = inc.get('item_id') or inc.get('id')
                        inc_qty = inc.get('qty') or inc.get('quantity') or 1
                        if inc_id:
                            inc_item = MenuItem.query.get(int(inc_id))
                            if inc_item:
                                included_names.append({'id': inc_item.id, 'name_he': inc_item.name_he, 'name_en': inc_item.name_en or '', 'qty': inc_qty})
                    deal_data['included_items'] = included_names
                oi.options_json = json.dumps(deal_data, ensure_ascii=False)
                verified_subtotal += oi.total_price
                db.session.add(oi)
                continue
            oi.menu_item_id = menu_item_id
            oi.item_name_he = item.get('name_he', item.get('name', ''))
            oi.item_name_en = item.get('name_en', '')
            oi.quantity = int(item.get('qty', 1))
            db_item = MenuItem.query.get(int(menu_item_id)) if menu_item_id else None
            if db_item and sel_branch_id:
                if not _is_item_available_for_branch(db_item.id, sel_branch_id):
                    continue
            elif db_item and not db_item.is_available:
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
            raw_excluded = item.get('excluded_ingredients', [])
            excluded_ingredients = []
            if isinstance(raw_excluded, list):
                for ei in raw_excluded:
                    if isinstance(ei, str):
                        cleaned = ei.strip()[:100]
                        if cleaned:
                            excluded_ingredients.append(cleaned)
                excluded_ingredients = excluded_ingredients[:20]
            combined_json = {}
            if item_options:
                combined_json['options'] = item_options
            if combo_selections:
                combined_json['combo_selections'] = combo_selections
            if excluded_ingredients:
                combined_json['excluded_ingredients'] = excluded_ingredients
            if combined_json:
                oi.options_json = json.dumps(combined_json if (combo_selections or excluded_ingredients) else item_options, ensure_ascii=False)
            verified_subtotal += oi.total_price
            db.session.add(oi)

        if verified_subtotal <= 0:
            db.session.rollback()
            flash('הפריטים שבחרת אינם זמינים כרגע.', 'warning')
            return redirect(url_for('order_page.order_page'))

        order.subtotal = verified_subtotal
        coupon_discount = 0.0
        coupon_code = request.form.get('coupon_code', '').strip()
        coupon_obj = None
        if coupon_code and Coupon:
            coupon_obj = Coupon.query.filter(db.func.upper(Coupon.code) == coupon_code.upper()).first()
            if coupon_obj and coupon_obj.is_valid():
                usage_identity = (customer_email or '').strip().lower()
                if coupon_obj.max_uses_per_email is not None:
                    if not usage_identity:
                        coupon_obj = None
                    elif not coupon_obj.can_be_used_by_email(usage_identity):
                        coupon_obj = None
                if coupon_obj and coupon_obj.minimum_order_amount and verified_subtotal < coupon_obj.minimum_order_amount:
                    coupon_obj = None
                if coupon_obj:
                    if coupon_obj.discount_type == 'percentage':
                        coupon_discount = verified_subtotal * (coupon_obj.discount_value / 100.0)
                        if coupon_obj.maximum_discount_amount:
                            coupon_discount = min(coupon_discount, coupon_obj.maximum_discount_amount)
                    elif coupon_obj.discount_type == 'fixed_amount':
                        coupon_discount = min(coupon_obj.discount_value, verified_subtotal)
                    coupon_discount = round(coupon_discount, 2)
            else:
                coupon_obj = None
        order.total_amount = verified_subtotal + delivery_fee - coupon_discount
        if coupon_discount > 0 and coupon_obj:
            order.coupon_code = coupon_obj.code
            order.coupon_discount = coupon_discount
            usage_identity = (customer_email or '').strip().lower()
            coupon_obj.record_usage(usage_identity)
            usage = CouponUsage.query.filter_by(coupon_id=coupon_obj.id).order_by(CouponUsage.id.desc()).first()
            if usage:
                usage.order_amount = verified_subtotal
                usage.discount_applied = coupon_discount
        db.session.commit()

        if OrderActivityLog:
            try:
                log = OrderActivityLog(
                    order_id=order.id,
                    action='order_created',
                    new_value='pending',
                    note=f'הזמנה חדשה #{order.order_number}',
                )
                db.session.add(log)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logging.warning(f"Failed to log order creation for #{order.order_number}: {e}")

        if payment_method == 'card':
            success_url = url_for('order_page.payment_success', _external=True) + f'?order={order.order_number}'
            failure_url = url_for('order_page.payment_failure', _external=True) + f'?order={order.order_number}'
            branch_prov = getattr(selected_branch, 'payment_provider', 'hyp') if selected_branch else 'hyp'

            def _try_max():
                if not max_payment:
                    return False
                try:
                    result = max_payment.create_payment(
                        order_id=order.order_number,
                        amount=order.total_amount,
                        success_url=success_url,
                        failure_url=failure_url,
                        customer_name=customer_name,
                        customer_email=customer_email,
                        customer_phone=customer_phone,
                        description=f'הזמנה {order.order_number}',
                        branch=selected_branch,
                        settings=settings,
                    )
                    if not result.get('error') and result.get('payment_url'):
                        order.hyp_order_ref = order.order_number
                        order.payment_provider = 'max'
                        if result.get('transaction_id'):
                            order.hyp_transaction_id = result['transaction_id']
                        db.session.commit()
                        return result['payment_url']
                    else:
                        logging.error(f"MAX Pay failed for #{order.order_number}: {result.get('message')}")
                except Exception as e:
                    logging.error(f"MAX Pay error for #{order.order_number}: {e}")
                return False

            def _try_hyp():
                if not hyp_payment:
                    return False
                try:
                    from standalone_order_service.hyp_payment import HYPPayment
                    hyp_local = HYPPayment(settings)
                    hyp_local._load_credentials(settings, branch=selected_branch)
                    if not hyp_local.is_configured:
                        return False
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
                    payment_url = hyp_local.create_payment_url(
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
                        order.payment_provider = 'hyp'
                        db.session.commit()
                        return payment_url
                except Exception as e:
                    logging.error(f"HYP payment failed for #{order.order_number}: {e}")
                return False

            payment_url = False
            if branch_prov == 'max':
                payment_url = _try_max()
                if not payment_url:
                    payment_url = _try_hyp()
            else:
                payment_url = _try_hyp()
                if not payment_url:
                    payment_url = _try_max()

            if payment_url:
                return render_template('hyp_redirect.html', payment_url=payment_url, order=order)

        if notifier:
            try:
                notifier.notify_new_order(order, settings)
            except Exception as e:
                logging.warning(f"Notification failed for #{order.order_number}: {e}")
            try:
                notifier.send_customer_confirmation(order, settings)
            except Exception as e:
                logging.warning(f"Customer SMS failed for #{order.order_number}: {e}")

        try:
            from ops_routes import _notify_sse_new_order
            items = json.loads(order.items_json) if order.items_json else []
            _notify_sse_new_order({
                'type': 'new_order',
                'id': order.id,
                'order_number': order.order_number,
                'order_type': order.order_type,
                'branch_id': order.branch_id,
                'customer_name': order.customer_name or '',
                'total_amount': order.total_amount or 0,
                'items_count': len(items),
                'created_at': order.created_at.isoformat() + 'Z' if order.created_at else '',
            })
        except Exception as e:
            logging.debug(f"SSE notify: {e}")

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
            'confirmed_at': _to_il_hour(order.confirmed_at),
            'ready_at': _to_il_hour(order.ready_at),
            'preparing_at': _to_il_hour(order.preparing_at),
            'estimated_ready_at': _to_il_hour(order.estimated_ready_at),
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

    def _confirm_paid_order(order, settings, transaction_id=None):
        order.payment_status = 'paid'
        if transaction_id:
            order.hyp_transaction_id = transaction_id
        if order.status == 'pending':
            old_status = order.status
            order.status = 'confirmed'
            order.confirmed_at = datetime.utcnow()
            if OrderActivityLog:
                log = OrderActivityLog(
                    order_id=order.id,
                    action='status_change',
                    old_value=old_status,
                    new_value='confirmed',
                    note='תשלום אושר - סטטוס עודכן אוטומטית',
                )
                db.session.add(log)
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
        try:
            from ops_routes import _notify_sse_new_order
            items = json.loads(order.items_json) if order.items_json else []
            _notify_sse_new_order({
                'type': 'new_order',
                'id': order.id,
                'order_number': order.order_number,
                'order_type': order.order_type,
                'branch_id': order.branch_id,
                'customer_name': order.customer_name or '',
                'total_amount': order.total_amount or 0,
                'items_count': len(items),
                'created_at': order.created_at.isoformat() + 'Z' if order.created_at else '',
            })
        except Exception:
            pass

    def _fail_payment(order):
        order.payment_status = 'failed'
        if OrderActivityLog:
            log = OrderActivityLog(
                order_id=order.id,
                action='payment_failed',
                note='תשלום נכשל',
            )
            db.session.add(log)
        db.session.commit()

    @bp.route('/payment-success')
    def payment_success():
        order_number = request.args.get('Order') or request.args.get('order') or ''
        settings = _settings()
        if order_number:
            order = FoodOrder.query.filter_by(order_number=order_number).first()
            if order:
                if order.payment_status == 'paid':
                    return redirect(url_for('order_page.order_confirmation', order_number=order_number))

                if getattr(order, 'payment_provider', None) == 'max' and max_payment:
                    tid = request.args.get('transactionId') or request.args.get('transaction_id') or request.args.get('Id')
                    if tid:
                        branch_obj = Branch.query.get(order.branch_id) if order.branch_id else None
                        verification = max_payment.verify_payment(tid, branch=branch_obj, settings=settings)
                        if verification and verification.get('status') in ('completed', 'approved', 'success', 'paid'):
                            v_amount = verification.get('amount') or verification.get('total') or verification.get('sum')
                            v_order = verification.get('order_id') or verification.get('orderId') or verification.get('reference')
                            amount_ok = True
                            order_ok = True
                            if v_amount is not None:
                                try:
                                    amount_ok = abs(float(v_amount) - float(order.total_amount)) < 0.01
                                except (ValueError, TypeError):
                                    amount_ok = False
                            if v_order is not None:
                                order_ok = str(v_order) == str(order.order_number)
                            if amount_ok and order_ok:
                                _confirm_paid_order(order, settings, transaction_id=tid)
                                return redirect(url_for('order_page.order_confirmation', order_number=order_number))
                            else:
                                logging.error(f"MAX Pay binding mismatch for #{order_number}: expected amount={order.total_amount} got={v_amount}, expected order={order.order_number} got={v_order}")
                                _fail_payment(order)
                                return redirect(url_for('order_page.payment_failure') + f'?order={order_number}')
                        else:
                            logging.warning(f"MAX Pay verification failed for #{order_number}, tid={tid}, result={verification}")
                            _fail_payment(order)
                            return redirect(url_for('order_page.payment_failure') + f'?order={order_number}')
                    else:
                        logging.warning(f"MAX Pay callback missing transaction ID for #{order_number}")
                        _fail_payment(order)
                        return redirect(url_for('order_page.payment_failure') + f'?order={order_number}')

                if hyp_payment:
                    from standalone_order_service.hyp_payment import HYPPayment
                    branch_obj = Branch.query.get(order.branch_id) if order.branch_id else None
                    hyp_local = HYPPayment(settings)
                    hyp_local._load_credentials(settings, branch=branch_obj)
                    verification = hyp_local.verify_payment_response(
                        dict(request.args),
                        expected_order_id=order.hyp_order_ref or order.order_number,
                        expected_amount=order.total_amount,
                    )
                    if verification.get('verified') and verification.get('success'):
                        tid = verification.get('transaction_id') or request.args.get('Id')
                        _confirm_paid_order(order, settings, transaction_id=tid)
                        return redirect(url_for('order_page.order_confirmation', order_number=order_number))
                    else:
                        _fail_payment(order)
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
