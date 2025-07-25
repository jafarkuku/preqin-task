import asyncio
import json
import logging
from decimal import Decimal
from typing import Optional

import redis.asyncio as redis
from redis.asyncio.client import PubSub

from app.config import settings
from app.repositories.investor_repository import InvestorRepository

logger = logging.getLogger(__name__)


class EventSubscriber:
    def __init__(self) -> None:
        self.redis_url = settings.redis_url
        self._redis: Optional[redis.Redis] = None
        self._pubsub: Optional[PubSub] = None
        self._running = False

    async def connect(self) -> None:
        """Connect to Redis and subscribe to channels."""
        self._redis = redis.from_url(self.redis_url)

        if self._redis is None:
            raise RuntimeError("Failed to create Redis connection")

        self._pubsub = self._redis.pubsub()
        if self._pubsub is None:
            raise RuntimeError("Failed to create Redis PubSub")

        await self._pubsub.subscribe("investor_updates")
        logger.info("Subscribed to investor_updates channel")

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        self._running = False
        if self._pubsub:
            await self._pubsub.unsubscribe("investor_updates")
            await self._pubsub.close()
        if self._redis:
            await self._redis.close()

    async def start_listening(self, investor_repo: InvestorRepository) -> None:
        """Start listening for events."""
        self._running = True
        logger.info("Started listening for investor update events")

        try:
            while self._running:
                if not self._pubsub:
                    logger.error("PubSub not connected")
                    break

                message = await self._pubsub.get_message(ignore_subscribe_messages=True)

                if message:
                    await self._handle_message(message, investor_repo)

                await asyncio.sleep(0.01)

        except (redis.RedisError, redis.ConnectionError, redis.TimeoutError) as e:
            logger.error("Redis error in event listener: %s", e)
        except asyncio.CancelledError:
            logger.info("Event listener cancelled")
        finally:
            logger.info("Stopped listening for events")

    async def _handle_message(self, message: dict[str, bytes], investor_repo: InvestorRepository) -> None:
        """Handle incoming event messages."""
        try:
            event_data: dict[str, str | float] = json.loads(message['data'])
            event_type = event_data.get('event_type')
            investor_id = event_data.get('investor_id')

            if not investor_id:
                logger.warning("Event missing investor_id: %s", event_data)
                return

            if event_type == "commitment_created":
                await self._handle_commitment_created(event_data, investor_repo)
            else:
                logger.warning("Unknown event type: %s", event_type)

        except json.JSONDecodeError as e:
            logger.error("JSON decode error handling message: %s", e)
        except (KeyError, ValueError, TypeError) as e:
            logger.error("Data error handling message: %s", e)

    async def _handle_commitment_created(self, event_data: dict[str, str | float], investor_repo: InvestorRepository) -> None:
        """Handle commitment created event."""
        try:
            investor_id = str(event_data['investor_id'])
            amount = Decimal(event_data['amount'])

            # Get current investor data
            investor = await investor_repo.get_investor_by_id(investor_id)
            if not investor:
                logger.warning(
                    "Investor not found for commitment event: %s", investor_id)
                return

            new_count = investor.commitment_count + 1
            new_total = Decimal(str(investor.total_commitment_amount)) + amount

            success = await investor_repo.update_commitment_metrics(
                investor_id, new_count, new_total
            )

            if success:
                logger.info("Updated investor %s: count=%d, total=%.2f",
                            investor_id, new_count, new_total)
            else:
                logger.error(
                    "Failed to update investor metrics for %s", investor_id)

        except (KeyError, ValueError, TypeError) as e:
            logger.error("Data error handling commitment_created: %s", e)


# Global instance
event_subscriber = EventSubscriber()
