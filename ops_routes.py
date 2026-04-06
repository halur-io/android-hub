import json
import logging
import os
import secrets
import socket
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Blueprint, render_template, request, session, redirect,
    url_for, jsonify, make_response, flash,
)
from database import db


def _is_secure():
    return request.is_secure or request.headers.get('X-Forwarded-Proto') == 'https' or os.environ.get('REPL_SLUG')
from models import (
    ManagerPIN, EnrolledDevice, SiteSettings, Branch, WorkingHours,
    MenuCategory, MenuItem, BranchMenuItem, StockItem, StockLevel, StockTransaction,
    StockAlert, Deal, Coupon, CouponUsage, FoodOrder,
    Printer, PrinterStation, PrintStation, TimeLog,
)
from services.order.order_service import DeliveryZone

ops_bp = Blueprint(
    'ops',
    __name__,
    template_folder='templates/ops',
    url_prefix='/ops',
)

def _settings():
    return SiteSettings.query.first()

def _get_israel_now():
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo('Asia/Jerusalem'))
    except Exception:
        return datetime.now()

def _check_device():
    token = request.cookies.get('ops_device_token')
    if not token:
        return None
    device = EnrolledDevice.query.filter_by(device_token=token, is_active=True).first()
    if device:
        device.last_seen = datetime.utcnow()
        device.user_agent = request.headers.get('User-Agent', '')[:500]
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
    return device

def _get_ops_user():
    import logging
    pin_id = session.get('ops_pin_id')
    if pin_id:
        user = ManagerPIN.query.filter_by(id=pin_id, is_active=True).first()
        if user:
            if 'ops_branch_id' not in session:
                session['ops_branch_id'] = getattr(user, 'branch_id', None)
                session.modified = True
            return user
        else:
            logging.debug(f'OPS: session pin_id={pin_id} not found in DB')
    device = _check_device()
    if device and device.last_pin_id:
        logging.debug(f'OPS: restoring session from device {device.id}, last_pin_id={device.last_pin_id}')
        user = ManagerPIN.query.filter_by(id=device.last_pin_id, is_active=True).first()
        if user:
            session['ops_pin_id'] = user.id
            session['ops_user_name'] = user.name
            session['ops_branch_id'] = getattr(user, 'branch_id', None)
            session.modified = True
            logging.debug(f'OPS: session restored for user {user.name}')
            return user
    elif device:
        logging.debug(f'OPS: device found but no last_pin_id')
    else:
        logging.debug(f'OPS: no device found from cookie')
    return None

