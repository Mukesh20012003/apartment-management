from celery import Celery
import smtplib
from email.mime.text import MimeText

celery_app = Celery('tasks', broker='redis://localhost:6379')

@celery_app.task
def send_welcome_email(user_id: str, email: str, flat_number: str):
    """Async welcome email"""
    msg = MimeText(f"Welcome to your flat {flat_number}!")
    msg['Subject'] = 'Welcome to Apartment Management'
    msg['From'] = 'no-reply@apartments.com'
    msg['To'] = email
    
    # SMTP config
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your-email@gmail.com', 'your-app-password')
        server.send_message(msg)

@celery_app.task
def send_payment_reminder(fee_id: str, resident_email: str):
    """Async payment reminder"""
    pass  # Implementation
