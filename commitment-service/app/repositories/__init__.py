"""
Repository factory and dependency injection.
"""

from app.database.connection import get_database
from app.repositories.commitment_repository import CommitmentRepository


def get_commitment_repository() -> CommitmentRepository:
    """
    Get a commitment repository instance using aiosqlite.

    This function is used for dependency injection in FastAPI endpoints.

    Returns:
        CommitmentRepository: Repository instance with async database connection
    """
    connection = get_database()
    return CommitmentRepository(connection)


# Export the main function for easy importing
__all__ = ["get_commitment_repository"]