def require_device(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        device = _check_device()
        if not device:
            return redirect(url_for('ops.not_enrolled'))
        return f(*args, **kwargs)
    return decorated

def require_ops_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        device = _check_device()
        if not device:
            return redirect(url_for('ops.not_enrolled'))
        user = _get_ops_user()
        if not user:
            return redirect(url_for('ops.login'))
        return f(*args, **kwargs)
    return decorated

def require_ops_module(module_name):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            device = _check_device()
            if not device:
                return redirect(url_for('ops.not_enrolled'))
            user = _get_ops_user()
            if not user:
                return redirect(url_for('ops.login'))
            if not user.has_ops_permission(module_name):
                if request.is_json:
                    return jsonify({'ok': False, 'error': 'אין הרשאה'}), 403
                modules = user.get_ops_modules()
                if modules:
                    return redirect(url_for('ops.' + modules[0]))
                return render_template('ops/not_enrolled.html', enrollment_code=None), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

def _get_effective_branch_id():
    worker_branch = session.get('ops_branch_id')
    if worker_branch:
        return worker_branch
    return None

@ops_bp.context_processor
def inject_ops_context():
    user = _get_ops_user()
    modules = user.get_ops_modules() if user else []
    branch_id = _get_effective_branch_id()
    branch_name = ''
    if branch_id:
        branch = Branch.query.get(branch_id)
        if branch:
            branch_name = branch.name_he
    is_ops_superadmin = user.is_ops_superadmin if user else False
    all_branches = Branch.query.filter_by(is_active=True).all() if is_ops_superadmin else []
    return dict(
        ops_modules=modules,
        ops_user=user,
        ops_branch_id=branch_id,
        ops_branch_name=branch_name,
        is_ops_superadmin=is_ops_superadmin,
        can_switch_branch=is_ops_superadmin,
        all_branches=all_branches,
    )


@ops_bp.route('/switch-branch', methods=['POST'])
def switch_branch():
    user = _get_ops_user()
    if not user or not user.is_ops_superadmin:
        return jsonify({'ok': False, 'error': 'אין הרשאה'})
    data = request.get_json(force=True)
    new_branch = data.get('branch_id')
    if new_branch:
        try:
            bid = int(new_branch)
        except (ValueError, TypeError):
            return jsonify({'ok': False, 'error': 'ערך סניף לא תקין'})
        if not Branch.query.get(bid):
            return jsonify({'ok': False, 'error': 'סניף לא נמצא'})
        session['ops_branch_id'] = bid
    else:
        session['ops_branch_id'] = None
    return jsonify({'ok': True})


@ops_bp.route('/')
def index():
    device = _check_device()
    if not device:
        return redirect(url_for('ops.not_enrolled'))
    user = _get_ops_user()
    if not user:
        return redirect(url_for('ops.login'))
    modules = user.get_ops_modules()
    if 'home' in modules:
        return redirect(url_for('ops.home'))
    elif modules:
        return redirect(url_for('ops.' + modules[0]))
    return redirect(url_for('ops.home'))


@ops_bp.route('/not-enrolled')
def not_enrolled():
    pending_token = request.cookies.get('ops_pending_request')
    if pending_token:
        device = EnrolledDevice.query.filter_by(pending_request_token=pending_token).first()
        if device and device.is_active and device.enrolled_at:
            device.pending_request_token = None
            device.last_seen = datetime.utcnow()
            db.session.commit()
            resp = make_response(redirect(url_for('ops.login')))
            resp.set_cookie('ops_device_token', device.device_token, max_age=365*24*3600, httponly=True, samesite='Lax', secure=_is_secure())
            resp.delete_cookie('ops_pending_request')
            return resp
        if device:
            return render_template('ops/not_enrolled.html', enrollment_code=pending_token, pending_device=device)
    return render_template('ops/not_enrolled.html', enrollment_code=None, pending_device=None)


@ops_bp.route('/request-enrollment', methods=['POST'])
def request_enrollment():
    device_name = request.form.get('device_name', 'iPad').strip()[:100] or 'iPad'
    user_agent = request.headers.get('User-Agent', '')[:500]
    request_token = secrets.token_urlsafe(32)
    device = EnrolledDevice(
        device_name=device_name,
        device_token=secrets.token_urlsafe(64),
        pending_request_token=request_token,
        is_active=False,
        user_agent=user_agent,
    )
    db.session.add(device)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return render_template('ops/not_enrolled.html', enrollment_code=None, pending_device=None)
    resp = make_response(render_template('ops/not_enrolled.html', enrollment_code=request_token, pending_device=device))
    resp.set_cookie('ops_pending_request', request_token, max_age=24*3600, httponly=True, samesite='Lax', secure=_is_secure())
    return resp


@ops_bp.route('/check-enrollment')
def check_enrollment():
    pending_token = request.cookies.get('ops_pending_request')
    if pending_token:
        device = EnrolledDevice.query.filter_by(pending_request_token=pending_token).first()
        if device and device.is_active and device.enrolled_at:
            device.pending_request_token = None
            device.last_seen = datetime.utcnow()
            db.session.commit()
            resp = make_response(redirect(url_for('ops.login')))
            resp.set_cookie('ops_device_token', device.device_token, max_age=365*24*3600, httponly=True, samesite='Lax', secure=_is_secure())
            resp.delete_cookie('ops_pending_request')
            return resp
        return render_template('ops/not_enrolled.html', enrollment_code=pending_token if device else None, pending_device=device)
    return redirect(url_for('ops.not_enrolled'))


@ops_bp.route('/enroll/<code>')
def enroll_device(code):
    device = EnrolledDevice.query.filter_by(enrollment_code=code, is_active=True).first()
    if not device:
        return render_template('ops/not_enrolled.html', enrollment_code=None)
    if not device.enrolled_at:
        device.enrolled_at = datetime.utcnow()
    device.enrollment_code = None
    device.last_seen = datetime.utcnow()
    device.user_agent = request.headers.get('User-Agent', '')[:500]
    db.session.commit()

    resp = make_response(redirect(url_for('ops.login')))
    resp.set_cookie(
        'ops_device_token',
        device.device_token,
        max_age=365 * 24 * 3600,
        httponly=True,
        samesite='Lax',
        secure=_is_secure(),
    )
    return resp


@ops_bp.route('/login', methods=['GET', 'POST'])
@require_device
def login():
    error = None
    users = ManagerPIN.query.filter_by(is_active=True).all()
    if request.method == 'POST':
        pin = request.form.get('pin', '')
        user_id = request.form.get('user_id', '')
        if user_id:
            p = ManagerPIN.query.filter_by(id=int(user_id), is_active=True).first()
            if p and p.check_pin(pin):
                session['ops_pin_id'] = p.id
                session['ops_user_name'] = p.name
                session['ops_branch_id'] = getattr(p, 'branch_id', None)
                p.last_used_at = datetime.utcnow()
                device = _check_device()
                if device:
                    device.last_pin_id = p.id
                db.session.commit()
                return redirect(url_for('ops.index'))
            error = 'קוד PIN שגוי'
        else:
            for p in users:
                if p.check_pin(pin):
                    session['ops_pin_id'] = p.id
                    session['ops_user_name'] = p.name
                    session['ops_branch_id'] = getattr(p, 'branch_id', None)
                    p.last_used_at = datetime.utcnow()
                    device = _check_device()
                    if device:
                        device.last_pin_id = p.id
                    db.session.commit()
                    return redirect(url_for('ops.index'))
            error = 'קוד PIN שגוי'
    return render_template('ops/login.html', error=error, users=users)


@ops_bp.route('/logout')
def logout():
    session.pop('ops_pin_id', None)
    session.pop('ops_user_name', None)
    session.pop('ops_branch_id', None)
    device = _check_device()
    if device:
        device.last_pin_id = None
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
    return redirect(url_for('ops.login'))


@ops_bp.route('/shifts')
@require_ops_module('shifts')
def shifts():
    effective_branch = _get_effective_branch_id()
    workers = ManagerPIN.query.filter_by(is_active=True).order_by(ManagerPIN.name).all()
    if effective_branch:
        workers = [w for w in workers if w.branch_id is None or w.branch_id == effective_branch]
    open_shifts = TimeLog.query.filter(TimeLog.clock_out.is_(None))
    if effective_branch:
        open_shifts = open_shifts.filter_by(branch_id=effective_branch)
    open_shifts = open_shifts.all()
    open_worker_ids = {tl.worker_id for tl in open_shifts}
    now = _get_israel_now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_logs = TimeLog.query.filter(TimeLog.clock_in >= today_start)
    if effective_branch:
        today_logs = today_logs.filter_by(branch_id=effective_branch)
    today_logs = today_logs.order_by(TimeLog.clock_in.desc()).all()
    return render_template('ops/shifts.html',
        active_tab='shifts',
        workers=workers,
        open_shifts=open_shifts,
        open_worker_ids=open_worker_ids,
        today_logs=today_logs,
    )


@ops_bp.route('/shifts/clock-in', methods=['POST'])
@require_ops_module('shifts')
def shift_clock_in():
    data = request.get_json(force=True)
    worker_id = data.get('worker_id')
    pin = data.get('pin', '')
    if not worker_id or not pin:
        return jsonify({'ok': False, 'error': 'חסרים פרטים'})
    try:
        worker_id = int(worker_id)
    except (ValueError, TypeError):
        return jsonify({'ok': False, 'error': 'שגיאה'})
    worker = ManagerPIN.query.filter_by(id=worker_id, is_active=True).first()
    if not worker or not worker.check_pin(pin):
        return jsonify({'ok': False, 'error': 'קוד PIN שגוי'})
    existing = TimeLog.query.filter_by(worker_id=worker_id).filter(TimeLog.clock_out.is_(None)).first()
    if existing:
        return jsonify({'ok': False, 'error': f'{worker.name} כבר בשעון נוכחות'})
    effective_branch = _get_effective_branch_id() or worker.branch_id
    tl = TimeLog(worker_id=worker_id, branch_id=effective_branch, source='ops')
    db.session.add(tl)
    db.session.commit()
    return jsonify({'ok': True, 'message': f'{worker.name} נכנס/ה למשמרת'})


@ops_bp.route('/shifts/clock-out', methods=['POST'])
@require_ops_module('shifts')
def shift_clock_out():
    data = request.get_json(force=True)
    worker_id = data.get('worker_id')
    pin = data.get('pin', '')
    if not worker_id or not pin:
        return jsonify({'ok': False, 'error': 'חסרים פרטים'})
    try:
        worker_id = int(worker_id)
    except (ValueError, TypeError):
        return jsonify({'ok': False, 'error': 'שגיאה'})
    worker = ManagerPIN.query.filter_by(id=worker_id, is_active=True).first()
    if not worker or not worker.check_pin(pin):
        return jsonify({'ok': False, 'error': 'קוד PIN שגוי'})
    open_log = TimeLog.query.filter_by(worker_id=worker_id).filter(TimeLog.clock_out.is_(None)).first()
    if not open_log:
        return jsonify({'ok': False, 'error': f'{worker.name} לא בשעון נוכחות'})
    open_log.close_shift()
    db.session.commit()
    return jsonify({'ok': True, 'message': f'{worker.name} יצא/ה מהמשמרת ({open_log.duration_display})'})


@ops_bp.route('/delivery')
@require_ops_module('delivery')
def delivery():
    effective_branch = _get_effective_branch_id()
    query = DeliveryZone.query
    if effective_branch:
        query = query.filter(
            db.or_(DeliveryZone.branch_id == effective_branch, DeliveryZone.branch_id.is_(None))
        )
    zones = query.order_by(DeliveryZone.display_order, DeliveryZone.city_name).all()
    return render_template('ops/delivery.html', active_tab='delivery', zones=zones)


@ops_bp.route('/api/cities')
@require_ops_module('delivery')
def api_cities():
    from city_autocomplete import fetch_cities
    q = request.args.get('q', '').strip()
    cities = fetch_cities(q)
    return jsonify({'cities': cities})


@ops_bp.route('/api/delivery/save', methods=['POST'])
@require_ops_module('delivery')
def delivery_save():
    data = request.get_json(force=True)
    zone_id = data.get('id')
    city_name = (data.get('city_name') or '').strip()
    if not city_name:
        return jsonify({'ok': False, 'error': 'חסר שם עיר'})
    effective_branch = _get_effective_branch_id()
    user = _get_ops_user()
    is_super = user and user.is_ops_superadmin

    if zone_id:
        zone = DeliveryZone.query.get(zone_id)
        if not zone:
            return jsonify({'ok': False, 'error': 'אזור לא נמצא'})
        if not is_super and effective_branch and zone.branch_id != effective_branch:
            return jsonify({'ok': False, 'error': 'אין הרשאה לערוך אזור זה'})
    else:
        zone = DeliveryZone()
        zone.branch_id = effective_branch
        db.session.add(zone)

    zone.city_name = city_name
    zone.name = (data.get('name') or '').strip() or None
    try:
        zone.delivery_fee = float(data.get('delivery_fee', 0) or 0)
    except (ValueError, TypeError):
        zone.delivery_fee = 0
    try:
        zone.minimum_order = float(data.get('minimum_order', 0) or 0)
    except (ValueError, TypeError):
        zone.minimum_order = 0
    free_val = data.get('free_delivery_above')
    try:
        zone.free_delivery_above = float(free_val) if free_val else None
    except (ValueError, TypeError):
        zone.free_delivery_above = None
    try:
        zone.estimated_minutes = int(data.get('estimated_minutes', 30) or 30)
    except (ValueError, TypeError):
        zone.estimated_minutes = 30
    try:
        zone.display_order = int(data.get('display_order', 0) or 0)
    except (ValueError, TypeError):
        zone.display_order = 0

    db.session.commit()
    return jsonify({'ok': True, 'message': f'אזור {city_name} נשמר', 'id': zone.id})


@ops_bp.route('/api/delivery/toggle', methods=['POST'])
@require_ops_module('delivery')
def delivery_toggle():
    data = request.get_json(force=True)
    zone_id = data.get('id')
    if not zone_id:
        return jsonify({'ok': False, 'error': 'חסר מזהה'})
    zone = DeliveryZone.query.get(zone_id)
    if not zone:
        return jsonify({'ok': False, 'error': 'אזור לא נמצא'})
    effective_branch = _get_effective_branch_id()
    user = _get_ops_user()
    if not (user and user.is_ops_superadmin) and effective_branch and zone.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'אין הרשאה'})
    zone.is_active = not zone.is_active
    db.session.commit()
    status = 'פעיל' if zone.is_active else 'מושבת'
    return jsonify({'ok': True, 'message': f'{zone.city_name}: {status}', 'is_active': zone.is_active})


