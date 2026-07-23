"""Servicio principal para generar asignaciones de amigo invisible."""

import random

from invisible_friend.exceptions import AssignmentError
from invisible_friend.models import Persona
from invisible_friend.utils.logger import get_logger
from invisible_friend.validators import ParejaValidator

logger = get_logger(__name__)


class SecretSantaService:
    """Genera asignaciones válidas de amigo invisible."""

    def __init__(self, validator: ParejaValidator, max_intentos: int = 100) -> None:
        """
        Inicializa el servicio.

        Args:
            validator: Validador de parejas
            max_intentos: Número máximo de intentos para generar asignaciones
        """
        self.validator = validator
        self.max_intentos = max_intentos

    def generar_asignaciones(self, personas: list[Persona]) -> dict[Persona, Persona]:
        """
        Genera un ciclo válido de asignaciones.

        Cada persona tiene exactamente un amigo invisible y es amigo invisible de exactamente uno.
        Forma un ciclo: persona[i] -> persona[(i+1) % n].

        Args:
            personas: Lista de personas

        Returns:
            Diccionario {persona: amigo_invisible}

        Raises:
            AssignmentError: Si no se puede generar un ciclo válido
        """
        if len(personas) < 2:
            raise AssignmentError("Se necesitan al menos 2 personas")

        logger.info(f"Iniciando generación de asignaciones para {len(personas)} personas")

        for intento in range(self.max_intentos):
            # Crear copia y barajar
            personas_barajadas = personas.copy()
            random.shuffle(personas_barajadas)

            # Validar que el ciclo sea válido
            if self.validator.validar_ciclo(personas_barajadas):
                # Crear diccionario de asignaciones
                asignaciones = {
                    personas_barajadas[i]: personas_barajadas[(i + 1) % len(personas_barajadas)]
                    for i in range(len(personas_barajadas))
                }

                logger.info(f"Asignaciones generadas exitosamente en intento {intento + 1}")
                return asignaciones

        error_msg = f"No se pudo generar asignaciones válidas tras {self.max_intentos} intentos"
        logger.error(error_msg)
        raise AssignmentError(error_msg)

    def obtener_asignaciones_formateadas(
        self, asignaciones: dict[Persona, Persona]
    ) -> dict[str, str]:
        """
        Convierte asignaciones a formato nombre -> nombre.

        Args:
            asignaciones: Diccionario de asignaciones

        Returns:
            Diccionario con nombres
        """
        return {
            persona_de.nombre: persona_para.nombre
            for persona_de, persona_para in asignaciones.items()
        }

    def imprimir_asignaciones(self, asignaciones: dict[Persona, Persona]) -> None:
        """
        Imprime las asignaciones en formato legible.

        Args:
            asignaciones: Diccionario de asignaciones
        """
        logger.info("=== ASIGNACIONES DE AMIGO INVISIBLE ===")
        for persona_de, persona_para in asignaciones.items():
            email = persona_de.email if persona_de.email else "[sin email]"
            print(f"  {persona_de.nombre} (email: {email}) -> {persona_para.nombre}")
            logger.debug(f"Asignacion: {persona_de.nombre} -> {persona_para.nombre}")
