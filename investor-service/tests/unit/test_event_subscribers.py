import json
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.services.event_subscriber import EventSubscriber
from tests.factories.investor import InvestorResponseFactory


class TestEventSubscriber:
    """Test cases for event subscriber."""

    @pytest.mark.asyncio
    async def test_handle_commitment_created_event(self):
        """Test handling commitment created event."""

        subscriber = EventSubscriber()
        mock_repo = AsyncMock()

        existing_investor = InvestorResponseFactory.build(
            id="inv-1",
            commitment_count=2,
            total_commitment_amount=1000000.0,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        mock_repo.get_investor_by_id.return_value = existing_investor
        mock_repo.update_commitment_metrics.return_value = True

        event_data = {
            "event_type": "commitment_created",
            "investor_id": "inv-1",
            "amount": 500000.0
        }

        message = {
            "data": json.dumps(event_data).encode("utf-8")
        }

        await subscriber._handle_message(message, mock_repo)

        mock_repo.get_investor_by_id.assert_called_once_with("inv-1")
        mock_repo.update_commitment_metrics.assert_called_once_with(
            "inv-1", 3, Decimal("1500000.0")
        )

    @pytest.mark.asyncio
    async def test_handle_commitment_created_investor_not_found(self):
        """Test handling commitment created event when investor not found."""
        subscriber = EventSubscriber()
        mock_repo = AsyncMock()
        mock_repo.get_investor_by_id.return_value = None

        event_data = {
            "event_type": "commitment_created",
            "investor_id": "non-existent",
            "amount": 500000.0
        }

        message = {
            "data": json.dumps(event_data).encode("utf-8")
        }

        await subscriber._handle_message(message, mock_repo)

        mock_repo.get_investor_by_id.assert_called_once_with("non-existent")
        mock_repo.update_commitment_metrics.assert_not_called()