@ops_bp.route('/api/delivery/delete', methods=['POST'])
@require_ops_module('delivery')
def delivery_delete():
    data = request.get_json(force=True)
    zone_id = data.get('id')
    if not zone_id:
        return jsonify({'ok': False, 'error': 'חסר מזהה'})
    zone = DeliveryZone.query.get(zone_id)
    if not zone:
        return jsonify({'ok': False, 'error': 'אזור לא נמצא'})
    effective_branch = _get_effective_branch_id()
    user = _get_ops_user()
    if not (user and user.is_ops_superadmin) and effective_branch and zone.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'אין הרשאה'})
    name = zone.city_name
    db.session.delete(zone)
    db.session.commit()
    return jsonify({'ok': True, 'message': f'אזור {name} נמחק'})


@ops_bp.route('/employees')
@require_ops_module('employees')
def employees():
    user = _get_ops_user()
    if not user:
        return redirect(url_for('ops.login'))
    effective_branch = _get_effective_branch_id()
    if user.is_ops_superadmin:
        query = ManagerPIN.query
        if effective_branch:
            query = query.filter(
                db.or_(ManagerPIN.branch_id == effective_branch, ManagerPIN.branch_id.is_(None))
            )
        branches_list = Branch.query.filter_by(is_active=True).order_by(Branch.name_he).all()
    else:
        if effective_branch:
            query = ManagerPIN.query.filter(
                ManagerPIN.branch_id == effective_branch,
                ManagerPIN.is_ops_superadmin == False,
            )
        else:
            query = ManagerPIN.query.filter(ManagerPIN.id < 0)
        branches_list = []
        if effective_branch:
            b = Branch.query.get(effective_branch)
            if b:
                branches_list = [b]
    pins = query.order_by(ManagerPIN.name).all()
    return render_template('ops/employees.html',
        active_tab='employees',
        pins=pins,
        branches=branches_list,
        all_modules=ManagerPIN.OPS_MODULES,
    )


@ops_bp.route('/api/employees/save', methods=['POST'])
@require_ops_module('employees')
def employees_save():
    user = _get_ops_user()
    if not user:
        return jsonify({'ok': False, 'error': 'אין הרשאה'}), 403
    effective_branch = _get_effective_branch_id()
    data = request.get_json(force=True)
    pin_id = data.get('id')
    name = (data.get('name') or '').strip()
    pin_code = (data.get('pin') or '').strip()
    description = (data.get('description') or '').strip()
    branch_id = data.get('branch_id')
    is_superadmin = bool(data.get('is_ops_superadmin'))
    raw_permissions = data.get('ops_permissions') or []
    valid_modules = set(ManagerPIN.OPS_MODULES)
    ops_permissions = [p for p in raw_permissions if isinstance(p, str) and p in valid_modules]
    if not user.is_ops_superadmin:
        if is_superadmin:
            return jsonify({'ok': False, 'error': 'אין הרשאה ליצור סופר אדמין'}), 403
        if not effective_branch:
            return jsonify({'ok': False, 'error': 'אין סניף משויך - לא ניתן לנהל עובדים'}), 403
    if not name:
        return jsonify({'ok': False, 'error': 'שם עובד הוא שדה חובה'})
    resolved_branch_id = None
    if branch_id:
        try:
            resolved_branch_id = int(branch_id)
        except (ValueError, TypeError):
            return jsonify({'ok': False, 'error': 'סניף לא תקין'})
        if not Branch.query.get(resolved_branch_id):
            return jsonify({'ok': False, 'error': 'סניף לא נמצא'})
    if not user.is_ops_superadmin:
        if resolved_branch_id and resolved_branch_id != effective_branch:
            return jsonify({'ok': False, 'error': 'אין הרשאה לנהל עובדים בסניף אחר'}), 403
        resolved_branch_id = effective_branch
    if pin_code and (not pin_code.isdigit() or len(pin_code) < 4 or len(pin_code) > 8):
        return jsonify({'ok': False, 'error': 'קוד PIN חייב להיות 4-8 ספרות בלבד'})
    if pin_id:
        mp = ManagerPIN.query.get(pin_id)
        if not mp:
            return jsonify({'ok': False, 'error': 'עובד לא נמצא'})
        if not user.is_ops_superadmin:
            if mp.is_ops_superadmin:
                return jsonify({'ok': False, 'error': 'אין הרשאה לערוך סופר אדמין'}), 403
            if mp.branch_id != effective_branch:
                return jsonify({'ok': False, 'error': 'אין הרשאה לערוך עובד מסניף אחר'}), 403
        if mp.is_ops_superadmin and not is_superadmin:
            other_superadmins = ManagerPIN.query.filter(
                ManagerPIN.is_ops_superadmin == True,
                ManagerPIN.is_active == True,
                ManagerPIN.id != mp.id,
            ).count()
            if other_superadmins == 0:
                return jsonify({'ok': False, 'error': 'לא ניתן להסיר סופר אדמין אחרון'})
        mp.name = name
        mp.description = description
        mp.is_ops_superadmin = is_superadmin if user.is_ops_superadmin else mp.is_ops_superadmin
        mp.ops_permissions = ops_permissions if not mp.is_ops_superadmin else []
        mp.branch_id = resolved_branch_id
        if pin_code:
            mp.set_pin(pin_code)
        db.session.commit()
        return jsonify({'ok': True, 'message': f'עובד "{name}" עודכן'})
    else:
        if not pin_code:
            return jsonify({'ok': False, 'error': 'קוד PIN הוא שדה חובה'})
        mp = ManagerPIN(
            name=name,
            description=description,
            is_ops_superadmin=is_superadmin if user.is_ops_superadmin else False,
            ops_permissions=ops_permissions if not is_superadmin else [],
            branch_id=resolved_branch_id,
        )
        mp.set_pin(pin_code)
        db.session.add(mp)
        db.session.commit()
        return jsonify({'ok': True, 'message': f'עובד "{name}" נוצר בהצלחה'})


@ops_bp.route('/api/employees/toggle', methods=['POST'])
@require_ops_module('employees')
def employees_toggle():
    user = _get_ops_user()
    if not user:
        return jsonify({'ok': False, 'error': 'אין הרשאה'}), 403
    effective_branch = _get_effective_branch_id()
    data = request.get_json(force=True)
    pin_id = data.get('id')
    if not pin_id:
        return jsonify({'ok': False, 'error': 'חסר מזהה'})
    mp = ManagerPIN.query.get(pin_id)
    if not mp:
        return jsonify({'ok': False, 'error': 'עובד לא נמצא'})
    if mp.id == user.id:
        return jsonify({'ok': False, 'error': 'לא ניתן לשנות סטטוס של עצמך'})
    if not user.is_ops_superadmin:
        if mp.is_ops_superadmin:
            return jsonify({'ok': False, 'error': 'אין הרשאה לשנות סטטוס סופר אדמין'}), 403
        if mp.branch_id != effective_branch:
            return jsonify({'ok': False, 'error': 'אין הרשאה לשנות עובד מסניף אחר'}), 403
    if mp.is_active and mp.is_ops_superadmin:
        other_superadmins = ManagerPIN.query.filter(
            ManagerPIN.is_ops_superadmin == True,
            ManagerPIN.is_active == True,
            ManagerPIN.id != mp.id,
        ).count()
        if other_superadmins == 0:
            return jsonify({'ok': False, 'error': 'לא ניתן להשבית סופר אדמין אחרון'})
    mp.is_active = not mp.is_active
    db.session.commit()
    status = 'פעיל' if mp.is_active else 'מושבת'
    return jsonify({'ok': True, 'message': f'{mp.name}: {status}', 'is_active': mp.is_active})


@ops_bp.route('/auto-print')
@require_ops_module('orders')
def auto_print():
    user = _get_ops_user()
    if not user or not user.is_ops_superadmin:
        flash('אין לך הרשאה לגשת לדף ההגדרות', 'danger')
        return redirect(url_for('ops.home'))
    return render_template('ops/auto_print.html', active_tab='settings')


@ops_bp.route('/settings')
@require_ops_module('home')
def settings():
    user = _get_ops_user()
    if not user or not user.is_ops_superadmin:
        flash('אין לך הרשאה לגשת לדף ההגדרות', 'danger')
        return redirect(url_for('ops.home'))
    settings = _settings()
    effective_branch = _get_effective_branch_id()
    branch_name = ''
    if effective_branch:
        branch = Branch.query.get(effective_branch)
        branch_name = branch.name_he if branch else ''
    return render_template('ops/settings.html',
        active_tab='settings',
        settings=settings,
        branch_name=branch_name,
    )


