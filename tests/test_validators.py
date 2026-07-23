"""Tests para ParejaValidator: restricciones simétricas y validación de ciclos."""

import pytest

from invisible_friend.exceptions import ValidationError
from invisible_friend.models import Persona
from invisible_friend.validators import ParejaValidator


def buscar(personas: list[Persona], nombre: str) -> Persona:
    """Devuelve la persona con ese nombre (helper de legibilidad)."""
    return next(p for p in personas if p.nombre == nombre)


def test_pareja_permitida_es_valida(validator: ParejaValidator, personas: list[Persona]) -> None:
    """Dos participantes sin restricción entre ellos pueden emparejarse."""
    assert validator.es_pareja_valida(buscar(personas, "Alice"), buscar(personas, "Charlie"))
    assert validator.es_pareja_valida(buscar(personas, "Bob"), buscar(personas, "Diana"))


@pytest.mark.parametrize(
    ("uno", "otro"),
    [
        ("Alice", "Bob"),
        ("Bob", "Alice"),
        ("Charlie", "Diana"),
        ("Diana", "Charlie"),
    ],
)
def test_pareja_prohibida_se_rechaza_en_ambos_sentidos(
    validator: ParejaValidator, personas: list[Persona], uno: str, otro: str
) -> None:
    """La restricción es simétrica: A-B y B-A se rechazan por igual."""
    assert not validator.es_pareja_valida(buscar(personas, uno), buscar(personas, otro))


def test_nadie_puede_ser_su_propio_amigo_invisible(
    validator: ParejaValidator, personas: list[Persona]
) -> None:
    """Una persona consigo misma nunca es una pareja válida."""
    alice = buscar(personas, "Alice")
    assert not validator.es_pareja_valida(alice, alice)


def test_ciclo_sin_parejas_prohibidas_es_valido(
    validator: ParejaValidator, personas: list[Persona]
) -> None:
    """Alice → Charlie → Bob → Diana → Alice no viola ninguna restricción."""
    ciclo = [
        buscar(personas, "Alice"),
        buscar(personas, "Charlie"),
        buscar(personas, "Bob"),
        buscar(personas, "Diana"),
    ]
    assert validator.validar_ciclo(ciclo)


def test_ciclo_con_pareja_prohibida_es_invalido(
    validator: ParejaValidator, personas: list[Persona]
) -> None:
    """Una sola arista prohibida invalida el ciclo entero."""
    ciclo = [
        buscar(personas, "Alice"),
        buscar(personas, "Bob"),
        buscar(personas, "Charlie"),
        buscar(personas, "Diana"),
    ]
    assert not validator.validar_ciclo(ciclo)


def test_ciclo_comprueba_el_cierre(validator: ParejaValidator, personas: list[Persona]) -> None:
    """La última arista vuelve al principio y también se valida."""
    # Charlie → Alice → Diana → ... → Charlie: el cierre Diana→Charlie está prohibido.
    ciclo = [
        buscar(personas, "Charlie"),
        buscar(personas, "Alice"),
        buscar(personas, "Diana"),
    ]
    assert not validator.validar_ciclo(ciclo)


def test_ciclo_vacio_lanza_validation_error(validator: ParejaValidator) -> None:
    """Validar una lista vacía es un error de uso, no un ciclo válido."""
    with pytest.raises(ValidationError):
        validator.validar_ciclo([])


def test_agregar_restriccion(validator: ParejaValidator, personas: list[Persona]) -> None:
    """Una restricción añadida en caliente pasa a rechazarse."""
    validator.agregar_restriccion("Alice", "Charlie")

    assert not validator.es_pareja_valida(buscar(personas, "Alice"), buscar(personas, "Charlie"))


def test_remover_restriccion(validator: ParejaValidator, personas: list[Persona]) -> None:
    """Al quitar una restricción, la pareja vuelve a ser válida."""
    validator.remover_restriccion("Alice", "Bob")

    assert validator.es_pareja_valida(buscar(personas, "Alice"), buscar(personas, "Bob"))


def test_obtener_restricciones_devuelve_tuplas_ordenadas(validator: ParejaValidator) -> None:
    """Las restricciones se exponen como tuplas ordenadas, independientes del orden de entrada."""
    assert sorted(validator.obtener_restricciones()) == [
        ("Alice", "Bob"),
        ("Charlie", "Diana"),
    ]
