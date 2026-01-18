# backend/app/core/exceptions.py
from fastapi import HTTPException, status

class AppException(HTTPException):
    """Base application exception"""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class UserAlreadyExists(AppException):
    def __init__(self):
        super().__init__(
            detail="User with this email already exists",
            status_code=status.HTTP_409_CONFLICT
        )

class InvalidCredentials(AppException):
    def __init__(self):
        super().__init__(
            detail="Invalid email or password",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class UserNotFound(AppException):
    def __init__(self):
        super().__init__(
            detail="User not found",
            status_code=status.HTTP_404_NOT_FOUND
        )

class UnauthorizedAccess(AppException):
    def __init__(self):
        super().__init__(
            detail="Unauthorized access",
            status_code=status.HTTP_403_FORBIDDEN
        )

class InvalidData(AppException):
    def __init__(self, detail: str = "Invalid data"):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

# 🔥 NEW S3 EXCEPTIONS
class S3UploadFailed(AppException):
    def __init__(self, error: str):
        super().__init__(
            detail=f"S3 upload failed: {error}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class S3NotConfigured(AppException):
    def __init__(self):
        super().__init__(
            detail="S3 storage not configured",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

class S3AccessDenied(AppException):
    def __init__(self, bucket: str):
        super().__init__(
            detail=f"S3 access denied for bucket: {bucket}",
            status_code=status.HTTP_403_FORBIDDEN
        )

class S3BucketNotFound(AppException):
    def __init__(self, bucket: str):
        super().__init__(
            detail=f"S3 bucket not found: {bucket}",
            status_code=status.HTTP_404_NOT_FOUND
        )