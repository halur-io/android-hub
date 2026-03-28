"""
SMS Helper Utilities — SMS4Free provider.

Provides a ready-to-use ``send_sms`` function for SMS4Free,
including phone number formatting (Israeli numbers).
These functions match the ``(phone, message) -> bool`` signature
expected by ``OrderNotifier`` and ``create_kds_blueprint``.

Quick-start::

    from standalone_order_service.sms_helpers import create_sender_from_env

    send_sms = create_sender_from_env()
    send_sms('0501234567', 'Hello!')
"""

import logging
import re
from typing import Callable, Optional

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


def create_sms4free_sender(
    api_key: str,
    user: str,
    password: str,
    sender_name: str = 'Restaurant',
) -> Callable:
    """
    Return a ``(phone, message) -> bool`` callable that sends SMS via SMS4Free.
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


def create_sender_from_env() -> Optional[Callable]:
    """
    Auto-detect available SMS provider from environment variables and
    return the best ``send_sms`` callable.

    Uses SMS4Free (if ``SMS4FREE_KEY`` is set).
    Returns ``None`` if no provider is configured.
    """
    return create_sms4free_sender_from_env()
