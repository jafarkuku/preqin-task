from typing import Any, Dict, List, Optional, cast

from faker import Faker

fake = Faker()


def make_investors(
    count: int = 2,
    overrides: Optional[List[Dict[str, Any]]] = None,
    meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate a fake investors response payload.
    """
    investors = []
    overrides = overrides or []

    for i in range(count):
        base = {
            "id": f"inv-{i + 1}",
            "name": fake.company(),
            "investor_type": fake.random_element(["Pension Fund", "Insurance Company", "Family Office"]),
            "country": fake.country(),
            "date_added": fake.date(),
            "commitment_count": fake.random_int(min=1, max=5),
            "total_commitment_amount": fake.random_number(digits=6),
            "created_at": fake.date_time().isoformat(),
            "updated_at": fake.date_time().isoformat()
        }

        if i < len(overrides):
            base.update(overrides[i])

        investors.append(base)

    total_commitment_amount = sum(
        cast(float, i["total_commitment_amount"]) for i in investors if "total_commitment_amount" in i
    )

    default_meta = {
        "total_commitment_amount": total_commitment_amount,
        "total": len(investors),
        "page": 1,
        "size": 20,
        "total_pages": 1
    }

    return {
        "investors": investors,
        **(meta or default_meta)
    }
