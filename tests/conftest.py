"""Fixtures compartidas por toda la suite.

Todos los datos son ficticios: los participantes reales viven únicamente en
`config/settings.yaml`, que no se versiona y ningún test debe leer.
"""

import pytest

from invisible_friend.models import Persona
from invisible_friend.services.email_service import EmailService
from invisible_friend.services.secret_santa import SecretSantaService
from invisible_friend.validators import ParejaValidator


@pytest.fixture
def personas() -> list[Persona]:
    """Cuatro participantes ficticios."""
    return [
        Persona("Alice", "alice@example.com"),
        Persona("Bob", "bob@example.com"),
        Persona("Charlie", "charlie@example.com"),
        Persona("Diana", "diana@example.com"),
    ]


@pytest.fixture
def restricciones() -> list[list[str]]:
    """Dos parejas prohibidas."""
    return [["Alice", "Bob"], ["Charlie", "Diana"]]


@pytest.fixture
def validator(restricciones: list[list[str]]) -> ParejaValidator:
    """Validador cargado con las restricciones ficticias."""
    return ParejaValidator(restricciones)


@pytest.fixture
def service(validator: ParejaValidator) -> SecretSantaService:
    """Servicio de asignaciones con el validador ficticio."""
    return SecretSantaService(validator, max_intentos=100)


@pytest.fixture
def email_service() -> EmailService:
    """Servicio de email apuntando a un SMTP ficticio (nunca se conecta)."""
    return EmailService(
        smtp_server="smtp.example.com",
        smtp_port=465,
        email_sender="sender@example.com",
        password="app-password",
    )
