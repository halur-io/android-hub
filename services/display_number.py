"""Short daily display-number generator (T/D/TB) per branch per operating day.

Counters reset only when a manager closes the day. Recycle-on-delete is supported
within the same open day (via ReleasedDisplayNumber).
"""
from datetime import datetime
from sqlalchemy import text
from database import db
from models import (
    OperatingDay, DailyCounter, ReleasedDisplayNumber, FoodOrder,
)

PREFIX_BY_TYPE = {
    'pickup': 'T',
    'delivery': 'D',
    'dine_in': 'TB',
}


def _prefix(order_type):
    return PREFIX_BY_TYPE.get((order_type or '').lower())


def get_open_day(branch_id):
    return OperatingDay.query.filter_by(branch_id=branch_id, status='open').first()


def ensure_open_day(branch_id, opened_by_pin_id=None, opened_by_name=None):
    """Return the currently-open OperatingDay for branch_id; auto-open if none.

    Race-hardened: if two requests both observe no open day and try to insert,
    the partial unique index `uq_one_open_day_per_branch` will reject one with
    IntegrityError; we catch that, roll back the failed savepoint, and re-fetch
    the row the winning transaction inserted.
    """
    from sqlalchemy.exc import IntegrityError
    od = get_open_day(branch_id)
    if od:
        return od
    try:
        with db.session.begin_nested():
            od = OperatingDay(
                branch_id=branch_id,
                status='open',
                opened_at=datetime.utcnow(),
                opened_by_pin_id=opened_by_pin_id,
                opened_by_name=opened_by_name or 'auto',
            )
            db.session.add(od)
            db.session.flush()
        return od
    except IntegrityError:
        # Another concurrent request won the open-day race. Re-fetch.
        od = get_open_day(branch_id)
        if od:
            return od
        raise


def assign_display_number(order, opened_by_pin_id=None, opened_by_name=None):
    """Set order.display_number + order.operating_day_id.

    Picks the smallest freed sequence first (recycle), otherwise atomically
    increments the per-(day,type) counter. No-ops for unknown order types.
    """
    prefix = _prefix(order.order_type)
    if not prefix:
        return None
    if not order.branch_id:
        # Display-number assignment requires a branch; refuse to assign rather
        # than fall through and create a branchless OperatingDay row that
        # would weaken the partial unique constraint (NULL branches don't
        # collide in PostgreSQL partial unique indexes).
        raise ValueError("assign_display_number requires order.branch_id")
    branch_id = order.branch_id
    day = ensure_open_day(branch_id, opened_by_pin_id, opened_by_name)
    order.operating_day_id = day.id

    # 1) Try recycle pool first (smallest seq).
    recycled = (
        ReleasedDisplayNumber.query
        .filter_by(operating_day_id=day.id, order_type=order.order_type)
        .order_by(ReleasedDisplayNumber.display_seq.asc())
        .with_for_update(skip_locked=False)
        .first()
    )
    if recycled is not None:
        seq = recycled.display_seq
        db.session.delete(recycled)
        order.display_number = f"{prefix}{seq:03d}"
        return order.display_number

    # 2) Atomic counter increment under row lock.
    # Race-safe bootstrap: INSERT ... ON CONFLICT DO NOTHING ensures the row
    # exists, then re-SELECT FOR UPDATE locks it. This avoids the case where
    # two concurrent first-orders both insert and one fails the unique
    # constraint. Postgres-specific (matches the project's database).
    db.session.execute(text(
        "INSERT INTO daily_counters (operating_day_id, order_type, next_seq) "
        "VALUES (:did, :ot, 1) "
        "ON CONFLICT (operating_day_id, order_type) DO NOTHING"
    ), {"did": day.id, "ot": order.order_type})
    counter = (
        DailyCounter.query
        .filter_by(operating_day_id=day.id, order_type=order.order_type)
        .with_for_update()
        .first()
    )

    seq = counter.next_seq
    counter.next_seq = seq + 1
    order.display_number = f"{prefix}{seq:03d}"
    return order.display_number


