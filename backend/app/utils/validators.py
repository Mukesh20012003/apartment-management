from pydantic import validator, ValidationError
from typing import Any
import re
from uuid import UUID

class CustomValidators:
    @staticmethod
    def flat_number(v: str) -> str:
        if not re.match(r'^[A-Z]\d{1,3}[A-Z]?$', v):  # B201, A1
            raise ValueError("Flat format: Block + Number (e.g. B201)")
        return v
    
    @staticmethod
    def phone_number(v: str) -> str:
        if not re.match(r'^\d{10}$', v):
            raise ValueError("Phone must be 10 digits")
        return v
    
    @staticmethod
    def positive_int(v: int) -> int:
        if v <= 0:
            raise ValueError("Value must be positive")
        return v
    
    @staticmethod
    def valid_uuid(v: str) -> UUID:
        try:
            return UUID(v)
        except ValueError:
            raise ValueError("Invalid UUID format")
