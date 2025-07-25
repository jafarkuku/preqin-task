from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from factory import DictFactory, Factory, Faker, Iterator, LazyFunction

from app.models.investor import InvestorCreate, InvestorResponse, InvestorType


class InvestorCreateFactory(Factory):
    class Meta:
        model = InvestorCreate

    name = Faker("company")
    investor_type = Iterator(list(InvestorType))
    country = Faker("country")
    date_added = LazyFunction(lambda: datetime.now(timezone.utc))


class InvestorResponseFactory(Factory):
    class Meta:
        model = InvestorResponse

    id = LazyFunction(lambda: str(uuid4()))
    name = Faker("company")
    investor_type = Iterator(list(InvestorType))
    country = Faker("country")
    date_added = LazyFunction(lambda: datetime.now(timezone.utc))
    commitment_count = 0
    total_commitment_amount = 0.0
    created_at = LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = LazyFunction(lambda: datetime.now(timezone.utc))


class MongoInvestorFactory(DictFactory):
    class Meta:
        model = dict

    _id = LazyFunction(lambda: f"mongo_id_{uuid4().hex[:4]}")
    id = LazyFunction(lambda: f"inv-{uuid4().hex[:4]}")
    name = Faker("company")
    investor_type = Iterator([t.value for t in InvestorType])
    country = Faker("country")
    date_added = LazyFunction(lambda: datetime.now(timezone.utc).isoformat())
    commitment_count = Iterator([1, 2, 3, 4, 5])
    total_commitment_amount = LazyFunction(lambda: Decimal("1500000.0"))
    created_at = LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = LazyFunction(lambda: datetime.now(timezone.utc))
