"""
Database module initialization.
"""

from .connection import (
    connect_to_database,
    close_database_connection,
    get_database,
    health_check
)

__all__ = [
    "connect_to_database",
    "close_database_connection",
    "get_database",
    "health_check"
]
