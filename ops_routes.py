import json
import logging
import os
import queue
import secrets
import socket
import threading
import time as _time
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Blueprint, render_template, request, session, redirect,
    url_for, jsonify, make_response, flash, Response, g,
)
from database import db


def _is_secure():
    return request.is_secure or request.headers.get('X-Forwarded-Proto') == 'https' or os.environ.get('REPL_SLUG')
from models import (
    ManagerPIN, EnrolledDevice, SiteSettings, Branch, WorkingHours,
    MenuCategory, MenuItem, BranchMenuItem, StockItem, StockLevel, StockTransaction,
    StockAlert, Deal, Coupon, CouponUsage, FoodOrder, FoodOrderItem,
    Printer, PrinterStation, PrintStation, TimeLog, PrintDevice, ApiKey,
    MenuItemOptionGroup, MenuItemOptionChoice,
    DineInTable, DineInSession, DineInPaymentSplit,
)
from services.order.order_service import DeliveryZone

ops_bp = Blueprint(
    'ops',
    __name__,
    template_folder='templates/ops',
    url_prefix='/ops',
)

@ops_bp.after_request
def _restore_device_cookie_if_needed(response):
    restore_token = getattr(g, '_ops_restore_device_cookie', None)
    if restore_token:
        response.set_cookie(
            'ops_device_token',
            restore_token,
            max_age=365 * 24 * 3600,
            httponly=True,
            samesite='Lax',
            secure=_is_secure(),
        )
    return response


def _settings():
    return SiteSettings.query.first()

def _get_israel_now():
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo('Asia/Jerusalem'))
    except Exception:
        return datetime.now()

def _israel_today_start_utc():
    il_now = _get_israel_now()
    il_midnight = il_now.replace(hour=0, minute=0, second=0, microsecond=0)
    try:
        from zoneinfo import ZoneInfo
        return il_midnight.astimezone(ZoneInfo('UTC')).replace(tzinfo=None)
    except Exception:
        return il_midnight.replace(tzinfo=None) - timedelta(hours=3)

def _to_il(dt, fmt='%d/%m %H:%M'):
    if dt is None:
        return ''
    try:
        from zoneinfo import ZoneInfo
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo('UTC'))
        return dt.astimezone(ZoneInfo('Asia/Jerusalem')).strftime(fmt)
    except Exception:
        return (dt + timedelta(hours=3)).strftime(fmt)

def _to_il_hour(dt):
    return _to_il(dt, '%H:%M')

def _to_il_full(dt):
    return _to_il(dt, '%d/%m/%Y %H:%M')

def _verify_print_api_key():
    api_key = request.headers.get('X-Print-Key') or request.args.get('key')
    if not api_key:
        return False
    master_key = os.environ.get('PRINT_AGENT_KEY', '')
    if master_key and api_key == master_key:
        return True
    ak = ApiKey.query.filter_by(key=api_key, is_active=True).first()
    if ak:
        ak.last_used_at = datetime.utcnow()
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
        return True
    return False


from urllib.parse import urlparse as _urlparse

@ops_bp.before_request
def _validate_csrf_origin():
    if request.method in ('GET', 'HEAD', 'OPTIONS'):
        return None
    if _verify_print_api_key():
        return None
    origin = request.headers.get('Origin') or ''
    referer = request.headers.get('Referer') or ''
    host = request.host
    if origin:
        parsed = _urlparse(origin)
        if parsed.netloc == host:
            return None
    if referer:
        parsed = _urlparse(referer)
        if parsed.netloc == host:
            return None
    from flask_wtf.csrf import validate_csrf
    token = request.headers.get('X-CSRFToken') or request.form.get('csrf_token')
    if token:
        try:
            validate_csrf(token)
            return None
        except Exception:
            pass
    return jsonify({'ok': False, 'error': 'CSRF validation failed'}), 403


def _check_device():
    token = request.cookies.get('ops_device_token')
    if not token:
        backup_device_id = session.get('ops_device_db_id')
        if backup_device_id:
            device = EnrolledDevice.query.filter_by(id=backup_device_id, is_active=True).first()
            if device and device.enrolled_at:
                import logging
                logging.debug(f'OPS: restoring device cookie from session backup (device {device.id})')
                device.last_seen = datetime.utcnow()
                device.user_agent = request.headers.get('User-Agent', '')[:500]
                try:
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                g._ops_restore_device_cookie = device.device_token
                return device
        return None
    device = EnrolledDevice.query.filter_by(device_token=token, is_active=True).first()
    if device:
        device.last_seen = datetime.utcnow()
        device.user_agent = request.headers.get('User-Agent', '')[:500]
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
        if session.get('ops_device_db_id') != device.id:
            session['ops_device_db_id'] = device.id
            session.modified = True
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

def require_ops_any_module(*module_names):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            device = _check_device()
            if not device:
                return redirect(url_for('ops.not_enrolled'))
            user = _get_ops_user()
            if not user:
                return redirect(url_for('ops.login'))
            if not any(user.has_ops_permission(m) for m in module_names):
                if request.is_json:
                    return jsonify({'ok': False, 'error': 'אין הרשאה'}), 403
                modules = user.get_ops_modules()
                if modules:
                    return redirect(url_for('ops.' + modules[0]))
                return render_template('ops/not_enrolled.html', enrollment_code=None), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

def _get_current_pin():
    return _get_ops_user()

def _safe_json_list(raw):
    if not raw:
        return []
    try:
        val = json.loads(raw)
        return val if isinstance(val, list) else []
    except Exception:
        return []

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
    branch_ordering_status = 'open'
    if branch_id:
        branch = Branch.query.get(branch_id)
        if branch:
            branch_name = branch.name_he
            branch_ordering_status = branch.ordering_status or 'open'
    is_ops_superadmin = user.is_ops_superadmin if user else False
    all_branches = Branch.query.filter_by(is_active=True).all() if is_ops_superadmin else []
    return dict(
        ops_modules=modules,
        ops_user=user,
        ops_branch_id=branch_id,
        ops_branch_name=branch_name,
        branch_ordering_status=branch_ordering_status,
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
            session['ops_device_db_id'] = device.id
            session.modified = True
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
            session['ops_device_db_id'] = device.id
            session.modified = True
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

    session['ops_device_db_id'] = device.id
    session.modified = True

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
    today_start_utc = _israel_today_start_utc()
    today_logs = TimeLog.query.filter(TimeLog.clock_in >= today_start_utc)
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
    user = _get_ops_user()
    is_super = user and user.is_ops_superadmin
    branches = Branch.query.order_by(Branch.id).all() if is_super else []
    return render_template('ops/delivery.html', active_tab='delivery', zones=zones,
                           is_superadmin=is_super, branches=branches, effective_branch=effective_branch)


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

    submitted_branch_id = data.get('branch_id')
    if submitted_branch_id:
        try:
            submitted_branch_id = int(submitted_branch_id)
        except (TypeError, ValueError):
            submitted_branch_id = None

    if zone_id:
        zone = DeliveryZone.query.get(zone_id)
        if not zone:
            return jsonify({'ok': False, 'error': 'אזור לא נמצא'})
        if not is_super and effective_branch and zone.branch_id != effective_branch:
            return jsonify({'ok': False, 'error': 'אין הרשאה לערוך אזור זה'})
        if is_super and submitted_branch_id:
            zone.branch_id = submitted_branch_id
    else:
        zone = DeliveryZone()
        if effective_branch:
            zone.branch_id = effective_branch
        elif is_super and submitted_branch_id:
            zone.branch_id = submitted_branch_id
        elif is_super and not submitted_branch_id:
            return jsonify({'ok': False, 'error': 'יש לבחור סניף'})
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


@ops_bp.route('/print-devices')
@require_ops_module('orders')
def print_devices_page():
    user = _get_ops_user()
    if not user or not user.is_ops_superadmin:
        flash('אין לך הרשאה לגשת לדף זה', 'danger')
        return redirect(url_for('ops.home'))
    cutoff = datetime.utcnow() - timedelta(minutes=2)
    devices = PrintDevice.query.all()
    for d in devices:
        if d.last_heartbeat and d.last_heartbeat < cutoff:
            d.is_online = False
    db.session.commit()
    branches = Branch.query.filter_by(is_active=True).order_by(Branch.display_order).all()
    print_key = os.environ.get('PRINT_AGENT_KEY', '')
    return render_template('ops/print_devices.html', devices=devices, branches=branches, active_tab='settings', print_key=print_key)


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


@ops_bp.route('/healthcheck')
@require_ops_module('home')
def healthcheck():
    user = _get_ops_user()
    if not user or not user.is_ops_superadmin:
        flash('אין לך הרשאה', 'danger')
        return redirect(url_for('ops.home'))
    return render_template('ops/healthcheck.html', active_tab='settings')


@ops_bp.route('/api/healthcheck')
def api_healthcheck():
    is_api_key_auth = _verify_print_api_key()

    if not is_api_key_auth:
        device = _check_device()
        user = _get_ops_user()
        if not device or not user or not user.is_ops_superadmin:
            return jsonify({'ok': False, 'error': 'אין הרשאה'}), 403

    import requests as http_requests
    checks = []

    t0 = _time.time()
    try:
        db.session.execute(db.text('SELECT 1'))
        ms = round((_time.time() - t0) * 1000)
        checks.append({'id': 'database', 'name': 'מסד נתונים', 'name_en': 'Database', 'status': 'ok', 'ms': ms})
    except Exception as e:
        ms = round((_time.time() - t0) * 1000)
        checks.append({'id': 'database', 'name': 'מסד נתונים', 'name_en': 'Database', 'status': 'error', 'ms': ms, 'detail': str(e)[:120]})

    t0 = _time.time()
    try:
        from app import app
        with app.test_client() as tc:
            resp = tc.get('/ops/login')
        ms = round((_time.time() - t0) * 1000)
        checks.append({'id': 'webserver', 'name': 'שרת אינטרנט', 'name_en': 'Web Server', 'status': 'ok' if resp.status_code < 500 else 'error', 'ms': ms, 'detail': f'HTTP {resp.status_code}'})
    except Exception as e:
        ms = round((_time.time() - t0) * 1000)
        checks.append({'id': 'webserver', 'name': 'שרת אינטרנט', 'name_en': 'Web Server', 'status': 'error', 'ms': ms, 'detail': str(e)[:120]})

    sms_key = os.environ.get('SMS4FREE_KEY', '').strip()
    sms_user = os.environ.get('SMS4FREE_USER', '').strip()
    sms_pass = os.environ.get('SMS4FREE_PASS', '').strip()
    if sms_key and sms_user and sms_pass:
        t0 = _time.time()
        try:
            resp = http_requests.get('https://www.sms4free.co.il/ApiSMS/v2/SendSMS', timeout=8)
            ms = round((_time.time() - t0) * 1000)
            checks.append({'id': 'sms', 'name': 'SMS', 'name_en': 'SMS (SMS4Free)', 'status': 'ok' if resp.status_code < 500 else 'warn', 'ms': ms, 'detail': f'API reachable ({resp.status_code})'})
        except Exception as e:
            ms = round((_time.time() - t0) * 1000)
            checks.append({'id': 'sms', 'name': 'SMS', 'name_en': 'SMS (SMS4Free)', 'status': 'error', 'ms': ms, 'detail': str(e)[:120]})
    else:
        checks.append({'id': 'sms', 'name': 'SMS', 'name_en': 'SMS (SMS4Free)', 'status': 'unconfigured', 'ms': 0, 'detail': 'חסרים פרטי חיבור'})

    hyp_terminal = os.environ.get('HYP_TERMINAL', '').strip()
    hyp_api_key = os.environ.get('HYP_API_KEY', '').strip()
    if hyp_terminal and hyp_api_key:
        t0 = _time.time()
        try:
            resp = http_requests.get('https://icom.yaad.net/p/', timeout=8)
            ms = round((_time.time() - t0) * 1000)
            checks.append({'id': 'hyp', 'name': 'תשלומים HYP', 'name_en': 'Payment (HYP)', 'status': 'ok' if resp.status_code < 500 else 'warn', 'ms': ms, 'detail': f'API reachable ({resp.status_code})'})
        except Exception as e:
            ms = round((_time.time() - t0) * 1000)
            checks.append({'id': 'hyp', 'name': 'תשלומים HYP', 'name_en': 'Payment (HYP)', 'status': 'error', 'ms': ms, 'detail': str(e)[:120]})
    else:
        checks.append({'id': 'hyp', 'name': 'תשלומים HYP', 'name_en': 'Payment (HYP)', 'status': 'unconfigured', 'ms': 0, 'detail': 'חסרים פרטי חיבור'})

    active_devices = PrintDevice.query.all()
    if active_devices:
        for dev in active_devices:
            last_seen = dev.last_heartbeat
            is_online = False
            age = 0
            if last_seen:
                age = (datetime.utcnow() - last_seen).total_seconds()
                is_online = age < 300
            checks.append({
                'id': f'print_device_{dev.id}',
                'name': f'מכשיר הדפסה: {dev.device_name or dev.device_id}',
                'name_en': f'Print Device: {dev.device_name or dev.device_id}',
                'status': 'ok' if is_online else 'warn',
                'ms': 0,
                'detail': f'נראה לפני {int(age)} שניות' if last_seen else 'לא נצפה',
            })
    else:
        checks.append({'id': 'print_devices', 'name': 'מכשירי הדפסה', 'name_en': 'Print Devices', 'status': 'unconfigured', 'ms': 0, 'detail': 'אין מכשירים רשומים'})

    printers = Printer.query.filter_by(is_active=True).all()
    for printer in printers:
        ip = (printer.ip_address or '').strip()
        port = printer.port or 9100
        if ip:
            t0 = _time.time()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((ip, port))
                s.close()
                ms = round((_time.time() - t0) * 1000)
                checks.append({'id': f'printer_{printer.id}', 'name': f'מדפסת: {printer.name}', 'name_en': f'Printer: {printer.name}', 'status': 'ok', 'ms': ms, 'detail': f'{ip}:{port}'})
            except Exception as e:
                ms = round((_time.time() - t0) * 1000)
                checks.append({'id': f'printer_{printer.id}', 'name': f'מדפסת: {printer.name}', 'name_en': f'Printer: {printer.name}', 'status': 'error', 'ms': ms, 'detail': f'{ip}:{port} - {str(e)[:60]}'})

    return jsonify({'ok': True, 'checks': checks, 'timestamp': datetime.utcnow().isoformat()})


@ops_bp.route('/home')
@require_ops_module('home')
def home():
    settings = _settings()
    now = _get_israel_now()
    today_start_utc = _israel_today_start_utc()
    effective_branch = _get_effective_branch_id()

    today_q = FoodOrder.query.filter(FoodOrder.created_at >= today_start_utc)
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

    recent_q = FoodOrder.query.filter(FoodOrder.created_at >= today_start_utc)
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

    if type_filter == 'dine_in':
        query = query.filter_by(order_type='dine_in')
    elif type_filter == 'delivery':
        query = query.filter_by(order_type='delivery')
    elif type_filter == 'pickup':
        query = query.filter_by(order_type='pickup')
    else:
        query = query.filter(FoodOrder.order_type != 'dine_in')

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
    from sqlalchemy import func, case
    count_q = db.session.query(
        func.sum(case((FoodOrder.status.in_(['pending', 'confirmed']), 1), else_=0)).label('new_count'),
        func.sum(case((FoodOrder.status == 'preparing', 1), else_=0)).label('preparing_count'),
        func.sum(case((FoodOrder.status == 'ready', 1), else_=0)).label('ready_count'),
        func.sum(case((FoodOrder.status.in_(['delivered', 'pickedup']), 1), else_=0)).label('done_count'),
        func.sum(case((FoodOrder.status == 'cancelled', 1), else_=0)).label('cancelled_count'),
    )
    if effective_branch:
        count_q = count_q.filter(FoodOrder.branch_id == effective_branch)
    if type_filter == 'dine_in':
        count_q = count_q.filter(FoodOrder.order_type == 'dine_in')
    elif type_filter == 'delivery':
        count_q = count_q.filter(FoodOrder.order_type == 'delivery')
    elif type_filter == 'pickup':
        count_q = count_q.filter(FoodOrder.order_type == 'pickup')
    else:
        count_q = count_q.filter(FoodOrder.order_type != 'dine_in')
    cr = count_q.one()
    counts = {
        'new': cr.new_count or 0,
        'preparing': cr.preparing_count or 0,
        'ready': cr.ready_count or 0,
        'done': cr.done_count or 0,
        'cancelled': cr.cancelled_count or 0,
    }
    counts['active'] = counts['new'] + counts['preparing'] + counts['ready']

    categories = {c.id: c.name_he for c in MenuCategory.query.all()}

    from models import SMSTemplate
    from sqlalchemy import or_
    effective_branch = _get_effective_branch_id()
    sms_tpl_q = SMSTemplate.query.filter_by(is_active=True)
    if effective_branch:
        sms_tpl_q = sms_tpl_q.filter(or_(SMSTemplate.branch_id.is_(None), SMSTemplate.branch_id == effective_branch))
    else:
        sms_tpl_q = sms_tpl_q.filter(SMSTemplate.branch_id.is_(None))
    sms_tpls = sms_tpl_q.order_by(SMSTemplate.id).all()
    sms_templates_data = [{'id': t.id, 'name_he': t.name_he, 'content_he': t.content_he or ''} for t in sms_tpls]

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
        sms_templates=sms_templates_data,
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
    terminal_statuses = ('delivered', 'pickedup', 'cancelled')
    if old_status in terminal_statuses and new_status == 'preparing':
        return jsonify({'ok': False, 'error': 'לא ניתן לשנות סטטוס הזמנה סגורה'})
    order.status = new_status
    now = datetime.utcnow()
    if new_status == 'confirmed':
        new_status = 'preparing'
        order.status = new_status
    if new_status == 'preparing':
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

    auto_sms_sent = 0
    if old_status != new_status:
        try:
            auto_sms_sent = _auto_send_sms_for_status(order, new_status)
        except Exception as e:
            import logging
            logging.error(f'Auto-SMS failed for order {order.id} status {new_status}: {e}')
        try:
            _notify_sse_status_change(order, old_status, new_status)
        except Exception as e:
            import logging
            logging.debug(f'SSE status notify: {e}')
        if new_status == 'preparing' and old_status != 'preparing' and not order.bon_printed:
            try:
                _queue_print_for_app(order)
            except Exception as e:
                import logging
                logging.debug(f'Auto-print queue for order {order.id}: {e}')

    msg = f'הזמנה #{order.order_number} → {OPS_STATUS_LABELS.get(new_status, new_status)}'
    if auto_sms_sent:
        msg += f' | SMS נשלח ({auto_sms_sent})'

    return jsonify({
        'ok': True,
        'message': msg,
        'new_status': new_status,
        'label': OPS_STATUS_LABELS.get(new_status, new_status),
        'auto_sms_sent': auto_sms_sent,
    })


def _auto_send_sms_for_status(order, new_status):
    from models import SMSAutoTrigger, SMSLog, Branch
    from standalone_order_service.sms_helpers import create_sender_from_env
    triggers = SMSAutoTrigger.query.filter_by(order_status=new_status, is_active=True).all()
    if not triggers:
        return 0
    phone = order.customer_phone
    if not phone:
        return 0

    branch_trigger = None
    global_trigger = None
    for trigger in triggers:
        if trigger.branch_id and trigger.branch_id == order.branch_id:
            branch_trigger = trigger
            break
        elif not trigger.branch_id:
            global_trigger = trigger

    effective_trigger = branch_trigger or global_trigger
    if not effective_trigger:
        return 0
    template = effective_trigger.template
    if not template or not template.is_active:
        return 0

    send_fn = create_sender_from_env()
    branch = Branch.query.get(order.branch_id) if order.branch_id else None
    user = _get_ops_user()
    message = template.render(order=order, branch=branch)
    status = 'sent'
    error_msg = None
    sent_count = 0
    if send_fn:
        try:
            send_fn(phone, message)
            sent_count = 1
        except Exception as e:
            status = 'failed'
            error_msg = str(e)
            import logging
            logging.error(f'Auto-SMS send failed for order {order.id}, trigger {effective_trigger.id}: {e}')
    else:
        status = 'failed'
        error_msg = 'SMS provider not configured'
    log = SMSLog(
        order_id=order.id,
        recipient_phone=phone,
        message_type='auto_trigger',
        message_text=message,
        status=status,
        error_message=error_msg,
        staff_name=user.name if user else 'Auto',
    )
    db.session.add(log)
    db.session.commit()
    return sent_count


@ops_bp.route('/api/orders/<int:order_id>/send-sms', methods=['POST'])
@require_ops_module('orders')
def send_order_sms(order_id):
    from models import SMSLog, Branch
    from standalone_order_service.sms_helpers import create_sender_from_env
    order = FoodOrder.query.get(order_id)
    if not order:
        return jsonify({'ok': False, 'error': 'הזמנה לא נמצאה'})
    effective_branch = _get_effective_branch_id()
    if effective_branch and order.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'הזמנה לא שייכת לסניף זה'})
    phone = order.customer_phone
    if not phone:
        return jsonify({'ok': False, 'error': 'אין מספר טלפון להזמנה'})
    data = request.get_json(force=True)
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'ok': False, 'error': 'נא לכתוב הודעה'})
    send_fn = create_sender_from_env()
    user = _get_ops_user()
    status = 'sent'
    error_msg = None
    if send_fn:
        try:
            send_fn(phone, message)
        except Exception as e:
            status = 'failed'
            error_msg = str(e)
    else:
        status = 'failed'
        error_msg = 'SMS provider not configured'
    log = SMSLog(
        order_id=order.id,
        recipient_phone=phone,
        message_type='manual_ops',
        message_text=message,
        status=status,
        error_message=error_msg,
        staff_name=user.name if user else 'Ops',
    )
    db.session.add(log)
    db.session.commit()
    if status == 'sent':
        return jsonify({'ok': True, 'message': f'SMS נשלח ל-{phone}'})
    else:
        return jsonify({'ok': False, 'error': f'שליחה נכשלה: {error_msg}'})


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
            'created_at': _to_il_hour(order.created_at),
            'items': items,
            'items_by_category': by_category,
            'items_by_station': by_station,
            'branch_name': order.branch_name or '',
            'estimated_ready_at': _to_il_hour(order.estimated_ready_at),
            'source': getattr(order, 'source', 'online') or 'online',
        }
    })


