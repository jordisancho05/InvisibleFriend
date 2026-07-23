"""Tests para SecretSantaService.

El servicio baraja al azar, así que estos tests fijan **invariantes** sobre
muchas ejecuciones, nunca un emparejamiento concreto esperado.
"""

import pytest

from invisible_friend.exceptions import AssignmentError
from invisible_friend.models import Persona
from invisible_friend.services.secret_santa import SecretSantaService
from invisible_friend.validators import ParejaValidator

REPETICIONES = 25


def test_cada_persona_da_y_recibe_exactamente_una_vez(
    service: SecretSantaService, personas: list[Persona]
) -> None:
    """n participantes producen n aristas, sin repetir emisor ni receptor."""
    for _ in range(REPETICIONES):
        asignaciones = service.generar_asignaciones(personas)

        assert len(asignaciones) == len(personas)
        assert set(asignaciones.keys()) == set(personas)
        assert sorted(p.nombre for p in asignaciones.values()) == sorted(p.nombre for p in personas)


def test_nadie_se_asigna_a_si_mismo(service: SecretSantaService, personas: list[Persona]) -> None:
    """No hay puntos fijos en la permutación."""
    for _ in range(REPETICIONES):
        asignaciones = service.generar_asignaciones(personas)

        for quien, a_quien in asignaciones.items():
            assert quien != a_quien


def test_ninguna_asignacion_viola_las_restricciones(
    service: SecretSantaService, validator: ParejaValidator, personas: list[Persona]
) -> None:
    """Ninguna arista generada es una pareja prohibida."""
    for _ in range(REPETICIONES):
        asignaciones = service.generar_asignaciones(personas)

        for quien, a_quien in asignaciones.items():
            assert validator.es_pareja_valida(quien, a_quien)


def test_el_resultado_es_un_unico_ciclo(
    service: SecretSantaService, personas: list[Persona]
) -> None:
    """Siguiendo n saltos desde cualquiera se vuelve al inicio habiendo visto a todos.

    Esto descarta que la permutación se parta en sub-ciclos (p. ej. dos parejas
    que se regalan entre sí y se ignoran mutuamente).
    """
    for _ in range(REPETICIONES):
        asignaciones = service.generar_asignaciones(personas)

        inicio = personas[0]
        visitados = []
        actual = inicio
        for _salto in range(len(personas)):
            actual = asignaciones[actual]
            visitados.append(actual)

        assert actual == inicio, "el recorrido no vuelve al punto de partida"
        assert len(set(visitados)) == len(personas), "hay sub-ciclos"


def test_menos_de_dos_personas_lanza_assignment_error(service: SecretSantaService) -> None:
    """Con una sola persona no existe amigo invisible posible."""
    with pytest.raises(AssignmentError, match="al menos 2"):
        service.generar_asignaciones([Persona("Alice", "alice@example.com")])


def test_lista_vacia_lanza_assignment_error(service: SecretSantaService) -> None:
    """Sin participantes tampoco hay nada que asignar."""
    with pytest.raises(AssignmentError):
        service.generar_asignaciones([])


def test_restricciones_insatisfacibles_lanzan_assignment_error() -> None:
    """Si las restricciones hacen el problema imposible, falla en vez de colgarse."""
    dos = [Persona("Alice", "alice@example.com"), Persona("Bob", "bob@example.com")]
    validator = ParejaValidator([["Alice", "Bob"]])
    service = SecretSantaService(validator, max_intentos=20)

    with pytest.raises(AssignmentError, match="20 intentos"):
        service.generar_asignaciones(dos)


def test_obtener_asignaciones_formateadas_devuelve_nombres(
    service: SecretSantaService, personas: list[Persona]
) -> None:
    """La versión formateada mapea nombre → nombre, apta para JSON y email."""
    asignaciones = service.generar_asignaciones(personas)

    formateadas = service.obtener_asignaciones_formateadas(asignaciones)

    assert set(formateadas) == {p.nombre for p in personas}
    assert all(isinstance(k, str) and isinstance(v, str) for k, v in formateadas.items())


def test_imprimir_asignaciones_muestra_cada_pareja(
    service: SecretSantaService, personas: list[Persona], capsys: pytest.CaptureFixture[str]
) -> None:
    """La salida por consola incluye una línea por participante."""
    asignaciones = service.generar_asignaciones(personas)

    service.imprimir_asignaciones(asignaciones)

    salida = capsys.readouterr().out
    for persona in personas:
        assert persona.nombre in salida
