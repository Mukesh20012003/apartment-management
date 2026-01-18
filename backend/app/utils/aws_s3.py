import os
from typing import Dict, Any
from uuid import uuid4
from datetime import datetime

from app.core.exceptions import (
    S3UploadFailed, 
    S3NotConfigured, 
    S3AccessDenied, 
    S3BucketNotFound  # ✅ Your exceptions
)

class S3Service:
    """Pure Python S3 - mock for dev, real for prod"""
    
    def __init__(self):
        self.enabled = os.getenv('AWS_S3_ENABLED', 'false').lower() == 'true'
        self.bucket = os.getenv('S3_BUCKET_NAME', 'apartment-docs')
        self.mock_storage = {}  # Local file storage

    def upload_file(self, file_content: bytes, file_name: str, content_type: str = 'application/octet-stream') -> Dict[str, Any]:
        """Upload with graceful fallback"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        safe_name = f"{timestamp}_{file_name}"
        
        # Always store locally first
        self.mock_storage[safe_name] = {
            "content": file_content,
            "content_type": content_type,
            "uploaded_at": timestamp
        }
        
        if not self.enabled:
            return {
                "url": f"https://apartment.local/files/{safe_name}",
                "file_name": safe_name,
                "storage": "mock",
                "size_bytes": len(file_content)
            }
        
        if not self.bucket:
            raise S3NotConfigured()
        
        # Real S3 upload (optional)
        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError
            
            s3 = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'ap-south-1')
            )
            
            s3.put_object(
                Bucket=self.bucket,
                Key=f"documents/{safe_name}",
                Body=file_content,
                ContentType=content_type
            )
            
            return {
                "url": f"https://{self.bucket}.s3.amazonaws.com/documents/{safe_name}",
                "file_name": safe_name,
                "storage": "s3",
                "size_bytes": len(file_content)
            }
            
        except (ImportError, NoCredentialsError):
            raise S3AccessDenied(self.bucket)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                raise S3BucketNotFound(self.bucket)
            raise S3UploadFailed(f"S3 error {error_code}: {str(e)}")
    
    def list_files(self) -> list:
        """Debug: list uploaded files"""
        return list(self.mock_storage.keys())

# Global singleton
s3_service = S3Service()
