"""
Email Notification Service for Training Nominations.
"""

import smtplib
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
import os

from src.training_models import (
    Employee, TrainingPlan, AreaOfWork, Nomination,
    EmailNotification, NominationStatus
)


class NotificationService:
    """Service for sending email notifications."""

    def __init__(self, config: Optional[dict] = None):
        """Initialize notification service with email configuration."""
        self.config = config or {}
        self.smtp_host = self.config.get('smtp_host', os.getenv('SMTP_HOST', 'localhost'))
        self.smtp_port = int(self.config.get('smtp_port', os.getenv('SMTP_PORT', 587)))
        self.smtp_user = self.config.get('smtp_user', os.getenv('SMTP_USER', ''))
        self.smtp_password = self.config.get('smtp_password', os.getenv('SMTP_PASSWORD', ''))
        self.from_email = self.config.get('from_email', os.getenv('FROM_EMAIL', 'hr@company.com'))
        self.from_name = self.config.get('from_name', os.getenv('FROM_NAME', 'HR Department'))

        # Store notifications (in production, this would be a database)
        self.notifications: list[EmailNotification] = []

    def create_nomination_email(
        self,
        employee: Employee,
        training_plan: TrainingPlan,
        aow: AreaOfWork,
        nomination: Nomination,
        nominated_by_name: str
    ) -> EmailNotification:
        """Create an email notification for a training nomination."""

        subject = f"Training Nomination: {aow.name}"

        body = f"""
Dear {employee.name},

You have been nominated for training in the following area:

Training Plan: {training_plan.name}
Area of Work: {aow.name}

Description:
{aow.description}

Skills to be developed:
{', '.join(aow.skills)}

Duration: {aow.duration_hours} hours

Priority: {nomination.priority.value.upper()}

Nominated by: {nominated_by_name}
Date: {nomination.nominated_at.strftime('%B %d, %Y at %I:%M %p')}

{'Additional Notes: ' + nomination.notes if nomination.notes else ''}

Resources:
{chr(10).join('- ' + r for r in aow.resources) if aow.resources else 'No additional resources specified.'}

{'Prerequisites: ' + ', '.join(aow.prerequisites) if aow.prerequisites else ''}

Please log in to the training portal to view more details and confirm your participation.

Best regards,
{self.from_name}
        """.strip()

        notification = EmailNotification(
            id=str(uuid.uuid4()),
            recipient_email=employee.email,
            recipient_name=employee.name,
            subject=subject,
            body=body,
            nomination_id=nomination.id
        )

        return notification

    def send_email(self, notification: EmailNotification) -> bool:
        """Send an email notification."""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = notification.recipient_email
            msg['Subject'] = notification.subject
            msg.attach(MIMEText(notification.body, 'plain'))

            # For demo purposes, we'll simulate sending
            # In production, uncomment the SMTP connection code below

            # Simulate email sending (for demo)
            print(f"[EMAIL SERVICE] Sending email to: {notification.recipient_email}")
            print(f"[EMAIL SERVICE] Subject: {notification.subject}")

            # Uncomment for actual SMTP sending:
            # with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            #     if self.smtp_user and self.smtp_password:
            #         server.starttls()
            #         server.login(self.smtp_user, self.smtp_password)
            #     server.send_message(msg)

            notification.is_sent = True
            notification.sent_at = datetime.now()
            self.notifications.append(notification)

            return True

        except Exception as e:
            notification.is_sent = False
            notification.error_message = str(e)
            self.notifications.append(notification)
            print(f"[EMAIL SERVICE] Error sending email: {e}")
            return False

    def send_nomination_notification(
        self,
        employee: Employee,
        training_plan: TrainingPlan,
        aow: AreaOfWork,
        nomination: Nomination,
        nominated_by_name: str
    ) -> tuple[bool, EmailNotification]:
        """Create and send a nomination notification email."""

        # Create the email notification
        notification = self.create_nomination_email(
            employee, training_plan, aow, nomination, nominated_by_name
        )

        # Send the email
        success = self.send_email(notification)

        return success, notification

    def get_notifications_for_nomination(self, nomination_id: str) -> list[EmailNotification]:
        """Get all notifications for a specific nomination."""
        return [n for n in self.notifications if n.nomination_id == nomination_id]

    def get_notifications_for_employee(self, email: str) -> list[EmailNotification]:
        """Get all notifications sent to a specific employee."""
        return [n for n in self.notifications if n.recipient_email == email]

    def get_all_notifications(self) -> list[EmailNotification]:
        """Get all notifications."""
        return self.notifications.copy()