@ops_bp.route('/orders/new/<order_type>')
@require_ops_module('orders')
def manual_order(order_type):
    if order_type not in ('takeaway', 'delivery'):
        return redirect(url_for('ops.orders'))
    effective_branch = _get_effective_branch_id()
    categories = MenuCategory.query.filter_by(is_active=True, show_in_order=True).order_by(MenuCategory.display_order).all()
    menu_data = []
    for cat in categories:
        items_q = MenuItem.query.filter_by(category_id=cat.id, is_available=True, show_in_order=True)
        cat_items = []
        for item in items_q.order_by(MenuItem.display_order).all():
            if effective_branch:
                bmi = BranchMenuItem.query.filter_by(branch_id=effective_branch, menu_item_id=item.id).first()
                if bmi and not bmi.is_available:
                    continue
                price = bmi.custom_price if (bmi and bmi.custom_price is not None) else item.base_price
            else:
                price = item.base_price
            option_groups = []
            for og in item.option_groups:
                if not og.is_active:
                    continue
                choices = []
                for ch in og.choices:
                    if not ch.is_available:
                        continue
                    choices.append({
                        'id': ch.id,
                        'name_he': ch.name_he,
                        'price_modifier': ch.price_modifier or 0,
                        'is_default': ch.is_default,
                    })
                if choices:
                    option_groups.append({
                        'id': og.id,
                        'name_he': og.name_he,
                        'selection_type': og.selection_type,
                        'is_required': og.is_required,
                        'min_selections': og.min_selections or 0,
                        'max_selections': og.max_selections or 0,
                        'choices': choices,
                    })
            from models import GlobalOptionGroupLink
            global_links = GlobalOptionGroupLink.query.filter_by(menu_item_id=item.id).all()
            for link in global_links:
                gog = link.global_group
                if not gog or not gog.is_active:
                    continue
                if link.linked_option_group_id:
                    continue
                g_choices = []
                for gc in gog.choices:
                    if not gc.is_available:
                        continue
                    g_choices.append({
                        'id': gc.id,
                        'name_he': gc.name_he,
                        'price_modifier': gc.price_modifier or 0,
                        'is_default': gc.is_default,
                        'is_global': True,
                    })
                if g_choices:
                    option_groups.append({
                        'id': f'g_{gog.id}',
                        'name_he': gog.name_he,
                        'selection_type': gog.selection_type,
                        'is_required': gog.is_required,
                        'min_selections': gog.min_selections or 0,
                        'max_selections': gog.max_selections or 0,
                        'choices': g_choices,
                    })
            cat_items.append({
                'id': item.id,
                'name_he': item.name_he,
                'name_en': item.name_en or '',
                'price': float(price) if price else 0,
                'description_he': item.short_description_he or item.description_he or '',
                'image_path': item.image_path or '',
                'option_groups': option_groups,
            })
        if cat_items:
            menu_data.append({
                'id': cat.id,
                'name_he': cat.name_he,
                'icon': cat.icon or 'utensils',
                'items': cat_items,
            })
    deals_data = []
    active_deals = Deal.query.filter_by(is_active=True).order_by(Deal.display_order).all()
    for deal in active_deals:
        if not deal.is_valid():
            continue
        deal_info = {
            'id': deal.id,
            'name_he': deal.name_he,
            'name_en': deal.name_en or '',
            'deal_price': float(deal.deal_price),
            'original_price': float(deal.original_price) if deal.original_price else None,
            'description_he': deal.description_he or '',
            'deal_type': deal.deal_type or 'fixed',
            'included_items': deal.included_items or [],
            'image_path': deal.image_path or '',
        }
        if deal.deal_type == 'customer_picks':
            deal_info['pick_count'] = deal.pick_count or 0
            source_cats = deal.effective_category_ids
            deal_info['source_category_ids'] = source_cats
            pick_items = []
            for sc_id in source_cats:
                sc_items = MenuItem.query.filter_by(category_id=sc_id, is_available=True, show_in_order=True).order_by(MenuItem.display_order).all()
                for pi in sc_items:
                    if effective_branch:
                        bmi = BranchMenuItem.query.filter_by(branch_id=effective_branch, menu_item_id=pi.id).first()
                        if bmi and not bmi.is_available:
                            continue
                    pick_items.append({
                        'item_id': pi.id,
                        'name_he': pi.name_he,
                        'name_en': pi.name_en or '',
                    })
            deal_info['pick_items'] = pick_items
        else:
            included_details = []
            for inc in (deal.included_items or []):
                inc_id = inc.get('item_id') or inc.get('id')
                if inc_id:
                    inc_item = MenuItem.query.get(int(inc_id))
                    if inc_item:
                        included_details.append({
                            'item_id': inc_item.id,
                            'name_he': inc_item.name_he,
                            'qty': inc.get('qty') or inc.get('quantity') or 1,
                        })
            deal_info['included_details'] = included_details
        deals_data.append(deal_info)
    return render_template('ops/manual_order.html',
        active_tab='orders',
        order_type=order_type,
        menu_data=menu_data,
        deals_data=deals_data,
    )


@ops_bp.route('/api/orders/create', methods=['POST'])
@require_ops_module('orders')
def create_manual_order():
    from standalone_order_service.order_helpers import (
        sanitize_phone, validate_phone_digits,
        verify_cart_items, calculate_delivery_fee,
    )
    import secrets as _secrets
    data = request.get_json(force=True)
    order_type_raw = data.get('order_type', 'takeaway')
    order_type = 'delivery' if order_type_raw == 'delivery' else 'pickup'
    customer_name = (data.get('customer_name') or '').strip()[:120]
    customer_phone = sanitize_phone(data.get('customer_phone'))
    delivery_address = (data.get('delivery_address') or '').strip()[:300]
    delivery_city = (data.get('delivery_city') or '').strip()[:100]
    delivery_notes = (data.get('delivery_notes') or '').strip()[:500]
    customer_notes = (data.get('customer_notes') or '').strip()[:500]
    payment_method = data.get('payment_method', 'cash')
    if payment_method not in ('cash', 'card'):
        payment_method = 'cash'
    if not customer_name or not customer_phone:
        return jsonify({'ok': False, 'error': 'נא למלא שם וטלפון'})
    if not validate_phone_digits(customer_phone):
        return jsonify({'ok': False, 'error': 'מספר טלפון לא תקין'})
    if order_type == 'delivery' and not delivery_address:
        return jsonify({'ok': False, 'error': 'נא למלא כתובת למשלוח'})
    cart = data.get('items', [])
    if not cart:
        return jsonify({'ok': False, 'error': 'לא נבחרו פריטים'})
    effective_branch = _get_effective_branch_id()
    branch = Branch.query.get(effective_branch) if effective_branch else None
    valid_cart, verified_subtotal = verify_cart_items(cart, effective_branch)
    if not valid_cart:
        return jsonify({'ok': False, 'error': 'סל ריק או פריטים לא תקינים'})
    settings = _settings()
    delivery_zone_id = data.get('delivery_zone_id') if order_type == 'delivery' else None
    delivery_fee, min_order_error = calculate_delivery_fee(
        order_type, verified_subtotal, delivery_zone_id, effective_branch, settings
    )
    if min_order_error:
        return jsonify({'ok': False, 'error': min_order_error})
    total_amount = verified_subtotal + delivery_fee
    order = FoodOrder()
    order.set_order_number()
    order.tracking_token = _secrets.token_urlsafe(24)
    if branch:
        order.branch_id = branch.id
        order.branch_name = branch.name_he
    order.order_type = order_type
    order.customer_name = customer_name
    order.customer_phone = customer_phone
    order.delivery_address = delivery_address
    order.delivery_city = delivery_city
    order.delivery_notes = delivery_notes
    order.customer_notes = customer_notes
    order.payment_method = payment_method
    order.subtotal = verified_subtotal
    order.delivery_fee = delivery_fee
    order.total_amount = total_amount
    order.status = 'pending'
    order.payment_status = 'cash' if payment_method == 'cash' else 'pending'
    order.source = 'ops'
    order.items_json = json.dumps(valid_cart, ensure_ascii=False)
    db.session.add(order)
    db.session.flush()
    for item in valid_cart:
        oi = FoodOrderItem()
        oi.order_id = order.id
        if item.get('is_deal'):
            oi.menu_item_id = None
            oi.item_name_he = item.get('name_he', '')
            oi.item_name_en = item.get('name_en', '')
            oi.quantity = int(item.get('qty', 1))
            oi.unit_price = float(item.get('price', 0))
            oi.total_price = oi.quantity * oi.unit_price
            oi.special_instructions = item.get('notes', '')
            deal_data = {'is_deal': True, 'deal_id': item.get('deal_id')}
            if item.get('deal_type') == 'customer_picks':
                deal_data['deal_type'] = 'customer_picks'
                deal_data['selected_items'] = item.get('selected_items', [])
                deal_data['included_items'] = []
            else:
                deal_data['included_items'] = item.get('included_items', [])
            oi.options_json = json.dumps(deal_data, ensure_ascii=False)
        else:
            oi.menu_item_id = item.get('id')
            oi.item_name_he = item.get('name_he', '')
            oi.item_name_en = item.get('name_en', '')
            oi.quantity = int(item.get('qty', 1))
            oi.unit_price = float(item.get('price', 0))
            oi.total_price = oi.quantity * oi.unit_price
            oi.special_instructions = item.get('notes', '')
            if item.get('options'):
                oi.options_json = json.dumps(item['options'], ensure_ascii=False)
        db.session.add(oi)
    db.session.commit()
    return jsonify({
        'ok': True,
        'message': f'הזמנה #{order.order_number} נוצרה בהצלחה',
        'order_id': order.id,
        'order_number': order.order_number,
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


@ops_bp.route('/api/branch-status', methods=['POST'])
@require_ops_any_module('branches', 'orders', 'home')
def update_branch_status():
    user = _get_ops_user()
    effective_branch = _get_effective_branch_id()
    data = request.get_json(force=True)
    new_status = data.get('status')
    branch_id = data.get('branch_id') or effective_branch
    if new_status not in ('open', 'busy', 'closed'):
        return jsonify({'ok': False, 'error': 'סטטוס לא תקין'}), 400
    if not branch_id:
        return jsonify({'ok': False, 'error': 'לא נבחר סניף'}), 400
    branch = Branch.query.get(branch_id)
    if not branch:
        return jsonify({'ok': False, 'error': 'סניף לא נמצא'}), 404
    if not user.is_ops_superadmin and (not effective_branch or branch.id != effective_branch):
        return jsonify({'ok': False, 'error': 'אין הרשאה לשנות סניף זה'}), 403
    branch.ordering_status = new_status
    db.session.commit()
    status_labels = {'open': 'פתוח', 'busy': 'עמוס', 'closed': 'סגור'}
    return jsonify({'ok': True, 'message': f'סטטוס סניף עודכן: {status_labels.get(new_status, new_status)}'})


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

    def __init__(self, ip, port=9100, encoding='cp862', codepage_num=36):
        self.ip = ip
        self.port = port
        self.encoding = encoding
        self.codepage_num = codepage_num
        self.buf = bytearray()

    def _add(self, data):
        if isinstance(data, str):
            self.buf.extend(data.encode(self.encoding, errors='replace'))
        else:
            self.buf.extend(data)

    def init(self):
        self._add(self.INIT)
        self._add(b'\x1bt' + bytes([self.codepage_num]))

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
    p.text(_to_il(o.created_at) if o.created_at else '')
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
    p.text(f'צ׳קר | {_to_il_hour(datetime.utcnow())}')
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
    p.text(f'{type_he} | {_to_il(o.created_at) if o.created_at else ""}')
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
    p.text(_to_il_hour(datetime.utcnow()))
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
    p.text(f'{type_he} | {_to_il(o.created_at) if o.created_at else ""}')
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
    p.text(f'#{o.order_number} | {station_name} | {_to_il_hour(datetime.utcnow())}')
    p.cut()


def _get_printer_routing(branch_id):
    printers = Printer.query.filter_by(branch_id=branch_id, is_active=True).order_by(Printer.display_order).all()
    station_map = {}
    default_printer = None
    for p in printers:
        pd = p.to_dict()
        if p.is_default:
            default_printer = pd
        for st in p.stations:
            station_map[st.station_name] = pd
    return default_printer, station_map, printers


def _build_print_jobs(order, items, by_station, checker_copies, payment_copies, station_bons):
    default_printer, station_map, printers = _get_printer_routing(order.branch_id or 0)
    fallback = default_printer or (printers[0].to_dict() if printers else None)

    jobs = []

    for _ in range(checker_copies):
        jobs.append({
            'bon_type': 'checker',
            'printer': fallback,
            'order_id': order.id,
            'order_number': order.order_number,
            'items': items,
        })

    for _ in range(payment_copies):
        jobs.append({
            'bon_type': 'payment',
            'printer': fallback,
            'order_id': order.id,
            'order_number': order.order_number,
        })

    if station_bons and by_station:
        for st_name, st_items in by_station.items():
            target = station_map.get(st_name, fallback)
            jobs.append({
                'bon_type': 'station',
                'station_name': st_name,
                'printer': target,
                'order_id': order.id,
                'order_number': order.order_number,
                'items': st_items,
            })

    return jobs


def _queue_print_for_app(order, checker_copies=2, payment_copies=1, station_bons=True, persist_options=True):
    if persist_options and not order.bon_print_options:
        order.bon_print_options = json.dumps({
            'checker_copies': checker_copies,
            'payment_copies': payment_copies,
            'station_bons': station_bons,
        })
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
    items = json.loads(order.items_json) if order.items_json else []
    by_station = {}
    for item in items:
        menu_item_id = item.get('menu_item_id') or item.get('item_id') or item.get('id')
        st = 'כללי'
        if menu_item_id:
            mi = MenuItem.query.get(menu_item_id)
            if mi:
                st = mi.print_station or 'כללי'
                if order.branch_id:
                    bmi = BranchMenuItem.query.filter_by(branch_id=order.branch_id, menu_item_id=menu_item_id).first()
                    if bmi and bmi.print_station:
                        st = bmi.print_station
                if mi.print_name:
                    item['print_name'] = mi.print_name
        if st not in by_station:
            by_station[st] = []
        by_station[st].append(item)

    print_jobs = _build_print_jobs(order, items, by_station, checker_copies, payment_copies, station_bons)

    order_event_data = {
        'type': 'print_order',
        'id': order.id,
        'order_number': order.order_number,
        'order_type': order.order_type,
        'branch_id': order.branch_id,
        'status': order.status,
        'customer_name': order.customer_name or '',
        'customer_phone': order.customer_phone or '',
        'delivery_address': order.delivery_address or '',
        'delivery_city': order.delivery_city or '',
        'delivery_notes': order.delivery_notes or '',
        'customer_notes': order.customer_notes or '',
        'subtotal': order.subtotal or 0,
        'delivery_fee': order.delivery_fee or 0,
        'discount_amount': order.discount_amount or 0,
        'total_amount': order.total_amount or 0,
        'payment_method': order.payment_method or '',
        'coupon_code': order.coupon_code or '',
        'created_at': _to_il(order.created_at) if order.created_at else '',
        'items': items,
        'items_by_station': by_station,
        'checker_copies': checker_copies,
        'payment_copies': payment_copies,
        'station_bons': station_bons,
        'print_jobs': print_jobs,
    }
    _notify_sse_order_event(order_event_data)

    _notify_sse_order_event({
        'type': 'new_print_job',
        'print_job_id': secrets.token_hex(8),
        'id': order.id,
        'order_number': order.order_number,
        'order_type': order.order_type,
        'branch_id': order.branch_id,
        'status': order.status,
        'customer_name': order.customer_name or '',
        'customer_phone': order.customer_phone or '',
        'delivery_address': order.delivery_address or '',
        'delivery_city': order.delivery_city or '',
        'delivery_notes': order.delivery_notes or '',
        'customer_notes': order.customer_notes or '',
        'subtotal': order.subtotal or 0,
        'delivery_fee': order.delivery_fee or 0,
        'discount_amount': order.discount_amount or 0,
        'total_amount': order.total_amount or 0,
        'payment_method': order.payment_method or '',
        'coupon_code': order.coupon_code or '',
        'created_at': _to_il(order.created_at) if order.created_at else '',
        'items': items,
        'items_by_station': by_station,
        'checker_copies': checker_copies,
        'payment_copies': payment_copies,
        'station_bons': station_bons,
        'print_jobs': print_jobs,
    })


@ops_bp.route('/api/print', methods=['POST'])
@require_ops_module('orders')
def direct_print():
    data = request.get_json(force=True)
    order_id = data.get('order_id')
    checker_copies = int(data.get('checker_copies', 2))
    payment_copies = int(data.get('payment_copies', 1))
    station_bons = data.get('station_bons', True)

    if not order_id:
        return jsonify({'ok': False, 'error': 'חסר מזהה הזמנה'})

    order = FoodOrder.query.get(order_id)
    if not order:
        return jsonify({'ok': False, 'error': 'הזמנה לא נמצאה'})
    effective_branch = _get_effective_branch_id()
    if effective_branch and order.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'הזמנה לא שייכת לסניף זה'})

    order.bon_printed = False
    order.bon_print_error = None
    order.bon_print_options = json.dumps({
        'checker_copies': checker_copies,
        'payment_copies': payment_copies,
        'station_bons': station_bons,
    })
    db.session.commit()
    _queue_print_for_app(order, checker_copies, payment_copies, station_bons, persist_options=False)
    return jsonify({'ok': True, 'message': 'נשלח לאפליקציית ההדפסה'})


