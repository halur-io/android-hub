"""
SMS Helper Utilities — Twilio & SMS4Free providers.

Provides ready-to-use ``send_sms`` functions for both Twilio and SMS4Free,
including phone number formatting (Israeli numbers) and primary/failover
routing.  These functions match the ``(phone, message) -> bool`` signature
expected by ``OrderNotifier`` and ``create_kds_blueprint``.

Quick-start::

    from standalone_order_service.sms_helpers import create_twilio_sender

    send_sms = create_twilio_sender(
        account_sid='ACxxxx',
        auth_token='xxxx',
        from_number='+972500000000',
    )

    send_sms('+972501234567', 'Hello!')
"""

import logging
import re
from typing import Callable, Dict, Optional

logger = logging.getLogger(__name__)


def clean_phone_number(phone: str) -> str:
    """
    Clean and normalise an Israeli phone number.

    * Strips all non-digit characters (except leading ``+``)
    * Converts a leading ``0`` to the ``972`` country code
    * Prepends ``972`` if no country code is present

    Examples::

        clean_phone_number('050-123-4567')   -> '972501234567'
        clean_phone_number('+972501234567')   -> '+972501234567'
        clean_phone_number('0501234567')      -> '972501234567'
    """
    if not phone:
        return phone
    cleaned = re.sub(r'[^\d+]', '', phone)
    if cleaned.startswith('0'):
        cleaned = cleaned[1:]
    if not cleaned.startswith('+') and not cleaned.startswith('972'):
        cleaned = '972' + cleaned
    return cleaned


def format_phone_for_twilio(phone: str) -> str:
    """
    Format phone for Twilio (E.164: ``+972...``).
    """
    cleaned = clean_phone_number(phone)
    if not cleaned:
        return phone
    if cleaned.startswith('+'):
        return cleaned
    return f'+{cleaned}'


# ─── Twilio ───────────────────────────────────────────────────────────

def create_twilio_sender(
    account_sid: str,
    auth_token: str,
    from_number: str,
    sender_id: Optional[str] = None,
) -> Callable:
    """
    Return a ``(phone, message) -> bool`` callable that sends SMS via Twilio.

    Parameters
    ----------
    account_sid : str
        Twilio Account SID.
    auth_token : str
        Twilio Auth Token.
    from_number : str
        Twilio phone number (E.164 format).
    sender_id : str, optional
        Alphanumeric sender ID (overrides ``from_number`` when set).
    """
    def send(to_phone: str, message: str) -> bool:
        try:
            from twilio.rest import Client
            client = Client(account_sid, auth_token)
            formatted = format_phone_for_twilio(to_phone)
            msg = client.messages.create(
                body=message,
                from_=sender_id or from_number,
                to=formatted,
            )
            logger.info(f"[TWILIO] SMS sent to {formatted}: SID={msg.sid}")
            return True
        except Exception as e:
            logger.error(f"[TWILIO] SMS to {to_phone} failed: {e}")
            return False
    return send


def create_twilio_sender_from_env() -> Optional[Callable]:
    """
    Create a Twilio sender using environment variables.

    Looks for: ``TWILIO_ACCOUNT_SID``, ``TWILIO_AUTH_TOKEN``,
    ``TWILIO_PHONE_NUMBER``, and optionally ``SMS_SENDER_ID``.

    Returns ``None`` if credentials are missing.
    """
    import os
    sid = os.environ.get('TWILIO_ACCOUNT_SID', '').strip()
    token = os.environ.get('TWILIO_AUTH_TOKEN', '').strip()
    phone = os.environ.get('TWILIO_PHONE_NUMBER', '').strip()
    sender_id = os.environ.get('SMS_SENDER_ID', '').strip() or None
    if not sid or not token or not phone:
        logger.warning("[TWILIO] Missing credentials in environment")
        return None
    return create_twilio_sender(sid, token, phone, sender_id)


# ─── SMS4Free ─────────────────────────────────────────────────────────

