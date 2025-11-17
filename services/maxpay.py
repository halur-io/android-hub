"""
MAX PAY Service Module
Handles payment creation and API communication with Max Pay
"""
import requests
import logging
from typing import Dict, Any, Optional
from config import Config

logger = logging.getLogger(__name__)


class MaxPayService:
    """Service class for Max Pay API integration"""
    
    def __init__(self):
        self.api_url = Config.MAX_API_URL
        self.api_key = Config.MAX_API_KEY
        self.merchant_id = Config.MAX_MERCHANT_ID
        self.success_url = Config.SUCCESS_URL
        self.cancel_url = Config.CANCEL_URL
    
    def _get_headers(self) -> Dict[str, str]:
        """Generate headers for Max Pay API requests"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def create_payment(self, order_id: str, amount: float) -> Dict[str, Any]:
        """
        Create a payment request with Max Pay
        
        Args:
            order_id: Unique order identifier
            amount: Payment amount in ILS
            
        Returns:
            Dict containing payment_url or error information
        """
        try:
            # Validate inputs
            if not order_id or not isinstance(order_id, str):
                logger.error("Invalid order_id provided")
                return {
                    'error': True,
                    'message': 'Invalid order_id. Must be a non-empty string.'
                }
            
            if not amount or amount <= 0:
                logger.error(f"Invalid amount provided: {amount}")
                return {
                    'error': True,
                    'message': 'Invalid amount. Must be greater than 0.'
                }
            
            # Prepare payload for Max Pay API
            payload = {
                'merchantId': self.merchant_id,
                'amount': round(float(amount), 2),  # Ensure 2 decimal places
                'currency': 'ILS',
                'orderId': order_id,
                'successUrl': self.success_url,
                'cancelUrl': self.cancel_url
            }
            
            logger.info(f"Creating payment for order {order_id}, amount: {amount} ILS")
            
            # Send request to Max Pay API
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self._get_headers(),
                timeout=30  # 30 second timeout
            )
            
            # Check response status
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                
                # Extract payment URL from response
                payment_url = data.get('payment_url') or data.get('paymentUrl') or data.get('url')
                
                if payment_url:
                    logger.info(f"Payment created successfully for order {order_id}")
                    return {
                        'payment_url': payment_url,
                        'order_id': order_id,
                        'amount': amount,
                        'transaction_id': data.get('transactionId') or data.get('transaction_id')
                    }
                else:
                    logger.error(f"No payment URL in response: {data}")
                    return {
                        'error': True,
                        'message': 'Payment URL not found in Max Pay response'
                    }
            else:
                logger.error(f"Max Pay API error: {response.status_code} - {response.text}")
                return {
                    'error': True,
                    'message': f'Max Pay API error: {response.status_code}',
                    'details': response.text
                }
                
        except requests.exceptions.Timeout:
            logger.error("Max Pay API request timed out")
            return {
                'error': True,
                'message': 'Payment gateway timeout. Please try again.'
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error communicating with Max Pay: {str(e)}")
            return {
                'error': True,
                'message': f'Network error: {str(e)}'
            }
        
        except Exception as e:
            logger.error(f"Unexpected error in create_payment: {str(e)}")
            return {
                'error': True,
                'message': f'Unexpected error: {str(e)}'
            }
    
    def verify_payment(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """
        Verify a payment status with Max Pay (optional method)
        
        Args:
            transaction_id: Transaction identifier from Max Pay
            
        Returns:
            Dict containing payment details or None
        """
        try:
            verify_url = f"{self.api_url}/{transaction_id}"
            
            response = requests.get(
                verify_url,
                headers=self._get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            
            return None
            
        except Exception as e:
            logger.error(f"Error verifying payment: {str(e)}")
            return None