@ops_bp.route('/home')
@require_ops_module('home')
def home():
    settings = _settings()
    now = _get_israel_now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    effective_branch = _get_effective_branch_id()

    today_q = FoodOrder.query.filter(FoodOrder.created_at >= today_start)
    if effective_branch:
        today_q = today_q.filter_by(branch_id=effective_branch)
    today_orders = today_q.all()
    total_revenue = sum(o.total_amount or 0 for o in today_orders if o.payment_status == 'paid')
    active_orders = sum(1 for o in today_orders if o.status in ('pending', 'confirmed', 'preparing'))
    completed_orders = sum(1 for o in today_orders if o.status in ('delivered', 'pickedup'))

    order_counts = {
        'new': sum(1 for o in today_orders if o.status in ('pending', 'confirmed')),
        'preparing': sum(1 for o in today_orders if o.status == 'preparing'),
        'ready': sum(1 for o in today_orders if o.status == 'ready'),
        'done': sum(1 for o in today_orders if o.status in ('delivered', 'pickedup')),
    }

    low_stock_count = 0
    try:
        stock_q = StockLevel.query.join(StockItem).filter(StockItem.is_active == True)
        if effective_branch:
            stock_q = stock_q.filter(StockLevel.branch_id == effective_branch)
        levels = stock_q.all()
        for lvl in levels:
            if lvl.item and lvl.current_quantity <= (lvl.item.minimum_stock or 0):
                low_stock_count += 1
    except Exception:
        pass

    if effective_branch:
        all_items = MenuItem.query.all()
        branch_overrides_map = {bmi.menu_item_id: bmi for bmi in BranchMenuItem.query.filter_by(branch_id=effective_branch).all()}
        unavailable_items = 0
        for mi in all_items:
            bmi = branch_overrides_map.get(mi.id)
            if bmi:
                if not bmi.is_available:
                    unavailable_items += 1
            elif not mi.is_available:
                unavailable_items += 1
    else:
        unavailable_items = MenuItem.query.filter_by(is_available=False).count()

    recent_q = FoodOrder.query.filter(FoodOrder.created_at >= today_start)
    if effective_branch:
        recent_q = recent_q.filter_by(branch_id=effective_branch)
    recent_orders = recent_q.order_by(FoodOrder.created_at.desc()).limit(8).all()

    return render_template('ops/home.html',
        active_tab='home',
        settings=settings,
        total_revenue=total_revenue,
        active_orders=active_orders,
        completed_orders=completed_orders,
        total_orders=len(today_orders),
        order_counts=order_counts,
        low_stock_count=low_stock_count,
        unavailable_items=unavailable_items,
        recent_orders=recent_orders,
    )


OPS_STATUS_FLOW = ['pending', 'preparing', 'ready', 'delivered', 'cancelled']
OPS_STATUS_LABELS = {
    'pending': 'חדשה',
    'confirmed': 'חדשה',
    'preparing': 'בהכנה',
    'ready': 'מוכנה',
    'delivered': 'נמסרה',
    'pickedup': 'נמסרה',
    'cancelled': 'בוטלה',
}
OPS_STATUS_COLORS = {
    'pending': 'orange',
    'confirmed': 'orange',
    'preparing': 'accent',
    'ready': 'green',
    'delivered': 'dim',
    'pickedup': 'dim',
    'cancelled': 'red',
}


@ops_bp.route('/orders')
@require_ops_module('orders')
def orders():
    effective_branch = _get_effective_branch_id()
    status_filter = request.args.get('status', 'active')
    type_filter = request.args.get('type', 'all')

    query = FoodOrder.query
    if effective_branch:
        query = query.filter_by(branch_id=effective_branch)

    if type_filter == 'delivery':
        query = query.filter_by(order_type='delivery')
    elif type_filter == 'pickup':
        query = query.filter_by(order_type='pickup')

    if status_filter == 'active':
        query = query.filter(FoodOrder.status.in_(['pending', 'confirmed', 'preparing', 'ready']))
    elif status_filter == 'done':
        query = query.filter(FoodOrder.status.in_(['delivered', 'pickedup']))
    elif status_filter == 'cancelled':
        query = query.filter_by(status='cancelled')
    elif status_filter == 'new':
        query = query.filter(FoodOrder.status.in_(['pending', 'confirmed']))
    elif status_filter == 'preparing':
        query = query.filter_by(status='preparing')
    elif status_filter == 'ready':
        query = query.filter_by(status='ready')

    order_list = query.order_by(FoodOrder.created_at.desc()).limit(100).all()

    now = _get_israel_now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_q = FoodOrder.query.filter(FoodOrder.created_at >= today_start)
    if effective_branch:
        today_q = today_q.filter_by(branch_id=effective_branch)
    if type_filter == 'delivery':
        today_q = today_q.filter_by(order_type='delivery')
    elif type_filter == 'pickup':
        today_q = today_q.filter_by(order_type='pickup')
    today_orders = today_q.all()
    counts = {
        'new': sum(1 for o in today_orders if o.status in ('pending', 'confirmed')),
        'preparing': sum(1 for o in today_orders if o.status == 'preparing'),
        'ready': sum(1 for o in today_orders if o.status == 'ready'),
        'done': sum(1 for o in today_orders if o.status in ('delivered', 'pickedup')),
        'cancelled': sum(1 for o in today_orders if o.status == 'cancelled'),
    }
    counts['active'] = counts['new'] + counts['preparing'] + counts['ready']

    categories = {c.id: c.name_he for c in MenuCategory.query.all()}

    return render_template('ops/orders.html',
        active_tab='orders',
        orders=order_list,
        status_filter=status_filter,
        type_filter=type_filter,
        counts=counts,
        now=now,
        status_labels=OPS_STATUS_LABELS,
        status_colors=OPS_STATUS_COLORS,
        categories=categories,
    )


@ops_bp.route('/api/orders/<int:order_id>/status', methods=['POST'])
@require_ops_module('orders')
def update_order_status(order_id):
    data = request.get_json(force=True)
    new_status = data.get('status')
    prep_minutes = data.get('prep_minutes', 0)
    valid = ['pending', 'confirmed', 'preparing', 'ready', 'delivered', 'pickedup', 'cancelled']
    if new_status not in valid:
        return jsonify({'ok': False, 'error': 'סטטוס לא תקין'})

    order = FoodOrder.query.get(order_id)
    if not order:
        return jsonify({'ok': False, 'error': 'הזמנה לא נמצאה'})

    effective_branch = _get_effective_branch_id()
    if effective_branch and order.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'הזמנה לא שייכת לסניף זה'})

    old_status = order.status
    order.status = new_status
    now = datetime.utcnow()
    if new_status == 'confirmed' and not order.confirmed_at:
        order.confirmed_at = now
    elif new_status == 'preparing':
        order.preparing_at = now
        if not order.confirmed_at:
            order.confirmed_at = now
        try:
            mins = int(prep_minutes)
            if mins > 0:
                order.estimated_ready_at = now + timedelta(minutes=mins)
        except (ValueError, TypeError):
            pass
    elif new_status == 'ready' and not order.ready_at:
        order.ready_at = now
    elif new_status in ('delivered', 'pickedup') and not order.completed_at:
        order.completed_at = now
    elif new_status == 'cancelled' and not order.cancelled_at:
        order.cancelled_at = now

    try:
        from models import OrderActivityLog
        user = _get_ops_user()
        log = OrderActivityLog(
            order_id=order.id,
            action='status_change',
            old_value=old_status,
            new_value=new_status,
            staff_name=user.name if user else 'Ops',
        )
        db.session.add(log)
    except Exception:
        pass

    db.session.commit()
    return jsonify({
        'ok': True,
        'message': f'הזמנה #{order.order_number} → {OPS_STATUS_LABELS.get(new_status, new_status)}',
        'new_status': new_status,
        'label': OPS_STATUS_LABELS.get(new_status, new_status),
    })


