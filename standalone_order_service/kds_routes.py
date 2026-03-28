"""
KDS (Kitchen Display System) / Order Dashboard Routes (Blueprint).

Register this blueprint in your Flask app::

    from standalone_order_service.kds_routes import create_kds_blueprint
    kds_bp = create_kds_blueprint(db, models, send_sms_fn)
    app.register_blueprint(kds_bp)

Authentication uses the ManagerPIN model (PIN-based login for staff).
"""

import json
import logging
import time
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Blueprint, render_template, request, session, redirect,
    url_for, jsonify, flash,
)


STATUS_FLOW = {
    'pending': 'confirmed',
    'confirmed': 'preparing',
    'preparing': 'ready',
    'ready': None,
}

STATUS_LABELS = {
    'pending': 'ממתין',
    'confirmed': 'אושר',
    'preparing': 'בהכנה',
    'ready': 'מוכן',
    'delivered': 'נמסר',
    'pickedup': 'נאסף',
    'cancelled': 'בוטל',
}


def create_kds_blueprint(db, models, send_sms=None, get_settings=None, clear_cache=None):
    """
    Factory that returns a configured KDS Blueprint.

    Parameters
    ----------
    db : flask_sqlalchemy.SQLAlchemy
    models : dict
        Model classes returned by ``register_models(db)``.
    send_sms : callable, optional
        ``(phone, message) -> bool`` for custom SMS from KDS.
    get_settings : callable, optional
    clear_cache : callable, optional
        Called after settings changes to invalidate caches.
    """
    bp = Blueprint(
        'order_dashboard',
        __name__,
        template_folder='templates/order_dashboard',
        url_prefix='/order-dashboard',
    )

    FoodOrder = models['FoodOrder']
    ManagerPIN = models['ManagerPIN']
    MenuItem = models['MenuItem']
    MenuItemOptionGroup = models['MenuItemOptionGroup']
    MenuItemOptionChoice = models['MenuItemOptionChoice']
    MenuItemPrice = models['MenuItemPrice']
    WorkingHours = models['WorkingHours']
    Branch = models['Branch']
    OrderActivityLog = models.get('OrderActivityLog')
    SMSLog = models.get('SMSLog')

    def _settings():
        if get_settings:
            return get_settings()
        return None

    def _get_israel_now():
        try:
            from zoneinfo import ZoneInfo
            return datetime.now(ZoneInfo('Asia/Jerusalem'))
        except Exception:
            return datetime.now()

    def _authenticated():
        return session.get('order_dashboard_authenticated', False)

    def require_auth(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not _authenticated():
                return redirect(url_for('order_dashboard.login_page'))
            return f(*args, **kwargs)
        return decorated

    # ── Auth ──────────────────────────────────────────────────────────

    @bp.route('/')
    def index():
        if _authenticated():
            return redirect(url_for('order_dashboard.orders'))
        return redirect(url_for('order_dashboard.login_page'))

    @bp.route('/login')
    def login_page():
        if _authenticated():
            return redirect(url_for('order_dashboard.orders'))
        staff = ManagerPIN.query.filter_by(is_active=True).order_by(ManagerPIN.name).all()
        return render_template('login.html', staff_members=staff)

    @bp.route('/auth', methods=['POST'])
    def authenticate():
        from werkzeug.security import check_password_hash
        pin_id = request.form.get('pin_id', '').strip()
        pin = request.form.get('pin', '').strip()
        if not pin:
            return jsonify({'success': False, 'message': 'נא להזין קוד PIN'})
        staff = None
        if pin_id:
            try:
                pin_id_int = int(pin_id)
            except (ValueError, TypeError):
                return jsonify({'success': False, 'message': 'קוד PIN לא תקין'})
            staff = ManagerPIN.query.filter_by(id=pin_id_int, is_active=True).first()
        else:
            staff = ManagerPIN.query.filter_by(is_active=True).first()
        if not staff:
            return jsonify({'success': False, 'message': 'משתמש לא נמצא'})
        try:
            pin_ok = check_password_hash(staff.pin_hash, pin)
        except Exception:
            pin_ok = False
        if not pin_ok:
            return jsonify({'success': False, 'message': 'קוד PIN שגוי'})
        session['order_dashboard_authenticated'] = True
        session['order_dashboard_staff_name'] = staff.name
        session['order_dashboard_staff_id'] = staff.id
        session.permanent = True
        return jsonify({'success': True, 'redirect': url_for('order_dashboard.orders')})

    @bp.route('/logout')
    def logout():
        session.pop('order_dashboard_authenticated', None)
        session.pop('order_dashboard_staff_name', None)
        session.pop('order_dashboard_staff_id', None)
        return redirect(url_for('order_dashboard.login_page'))

    # ── Orders list ───────────────────────────────────────────────────

    @bp.route('/orders')
    @require_auth
    def orders():
        settings = _settings()
        status_filter = request.args.get('status', 'active')
        date_str = request.args.get('date', '')
        branch_filter = request.args.get('branch_id', '')
        now = _get_israel_now()
        today = now.date()
        if date_str:
            try:
                selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                selected_date = today
        else:
            selected_date = today
        q = FoodOrder.query.filter(
            FoodOrder.created_at >= datetime.combine(selected_date, datetime.min.time()),
            FoodOrder.created_at < datetime.combine(selected_date + timedelta(days=1), datetime.min.time())
        )
        if branch_filter:
            try:
                q = q.filter(FoodOrder.branch_id == int(branch_filter))
            except (ValueError, TypeError):
                pass
        all_today = q.order_by(FoodOrder.created_at.desc()).all()
        if status_filter == 'active':
            orders_list = [o for o in all_today if o.status not in ('delivered', 'pickedup', 'cancelled')]
        elif status_filter == 'all':
            orders_list = all_today
        else:
            orders_list = [o for o in all_today if o.status == status_filter]

        all_branches = Branch.query.filter_by(is_active=True).order_by(Branch.display_order).all()
        return render_template('orders.html',
                               orders=orders_list,
                               all_today=all_today,
                               new_orders=[o for o in all_today if o.status == 'pending'],
                               prep_orders=[o for o in all_today if o.status in ('confirmed', 'preparing')],
                               ready_orders=[o for o in all_today if o.status == 'ready'],
                               done_orders=list(reversed([o for o in all_today if o.status in ('delivered', 'pickedup', 'cancelled')])),
                               status_filter=status_filter,
                               selected_date=selected_date,
                               today=today,
                               prev_date=(selected_date - timedelta(days=1)).strftime('%Y-%m-%d'),
                               next_date=(selected_date + timedelta(days=1)).strftime('%Y-%m-%d'),
                               now_ts=int(time.time()),
                               total_today=len(all_today),
                               pending_count=sum(1 for o in all_today if o.status == 'pending'),
                               active_count=sum(1 for o in all_today if o.status not in ('delivered', 'pickedup', 'cancelled')),
                               revenue_today=sum(o.total_amount for o in all_today if o.status != 'cancelled'),
                               settings=settings,
                               ordering_paused=getattr(settings, 'ordering_paused', False) if settings else False,
                               staff_name=session.get('order_dashboard_staff_name', ''),
                               branches=all_branches,
                               branch_filter=branch_filter)

    # ── Order detail ──────────────────────────────────────────────────

    @bp.route('/orders/<int:order_id>')
    @require_auth
    def order_detail(order_id):
        settings = _settings()
        order = FoodOrder.query.get_or_404(order_id)
        return render_template('order_detail.html',
                               order=order,
                               items=order.get_items(),
                               settings=settings,
                               staff_name=session.get('order_dashboard_staff_name', ''))

    # ── Status update ─────────────────────────────────────────────────

    @bp.route('/orders/<int:order_id>/update-status', methods=['POST'])
    @require_auth
    def update_status(order_id):
        order = FoodOrder.query.get_or_404(order_id)
        new_status = request.form.get('status') or (request.json.get('status') if request.is_json else None)
        admin_note = request.form.get('admin_note', '').strip()[:500]
        valid = ['pending', 'confirmed', 'preparing', 'ready', 'delivered', 'pickedup', 'cancelled']
        if new_status not in valid:
            return jsonify({'success': False, 'error': 'Invalid status'})
        old_status = order.status
        order.status = new_status
        now = datetime.utcnow()
        prep_minutes = 0
        try:
            prep_minutes = int(request.form.get('prep_minutes', 0))
        except (ValueError, TypeError):
            pass
        if new_status == 'confirmed' and not order.confirmed_at:
            order.confirmed_at = now
            if prep_minutes > 0:
                order.estimated_ready_at = now + timedelta(minutes=prep_minutes)
        elif new_status == 'preparing' and not order.preparing_at:
            order.preparing_at = now
            if prep_minutes > 0:
                order.estimated_ready_at = now + timedelta(minutes=prep_minutes)
        elif new_status == 'ready' and not order.ready_at:
            order.ready_at = now
        elif new_status in ('delivered', 'pickedup') and not order.completed_at:
            order.completed_at = now
        elif new_status == 'cancelled' and not order.cancelled_at:
            order.cancelled_at = now
        if admin_note:
            existing = order.admin_notes or ''
            ts = _get_israel_now().strftime('%d/%m %H:%M')
            staff = session.get('order_dashboard_staff_name', 'צוות')
            order.admin_notes = f"{existing}\n[{ts} - {staff}]: {admin_note}".strip()
        if OrderActivityLog:
            log = OrderActivityLog(
                order_id=order.id,
                action='status_change',
                old_value=old_status,
                new_value=new_status,
                staff_name=session.get('order_dashboard_staff_name', 'צוות'),
                note=admin_note or None,
            )
            db.session.add(log)
        db.session.commit()
        return jsonify({'success': True, 'new_status': new_status, 'status_label': STATUS_LABELS.get(new_status, new_status)})

    # ── Add note ──────────────────────────────────────────────────────

    @bp.route('/orders/<int:order_id>/add-note', methods=['POST'])
    @require_auth
    def add_note(order_id):
        order = FoodOrder.query.get_or_404(order_id)
        note = request.form.get('note', '').strip()
        if note:
            ts = _get_israel_now().strftime('%d/%m %H:%M')
            staff = session.get('order_dashboard_staff_name', 'צוות')
            existing = order.admin_notes or ''
            order.admin_notes = f"{existing}\n[{ts} - {staff}]: {note}".strip()
            db.session.commit()
        return redirect(url_for('order_dashboard.order_detail', order_id=order_id))

    # ── Send custom SMS ───────────────────────────────────────────────

    @bp.route('/orders/<int:order_id>/send-sms', methods=['POST'])
    @require_auth
    def send_sms_route(order_id):
        order = FoodOrder.query.get_or_404(order_id)
        message = request.form.get('message', '').strip()[:500]
        if not message:
            flash('נא להזין הודעה.', 'warning')
            return redirect(url_for('order_dashboard.order_detail', order_id=order_id))
        staff_name = session.get('order_dashboard_staff_name', 'צוות')
        if send_sms:
            try:
                result = send_sms(order.customer_phone, message)
                ts = _get_israel_now().strftime('%d/%m %H:%M')
                if SMSLog:
                    sms_log = SMSLog(
                        order_id=order.id,
                        recipient_phone=order.customer_phone,
                        message_type='custom_kds',
                        message_text=message,
                        provider='sms4free',
                        status='sent' if result else 'failed',
                        staff_name=staff_name,
                    )
                    db.session.add(sms_log)
                if result:
                    existing = order.admin_notes or ''
                    order.admin_notes = f"{existing}\n[{ts} - {staff_name}] SMS נשלח: {message}".strip()
                    db.session.commit()
                    flash('SMS נשלח ללקוח.', 'success')
                else:
                    db.session.commit()
                    flash('שליחת SMS נכשלה.', 'danger')
            except Exception as e:
                logging.error(f"KDS send_sms error: {e}")
                if SMSLog:
                    sms_log = SMSLog(
                        order_id=order.id,
                        recipient_phone=order.customer_phone,
                        message_type='custom_kds',
                        message_text=message,
                        provider='sms4free',
                        status='failed',
                        error_message=str(e)[:500],
                        staff_name=staff_name,
                    )
                    db.session.add(sms_log)
                    db.session.commit()
                flash('שגיאה בשליחת SMS.', 'danger')
        else:
            flash('SMS לא מוגדר.', 'warning')
        return redirect(url_for('order_dashboard.order_detail', order_id=order_id))

    # ── Cancel order ──────────────────────────────────────────────────

    @bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
    @require_auth
    def cancel_order(order_id):
        order = FoodOrder.query.get_or_404(order_id)
        reason = request.form.get('reason', '').strip()[:500]
        old_status = order.status
        order.status = 'cancelled'
        order.cancelled_at = datetime.utcnow()
        staff_name = session.get('order_dashboard_staff_name', 'צוות')
        if reason:
            ts = _get_israel_now().strftime('%d/%m %H:%M')
            existing = order.admin_notes or ''
            order.admin_notes = f"{existing}\n[{ts} - {staff_name}] בוטל: {reason}".strip()
        if OrderActivityLog:
            log = OrderActivityLog(
                order_id=order.id,
                action='cancelled',
                old_value=old_status,
                new_value='cancelled',
                staff_name=staff_name,
                note=reason or None,
            )
            db.session.add(log)
        db.session.commit()
        flash(f'הזמנה #{order.order_number} בוטלה.', 'info')
        return redirect(url_for('order_dashboard.orders'))

    # ── Live feed ─────────────────────────────────────────────────────

    @bp.route('/orders/feed')
    @require_auth
    def orders_feed():
        now = _get_israel_now()
        today = now.date()
        ords = FoodOrder.query.filter(
            FoodOrder.created_at >= datetime.combine(today, datetime.min.time())
        ).order_by(FoodOrder.created_at.desc()).all()
        return jsonify([{
            'id': o.id,
            'order_number': o.order_number,
            'customer_name': o.customer_name,
            'customer_phone': o.customer_phone,
            'order_type': o.order_type,
            'status': o.status,
            'status_label': STATUS_LABELS.get(o.status, o.status),
            'total_amount': o.total_amount,
            'pickup_time': o.pickup_time or '',
            'created_at': o.created_at.strftime('%H:%M') if o.created_at else '',
        } for o in ords])

    # ── Settings ──────────────────────────────────────────────────────

    @bp.route('/settings', methods=['GET', 'POST'])
    @require_auth
    def settings_page():
        site_settings = _settings()

        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'toggle_pause':
                site_settings.ordering_paused = not site_settings.ordering_paused
                db.session.commit()
                if clear_cache:
                    clear_cache()
                return jsonify({'success': True, 'paused': site_settings.ordering_paused})
            if action == 'toggle_ordering':
                site_settings.enable_online_ordering = not site_settings.enable_online_ordering
                db.session.commit()
                if clear_cache:
                    clear_cache()
                return jsonify({'success': True, 'enabled': site_settings.enable_online_ordering})
            if action == 'toggle_delivery':
                site_settings.enable_delivery = not site_settings.enable_delivery
                db.session.commit()
                if clear_cache:
                    clear_cache()
                return jsonify({'success': True, 'enabled': site_settings.enable_delivery})
            if action == 'toggle_pickup':
                site_settings.enable_pickup = not site_settings.enable_pickup
                db.session.commit()
                if clear_cache:
                    clear_cache()
                return jsonify({'success': True, 'enabled': site_settings.enable_pickup})
            if action == 'toggle_enforce_hours':
                site_settings.enforce_ordering_hours = not site_settings.enforce_ordering_hours
                db.session.commit()
                if clear_cache:
                    clear_cache()
                return jsonify({'success': True, 'enabled': site_settings.enforce_ordering_hours})
            if action == 'save_messages':
                paused_msg = request.form.get('ordering_paused_message', '').strip()
                closed_msg = request.form.get('ordering_closed_message', '').strip()
                outside_msg = request.form.get('ordering_outside_hours_message', '').strip()
                if paused_msg:
                    site_settings.ordering_paused_message = paused_msg
                if closed_msg:
                    site_settings.ordering_closed_message = closed_msg
                if outside_msg:
                    site_settings.ordering_outside_hours_message = outside_msg
                site_settings.enforce_ordering_hours = request.form.get('enforce_ordering_hours') == '1'
                db.session.commit()
                if clear_cache:
                    clear_cache()
                return jsonify({'success': True, 'message': 'ההודעות נשמרו'})
            if action == 'update_delivery_time':
                val = request.form.get('estimated_delivery_time', '').strip()
                if val:
                    site_settings.estimated_delivery_time = val
                    db.session.commit()
                return jsonify({'success': True})
            if action == 'save_working_hours':
                branches = Branch.query.filter_by(is_active=True).all()
                branch_id = branches[0].id if branches else None
                if branch_id:
                    for d in range(7):
                        is_closed = request.form.get(f'closed_{d}') == '1'
                        open_time = request.form.get(f'open_{d}', '09:00').strip() or '09:00'
                        close_time = request.form.get(f'close_{d}', '22:00').strip() or '22:00'
                        wh = WorkingHours.query.filter_by(branch_id=branch_id, day_of_week=d).first()
                        if wh:
                            wh.is_closed = is_closed
                            wh.open_time = open_time
                            wh.close_time = close_time
                        else:
                            wh = WorkingHours(
                                branch_id=branch_id, day_of_week=d,
                                is_closed=is_closed, open_time=open_time, close_time=close_time
                            )
                            db.session.add(wh)
                    db.session.commit()
                    return jsonify({'success': True, 'message': 'שעות הפעילות נשמרו'})
                return jsonify({'success': False, 'message': 'לא נמצא סניף פעיל'})
            if action == 'toggle_tracking':
                site_settings.send_order_tracking_link = not getattr(site_settings, 'send_order_tracking_link', True)
                db.session.commit()
                return jsonify({'success': True, 'enabled': site_settings.send_order_tracking_link})
            db.session.commit()
            flash('הגדרות נשמרו.', 'success')
            return redirect(url_for('order_dashboard.settings_page'))

        now = _get_israel_now()
        db_dow = (now.weekday() + 1) % 7
        branches = Branch.query.filter_by(is_active=True).all()
        branch_id = branches[0].id if branches else None
        all_hours = {}
        if branch_id:
            for wh in WorkingHours.query.filter_by(branch_id=branch_id).all():
                all_hours[wh.day_of_week] = wh
        today_hours = all_hours.get(db_dow)
        day_names_he = ['ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת']
        days_list = []
        for d in range(7):
            wh = all_hours.get(d)
            days_list.append({
                'day': d,
                'name': day_names_he[d],
                'is_today': d == db_dow,
                'is_closed': wh.is_closed if wh else True,
                'open_time': wh.open_time if wh else '09:00',
                'close_time': wh.close_time if wh else '22:00',
            })
        time_slots = []
        for h in range(24):
            for m in (0, 15, 30, 45):
                time_slots.append(f'{h:02d}:{m:02d}')

        order_dishes = MenuItem.query.filter(
            db.or_(MenuItem.show_in_order == True, MenuItem.show_in_order.is_(None))
        ).order_by(MenuItem.display_order).all()
        return render_template('settings.html',
                               settings=site_settings,
                               today_hours=today_hours,
                               days_list=days_list,
                               branch_id=branch_id,
                               time_slots=time_slots,
                               order_dishes=order_dishes,
                               staff_name=session.get('order_dashboard_staff_name', ''))

    # ── Dish management ───────────────────────────────────────────────

    @bp.route('/dishes/toggle-availability', methods=['POST'])
    @require_auth
    def toggle_dish_availability():
        item_id = request.form.get('item_id')
        item = MenuItem.query.get_or_404(item_id)
        item.is_available = not item.is_available
        db.session.commit()
        if clear_cache:
            clear_cache()
        return jsonify({'success': True, 'is_available': item.is_available})

    @bp.route('/dishes/update-days', methods=['POST'])
    @require_auth
    def update_dish_days():
        item_id = request.form.get('item_id')
        item = MenuItem.query.get_or_404(item_id)
        days = request.form.get('available_days', '1111111')
        if len(days) == 7 and all(c in '01' for c in days):
            item.available_days = days
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Invalid days format'})

    @bp.route('/dishes/update-times', methods=['POST'])
    @require_auth
    def update_dish_times():
        import re
        item_id = request.form.get('item_id')
        item = MenuItem.query.get_or_404(item_id)
        from_time = request.form.get('available_from_time', '').strip()
        to_time = request.form.get('available_to_time', '').strip()
        time_re = re.compile(r'^\d{2}:\d{2}$')
        item.available_from_time = from_time if from_time and time_re.match(from_time) else None
        item.available_to_time = to_time if to_time and time_re.match(to_time) else None
        db.session.commit()
        return jsonify({'success': True})

    @bp.route('/dishes/update-price', methods=['POST'])
    @require_auth
    def update_dish_price():
        item_id = request.form.get('item_id')
        item = MenuItem.query.get_or_404(item_id)
        try:
            price = float(request.form.get('price', 0))
            if price < 0:
                return jsonify({'success': False, 'error': 'Invalid price'})
            item.base_price = price
            db.session.commit()
            return jsonify({'success': True, 'price': price})
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Invalid price'})

    # ── Dish detail & option group management ────────────────────────

    @bp.route('/dishes/<int:item_id>/detail', methods=['GET'])
    @require_auth
    def dish_detail(item_id):
        item = MenuItem.query.get_or_404(item_id)
        groups = []
        for g in item.option_groups:
            choices = [{
                'id': c.id, 'name_he': c.name_he, 'name_en': c.name_en,
                'price_modifier': c.price_modifier, 'is_available': c.is_available,
                'is_default': c.is_default, 'display_order': c.display_order
            } for c in g.choices]
            groups.append({
                'id': g.id, 'name_he': g.name_he, 'name_en': g.name_en,
                'selection_type': g.selection_type, 'is_required': g.is_required,
                'min_selections': g.min_selections, 'max_selections': g.max_selections,
                'is_active': g.is_active, 'display_order': g.display_order,
                'choices': choices
            })
        prices = [{
            'id': p.id, 'size_name_he': p.size_name_he, 'size_name_en': p.size_name_en,
            'price': p.price, 'is_default': p.is_default, 'display_order': p.display_order
        } for p in item.price_options]
        return jsonify({
            'success': True,
            'item': {
                'id': item.id, 'name_he': item.name_he, 'name_en': item.name_en or '',
                'base_price': item.base_price, 'is_available': item.is_available,
                'available_days': item.available_days or '1111111',
                'available_from_time': item.available_from_time or '',
                'available_to_time': item.available_to_time or '',
                'image_path': item.image_path or '',
            },
            'option_groups': groups,
            'prices': prices
        })

    @bp.route('/dishes/option-group/save', methods=['POST'])
    @require_auth
    def save_option_group():
        data = request.get_json() if request.is_json else {}
        item_id = data.get('menu_item_id')
        group_id = data.get('id')
        if group_id:
            group = MenuItemOptionGroup.query.get_or_404(group_id)
        else:
            group = MenuItemOptionGroup(menu_item_id=item_id)
            db.session.add(group)
        group.name_he = data.get('name_he', '')
        group.name_en = data.get('name_en', '')
        group.selection_type = data.get('selection_type', 'single')
        group.is_required = data.get('is_required', False)
        group.min_selections = int(data.get('min_selections', 0))
        group.max_selections = int(data.get('max_selections', 0))
        group.display_order = int(data.get('display_order', 0))
        group.is_active = data.get('is_active', True)
        existing_choice_ids = {c.id for c in group.choices} if group_id else set()
        submitted_ids = set()
        for c_data in data.get('choices', []):
            cid = c_data.get('id')
            if cid and cid in existing_choice_ids:
                choice = MenuItemOptionChoice.query.get(cid)
                submitted_ids.add(cid)
            else:
                choice = MenuItemOptionChoice(option_group_id=group.id if group_id else None)
                db.session.add(choice)
            choice.name_he = c_data.get('name_he', '')
            choice.name_en = c_data.get('name_en', '')
            choice.price_modifier = float(c_data.get('price_modifier', 0))
            choice.is_available = c_data.get('is_available', True)
            choice.is_default = c_data.get('is_default', False)
            choice.display_order = int(c_data.get('display_order', 0))
            if not group_id:
                choice.option_group = group
        for old_id in existing_choice_ids - submitted_ids:
            old_choice = MenuItemOptionChoice.query.get(old_id)
            if old_choice:
                db.session.delete(old_choice)
        db.session.commit()
        return jsonify({'success': True, 'group_id': group.id})

    @bp.route('/dishes/option-group/<int:group_id>/delete', methods=['POST'])
    @require_auth
    def delete_option_group(group_id):
        group = MenuItemOptionGroup.query.get_or_404(group_id)
        db.session.delete(group)
        db.session.commit()
        return jsonify({'success': True})

    @bp.route('/dishes/price-variant/save', methods=['POST'])
    @require_auth
    def save_price_variant():
        data = request.get_json() if request.is_json else {}
        variant_id = data.get('id')
        if variant_id:
            pv = MenuItemPrice.query.get_or_404(variant_id)
        else:
            pv = MenuItemPrice(menu_item_id=data.get('menu_item_id'))
            db.session.add(pv)
        pv.size_name_he = data.get('size_name_he', '')
        pv.size_name_en = data.get('size_name_en', '')
        pv.price = float(data.get('price', 0))
        pv.is_default = data.get('is_default', False)
        pv.display_order = int(data.get('display_order', 0))
        db.session.commit()
        return jsonify({'success': True, 'id': pv.id})

    @bp.route('/dishes/price-variant/<int:variant_id>/delete', methods=['POST'])
    @require_auth
    def delete_price_variant(variant_id):
        pv = MenuItemPrice.query.get_or_404(variant_id)
        db.session.delete(pv)
        db.session.commit()
        return jsonify({'success': True})

    @bp.route('/dishes/toggle-tracking', methods=['POST'])
    @require_auth
    def toggle_tracking_link():
        site_settings = _settings()
        if site_settings:
            site_settings.send_order_tracking_link = not getattr(site_settings, 'send_order_tracking_link', True)
            db.session.commit()
            return jsonify({'success': True, 'enabled': site_settings.send_order_tracking_link})
        return jsonify({'success': False})

    # ── Statistics ────────────────────────────────────────────────────

    @bp.route('/statistics')
    @require_auth
    def statistics():
        now = _get_israel_now()
        today = now.date()
        days_data = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            day_orders = FoodOrder.query.filter(
                FoodOrder.created_at >= datetime.combine(d, datetime.min.time()),
                FoodOrder.created_at < datetime.combine(d + timedelta(days=1), datetime.min.time()),
                FoodOrder.status != 'cancelled'
            ).all()
            days_data.append({
                'date': d.strftime('%d/%m'),
                'count': len(day_orders),
                'revenue': sum(o.total_amount for o in day_orders),
            })
        month_start = today - timedelta(days=30)
        month_orders = FoodOrder.query.filter(
            FoodOrder.created_at >= datetime.combine(month_start, datetime.min.time()),
            FoodOrder.status != 'cancelled'
        ).all()
        month_revenue = sum(o.total_amount for o in month_orders)
        month_count = len(month_orders)
        avg_order = (month_revenue / month_count) if month_count else 0
        item_counts = {}
        for o in month_orders:
            for item in o.get_items():
                name = item.get('name_he') or item.get('name_en') or 'פריט'
                item_counts[name] = item_counts.get(name, 0) + item.get('qty', 1)
        top_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:8]
        today_orders = FoodOrder.query.filter(
            FoodOrder.created_at >= datetime.combine(today, datetime.min.time()),
        ).all()
        return render_template('statistics.html',
                               days_data=days_data,
                               month_revenue=month_revenue,
                               month_count=month_count,
                               avg_order=avg_order,
                               top_items=top_items,
                               delivery_count=sum(1 for o in today_orders if o.order_type == 'delivery'),
                               pickup_count=sum(1 for o in today_orders if o.order_type != 'delivery'),
                               cash_count=sum(1 for o in today_orders if o.payment_method == 'cash'),
                               card_count=sum(1 for o in today_orders if o.payment_method == 'card'),
                               staff_name=session.get('order_dashboard_staff_name', ''),
                               today=today)

    return bp