@ops_bp.route('/api/orders/unprinted', methods=['GET'])
def get_unprinted_orders():
    is_api_key_auth = _verify_print_api_key()
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
        FoodOrder.status.in_(['preparing', 'ready'])
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

        print_options = {}
        if o.bon_print_options:
            try:
                print_options = json.loads(o.bon_print_options)
            except Exception:
                pass

        p_checker = print_options.get('checker_copies', 2)
        p_payment = print_options.get('payment_copies', 1)
        p_station = print_options.get('station_bons', True)
        print_jobs = _build_print_jobs(o, items, by_station, p_checker, p_payment, p_station)

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
            'created_at': _to_il(o.created_at) if o.created_at else '',
            'items': items,
            'items_by_station': by_station,
            'print_options': print_options,
            'print_jobs': print_jobs,
        })

    return jsonify({'ok': True, 'orders': result})


@ops_bp.route('/api/orders/mark-printed', methods=['POST'])
def mark_orders_printed():
    is_api_key_auth = _verify_print_api_key()
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
    if not _verify_print_api_key():
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

    cp862_map = {
        'א': 0x80, 'ב': 0x81, 'ג': 0x82, 'ד': 0x83, 'ה': 0x84,
        'ו': 0x85, 'ז': 0x86, 'ח': 0x87, 'ט': 0x88, 'י': 0x89,
        'ך': 0x8A, 'כ': 0x8B, 'ל': 0x8C, 'ם': 0x8D, 'מ': 0x8E,
        'ן': 0x8F, 'נ': 0x90, 'ס': 0x91, 'ע': 0x92, 'ף': 0x93,
        'פ': 0x94, 'ץ': 0x95, 'צ': 0x96, 'ק': 0x97, 'ר': 0x98,
        'ש': 0x99, 'ת': 0x9A,
    }

    return jsonify({
        'ok': True,
        'branch_id': branch_id,
        'branch_name': branch.name_he,
        'default_printer': default_printer,
        'station_map': station_map,
        'printers': [p.to_dict() for p in printers],
        'cp862_hebrew_map': cp862_map,
        'rtl': True,
        'rtl_note': 'Hebrew text must be reversed (character order) before sending to printer. ESC/POS printers print left-to-right only.',
    })


@ops_bp.route('/api/print/test-bytes', methods=['GET'])
def print_test_bytes():
    _verify_print_api_key()
    codepage_num = int(request.args.get('codepage_num', 36))

    test_text = "המבורגר קלאסי"
    reversed_text = test_text[::-1]

    cp862_map = {}
    for i, ch in enumerate("אבגדהוזחטיךכלםמןנסעףפץצקרשת"):
        cp862_map[ch] = 0x80 + i

    raw_bytes = []
    raw_bytes += [0x1B, 0x40]
    raw_bytes += [0x1B, 0x74, codepage_num]
    raw_bytes += [0x1B, 0x61, 0x01]

    for ch in reversed_text:
        if ch in cp862_map:
            raw_bytes.append(cp862_map[ch])
        else:
            raw_bytes.append(ord(ch))
    raw_bytes.append(0x0A)
    raw_bytes += [0x0A] * 6
    raw_bytes += [0x1D, 0x56, 0x00]

    hex_str = ' '.join(f'{b:02X}' for b in raw_bytes)
    dec_str = ' '.join(str(b) for b in raw_bytes)

    return jsonify({
        'ok': True,
        'description': f'Test print bytes for: {test_text}',
        'reversed_text': reversed_text,
        'codepage_num': codepage_num,
        'total_bytes': len(raw_bytes),
        'bytes_hex': hex_str,
        'bytes_decimal': dec_str,
        'raw_bytes_array': raw_bytes,
        'breakdown': {
            'init': '1B 40 (ESC @)',
            'codepage': f'1B 74 {codepage_num:02X} (ESC t {codepage_num})',
            'center': '1B 61 01 (ESC a 1)',
            'text_bytes': ' '.join(f'{b:02X}' for b in raw_bytes[6:-7]),
            'newline': '0A',
            'feed': '0A x6',
            'cut': '1D 56 00 (GS V 0)',
        },
        'android_must_send_exactly_these_bytes': raw_bytes,
        'note': 'If the Android app sends these exact bytes and it prints gibberish, the codepage_num is wrong for this printer. Try codepage_num=15 or codepage_num=7.',
    })


@ops_bp.route('/api/print/test', methods=['POST'])
@require_ops_module('orders')
def direct_print_test():
    data = request.get_json(force=True)
    printer_ip = data.get('printer_ip')
    printer_port = int(data.get('printer_port', 9100))
    if not printer_ip:
        return jsonify({'ok': False, 'error': 'חסר כתובת מדפסת'})

    encoding = data.get('encoding', 'cp862')
    codepage_num = int(data.get('codepage_num', 36))
    p = DirectPrinter(printer_ip, printer_port, encoding=encoding, codepage_num=codepage_num)
    p.init()
    p.align('center')
    p.font('double')
    p.text('SUMO')
    p.font('normal')
    p.text('בדיקת מדפסת')
    p.dashed()
    p.text(_to_il(datetime.utcnow(), '%Y-%m-%d %H:%M:%S'))
    p.text('החיבור תקין!')
    p.cut()
    success = p.send()
    if success:
        return jsonify({'ok': True, 'message': 'הדפסת בדיקה נשלחה'})
    else:
        return jsonify({'ok': False, 'error': 'שגיאת חיבור'})


@ops_bp.route('/history')
@require_ops_module('history')
def order_history():
    from models import FoodOrder, Branch
    effective_branch = _get_effective_branch_id()

    q = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '')
    type_filter = request.args.get('type', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    branch_filter = request.args.get('branch_id', '')

    query = FoodOrder.query
    if effective_branch:
        query = query.filter_by(branch_id=effective_branch)
    elif branch_filter:
        try:
            query = query.filter_by(branch_id=int(branch_filter))
        except (ValueError, TypeError):
            pass
    if q:
        query = query.filter(
            db.or_(
                FoodOrder.customer_name.ilike(f'%{q}%'),
                FoodOrder.customer_phone.ilike(f'%{q}%'),
                FoodOrder.order_number.ilike(f'%{q}%'),
            )
        )
    if status_filter:
        query = query.filter_by(status=status_filter)
    if type_filter:
        query = query.filter_by(order_type=type_filter)
    if date_from:
        try:
            df_local = datetime.strptime(date_from, '%Y-%m-%d')
            try:
                from zoneinfo import ZoneInfo
                df_utc = df_local.replace(tzinfo=ZoneInfo('Asia/Jerusalem')).astimezone(ZoneInfo('UTC')).replace(tzinfo=None)
            except Exception:
                df_utc = df_local - timedelta(hours=3)
            query = query.filter(FoodOrder.created_at >= df_utc)
        except ValueError:
            pass
    if date_to:
        try:
            dt_local = datetime.strptime(date_to, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            try:
                from zoneinfo import ZoneInfo
                dt_utc = dt_local.replace(tzinfo=ZoneInfo('Asia/Jerusalem')).astimezone(ZoneInfo('UTC')).replace(tzinfo=None)
            except Exception:
                dt_utc = dt_local - timedelta(hours=3)
            query = query.filter(FoodOrder.created_at <= dt_utc)
        except ValueError:
            pass

    orders = query.order_by(FoodOrder.created_at.desc()).limit(200).all()
    branches = Branch.query.order_by(Branch.name_he).all()

    pin = _get_current_pin()
    is_superadmin = pin.is_ops_superadmin if pin else False

    return render_template('ops/order_history.html',
        active_tab='history',
        orders=orders,
        q=q,
        status_filter=status_filter,
        type_filter=type_filter,
        date_from=date_from,
        date_to=date_to,
        branch_filter=branch_filter,
        branches=branches,
        is_superadmin=is_superadmin,
    )


@ops_bp.route('/api/orders/<int:order_id>/reorder', methods=['POST'])
@require_ops_module('history')
def reorder(order_id):
    import json as _json
    from models import FoodOrder, Branch as BranchModel
    original = FoodOrder.query.get(order_id)
    if not original:
        return jsonify({'ok': False, 'error': 'הזמנה לא נמצאה'})

    effective_branch = _get_effective_branch_id()
    if effective_branch and original.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'הזמנה לא שייכת לסניף זה'})

    items = original.get_items()
    reorder_data = {
        'source_order': original.order_number,
        'customer_name': original.customer_name or '',
        'customer_phone': original.customer_phone or '',
        'customer_email': original.customer_email or '',
        'order_type': original.order_type or 'pickup',
        'delivery_address': original.delivery_address or '',
        'delivery_city': original.delivery_city or '',
        'delivery_notes': original.delivery_notes or '',
        'branch_id': original.branch_id,
        'items': [{
            'menu_item_id': it.get('menu_item_id'),
            'name_he': it.get('item_name_he', it.get('name_he', '?')),
            'name_en': it.get('item_name_en', it.get('name_en', '')),
            'quantity': it.get('quantity', it.get('qty', 1)),
            'price': it.get('unit_price', it.get('price', 0)),
            'special_instructions': it.get('special_instructions', ''),
            'options_json': it.get('options_json'),
        } for it in items]
    }

    session['reorder_data'] = _json.dumps(reorder_data, ensure_ascii=False)
    session['reorder_customer'] = {
        'name': original.customer_name or '',
        'phone': original.customer_phone or '',
        'email': original.customer_email or '',
        'address': original.delivery_address or '',
        'city': original.delivery_city or '',
        'notes': original.delivery_notes or '',
    }

    order_url = url_for('order_page.order_page', branch_id=original.branch_id) if original.branch_id else url_for('order_page.order_page')

    return jsonify({'ok': True, 'redirect': order_url, 'message': f'מפנה להזמנה חוזרת מ-#{original.order_number}'})


@ops_bp.route('/api/orders/<int:order_id>/send-receipt', methods=['POST'])
@require_ops_any_module('orders', 'history')
def send_receipt(order_id):
    from models import FoodOrder, SMSLog
    order = FoodOrder.query.get(order_id)
    if not order:
        return jsonify({'ok': False, 'error': 'הזמנה לא נמצאה'})

    effective_branch = _get_effective_branch_id()
    if effective_branch and order.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'הזמנה לא שייכת לסניף זה'})

    if order.payment_method not in ('cash', None, ''):
        return jsonify({'ok': False, 'error': 'קבלות זמינות רק להזמנות מזומן'})

    if not order.customer_phone:
        return jsonify({'ok': False, 'error': 'אין מספר טלפון'})

    items = order.get_items()
    items_text = '\n'.join([
        f"  {it.get('name_he', it.get('item_name_he', '?'))} x{it.get('qty', it.get('quantity', 1))} - ₪{(it.get('price', it.get('unit_price', 0)) * it.get('qty', it.get('quantity', 1))):.0f}"
        for it in items
    ])

    branch_name = order.branch_name or 'SUMO'
    msg = (
        f"קבלה - {branch_name}\n"
        f"הזמנה: {order.order_number}\n"
        f"תאריך: {_to_il_full(order.created_at) if order.created_at else '-'}\n"
        f"---\n"
        f"{items_text}\n"
        f"---\n"
        f"סה\"כ: ₪{order.total_amount:.0f}\n"
        f"תשלום: מזומן\n"
        f"תודה רבה! 🙏"
    )

    from standalone_order_service.sms_helpers import create_sender_from_env
    send_sms = create_sender_from_env()
    if not send_sms:
        return jsonify({'ok': False, 'error': 'ספק SMS לא מוגדר'})

    success = send_sms(order.customer_phone, msg)
    pin = _get_current_pin()

    sms_log = SMSLog(
        recipient_phone=order.customer_phone,
        message_text=msg,
        message_type='receipt',
        status='sent' if success else 'failed',
        order_id=order.id,
        staff_name=pin.name if pin else 'Ops',
    )
    db.session.add(sms_log)
    db.session.commit()

    if success:
        return jsonify({'ok': True, 'message': 'קבלה נשלחה בהצלחה'})
    return jsonify({'ok': False, 'error': 'שליחה נכשלה'})


