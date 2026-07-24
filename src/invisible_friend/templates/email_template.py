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

        The lines are assembled instead of using a triple-quoted literal so the
        source indentation never reaches the participant's inbox.

        Args:
            name: Name of the recipient
            assigned_person: Name of their secret friend

        Returns:
            Formatted email body (Spanish copy)
        """
        return (
            f"Hola {name},\n"
            "\n"
            "¡Felicidades! 🎉\n"
            "\n"
            f"Tu amigo invisible es: {assigned_person}\n"
            "\n"
            "Recuerda:\n"
            "- Prepara un regalo especial\n"
            "- Mantén el secreto hasta el final\n"
            "- ¡Que disfrutes! 🎁\n"
            "\n"
            "¡Gracias por participar!\n"
        )
