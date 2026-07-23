"""Tests para EmailTemplate: el texto que reciben los participantes."""

from invisible_friend.templates.email_template import EmailTemplate


def test_cuerpo_nombra_al_destinatario_y_a_su_amigo_invisible() -> None:
    """El mensaje saluda a quien lo recibe y revela a quién le toca regalar."""
    cuerpo = EmailTemplate.generar_email("Alice", "Bob")

    assert "Alice" in cuerpo
    assert "Bob" in cuerpo


def test_cuerpo_esta_en_castellano() -> None:
    """La copia de cara al usuario se mantiene en español."""
    cuerpo = EmailTemplate.generar_email("Alice", "Bob")

    assert "Hola" in cuerpo
    assert "Tu amigo invisible es" in cuerpo


def test_asunto_menciona_el_amigo_invisible() -> None:
    """El asunto identifica el email sin desvelar la asignación."""
    assert "Amigo Invisible" in EmailTemplate.ASUNTO
    assert "Bob" not in EmailTemplate.ASUNTO


def test_version_html_es_un_documento_completo() -> None:
    """La variante HTML envuelve el mismo contenido en marcado válido."""
    html = EmailTemplate.generar_email_html("Alice", "Bob")

    assert html.strip().startswith("<html>")
    assert html.strip().endswith("</html>")
    assert "Alice" in html
    assert "Bob" in html