@ops_bp.route('/api/orders/<int:order_id>/delete', methods=['POST'])
@require_ops_any_module('orders', 'history')
def delete_order(order_id):
    import json as _json
    from models import FoodOrder, ArchivedOrder

    pin = _get_current_pin()
    if not pin or not pin.is_ops_superadmin:
        return jsonify({'ok': False, 'error': 'הרשאת מנהל נדרשת'})

    order = FoodOrder.query.get(order_id)
    if not order:
        return jsonify({'ok': False, 'error': 'הזמנה לא נמצאה'})

    if order.payment_method not in ('cash', None, ''):
        return jsonify({'ok': False, 'error': 'ניתן למחוק רק הזמנות מזומן'})

    effective_branch = _get_effective_branch_id()
    if effective_branch and order.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'הזמנה לא שייכת לסניף זה'})

    data = request.get_json(force=True) if request.is_json else {}
    reason = data.get('reason', '')

    items_list = order.get_items()
    if not items_list:
        items_list = []
        for item in order.items:
            items_list.append({
                'item_name_he': item.item_name_he,
                'item_name_en': item.item_name_en,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'total_price': item.total_price,
                'special_instructions': item.special_instructions,
                'options_json': item.options_json,
            })

    full_data = {
        'id': order.id,
        'order_number': order.order_number,
        'branch_id': order.branch_id,
        'branch_name': order.branch_name,
        'order_type': order.order_type,
        'status': order.status,
        'customer_name': order.customer_name,
        'customer_phone': order.customer_phone,
        'customer_email': order.customer_email,
        'delivery_address': order.delivery_address,
        'delivery_city': order.delivery_city,
        'subtotal': order.subtotal,
        'delivery_fee': order.delivery_fee,
        'discount_amount': order.discount_amount,
        'total_amount': order.total_amount,
        'payment_method': order.payment_method,
        'payment_status': order.payment_status,
        'coupon_code': order.coupon_code,
        'customer_notes': order.customer_notes,
        'admin_notes': order.admin_notes,
        'created_at': order.created_at.isoformat() if order.created_at else None,
        'items': items_list,
    }

    archived = ArchivedOrder(
        original_order_id=order.id,
        order_number=order.order_number,
        branch_id=order.branch_id,
        branch_name=order.branch_name,
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        customer_email=order.customer_email,
        order_type=order.order_type,
        status=order.status,
        payment_method=order.payment_method,
        payment_status=order.payment_status,
        total_amount=order.total_amount,
        subtotal=order.subtotal,
        delivery_fee=order.delivery_fee,
        discount_amount=order.discount_amount,
        coupon_code=order.coupon_code,
        items_snapshot=_json.dumps(items_list, ensure_ascii=False),
        full_order_json=_json.dumps(full_data, ensure_ascii=False),
        deleted_by=pin.name if pin else 'Ops',
        deletion_reason=reason or None,
        original_created_at=order.created_at,
    )

    from models import ReleasedOrderNumber
    released = ReleasedOrderNumber(order_number=order.order_number)
    db.session.add(archived)
    db.session.add(released)
    for item in order.items:
        db.session.delete(item)
    db.session.delete(order)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        import logging
        logging.error(f"Failed to delete order {order_id}: {e}")
        return jsonify({'ok': False, 'error': 'שגיאה במחיקת ההזמנה'})

    return jsonify({'ok': True, 'message': f'הזמנה #{order.order_number} נמחקה'})


_sse_subscribers = []
_sse_lock = threading.Lock()

def _notify_sse_new_order(order_data):
    _notify_sse_order_event(order_data)


def _notify_sse_order_event(event_data):
    event_json = json.dumps(event_data, ensure_ascii=False)
    dead = []
    with _sse_lock:
        for sub in _sse_subscribers:
            try:
                branch_filter = sub.get('branch_id')
                if branch_filter and event_data.get('branch_id') != branch_filter:
                    continue
                sub['queue'].put_nowait(event_json)
            except Exception:
                dead.append(sub)
        for d in dead:
            try:
                _sse_subscribers.remove(d)
            except ValueError:
                pass


def _notify_sse_status_change(order, old_status, new_status):
    _notify_sse_order_event({
        'type': 'order_status_changed',
        'id': order.id,
        'order_number': order.order_number,
        'order_type': order.order_type,
        'branch_id': order.branch_id,
        'old_status': old_status,
        'new_status': new_status,
        'customer_name': order.customer_name or '',
        'total_amount': order.total_amount or 0,
        'source': getattr(order, 'source', 'online') or 'online',
        'updated_at': datetime.utcnow().isoformat() + 'Z',
    })


@ops_bp.route('/api/orders/stream')
def sse_order_stream():
    if not _verify_print_api_key():
        return jsonify({'ok': False, 'error': 'unauthorized'}), 401

    branch_id = request.args.get('branch_id', type=int)
    q = queue.Queue(maxsize=50)
    sub = {'queue': q, 'branch_id': branch_id}
    with _sse_lock:
        _sse_subscribers.append(sub)

    def generate():
        try:
            yield 'data: {"type":"connected"}\n\n'
            while True:
                try:
                    data = q.get(timeout=25)
                    yield f'data: {data}\n\n'
                except queue.Empty:
                    yield ': keepalive\n\n'
        except GeneratorExit:
            pass
        finally:
            with _sse_lock:
                try:
                    _sse_subscribers.remove(sub)
                except ValueError:
                    pass

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        },
    )


@ops_bp.route('/api/devices/register', methods=['POST'])
def register_print_device():
    if not _verify_print_api_key():
        return jsonify({'ok': False, 'error': 'unauthorized'}), 401

    data = request.get_json(force=True)
    device_id = data.get('device_id', '').strip()
    branch_id = data.get('branch_id')
    device_name = data.get('device_name', '').strip()

    if not device_id or not branch_id or not device_name:
        return jsonify({'ok': False, 'error': 'missing device_id, branch_id, or device_name'}), 400

    branch = Branch.query.get(branch_id)
    if not branch:
        return jsonify({'ok': False, 'error': 'branch not found'}), 404

    device = PrintDevice.query.filter_by(device_id=device_id).first()
    now = datetime.utcnow()
    if device:
        device.branch_id = branch_id
        device.device_name = device_name
        device.last_heartbeat = now
        device.is_online = True
    else:
        device = PrintDevice(
            device_id=device_id,
            branch_id=branch_id,
            device_name=device_name,
            last_heartbeat=now,
            is_online=True,
            registered_at=now,
        )
        db.session.add(device)

    db.session.commit()
    return jsonify({'ok': True, 'device': device.to_dict()})


@ops_bp.route('/api/devices/heartbeat', methods=['POST'])
def print_device_heartbeat():
    if not _verify_print_api_key():
        return jsonify({'ok': False, 'error': 'unauthorized'}), 401

    data = request.get_json(force=True)
    device_id = data.get('device_id', '').strip()
    if not device_id:
        return jsonify({'ok': False, 'error': 'missing device_id'}), 400

    device = PrintDevice.query.filter_by(device_id=device_id).first()
    if not device:
        return jsonify({'ok': False, 'error': 'device not registered'}), 404

    device.last_heartbeat = datetime.utcnow()
    device.is_online = True
    db.session.commit()
    return jsonify({'ok': True, 'server_time': datetime.utcnow().isoformat() + 'Z'})


@ops_bp.route('/api/devices', methods=['GET'])
def list_print_devices():
    is_api_key_auth = _verify_print_api_key()
    if not is_api_key_auth:
        pin = _get_ops_user()
        if not pin:
            return jsonify({'ok': False, 'error': 'unauthorized'}), 401

    cutoff = datetime.utcnow() - timedelta(minutes=2)
    devices = PrintDevice.query.all()
    for d in devices:
        if d.last_heartbeat and d.last_heartbeat < cutoff:
            d.is_online = False
    db.session.commit()

    return jsonify({
        'ok': True,
        'devices': [d.to_dict() for d in devices],
    })


@ops_bp.route('/api/devices/<int:device_db_id>/config', methods=['GET'])
def get_print_device_config(device_db_id):
    if not _verify_print_api_key():
        return jsonify({'ok': False, 'error': 'unauthorized'}), 401

    device = PrintDevice.query.get(device_db_id)
    if not device:
        return jsonify({'ok': False, 'error': 'device not found'}), 404

    printers = Printer.query.filter_by(branch_id=device.branch_id, is_active=True).order_by(Printer.display_order).all()
    station_map = {}
    default_printer = None
    for p in printers:
        pd = p.to_dict()
        if p.is_default:
            default_printer = pd
        for st in p.stations:
            station_map[st.station_name] = pd

    branch = Branch.query.get(device.branch_id)
    custom_config = {}
    if device.config_json:
        try:
            custom_config = json.loads(device.config_json)
        except Exception:
            pass

    config = {
        'device_id': device.device_id,
        'device_db_id': device.id,
        'branch_id': device.branch_id,
        'branch_name': branch.name_he if branch else '',
        'poll_interval_seconds': custom_config.get('poll_interval_seconds', 5),
        'sse_reconnect_delay_ms': custom_config.get('sse_reconnect_delay_ms', 3000),
        'heartbeat_interval_seconds': custom_config.get('heartbeat_interval_seconds', 30),
        'sound_enabled': custom_config.get('sound_enabled', True),
        'sound_file': custom_config.get('sound_file', 'new_order.mp3'),
        'notification_enabled': custom_config.get('notification_enabled', True),
        'default_printer': default_printer,
        'station_map': station_map,
        'printers': [p.to_dict() for p in printers],
        'encoding': custom_config.get('encoding', 'iso-8859-8'),
        'codepage_num': custom_config.get('codepage_num', 32),
    }

    return jsonify({'ok': True, 'config': config})


@ops_bp.route('/api/devices/<int:device_db_id>/config', methods=['PUT'])
def update_print_device_config(device_db_id):
    is_api_key_auth = _verify_print_api_key()
    if not is_api_key_auth:
        pin = _get_ops_user()
        if not pin:
            return jsonify({'ok': False, 'error': 'unauthorized'}), 401

    device = PrintDevice.query.get(device_db_id)
    if not device:
        return jsonify({'ok': False, 'error': 'device not found'}), 404

    data = request.get_json(force=True)

    if 'device_name' in data:
        device.device_name = data['device_name']
    if 'branch_id' in data:
        branch = Branch.query.get(data['branch_id'])
        if branch:
            device.branch_id = data['branch_id']

    config_fields = [
        'poll_interval_seconds', 'sse_reconnect_delay_ms', 'heartbeat_interval_seconds',
        'sound_enabled', 'sound_file', 'notification_enabled', 'encoding', 'codepage_num',
    ]
    existing = {}
    if device.config_json:
        try:
            existing = json.loads(device.config_json)
        except Exception:
            pass

    if 'config' in data and isinstance(data['config'], dict):
        existing.update(data['config'])
    else:
        for f in config_fields:
            if f in data:
                existing[f] = data[f]

    device.config_json = json.dumps(existing, ensure_ascii=False)
    db.session.commit()
    return jsonify({'ok': True, 'device': device.to_dict()})


@ops_bp.route('/api/devices/<int:device_db_id>', methods=['DELETE'])
def delete_print_device(device_db_id):
    is_api_key_auth = _verify_print_api_key()
    if not is_api_key_auth:
        pin = _get_ops_user()
        if not pin:
            return jsonify({'ok': False, 'error': 'unauthorized'}), 401

    device = PrintDevice.query.get(device_db_id)
    if not device:
        return jsonify({'ok': False, 'error': 'device not found'}), 404

    db.session.delete(device)
    db.session.commit()
    return jsonify({'ok': True, 'message': 'device deleted'})


@ops_bp.route('/api/orders/<int:order_id>/ack', methods=['POST'])
def ack_order(order_id):
    if not _verify_print_api_key():
        return jsonify({'ok': False, 'error': 'unauthorized'}), 401

    order = FoodOrder.query.get(order_id)
    if not order:
        return jsonify({'ok': False, 'error': 'order not found'}), 404

    data = request.get_json(force=True) if request.content_length else {}
    device_id = data.get('device_id', '')

    now = datetime.utcnow()
    order.bon_acked_at = now
    order.bon_printed = True
    if device_id:
        order.bon_acked_device_id = device_id

    existing = order.admin_notes or ''
    ts = now.strftime('%Y-%m-%d %H:%M:%S')
    ack_note = f'[{ts} UTC] Received by tablet'
    if device_id:
        ack_note += f' ({device_id})'
    order.admin_notes = f"{existing}\n{ack_note}".strip()
    db.session.commit()

    return jsonify({'ok': True, 'message': f'Order {order_id} acknowledged'})


@ops_bp.route('/api/orders/<int:order_id>/print-status', methods=['POST'])
def report_print_status(order_id):
    if not _verify_print_api_key():
        return jsonify({'ok': False, 'error': 'unauthorized'}), 401

    order = FoodOrder.query.get(order_id)
    if not order:
        return jsonify({'ok': False, 'error': 'order not found'}), 404

    data = request.get_json(force=True) if request.content_length else {}
    status = data.get('status', '')
    device_id = data.get('device_id', '')
    error_message = data.get('error', '')
    stations_printed = data.get('stations_printed', [])
    stations_failed = data.get('stations_failed', [])

    now = datetime.utcnow()
    order.bon_print_attempts = (order.bon_print_attempts or 0) + 1

    existing_notes = order.admin_notes or ''
    ts = now.strftime('%Y-%m-%d %H:%M:%S')

    if status == 'success':
        order.bon_printed = True
        order.bon_printed_at = now
        order.bon_print_error = None
        note = f'[{ts} UTC] Print SUCCESS'
        if device_id:
            note += f' by {device_id}'
        if stations_printed:
            note += f' stations: {", ".join(stations_printed)}'
    elif status == 'partial':
        order.bon_printed = True
        order.bon_printed_at = now
        order.bon_print_error = error_message or f'Failed stations: {", ".join(stations_failed)}'
        note = f'[{ts} UTC] Print PARTIAL'
        if device_id:
            note += f' by {device_id}'
        if stations_printed:
            note += f' OK: {", ".join(stations_printed)}'
        if stations_failed:
            note += f' FAILED: {", ".join(stations_failed)}'
        if error_message:
            note += f' Error: {error_message}'
    elif status == 'error':
        order.bon_print_error = error_message or 'Unknown print error'
        note = f'[{ts} UTC] Print ERROR'
        if device_id:
            note += f' by {device_id}'
        if error_message:
            note += f': {error_message}'
    else:
        return jsonify({'ok': False, 'error': 'invalid status, must be: success, partial, or error'}), 400

    order.admin_notes = f"{existing_notes}\n{note}".strip()
    db.session.commit()

    return jsonify({
        'ok': True,
        'message': f'Print status recorded for order {order_id}',
        'bon_printed': order.bon_printed,
        'attempts': order.bon_print_attempts,
    })


@ops_bp.route('/api/orders/<int:order_id>/detail', methods=['GET'])
def api_order_detail(order_id):
    if not _verify_print_api_key():
        return jsonify({'ok': False, 'error': 'unauthorized'}), 401

    order = FoodOrder.query.get(order_id)
    if not order:
        return jsonify({'ok': False, 'error': 'order not found'}), 404

    items = json.loads(order.items_json) if order.items_json else []
    by_station = {}
    for item in items:
        menu_item_id = item.get('menu_item_id') or item.get('item_id') or item.get('id')
        st = 'כללי'
        if menu_item_id:
            mi = MenuItem.query.get(menu_item_id)
            if mi:
                if mi.print_station:
                    st = mi.print_station
                if order.branch_id:
                    bmi = BranchMenuItem.query.filter_by(branch_id=order.branch_id, menu_item_id=menu_item_id).first()
                    if bmi and bmi.print_station:
                        st = bmi.print_station
                if mi.print_name:
                    item['print_name'] = mi.print_name
        if st not in by_station:
            by_station[st] = []
        by_station[st].append(item)

    return jsonify({
        'ok': True,
        'order': {
            'id': order.id,
            'order_number': order.order_number,
            'order_type': order.order_type,
            'status': order.status,
            'branch_id': order.branch_id,
            'customer_name': order.customer_name or '',
            'customer_phone': order.customer_phone or '',
            'delivery_address': order.delivery_address or '',
            'delivery_city': order.delivery_city or '',
            'delivery_notes': order.delivery_notes or '',
            'customer_notes': order.customer_notes or '',
            'subtotal': order.subtotal or 0,
            'delivery_fee': order.delivery_fee or 0,
            'discount_amount': order.discount_amount or 0,
            'total_amount': order.total_amount or 0,
            'payment_method': order.payment_method or '',
            'coupon_code': order.coupon_code or '',
            'created_at': _to_il(order.created_at) if order.created_at else '',
            'items': items,
            'items_by_station': by_station,
            'bon_printed': order.bon_printed,
            'bon_printed_at': _to_il(order.bon_printed_at) if order.bon_printed_at else None,
            'bon_acked_at': _to_il(order.bon_acked_at) if order.bon_acked_at else None,
            'bon_acked_device_id': order.bon_acked_device_id or '',
            'bon_print_error': order.bon_print_error or '',
            'bon_print_attempts': order.bon_print_attempts or 0,
        }
    })


