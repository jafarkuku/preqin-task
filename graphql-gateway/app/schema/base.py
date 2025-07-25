import strawberry

from .commitments import CommitmentQueries
from .investors import InvestorQueries


@strawberry.type
class Query(InvestorQueries, CommitmentQueries):
    """
    Root query type that composes all query modules.

    Inherits from:
    - InvestorQueries: investors()
    - CommitmentQueries: commitment_breakdown()
    """


schema = strawberry.Schema(query=Query)
