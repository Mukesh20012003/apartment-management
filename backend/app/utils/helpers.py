from datetime import datetime, timedelta
from typing import Dict, Any
import uuid
import hashlib

def generate_transaction_id(prefix: str = "TXN") -> str:
    """Generate unique transaction ID"""
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"

def calculate_age(dob: str) -> int:
    """Calculate age from DOB string"""
    birth_date = datetime.fromisoformat(dob)
    today = datetime.utcnow()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def format_indian_currency(amount: float) -> str:
    """Format as INR"""
    return f"₹{amount:,.2f}"

def hash_password(password: str) -> str:
    """Simple hash for demo"""
    return hashlib.sha256(password.encode()).hexdigest()[:32]

def parse_month_year(month_year: str) -> tuple:
    """Parse MM-YYYY → (month, year)"""
    month, year = month_year.split("-")
    return int(month), int(year)