@ops_bp.route('/api/orders/<int:order_id>')
@require_ops_module('orders')
def get_order_detail(order_id):
    order = FoodOrder.query.get(order_id)
    if not order:
        return jsonify({'ok': False, 'error': 'הזמנה לא נמצאה'})
    effective_branch = _get_effective_branch_id()
    if effective_branch and order.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'הזמנה לא שייכת לסניף זה'})
    items = order.get_items()
    categories = {c.id: c.name_he for c in MenuCategory.query.all()}
    for item in items:
        cat_id = item.get('category_id')
        if cat_id and cat_id in categories:
            item['category_name'] = categories[cat_id]
        elif not item.get('category_name'):
            menu_item_id = item.get('menu_item_id') or item.get('item_id')
            if menu_item_id:
                mi = MenuItem.query.get(menu_item_id)
                if mi and mi.category:
                    item['category_name'] = mi.category.name_he
                    item['category_id'] = mi.category_id

    for item in items:
        menu_item_id = item.get('menu_item_id') or item.get('item_id')
        if menu_item_id:
            mi = MenuItem.query.get(menu_item_id)
            if mi:
                station = mi.print_station
                if order.branch_id:
                    bmi = BranchMenuItem.query.filter_by(branch_id=order.branch_id, menu_item_id=menu_item_id).first()
                    if bmi and bmi.print_station:
                        station = bmi.print_station
                if station:
                    item['print_station'] = station

    by_category = {}
    for item in items:
        cat = item.get('category_name', 'כללי')
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(item)

    by_station = {}
    for item in items:
        station = item.get('print_station', 'כללי')
        if station not in by_station:
            by_station[station] = []
        by_station[station].append(item)

    return jsonify({
        'ok': True,
        'order': {
            'id': order.id,
            'order_number': order.order_number,
            'status': order.status,
            'status_label': OPS_STATUS_LABELS.get(order.status, order.status),
            'customer_name': order.customer_name,
            'customer_phone': order.customer_phone,
            'order_type': order.order_type,
            'order_type_label': order.order_type_display_he,
            'delivery_address': order.delivery_address or '',
            'delivery_city': order.delivery_city or '',
            'delivery_notes': order.delivery_notes or '',
            'pickup_time': order.pickup_time or '',
            'customer_notes': order.customer_notes or '',
            'subtotal': order.subtotal,
            'delivery_fee': order.delivery_fee or 0,
            'discount_amount': order.discount_amount or 0,
            'coupon_code': order.coupon_code or '',
            'total_amount': order.total_amount,
            'payment_method': order.payment_method or '',
            'payment_status': order.payment_status or '',
            'created_at': order.created_at.strftime('%H:%M') if order.created_at else '',
            'items': items,
            'items_by_category': by_category,
            'items_by_station': by_station,
            'branch_name': order.branch_name or '',
            'estimated_ready_at': order.estimated_ready_at.strftime('%H:%M') if order.estimated_ready_at else '',
        }
    })


@ops_bp.route('/api/toggle-setting', methods=['POST'])
@require_ops_module('home')
def toggle_setting():
    data = request.get_json(force=True)
    field = data.get('field')
    value = data.get('value')
    allowed = ['ordering_paused', 'enable_online_ordering', 'enable_delivery', 'enable_pickup']
    if field not in allowed:
        return jsonify({'ok': False, 'error': 'שדה לא מורשה'})
    settings = _settings()
    if not settings:
        return jsonify({'ok': False, 'error': 'הגדרות לא נמצאו'})
    setattr(settings, field, bool(value))
    db.session.commit()
    return jsonify({'ok': True, 'message': 'עודכן'})


@ops_bp.route('/api/update-delivery-time', methods=['POST'])
@require_ops_module('home')
def update_delivery_time():
    data = request.get_json(force=True)
    time_val = data.get('value', '')
    settings = _settings()
    if settings:
        settings.estimated_delivery_time = time_val
        db.session.commit()
    return jsonify({'ok': True, 'message': 'עודכן'})


@ops_bp.route('/menu')
@require_ops_module('menu')
def menu():
    effective_branch = _get_effective_branch_id()
    categories = MenuCategory.query.filter_by(is_active=True).order_by(MenuCategory.display_order).all()
    cat_id = request.args.get('category', type=int)
    search = request.args.get('q', '').strip()

    items_query = MenuItem.query
    if cat_id:
        items_query = items_query.filter_by(category_id=cat_id)
    if search:
        items_query = items_query.filter(
            db.or_(
                MenuItem.name_he.ilike(f'%{search}%'),
                MenuItem.name_en.ilike(f'%{search}%')
            )
        )
    items = items_query.order_by(MenuItem.display_order).all()

    branch_overrides = {}
    if effective_branch:
        for bmi in BranchMenuItem.query.filter_by(branch_id=effective_branch).all():
            branch_overrides[bmi.menu_item_id] = bmi

    stations = PrintStation.query.order_by(PrintStation.name).all()

    return render_template('ops/menu.html',
        active_tab='menu',
        categories=categories,
        items=items,
        selected_category=cat_id,
        search=search,
        effective_branch=effective_branch,
        branch_overrides=branch_overrides,
        stations=stations,
    )


@ops_bp.route('/api/menu/toggle', methods=['POST'])
@require_ops_module('menu')
def menu_toggle():
    data = request.get_json(force=True)
    item_id = data.get('item_id')
    item = MenuItem.query.get(item_id)
    if not item:
        return jsonify({'ok': False, 'error': 'פריט לא נמצא'})
    effective_branch = _get_effective_branch_id()
    if effective_branch:
        bmi = BranchMenuItem.query.filter_by(branch_id=effective_branch, menu_item_id=item_id).first()
        if bmi:
            bmi.is_available = not bmi.is_available
        else:
            bmi = BranchMenuItem(branch_id=effective_branch, menu_item_id=item_id, is_available=False)
            db.session.add(bmi)
        db.session.commit()
        return jsonify({'ok': True, 'message': 'עודכן', 'available': bmi.is_available})
    item.is_available = not item.is_available
    db.session.commit()
    return jsonify({'ok': True, 'message': 'עודכן', 'available': item.is_available})


@ops_bp.route('/api/menu/price', methods=['POST'])
@require_ops_module('menu')
def menu_price():
    data = request.get_json(force=True)
    item_id = data.get('item_id')
    price = data.get('price')
    item = MenuItem.query.get(item_id)
    if not item:
        return jsonify({'ok': False, 'error': 'פריט לא נמצא'})
    try:
        new_price = float(price)
    except (ValueError, TypeError):
        return jsonify({'ok': False, 'error': 'מחיר לא תקין'})
    effective_branch = _get_effective_branch_id()
    if effective_branch:
        bmi = BranchMenuItem.query.filter_by(branch_id=effective_branch, menu_item_id=item_id).first()
        if bmi:
            bmi.custom_price = new_price
        else:
            bmi = BranchMenuItem(
                branch_id=effective_branch,
                menu_item_id=item_id,
                custom_price=new_price,
                is_available=item.is_available,
            )
            db.session.add(bmi)
        db.session.commit()
        return jsonify({'ok': True, 'message': 'מחיר עודכן (סניף)'})
    item.base_price = new_price
    db.session.commit()
    return jsonify({'ok': True, 'message': 'מחיר עודכן'})


@ops_bp.route('/api/menu/station', methods=['POST'])
@require_ops_module('menu')
def menu_station():
    data = request.get_json(force=True)
    item_id = data.get('item_id')
    station = (data.get('station') or '').strip() or None
    item = MenuItem.query.get(item_id)
    if not item:
        return jsonify({'ok': False, 'error': 'פריט לא נמצא'})
    effective_branch = _get_effective_branch_id()
    if effective_branch:
        bmi = BranchMenuItem.query.filter_by(branch_id=effective_branch, menu_item_id=item_id).first()
        if bmi:
            bmi.print_station = station
        else:
            bmi = BranchMenuItem(
                branch_id=effective_branch,
                menu_item_id=item_id,
                print_station=station,
                is_available=item.is_available,
            )
            db.session.add(bmi)
        db.session.commit()
        return jsonify({'ok': True, 'message': 'עמדת הדפסה עודכנה (סניף)', 'station': station})
    item.print_station = station
    db.session.commit()
    return jsonify({'ok': True, 'message': 'עמדת הדפסה עודכנה', 'station': station})


@ops_bp.route('/stock')
@require_ops_module('stock')
def stock():
    effective_branch = _get_effective_branch_id()

    items = StockItem.query.filter_by(is_active=True).order_by(StockItem.name_he).all()
    levels = {}
    level_query = StockLevel.query
    if effective_branch:
        level_query = level_query.filter_by(branch_id=effective_branch)
    for lvl in level_query.all():
        levels[lvl.item_id] = lvl

    txn_query = StockTransaction.query
    if effective_branch:
        txn_query = txn_query.filter_by(branch_id=effective_branch)
    recent_txns = txn_query.order_by(
        StockTransaction.transaction_date.desc()
    ).limit(20).all()

    low_items = []
    for item in items:
        lvl = levels.get(item.id)
        if lvl and lvl.current_quantity <= (item.minimum_stock or 0):
            low_items.append((item, lvl))

    return render_template('ops/stock.html',
        active_tab='stock',
        items=items,
        levels=levels,
        recent_txns=recent_txns,
        low_items=low_items,
    )


