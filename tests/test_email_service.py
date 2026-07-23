"""Tests para EmailService.

Ningún test abre un socket: `smtplib.SMTP_SSL` va siempre parcheado y los
envíos masivos usan `simular=True`.
"""

import smtplib
from unittest.mock import MagicMock, patch

import pytest

from invisible_friend.exceptions import EmailError
from invisible_friend.services.email_service import EmailService


def test_crear_email_rellena_las_cabeceras(email_service: EmailService) -> None:
    """From, To y Subject salen del remitente configurado y de los argumentos."""
    email = email_service.crear_email("recipient@example.com", "Asunto", "Cuerpo")

    assert email["From"] == "sender@example.com"
    assert email["To"] == "recipient@example.com"
    assert email["Subject"] == "Asunto"
    assert "Cuerpo" in email.get_content()


@patch("smtplib.SMTP_SSL")
def test_enviar_email_hace_login_y_sendmail(
    mock_smtp: MagicMock, email_service: EmailService
) -> None:
    """El envío entra al context manager, autentica y manda al destinatario."""
    conexion = MagicMock()
    mock_smtp.return_value.__enter__.return_value = conexion
    email = email_service.crear_email("test@example.com", "Asunto", "Cuerpo")

    resultado = email_service.enviar_email("test@example.com", email)

    assert resultado is True
    assert mock_smtp.call_args.args == ("smtp.example.com", 465)
    assert "context" in mock_smtp.call_args.kwargs, "la conexión debe ir sobre SSL"
    conexion.login.assert_called_once_with("sender@example.com", "app-password")
    assert conexion.sendmail.call_args.args[1] == "test@example.com"


@patch("smtplib.SMTP_SSL")
def test_error_smtp_se_traduce_a_email_error(
    mock_smtp: MagicMock, email_service: EmailService
) -> None:
    """Un fallo de SMTP no se escapa como excepción de librería."""
    mock_smtp.return_value.__enter__.side_effect = smtplib.SMTPAuthenticationError(535, b"nope")
    email = email_service.crear_email("test@example.com", "Asunto", "Cuerpo")

    with pytest.raises(EmailError, match="test@example.com"):
        email_service.enviar_email("test@example.com", email)


def test_enviar_asignacion_usa_el_template(email_service: EmailService) -> None:
    """Con usar_template=True el cuerpo lo genera EmailTemplate."""
    with patch.object(email_service, "enviar_email", return_value=True) as mock_enviar:
        resultado = email_service.enviar_asignacion(
            "recipient@example.com", "Alice", "Bob", usar_template=True
        )

    assert resultado is True
    email_enviado = mock_enviar.call_args.args[1]
    cuerpo = email_enviado.get_content()
    assert "Alice" in cuerpo
    assert "Bob" in cuerpo


def test_enviar_asignacion_sin_template_usa_texto_plano(email_service: EmailService) -> None:
    """Con usar_template=False el cuerpo es el mensaje corto, en español."""
    with patch.object(email_service, "enviar_email", return_value=True) as mock_enviar:
        email_service.enviar_asignacion(
            "recipient@example.com", "Alice", "Bob", usar_template=False
        )

    email_enviado = mock_enviar.call_args.args[1]
    assert email_enviado["Subject"] == "Amigo Invisible"
    assert "Hola Alice," in email_enviado.get_content()
    assert "tu amigo invisible es bob" in email_enviado.get_content().lower()


def test_envio_masivo_simulado_no_toca_la_red(email_service: EmailService) -> None:
    """simular=True cuenta todos como exitosos sin abrir conexión."""
    asignaciones = {"Alice": "Bob", "Bob": "Charlie", "Charlie": "Alice"}
    emails = {
        "Alice": "alice@example.com",
        "Bob": "bob@example.com",
        "Charlie": "charlie@example.com",
    }

    with patch("smtplib.SMTP_SSL") as mock_smtp:
        exitosos, fallidos = email_service.enviar_asignaciones_masivas(
            asignaciones, emails, simular=True
        )

    assert (exitosos, fallidos) == (3, 0)
    mock_smtp.assert_not_called()


def test_participante_sin_email_cuenta_como_fallido(email_service: EmailService) -> None:
    """Falta el email de alguien: se registra como fallo y no rompe el lote."""
    exitosos, fallidos = email_service.enviar_asignaciones_masivas(
        {"Alice": "Bob", "Bob": "Alice"},
        {"Alice": "", "Bob": "bob@example.com"},
        simular=True,
    )

    assert (exitosos, fallidos) == (1, 1)


@patch("smtplib.SMTP_SSL")
def test_un_fallo_no_aborta_el_lote(mock_smtp: MagicMock, email_service: EmailService) -> None:
    """Si un envío revienta, el resto continúa y se contabiliza."""
    mock_smtp.return_value.__enter__.return_value.sendmail.side_effect = [
        None,
        smtplib.SMTPRecipientsRefused({}),
    ]

    exitosos, fallidos = email_service.enviar_asignaciones_masivas(
        {"Alice": "Bob", "Bob": "Alice"},
        {"Alice": "alice@example.com", "Bob": "bob@example.com"},
        simular=False,
    )

    assert (exitosos, fallidos) == (1, 1)
