# backend/app/tasks/celery_app.py
from celery import Celery
from celery.schedules import crontab
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "apartment_management",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.email_tasks",
        "app.tasks.notification_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    broker_connection_retry_on_startup=True,
    result_backend_transport_options={
        "master_name": "mymaster",
        "retry_on_timeout": True
    }
)

# Scheduled tasks
celery_app.conf.beat_schedule = {
    "send-pending-payment-reminders": {
        "task": "app.tasks.notification_tasks.send_payment_reminder",
        "schedule": crontab(hour=10, minute=0),  # Daily at 10 AM
    },
    "check-overdue-fees": {
        "task": "app.tasks.notification_tasks.check_overdue_fees",
        "schedule": crontab(hour=0, minute=0),  # Daily at midnight
    },
}

@celery_app.task(bind=True)
def debug_task(self):
    logger.info(f"Request: {self.request!r}")
