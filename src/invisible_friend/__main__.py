"""Punto de entrada de la aplicación.

    python -m invisible_friend            # simula el envío (por defecto)
    python -m invisible_friend --enviar   # envía los emails de verdad

El envío real es siempre explícito: sin `--enviar` no se abre ninguna conexión
SMTP.
"""

import argparse
import sys
from pathlib import Path

from invisible_friend import __version__
from invisible_friend.config import Config
from invisible_friend.exceptions import InvisibleFriendError
from invisible_friend.services.email_service import EmailService
from invisible_friend.services.secret_santa import SecretSantaService
from invisible_friend.utils.file_handler import FileHandler
from invisible_friend.utils.logger import get_logger
from invisible_friend.validators import ParejaValidator

logger = get_logger(__name__)

CONFIG_POR_DEFECTO = Path("config/settings.yaml")
OUTPUT_POR_DEFECTO = Path("output/asignaciones.json")


class InvisibleFriendApp:
    """Orquesta el flujo completo: generar, mostrar, guardar y repartir."""

    def __init__(self, config_path: Path = CONFIG_POR_DEFECTO) -> None:
        """
        Inicializa la aplicación.

        Args:
            config_path: Ruta a la configuración YAML
        """
        logger.info("Inicializando aplicación Invisible Friend")
        self.config = Config(config_path)
        self.validator = ParejaValidator(self.config.restricciones)
        self.secret_santa_service = SecretSantaService(self.validator, self.config.max_intentos)
        self.email_service = EmailService(
            self.config.smtp_server,
            self.config.smtp_port,
            self.config.email_sender,
            self.config.email_password,
        )

    def generar_asignaciones(self) -> dict:
        """
        Genera las asignaciones de amigo invisible.

        Returns:
            Diccionario con asignaciones
        """
        try:
            return self.secret_santa_service.generar_asignaciones(self.config.personas)
        except InvisibleFriendError as e:
            logger.error(f"Error al generar asignaciones: {e}")
            raise

    def mostrar_asignaciones(self, asignaciones: dict) -> None:
        """
        Muestra las asignaciones en consola.

        Args:
            asignaciones: Diccionario de asignaciones
        """
        self.secret_santa_service.imprimir_asignaciones(asignaciones)

    def guardar_asignaciones(self, asignaciones: dict, ruta: Path = OUTPUT_POR_DEFECTO) -> None:
        """
        Guarda las asignaciones en archivo JSON.

        Args:
            asignaciones: Diccionario de asignaciones
            ruta: Ruta donde guardar
        """
        formateadas = self.secret_santa_service.obtener_asignaciones_formateadas(asignaciones)
        FileHandler.guardar_asignaciones(ruta, formateadas)
        logger.info(f"Asignaciones guardadas en {ruta}")

    def enviar_emails(self, asignaciones: dict, simular: bool = True) -> tuple[int, int]:
        """
        Envía los emails con las asignaciones.

        Args:
            asignaciones: Diccionario de asignaciones
            simular: Si True, solo simula sin enviar

        Returns:
            Tupla (exitosos, fallidos)
        """
        formateadas = self.secret_santa_service.obtener_asignaciones_formateadas(asignaciones)
        emails = {p.nombre: p.email for p in self.config.personas}

        return self.email_service.enviar_asignaciones_masivas(formateadas, emails, simular=simular)

    def ejecutar_completo(
        self, enviar: bool = False, output_path: Path = OUTPUT_POR_DEFECTO
    ) -> None:
        """
        Ejecuta el flujo completo de la aplicación.

        Args:
            enviar: Si True, envía los emails de verdad; si no, solo simula
            output_path: Dónde guardar el JSON de asignaciones
        """
        logger.info("=" * 50)
        logger.info("INICIANDO FLUJO COMPLETO DE AMIGO INVISIBLE")
        logger.info("=" * 50)

        logger.info("PASO 1: Generando asignaciones...")
        asignaciones = self.generar_asignaciones()

        logger.info("PASO 2: Mostrando asignaciones...")
        self.mostrar_asignaciones(asignaciones)

        logger.info("PASO 3: Guardando asignaciones...")
        self.guardar_asignaciones(asignaciones, output_path)

        logger.info(f"PASO 4: {'Enviando' if enviar else 'Simulando envío de'} emails...")
        exitosos, fallidos = self.enviar_emails(asignaciones, simular=not enviar)
        print(f"\n✓ Emails {'enviados' if enviar else 'simulados'}: {exitosos}")
        if fallidos > 0:
            print(f"✗ Emails fallidos: {fallidos}")

        logger.info("=" * 50)
        logger.info("FLUJO COMPLETADO EXITOSAMENTE")
        logger.info("=" * 50)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """
    Define y parsea los argumentos de línea de comandos.

    Args:
        argv: Argumentos a parsear (None = los de sys.argv)

    Returns:
        Namespace con enviar, config y output
    """
    parser = argparse.ArgumentParser(
        prog="invisible-friend",
        description="Genera las asignaciones de Amigo Invisible y las reparte por email.",
    )
    parser.add_argument(
        "--enviar",
        action="store_true",
        help="envía los emails de verdad (por defecto solo se simula)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=CONFIG_POR_DEFECTO,
        help=f"ruta al YAML de participantes (por defecto: {CONFIG_POR_DEFECTO})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_POR_DEFECTO,
        help=f"dónde guardar el JSON de asignaciones (por defecto: {OUTPUT_POR_DEFECTO})",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """
    Ejecuta la aplicación desde línea de comandos.

    Args:
        argv: Argumentos a parsear (None = los de sys.argv)

    Returns:
        0 si todo fue bien, 1 si hubo un error controlado
    """
    args = parse_args(argv)
    try:
        app = InvisibleFriendApp(args.config)
        app.ejecutar_completo(enviar=args.enviar, output_path=args.output)
    except InvisibleFriendError as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        return 1
    except Exception as e:  # noqa: BLE001 - último cortafuegos del CLI
        logger.error(f"Error fatal: {e}", exc_info=True)
        print(f"❌ Error fatal: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
