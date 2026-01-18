# backend/app/services/notification_service.py
from app.tasks.email_tasks import send_email_task
from app.tasks.notification_tasks import send_sms_notification
from app.core.constants import UserRole
from sqlalchemy.orm import Session
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """Handle all notifications (email, SMS, in-app)"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def notify_resident_registration_confirmation(self, user: User):
        """Send registration confirmation email"""
        send_email_task.delay(
            to_email=user.email,
            subject="Welcome to Apartment Management System",
            body=f"Hi {user.full_name},\n\nYour account has been created successfully. Please wait for admin approval to access resident features.",
            html_body=self._get_registration_html(user)
        )
        logger.info(f"Registration email sent to {user.email}")
    
    def notify_resident_approval(self, resident):
        """Send approval notification to resident"""
        user = self.db.query(User).filter(User.id == resident.user_id).first()
        if not user:
            return
        
        send_email_task.delay(
            to_email=user.email,
            subject="🎉 Your Resident Registration has been Approved!",
            body=f"Hi {user.full_name},\n\nCongratulations! Your registration has been approved. You now have full access to the platform.",
            html_body=self._get_approval_html(user, resident)
        )
        logger.info(f"Approval notification sent to {user.email}")
    
    def notify_resident_rejection(self, resident, reason: str):
        """Send rejection notification"""
        user = self.db.query(User).filter(User.id == resident.user_id).first()
        if not user:
            return
        
        send_email_task.delay(
            to_email=user.email,
            subject="Update on Your Resident Registration",
            body=f"Hi {user.full_name},\n\nUnfortunately, your registration could not be approved.\n\nReason: {reason}\n\nPlease contact the association for more details.",
            html_body=self._get_rejection_html(user, reason)
        )
        logger.info(f"Rejection notification sent to {user.email}")
    
    def notify_ticket_assignment(self, ticket, assigned_user: User):
        """Notify staff member when ticket is assigned"""
        send_email_task.delay(
            to_email=assigned_user.email,
            subject=f"New Maintenance Ticket Assigned: {ticket.ticket_number}",
            body=f"Hi {assigned_user.full_name},\n\nA new maintenance ticket has been assigned to you:\n\nTicket: {ticket.ticket_number}\nFlat: {ticket.flat_id}\nTitle: {ticket.title}\nPriority: {ticket.priority}\n\nPlease address this as soon as possible.",
            html_body=self._get_ticket_assignment_html(ticket, assigned_user)
        )
        logger.info(f"Ticket assignment notification sent to {assigned_user.email}")
    
    def notify_ticket_update(self, ticket, resident):
        """Notify resident when ticket status changes"""
        user = self.db.query(User).filter(User.id == resident.user_id).first()
        if not user:
            return
        
        send_email_task.delay(
            to_email=user.email,
            subject=f"Update on Your Maintenance Ticket: {ticket.ticket_number}",
            body=f"Hi {user.full_name},\n\nYour maintenance ticket has been updated:\n\nStatus: {ticket.status}\nNotes: {ticket.resolution_notes}",
            html_body=self._get_ticket_update_html(ticket, user)
        )
        logger.info(f"Ticket update notification sent to {user.email}")
    
    def notify_payment_due_reminder(self, resident, fee):
        """Send payment due reminder"""
        user = self.db.query(User).filter(User.id == resident.user_id).first()
        if not user:
            return
        
        send_email_task.delay(
            to_email=user.email,
            subject=f"⏰ Monthly Fee Due Reminder - {fee.month_year}",
            body=f"Hi {user.full_name},\n\nThis is a reminder that your monthly fee for {fee.month_year} is due.\n\nAmount: ₹{fee.base_amount + fee.maintenance_charge + fee.water_charge}\nDue Date: {fee.due_date}",
            html_body=self._get_payment_reminder_html(user, fee)
        )
        logger.info(f"Payment reminder sent to {user.email}")
    
    def notify_notice_published(self, notice, residents: list):
        """Broadcast notice to all residents"""
        for resident in residents:
            user = self.db.query(User).filter(User.id == resident.user_id).first()
            if not user:
                continue
            
            send_email_task.delay(
                to_email=user.email,
                subject=f"📢 New Notice: {notice.title}",
                body=f"Hi {user.full_name},\n\nA new notice has been published:\n\n{notice.content}",
                html_body=self._get_notice_html(notice, user)
            )
        
        logger.info(f"Notice {notice.id} published to {len(residents)} residents")
    
    # HTML Template Builders
    def _get_registration_html(self, user: User) -> str:
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Welcome to Apartment Management System!</h2>
                <p>Hi {user.full_name},</p>
                <p>Your account has been created successfully.</p>
                <p>Your account will be activated once the administrator approves your resident registration.</p>
                <p>Best regards,<br>Apartment Management Team</p>
            </body>
        </html>
        """
    
    def _get_approval_html(self, user: User, resident) -> str:
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: green;">🎉 Congratulations!</h2>
                <p>Hi {user.full_name},</p>
                <p>Your resident registration has been <strong>approved</strong>.</p>
                <p>You now have full access to the Apartment Management System.</p>
                <p>You can now:</p>
                <ul>
                    <li>Raise and track maintenance tickets</li>
                    <li>View community notices</li>
                    <li>Track and pay monthly fees</li>
                    <li>Manage your resident profile</li>
                </ul>
                <p><a href="http://your-app-url/dashboard" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Login Now</a></p>
                <p>Best regards,<br>Apartment Management Team</p>
            </body>
        </html>
        """
    
    def _get_rejection_html(self, user: User, reason: str) -> str:
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Registration Status Update</h2>
                <p>Hi {user.full_name},</p>
                <p>Unfortunately, your resident registration could not be approved at this time.</p>
                <p><strong>Reason:</strong> {reason}</p>
                <p>Please contact the association office for more details and to understand the next steps.</p>
                <p>Best regards,<br>Apartment Management Team</p>
            </body>
        </html>
        """
    
    def _get_ticket_assignment_html(self, ticket, user: User) -> str:
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>New Maintenance Ticket Assigned</h2>
                <p>Hi {user.full_name},</p>
                <p>A new maintenance ticket has been assigned to you:</p>
                <table style="border: 1px solid #ddd; padding: 10px;">
                    <tr><td><strong>Ticket Number:</strong></td><td>{ticket.ticket_number}</td></tr>
                    <tr><td><strong>Title:</strong></td><td>{ticket.title}</td></tr>
                    <tr><td><strong>Priority:</strong></td><td>{ticket.priority}</td></tr>
                    <tr><td><strong>Flat:</strong></td><td>{ticket.flat_id}</td></tr>
                </table>
                <p>Please address this as soon as possible.</p>
                <p>Best regards,<br>Apartment Management Team</p>
            </body>
        </html>
        """
    
    def _get_ticket_update_html(self, ticket, user: User) -> str:
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Maintenance Ticket Update</h2>
                <p>Hi {user.full_name},</p>
                <p>Your maintenance ticket <strong>{ticket.ticket_number}</strong> has been updated:</p>
                <p><strong>Status:</strong> {ticket.status.upper()}</p>
                <p><strong>Notes:</strong> {ticket.resolution_notes or 'No notes added'}</p>
                <p>Best regards,<br>Apartment Management Team</p>
            </body>
        </html>
        """
    
    def _get_payment_reminder_html(self, user: User, fee) -> str:
        total_amount = fee.base_amount + fee.maintenance_charge + fee.water_charge + fee.penalty_amount
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #ff6b00;">⏰ Payment Due Reminder</h2>
                <p>Hi {user.full_name},</p>
                <p>This is a friendly reminder that your monthly fee for <strong>{fee.month_year}</strong> is due.</p>
                <table style="border: 1px solid #ddd; padding: 10px;">
                    <tr><td><strong>Month:</strong></td><td>{fee.month_year}</td></tr>
                    <tr><td><strong>Amount:</strong></td><td>₹{total_amount}</td></tr>
                    <tr><td><strong>Due Date:</strong></td><td>{fee.due_date}</td></tr>
                </table>
                <p>Please make the payment at your earliest convenience to avoid penalties.</p>
                <p><a href="http://your-app-url/payments" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Pay Now</a></p>
                <p>Best regards,<br>Apartment Management Team</p>
            </body>
        </html>
        """
    
    def _get_notice_html(self, notice, user: User) -> str:
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>📢 New Community Notice</h2>
                <p>Hi {user.full_name},</p>
                <h3>{notice.title}</h3>
                <p>{notice.content}</p>
                <p><strong>Category:</strong> {notice.category}</p>
                <p>Best regards,<br>Apartment Management Team</p>
            </body>
        </html>
        """
