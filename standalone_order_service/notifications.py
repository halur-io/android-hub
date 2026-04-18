"""
Order Notification Service — SMS & Telegram.

Provides pluggable notification functions for food orders.
The host application must supply concrete ``send_sms`` and
``send_telegram`` callables (see INTEGRATION_GUIDE.md).

Quick-start::

    from standalone_order_service.notifications import OrderNotifier
    notifier = OrderNotifier(
        send_sms=my_sms_function,          # (phone, message) -> bool
        send_telegram=my_telegram_function  # (chat_id, message_html) -> bool
    )
    notifier.notify_new_order(order, settings)
    notifier.send_customer_confirmation(order, settings)
"""

import logging
from typing import Callable, Optional, Any

logger = logging.getLogger(__name__)


class OrderNotifier:
    def __init__(
        self,
        send_sms: Optional[Callable] = None,
        send_telegram: Optional[Callable] = None,
        db=None,
        SMSLog=None,
    ):
        self._send_sms = send_sms
        self._send_telegram = send_telegram
        self._db = db
        self._SMSLog = SMSLog

    def _log_sms(self, order_id, phone, msg_type, message, success, error=None):
        if not self._SMSLog or not self._db:
            return
        try:
            sms_log = self._SMSLog(
                order_id=order_id,
                recipient_phone=phone,
                message_type=msg_type,
                message_text=message[:2000] if message else '',
                provider='sms4free',
                status='sent' if success else 'failed',
                error_message=str(error)[:500] if error else None,
            )
            self._db.session.add(sms_log)
            self._db.session.commit()
        except Exception as e:
            logger.warning(f"[SMS-LOG] Failed to log SMS: {e}")

    def notify_new_order(self, order, settings=None):
        try:
            self._send_admin_sms(order, settings)
        except Exception as e:
            logger.warning(f"[ORDER-SMS-ADMIN] {e}")
        try:
            self._send_order_telegram(order, settings)
        except Exception as e:
            logger.warning(f"[ORDER-TELEGRAM] {e}")

    def send_customer_confirmation(self, order, settings=None):
        if not self._send_sms:
            return None
        try:
            type_he = 'משלוח' if order.order_type == 'delivery' else 'איסוף עצמי'
            msg = (
                f"שלום {order.customer_name}!\n"
                f"הזמנתך {(order.display_number or order.order_number)} התקבלה בהצלחה 🎉\n"
                f"סוג: {type_he}\n"
                f'סה"כ: ₪{order.total_amount:.0f}\n'
            )
            if order.order_type == 'delivery':
                est = getattr(settings, 'estimated_delivery_time', '45-60') if settings else '45-60'
                msg += f"זמן משוער: {est} דקות\n"
            else:
                if order.pickup_time and order.pickup_time != 'ASAP':
                    msg += f"זמן איסוף: {order.pickup_time}\n"
            if getattr(order, 'tracking_token', None):
                send_link = True
                if settings and not getattr(settings, 'send_order_tracking_link', True):
                    send_link = False
                if send_link:
                    try:
                        from flask import url_for
                        tracking_url = url_for('order_page.order_track', token=order.tracking_token, _external=True)
                        msg += f"עקוב אחר ההזמנה:\n{tracking_url}\n"
                    except Exception:
                        pass
            msg += "תודה שהזמנת אצלנו! 🍽️"
            result = self._send_sms(order.customer_phone, msg)
            self._log_sms(order.id, order.customer_phone, 'customer_confirmation', msg, bool(result))
            return result
        except Exception as e:
            logger.error(f"[ORDER-SMS-CUSTOMER] {e}")
            self._log_sms(getattr(order, 'id', None), getattr(order, 'customer_phone', ''), 'customer_confirmation', '', False, e)
            return None

    def _send_admin_sms(self, order, settings):
        if not self._send_sms or not settings:
            return
        admin_phone = getattr(settings, 'admin_phone', None) or getattr(settings, 'contact_phone', None)
        if not admin_phone:
            return
        type_he = 'משלוח' if order.order_type == 'delivery' else 'איסוף עצמי'
        items_text = ''
        for item in order.get_items():
            qty = item.get('qty', 1)
            name = item.get('name_he', item.get('name', ''))
            price = item.get('price', 0)
            items_text += f"  • {name} x{qty} — ₪{qty * price:.0f}\n"
        msg = (
            f"🛵 הזמנה חדשה! {(order.display_number or order.order_number)}\n"
            f"סוג: {type_he}\n"
            f"לקוח: {order.customer_name} | {order.customer_phone}\n"
        )
        if order.order_type == 'delivery':
            addr = f"{order.delivery_address}, {order.delivery_city}" if order.delivery_city else order.delivery_address
            msg += f"כתובת: {addr}\n"
        else:
            msg += f"זמן איסוף: {order.pickup_time or 'ASAP'}\n"
        msg += f"פריטים:\n{items_text}"
        msg += f'סה"כ: ₪{order.total_amount:.0f} ({("כרטיס" if order.payment_method == "card" else "מזומן")})'
        if order.customer_notes:
            msg += f"\nהערות: {order.customer_notes}"
        try:
            result = self._send_sms(admin_phone, msg)
            self._log_sms(order.id, admin_phone, 'admin_notification', msg, bool(result))
        except Exception as e:
            self._log_sms(order.id, admin_phone, 'admin_notification', msg, False, e)
            raise

    def _send_order_telegram(self, order, settings):
        if not self._send_telegram or not settings:
            return
        import requests as _req
        bot_token = getattr(settings, 'telegram_bot_token', None)
        if not bot_token:
            return
        targets = []
        if getattr(settings, 'telegram_chat_id', None):
            targets.append(settings.telegram_chat_id)
        if getattr(settings, 'telegram_channel_id', None):
            targets.append(settings.telegram_channel_id)
        if not targets:
            return

        type_he = '🛵 משלוח' if order.order_type == 'delivery' else '🏃 איסוף עצמי'
        payment_he = '💳 כרטיס' if order.payment_method == 'card' else '💵 מזומן'
        items_text = ''
        for item in order.get_items():
            qty = item.get('qty', 1)
            name = item.get('name_he', item.get('name', ''))
            price = item.get('price', 0)
            items_text += f"  • {name} ×{qty}  ₪{qty * price:.0f}\n"
        msg = (
            f"🍽️ <b>הזמנה חדשה #{(order.display_number or order.order_number)}</b>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"{type_he}\n"
            f"👤 {order.customer_name}  📞 {order.customer_phone}\n"
        )
        if order.order_type == 'delivery':
            addr = order.delivery_address or ''
            if order.delivery_city:
                addr += f", {order.delivery_city}"
            msg += f"📍 {addr}\n"
        else:
            if order.pickup_time and order.pickup_time != 'ASAP':
                msg += f"⏰ איסוף: {order.pickup_time}\n"
        msg += f"\n<b>פריטים:</b>\n{items_text}\n"
        msg += f'💰 <b>סה"כ: ₪{order.total_amount:.0f}</b>  |  {payment_he}\n'
        if order.customer_notes:
            msg += f"📝 הערות: {order.customer_notes}\n"
        if order.delivery_notes:
            msg += f"🏠 כניסה: {order.delivery_notes}\n"

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        for chat_id in targets:
            try:
                _req.post(url, json={'chat_id': chat_id, 'text': msg, 'parse_mode': 'HTML'}, timeout=10)
            except Exception as ex:
                logger.warning(f"[ORDER-TELEGRAM] chat {chat_id}: {ex}")
