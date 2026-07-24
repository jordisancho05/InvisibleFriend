"""Tests for EmailTemplate: the text the participants receive.

The identifiers are English; the asserted copy stays in Spanish, because that
is what the participants actually read.
"""

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
