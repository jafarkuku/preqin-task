from typing import List, Optional

from faker import Faker

fake = Faker()


def make_commitments(commitments: Optional[List[dict]] = None):
    """Commitments factory"""
    if commitments is None:
        commitments = [
            {
                "id": "com-1",
                "investor_id": "inv-1",
                "asset_class_id": "ac-1",
                "amount": 1_000_000.0,
                "currency": "USD",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": "com-2",
                "investor_id": "inv-1",
                "asset_class_id": "ac-2",
                "amount": 500_000.0,
                "currency": "USD",
                "created_at": "2024-01-02T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z"
            }
        ]

    total_amount = sum(float(c.get("amount", 0)) for c in commitments)

    return {
        "commitments": commitments,
        "total": len(commitments),
        "total_amount": total_amount,
        "page": 1,
        "size": 100,
        "total_pages": 1,
        "has_next": False,
        "has_prev": False
    }