@ops_bp.route('/api/device/log-error', methods=['POST'])
def device_log_error():
    if not _verify_print_api_key():
        return jsonify({'ok': False, 'error': 'unauthorized'}), 401

    data = request.get_json(force=True) if request.content_length else {}
    device_id = data.get('device_id', 'unknown')
    error_type = data.get('error_type', 'general')
    error_message = data.get('error_message', '')
    order_id = data.get('order_id')
    extra = data.get('extra', {})

    logging.error(f"[DEVICE ERROR] device={device_id} type={error_type} order={order_id} msg={error_message} extra={json.dumps(extra, ensure_ascii=False)}")

    if order_id:
        order = FoodOrder.query.get(order_id)
        if order:
            now = datetime.utcnow()
            ts = now.strftime('%Y-%m-%d %H:%M:%S')
            existing = order.admin_notes or ''
            note = f'[{ts} UTC] Device error ({device_id}): {error_type} - {error_message}'
            order.admin_notes = f"{existing}\n{note}".strip()
            db.session.commit()

    return jsonify({'ok': True, 'message': 'error logged'})


# ─── Dine-In Table Service ─────────────────────────────────────────

@ops_bp.route('/tables')
@require_ops_module('tables')
def tables_view():
    effective_branch = _get_effective_branch_id()
    tables = DineInTable.query.filter_by(branch_id=effective_branch, is_active=True).order_by(DineInTable.display_order, DineInTable.id).all() if effective_branch else []
    active_sessions = {}
    recently_closed = []
    if effective_branch:
        sess_list = DineInSession.query.filter_by(branch_id=effective_branch).filter(DineInSession.status.in_(['open', 'awaiting_payment'])).all()
        for s in sess_list:
            s.item_count = sum(len((o.get_items() or [])) for o in s.orders if o.status != 'cancelled')
            try:
                s.has_pending_voids = bool(s.pending_void_approvals and json.loads(s.pending_void_approvals))
            except Exception:
                s.has_pending_voids = False
            active_sessions[s.table_id] = s
        cutoff = datetime.utcnow() - timedelta(hours=4)
        recently_closed = DineInSession.query.filter_by(branch_id=effective_branch).filter(
            DineInSession.status.in_(['closed', 'cancelled']),
            DineInSession.closed_at >= cutoff
        ).order_by(DineInSession.closed_at.desc()).limit(10).all()
    has_layout = any(t.pos_x is not None and t.pos_y is not None for t in tables)
    return render_template('ops/tables.html',
        active_tab='tables',
        tables=tables,
        active_sessions=active_sessions,
        recently_closed=recently_closed,
        has_layout=has_layout,
    )


@ops_bp.route('/api/tables', methods=['GET'])
@require_ops_module('tables')
def api_list_tables():
    effective_branch = _get_effective_branch_id()
    if not effective_branch:
        return jsonify({'ok': False, 'error': 'לא נבחר סניף'})
    tables = DineInTable.query.filter_by(branch_id=effective_branch, is_active=True).order_by(DineInTable.display_order, DineInTable.id).all()
    active_sessions = {}
    sess_list = DineInSession.query.filter_by(branch_id=effective_branch).filter(DineInSession.status.in_(['open', 'awaiting_payment'])).all()
    for s in sess_list:
        active_sessions[s.table_id] = s
    result = []
    for t in tables:
        s = active_sessions.get(t.id)
        has_pending_voids = False
        if s and s.pending_void_approvals:
            try:
                has_pending_voids = bool(json.loads(s.pending_void_approvals))
            except Exception:
                pass
        result.append({
            'id': t.id,
            'table_number': t.table_number,
            'capacity': t.capacity,
            'area': t.area or '',
            'status': s.status if s else 'available',
            'session_id': s.id if s else None,
            'elapsed_minutes': s.elapsed_minutes if s else 0,
            'total': s.total_amount if s else 0,
            'item_count': sum(len((o.get_items() or [])) for o in s.orders if o.status != 'cancelled') if s else 0,
            'waiter': s.waiter.name if s and s.waiter else '',
            'pos_x': t.pos_x,
            'pos_y': t.pos_y,
            'width': t.width or 100,
            'height': t.height or 80,
            'shape': t.shape or 'rect',
            'has_pending_voids': has_pending_voids,
        })
    return jsonify({'ok': True, 'tables': result})


@ops_bp.route('/api/tables/manage', methods=['POST'])
@require_ops_module('tables')
def api_manage_tables():
    effective_branch = _get_effective_branch_id()
    if not effective_branch:
        return jsonify({'ok': False, 'error': 'לא נבחר סניף'})
    data = request.get_json(force=True)
    action = data.get('action')
    if action == 'add':
        table_number = (data.get('table_number') or '').strip()
        if not table_number:
            return jsonify({'ok': False, 'error': 'נא להזין מספר שולחן'})
        existing = DineInTable.query.filter_by(branch_id=effective_branch, table_number=table_number).first()
        if existing:
            if not existing.is_active:
                existing.is_active = True
                db.session.commit()
                return jsonify({'ok': True, 'message': f'שולחן {table_number} הופעל מחדש'})
            return jsonify({'ok': False, 'error': f'שולחן {table_number} כבר קיים'})
        t = DineInTable(branch_id=effective_branch, table_number=table_number, capacity=int(data.get('capacity', 4)), area=(data.get('area') or '').strip())
        max_order = db.session.query(db.func.max(DineInTable.display_order)).filter_by(branch_id=effective_branch).scalar() or 0
        t.display_order = max_order + 1
        db.session.add(t)
        db.session.commit()
        return jsonify({'ok': True, 'message': f'שולחן {table_number} נוסף'})
    elif action == 'remove':
        table_id = data.get('table_id')
        t = DineInTable.query.get(table_id)
        if t and t.branch_id == effective_branch:
            active_sess = DineInSession.query.filter_by(table_id=t.id).filter(DineInSession.status.in_(['open', 'awaiting_payment'])).first()
            if active_sess:
                return jsonify({'ok': False, 'error': 'לא ניתן למחוק שולחן עם ישיבה פעילה'})
            t.is_active = False
            db.session.commit()
            return jsonify({'ok': True, 'message': 'שולחן הוסר'})
        return jsonify({'ok': False, 'error': 'שולחן לא נמצא'})
    return jsonify({'ok': False, 'error': 'פעולה לא ידועה'})


@ops_bp.route('/api/tables/layout', methods=['POST'])
@require_ops_module('branches')
def api_save_table_layout():
    effective_branch = _get_effective_branch_id()
    if not effective_branch:
        return jsonify({'ok': False, 'error': 'לא נבחר סניף'})
    data = request.get_json(force=True)
    positions = data.get('positions', [])
    if not isinstance(positions, list):
        return jsonify({'ok': False, 'error': 'נתונים לא תקינים'})
    def _safe_float(val, mn=0, mx=2000, default=None):
        if val is None:
            return default
        try:
            v = float(val)
            return max(mn, min(mx, v))
        except (ValueError, TypeError):
            return default

    for pos in positions:
        table_id = pos.get('id')
        if not table_id:
            continue
        try:
            table_id = int(table_id)
        except (ValueError, TypeError):
            continue
        t = DineInTable.query.get(table_id)
        if not t or t.branch_id != effective_branch:
            continue
        if pos.get('pos_x') is None and 'pos_x' in pos:
            t.pos_x = None
        else:
            px = _safe_float(pos.get('pos_x'), 0, 5000)
            if px is not None:
                t.pos_x = px
        if pos.get('pos_y') is None and 'pos_y' in pos:
            t.pos_y = None
        else:
            py = _safe_float(pos.get('pos_y'), 0, 5000)
            if py is not None:
                t.pos_y = py
        w = _safe_float(pos.get('width'), 40, 400)
        if w is not None:
            t.width = w
        h = _safe_float(pos.get('height'), 40, 400)
        if h is not None:
            t.height = h
        if pos.get('shape') in ('rect', 'round'):
            t.shape = pos['shape']
        if pos.get('area') is not None:
            t.area = str(pos['area'] or '').strip()[:50]
    try:
        db.session.commit()
        return jsonify({'ok': True, 'message': 'הפריסה נשמרה בהצלחה'})
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error saving table layout: {e}')
        return jsonify({'ok': False, 'error': 'שגיאה בשמירת הפריסה'})


@ops_bp.route('/table-layout')
@require_ops_module('branches')
def table_layout():
    effective_branch = _get_effective_branch_id()
    tables = DineInTable.query.filter_by(branch_id=effective_branch, is_active=True).order_by(DineInTable.display_order, DineInTable.id).all() if effective_branch else []
    areas = sorted(set(t.area for t in tables if t.area))
    active_sessions = {}
    if effective_branch:
        sess_list = DineInSession.query.filter_by(branch_id=effective_branch).filter(DineInSession.status.in_(['open', 'awaiting_payment'])).all()
        for s in sess_list:
            active_sessions[s.table_id] = s
    return render_template('ops/table_layout.html',
        active_tab='tables',
        tables=tables,
        areas=areas,
        active_sessions=active_sessions,
    )


@ops_bp.route('/api/tables/<int:table_id>/open-session', methods=['POST'])
@require_ops_module('tables')
def api_open_session(table_id):
    effective_branch = _get_effective_branch_id()
    table = DineInTable.query.get(table_id)
    if not table or table.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'שולחן לא נמצא'})
    existing = DineInSession.query.filter_by(table_id=table.id).filter(DineInSession.status.in_(['open', 'awaiting_payment'])).first()
    if existing:
        return jsonify({'ok': True, 'session_id': existing.id, 'message': 'ישיבה קיימת'})
    user = _get_ops_user()
    data = request.get_json(force=True) if request.content_length else {}
    sess = DineInSession(
        table_id=table.id,
        branch_id=effective_branch,
        waiter_pin_id=user.id if user else None,
        guests_count=int(data.get('guests_count', 1)),
        status='open',
    )
    db.session.add(sess)
    db.session.commit()
    return jsonify({'ok': True, 'session_id': sess.id, 'message': f'ישיבה נפתחה לשולחן {table.table_number}'})


@ops_bp.route('/api/sessions/<int:session_id>', methods=['GET'])
@require_ops_module('tables')
def api_get_session(session_id):
    effective_branch = _get_effective_branch_id()
    sess = DineInSession.query.get(session_id)
    if not sess or sess.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'ישיבה לא נמצאה'})
    items = []
    for order in sess.orders:
        if order.status == 'cancelled':
            continue
        order_items = order.get_items() or []
        for idx, item_data in enumerate(order_items):
            item_data['order_id'] = order.id
            item_data['item_index'] = idx
            item_data['sent_to_kitchen'] = order.status in ('preparing', 'ready', 'delivered', 'pickedup')
            items.append(item_data)
    return jsonify({
        'ok': True,
        'session': {
            'id': sess.id,
            'table_number': sess.table.table_number if sess.table else '?',
            'status': sess.status,
            'waiter': sess.waiter.name if sess.waiter else '',
            'guests_count': sess.guests_count,
            'discount_type': sess.discount_type,
            'discount_value': sess.discount_value,
            'notes': sess.notes or '',
            'subtotal': sess.subtotal_before_discount,
            'total': sess.total_amount,
            'elapsed_minutes': sess.elapsed_minutes,
            'payment_url': sess.payment_url or '',
            'items': items,
            'opened_at': sess.opened_at.isoformat() if sess.opened_at else '',
            'pending_void_approvals': _safe_json_list(sess.pending_void_approvals),
        },
    })


@ops_bp.route('/api/sessions/<int:session_id>/add-items', methods=['POST'])
@require_ops_module('tables')
def api_session_add_items(session_id):
    from standalone_order_service.order_helpers import verify_cart_items
    import secrets as _secrets
    effective_branch = _get_effective_branch_id()
    sess = DineInSession.query.get(session_id)
    if not sess or sess.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'ישיבה לא נמצאה'})
    if sess.status != 'open':
        return jsonify({'ok': False, 'error': 'הישיבה לא פעילה'})
    data = request.get_json(force=True)
    cart = data.get('items', [])
    if not cart:
        return jsonify({'ok': False, 'error': 'לא נבחרו פריטים'})
    valid_cart, verified_subtotal = verify_cart_items(cart, effective_branch)
    if not valid_cart:
        return jsonify({'ok': False, 'error': 'פריטים לא תקינים'})
    branch = Branch.query.get(effective_branch)
    user = _get_ops_user()
    order = FoodOrder()
    order.set_order_number()
    order.tracking_token = _secrets.token_urlsafe(24)
    order.branch_id = effective_branch
    order.branch_name = branch.name_he if branch else ''
    order.order_type = 'dine_in'
    order.customer_name = f'שולחן {sess.table.table_number}' if sess.table else 'ישיבה'
    order.customer_phone = '0000000000'
    order.payment_method = 'cash'
    order.subtotal = verified_subtotal
    order.delivery_fee = 0
    order.total_amount = verified_subtotal
    order.status = 'pending'
    order.payment_status = 'pending'
    order.source = 'dine_in'
    order.table_number = sess.table.table_number if sess.table else ''
    order.dine_in_session_id = sess.id
    order.created_by_name = user.name if user else None
    order.items_json = json.dumps(valid_cart, ensure_ascii=False)
    db.session.add(order)
    db.session.flush()
    for item in valid_cart:
        oi = FoodOrderItem()
        oi.order_id = order.id
        if item.get('is_deal'):
            oi.menu_item_id = None
            oi.item_name_he = item.get('name_he', '')
            oi.item_name_en = item.get('name_en', '')
            oi.quantity = int(item.get('qty', 1))
            oi.unit_price = float(item.get('price', 0))
            oi.total_price = oi.quantity * oi.unit_price
            oi.special_instructions = item.get('notes', '')
            deal_data = {'is_deal': True, 'deal_id': item.get('deal_id')}
            if item.get('deal_type') == 'customer_picks':
                deal_data['deal_type'] = 'customer_picks'
                deal_data['selected_items'] = item.get('selected_items', [])
            else:
                deal_data['included_items'] = item.get('included_items', [])
            oi.options_json = json.dumps(deal_data, ensure_ascii=False)
        else:
            oi.menu_item_id = item.get('id')
            oi.item_name_he = item.get('name_he', '')
            oi.item_name_en = item.get('name_en', '')
            oi.quantity = int(item.get('qty', 1))
            oi.unit_price = float(item.get('price', 0))
            oi.total_price = oi.quantity * oi.unit_price
            oi.special_instructions = item.get('notes', '')
            if item.get('options'):
                oi.options_json = json.dumps(item['options'], ensure_ascii=False)
        db.session.add(oi)
    db.session.commit()
    return jsonify({
        'ok': True,
        'message': f'{len(valid_cart)} פריטים נוספו',
        'order_id': order.id,
        'order_number': order.order_number,
    })


@ops_bp.route('/api/sessions/<int:session_id>/send-to-kitchen', methods=['POST'])
@require_ops_module('tables')
def api_session_send_to_kitchen(session_id):
    effective_branch = _get_effective_branch_id()
    sess = DineInSession.query.get(session_id)
    if not sess or sess.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'ישיבה לא נמצאה'})
    sent_count = 0
    for order in sess.orders:
        if order.status in ('pending', 'confirmed') and order.status != 'cancelled':
            order.status = 'preparing'
            order.preparing_at = datetime.utcnow()
            sent_count += 1
            try:
                _queue_print_for_app(order)
            except Exception as e:
                logging.warning(f"Print failed for dine-in order {order.id}: {e}")
    db.session.commit()
    if sent_count == 0:
        return jsonify({'ok': True, 'message': 'אין פריטים חדשים לשלוח'})
    return jsonify({'ok': True, 'message': f'{sent_count} הזמנות נשלחו למטבח'})


