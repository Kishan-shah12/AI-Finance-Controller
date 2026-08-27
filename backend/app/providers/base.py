from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from app.schemas.financial import Order, Payment, Settlement

class PaymentProvider(ABC):
    """
    Abstract base class for all payment providers.
    The reconciliation engine expects data matching the canonical schemas in app.schemas.financial.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the string identifier for this provider."""
        pass

    @abstractmethod
    def get_status(self) -> dict:
        """
        Return a status dictionary containing configured, reachable, and capabilities.
        Must NEVER expose credentials.
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Perform a harmless read-only test call.
        Returns True if successful, False otherwise.
        """
        pass

    @abstractmethod
    def fetch_data(self, limit: int = 100) -> Tuple[List[Order], List[Payment], List[Settlement]]:
        """
        Fetch recent data from the provider and normalize it to canonical schemas.
        Returns (orders, payments, settlements).
        """
        pass
