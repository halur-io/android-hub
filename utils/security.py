"""
Security Utilities for Max Pay Integration
Handles webhook signature verification using HMAC SHA256
"""
import hmac
import hashlib
import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def verify_signature(data: bytes, signature: str, secret: str) -> bool:
    """
    Verify webhook signature using HMAC SHA256
    
    Args:
        data: Raw request body as bytes
        signature: Signature from Max Pay webhook header
        secret: Webhook secret key
        
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        if not signature or not secret:
            logger.warning("Missing signature or secret for verification")
            return False
        
        # Generate expected signature
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            data,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures (constant-time comparison to prevent timing attacks)
        is_valid = hmac.compare_digest(signature, expected_signature)
        
        if not is_valid:
            logger.warning(f"Invalid signature. Expected: {expected_signature[:8]}..., Got: {signature[:8]}...")
        
        return is_valid
        
    except Exception as e:
        logger.error(f"Error verifying signature: {str(e)}")
        return False


def verify_signature_sha256_base64(data: bytes, signature: str, secret: str) -> bool:
    """
    Alternative signature verification using base64-encoded SHA256
    (Some payment providers use this format)
    
    Args:
        data: Raw request body as bytes
        signature: Base64-encoded signature from webhook header
        secret: Webhook secret key
        
    Returns:
        True if signature is valid, False otherwise
    """
    import base64
    
    try:
        if not signature or not secret:
            return False
        
        # Generate expected signature
        expected_signature = base64.b64encode(
            hmac.new(
                secret.encode('utf-8'),
                data,
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        
        # Compare signatures
        is_valid = hmac.compare_digest(signature, expected_signature)
        
        return is_valid
        
    except Exception as e:
        logger.error(f"Error verifying base64 signature: {str(e)}")
        return False


def extract_signature_from_header(header_value: str, prefix: str = 'sha256=') -> str:
    """
    Extract signature value from header
    Some webhooks send signatures like "sha256=abc123..."
    
    Args:
        header_value: Full header value
        prefix: Prefix to remove (default: 'sha256=')
        
    Returns:
        Extracted signature without prefix
    """
    if not header_value:
        return ''
    
    if header_value.startswith(prefix):
        return header_value[len(prefix):]
    
    return header_value
