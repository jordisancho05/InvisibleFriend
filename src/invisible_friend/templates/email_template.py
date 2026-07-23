"""Template de emails para asignaciones."""


class EmailTemplate:
    """Templates para emails de amigo invisible."""

    ASUNTO = "🎁 ¡Tu Amigo Invisible! 🎁"

    @staticmethod
    def generar_email(nombre_persona: str, amigo_invisible: str) -> str:
        """
        Genera el cuerpo del email con formato.

        Args:
            nombre_persona: Nombre de quien recibe el email
            amigo_invisible: Nombre del amigo invisible

        Returns:
            Cuerpo del email formateado
        """
        return f"""Hola {nombre_persona},

        ¡Felicidades! 🎉

        Tu amigo invisible es: {amigo_invisible}

        Recuerda:
        - Prepara un regalo especial
        - Mantén el secreto hasta el final
        - ¡Que disfrutes! 🎁

        ¡Gracias por participar!
        """

    @staticmethod
    def generar_email_html(nombre_persona: str, amigo_invisible: str) -> str:
        """Genera email en formato HTML."""
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px;">
                    <h1 style="color: #d4a574; text-align: center;">🎁 ¡Amigo Invisible! 🎁</h1>
                    <p>Hola <strong>{nombre_persona}</strong>,</p>
                    <p>¡Felicidades! 🎉
                    <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px; text-align: center;">
                        <p style="margin: 0;">Tu amigo invisible es:</p>
                        <p style="font-size: 24px; color: #d4a574; margin: 10px 0; font-weight: bold;">{amigo_invisible}</p>
                    </div>
                    <p><strong>Recuerda:</strong></p>
                    <ul>
                        <li>Prepara un regalo especial</li>
                        <li>Mantén el secreto hasta el final</li>
                        <li>¡Que disfrutes! 🎁</li>
                    </ul>
                    <p style="text-align: center; color: #999; margin-top: 30px;">¡Gracias por participar!</p>
                </div>
            </body>
        </html>
        """
