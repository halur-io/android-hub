import json
import logging
import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Blueprint, render_template, request, session, redirect,
    url_for, jsonify, make_response, flash,
)
from database import db
from models import (
    ManagerPIN, EnrolledDevice, SiteSettings, Branch, WorkingHours,
    MenuCategory, MenuItem, StockItem, StockLevel, StockTransaction,
    StockAlert, Deal, Coupon, CouponUsage, FoodOrder,
)

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
    pin_id = session.get('ops_pin_id')
    if not pin_id:
        return None
    return ManagerPIN.query.filter_by(id=pin_id, is_active=True).first()

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

@ops_bp.context_processor
def inject_ops_context():
    user = _get_ops_user()
    modules = user.get_ops_modules() if user else []
    return dict(
        ops_modules=modules,
        ops_user=user,
    )


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
    return render_template('ops/not_enrolled.html', enrollment_code=None)


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
        secure=request.is_secure,
    )
    return resp


@ops_bp.route('/login', methods=['GET', 'POST'])
@require_device
def login():
    error = None
    if request.method == 'POST':
        pin = request.form.get('pin', '')
        pins = ManagerPIN.query.filter_by(is_active=True).all()
        for p in pins:
            if p.check_pin(pin):
                session['ops_pin_id'] = p.id
                session['ops_user_name'] = p.name
                p.last_used_at = datetime.utcnow()
                db.session.commit()
                return redirect(url_for('ops.index'))
        error = 'קוד PIN שגוי'
    return render_template('ops/login.html', error=error)


@ops_bp.route('/logout')
def logout():
    session.pop('ops_pin_id', None)
    session.pop('ops_user_name', None)
    return redirect(url_for('ops.login'))


@ops_bp.route('/home')
@require_ops_module('home')
def home():
    settings = _settings()
    now = _get_israel_now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    today_orders = FoodOrder.query.filter(FoodOrder.created_at >= today_start).all()
    total_revenue = sum(o.total_amount or 0 for o in today_orders if o.payment_status == 'paid')
    active_orders = sum(1 for o in today_orders if o.status in ('pending', 'confirmed', 'preparing'))
    completed_orders = sum(1 for o in today_orders if o.status in ('delivered', 'pickedup'))

    low_stock_count = 0
    try:
        levels = StockLevel.query.join(StockItem).filter(StockItem.is_active == True).all()
        for lvl in levels:
            if lvl.item and lvl.current_quantity <= (lvl.item.minimum_stock or 0):
                low_stock_count += 1
    except Exception:
        pass

    return render_template('ops/home.html',
        active_tab='home',
        settings=settings,
        total_revenue=total_revenue,
        active_orders=active_orders,
        completed_orders=completed_orders,
        total_orders=len(today_orders),
        low_stock_count=low_stock_count,
    )


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

    return render_template('ops/menu.html',
        active_tab='menu',
        categories=categories,
        items=items,
        selected_category=cat_id,
        search=search,
    )


@ops_bp.route('/api/menu/toggle', methods=['POST'])
@require_ops_module('menu')
def menu_toggle():
    data = request.get_json(force=True)
    item_id = data.get('item_id')
    item = MenuItem.query.get(item_id)
    if not item:
        return jsonify({'ok': False, 'error': 'פריט לא נמצא'})
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
        item.base_price = float(price)
        db.session.commit()
        return jsonify({'ok': True, 'message': 'מחיר עודכן'})
    except (ValueError, TypeError):
        return jsonify({'ok': False, 'error': 'מחיר לא תקין'})


@ops_bp.route('/stock')
@require_ops_module('stock')
def stock():
    items = StockItem.query.filter_by(is_active=True).order_by(StockItem.name_he).all()
    levels = {}
    for lvl in StockLevel.query.all():
        levels[lvl.item_id] = lvl

    recent_txns = StockTransaction.query.order_by(
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

    branches = Branch.query.filter_by(is_active=True).all()
    branch_id = branches[0].id if branches else None
    if not branch_id:
        return jsonify({'ok': False, 'error': 'לא נמצא סניף'})

    txn = StockTransaction(
        item_id=item_id,
        branch_id=branch_id,
        transaction_type=txn_type,
        quantity=qty,
        notes=notes,
        transaction_date=datetime.utcnow(),
    )
    db.session.add(txn)

    lvl = StockLevel.query.filter_by(item_id=item_id, branch_id=branch_id).first()
    if lvl:
        lvl.current_quantity = (lvl.current_quantity or 0) + qty
        lvl.available_quantity = lvl.current_quantity - (lvl.reserved_quantity or 0)
    else:
        lvl = StockLevel(
            item_id=item_id,
            branch_id=branch_id,
            current_quantity=qty,
            available_quantity=qty,
        )
        db.session.add(lvl)

    db.session.commit()
    return jsonify({'ok': True, 'message': 'עסקה נרשמה', 'new_qty': lvl.current_quantity})


@ops_bp.route('/deals')
@require_ops_module('deals')
def deals():
    all_deals = Deal.query.order_by(Deal.display_order).all()
    all_coupons = Coupon.query.order_by(Coupon.created_at.desc()).all()
    filter_type = request.args.get('filter', 'all')
    return render_template('ops/deals.html',
        active_tab='deals',
        deals=all_deals,
        coupons=all_coupons,
        filter_type=filter_type,
    )


@ops_bp.route('/api/deals/toggle', methods=['POST'])
@require_ops_module('deals')
def deal_toggle():
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
    all_branches = Branch.query.filter_by(is_active=True).order_by(Branch.display_order).all()
    hours = {}
    for h in WorkingHours.query.all():
        hours.setdefault(h.branch_id, []).append(h)
    settings = _settings()
    return render_template('ops/branches.html',
        active_tab='branches',
        branches=all_branches,
        hours=hours,
        settings=settings,
    )


@ops_bp.route('/api/branches/toggle', methods=['POST'])
@require_ops_module('branches')
def branch_toggle():
    data = request.get_json(force=True)
    field = data.get('field')
    branch_id = data.get('branch_id')
    value = data.get('value')
    allowed = ['is_active']
    if field not in allowed:
        settings = _settings()
        if settings and field in ('enable_delivery', 'enable_pickup'):
            setattr(settings, field, bool(value))
            db.session.commit()
            return jsonify({'ok': True, 'message': 'עודכן'})
        return jsonify({'ok': False, 'error': 'שדה לא מורשה'})
    branch = Branch.query.get(branch_id)
    if not branch:
        return jsonify({'ok': False, 'error': 'סניף לא נמצא'})
    setattr(branch, field, bool(value))
    db.session.commit()
    return jsonify({'ok': True, 'message': 'עודכן'})


@ops_bp.route('/api/branches/hours', methods=['POST'])
@require_ops_module('branches')
def branch_hours():
    data = request.get_json(force=True)
    hour_id = data.get('hour_id')
    open_time = data.get('open_time')
    close_time = data.get('close_time')
    is_closed = data.get('is_closed')

    wh = WorkingHours.query.get(hour_id)
    if not wh:
        return jsonify({'ok': False, 'error': 'שעות לא נמצאו'})
    if open_time is not None:
        wh.open_time = open_time
    if close_time is not None:
        wh.close_time = close_time
    if is_closed is not None:
        wh.is_closed = bool(is_closed)
    db.session.commit()
    return jsonify({'ok': True, 'message': 'שעות עודכנו'})