@ops_bp.route('/api/sessions/<int:session_id>/remove-item', methods=['POST'])
@require_ops_module('tables')
def api_session_remove_item(session_id):
    effective_branch = _get_effective_branch_id()
    sess = DineInSession.query.get(session_id)
    if not sess or sess.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'ישיבה לא נמצאה'})
    data = request.get_json(force=True)
    order_id = data.get('order_id')
    item_index = data.get('item_index')
    order = FoodOrder.query.get(order_id)
    if not order or order.dine_in_session_id != sess.id:
        return jsonify({'ok': False, 'error': 'הזמנה לא נמצאה'})
    manager_name = None
    is_sent = order.status in ('preparing', 'ready', 'delivered', 'pickedup')
    pin_val = data.get('manager_pin')
    if pin_val:
        for pm in ManagerPIN.query.filter_by(is_ops_superadmin=True).all():
            if pm.check_pin(str(pin_val)):
                manager_name = pm.name
                break
        if not manager_name:
            return jsonify({'ok': False, 'error': 'PIN שגוי'})
    items = order.get_items()
    if item_index is not None and 0 <= item_index < len(items):
        removed = items.pop(item_index)
        removed_price = float(removed.get('price', 0)) * int(removed.get('qty', 1))
        order.items_json = json.dumps(items, ensure_ascii=False)
        order.subtotal = max(0, (order.subtotal or 0) - removed_price)
        order.total_amount = max(0, (order.total_amount or 0) - removed_price)
        order_items = FoodOrderItem.query.filter_by(order_id=order.id).order_by(FoodOrderItem.id).all()
        if item_index < len(order_items):
            db.session.delete(order_items[item_index])
        if not items:
            order.status = 'cancelled'
            order.cancelled_at = datetime.utcnow()
        void_reason = data.get('void_reason', '').strip()
        if is_sent:
            if not void_reason:
                void_reason = 'לא צוין'
            existing_log = []
            if order.void_log:
                try:
                    existing_log = json.loads(order.void_log)
                except Exception:
                    existing_log = []
            existing_log.append({
                'item_name': removed.get('name_he', ''),
                'item_price': removed.get('price', 0),
                'item_qty': removed.get('qty', 1),
                'void_reason': void_reason,
                'manager': manager_name or '',
                'voided_at': datetime.utcnow().isoformat(),
                'voided_by': session.get('ops_user_name', ''),
            })
            order.void_log = json.dumps(existing_log, ensure_ascii=False)
            if not manager_name:
                pending = []
                if sess.pending_void_approvals:
                    try:
                        pending = json.loads(sess.pending_void_approvals)
                    except Exception:
                        pending = []
                pending.append({
                    'item_name': removed.get('name_he', ''),
                    'item_price': removed.get('price', 0),
                    'item_qty': removed.get('qty', 1),
                    'void_reason': void_reason,
                    'voided_at': datetime.utcnow().isoformat(),
                    'voided_by': session.get('ops_user_name', ''),
                    'order_id': order.id,
                })
                sess.pending_void_approvals = json.dumps(pending, ensure_ascii=False)
        db.session.commit()
        try:
            needs_approval = bool(sess.pending_void_approvals and json.loads(sess.pending_void_approvals))
        except Exception:
            needs_approval = False
        return jsonify({'ok': True, 'message': 'פריט הוסר', 'needs_manager_approval': needs_approval})
    return jsonify({'ok': False, 'error': 'פריט לא נמצא'})


@ops_bp.route('/api/sessions/<int:session_id>/update-item', methods=['POST'])
@require_ops_module('tables')
def api_session_update_item(session_id):
    effective_branch = _get_effective_branch_id()
    sess = DineInSession.query.get(session_id)
    if not sess or sess.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'ישיבה לא נמצאה'})
    data = request.get_json(force=True)
    try:
        order_id = int(data.get('order_id', 0))
        item_index = int(data.get('item_index', -1))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'נתונים לא תקינים'})
    order = FoodOrder.query.get(order_id)
    if not order or order.dine_in_session_id != sess.id:
        return jsonify({'ok': False, 'error': 'הזמנה לא נמצאה'})
    if order.status in ('preparing', 'ready', 'delivered', 'pickedup'):
        pin_val = data.get('manager_pin')
        if pin_val:
            pin_valid = False
            for pm in ManagerPIN.query.filter_by(is_ops_superadmin=True).all():
                if pm.check_pin(str(pin_val)):
                    pin_valid = True
                    break
            if not pin_valid:
                return jsonify({'ok': False, 'error': 'PIN מנהל לא תקין'})
        else:
            return jsonify({'ok': False, 'error': 'פריט נשלח למטבח — נדרש PIN מנהל', 'require_pin': True})
    items = order.get_items()
    if item_index < 0 or item_index >= len(items):
        return jsonify({'ok': False, 'error': 'פריט לא נמצא'})
    item = items[item_index]
    old_price = float(item.get('price', 0)) * int(item.get('qty', 1))
    new_qty = data.get('qty')
    new_notes = data.get('notes')
    new_options = data.get('options')
    if new_qty is not None:
        try:
            new_qty = max(1, int(new_qty))
        except (TypeError, ValueError):
            return jsonify({'ok': False, 'error': 'כמות לא תקינה'})
        item['qty'] = new_qty
        item['quantity'] = new_qty
    if new_notes is not None:
        item['notes'] = new_notes
        item['special_instructions'] = new_notes
    if new_options is not None and not item.get('is_deal'):
        from models import MenuItemOptionChoice
        validated_options = []
        extra_price = 0
        for opt in new_options:
            choice_id = opt.get('choice_id')
            if not choice_id:
                continue
            choice = MenuItemOptionChoice.query.get(int(choice_id))
            if not choice:
                continue
            server_price = float(choice.price_modifier or 0)
            extra_price += server_price
            validated_options.append({
                'group_id': opt.get('group_id', ''),
                'choice_id': choice.id,
                'name_he': choice.name_he,
                'price': server_price
            })
        menu_item_id = item.get('id')
        if menu_item_id:
            mi = MenuItem.query.get(menu_item_id)
            if mi:
                bmi = BranchMenuItem.query.filter_by(branch_id=effective_branch, menu_item_id=mi.id).first()
                base_price = bmi.custom_price if bmi and bmi.custom_price is not None else mi.base_price
                item['price'] = base_price + extra_price
        item['options'] = validated_options
    new_price = float(item.get('price', 0)) * int(item.get('qty', 1))
    price_diff = new_price - old_price
    items[item_index] = item
    order.items_json = json.dumps(items, ensure_ascii=False)
    order.subtotal = max(0, (order.subtotal or 0) + price_diff)
    order.total_amount = max(0, (order.total_amount or 0) + price_diff)
    order_items_db = FoodOrderItem.query.filter_by(order_id=order.id).order_by(FoodOrderItem.id).all()
    if item_index < len(order_items_db):
        oi = order_items_db[item_index]
        if new_qty is not None:
            oi.quantity = new_qty
        if new_notes is not None:
            oi.special_instructions = new_notes
        if new_options is not None:
            oi.options_json = json.dumps(item.get('options', []), ensure_ascii=False)
        oi.unit_price = float(item.get('price', 0))
        oi.total_price = float(item.get('price', 0)) * int(item.get('qty', 1))
    db.session.commit()
    return jsonify({'ok': True, 'message': 'פריט עודכן'})


@ops_bp.route('/api/sessions/<int:session_id>/reprint-kitchen', methods=['POST'])
@require_ops_module('tables')
def api_session_reprint_kitchen(session_id):
    effective_branch = _get_effective_branch_id()
    sess = DineInSession.query.get(session_id)
    if not sess or sess.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'ישיבה לא נמצאה'})
    printed = 0
    for order in sess.orders:
        if order.status in ('preparing', 'ready') and order.status != 'cancelled':
            try:
                _queue_print_for_app(order)
                printed += 1
            except Exception as e:
                logging.warning(f"Reprint failed for order {order.id}: {e}")
    if printed == 0:
        return jsonify({'ok': True, 'message': 'אין הזמנות פעילות להדפסה'})
    return jsonify({'ok': True, 'message': f'{printed} הזמנות נשלחו להדפסה מחדש'})


@ops_bp.route('/api/sessions/<int:session_id>/discount', methods=['POST'])
@require_ops_module('tables')
def api_session_discount(session_id):
    effective_branch = _get_effective_branch_id()
    sess = DineInSession.query.get(session_id)
    if not sess or sess.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'ישיבה לא נמצאה'})
    data = request.get_json(force=True)
    discount_type = data.get('discount_type')
    discount_value = float(data.get('discount_value', 0))
    if discount_type not in ('percentage', 'fixed', None, ''):
        return jsonify({'ok': False, 'error': 'סוג הנחה לא תקין'})
    if not discount_type or discount_value <= 0:
        sess.discount_type = None
        sess.discount_value = 0
    else:
        sess.discount_type = discount_type
        sess.discount_value = discount_value
    db.session.commit()
    return jsonify({'ok': True, 'message': 'הנחה עודכנה', 'total': sess.total_amount})


@ops_bp.route('/api/sessions/<int:session_id>/notes', methods=['POST'])
@require_ops_module('tables')
def api_session_notes(session_id):
    effective_branch = _get_effective_branch_id()
    sess = DineInSession.query.get(session_id)
    if not sess or sess.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'ישיבה לא נמצאה'})
    data = request.get_json(force=True)
    sess.notes = (data.get('notes') or '').strip()[:500]
    db.session.commit()
    return jsonify({'ok': True, 'message': 'הערות עודכנו'})


@ops_bp.route('/api/sessions/<int:session_id>/approve-voids', methods=['POST'])
@require_ops_module('tables')
def api_session_approve_voids(session_id):
    effective_branch = _get_effective_branch_id()
    sess = DineInSession.query.get(session_id)
    if not sess or sess.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'ישיבה לא נמצאה'})
    data = request.get_json(force=True)
    pin_val = data.get('manager_pin')
    if not pin_val:
        return jsonify({'ok': False, 'error': 'נדרש PIN מנהל'})
    manager_name = None
    for pm in ManagerPIN.query.filter_by(is_ops_superadmin=True).all():
        if pm.check_pin(str(pin_val)):
            manager_name = pm.name
            break
    if not manager_name:
        return jsonify({'ok': False, 'error': 'PIN מנהל לא תקין'})
    sess.pending_void_approvals = None
    db.session.commit()
    return jsonify({'ok': True, 'message': f'ביטולים אושרו ע"י {manager_name}'})


@ops_bp.route('/api/sessions/<int:session_id>/pay-cash', methods=['POST'])
@require_ops_module('tables')
def api_session_pay_cash(session_id):
    effective_branch = _get_effective_branch_id()
    sess = DineInSession.query.get(session_id)
    if not sess or sess.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'ישיבה לא נמצאה'})
    active_splits = DineInPaymentSplit.query.filter_by(session_id=sess.id).filter(DineInPaymentSplit.payment_status != 'paid').count()
    if active_splits > 0:
        return jsonify({'ok': False, 'error': 'יש חלוקת תשלום פעילה — יש לשלם דרך החלקים'})
    if sess.pending_void_approvals:
        try:
            pending = json.loads(sess.pending_void_approvals)
            if pending:
                return jsonify({'ok': False, 'error': 'יש ביטולים הממתינים לאישור מנהל', 'pending_voids': True})
        except Exception:
            pass
    data = request.get_json(force=True) if request.is_json else {}
    try:
        tip = max(0, float(data.get('tip_amount', 0) or 0))
    except (ValueError, TypeError):
        tip = 0
    try:
        cash_received = data.get('cash_received')
        if cash_received is not None:
            cash_received = max(0, float(cash_received))
    except (ValueError, TypeError):
        cash_received = None
    total_due = sess.total_amount + tip
    if cash_received is None:
        return jsonify({'ok': False, 'error': 'נא להזין סכום שהתקבל'})
    if cash_received < total_due:
        return jsonify({'ok': False, 'error': f'סכום שהתקבל (₪{cash_received:.2f}) נמוך מהסה"כ (₪{total_due:.2f})'})
    sess.tip_amount = tip
    sess.cash_received = cash_received
    for order in sess.orders:
        if order.status != 'cancelled':
            order.payment_status = 'cash'
            order.payment_method = 'cash'
            if order.status in ('pending', 'confirmed'):
                order.status = 'preparing'
            if order.status not in ('delivered', 'pickedup', 'cancelled'):
                order.status = 'pickedup'
                order.completed_at = datetime.utcnow()
    sess.status = 'closed'
    sess.closed_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'ok': True, 'message': 'תשלום במזומן — שולחן נסגר'})


@ops_bp.route('/api/sessions/<int:session_id>/generate-payment-link', methods=['POST'])
@require_ops_module('tables')
def api_session_generate_payment(session_id):
    effective_branch = _get_effective_branch_id()
    sess = DineInSession.query.get(session_id)
    if not sess or sess.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'ישיבה לא נמצאה'})
    active_splits = DineInPaymentSplit.query.filter_by(session_id=sess.id).filter(DineInPaymentSplit.payment_status != 'paid').count()
    if active_splits > 0:
        return jsonify({'ok': False, 'error': 'יש חלוקת תשלום פעילה — יש לשלם דרך החלקים'})
    if sess.pending_void_approvals:
        try:
            pending = json.loads(sess.pending_void_approvals)
            if pending:
                return jsonify({'ok': False, 'error': 'יש ביטולים הממתינים לאישור מנהל', 'pending_voids': True})
        except Exception:
            pass
    data = request.get_json(force=True) if request.is_json else {}
    try:
        tip = max(0, float(data.get('tip_amount', 0) or 0))
    except (ValueError, TypeError):
        tip = 0
    sess.tip_amount = tip
    total = sess.total_amount
    if total <= 0:
        return jsonify({'ok': False, 'error': 'סכום לתשלום 0'})
    charge_amount = total + tip
    first_order = None
    for o in sess.orders:
        if o.status != 'cancelled':
            first_order = o
            break
    if not first_order:
        return jsonify({'ok': False, 'error': 'אין הזמנות בישיבה'})
    try:
        from standalone_order_service.hyp_payment import HYPPayment
        branch = Branch.query.get(effective_branch)
        settings = _settings()
        hyp = HYPPayment(settings=settings)
        if branch:
            hyp._load_credentials(branch=branch)
        if not hyp.is_configured:
            return jsonify({'ok': False, 'error': 'הגדרות HYP חסרות'})
        table_num = sess.table.table_number if sess.table else '?'
        order_ref = first_order.order_number
        import secrets as _secrets
        cb_token = _secrets.token_urlsafe(32)
        sess.payment_callback_token = cb_token
        scheme = 'https' if _is_secure() else 'http'
        base_url = f"{scheme}://{request.host}"
        success_url = f"{base_url}/ops/api/sessions/{sess.id}/payment-callback?status=success&token={cb_token}"
        fail_url = f"{base_url}/ops/api/sessions/{sess.id}/payment-callback?status=fail&token={cb_token}"
        payment_url = hyp.create_payment_url(
            amount=charge_amount,
            order_id=order_ref,
            description=f'שולחן {table_num}',
            success_url=success_url,
            failure_url=fail_url,
            customer_name=f'שולחן {table_num}',
        )
        sess.payment_url = payment_url
        sess.status = 'awaiting_payment'
        db.session.commit()
        return jsonify({'ok': True, 'payment_url': payment_url, 'message': 'קישור תשלום נוצר'})
    except Exception as e:
        logging.error(f"HYP payment link error for session {session_id}: {e}")
        return jsonify({'ok': False, 'error': f'שגיאה ביצירת קישור: {str(e)}'})


@ops_bp.route('/api/sessions/<int:session_id>/send-payment-sms', methods=['POST'])
@require_ops_module('tables')
def api_session_send_payment_sms(session_id):
    effective_branch = _get_effective_branch_id()
    sess = DineInSession.query.get(session_id)
    if not sess or sess.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'ישיבה לא נמצאה'})
    if not sess.payment_url:
        return jsonify({'ok': False, 'error': 'יש ליצור קישור תשלום קודם'})
    data = request.get_json(force=True)
    phone = (data.get('phone') or '').strip()
    if not phone or len(phone) < 9:
        return jsonify({'ok': False, 'error': 'נא להזין מספר טלפון'})
    try:
        from standalone_order_service.sms_helpers import create_sender_from_env
        send_sms = create_sender_from_env()
        if not send_sms:
            return jsonify({'ok': False, 'error': 'שליחת SMS לא מוגדרת'})
        table_num = sess.table.table_number if sess.table else '?'
        total = sess.total_amount
        tip = sess.tip_amount or 0
        charge = total + tip
        tip_text = f'\nכולל טיפ: ₪{tip:.2f}' if tip > 0 else ''
        msg = f'SUMO - שולחן {table_num}\nסה"כ לתשלום: ₪{charge:.2f}{tip_text}\nלתשלום: {sess.payment_url}'
        success = send_sms(phone, msg)
        if not success:
            return jsonify({'ok': False, 'error': 'שליחת SMS נכשלה'})
        return jsonify({'ok': True, 'message': 'SMS נשלח בהצלחה'})
    except Exception as e:
        logging.error(f"SMS send error for session {session_id}: {e}")
        return jsonify({'ok': False, 'error': f'שגיאה בשליחת SMS: {str(e)}'})


