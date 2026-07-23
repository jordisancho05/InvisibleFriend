"""Tests para el servicio de emails."""

import unittest
from unittest.mock import MagicMock, patch
from invisible_friend.services.email_service import EmailService
from invisible_friend.exceptions import EmailError


class TestEmailService(unittest.TestCase):
    """Tests para EmailService."""
    
    def setUp(self) -> None:
        """Configuración previa a cada test."""
        self.service = EmailService(
            smtp_server="smtp.gmail.com",
            smtp_port=465,
            email_sender="sender@example.com",
            password="password123"
        )
    
    def test_crear_email(self) -> None:
        """Test para creación de email."""
        email = self.service.crear_email(
            "recipient@example.com",
            "Test Subject",
            "Test body"
        )
        
        self.assertEqual(email["From"], "sender@example.com")
        self.assertEqual(email["To"], "recipient@example.com")
        self.assertEqual(email["Subject"], "Test Subject")
    
    def test_crear_email_estructura(self) -> None:
        """Test que verifica estructura del email."""
        email = self.service.crear_email(
            "recipient@example.com",
            "Subject",
            "Body content"
        )
        
        # Verificar que es EmailMessage
        self.assertIsNotNone(email.get_content())
    
    def test_enviar_asignacion_formato(self) -> None:
        """Test formato de envío de asignación."""
        with patch.object(self.service, 'enviar_email', return_value=True):
            resultado = self.service.enviar_asignacion(
                "recipient@example.com",
                "Juan",
                "María",
                usar_template=True
            )
            self.assertTrue(resultado)
    
    @patch('smtplib.SMTP_SSL')
    def test_enviar_email_exitoso(self, mock_smtp) -> None:
        """Test envío exitoso de email."""
        mock_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_instance
        
        email = self.service.crear_email("test@example.com", "Subject", "Body")
        resultado = self.service.enviar_email("test@example.com", email)
        
        self.assertTrue(resultado)
        mock_instance.login.assert_called_once()
    
    def test_enviar_asignaciones_masivas_simulacion(self) -> None:
        """Test envío masivo en modo simulación."""
        asignaciones = {
            "Alice": "Bob",
            "Bob": "Charlie",
            "Charlie": "Alice"
        }
        
        personas_dict = {
            "Alice": "alice@example.com",
            "Bob": "bob@example.com",
            "Charlie": "charlie@example.com"
        }
        
        exitosos, fallidos = self.service.enviar_asignaciones_masivas(
            asignaciones,
            personas_dict,
            simular=True
        )
        
        self.assertEqual(exitosos, 3)
        self.assertEqual(fallidos, 0)
    
    def test_enviar_asignaciones_sin_email(self) -> None:
        """Test envío cuando falta email."""
        asignaciones = {"Alice": "Bob"}
        personas_dict = {"Alice": ""}  # Sin email
        
        exitosos, fallidos = self.service.enviar_asignaciones_masivas(
            asignaciones,
            personas_dict,
            simular=True
        )
        
        self.assertEqual(fallidos, 1)


if __name__ == "__main__":
    unittest.main()