def release_display_number(order):
    """Push order.display_number back into the recycle pool, if its day is open."""
    if not order or not order.display_number or not order.operating_day_id:
        return False
    day = OperatingDay.query.get(order.operating_day_id)
    if not day or day.status != 'open':
        return False
    prefix = _prefix(order.order_type)
    if not prefix or not order.display_number.startswith(prefix):
        return False
    try:
        seq = int(order.display_number[len(prefix):])
    except (TypeError, ValueError):
        return False
    # Avoid double-recycle.
    existing = ReleasedDisplayNumber.query.filter_by(
        operating_day_id=day.id, order_type=order.order_type, display_seq=seq
    ).first()
    if existing:
        return True
    db.session.add(ReleasedDisplayNumber(
        operating_day_id=day.id,
        branch_id=order.branch_id,
        order_type=order.order_type,
        display_seq=seq,
    ))
    return True


def close_operating_day(branch_id, closed_by_pin_id=None, closed_by_name=None):
    """Mark the open day closed, snapshot counts/totals, wipe recycle pool."""
    day = get_open_day(branch_id)
    if not day:
        return None

    rows = db.session.execute(text(
        """
        SELECT order_type,
               COUNT(*) AS cnt,
               COALESCE(SUM(total_amount),0) AS revenue,
               COALESCE(SUM(CASE WHEN payment_method='cash' AND payment_status='paid'
                                 THEN total_amount ELSE 0 END),0) AS cash
        FROM food_orders
        WHERE operating_day_id = :did
          AND (status IS NULL OR status <> 'cancelled')
        GROUP BY order_type
        """
    ), {"did": day.id}).fetchall()

    pickup = delivery = dine = 0
    revenue = cash = 0.0
    for r in rows:
        ot = r[0]
        cnt = int(r[1] or 0)
        rev = float(r[2] or 0)
        ch = float(r[3] or 0)
        revenue += rev
        cash += ch
        if ot == 'pickup':
            pickup = cnt
        elif ot == 'delivery':
            delivery = cnt
        elif ot == 'dine_in':
            dine = cnt

    day.pickup_count = pickup
    day.delivery_count = delivery
    day.dine_in_count = dine
    day.total_revenue = revenue
    day.total_cash = cash
    day.status = 'closed'
    day.closed_at = datetime.utcnow()
    day.closed_by_pin_id = closed_by_pin_id
    day.closed_by_name = closed_by_name

    ReleasedDisplayNumber.query.filter_by(operating_day_id=day.id).delete()
    return day


def open_day_summary(branch_id):
    """Return dict {open, day_id, opened_at, opened_by, pickup, delivery, dine_in, revenue, cash} for the open day."""
    day = get_open_day(branch_id)
    if not day:
        return {'open': False}
    rows = db.session.execute(text(
        """
        SELECT order_type,
               COUNT(*) AS cnt,
               COALESCE(SUM(total_amount),0) AS revenue,
               COALESCE(SUM(CASE WHEN payment_method='cash' AND payment_status='paid'
                                 THEN total_amount ELSE 0 END),0) AS cash
        FROM food_orders
        WHERE operating_day_id = :did
          AND (status IS NULL OR status <> 'cancelled')
        GROUP BY order_type
        """
    ), {"did": day.id}).fetchall()
    pickup = delivery = dine = 0
    revenue = cash = 0.0
    for r in rows:
        ot = r[0]
        cnt = int(r[1] or 0)
        revenue += float(r[2] or 0)
        cash += float(r[3] or 0)
        if ot == 'pickup':
            pickup = cnt
        elif ot == 'delivery':
            delivery = cnt
        elif ot == 'dine_in':
            dine = cnt
    return {
        'open': True,
        'day_id': day.id,
        'opened_at': day.opened_at.isoformat() + 'Z' if day.opened_at else None,
        'opened_by': day.opened_by_name,
        'pickup': pickup,
        'delivery': delivery,
        'dine_in': dine,
        'orders_total': pickup + delivery + dine,
        'revenue': round(revenue, 2),
        'cash': round(cash, 2),
    }


def disp_num(order):
    """Jinja helper: short display number, falling back to legacy order_number."""
    if order is None:
        return ''
    dn = getattr(order, 'display_number', None)
    if dn:
        return dn
    return getattr(order, 'order_number', '') or ''
