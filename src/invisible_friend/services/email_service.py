"""Email sending service.

Two rules shape this module: `simulate=True` never opens a socket, and the log
records *that* a message went out, never *what* it revealed — the receiver's
name belongs in the inbox, not in `logs/`.
"""

import smtplib
import ssl
from collections.abc import Iterator
from contextlib import ExitStack, contextmanager
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

    @contextmanager
    def _session(self) -> Iterator[smtplib.SMTP_SSL]:
        """
        Open one authenticated SMTP session.

        Yields:
            A logged-in SMTP_SSL connection, closed on exit
        """
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as smtp:
            smtp.login(self.email_sender, self.password)
            yield smtp

    def send_email(
        self,
        recipient: str,
        email: EmailMessage,
        connection: smtplib.SMTP_SSL | None = None,
    ) -> bool:
        """
        Send an email over SMTP.

        Args:
            recipient: Recipient email address
            email: EmailMessage object
            connection: An already authenticated session to reuse. Without it a
                new one is opened just for this message

        Returns:
            True if it was sent successfully

        Raises:
            EmailError: If sending fails
        """
        try:
            if connection is None:
                with self._session() as smtp:
                    smtp.sendmail(self.email_sender, recipient, email.as_string())
            else:
                connection.sendmail(self.email_sender, recipient, email.as_string())

            logger.debug("Message accepted by the server for %s", recipient)
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
        connection: smtplib.SMTP_SSL | None = None,
    ) -> bool:
        """
        Send the email with the Secret Santa assignment.

        Args:
            recipient: Recipient email address
            person_name: Name of the recipient
            assigned_person: Name of their secret friend
            connection: An already authenticated session to reuse

        Returns:
            True if it was sent successfully

        Raises:
            EmailError: If sending fails (raised by `send_email`, not re-wrapped)
        """
        body = EmailTemplate.render_body(person_name, assigned_person)
        email = self.create_email(recipient, EmailTemplate.SUBJECT, body)
        return self.send_email(recipient, email, connection)

    def send_assignments(
        self, assignments: dict[str, str], emails: dict[str, str], simulate: bool = False
    ) -> tuple[int, int]:
        """
        Send emails to multiple people over a single SMTP session.

        Args:
            assignments: Dict {person_name: secret_friend}
            emails: Dict {name: email}
            simulate: If True, only simulate without sending

        Returns:
            Tuple (successful, failed)

        Raises:
            EmailError: If the SMTP session cannot be opened at all
        """
        successful = 0
        failed = 0

        logger.info("Starting email delivery%s", " (SIMULATION)" if simulate else "")

        try:
            with ExitStack() as stack:
                # One login for the whole batch: authenticating once per
                # recipient is what makes Gmail flag the account mid-delivery.
                # Simulating enters no session at all.
                connection = None if simulate else stack.enter_context(self._session())

                for person_name, assigned_person in assignments.items():
                    recipient_email = emails.get(person_name)

                    if not recipient_email:
                        logger.warning("No email for %s, skipping", person_name)
                        failed += 1
                        continue

                    if simulate:
                        logger.info("Email simulated to %s", person_name)
                        successful += 1
                        continue

                    try:
                        self.send_assignment(
                            recipient_email, person_name, assigned_person, connection
                        )
                        logger.info("Email sent to %s", person_name)
                        successful += 1
                    except EmailError:
                        failed += 1
        except smtplib.SMTPException as e:
            error_msg = f"Could not open the SMTP session: {e}"
            logger.error(error_msg)
            raise EmailError(error_msg) from e

        logger.info("Delivery finished: %s successful, %s failed", successful, failed)
        return successful, failed
