"""Tests for EmailTemplate: the text the participants receive.

The identifiers are English; the asserted copy stays in Spanish, because that
is what the participants actually read.
"""

import pytest

from invisible_friend.models import GiftDetails
from invisible_friend.templates.email_template import EmailTemplate


def test_body_names_the_recipient_and_their_secret_friend() -> None:
    """The message greets the recipient and reveals who they gift to."""
    body = EmailTemplate.render_body("Alice", "Bob")

    assert "Alice" in body
    assert "Bob" in body


def test_body_is_in_spanish() -> None:
    """The user-facing copy stays in Spanish."""
    body = EmailTemplate.render_body("Alice", "Bob")

    assert "Hola" in body
    assert "Tu amigo invisible es" in body


def test_body_says_when_the_gift_is_exchanged() -> None:
    """Every participant learns the date from the email itself."""
    body = EmailTemplate.render_body("Alice", "Bob")

    assert "El regalo se entrega el día 24 de diciembre" in body


def test_body_states_the_minimum_budget() -> None:
    """The minimum spend is in the email, so nobody has to ask the organiser."""
    body = EmailTemplate.render_body("Alice", "Bob")

    assert "El presupuesto mínimo es de 30 €" in body


def test_body_uses_the_configured_exchange_date() -> None:
    """Day and month come from the gift details, not from the template."""
    gift = GiftDetails(exchange_day=6, exchange_month=1)

    body = EmailTemplate.render_body("Alice", "Bob", gift)

    assert "El regalo se entrega el día 6 de enero" in body


@pytest.mark.parametrize(("month", "name"), [(1, "enero"), (8, "agosto"), (12, "diciembre")])
def test_months_are_written_in_spanish(month: int, name: str) -> None:
    """The month number becomes the Spanish name the participants read."""
    gift = GiftDetails(exchange_day=1, exchange_month=month)

    assert f"el día 1 de {name}" in EmailTemplate.render_body("Alice", "Bob", gift)


def test_body_states_a_budget_range_when_there_is_a_maximum() -> None:
    """With a maximum the email gives the range instead of the minimum alone."""
    gift = GiftDetails(min_budget=30, max_budget=50)

    body = EmailTemplate.render_body("Alice", "Bob", gift)

    assert "El presupuesto del regalo es de entre 30 € y 50 €" in body
    assert "presupuesto mínimo" not in body


def test_equal_minimum_and_maximum_is_a_fixed_budget() -> None:
    """Minimum == maximum reads as one amount, not as a range from 30 to 30."""
    gift = GiftDetails(min_budget=30, max_budget=30)

    assert "El presupuesto del regalo es de 30 €" in EmailTemplate.render_body("Alice", "Bob", gift)


def test_subject_mentions_the_secret_friend_theme() -> None:
    """The subject identifies the email without revealing the assignment."""
    assert "Amigo Invisible" in EmailTemplate.SUBJECT
    assert "Bob" not in EmailTemplate.SUBJECT


def test_body_has_no_leading_indentation() -> None:
    """No line starts with whitespace: the source indentation is not the email's."""
    body = EmailTemplate.render_body("Alice", "Bob")

    indented = [line for line in body.splitlines() if line != line.lstrip()]

    assert indented == [], f"these lines reach the participant indented: {indented}"


def test_the_html_variant_is_gone() -> None:
    """render_html was dead code; the email is plain text only."""
    assert not hasattr(EmailTemplate, "render_html")
