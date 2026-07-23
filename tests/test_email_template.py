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


def test_html_version_is_a_full_document() -> None:
    """The HTML variant wraps the same content in valid markup."""
    html = EmailTemplate.render_html("Alice", "Bob")

    assert html.strip().startswith("<html>")
    assert html.strip().endswith("</html>")
    assert "Alice" in html
    assert "Bob" in html
