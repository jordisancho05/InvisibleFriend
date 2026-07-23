"""Servicio de envío de emails."""

import smtplib
import ssl
from email.message import EmailMessage

from invisible_friend.exceptions import EmailError
from invisible_friend.templates.email_template import EmailTemplate
from invisible_friend.utils.logger import get_logger

logger = get_logger(__name__)


class EmailService:
    """Gestor de envío de emails."""

    def __init__(self, smtp_server: str, smtp_port: int, email_sender: str, password: str) -> None:
        """
        Inicializa el servicio de email.

        Args:
            smtp_server: Servidor SMTP
            smtp_port: Puerto SMTP
            email_sender: Email del remitente
            password: Contraseña del remitente
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_sender = email_sender
        self.password = password

    def crear_email(self, destinatario: str, asunto: str, cuerpo: str) -> EmailMessage:
        """
        Crea un objeto EmailMessage.

        Args:
            destinatario: Email del destinatario
            asunto: Asunto del email
            cuerpo: Cuerpo del email

        Returns:
            EmailMessage configurado
        """
        email = EmailMessage()
        email["From"] = self.email_sender
        email["To"] = destinatario
        email["Subject"] = asunto
        email.set_content(cuerpo)
        return email

    def enviar_email(self, destinatario: str, email: EmailMessage) -> bool:
        """
        Envía un email usando SMTP.

        Args:
            destinatario: Email del destinatario
            email: Objeto EmailMessage

        Returns:
            True si se envió correctamente

        Raises:
            EmailError: Si hay error al enviar
        """
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as smtp:
                smtp.login(self.email_sender, self.password)
                smtp.sendmail(self.email_sender, destinatario, email.as_string())

            logger.info(f"Email enviado correctamente a {destinatario}")
            return True
        except smtplib.SMTPException as e:
            error_msg = f"Error SMTP al enviar email a {destinatario}: {e}"
            logger.error(error_msg)
            raise EmailError(error_msg) from e
        except Exception as e:
            error_msg = f"Error al enviar email a {destinatario}: {e}"
            logger.error(error_msg)
            raise EmailError(error_msg) from e

    def enviar_asignacion(
        self,
        destinatario: str,
        nombre_persona: str,
        amigo_invisible: str,
        usar_template: bool = True,
    ) -> bool:
        """
        Envía el email con la asignación de amigo invisible.

        Args:
            destinatario: Email del destinatario
            nombre_persona: Nombre de la persona
            amigo_invisible: Nombre del amigo invisible
            usar_template: Si usar template HTML

        Returns:
            True si se envió correctamente
        """
        try:
            if usar_template:
                cuerpo = EmailTemplate.generar_email(nombre_persona, amigo_invisible)
                asunto = EmailTemplate.ASUNTO
            else:
                asunto = "Amigo Invisible"
                cuerpo = (
                    f"Hola {nombre_persona},\n\n"
                    f"Tu amigo invisible es {amigo_invisible}.\n\n"
                    "¡Que disfrutes!"
                )

            email = self.crear_email(destinatario, asunto, cuerpo)
            return self.enviar_email(destinatario, email)
        except Exception as e:
            logger.error(f"Error al enviar asignación a {nombre_persona}: {e}")
            raise EmailError(f"Error al enviar asignación: {e}") from e

    def enviar_asignaciones_masivas(
        self, asignaciones: dict, personas_dict: dict, simular: bool = False
    ) -> tuple[int, int]:
        """
        Envía emails a múltiples personas.

        Args:
            asignaciones: Dict {nombre_persona: amigo_invisible}
            personas_dict: Dict {nombre: email}
            simular: Si True, solo simula sin enviar

        Returns:
            Tupla (exitosos, fallidos)
        """
        exitosos = 0
        fallidos = 0

        logger.info(f"Iniciando envío de emails {'(SIMULACIÓN)' if simular else ''}")

        for persona_nombre, amigo_invisible in asignaciones.items():
            email_destinatario = personas_dict.get(persona_nombre)

            if not email_destinatario:
                logger.warning(f"Sin email para {persona_nombre}, omitiendo")
                fallidos += 1
                continue

            if simular:
                logger.info(f"[SIMULADO] Email a {persona_nombre}: {amigo_invisible}")
                exitosos += 1
            else:
                try:
                    self.enviar_asignacion(email_destinatario, persona_nombre, amigo_invisible)
                    exitosos += 1
                except EmailError:
                    fallidos += 1

        logger.info(f"Envío completado: {exitosos} exitosos, {fallidos} fallidos")
        return exitosos, fallidos
