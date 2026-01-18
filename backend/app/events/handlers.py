from app.events.base_event import BaseEvent
from app.tasks.notification_tasks import send_welcome_email

class EventHandler:
    @staticmethod
    def handle_user_registered(event: BaseEvent):
        """Handle new resident registration"""
        data = event.data
        send_welcome_email.delay(
            data['user_id'], 
            data['email'], 
            data['flat_number']
        )

    @staticmethod
    def handle_notice_published(event: BaseEvent):
        """Handle notice publication"""
        pass  # Email all residents