@ops_bp.route('/api/stock/transaction', methods=['POST'])
@require_ops_module('stock')
def stock_transaction():
    data = request.get_json(force=True)
    item_id = data.get('item_id')
    qty = data.get('quantity')
    txn_type = data.get('type', 'delivery')
    notes = data.get('notes', '')

    item = StockItem.query.get(item_id)
    if not item:
        return jsonify({'ok': False, 'error': 'פריט לא נמצא'})
    try:
        qty = float(qty)
    except (ValueError, TypeError):
        return jsonify({'ok': False, 'error': 'כמות לא תקינה'})

    effective_branch = _get_effective_branch_id()
    if not effective_branch:
        first_branch = Branch.query.filter_by(is_active=True).first()
        effective_branch = first_branch.id if first_branch else None
    if not effective_branch:
        return jsonify({'ok': False, 'error': 'לא נמצא סניף'})

    txn = StockTransaction(
        item_id=item_id,
        branch_id=effective_branch,
        transaction_type=txn_type,
        quantity=qty,
        notes=notes,
        transaction_date=datetime.utcnow(),
    )
    db.session.add(txn)

    lvl = StockLevel.query.filter_by(item_id=item_id, branch_id=effective_branch).first()
    if lvl:
        lvl.current_quantity = (lvl.current_quantity or 0) + qty
        lvl.available_quantity = lvl.current_quantity - (lvl.reserved_quantity or 0)
    else:
        lvl = StockLevel(
            item_id=item_id,
            branch_id=effective_branch,
            current_quantity=qty,
            available_quantity=qty,
        )
        db.session.add(lvl)

    db.session.commit()
    return jsonify({'ok': True, 'message': 'עסקה נרשמה', 'new_qty': lvl.current_quantity})


@ops_bp.route('/deals')
@require_ops_module('deals')
def deals():
    effective_branch = _get_effective_branch_id()
    all_deals = Deal.query.order_by(Deal.display_order).all()
    all_coupons = Coupon.query.order_by(Coupon.created_at.desc()).all()
    filter_type = request.args.get('filter', 'all')
    return render_template('ops/deals.html',
        active_tab='deals',
        deals=all_deals,
        coupons=all_coupons,
        filter_type=filter_type,
        is_readonly=bool(effective_branch),
    )


@ops_bp.route('/api/deals/toggle', methods=['POST'])
@require_ops_module('deals')
def deal_toggle():
    if _get_effective_branch_id():
        return jsonify({'ok': False, 'error': 'אין הרשאה – ניתן לצפות בלבד'})
    data = request.get_json(force=True)
    deal_id = data.get('deal_id')
    deal = Deal.query.get(deal_id)
    if not deal:
        return jsonify({'ok': False, 'error': 'מבצע לא נמצא'})
    deal.is_active = not deal.is_active
    db.session.commit()
    return jsonify({'ok': True, 'message': 'עודכן', 'active': deal.is_active})


@ops_bp.route('/api/coupons/toggle', methods=['POST'])
@require_ops_module('deals')
def coupon_toggle():
    if _get_effective_branch_id():
        return jsonify({'ok': False, 'error': 'אין הרשאה – ניתן לצפות בלבד'})
    data = request.get_json(force=True)
    coupon_id = data.get('coupon_id')
    coupon = Coupon.query.get(coupon_id)
    if not coupon:
        return jsonify({'ok': False, 'error': 'קופון לא נמצא'})
    coupon.is_active = not coupon.is_active
    db.session.commit()
    return jsonify({'ok': True, 'message': 'עודכן', 'active': coupon.is_active})


@ops_bp.route('/api/coupons/create', methods=['POST'])
@require_ops_module('deals')
def coupon_create():
    if _get_effective_branch_id():
        return jsonify({'ok': False, 'error': 'אין הרשאה – ניתן לצפות בלבד'})
    data = request.get_json(force=True)
    name = data.get('name', '').strip()
    code = data.get('code', '').strip().upper()
    discount_type = data.get('discount_type', 'percentage')
    discount_value = data.get('discount_value', 0)
    if not name or not code:
        return jsonify({'ok': False, 'error': 'שם וקוד הם שדות חובה'})
    existing = Coupon.query.filter_by(code=code).first()
    if existing:
        return jsonify({'ok': False, 'error': 'קוד קופון כבר קיים'})
    try:
        coupon = Coupon(
            name=name,
            code=code,
            discount_type=discount_type,
            discount_value=float(discount_value),
            is_active=True,
        )
        db.session.add(coupon)
        db.session.commit()
        return jsonify({'ok': True, 'message': 'קופון נוצר', 'id': coupon.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'ok': False, 'error': str(e)})


@ops_bp.route('/api/deals/edit', methods=['POST'])
@require_ops_module('deals')
def deal_edit():
    if _get_effective_branch_id():
        return jsonify({'ok': False, 'error': 'אין הרשאה – ניתן לצפות בלבד'})
    data = request.get_json(force=True)
    deal_id = data.get('deal_id')
    deal = Deal.query.get(deal_id)
    if not deal:
        return jsonify({'ok': False, 'error': 'מבצע לא נמצא'})
    if 'name_he' in data:
        deal.name_he = data['name_he']
    if 'deal_price' in data:
        deal.deal_price = float(data['deal_price'])
    if 'original_price' in data:
        deal.original_price = float(data['original_price']) if data['original_price'] else None
    db.session.commit()
    return jsonify({'ok': True, 'message': 'מבצע עודכן'})


@ops_bp.route('/api/coupons/edit', methods=['POST'])
@require_ops_module('deals')
def coupon_edit():
    if _get_effective_branch_id():
        return jsonify({'ok': False, 'error': 'אין הרשאה – ניתן לצפות בלבד'})
    data = request.get_json(force=True)
    coupon_id = data.get('coupon_id')
    coupon = Coupon.query.get(coupon_id)
    if not coupon:
        return jsonify({'ok': False, 'error': 'קופון לא נמצא'})
    if 'name' in data:
        coupon.name = data['name']
    if 'discount_type' in data:
        coupon.discount_type = data['discount_type']
    if 'discount_value' in data:
        coupon.discount_value = float(data['discount_value'])
    if 'max_total_uses' in data:
        coupon.max_total_uses = int(data['max_total_uses']) if data['max_total_uses'] else None
    db.session.commit()
    return jsonify({'ok': True, 'message': 'קופון עודכן'})


@ops_bp.route('/branches')
@require_ops_module('branches')
def branches():
    user = _get_ops_user()
    effective_branch = _get_effective_branch_id()
    if user and user.is_ops_superadmin:
        branch_list = Branch.query.filter_by(is_active=True).order_by(Branch.display_order).all()
    elif effective_branch:
        branch_list = Branch.query.filter_by(id=effective_branch, is_active=True).all()
    else:
        branch_list = []
    hours = {}
    branch_ids = [b.id for b in branch_list]
    for h in WorkingHours.query.filter(WorkingHours.branch_id.in_(branch_ids)).all():
        hours.setdefault(h.branch_id, []).append(h)
    settings = _settings() if (user and user.is_ops_superadmin) else None
    return render_template('ops/branches.html',
        active_tab='branches',
        branches=branch_list,
        hours=hours,
        settings=settings,
    )


@ops_bp.route('/api/branches/toggle', methods=['POST'])
@require_ops_module('branches')
def branch_toggle():
    user = _get_ops_user()
    effective_branch = _get_effective_branch_id()
    data = request.get_json(force=True)
    field = data.get('field')
    branch_id = data.get('branch_id')
    value = data.get('value')
    allowed_branch = ['is_active', 'enable_delivery', 'enable_pickup']
    allowed_global = ['enable_delivery', 'enable_pickup']
    if field in allowed_global and not branch_id:
        if not user or not user.is_ops_superadmin:
            return jsonify({'ok': False, 'error': 'רק סופר אדמין יכול לשנות הגדרות כלליות'}), 403
        settings = _settings()
        if settings:
            setattr(settings, field, bool(value))
            db.session.commit()
            return jsonify({'ok': True, 'message': 'עודכן'})
        return jsonify({'ok': False, 'error': 'הגדרות לא נמצאו'})
    if field not in allowed_branch:
        return jsonify({'ok': False, 'error': 'שדה לא מורשה'})
    branch = Branch.query.get(branch_id)
    if not branch:
        return jsonify({'ok': False, 'error': 'סניף לא נמצא'})
    if not user or (not user.is_ops_superadmin and (not effective_branch or branch.id != effective_branch)):
        return jsonify({'ok': False, 'error': 'אין הרשאה לשנות סניף זה'}), 403
    setattr(branch, field, bool(value))
    db.session.commit()
    return jsonify({'ok': True, 'message': 'עודכן'})


