"""Email sending service."""

import smtplib
import ssl
from email.message import EmailMessage

from invisible_friend.exceptions import EmailError
from invisible_friend.templates.email_template import EmailTemplate
from invisible_friend.utils.logger import get_logger

logger = get_logger(__name__)


class EmailService:
    """Handles composing and sending the assignment emails."""

    def __init__(self, smtp_server: str, smtp_port: int, email_sender: str, password: str) -> None:
        """
        Initialize the email service.

        Args:
            smtp_server: SMTP server
            smtp_port: SMTP port
            email_sender: Sender email address
            password: Sender password
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_sender = email_sender
        self.password = password

    def create_email(self, recipient: str, subject: str, body: str) -> EmailMessage:
        """
        Build an EmailMessage object.

        Args:
            recipient: Recipient email address
            subject: Email subject
            body: Email body

        Returns:
            Configured EmailMessage
        """
        email = EmailMessage()
        email["From"] = self.email_sender
        email["To"] = recipient
        email["Subject"] = subject
        email.set_content(body)
        return email

    def send_email(self, recipient: str, email: EmailMessage) -> bool:
        """
        Send an email over SMTP.

        Args:
            recipient: Recipient email address
            email: EmailMessage object

        Returns:
            True if it was sent successfully

        Raises:
            EmailError: If sending fails
        """
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as smtp:
                smtp.login(self.email_sender, self.password)
                smtp.sendmail(self.email_sender, recipient, email.as_string())

            logger.info(f"Email sent successfully to {recipient}")
            return True
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error while sending email to {recipient}: {e}"
            logger.error(error_msg)
            raise EmailError(error_msg) from e
        except Exception as e:
            error_msg = f"Error while sending email to {recipient}: {e}"
            logger.error(error_msg)
            raise EmailError(error_msg) from e

    def send_assignment(
        self,
        recipient: str,
        person_name: str,
        assigned_person: str,
        use_template: bool = True,
    ) -> bool:
        """
        Send the email with the Secret Santa assignment.

        Args:
            recipient: Recipient email address
            person_name: Name of the recipient
            assigned_person: Name of their secret friend
            use_template: Whether to use the template body

        Returns:
            True if it was sent successfully
        """
        try:
            if use_template:
                body = EmailTemplate.render_body(person_name, assigned_person)
                subject = EmailTemplate.SUBJECT
            else:
                subject = "Amigo Invisible"
                body = (
                    f"Hola {person_name},\n\n"
                    f"Tu amigo invisible es {assigned_person}.\n\n"
                    "¡Que disfrutes!"
                )

            email = self.create_email(recipient, subject, body)
            return self.send_email(recipient, email)
        except Exception as e:
            logger.error(f"Error while sending assignment to {person_name}: {e}")
            raise EmailError(f"Error while sending assignment: {e}") from e

    def send_assignments(
        self, assignments: dict[str, str], emails: dict[str, str], simulate: bool = False
    ) -> tuple[int, int]:
        """
        Send emails to multiple people.

        Args:
            assignments: Dict {person_name: secret_friend}
            emails: Dict {name: email}
            simulate: If True, only simulate without sending

        Returns:
            Tuple (successful, failed)
        """
        successful = 0
        failed = 0

        logger.info(f"Starting email delivery {'(SIMULATION)' if simulate else ''}")

        for person_name, assigned_person in assignments.items():
            recipient_email = emails.get(person_name)

            if not recipient_email:
                logger.warning(f"No email for {person_name}, skipping")
                failed += 1
                continue

            if simulate:
                logger.info(f"[SIMULATED] Email to {person_name}: {assigned_person}")
                successful += 1
            else:
                try:
                    self.send_assignment(recipient_email, person_name, assigned_person)
                    successful += 1
                except EmailError:
                    failed += 1

        logger.info(f"Delivery finished: {successful} successful, {failed} failed")
        return successful, failed