@ops_bp.route('/api/sessions/<int:session_id>/payment-callback')
def session_payment_callback(session_id):
    sess = DineInSession.query.get(session_id)
    if not sess:
        return 'Session not found', 404
    cb_token = request.args.get('token', '')
    if not cb_token or not sess.payment_callback_token or cb_token != sess.payment_callback_token:
        return 'Invalid callback token', 403
    status = request.args.get('status', '')
    if status == 'success':
        if sess.pending_void_approvals:
            try:
                pending = json.loads(sess.pending_void_approvals)
            except Exception:
                pending = []
            if pending:
                logging.warning(f'Dine-in session {sess.id}: payment callback blocked — {len(pending)} pending void approvals')
                return render_template('ops/payment_fail.html', session=sess,
                    error_message='לא ניתן לסגור — יש ביטולים הממתינים לאישור מנהל')
        hyp_verified = False
        try:
            from standalone_order_service.hyp_payment import HYPPayment
            hyp = HYPPayment()
            if sess.branch_id:
                hyp._load_credentials(branch=Branch.query.get(sess.branch_id))
            response_params = dict(request.args)
            expected_amt = float(sess.total_amount + (sess.tip_amount or 0))
            verification = hyp.verify_payment_response(
                response_params,
                expected_amount=expected_amt,
                verify_signature=True
            )
            if verification.get('verified'):
                hyp_verified = True
                logging.info(f'Dine-in session {sess.id}: HYP payment verified (tx={verification.get("transaction_id")})')
            else:
                logging.warning(f'Dine-in session {sess.id}: HYP verification failed: {verification.get("error_message")}')
        except Exception as e:
            logging.error(f'Dine-in session {sess.id}: HYP verification error: {e}')
            hyp_verified = False
        if not hyp_verified:
            return render_template('ops/payment_fail.html', session=sess)
        for order in sess.orders:
            if order.status != 'cancelled':
                order.payment_status = 'paid'
                order.payment_method = 'card'
                order.payment_provider = 'hyp'
                if order.status not in ('delivered', 'pickedup', 'cancelled'):
                    order.status = 'pickedup'
                    order.completed_at = datetime.utcnow()
        sess.status = 'closed'
        sess.closed_at = datetime.utcnow()
        sess.payment_callback_token = None
        db.session.commit()
        return render_template('ops/payment_success.html', session=sess)
    else:
        return render_template('ops/payment_fail.html', session=sess)


@ops_bp.route('/api/sessions/<int:session_id>/cancel', methods=['POST'])
@require_ops_module('tables')
def api_session_cancel(session_id):
    effective_branch = _get_effective_branch_id()
    sess = DineInSession.query.get(session_id)
    if not sess or sess.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'ישיבה לא נמצאה'})
    if sess.pending_void_approvals:
        try:
            pending = json.loads(sess.pending_void_approvals)
            if pending:
                return jsonify({'ok': False, 'error': 'יש ביטולים הממתינים לאישור מנהל', 'pending_voids': True})
        except Exception:
            pass
    paid_splits = DineInPaymentSplit.query.filter_by(session_id=sess.id, payment_status='paid').first()
    if paid_splits:
        return jsonify({'ok': False, 'error': 'לא ניתן לבטל — יש חלקי תשלום ששולמו כבר'})
    data = request.get_json(force=True) if request.is_json else {}
    cancel_reason = (data.get('cancel_reason') or '').strip()
    cancel_note = (data.get('cancel_note') or '').strip()
    if not cancel_reason:
        return jsonify({'ok': False, 'error': 'נא לבחור סיבת ביטול'})
    manager_pin = data.get('manager_pin')
    has_kitchen_items = False
    for order in sess.orders:
        if order.status not in ('cancelled', 'pending'):
            has_kitchen_items = True
            break
    if has_kitchen_items:
        if not manager_pin:
            return jsonify({'ok': False, 'error': 'נדרש PIN מנהל — פריטים כבר נשלחו למטבח', 'require_pin': True})
        manager_name = None
        for pm in ManagerPIN.query.filter_by(is_ops_superadmin=True).all():
            if pm.check_pin(str(manager_pin)):
                manager_name = pm.name
                break
        if not manager_name:
            return jsonify({'ok': False, 'error': 'PIN מנהל לא תקין'})
    sess.cancel_reason = cancel_reason
    sess.cancel_note = cancel_note
    for order in sess.orders:
        if order.status != 'cancelled':
            order.status = 'cancelled'
            order.cancelled_at = datetime.utcnow()
    sess.status = 'cancelled'
    sess.closed_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'ok': True, 'message': 'ישיבה בוטלה'})


@ops_bp.route('/api/sessions/<int:session_id>/split-setup', methods=['POST'])
@require_ops_module('tables')
def api_session_split_setup(session_id):
    effective_branch = _get_effective_branch_id()
    sess = DineInSession.query.get(session_id)
    if not sess or sess.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'ישיבה לא נמצאה'})
    if sess.pending_void_approvals:
        try:
            pending = json.loads(sess.pending_void_approvals)
            if pending:
                return jsonify({'ok': False, 'error': 'יש ביטולים הממתינים לאישור מנהל', 'pending_voids': True})
        except Exception:
            pass
    existing_splits = DineInPaymentSplit.query.filter_by(session_id=sess.id).all()
    has_paid = any(s.payment_status == 'paid' for s in existing_splits)
    if has_paid:
        return jsonify({'ok': False, 'error': 'לא ניתן לחלק מחדש — יש חלקים ששולמו כבר'})
    has_pending_link = any(s.payment_callback_token and s.payment_status != 'paid' for s in existing_splits)
    if has_pending_link:
        return jsonify({'ok': False, 'error': 'לא ניתן לחלק מחדש — יש קישור תשלום פעיל שטרם שולם'})
    data = request.get_json(force=True)
    split_mode = data.get('mode', 'equal')
    portions = data.get('portions', [])
    total = sess.total_amount
    if total <= 0:
        return jsonify({'ok': False, 'error': 'סכום לתשלום 0'})
    if split_mode == 'equal':
        try:
            num_payers = int(data.get('num_payers', 2))
        except (ValueError, TypeError):
            return jsonify({'ok': False, 'error': 'מספר משלמים לא תקין'})
        if num_payers < 2:
            return jsonify({'ok': False, 'error': 'מספר משלמים חייב להיות לפחות 2'})
    elif split_mode == 'custom':
        if not portions:
            return jsonify({'ok': False, 'error': 'נדרשים סכומים לחלוקה'})
        for p in portions:
            try:
                amt = float(p.get('amount', 0))
            except (ValueError, TypeError):
                return jsonify({'ok': False, 'error': 'סכום לא תקין'})
            if amt < 0 or amt != amt:
                return jsonify({'ok': False, 'error': 'סכום חייב להיות חיובי'})
        portions_total = sum(float(p.get('amount', 0)) for p in portions)
        if abs(portions_total - total) > 0.01:
            return jsonify({'ok': False, 'error': f'סכום החלוקה ({portions_total:.2f}) לא תואם את הסה"כ ({total:.2f})'})
    elif split_mode == 'by_items':
        if not portions:
            return jsonify({'ok': False, 'error': 'נדרשות קבוצות פריטים'})
        for p in portions:
            try:
                amt = float(p.get('amount', 0))
            except (ValueError, TypeError):
                return jsonify({'ok': False, 'error': 'סכום לא תקין'})
            if amt < 0 or amt != amt:
                return jsonify({'ok': False, 'error': 'סכום חייב להיות חיובי'})
        portions_total = sum(float(p.get('amount', 0)) for p in portions)
        if abs(portions_total - total) > 0.01:
            return jsonify({'ok': False, 'error': f'סכום החלוקה ({portions_total:.2f}) לא תואם את הסה"כ ({total:.2f})'})
    else:
        return jsonify({'ok': False, 'error': 'מצב חלוקה לא תקין'})
    DineInPaymentSplit.query.filter_by(session_id=sess.id).delete()
    if split_mode == 'equal':
        total_cents = int(round(total * 100))
        base_cents = total_cents // num_payers
        extra = total_cents % num_payers
        for i in range(num_payers):
            amt_cents = base_cents + (1 if i < extra else 0)
            split = DineInPaymentSplit(
                session_id=sess.id, portion_index=i,
                amount=round(amt_cents / 100, 2), payer_label=f'משלם {i+1}'
            )
            db.session.add(split)
    elif split_mode == 'custom':
        for i, p in enumerate(portions):
            split = DineInPaymentSplit(
                session_id=sess.id, portion_index=i,
                amount=round(float(p.get('amount', 0)), 2),
                payer_label=p.get('label', f'משלם {i+1}')
            )
            db.session.add(split)
    elif split_mode == 'by_items':
        for i, p in enumerate(portions):
            amt = max(0, round(float(p.get('amount', 0)), 2))
            split = DineInPaymentSplit(
                session_id=sess.id, portion_index=i,
                amount=amt,
                payer_label=p.get('label', f'משלם {i+1}')
            )
            db.session.add(split)
    else:
        return jsonify({'ok': False, 'error': 'מצב חלוקה לא תקין'})
    split_meta = {'mode': split_mode, 'num_portions': len(portions) if portions else int(data.get('num_payers', 2))}
    if split_mode == 'by_items' and portions:
        split_meta['item_assignments'] = [
            {'label': p.get('label', ''), 'amount': round(float(p.get('amount', 0)), 2), 'item_indices': p.get('item_indices', [])}
            for p in portions
        ]
    elif split_mode == 'custom' and portions:
        split_meta['portions'] = [
            {'label': p.get('label', ''), 'amount': round(float(p.get('amount', 0)), 2)}
            for p in portions
        ]
    sess.split_config = json.dumps(split_meta, ensure_ascii=False)
    db.session.commit()
    splits = DineInPaymentSplit.query.filter_by(session_id=sess.id).order_by(DineInPaymentSplit.portion_index).all()
    return jsonify({
        'ok': True,
        'splits': [{'id': s.id, 'index': s.portion_index, 'amount': s.amount,
                     'label': s.payer_label, 'status': s.payment_status, 'method': s.payment_method} for s in splits]
    })


@ops_bp.route('/api/sessions/<int:session_id>/split/<int:split_id>/pay', methods=['POST'])
@require_ops_module('tables')
def api_session_split_pay(session_id, split_id):
    effective_branch = _get_effective_branch_id()
    sess = DineInSession.query.get(session_id)
    if not sess or sess.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'ישיבה לא נמצאה'})
    if sess.pending_void_approvals:
        try:
            pending = json.loads(sess.pending_void_approvals)
            if pending:
                return jsonify({'ok': False, 'error': 'יש ביטולים הממתינים לאישור מנהל', 'pending_voids': True})
        except Exception:
            pass
    split = DineInPaymentSplit.query.get(split_id)
    if not split or split.session_id != sess.id:
        return jsonify({'ok': False, 'error': 'חלוקה לא נמצאה'})
    if split.payment_status == 'paid':
        return jsonify({'ok': False, 'error': 'חלק זה כבר שולם'})
    data = request.get_json(force=True) if request.is_json else {}
    method = data.get('payment_method', 'cash')
    if method != 'cash':
        return jsonify({'ok': False, 'error': 'תשלום ידני זמין במזומן בלבד — לתשלום בקישור השתמש ביצירת קישור'})
    try:
        tip = max(0, float(data.get('tip_amount', 0) or 0))
    except (ValueError, TypeError):
        tip = 0
    try:
        cash_received = data.get('cash_received')
        if cash_received is not None:
            cash_received = max(0, float(cash_received))
    except (ValueError, TypeError):
        cash_received = None
    split_due = split.amount + tip
    if cash_received is None:
        return jsonify({'ok': False, 'error': 'נא להזין סכום שהתקבל'})
    if cash_received < split_due:
        return jsonify({'ok': False, 'error': f'סכום שהתקבל (₪{cash_received:.2f}) נמוך מהסה"כ (₪{split_due:.2f})'})
    split.payment_method = method
    split.payment_status = 'paid'
    split.tip_amount = tip
    split.cash_received = cash_received
    split.paid_at = datetime.utcnow()
    split.payment_callback_token = None
    all_splits = DineInPaymentSplit.query.filter_by(session_id=sess.id).all()
    all_paid = all(s.payment_status == 'paid' for s in all_splits)
    if all_paid:
        total_tip = sum(s.tip_amount or 0 for s in all_splits)
        sess.tip_amount = total_tip
        for order in sess.orders:
            if order.status != 'cancelled':
                order.payment_status = 'paid'
                order.payment_method = 'split'
                if order.status not in ('delivered', 'pickedup', 'cancelled'):
                    order.status = 'pickedup'
                    order.completed_at = datetime.utcnow()
        sess.status = 'closed'
        sess.closed_at = datetime.utcnow()
    db.session.commit()
    return jsonify({
        'ok': True,
        'all_paid': all_paid,
        'message': 'שולחן נסגר — כל החלקים שולמו' if all_paid else f'חלק {split.portion_index + 1} שולם',
        'splits': [{'id': s.id, 'index': s.portion_index, 'amount': s.amount,
                     'label': s.payer_label, 'status': s.payment_status, 'method': s.payment_method} for s in all_splits]
    })


@ops_bp.route('/api/sessions/<int:session_id>/split/<int:split_id>/generate-link', methods=['POST'])
@require_ops_module('tables')
def api_session_split_generate_link(session_id, split_id):
    effective_branch = _get_effective_branch_id()
    sess = DineInSession.query.get(session_id)
    if not sess or sess.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'ישיבה לא נמצאה'})
    if sess.pending_void_approvals:
        try:
            pending = json.loads(sess.pending_void_approvals)
            if pending:
                return jsonify({'ok': False, 'error': 'יש ביטולים הממתינים לאישור מנהל', 'pending_voids': True})
        except Exception:
            pass
    split = DineInPaymentSplit.query.get(split_id)
    if not split or split.session_id != sess.id:
        return jsonify({'ok': False, 'error': 'חלוקה לא נמצאה'})
    if split.payment_status == 'paid':
        return jsonify({'ok': False, 'error': 'חלק זה כבר שולם'})
    data = request.get_json(force=True) if request.is_json else {}
    try:
        tip = max(0, float(data.get('tip_amount', 0) or 0))
    except (ValueError, TypeError):
        tip = 0
    split.tip_amount = tip
    amount = split.amount
    if amount <= 0:
        return jsonify({'ok': False, 'error': 'סכום לתשלום 0'})
    charge_amount = amount + tip
    first_order = None
    for o in sess.orders:
        if o.status != 'cancelled':
            first_order = o
            break
    if not first_order:
        return jsonify({'ok': False, 'error': 'אין הזמנות בישיבה'})
    try:
        from standalone_order_service.hyp_payment import HYPPayment
        branch = Branch.query.get(effective_branch)
        settings = _settings()
        hyp = HYPPayment(settings=settings)
        if branch:
            hyp._load_credentials(branch=branch)
        if not hyp.is_configured:
            return jsonify({'ok': False, 'error': 'הגדרות HYP חסרות'})
        table_num = sess.table.table_number if sess.table else '?'
        order_ref = first_order.order_number
        import secrets as _secrets
        cb_token = _secrets.token_urlsafe(32)
        scheme = 'https' if _is_secure() else 'http'
        base_url = f"{scheme}://{request.host}"
        success_url = f"{base_url}/ops/api/sessions/{sess.id}/split/{split.id}/payment-callback?status=success&token={cb_token}"
        fail_url = f"{base_url}/ops/api/sessions/{sess.id}/split/{split.id}/payment-callback?status=fail&token={cb_token}"
        payment_url = hyp.create_payment_url(
            amount=charge_amount,
            order_id=f"{order_ref}-S{split.portion_index+1}",
            description=f'שולחן {table_num} חלק {split.portion_index+1}',
            success_url=success_url,
            failure_url=fail_url,
            customer_name=split.payer_label or f'משלם {split.portion_index+1}',
        )
        split.payment_method = 'payment_link'
        split.payment_callback_token = cb_token
        db.session.commit()
        return jsonify({'ok': True, 'payment_url': payment_url, 'message': 'קישור תשלום נוצר'})
    except Exception as e:
        logging.error(f"HYP split payment link error for session {session_id}, split {split_id}: {e}")
        return jsonify({'ok': False, 'error': f'שגיאה ביצירת קישור: {str(e)}'})


@ops_bp.route('/api/sessions/<int:session_id>/split/<int:split_id>/payment-callback')
def session_split_payment_callback(session_id, split_id):
    sess = DineInSession.query.get(session_id)
    if not sess:
        return 'Session not found', 404
    split = DineInPaymentSplit.query.get(split_id)
    if not split or split.session_id != sess.id:
        return 'Split not found', 404
    cb_token = request.args.get('token', '')
    if not cb_token or not split.payment_callback_token or cb_token != split.payment_callback_token:
        return 'Invalid callback token', 403
    if split.payment_status == 'paid':
        effective_branch = sess.branch_id
        return redirect(url_for('ops.tables_page', branch=effective_branch))
    status = request.args.get('status', '')
    if status == 'success':
        if sess.pending_void_approvals:
            try:
                pending = json.loads(sess.pending_void_approvals)
                if pending:
                    logging.warning(f'Split payment callback blocked — {len(pending)} pending void approvals for session {sess.id}')
                    effective_branch = sess.branch_id
                    return redirect(url_for('ops.tables_page', branch=effective_branch))
            except Exception:
                pass
        hyp_verified = False
        expected_amount = float(split.amount + (split.tip_amount or 0))
        try:
            from standalone_order_service.hyp_payment import HYPPayment
            hyp = HYPPayment()
            if sess.branch_id:
                hyp._load_credentials(branch=Branch.query.get(sess.branch_id))
            response_params = dict(request.args)
            verification = hyp.verify_payment_response(
                response_params,
                expected_amount=expected_amount,
                verify_signature=True
            )
            if verification.get('verified'):
                hyp_verified = True
                logging.info(f'Split {split.id} session {sess.id}: HYP payment verified (tx={verification.get("transaction_id")})')
            else:
                logging.warning(f'Split {split.id} session {sess.id}: HYP verification failed: {verification.get("error_message")}')
        except Exception as e:
            logging.error(f'Split {split.id} session {sess.id}: HYP verification error: {e}')
            hyp_verified = False
        if not hyp_verified:
            effective_branch = sess.branch_id
            return redirect(url_for('ops.tables_page', branch=effective_branch))
        split.payment_status = 'paid'
        split.payment_method = 'payment_link'
        split.paid_at = datetime.utcnow()
        split.payment_callback_token = None
        all_splits = DineInPaymentSplit.query.filter_by(session_id=sess.id).all()
        all_paid = all(s.payment_status == 'paid' for s in all_splits)
        if all_paid:
            total_tip = sum(s.tip_amount or 0 for s in all_splits)
            sess.tip_amount = total_tip
            for order in sess.orders:
                if order.status != 'cancelled':
                    order.payment_status = 'paid'
                    order.payment_method = 'split'
                    if order.status not in ('delivered', 'pickedup', 'cancelled'):
                        order.status = 'pickedup'
                        order.completed_at = datetime.utcnow()
            sess.status = 'closed'
            sess.closed_at = datetime.utcnow()
        db.session.commit()
    effective_branch = sess.branch_id
    return redirect(url_for('ops.tables_page', branch=effective_branch))


