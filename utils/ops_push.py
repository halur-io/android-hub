"""Web Push helper for Ops PWA.

Handles VAPID key generation/persistence and pushing notifications to
subscribed Ops devices using pywebpush.
"""
import json
import logging
import os
import base64
from typing import Optional

logger = logging.getLogger(__name__)

_VAPID_CACHE = {'public': None, 'private': None, 'subject': None, 'vapid_obj': None}


def _b64url(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b'=').decode('ascii')


def _generate_vapid_keypair():
    """Generate a new VAPID P-256 keypair. Returns (private_pem, public_b64url)."""
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import serialization
    private_key = ec.generate_private_key(ec.SECP256R1())
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode('ascii')
    public_numbers = private_key.public_key().public_numbers()
    x = public_numbers.x.to_bytes(32, 'big')
    y = public_numbers.y.to_bytes(32, 'big')
    public_uncompressed = b'\x04' + x + y  # 65 bytes
    public_b64 = _b64url(public_uncompressed)
    return private_pem, public_b64


def get_vapid(db, OpsPushVAPID) -> dict:
    """Load (or create) the VAPID keypair. Returns dict with public/private/subject."""
    if _VAPID_CACHE['public']:
        return dict(_VAPID_CACHE)
    row = OpsPushVAPID.query.first()
    if not row:
        priv, pub = _generate_vapid_keypair()
        subject = os.environ.get('VAPID_SUBJECT', 'mailto:admin@sumo-restaurant.co.il')
        row = OpsPushVAPID(public_key=pub, private_key=priv, subject=subject)
        try:
            db.session.add(row)
            db.session.commit()
            logger.info("[PUSH] Generated new VAPID keypair")
        except Exception as e:
            db.session.rollback()
            logger.error(f"[PUSH] Failed to persist VAPID keypair: {e}")
            return {'public': pub, 'private': priv, 'subject': subject}
    _VAPID_CACHE['public'] = row.public_key
    _VAPID_CACHE['private'] = row.private_key
    _VAPID_CACHE['subject'] = row.subject
    return dict(_VAPID_CACHE)


def _get_vapid_object(vapid: dict):
    """Build (and cache) a py_vapid.Vapid02 instance from the stored PEM private key.
    pywebpush can't parse the PEM string directly in some versions, so we pass the
    instance instead."""
    if _VAPID_CACHE.get('vapid_obj') is not None:
        return _VAPID_CACHE['vapid_obj']
    try:
        from py_vapid import Vapid02
        v = Vapid02.from_pem(vapid['private'].encode())
        _VAPID_CACHE['vapid_obj'] = v
        return v
    except Exception as e:
        logger.error(f"[PUSH] Failed to build Vapid02 from PEM: {e}")
        return None


def send_push_to_subscription(sub, payload: dict, vapid: dict) -> bool:
    """Send a single push. Returns True on success, False on failure.
    Sets sub.last_send_status / last_send_error for diagnostics if those columns exist.
    """
    try:
        from pywebpush import webpush, WebPushException
    except ImportError:
        logger.warning("[PUSH] pywebpush not installed")
        return False
    vapid_obj = _get_vapid_object(vapid)
    if vapid_obj is None:
        return False
    try:
        webpush(
            subscription_info={
                'endpoint': sub.endpoint,
                'keys': {'p256dh': sub.p256dh, 'auth': sub.auth},
            },
            data=json.dumps(payload, ensure_ascii=False),
            vapid_private_key=vapid_obj,
            vapid_claims={'sub': vapid['subject']},
            ttl=120,
        )
        logger.info(f"[PUSH] Sent OK to sub {getattr(sub,'id','?')} ({sub.endpoint[:60]})")
        return True
    except WebPushException as e:
        status = getattr(getattr(e, 'response', None), 'status_code', None)
        body = ''
        try:
            body = e.response.text[:200] if e.response is not None else ''
        except Exception:
            pass
        logger.warning(f"[PUSH] Send failed sub={getattr(sub,'id','?')} status={status} body={body} err={e}")
        return False
    except Exception as e:
        logger.warning(f"[PUSH] Unexpected send error sub={getattr(sub,'id','?')}: {type(e).__name__}: {e}")
        return False


def broadcast_new_order_push(order_data: dict):
    """Send push notifications for a new order to all active Ops subscriptions
    (filtered by branch when applicable). Safe to call from any context — never
    raises. Designed to be invoked from the SSE broadcast hook.
    """
    try:
        from database import db
        from models import OpsPushSubscription, OpsPushVAPID
        from datetime import datetime
        vapid = get_vapid(db, OpsPushVAPID)
        if not vapid.get('private'):
            return
        branch_id = order_data.get('branch_id')
        q = OpsPushSubscription.query.filter_by(is_active=True)
        if branch_id:
            from sqlalchemy import or_
            q = q.filter(or_(OpsPushSubscription.branch_id == branch_id,
                             OpsPushSubscription.branch_id.is_(None)))
        subs = q.all()
        if not subs:
            return
        order_no = order_data.get('order_number') or order_data.get('id') or ''
        customer = order_data.get('customer_name') or ''
        total = order_data.get('total_amount') or 0
        otype = order_data.get('order_type') or ''
        type_he = {'delivery': 'משלוח', 'pickup': 'איסוף', 'dine_in': 'ישיבה'}.get(otype, otype)
        title = f"הזמנה חדשה #{order_no}"
        body_parts = []
        if customer:
            body_parts.append(customer)
        if type_he:
            body_parts.append(type_he)
        if total:
            try:
                body_parts.append(f"₪{float(total):.0f}")
            except Exception:
                pass
        payload = {
            'title': title,
            'body': ' • '.join(body_parts) if body_parts else 'יש הזמנה חדשה',
            'tag': f'order-{order_no}',
            'url': '/ops/orders',
            'orderId': order_data.get('id'),
            'requireInteraction': True,
        }
        sent = 0
        failed = 0
        for sub in subs:
            ok = send_push_to_subscription(sub, payload, vapid)
            if ok:
                sub.last_used_at = datetime.utcnow()
                sub.failure_count = 0
                sent += 1
            else:
                sub.failure_count = (sub.failure_count or 0) + 1
                if sub.failure_count >= 3:
                    sub.is_active = False
                failed += 1
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
        logger.info(f"[PUSH] Broadcast new order {order_no}: {sent} sent, {failed} failed")
    except Exception as e:
        logger.warning(f"[PUSH] broadcast_new_order_push error: {e}")
