"""Email templates for the assignments.

The identifiers are English; the copy the participants read stays in Spanish.
"""


class EmailTemplate:
    """Templates for the Secret Santa emails."""

    SUBJECT = "🎁 ¡Tu Amigo Invisible! 🎁"

    @staticmethod
    def render_body(name: str, assigned_person: str) -> str:
        """
        Render the plain-text email body.

        Args:
            name: Name of the recipient
            assigned_person: Name of their secret friend

        Returns:
            Formatted email body (Spanish copy)
        """
        return f"""Hola {name},

        ¡Felicidades! 🎉

        Tu amigo invisible es: {assigned_person}

        Recuerda:
        - Prepara un regalo especial
        - Mantén el secreto hasta el final
        - ¡Que disfrutes! 🎁

        ¡Gracias por participar!
        """

    @staticmethod
    def render_html(name: str, assigned_person: str) -> str:
        """Render the HTML email body (Spanish copy)."""
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px;">
                    <h1 style="color: #d4a574; text-align: center;">🎁 ¡Amigo Invisible! 🎁</h1>
                    <p>Hola <strong>{name}</strong>,</p>
                    <p>¡Felicidades! 🎉
                    <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px; text-align: center;">
                        <p style="margin: 0;">Tu amigo invisible es:</p>
                        <p style="font-size: 24px; color: #d4a574; margin: 10px 0; font-weight: bold;">{assigned_person}</p>
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