@ops_bp.route('/api/sessions/<int:session_id>/splits', methods=['GET'])
@require_ops_module('tables')
def api_session_splits(session_id):
    effective_branch = _get_effective_branch_id()
    sess = DineInSession.query.get(session_id)
    if not sess or sess.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'ישיבה לא נמצאה'})
    splits = DineInPaymentSplit.query.filter_by(session_id=sess.id).order_by(DineInPaymentSplit.portion_index).all()
    return jsonify({
        'ok': True,
        'total': sess.total_amount,
        'splits': [{'id': s.id, 'index': s.portion_index, 'amount': s.amount,
                     'label': s.payer_label, 'status': s.payment_status, 'method': s.payment_method,
                     'tip': s.tip_amount or 0} for s in splits]
    })


@ops_bp.route('/api/sessions/<int:session_id>/move-table', methods=['POST'])
@require_ops_module('tables')
def api_session_move_table(session_id):
    effective_branch = _get_effective_branch_id()
    sess = DineInSession.query.get(session_id)
    if not sess or sess.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'ישיבה לא נמצאה'})
    if sess.status not in ('open', 'awaiting_payment'):
        return jsonify({'ok': False, 'error': 'ניתן להעביר רק ישיבה פעילה'})
    data = request.get_json(force=True)
    new_table_id = data.get('new_table_id')
    new_table = DineInTable.query.get(new_table_id)
    if not new_table or new_table.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'שולחן יעד לא נמצא'})
    existing = DineInSession.query.filter_by(table_id=new_table.id).filter(
        DineInSession.status.in_(['open', 'awaiting_payment'])).first()
    if existing:
        return jsonify({'ok': False, 'error': 'שולחן היעד תפוס'})
    old_num = sess.table.table_number if sess.table else '?'
    sess.table_id = new_table.id
    for order in sess.orders:
        order.table_number = new_table.table_number
        if order.customer_name and old_num in order.customer_name:
            order.customer_name = f'שולחן {new_table.table_number}'
    db.session.commit()
    return jsonify({'ok': True, 'message': f'שולחן הועבר ל-{new_table.table_number}'})


@ops_bp.route('/api/sessions/<int:session_id>/reopen', methods=['POST'])
@require_ops_module('tables')
def api_session_reopen(session_id):
    effective_branch = _get_effective_branch_id()
    sess = DineInSession.query.get(session_id)
    if not sess or sess.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'ישיבה לא נמצאה'})
    if sess.status not in ('closed', 'cancelled'):
        return jsonify({'ok': False, 'error': 'ניתן לפתוח מחדש רק ישיבות סגורות'})
    active = DineInSession.query.filter_by(table_id=sess.table_id).filter(DineInSession.status.in_(['open', 'awaiting_payment'])).first()
    if active:
        return jsonify({'ok': False, 'error': 'יש ישיבה פעילה בשולחן זה'})
    sess.status = 'open'
    sess.closed_at = None
    sess.payment_callback_token = None
    for order in sess.orders:
        if order.status == 'cancelled':
            continue
        if order.payment_status == 'paid':
            order.payment_status = 'pending'
    db.session.commit()
    return jsonify({'ok': True, 'session_id': sess.id, 'message': 'ישיבה נפתחה מחדש'})


@ops_bp.route('/api/sessions/<int:session_id>/print-check', methods=['POST'])
@require_ops_module('tables')
def api_session_print_check(session_id):
    effective_branch = _get_effective_branch_id()
    sess = DineInSession.query.get(session_id)
    if not sess or sess.branch_id != effective_branch:
        return jsonify({'ok': False, 'error': 'ישיבה לא נמצאה'})
    total = sess.total_amount
    if total <= 0:
        return jsonify({'ok': False, 'error': 'אין פריטים לחשבון'})
    if not sess.payment_url:
        try:
            from standalone_order_service.hyp_payment import HYPPayment
            branch = Branch.query.get(effective_branch)
            settings = _settings()
            hyp = HYPPayment(settings=settings)
            if branch:
                hyp._load_credentials(branch=branch)
            if hyp.is_configured:
                first_order = next((o for o in sess.orders if o.status != 'cancelled'), None)
                if first_order:
                    import secrets as _secrets
                    cb_token = _secrets.token_urlsafe(32)
                    sess.payment_callback_token = cb_token
                    table_num = sess.table.table_number if sess.table else '?'
                    scheme = 'https' if _is_secure() else 'http'
                    base_url = f"{scheme}://{request.host}"
                    success_url = f"{base_url}/ops/api/sessions/{sess.id}/payment-callback?status=success&token={cb_token}"
                    fail_url = f"{base_url}/ops/api/sessions/{sess.id}/payment-callback?status=fail&token={cb_token}"
                    payment_url = hyp.create_payment_url(
                        amount=total,
                        order_id=first_order.order_number,
                        description=f'שולחן {table_num}',
                        success_url=success_url,
                        failure_url=fail_url,
                        customer_name=f'שולחן {table_num}',
                    )
                    sess.payment_url = payment_url
                    sess.status = 'awaiting_payment'
                    db.session.commit()
        except Exception as e:
            logging.warning(f"Could not generate payment URL for check print: {e}")
    try:
        printers = Printer.query.filter_by(branch_id=effective_branch, is_active=True).all()
        if not printers:
            return jsonify({'ok': False, 'error': 'לא נמצאה מדפסת לסניף'})
        default_printer = next((p for p in printers if p.is_default), printers[0])
        table_num = sess.table.table_number if sess.table else '?'
        all_items = []
        for order in sess.orders:
            if order.status != 'cancelled':
                for item in (order.get_items() or []):
                    all_items.append(item)

        check_job = {
            'type': 'print_check',
            'session_id': sess.id,
            'table_number': table_num,
            'branch_id': effective_branch,
            'printer': default_printer.to_dict(),
            'items': all_items,
            'subtotal': sess.subtotal_before_discount,
            'discount_type': sess.discount_type or '',
            'discount_value': sess.discount_value or 0,
            'total': total,
            'payment_url': sess.payment_url or '',
        }
        _notify_sse_order_event(check_job)
        return jsonify({'ok': True, 'message': 'חשבון נשלח למדפסת'})
    except Exception as e:
        logging.error(f"Check print error for session {session_id}: {e}")
        return jsonify({'ok': False, 'error': f'שגיאה בהדפסה: {str(e)}'})


def _build_dine_in_check(printer, table_number, items, subtotal, discount_type, discount_value, total, payment_url=None):
    buf = bytearray()
    encoding = getattr(printer, 'encoding', 'cp862') or 'cp862'
    codepage = getattr(printer, 'codepage_num', 15) or 15

    def add(text_str):
        try:
            for ch in text_str:
                if '\u0590' <= ch <= '\u05FF':
                    buf.append(0x80 + (ord(ch) - 0x05D0))
                else:
                    buf.extend(ch.encode(encoding, errors='replace'))
        except Exception:
            buf.extend(text_str.encode('ascii', errors='replace'))

    buf.extend(b'\x1b\x40')
    buf.extend(b'\x1bt')
    buf.append(codepage)
    buf.extend(b'\x1ba\x01')
    buf.extend(b'\x1b!\x30')
    add('SUMO')
    buf.append(0x0A)
    buf.extend(b'\x1b!\x00')
    buf.append(0x0A)
    buf.extend(b'\x1b!\x10')
    reversed_table = table_number[::-1] if any('\u0590' <= c <= '\u05FF' for c in table_number) else table_number
    add(f'{reversed_table} ןחלוש')
    buf.append(0x0A)
    buf.extend(b'\x1b!\x00')
    buf.append(0x0A)
    buf.extend(b'\x1ba\x00')
    buf.extend(b'-' * 32)
    buf.append(0x0A)

    for item in items:
        name = item.get('name_he', item.get('item_name_he', ''))
        qty = int(item.get('qty', item.get('quantity', 1)))
        price = float(item.get('price', item.get('unit_price', 0)))
        line_total = qty * price
        reversed_name = name[::-1]
        price_str = f'{line_total:.0f}'
        qty_str = f'x{qty} ' if qty > 1 else ''
        right_part = f'{qty_str}{reversed_name}'
        left_part = price_str
        pad = 32 - len(right_part) - len(left_part)
        if pad < 1:
            pad = 1
        line = f'{left_part}{" " * pad}{right_part}'
        add(line)
        buf.append(0x0A)
        if item.get('notes') or item.get('special_instructions'):
            note = item.get('notes') or item.get('special_instructions', '')
            add(f'  {note[::-1]}')
            buf.append(0x0A)

    buf.extend(b'-' * 32)
    buf.append(0x0A)

    if discount_type and discount_value and discount_value > 0:
        buf.extend(b'\x1ba\x00')
        if discount_type == 'percentage':
            disc_label = f'%{discount_value:.0f} החנה'
        else:
            disc_label = f'₪{discount_value:.0f} החנה'
        disc_amount = subtotal - total
        disc_line = f'{disc_amount:.0f}-    {disc_label}'
        add(disc_line)
        buf.append(0x0A)

    buf.extend(b'\x1ba\x01')
    buf.extend(b'\x1b!\x10')
    total_line = f'₪{total:.2f} :םולשתל כ"הס'
    add(total_line)
    buf.append(0x0A)
    buf.extend(b'\x1b!\x00')
    buf.append(0x0A)

    if payment_url:
        buf.extend(b'\x1ba\x01')
        add('QR ורקס - םולשתל')
        buf.append(0x0A)
        buf.append(0x0A)
        try:
            import qrcode
            import io
            qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=6, border=2)
            qr.add_data(payment_url)
            qr.make(fit=True)
            matrix = qr.get_matrix()
            height = len(matrix)
            width = len(matrix[0]) if matrix else 0
            byte_width = (width + 7) // 8
            buf.extend(b'\x1dv0\x00')
            buf.append(byte_width & 0xFF)
            buf.append((byte_width >> 8) & 0xFF)
            buf.append(height & 0xFF)
            buf.append((height >> 8) & 0xFF)
            for row in matrix:
                row_bytes = bytearray(byte_width)
                for x, cell in enumerate(row):
                    if cell:
                        row_bytes[x // 8] |= (0x80 >> (x % 8))
                buf.extend(row_bytes)
        except ImportError:
            add(payment_url)
            buf.append(0x0A)
        buf.append(0x0A)

    buf.extend(b'\x1ba\x01')
    add('!הבוט ןובאת')
    buf.append(0x0A)
    from datetime import datetime as _dt
    from zoneinfo import ZoneInfo
    il_tz = ZoneInfo('Asia/Jerusalem')
    now_il = _dt.now(il_tz)
    add(now_il.strftime('%H:%M %d/%m/%Y'))
    buf.append(0x0A)
    for _ in range(5):
        buf.append(0x0A)
    buf.extend(b'\x1dV\x00')
    return buf


@ops_bp.route('/dine-in/<int:session_id>')
@require_ops_module('tables')
def dine_in_order(session_id):
    effective_branch = _get_effective_branch_id()
    sess = DineInSession.query.get(session_id)
    if not sess or sess.branch_id != effective_branch:
        flash('ישיבה לא נמצאה', 'danger')
        return redirect(url_for('ops.tables_view'))
    categories = MenuCategory.query.filter_by(is_active=True).order_by(MenuCategory.display_order).all()
    menu_data = []
    for cat in categories:
        items_q = MenuItem.query.filter_by(category_id=cat.id, is_available=True)
        cat_items = []
        for item in items_q.order_by(MenuItem.display_order).all():
            if effective_branch:
                bmi = BranchMenuItem.query.filter_by(branch_id=effective_branch, menu_item_id=item.id).first()
                if bmi and not bmi.is_available:
                    continue
                price = bmi.custom_price if (bmi and bmi.custom_price is not None) else item.base_price
            else:
                price = item.base_price
            option_groups_list = []
            for og in item.option_groups:
                if not og.is_active:
                    continue
                choices = []
                for ch in og.choices:
                    if not ch.is_available:
                        continue
                    choices.append({
                        'id': ch.id,
                        'name_he': ch.name_he,
                        'price_modifier': ch.price_modifier or 0,
                        'is_default': ch.is_default,
                    })
                if choices:
                    option_groups_list.append({
                        'id': og.id,
                        'name_he': og.name_he,
                        'selection_type': og.selection_type,
                        'is_required': og.is_required,
                        'min_selections': og.min_selections or 0,
                        'max_selections': og.max_selections or 0,
                        'choices': choices,
                    })
            from models import GlobalOptionGroupLink
            global_links = GlobalOptionGroupLink.query.filter_by(menu_item_id=item.id).all()
            for link in global_links:
                gog = link.global_group
                if not gog or not gog.is_active:
                    continue
                if link.linked_option_group_id:
                    continue
                g_choices = []
                for gc in gog.choices:
                    if not gc.is_available:
                        continue
                    g_choices.append({
                        'id': gc.id,
                        'name_he': gc.name_he,
                        'price_modifier': gc.price_modifier or 0,
                        'is_default': gc.is_default,
                        'is_global': True,
                    })
                if g_choices:
                    option_groups_list.append({
                        'id': f'g_{gog.id}',
                        'name_he': gog.name_he,
                        'selection_type': gog.selection_type,
                        'is_required': gog.is_required,
                        'min_selections': gog.min_selections or 0,
                        'max_selections': gog.max_selections or 0,
                        'choices': g_choices,
                    })
            cat_items.append({
                'id': item.id,
                'name_he': item.name_he,
                'name_en': item.name_en or '',
                'price': float(price) if price else 0,
                'description_he': item.short_description_he or item.description_he or '',
                'option_groups': option_groups_list,
            })
        if cat_items:
            menu_data.append({
                'id': cat.id,
                'name_he': cat.name_he,
                'icon': cat.icon or 'utensils',
                'items': cat_items,
            })
    deals_data = []
    active_deals = Deal.query.filter_by(is_active=True).order_by(Deal.display_order).all()
    for deal in active_deals:
        if not deal.is_valid():
            continue
        deal_info = {
            'id': deal.id,
            'name_he': deal.name_he,
            'name_en': deal.name_en or '',
            'deal_price': float(deal.deal_price),
            'original_price': float(deal.original_price) if deal.original_price else None,
            'description_he': deal.description_he or '',
            'deal_type': deal.deal_type or 'fixed',
            'included_items': deal.included_items or [],
        }
        if deal.deal_type == 'customer_picks':
            deal_info['pick_count'] = deal.pick_count or 0
            source_cats = deal.effective_category_ids
            deal_info['source_category_ids'] = source_cats
            pick_items = []
            for sc_id in source_cats:
                sc_items = MenuItem.query.filter_by(category_id=sc_id, is_available=True, show_in_order=True).order_by(MenuItem.display_order).all()
                for pi in sc_items:
                    if effective_branch:
                        bmi = BranchMenuItem.query.filter_by(branch_id=effective_branch, menu_item_id=pi.id).first()
                        if bmi and not bmi.is_available:
                            continue
                    pick_items.append({'item_id': pi.id, 'name_he': pi.name_he, 'name_en': pi.name_en or ''})
            deal_info['pick_items'] = pick_items
        else:
            included_details = []
            for inc in (deal.included_items or []):
                inc_id = inc.get('item_id') or inc.get('id')
                if inc_id:
                    inc_item = MenuItem.query.get(int(inc_id))
                    if inc_item:
                        included_details.append({'item_id': inc_item.id, 'name_he': inc_item.name_he, 'qty': inc.get('qty') or inc.get('quantity') or 1})
            deal_info['included_details'] = included_details
        deals_data.append(deal_info)
    return render_template('ops/dine_in_order.html',
        active_tab='tables',
        din_session=sess,
        menu_data=menu_data,
        deals_data=deals_data,
    )
