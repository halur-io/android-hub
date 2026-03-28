"""
MAX PAY Service Module
Handles payment creation and API communication with Max Pay.

Credentials are resolved at payment time from a Branch object,
falling back to global SiteSettings or environment variables.
"""
import os
import logging
from typing import Dict, Any, Optional

import requests

logger = logging.getLogger(__name__)


class MaxPayService:

    def __init__(self):
        self.api_url = None
        self.api_key = None
        self.merchant_id = None
        self._credentials_source = None

    def _load_credentials(self, branch=None, settings=None):
        self.api_url = None
        self.api_key = None
        self.merchant_id = None
        self._credentials_source = None

        if branch:
            self.api_url = getattr(branch, 'max_api_url', None) or None
            self.api_key = getattr(branch, 'max_api_key', None) or None
            self.merchant_id = getattr(branch, 'max_merchant_id', None) or None
            if self.api_key and self.merchant_id:
                self._credentials_source = 'branch'
                if not self.api_url:
                    self.api_url = os.environ.get('MAX_API_URL', 'https://api.maxpay.co.il/v1/payments')
                return

        if settings:
            self.api_url = getattr(settings, 'max_api_url', None) or None
            self.api_key = getattr(settings, 'max_api_key', None) or None
            self.merchant_id = getattr(settings, 'max_merchant_id', None) or None
            if self.api_key and self.merchant_id:
                self._credentials_source = 'settings'
                if not self.api_url:
                    self.api_url = os.environ.get('MAX_API_URL', 'https://api.maxpay.co.il/v1/payments')
                return

        self.api_url = os.environ.get('MAX_API_URL', 'https://api.maxpay.co.il/v1/payments')
        self.api_key = os.environ.get('MAX_API_KEY', '').strip() or None
        self.merchant_id = os.environ.get('MAX_MERCHANT_ID', '').strip() or None
        if self.api_key and self.merchant_id:
            self._credentials_source = 'env'

    @property
    def is_configured(self) -> bool:
        return bool(self.api_url and self.api_key and self.merchant_id)

    def _get_headers(self) -> Dict[str, str]:
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

    def create_payment(
        self,
        order_id: str,
        amount: float,
        success_url: str,
        failure_url: str,
        customer_name: Optional[str] = None,
        customer_email: Optional[str] = None,
        customer_phone: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self.is_configured:
            logger.error("MAX Pay not configured - missing credentials")
            return {'error': True, 'message': 'MAX Pay not configured'}

        if not order_id or not isinstance(order_id, str):
            return {'error': True, 'message': 'Invalid order_id'}

        if not amount or amount <= 0:
            return {'error': True, 'message': 'Invalid amount'}

        payload = {
            'merchantId': self.merchant_id,
            'amount': round(float(amount), 2),
            'currency': 'ILS',
            'orderId': order_id,
            'successUrl': success_url,
            'cancelUrl': failure_url,
        }
        if description:
            payload['description'] = description[:100]
        if customer_name:
            payload['customerName'] = customer_name
        if customer_email:
            payload['customerEmail'] = customer_email
        if customer_phone:
            payload['customerPhone'] = customer_phone

        try:
            logger.info(f"MAX Pay: creating payment for order {order_id}, {amount} ILS")
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self._get_headers(),
                timeout=30,
            )

            if response.status_code in (200, 201):
                data = response.json()
                payment_url = (
                    data.get('payment_url')
                    or data.get('paymentUrl')
                    or data.get('url')
                )
                if payment_url:
                    logger.info(f"MAX Pay: URL created for order {order_id}")
                    return {
                        'payment_url': payment_url,
                        'order_id': order_id,
                        'amount': amount,
                        'transaction_id': data.get('transactionId') or data.get('transaction_id'),
                    }
                else:
                    logger.error(f"MAX Pay: no payment URL in response: {data}")
                    return {'error': True, 'message': 'Payment URL not found in MAX Pay response'}
            else:
                logger.error(f"MAX Pay API error: {response.status_code} - {response.text[:300]}")
                return {'error': True, 'message': f'MAX Pay API error: {response.status_code}'}

        except requests.exceptions.Timeout:
            logger.error("MAX Pay API request timed out")
            return {'error': True, 'message': 'Payment gateway timeout'}
        except requests.exceptions.RequestException as e:
            logger.error(f"MAX Pay network error: {e}")
            return {'error': True, 'message': f'Network error: {e}'}
        except Exception as e:
            logger.error(f"MAX Pay unexpected error: {e}")
            return {'error': True, 'message': f'Unexpected error: {e}'}

    def verify_payment(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        if not self.is_configured:
            return None
        try:
            verify_url = f"{self.api_url}/{transaction_id}"
            response = requests.get(
                verify_url,
                headers=self._get_headers(),
                timeout=30,
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"MAX Pay verify error: {e}")
            return None
