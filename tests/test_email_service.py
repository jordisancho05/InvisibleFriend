"""Tests for EmailService.

No test opens a socket: `smtplib.SMTP_SSL` is always patched and bulk sends use
`simulate=True`.
"""

import smtplib
from unittest.mock import MagicMock, patch

import pytest

from invisible_friend.exceptions import EmailError
from invisible_friend.services.email_service import EmailService


def test_create_email_fills_the_headers(email_service: EmailService) -> None:
    """From, To and Subject come from the configured sender and the arguments."""
    email = email_service.create_email("recipient@example.com", "Subject", "Body")

    assert email["From"] == "sender@example.com"
    assert email["To"] == "recipient@example.com"
    assert email["Subject"] == "Subject"
    assert "Body" in email.get_content()


@patch("smtplib.SMTP_SSL")
def test_send_email_logs_in_and_sends(mock_smtp: MagicMock, email_service: EmailService) -> None:
    """Sending enters the context manager, authenticates and mails the recipient."""
    connection = MagicMock()
    mock_smtp.return_value.__enter__.return_value = connection
    email = email_service.create_email("test@example.com", "Subject", "Body")

    result = email_service.send_email("test@example.com", email)

    assert result is True
    assert mock_smtp.call_args.args == ("smtp.example.com", 465)
    assert "context" in mock_smtp.call_args.kwargs, "the connection must be over SSL"
    connection.login.assert_called_once_with("sender@example.com", "app-password")
    assert connection.sendmail.call_args.args[1] == "test@example.com"


@patch("smtplib.SMTP_SSL")
def test_smtp_error_is_translated_to_email_error(
    mock_smtp: MagicMock, email_service: EmailService
) -> None:
    """An SMTP failure does not escape as a library exception."""
    mock_smtp.return_value.__enter__.side_effect = smtplib.SMTPAuthenticationError(535, b"nope")
    email = email_service.create_email("test@example.com", "Subject", "Body")

    with pytest.raises(EmailError, match="test@example.com"):
        email_service.send_email("test@example.com", email)


def test_send_assignment_uses_the_template(email_service: EmailService) -> None:
    """With use_template=True the body is rendered by EmailTemplate."""
    with patch.object(email_service, "send_email", return_value=True) as mock_send:
        result = email_service.send_assignment(
            "recipient@example.com", "Alice", "Bob", use_template=True
        )

    assert result is True
    sent_email = mock_send.call_args.args[1]
    body = sent_email.get_content()
    assert "Alice" in body
    assert "Bob" in body


def test_send_assignment_without_template_uses_plain_text(email_service: EmailService) -> None:
    """With use_template=False the body is the short message, in Spanish."""
    with patch.object(email_service, "send_email", return_value=True) as mock_send:
        email_service.send_assignment("recipient@example.com", "Alice", "Bob", use_template=False)

    sent_email = mock_send.call_args.args[1]
    assert sent_email["Subject"] == "Amigo Invisible"
    assert "Hola Alice," in sent_email.get_content()
    assert "tu amigo invisible es bob" in sent_email.get_content().lower()


def test_simulated_bulk_send_does_not_touch_the_network(email_service: EmailService) -> None:
    """simulate=True counts everyone as successful without opening a connection."""
    assignments = {"Alice": "Bob", "Bob": "Charlie", "Charlie": "Alice"}
    emails = {
        "Alice": "alice@example.com",
        "Bob": "bob@example.com",
        "Charlie": "charlie@example.com",
    }

    with patch("smtplib.SMTP_SSL") as mock_smtp:
        successful, failed = email_service.send_assignments(assignments, emails, simulate=True)

    assert (successful, failed) == (3, 0)
    mock_smtp.assert_not_called()


def test_participant_without_email_counts_as_failed(email_service: EmailService) -> None:
    """Someone's email is missing: it is recorded as a failure and does not break the batch."""
    successful, failed = email_service.send_assignments(
        {"Alice": "Bob", "Bob": "Alice"},
        {"Alice": "", "Bob": "bob@example.com"},
        simulate=True,
    )

    assert (successful, failed) == (1, 1)


@patch("smtplib.SMTP_SSL")
def test_one_failure_does_not_abort_the_batch(
    mock_smtp: MagicMock, email_service: EmailService
) -> None:
    """If one send blows up, the rest continues and is counted."""
    mock_smtp.return_value.__enter__.return_value.sendmail.side_effect = [
        None,
        smtplib.SMTPRecipientsRefused({}),
    ]

    successful, failed = email_service.send_assignments(
        {"Alice": "Bob", "Bob": "Alice"},
        {"Alice": "alice@example.com", "Bob": "bob@example.com"},
        simulate=False,
    )

    assert (successful, failed) == (1, 1)
