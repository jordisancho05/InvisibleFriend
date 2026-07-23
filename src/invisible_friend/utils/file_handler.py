"""Gestor de archivos para guardar y cargar datos."""

import json
from pathlib import Path
from typing import Any

from invisible_friend.exceptions import InvisibleFriendError
from invisible_friend.utils.logger import get_logger

logger = get_logger(__name__)


class FileHandler:
    """Gestor de lectura y escritura de datos a archivos."""

    @staticmethod
    def guardar_json(ruta: Path, datos: dict[str, Any]) -> None:
        """
        Guarda datos en formato JSON.

        Args:
            ruta: Ruta del archivo
            datos: Datos a guardar

        Raises:
            InvisibleFriendError: Si hay error al guardar
        """
        try:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            logger.info(f"Datos guardados en {ruta}")
        except Exception as e:
            logger.error(f"Error al guardar archivo {ruta}: {e}")
            raise InvisibleFriendError(f"Error al guardar JSON: {e}") from e

    @staticmethod
    def cargar_json(ruta: Path) -> dict[str, Any]:
        """
        Carga datos desde JSON.

        Args:
            ruta: Ruta del archivo

        Returns:
            Datos cargados

        Raises:
            InvisibleFriendError: Si hay error al cargar
        """
        try:
            if not ruta.exists():
                raise InvisibleFriendError(f"Archivo no encontrado: {ruta}")

            with open(ruta, encoding="utf-8") as f:
                datos: dict[str, Any] = json.load(f)
            logger.info(f"Datos cargados desde {ruta}")
            return datos
        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear JSON {ruta}: {e}")
            raise InvisibleFriendError(f"Error al cargar JSON: {e}") from e
        except Exception as e:
            logger.error(f"Error al cargar archivo {ruta}: {e}")
            raise InvisibleFriendError(f"Error al cargar archivo: {e}") from e

    @staticmethod
    def guardar_asignaciones(ruta: Path, asignaciones: dict[str, str]) -> None:
        """
        Guarda asignaciones en formato JSON humano.

        Args:
            ruta: Ruta del archivo
            asignaciones: Diccionario de asignaciones {quien: para_quien}
        """
        datos = {"asignaciones": asignaciones, "total_personas": len(asignaciones)}
        FileHandler.guardar_json(ruta, datos)
