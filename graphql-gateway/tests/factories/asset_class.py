from typing import List, Optional

from faker import Faker

fake = Faker()


def make_asset_classes(classes: Optional[List[dict]] = None):
    """Asset Class Factory"""
    if classes is None:
        classes = [
            {
                "id": "ac-1",
                "name": "Private Equity",
                "description": "PE investments",
                "status": "active"
            },
            {
                "id": "ac-2",
                "name": "Real Estate",
                "description": "RE investments",
                "status": "active"
            }
        ]
    return classes
