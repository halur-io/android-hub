"""
HYP (Yaad Pay) Payment Gateway Integration.

Credential resolution precedence (first complete set wins):
  1. Branch-specific fields  (Branch.hyp_terminal/api_key/passp)
  2. Global site settings    (SiteSettings.hyp_terminal/api_key/passp)
  3. Environment variables   (HYP_TERMINAL, HYP_API_KEY, HYP_PASSP)

Usage::

    from standalone_order_service.hyp_payment import HYPPayment
    hyp = HYPPayment()
    url = hyp.create_payment_url(amount=99.90, order_id='ORD-001', ...)
"""

import os
import hashlib
import hmac
import logging
import urllib.parse
from typing import Optional, Dict, Any

import requests

logger = logging.getLogger(__name__)


class HYPPayment:
    SANDBOX_URL = "https://icom.yaad.net/p/"
    PRODUCTION_URL = "https://pay.hyp.co.il/p/"

    def __init__(self, settings=None):
        self._sandbox_mode = None
        self._settings = settings
        self._credentials_source = None
        self._load_credentials()

    def _load_credentials(self, settings=None, branch=None):
        if settings:
            self._settings = settings

        if branch:
            bt = getattr(branch, 'hyp_terminal', None)
            bk = getattr(branch, 'hyp_api_key', None)
            bp = getattr(branch, 'hyp_passp', None)
            if bt and bk and bp:
                self.terminal = bt
                self.api_key = bk
                self.passp = bp
                self._credentials_source = 'branch'
                return

        s = self._settings
        if s:
            st = getattr(s, 'hyp_terminal', None)
            sk = getattr(s, 'hyp_api_key', None)
            sp = getattr(s, 'hyp_passp', None)
            if st and sk and sp:
                self.terminal = st
                self.api_key = sk
                self.passp = sp
                self._credentials_source = 'settings'
                return

        self.terminal = os.environ.get('HYP_TERMINAL', '').strip()
        self.api_key = os.environ.get('HYP_API_KEY', '').strip()
        self.passp = os.environ.get('HYP_PASSP', '').strip()

        if self.terminal and self.api_key and self.passp:
            self._credentials_source = 'env'
        else:
            self._credentials_source = 'partial'

    @property
    def sandbox_mode(self) -> bool:
        if self._sandbox_mode is None:
            s = self._settings
            self._sandbox_mode = getattr(s, 'hyp_sandbox_mode', True) if s else True
        return self._sandbox_mode

    @property
    def base_url(self) -> str:
        return self.SANDBOX_URL if self.sandbox_mode else self.PRODUCTION_URL

    @property
    def is_configured(self) -> bool:
        return all([self.terminal, self.api_key, self.passp])

    def validate_configuration(self) -> Dict[str, Any]:
        self._load_credentials()
        issues = []
        if not self.terminal:
            issues.append("Terminal (Masof) not set")
        if not self.api_key:
            issues.append("API Key not set")
        if not self.passp:
            issues.append("PassP password not set")
        return {
            'configured': self.is_configured,
            'sandbox_mode': self.sandbox_mode,
            'issues': issues,
            'terminal_masked': f"***{self.terminal[-4:]}" if self.terminal and len(self.terminal) > 4 else None,
            'source': self._credentials_source,
        }

    def generate_signature(self, params: Dict[str, str]) -> str:
        sorted_params = sorted(params.items())
        query_string = urllib.parse.urlencode(sorted_params)
        signature = hmac.new(
            self.api_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def create_payment_url(
        self,
        amount: float,
        order_id: str,
        description: str,
        success_url: str,
        failure_url: str,
        customer_name: Optional[str] = None,
        customer_first_name: Optional[str] = None,
        customer_last_name: Optional[str] = None,
        customer_email: Optional[str] = None,
        customer_phone: Optional[str] = None,
        currency: str = "1",
        installments: int = 1,
        additional_params: Optional[Dict[str, str]] = None,
    ) -> Optional[str]:
        if self._credentials_source != 'branch':
            self._load_credentials()
        self._sandbox_mode = None

        if not self.is_configured:
            logger.error("HYP Payment not configured — missing credentials")
            return None

        params = {
            'Amount': str(float(amount)),
            'Coin': currency,
            'Order': order_id,
            'Info': description[:50],
            'Tash': str(installments),
            'UTF8': 'True',
            'UTF8out': 'True',
            'PageLang': 'HEB',
            'sendemail': 'True',
            'SendHesh': 'True',
            'tmp': '5',
            'Sign': 'True',
            'MoreData': 'True',
            'Iframe': 'True',
        }
        if success_url:
            params['SuccessURL'] = success_url
        if failure_url:
            params['ErrorURL'] = failure_url
        if customer_first_name:
            params['ClientName'] = customer_first_name
        if customer_last_name:
            params['ClientLName'] = customer_last_name
        if not customer_first_name and customer_name:
            params['ClientName'] = customer_name
        if customer_email:
            params['email'] = customer_email
        if customer_phone:
            params['phone'] = customer_phone
        if additional_params:
            params.update(additional_params)

        apisign_params = {
            'action': 'APISign',
            'What': 'SIGN',
            'KEY': self.api_key,
            'PassP': self.passp,
            'Masof': self.terminal,
        }
        apisign_params.update(params)

        try:
            logger.info(f"HYP APISign Step 1: order {order_id}")
            response = requests.get(self.base_url, params=apisign_params, timeout=30)
            response_text = response.text.strip()
            logger.info(f"HYP APISign response: {response_text[:200]}")

            if 'CCode=' in response_text and 'CCode=0' not in response_text:
                error_params = dict(urllib.parse.parse_qsl(response_text))
                ccode = error_params.get('CCode', 'unknown')
                logger.error(f"HYP APISign failed CCode={ccode}: {response_text}")
                return None

            if 'signature=' not in response_text.lower():
                logger.error(f"HYP APISign missing signature: {response_text[:300]}")
                return None

            payment_url = f"{self.base_url}?{response_text}"
            logger.info(f"HYP Step 2: URL created for {order_id}, {amount} ILS")
            return payment_url
        except Exception as e:
            logger.error(f"HYP APISign request failed: {e}")
            return None

    def verify_callback_signature(self, response_params: Dict[str, str]) -> bool:
        if not self.api_key:
            return False
        received_signature = (
            response_params.get('Sign') or
            response_params.get('sign') or
            response_params.get('Signature') or
            response_params.get('signature') or
            ''
        )
        if not received_signature:
            logger.warning("No signature in HYP callback response")
            return False
        params_to_sign = {k: v for k, v in response_params.items()
                          if k.lower() not in ('sign', 'signature', 'apisign')}
        expected_signature = self.generate_signature(params_to_sign)
        return hmac.compare_digest(received_signature.lower(), expected_signature.lower())

    def verify_payment_response(
        self,
        response_params: Dict[str, str],
        expected_order_id: Optional[str] = None,
        expected_amount: Optional[float] = None,
        verify_signature: bool = True,
    ) -> Dict[str, Any]:
        result = {
            'verified': False, 'success': False, 'signature_valid': False,
            'order_id_match': True, 'amount_match': True,
            'error_code': None, 'error_message': None,
            'transaction_id': None, 'order_id': None, 'amount': None,
        }

        if verify_signature:
            if not self.api_key:
                result['error_message'] = 'API key not configured'
                return result
            received_signature = (
                response_params.get('Sign') or response_params.get('sign') or
                response_params.get('Signature') or response_params.get('signature') or ''
            )
            if not received_signature:
                result['error_message'] = 'Missing payment signature'
                return result
            signature_valid = self.verify_callback_signature(response_params)
            result['signature_valid'] = signature_valid
            if not signature_valid:
                ccode = response_params.get('CCode', '')
                if ccode != '0':
                    result['error_message'] = 'Invalid signature'
                    return result
        else:
            result['signature_valid'] = True

        ccode = response_params.get('CCode', '')
        if ccode == '0':
            result['success'] = True
        else:
            result['error_code'] = ccode
            result['error_message'] = self.get_error_message(ccode)

        result['transaction_id'] = response_params.get('Id', response_params.get('Fild1'))
        result['order_id'] = response_params.get('Order')
        try:
            result['amount'] = float(response_params.get('Amount', '0'))
        except (ValueError, TypeError):
            result['amount'] = 0

        if expected_order_id and result['order_id'] != expected_order_id:
            result['order_id_match'] = False
        if expected_amount and abs(float(result['amount']) - float(expected_amount)) > 0.01:
            result['amount_match'] = False

        result['verified'] = (
            result['signature_valid'] and result['success'] and
            result['order_id_match'] and result['amount_match']
        )

        for key, param in [('approval_number', 'Hesh'), ('card_last_4', 'L4digit'), ('card_brand', 'Brand')]:
            if param in response_params:
                result[key] = response_params[param]

        return result

    def get_error_message(self, error_code: str) -> str:
        error_messages = {
            '1': 'הכרטיס חסום',
            '2': 'הכרטיס גנוב',
            '3': 'פנה לחברת האשראי',
            '4': 'סירוב',
            '5': 'כרטיס מזויף',
            '6': 'תעודה שגויה',
            '10': 'סכום גדול מדי',
            '11': 'כרטיס לא קיים',
            '14': 'כרטיס לא תקף',
            '15': 'מספר כרטיס לא קיים',
            '17': 'הלקוח ביטל',
            '26': 'כרטיס פג תוקף',
            '27': 'CVV שגוי',
            '33': 'כרטיס לא ניתן לסליקה',
            '36': 'כרטיס פג תוקף',
            '101': 'אימות נכשל',
            '102': 'טרמינל לא פעיל',
            '103': 'עסקה כפולה',
            '106': 'סכום שגוי',
            '108': 'פרמטר חסר',
        }
        return error_messages.get(error_code, f'שגיאה ({error_code})')

    def refund_transaction(self, transaction_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        if not self.is_configured:
            return {'success': False, 'error': 'HYP not configured'}
        params = {
            'Masof': self.terminal,
            'PassP': self.passp,
            'action': 'APISign',
            'What': 'VERIFY',
            'TransId': transaction_id,
        }
        if amount:
            params['Amount'] = str(int(float(amount) * 100))
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            result_params = dict(urllib.parse.parse_qsl(response.text))
            return {
                'success': result_params.get('CCode') == '0',
                'error_code': result_params.get('CCode'),
                'error_message': self.get_error_message(result_params.get('CCode', '')),
                'raw': result_params,
            }
        except Exception as e:
            logger.error(f"HYP refund failed: {e}")
            return {'success': False, 'error': str(e)}
