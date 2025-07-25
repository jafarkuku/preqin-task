"""
GraphQL Schema package for Investment Platform.
"""

from .base import Query, schema
from .commitments import CommitmentBreakdown, CommitmentDetail
from .investors import InvestorDetail, InvestorList

__all__ = [
    "Query",
    "schema",
    "InvestorDetail",
    "InvestorList",
    "CommitmentDetail",
    "CommitmentBreakdown",
]
