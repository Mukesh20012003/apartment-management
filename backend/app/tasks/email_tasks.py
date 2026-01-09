# backend/app/tasks/email_tasks.py
from celery import shared_task
from app.tasks.celery_app import celery_app
from app.config import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def send_email_task(self, to_email: str, subject: str, body: str, html_body: str = None):
    """Send email using SMTP"""
    try:
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_USER
        msg["To"] = to_email

        msg.attach(MIMEText(body, "plain"))
        if html_body:
            msg.attach(MIMEText(html_body, "html"))

        server.sendmail(settings.SMTP_USER, [to_email], msg.as_string())
        server.quit()

        logger.info(f"Email sent to {to_email}")
        return {"status": "success"}

    except Exception as exc:
        logger.error(f"Email send failed: {exc}")
        raise self.retry(exc=exc, countdown=60)

@celery_app.task
def send_user_registration_email(user_email: str, user_name: str):
    """Send registration confirmation email"""
    subject = "Welcome to Apartment Management System"
    body = f"Hi {user_name},\n\nWelcome! Your account has been created."
    
    send_email_task.delay(user_email, subject, body)

@celery_app.task
def send_resident_approval_email(resident_email: str, resident_name: str):
    """Send resident approval email"""
    subject = "Your Resident Registration has been Approved"
    body = f"Hi {resident_name},\n\nYour registration has been approved."
    
    send_email_task.delay(resident_email, subject, body)

@celery_app.task
def send_ticket_assignment_email(staff_email: str, ticket_number: str):
    """Send ticket assignment notification"""
    subject = f"Ticket {ticket_number} has been assigned to you"
    body = f"A new maintenance ticket has been assigned to you."
    
    send_email_task.delay(staff_email, subject, body)
