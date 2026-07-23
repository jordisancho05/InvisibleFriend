"""Tests para FileHandler: persistencia JSON de las asignaciones."""

import json
from pathlib import Path

import pytest

from invisible_friend.exceptions import InvisibleFriendError
from invisible_friend.utils.file_handler import FileHandler


def test_guardar_y_cargar_conserva_los_datos(tmp_path: Path) -> None:
    """Ida y vuelta por disco sin pérdida."""
    ruta = tmp_path / "datos.json"
    datos = {"asignaciones": {"Alice": "Bob"}, "total_personas": 2}

    FileHandler.guardar_json(ruta, datos)

    assert FileHandler.cargar_json(ruta) == datos


def test_guardar_conserva_acentos_y_enies(tmp_path: Path) -> None:
    """El JSON se escribe en UTF-8 legible, sin escapar los no-ASCII."""
    ruta = tmp_path / "datos.json"

    FileHandler.guardar_json(ruta, {"asignaciones": {"Begoña": "Martín"}})

    contenido = ruta.read_text(encoding="utf-8")
    assert "Begoña" in contenido
    assert "Martín" in contenido
    assert "\\u" not in contenido


def test_guardar_crea_los_directorios_intermedios(tmp_path: Path) -> None:
    """No hace falta crear output/ a mano antes de guardar."""
    ruta = tmp_path / "output" / "anidado" / "datos.json"

    FileHandler.guardar_json(ruta, {"ok": True})

    assert ruta.exists()


def test_cargar_archivo_inexistente_lanza_error(tmp_path: Path) -> None:
    """Leer algo que no está es un error del proyecto, no un FileNotFoundError suelto."""
    with pytest.raises(InvisibleFriendError, match="no encontrado"):
        FileHandler.cargar_json(tmp_path / "no_existe.json")


def test_cargar_json_corrupto_lanza_error(tmp_path: Path) -> None:
    """Un JSON malformado se traduce al error del dominio."""
    ruta = tmp_path / "roto.json"
    ruta.write_text("{esto no es json", encoding="utf-8")

    with pytest.raises(InvisibleFriendError):
        FileHandler.cargar_json(ruta)


def test_guardar_asignaciones_envuelve_con_el_total(tmp_path: Path) -> None:
    """El archivo de asignaciones lleva el mapa y el número de participantes."""
    ruta = tmp_path / "asignaciones.json"
    asignaciones = {"Alice": "Bob", "Bob": "Charlie", "Charlie": "Alice"}

    FileHandler.guardar_asignaciones(ruta, asignaciones)

    guardado = json.loads(ruta.read_text(encoding="utf-8"))
    assert guardado == {"asignaciones": asignaciones, "total_personas": 3}
