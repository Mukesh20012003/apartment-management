# backend/app/events/event_bus.py
from abc import ABC, abstractmethod
from typing import Any
from enum import Enum
import json
import logging

import aio_pika
import pika

from app.config import settings

logger = logging.getLogger(__name__)

# Async exchange name
ASYNC_EXCHANGE_NAME = "apartment_events"

# Simple sync exchange name (for use from sync services)
SYNC_EXCHANGE_NAME = "app.events"

# For sync publisher
_sync_connection = None
_sync_channel = None


class EventType(str, Enum):
    """Event types in the system"""
    USER_REGISTERED = "user.registered"
    RESIDENT_APPROVED = "resident.approved"
    RESIDENT_REJECTED = "resident.rejected"
    TICKET_CREATED = "ticket.created"
    TICKET_ASSIGNED = "ticket.assigned"
    TICKET_RESOLVED = "ticket.resolved"
    NOTICE_PUBLISHED = "notice.published"
    PAYMENT_COMPLETED = "payment.completed"
    PAYMENT_FAILED = "payment.failed"


class BaseEvent(ABC):
    """Base event class"""

    event_type: EventType

    def __init__(self, data: dict):
        self.data = data
        self.timestamp = self._get_timestamp()

    def _get_timestamp(self):
        from datetime import datetime
        return datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type.value,
            "data": self.data,
            "timestamp": self.timestamp,
        }


class IEventPublisher(ABC):
    """Event publisher interface"""

    @abstractmethod
    async def publish(self, event: BaseEvent) -> None:
        ...


class RabbitMQEventPublisher(IEventPublisher):
    """RabbitMQ-based async event publisher using aio_pika"""

    def __init__(self):
        self.connection: aio_pika.RobustConnection | None = None
        self.channel: aio_pika.Channel | None = None
        self.exchange: aio_pika.Exchange | None = None

    async def connect(self):
        """Connect to RabbitMQ"""
        try:
            self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            self.channel = await self.connection.channel()
            self.exchange = await self.channel.declare_exchange(
                ASYNC_EXCHANGE_NAME,
                aio_pika.ExchangeType.TOPIC,
                durable=True,
            )
            logger.info("Connected to RabbitMQ (async publisher)")
        except Exception as e:
            logger.error(f"RabbitMQ connection failed: {e}")
            raise

    async def publish(self, event: BaseEvent) -> None:
        """Publish event to RabbitMQ (async)"""
        try:
            if not self.channel:
                await self.connect()

            message = aio_pika.Message(
                body=json.dumps(event.to_dict(), default=str).encode(),
                content_type="application/json",
            )

            await self.exchange.publish(
                message,
                routing_key=event.event_type.value,
            )

            logger.info("Event published (async): %s", event.event_type.value)
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            raise

    async def disconnect(self):
        """Disconnect from RabbitMQ"""
        if self.connection:
            await self.connection.close()


# Global async event publisher instance
event_publisher: RabbitMQEventPublisher | None = None


async def init_event_publisher():
    """Initialize async event publisher (used by lifespan)"""
    global event_publisher
    event_publisher = RabbitMQEventPublisher()
    await event_publisher.connect()


async def get_event_publisher() -> IEventPublisher:
    """Get async event publisher instance (for async endpoints/workers)"""
    if event_publisher is None:
        await init_event_publisher()
    return event_publisher


# --------------------------------------------------------------------
# Simple sync publisher helper for use from sync services like TicketService
# --------------------------------------------------------------------


def _init_sync_publisher():
    global _sync_connection, _sync_channel
    if _sync_connection is not None:
        return

    params = pika.URLParameters(settings.RABBITMQ_URL)
    _sync_connection = pika.BlockingConnection(params)
    _sync_channel = _sync_connection.channel()
    _sync_channel.exchange_declare(
        exchange=SYNC_EXCHANGE_NAME,
        exchange_type="topic",
        durable=True,
    )

    logger.info("Connected to RabbitMQ (sync publisher)")


def publish_event_sync(routing_key: str, payload: dict) -> None:
    """
    Simple sync publisher to send events from sync code (services).
    This avoids needing async/await inside TicketService.
    """
    global _sync_channel
    try:
        if _sync_channel is None:
            _init_sync_publisher()

        body = json.dumps(payload, default=str)
        _sync_channel.basic_publish(
            exchange=SYNC_EXCHANGE_NAME,
            routing_key=routing_key,
            body=body,
            properties=pika.BasicProperties(content_type="application/json"),
        )
        logger.info("Event published (sync): %s %s", routing_key, body)
    except Exception as e:
        logger.error("Sync RabbitMQ publish failed: %s", e)
