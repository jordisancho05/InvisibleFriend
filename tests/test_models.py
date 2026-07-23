"""Tests para los modelos de dominio: Persona, Asignacion y ConfigData."""

import pytest

from invisible_friend.exceptions import ValidationError
from invisible_friend.models import Asignacion, ConfigData, Persona


def test_persona_valida_conserva_sus_datos() -> None:
    """Una persona bien formada guarda nombre y email tal cual."""
    persona = Persona("Alice", "alice@example.com")

    assert persona.nombre == "Alice"
    assert persona.email == "alice@example.com"


@pytest.mark.parametrize(
    ("nombre", "email"),
    [
        ("", "alice@example.com"),
        ("Alice", ""),
        ("Alice", "sin-arroba"),
        ("Alice", "sin@punto"),
    ],
    ids=["nombre vacío", "email vacío", "email sin @", "dominio sin punto"],
)
def test_persona_invalida_lanza_validation_error(nombre: str, email: str) -> None:
    """El nombre y un email con formato razonable son obligatorios."""
    with pytest.raises(ValidationError):
        Persona(nombre, email)


def test_dos_personas_con_el_mismo_nombre_son_la_misma() -> None:
    """La identidad es el nombre: el email no distingue participantes."""
    una = Persona("Alice", "alice@example.com")
    otra = Persona("Alice", "otra-direccion@example.com")

    assert una == otra
    assert len({una, otra}) == 1


def test_personas_con_nombres_distintos_no_son_iguales() -> None:
    """Nombres distintos son participantes distintos."""
    assert Persona("Alice", "alice@example.com") != Persona("Bob", "bob@example.com")


def test_persona_no_es_igual_a_otro_tipo() -> None:
    """Comparar con algo que no es Persona devuelve False, no revienta."""
    assert Persona("Alice", "alice@example.com") != "Alice"


def test_repr_de_persona_es_legible() -> None:
    """El repr muestra nombre y email, útil en los fallos de test."""
    assert repr(Persona("Alice", "alice@example.com")) == (
        "Persona(nombre='Alice', email='alice@example.com')"
    )


def test_asignacion_entre_personas_distintas() -> None:
    """Una asignación normal se construye sin problemas."""
    alice = Persona("Alice", "alice@example.com")
    bob = Persona("Bob", "bob@example.com")

    asignacion = Asignacion(alice, bob)

    assert asignacion.de == alice
    assert asignacion.para == bob
    assert repr(asignacion) == "Alice → Bob"


def test_asignacion_a_uno_mismo_lanza_validation_error() -> None:
    """Nadie puede ser su propio amigo invisible."""
    alice = Persona("Alice", "alice@example.com")

    with pytest.raises(ValidationError):
        Asignacion(alice, alice)


def test_config_data_trae_defaults_sensatos() -> None:
    """ConfigData vacío arranca con los valores por defecto del proyecto."""
    datos = ConfigData()

    assert datos.personas == []
    assert datos.restricciones == []
    assert datos.max_intentos == 100
    assert datos.smtp_server == "smtp.gmail.com"
    assert datos.smtp_port == 465
