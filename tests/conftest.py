"""Fixtures shared across the whole suite.

All the data is fictional: the real participants live only in
`config/settings.yaml`, which is not versioned and no test should read.
"""

import pytest

from invisible_friend.models import Person
from invisible_friend.services.email_service import EmailService
from invisible_friend.services.secret_santa import SecretSantaService
from invisible_friend.validators import PairValidator


@pytest.fixture
def participants() -> list[Person]:
    """Four fictional participants."""
    return [
        Person("Alice", "alice@example.com"),
        Person("Bob", "bob@example.com"),
        Person("Charlie", "charlie@example.com"),
        Person("Diana", "diana@example.com"),
    ]


@pytest.fixture
def restrictions() -> list[list[str]]:
    """Two forbidden pairs."""
    return [["Alice", "Bob"], ["Charlie", "Diana"]]


@pytest.fixture
def validator(restrictions: list[list[str]]) -> PairValidator:
    """Validator loaded with the fictional restrictions."""
    return PairValidator(restrictions)


@pytest.fixture
def service(validator: PairValidator) -> SecretSantaService:
    """Assignment service with the fictional validator."""
    return SecretSantaService(validator, max_attempts=100)


@pytest.fixture
def email_service() -> EmailService:
    """Email service pointing at a fictional SMTP (never connects)."""
    return EmailService(
        smtp_server="smtp.example.com",
        smtp_port=465,
        email_sender="sender@example.com",
        password="app-password",
    )
