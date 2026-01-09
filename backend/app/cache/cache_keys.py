# backend/app/cache/cache_keys.py
from uuid import UUID

class CacheKeys:
    """Cache key constants"""
    
    # User cache
    @staticmethod
    def user_by_id(user_id: UUID) -> str:
        return f"user:{user_id}"
    
    @staticmethod
    def user_by_email(email: str) -> str:
        return f"user:email:{email}"
    
    @staticmethod
    def active_users() -> str:
        return "users:active:*"
    
    # Resident cache
    @staticmethod
    def resident_by_id(resident_id: UUID) -> str:
        return f"resident:{resident_id}"
    
    @staticmethod
    def resident_by_user(user_id: UUID) -> str:
        return f"resident:user:{user_id}"
    
    @staticmethod
    def pending_approvals() -> str:
        return "residents:pending:*"
    
    # Ticket cache
    @staticmethod
    def ticket_by_id(ticket_id: UUID) -> str:
        return f"ticket:{ticket_id}"
    
    @staticmethod
    def tickets_by_resident(resident_id: UUID) -> str:
        return f"tickets:resident:{resident_id}:*"
    
    @staticmethod
    def open_tickets() -> str:
        return "tickets:open:*"
    
    # Notice cache
    @staticmethod
    def notice_by_id(notice_id: UUID) -> str:
        return f"notice:{notice_id}"
    
    @staticmethod
    def published_notices() -> str:
        return "notices:published:*"
    
    # Payment cache
    @staticmethod
    def payment_by_id(payment_id: UUID) -> str:
        return f"payment:{payment_id}"
    
    @staticmethod
    def resident_fees(resident_id: UUID) -> str:
        return f"fees:resident:{resident_id}:*"
