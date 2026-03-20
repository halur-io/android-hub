"""
SMS Routing Configuration — standalone equivalent of sms_encryption routing.

Provides a simple routing configuration layer that determines which SMS
provider to use as primary and which as failover, without requiring
database tables or encrypted credentials from the parent project.

Usage::

    from standalone_order_service.sms_routing import SmsRoutingConfig

    routing = SmsRoutingConfig(
        primary='twilio',
        failover='sms4free',
        failover_enabled=True,
    )

    # Or load from environment
    routing = SmsRoutingConfig.from_env()

    # Use with sms_helpers
    from standalone_order_service.sms_helpers import (
        create_twilio_sender_from_env,
        create_sms4free_sender_from_env,
        create_failover_sender,
    )
    primary_fn = create_twilio_sender_from_env()
    secondary_fn = create_sms4free_sender_from_env()
    send_sms = routing.build_sender(primary_fn, secondary_fn)
"""

import logging
import os
from typing import Callable, Dict, Optional

logger = logging.getLogger(__name__)


class SmsRoutingConfig:
    """
    Lightweight SMS routing configuration.

    Replaces the database-backed ``SmsRoutingConfig`` + ``sms_encryption``
    modules from the parent project with a simple in-memory or env-var
    configuration.
    """

    VALID_PROVIDERS = ('twilio', 'sms4free')

    def __init__(
        self,
        primary: str = 'twilio',
        failover: Optional[str] = 'sms4free',
        failover_enabled: bool = True,
        max_retries: int = 2,
    ):
        if primary not in self.VALID_PROVIDERS:
            raise ValueError(f"primary must be one of {self.VALID_PROVIDERS}")
        if failover and failover not in self.VALID_PROVIDERS:
            raise ValueError(f"failover must be one of {self.VALID_PROVIDERS} or None")
        self.primary = primary
        self.failover = failover
        self.failover_enabled = failover_enabled
        self.max_retries = max_retries

    @classmethod
    def from_env(cls) -> 'SmsRoutingConfig':
        """
        Load routing config from environment variables.

        | Variable | Default | Description |
        |---|---|---|
        | ``SMS_PRIMARY_PROVIDER`` | ``twilio`` | Primary SMS provider |
        | ``SMS_FAILOVER_PROVIDER`` | ``sms4free`` | Failover provider |
        | ``SMS_FAILOVER_ENABLED`` | ``true`` | Enable failover |
        | ``SMS_MAX_RETRIES`` | ``2`` | Max retry count |
        """
        primary = os.environ.get('SMS_PRIMARY_PROVIDER', 'twilio').strip().lower()
        failover = os.environ.get('SMS_FAILOVER_PROVIDER', 'sms4free').strip().lower()
        failover_enabled = os.environ.get('SMS_FAILOVER_ENABLED', 'true').strip().lower() in ('true', '1', 'yes')
        max_retries = int(os.environ.get('SMS_MAX_RETRIES', '2'))
        if primary not in cls.VALID_PROVIDERS:
            logger.warning(f"Invalid SMS_PRIMARY_PROVIDER '{primary}', defaulting to 'twilio'")
            primary = 'twilio'
        if failover and failover not in cls.VALID_PROVIDERS:
            failover = None
        return cls(primary=primary, failover=failover, failover_enabled=failover_enabled, max_retries=max_retries)

    def to_dict(self) -> Dict:
        return {
            'primary_provider': self.primary,
            'failover_provider': self.failover,
            'failover_enabled': self.failover_enabled,
            'max_retries': self.max_retries,
        }

    def build_sender(
        self,
        twilio_fn: Optional[Callable] = None,
        sms4free_fn: Optional[Callable] = None,
    ) -> Optional[Callable]:
        """
        Build a ``(phone, message) -> bool`` sender based on routing config.

        Selects the primary and failover callables based on the configured
        provider names, and wraps them with failover logic.

        Parameters
        ----------
        twilio_fn : callable, optional
            Twilio sender (from ``create_twilio_sender`` or ``create_twilio_sender_from_env``).
        sms4free_fn : callable, optional
            SMS4Free sender (from ``create_sms4free_sender`` or ``create_sms4free_sender_from_env``).

        Returns
        -------
        callable or None
            A ``(phone, message) -> bool`` function, or ``None`` if no provider is available.
        """
        from standalone_order_service.sms_helpers import create_failover_sender

        providers = {
            'twilio': twilio_fn,
            'sms4free': sms4free_fn,
        }

        primary_fn = providers.get(self.primary)
        failover_fn = providers.get(self.failover) if self.failover_enabled and self.failover else None

        if primary_fn and failover_fn:
            return create_failover_sender(primary_fn, failover_fn)
        return primary_fn or failover_fn
