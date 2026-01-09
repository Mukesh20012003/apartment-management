# backend/app/events/events.py
from app.events.event_bus import BaseEvent, EventType
from typing import Optional
from uuid import UUID

class UserRegisteredEvent(BaseEvent):
    event_type = EventType.USER_REGISTERED

class ResidentApprovedEvent(BaseEvent):
    event_type = EventType.RESIDENT_APPROVED

class ResidentRejectedEvent(BaseEvent):
    event_type = EventType.RESIDENT_REJECTED

class TicketCreatedEvent(BaseEvent):
    event_type = EventType.TICKET_CREATED

class TicketAssignedEvent(BaseEvent):
    event_type = EventType.TICKET_ASSIGNED

class TicketResolvedEvent(BaseEvent):
    event_type = EventType.TICKET_RESOLVED

class NoticePublishedEvent(BaseEvent):
    event_type = EventType.NOTICE_PUBLISHED

class PaymentCompletedEvent(BaseEvent):
    event_type = EventType.PAYMENT_COMPLETED

class PaymentFailedEvent(BaseEvent):
    event_type = EventType.PAYMENT_FAILED
