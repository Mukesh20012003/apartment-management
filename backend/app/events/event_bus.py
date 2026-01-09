# backend/app/events/event_bus.py
from abc import ABC, abstractmethod
from typing import Callable, List, Any
from enum import Enum
import json
import logging
from app.config import settings
import aio_pika

logger = logging.getLogger(__name__)

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
            "timestamp": self.timestamp
        }

class IEventPublisher(ABC):
    """Event publisher interface"""
    
    @abstractmethod
    async def publish(self, event: BaseEvent) -> None:
        pass

class RabbitMQEventPublisher(IEventPublisher):
    """RabbitMQ-based event publisher"""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None
    
    async def connect(self):
        """Connect to RabbitMQ"""
        try:
            self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            self.channel = await self.connection.channel()
            self.exchange = await self.channel.declare_exchange(
                "apartment_events",
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )
            logger.info("Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"RabbitMQ connection failed: {e}")
            raise
    
    async def publish(self, event: BaseEvent) -> None:
        """Publish event to RabbitMQ"""
        try:
            if not self.channel:
                await self.connect()
            
            message = aio_pika.Message(
                body=json.dumps(event.to_dict()).encode(),
                content_type="application/json"
            )
            
            await self.exchange.publish(
                message,
                routing_key=event.event_type.value
            )
            
            logger.info(f"Event published: {event.event_type.value}")
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from RabbitMQ"""
        if self.connection:
            await self.connection.close()

# Global event publisher instance
event_publisher: RabbitMQEventPublisher = None

async def init_event_publisher():
    """Initialize event publisher"""
    global event_publisher
    event_publisher = RabbitMQEventPublisher()
    await event_publisher.connect()

async def get_event_publisher() -> IEventPublisher:
    """Get event publisher instance"""
    if event_publisher is None:
        await init_event_publisher()
    return event_publisher