@ops_bp.route('/api/branches/hours', methods=['POST'])
@require_ops_module('branches')
def branch_hours():
    user = _get_ops_user()
    effective_branch = _get_effective_branch_id()
    data = request.get_json(force=True)
    hour_id = data.get('hour_id')
    open_time = data.get('open_time')
    close_time = data.get('close_time')
    is_closed = data.get('is_closed')

    wh = WorkingHours.query.get(hour_id)
    if not wh:
        return jsonify({'ok': False, 'error': 'שעות לא נמצאו'})
    if not user or (not user.is_ops_superadmin and (not effective_branch or wh.branch_id != effective_branch)):
        return jsonify({'ok': False, 'error': 'אין הרשאה לשנות שעות סניף זה'}), 403
    if open_time is not None:
        wh.open_time = open_time
    if close_time is not None:
        wh.close_time = close_time
    if is_closed is not None:
        wh.is_closed = bool(is_closed)
    db.session.commit()
    return jsonify({'ok': True, 'message': 'שעות עודכנו'})


class DirectPrinter:
    ESC = b'\x1b'
    GS = b'\x1d'
    INIT = b'\x1b@'
    CUT_FULL = b'\x1dV\x00'
    CUT_PARTIAL = b'\x1dV\x01'
    ALIGN_LEFT = b'\x1ba\x00'
    ALIGN_CENTER = b'\x1ba\x01'
    ALIGN_RIGHT = b'\x1ba\x02'
    FONT_NORMAL = b'\x1b!\x00'
    FONT_DOUBLE_H = b'\x1b!\x10'
    FONT_DOUBLE_W = b'\x1b!\x20'
    FONT_DOUBLE = b'\x1b!\x30'
    BOLD_ON = b'\x1bE\x01'
    BOLD_OFF = b'\x1bE\x00'

    def __init__(self, ip, port=9100):
        self.ip = ip
        self.port = port
        self.buf = bytearray()

    def _add(self, data):
        if isinstance(data, str):
            self.buf.extend(data.encode('utf-8'))
        else:
            self.buf.extend(data)

    def init(self):
        self._add(self.INIT)

    def cut(self):
        self._add(b'\n\n\n')
        self._add(self.CUT_FULL)

    def align(self, a):
        self._add({'center': self.ALIGN_CENTER, 'right': self.ALIGN_RIGHT}.get(a, self.ALIGN_LEFT))

    def font(self, s):
        self._add({'double': self.FONT_DOUBLE, 'double_h': self.FONT_DOUBLE_H, 'double_w': self.FONT_DOUBLE_W}.get(s, self.FONT_NORMAL))

    def bold(self, on=True):
        self._add(self.BOLD_ON if on else self.BOLD_OFF)

    def text(self, t):
        self._add(t + '\n')

    def line(self, ch='-', w=32):
        self._add(ch * w + '\n')

    def dashed(self, w=32):
        self.line('-', w)

    def thick(self, w=32):
        self.line('=', w)

    def send(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((self.ip, self.port))
            s.sendall(bytes(self.buf))
            s.close()
            return True
        except Exception as e:
            logging.error(f'Printer send error: {e}')
            return False


def _build_checker_bon(p, o):
    p.init()
    p.align('center')
    p.font('double')
    p.text('SUMO')
    p.font('double_h')
    type_he = 'משלוח' if o.order_type == 'delivery' else 'איסוף עצמי'
    p.text(type_he)
    p.font('double')
    p.text(f'#{o.order_number}')
    p.font('normal')
    p.text(o.created_at.strftime('%d/%m %H:%M') if o.created_at else '')
    p.thick()
    p.align('right')

    if o.customer_notes:
        p.bold()
        p.text(f'⚠ {o.customer_notes}')
        p.bold(False)
    if o.delivery_notes:
        p.bold()
        p.text(f'🚗 {o.delivery_notes}')
        p.bold(False)

    p.font('double_h')
    p.bold()
    p.text(o.customer_name or '')
    p.font('normal')
    p.text(o.customer_phone or '')
    if o.delivery_address:
        addr = o.delivery_address
        if o.delivery_city:
            addr += f', {o.delivery_city}'
        p.text(addr)
    p.bold(False)
    p.dashed()

    items = json.loads(o.items_json) if o.items_json else []
    for item in items:
        menu_item_id = item.get('menu_item_id') or item.get('item_id')
        display_name = item.get('name_he') or item.get('item_name_he') or item.get('name', '')
        if menu_item_id:
            mi = MenuItem.query.get(menu_item_id)
            if mi and mi.print_name:
                display_name = mi.print_name
        qty = item.get('qty') or item.get('quantity', 1)
        p.bold()
        p.text(f'{qty}× {display_name}')
        p.bold(False)
        opts = item.get('options') or []
        for op in opts:
            op_name = op.get('choice_name_he') or op.get('name', str(op)) if isinstance(op, dict) else str(op)
            p.text(f'  + {op_name}')

    p.thick()
    p.align('right')
    p.font('double')
    p.bold()
    p.text(f'סה"כ: ₪{o.total_amount:.0f}')
    p.bold(False)
    p.font('normal')
    p.align('center')
    from datetime import datetime as dt
    p.text(f'צ׳קר | {dt.now().strftime("%H:%M")}')
    p.cut()


def _build_payment_bon(p, o):
    p.init()
    p.align('center')
    p.font('double')
    p.text('SUMO')
    p.font('double_h')
    p.text('בון תשלום')
    p.font('double')
    p.text(f'#{o.order_number}')
    p.font('normal')
    type_he = 'משלוח' if o.order_type == 'delivery' else 'איסוף עצמי'
    p.text(f'{type_he} | {o.created_at.strftime("%d/%m %H:%M") if o.created_at else ""}')
    p.thick()
    p.align('right')
    p.font('double_h')
    p.bold()
    p.text(o.customer_name or '')
    p.bold(False)
    p.font('normal')
    p.dashed()

    items = json.loads(o.items_json) if o.items_json else []
    for item in items:
        menu_item_id = item.get('menu_item_id') or item.get('item_id')
        display_name = item.get('name_he') or item.get('item_name_he') or item.get('name', '')
        if menu_item_id:
            mi = MenuItem.query.get(menu_item_id)
            if mi and mi.print_name:
                display_name = mi.print_name
        qty = item.get('qty') or item.get('quantity', 1)
        price = item.get('price') or item.get('unit_price', 0)
        total = qty * price
        p.bold()
        p.text(f'{qty}× {display_name}  ₪{total:.0f}')
        p.bold(False)
        opts = item.get('options') or []
        for op in opts:
            op_name = op.get('choice_name_he') or op.get('name', str(op)) if isinstance(op, dict) else str(op)
            p.text(f'  + {op_name}')

    p.dashed()
    p.text(f'סכום: ₪{o.subtotal:.0f}')
    if o.delivery_fee and o.delivery_fee > 0:
        p.text(f'משלוח: ₪{o.delivery_fee:.0f}')
    if o.discount_amount and o.discount_amount > 0:
        p.text(f'הנחה: -₪{o.discount_amount:.0f}')
    p.thick()
    p.font('double')
    p.bold()
    p.text(f'לתשלום: ₪{o.total_amount:.0f}')
    p.bold(False)
    p.font('normal')
    p.align('center')
    p.text(f'תשלום: {o.payment_method or "—"}')
    from datetime import datetime as dt
    p.text(dt.now().strftime('%H:%M'))
    p.cut()


def _build_station_bon(p, o, station_name, station_items):
    p.init()
    p.align('center')
    p.font('double')
    p.bold()
    p.text(station_name)
    p.bold(False)
    p.font('double_h')
    p.text(f'#{o.order_number}')
    p.font('normal')
    type_he = 'משלוח' if o.order_type == 'delivery' else 'איסוף עצמי'
    p.text(f'{type_he} | {o.created_at.strftime("%d/%m %H:%M") if o.created_at else ""}')
    p.thick()
    p.align('right')

    if o.customer_notes:
        p.bold()
        p.text(f'⚠ {o.customer_notes}')
        p.bold(False)

    for item in station_items:
        menu_item_id = item.get('menu_item_id') or item.get('item_id')
        display_name = item.get('name_he') or item.get('item_name_he') or item.get('name', '')
        if menu_item_id:
            mi = MenuItem.query.get(menu_item_id)
            if mi and mi.print_name:
                display_name = mi.print_name
        qty = item.get('qty') or item.get('quantity', 1)
        p.bold()
        p.text(f'{qty}× {display_name}')
        p.bold(False)
        opts = item.get('options') or []
        for op in opts:
            op_name = op.get('choice_name_he') or op.get('name', str(op)) if isinstance(op, dict) else str(op)
            p.text(f'  + {op_name}')

    p.align('center')
    p.dashed()
    from datetime import datetime as dt
    p.text(f'#{o.order_number} | {station_name} | {dt.now().strftime("%H:%M")}')
    p.cut()


@ops_bp.route('/api/print', methods=['POST'])
@require_ops_module('orders')
def direct_print():
    data = request.get_json(force=True)
    order_id = data.get('order_id')
    printer_ip = data.get('printer_ip')
    printer_port = int(data.get('printer_port', 9100))
    checker_copies = int(data.get('checker_copies', 2))
    payment_copies = int(data.get('payment_copies', 1))
    station_bons = data.get('station_bons', True)

    if not order_id or not printer_ip:
        return jsonify({'ok': False, 'error': 'חסר מזהה הזמנה או כתובת מדפסת'})

    order = FoodOrder.query.get(order_id)
    if not order:
        return jsonify({'ok': False, 'error': 'הזמנה לא נמצאה'})
    effective_branch = _get_effective_branch_id()
    if effective_branch and order.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'הזמנה לא שייכת לסניף זה'})

    p = DirectPrinter(printer_ip, printer_port)

    for _ in range(checker_copies):
        _build_checker_bon(p, order)

    for _ in range(payment_copies):
        _build_payment_bon(p, order)

    if station_bons:
        items = json.loads(order.items_json) if order.items_json else []
        by_station = {}
        for item in items:
            menu_item_id = item.get('menu_item_id') or item.get('item_id')
            st = 'כללי'
            if menu_item_id:
                mi = MenuItem.query.get(menu_item_id)
                if mi:
                    st = mi.print_station or 'כללי'
                    if order.branch_id:
                        bmi = BranchMenuItem.query.filter_by(branch_id=order.branch_id, menu_item_id=menu_item_id).first()
                        if bmi and bmi.print_station:
                            st = bmi.print_station
            if st not in by_station:
                by_station[st] = []
            by_station[st].append(item)
        for st_name, st_items in by_station.items():
            _build_station_bon(p, order, st_name, st_items)

    success = p.send()
    if success:
        order.bon_printed = True
        order.bon_printed_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'ok': True, 'message': 'נשלח להדפסה'})
    else:
        return jsonify({'ok': False, 'error': 'שגיאת חיבור למדפסת'})


