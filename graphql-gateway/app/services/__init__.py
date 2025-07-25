"""
Router module initialization.
"""

from .asset_class_service import (close_asset_class_client,
                                  get_asset_class_client)
from .commitment_service import close_commitment_client, get_commitment_client
from .investor_service import close_investor_client, get_investor_client

__all__ = ["get_asset_class_client", "close_asset_class_client",
           "get_investor_client", "close_commitment_client", "get_commitment_client", "close_investor_client"]
