import logging
from typing import Optional

import redis.asyncio as redis

from app.config import settings
from app.models.commitment import CommitmentCreatedEvent

logger = logging.getLogger(__name__)


class EventPublisher:
    """
        Redis event publisher
    """

    def __init__(self) -> None:
        self.redis_url = settings.redis_url
        self._redis: Optional[redis.Redis] = None

    async def connect(self):
        """Connect to Redis."""
        self._redis = redis.from_url(self.redis_url)

        if self._redis is None:
            raise RuntimeError("Failed to create Redis connection")

        await self._redis.ping()
        logger.info("Connected to Redis for event publishing")

    async def disconnect(self):
        """Disconnect from Redis."""
        if self._redis:
            await self._redis.close()

    async def publish_commitment_created(self, commitment_data: dict):
        """Publish commitment created event."""
        try:
            event = CommitmentCreatedEvent(
                commitment_id=commitment_data["id"],
                investor_id=commitment_data["investor_id"],
                asset_class_id=commitment_data["asset_class_id"],
                amount=commitment_data["amount"],
                currency=commitment_data["currency"]
            )

            if self._redis is None:
                raise RuntimeError("No Redis connection found")

            await self._redis.publish(
                "investor_updates",
                event.model_dump_json()
            )

            logger.info("Published commitment_created event for investor %s",
                        event.investor_id)

        except (redis.RedisError, redis.ConnectionError, redis.TimeoutError) as e:
            logger.error("Redis error in event publisher: %s", e)
        finally:
            logger.info("Stopped publishing events")


event_publisher = EventPublisher()
