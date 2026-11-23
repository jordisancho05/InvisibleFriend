"""Email templates for the assignments.

The identifiers are English; the copy the participants read stays in Spanish.
"""

from invisible_friend.models import GiftDetails

# Participant-facing copy, so Spanish like the rest of the email body.
_MONTH_NAMES = (
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)


class EmailTemplate:
    """Templates for the Secret Santa emails."""

    SUBJECT = "🎁 ¡Tu Amigo Invisible! 🎁"

    @staticmethod
    def render_body(name: str, assigned_person: str, gift: GiftDetails | None = None) -> str:
        """
        Render the plain-text email body.

        The lines are assembled instead of using a triple-quoted literal so the
        source indentation never reaches the participant's inbox.

        Args:
            name: Name of the recipient
            assigned_person: Name of their secret friend
            gift: Exchange date and budget; the defaults when omitted

        Returns:
            Formatted email body (Spanish copy)
        """
        details = gift if gift is not None else GiftDetails()
        return (
            f"Hola {name},\n"
            "\n"
            "¡Felicidades! 🎉\n"
            "\n"
            f"Tu amigo invisible es: {assigned_person}\n"
            "\n"
            "Recuerda:\n"
            "- Prepara un regalo especial\n"
            f"- El regalo se entrega el día {EmailTemplate._exchange_date(details)}\n"
            f"- {EmailTemplate._budget(details)}\n"
            "- Mantén el secreto hasta el final\n"
            "- ¡Que disfrutes! 🎁\n"
            "\n"
            "¡Gracias por participar!\n"
        )

    @staticmethod
    def _exchange_date(gift: GiftDetails) -> str:
        """Write the exchange date as the email shows it: the day, then the month's name."""
        return f"{gift.exchange_day} de {_MONTH_NAMES[gift.exchange_month - 1]}"

    @staticmethod
    def _budget(gift: GiftDetails) -> str:
        """Write the budget line: a minimum alone, a fixed amount or a range."""
        if gift.max_budget is None:
            return f"El presupuesto mínimo es de {gift.min_budget} €"
        if gift.max_budget == gift.min_budget:
            return f"El presupuesto del regalo es de {gift.min_budget} €"
        return f"El presupuesto del regalo es de entre {gift.min_budget} € y {gift.max_budget} €"