@ops_bp.route('/api/orders/unprinted', methods=['GET'])
def get_unprinted_orders():
    api_key = request.headers.get('X-Print-Key') or request.args.get('key')
    expected_key = os.environ.get('PRINT_AGENT_KEY', '')
    is_api_key_auth = api_key and expected_key and api_key == expected_key
    if not is_api_key_auth:
        pin = _get_ops_user()
        if not pin:
            return jsonify({'ok': False, 'error': 'unauthorized'}), 401

    branch_id = request.args.get('branch_id', type=int)
    if not is_api_key_auth:
        effective_branch = _get_effective_branch_id()
        if effective_branch:
            branch_id = effective_branch
    query = FoodOrder.query.filter(
        FoodOrder.bon_printed == False,
        FoodOrder.status.in_(['pending', 'confirmed', 'preparing'])
    )
    if branch_id:
        query = query.filter_by(branch_id=branch_id)
    orders = query.order_by(FoodOrder.created_at.asc()).all()

    result = []
    for o in orders:
        items = json.loads(o.items_json) if o.items_json else []
        by_station = {}
        for item in items:
            menu_item_id = item.get('menu_item_id') or item.get('item_id')
            st = 'כללי'
            if menu_item_id:
                mi = MenuItem.query.get(menu_item_id)
                if mi:
                    if mi.print_station:
                        st = mi.print_station
                    if o.branch_id:
                        bmi = BranchMenuItem.query.filter_by(branch_id=o.branch_id, menu_item_id=menu_item_id).first()
                        if bmi and bmi.print_station:
                            st = bmi.print_station
                    if mi.print_name:
                        item['print_name'] = mi.print_name
            if st not in by_station:
                by_station[st] = []
            by_station[st].append(item)

        result.append({
            'id': o.id,
            'order_number': o.order_number,
            'order_type': o.order_type,
            'status': o.status,
            'branch_id': o.branch_id,
            'customer_name': o.customer_name or '',
            'customer_phone': o.customer_phone or '',
            'delivery_address': o.delivery_address or '',
            'delivery_city': o.delivery_city or '',
            'delivery_notes': o.delivery_notes or '',
            'customer_notes': o.customer_notes or '',
            'subtotal': o.subtotal or 0,
            'delivery_fee': o.delivery_fee or 0,
            'discount_amount': o.discount_amount or 0,
            'total_amount': o.total_amount or 0,
            'payment_method': o.payment_method or '',
            'coupon_code': o.coupon_code or '',
            'created_at': o.created_at.strftime('%d/%m %H:%M') if o.created_at else '',
            'items': items,
            'items_by_station': by_station,
        })

    return jsonify({'ok': True, 'orders': result})


@ops_bp.route('/api/orders/mark-printed', methods=['POST'])
def mark_orders_printed():
    api_key = request.headers.get('X-Print-Key') or request.args.get('key')
    expected_key = os.environ.get('PRINT_AGENT_KEY', '')
    is_api_key_auth = api_key and expected_key and api_key == expected_key
    if not is_api_key_auth:
        pin = _get_ops_user()
        if not pin:
            return jsonify({'ok': False, 'error': 'unauthorized'}), 401

    data = request.get_json(force=True)
    order_ids = data.get('order_ids', [])
    if not order_ids:
        return jsonify({'ok': False, 'error': 'missing order_ids'})

    effective_branch = _get_effective_branch_id() if not is_api_key_auth else None

    from datetime import datetime as dt
    for oid in order_ids:
        order = FoodOrder.query.get(oid)
        if order:
            if effective_branch and order.branch_id != effective_branch:
                continue
            order.bon_printed = True
            order.bon_printed_at = dt.utcnow()
    db.session.commit()
    return jsonify({'ok': True, 'message': f'{len(order_ids)} orders marked as printed'})


@ops_bp.route('/api/branch/<int:branch_id>/printers', methods=['GET'])
def get_branch_printers(branch_id):
    api_key = request.headers.get('X-Print-Key') or request.args.get('key')
    expected_key = os.environ.get('PRINT_AGENT_KEY', '')
    if not api_key or not expected_key or api_key != expected_key:
        pin = _get_ops_user()
        if not pin:
            return jsonify({'ok': False, 'error': 'unauthorized'}), 401

    branch = Branch.query.get(branch_id)
    if not branch:
        return jsonify({'ok': False, 'error': 'branch not found'}), 404

    printers = Printer.query.filter_by(branch_id=branch_id, is_active=True).order_by(Printer.display_order).all()
    station_map = {}
    default_printer = None
    for p in printers:
        pd = p.to_dict()
        if p.is_default:
            default_printer = pd
        for st in p.stations:
            station_map[st.station_name] = pd

    return jsonify({
        'ok': True,
        'branch_id': branch_id,
        'branch_name': branch.name_he,
        'default_printer': default_printer,
        'station_map': station_map,
        'printers': [p.to_dict() for p in printers],
    })


@ops_bp.route('/api/print/test', methods=['POST'])
@require_ops_module('orders')
def direct_print_test():
    data = request.get_json(force=True)
    printer_ip = data.get('printer_ip')
    printer_port = int(data.get('printer_port', 9100))
    if not printer_ip:
        return jsonify({'ok': False, 'error': 'חסר כתובת מדפסת'})

    p = DirectPrinter(printer_ip, printer_port)
    p.init()
    p.align('center')
    p.font('double')
    p.text('SUMO')
    p.font('normal')
    p.text('בדיקת מדפסת')
    p.dashed()
    from datetime import datetime as dt
    p.text(dt.now().strftime('%Y-%m-%d %H:%M:%S'))
    p.text('החיבור תקין!')
    p.cut()
    success = p.send()
    if success:
        return jsonify({'ok': True, 'message': 'הדפסת בדיקה נשלחה'})
    else:
        return jsonify({'ok': False, 'error': 'שגיאת חיבור'})