def create_sms4free_sender(
    api_key: str,
    user: str,
    password: str,
    sender_name: str = 'Restaurant',
) -> Callable:
    """
    Return a ``(phone, message) -> bool`` callable that sends SMS via SMS4Free.

    Parameters
    ----------
    api_key : str
        SMS4Free API key.
    user : str
        SMS4Free username.
    password : str
        SMS4Free password.
    sender_name : str
        Sender name displayed on the SMS (max 11 chars).
    """
    def send(to_phone: str, message: str) -> bool:
        try:
            import requests
            cleaned = clean_phone_number(to_phone)
            if cleaned.startswith('+'):
                cleaned = cleaned[1:]
            resp = requests.post(
                'https://api.sms4free.co.il/ApiSMS/v2/SendSMS',
                json={
                    'key': api_key,
                    'user': user,
                    'pass': password,
                    'sender': sender_name,
                    'recipient': cleaned,
                    'msg': message,
                },
                timeout=15,
            )
            if resp.status_code == 200:
                try:
                    result = resp.json()
                    status = result.get('status', -1)
                    if status == 0 or status == 1:
                        logger.info(f"[SMS4FREE] SMS sent to {cleaned}")
                        return True
                    logger.warning(f"[SMS4FREE] API returned status {status}: {result}")
                    return False
                except Exception:
                    if '1' in resp.text or 'ok' in resp.text.lower():
                        logger.info(f"[SMS4FREE] SMS sent to {cleaned}")
                        return True
            logger.warning(f"[SMS4FREE] HTTP {resp.status_code}: {resp.text[:200]}")
            return False
        except Exception as e:
            logger.error(f"[SMS4FREE] SMS to {to_phone} failed: {e}")
            return False
    return send


def create_sms4free_sender_from_env() -> Optional[Callable]:
    """
    Create an SMS4Free sender using environment variables.

    Looks for: ``SMS4FREE_KEY``, ``SMS4FREE_USER``, ``SMS4FREE_PASS``,
    and optionally ``SMS4FREE_SENDER``.

    Returns ``None`` if credentials are missing.
    """
    import os
    key = os.environ.get('SMS4FREE_KEY', '').strip()
    user = os.environ.get('SMS4FREE_USER', '').strip()
    password = os.environ.get('SMS4FREE_PASS', '').strip()
    sender = os.environ.get('SMS4FREE_SENDER', 'Restaurant').strip()
    if not key or not user or not password:
        logger.warning("[SMS4FREE] Missing credentials in environment")
        return None
    return create_sms4free_sender(key, user, password, sender)


# ─── Multi-provider with failover ─────────────────────────────────────

def create_failover_sender(
    primary: Callable,
    secondary: Optional[Callable] = None,
) -> Callable:
    """
    Wrap two SMS senders with automatic failover.

    If ``primary`` fails, ``secondary`` is tried.  If ``secondary`` is
    ``None`` the call simply returns ``False`` on primary failure.

    Usage::

        twilio = create_twilio_sender_from_env()
        sms4free = create_sms4free_sender_from_env()
        send_sms = create_failover_sender(twilio, sms4free)
    """
    def send(to_phone: str, message: str) -> bool:
        if primary:
            try:
                if primary(to_phone, message):
                    return True
            except Exception as e:
                logger.warning(f"[FAILOVER] Primary sender failed: {e}")
        if secondary:
            try:
                return secondary(to_phone, message)
            except Exception as e:
                logger.error(f"[FAILOVER] Secondary sender also failed: {e}")
        return False
    return send


def create_sender_from_env() -> Optional[Callable]:
    """
    Auto-detect available SMS providers from environment variables and
    return the best ``send_sms`` callable.

    Priority:
      1. Twilio (if ``TWILIO_ACCOUNT_SID`` is set)
      2. SMS4Free (if ``SMS4FREE_KEY`` is set)
      3. Both with failover (if both are set)

    Returns ``None`` if no provider is configured.
    """
    twilio = create_twilio_sender_from_env()
    sms4free = create_sms4free_sender_from_env()
    if twilio and sms4free:
        return create_failover_sender(twilio, sms4free)
    return twilio or sms4free
