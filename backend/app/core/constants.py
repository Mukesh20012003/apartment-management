# backend/app/core/constants.py
from enum import Enum

class UserRole(str, Enum):
    """User roles in the system"""
    RESIDENT = "resident"
    SECURITY = "security"
    ASSOCIATION_STAFF = "association_staff"
    ADMIN = "admin"

class ResidentStatus(str, Enum):
    """Resident approval status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    INACTIVE = "inactive"

class TicketStatus(str, Enum):
    """Maintenance ticket status"""
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(str, Enum):
    """Ticket priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class PaymentStatus(str, Enum):
    """Payment status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class NoticeStatus(str, Enum):
    """Notice publication status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
