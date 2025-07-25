"""
Repository factory and dependency injection.
"""

from app.database.connection import get_investors_collection
from app.repositories.investor_repository import InvestorRepository


def get_investor_repository() -> InvestorRepository:
    """
    Get an investor repository instance using Motor (async MongoDB).

    This function is used for dependency injection in FastAPI endpoints.

    Returns:
        InvestorRepository: Repository instance with async database connection
    """
    collection = get_investors_collection()
    return InvestorRepository(collection)


# Export the main function for easy importing
__all__ = ["get_investor_repository"]
