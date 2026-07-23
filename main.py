"""Punto de entrada principal de la aplicación."""

from pathlib import Path
from invisible_friend.config import Config
from invisible_friend.validators import ParejaValidator
from invisible_friend.services.secret_santa import SecretSantaService
from invisible_friend.services.email_service import EmailService
from invisible_friend.utils.file_handler import FileHandler
from invisible_friend.utils.logger import get_logger
from invisible_friend.exceptions import InvisibleFriendError

logger = get_logger(__name__)


class InvisibleFriendApp:
    """Aplicación principal de Amigo Invisible."""
    
    def __init__(self, config_path: Path = Path("config/settings.yaml")) -> None:
        """
        Inicializa la aplicación.
        
        Args:
            config_path: Ruta a la configuración YAML
        """
        logger.info("Inicializando aplicación Invisible Friend")
        self.config = Config(config_path)
        self.validator = ParejaValidator(self.config.restricciones)
        self.secret_santa_service = SecretSantaService(
            self.validator, 
            self.config.max_intentos
        )
        self.email_service = EmailService(
            self.config.smtp_server,
            self.config.smtp_port,
            self.config.email_sender,
            self.config.email_password
        )
    
    def generar_asignaciones(self) -> dict:
        """
        Genera las asignaciones de amigo invisible.
        
        Returns:
            Diccionario con asignaciones
        """
        try:
            asignaciones = self.secret_santa_service.generar_asignaciones(
                self.config.personas
            )
            return asignaciones
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
    
    def guardar_asignaciones(
        self, 
        asignaciones: dict, 
        ruta: Path = Path("output/asignaciones.json")
    ) -> None:
        """
        Guarda las asignaciones en archivo JSON.
        
        Args:
            asignaciones: Diccionario de asignaciones
            ruta: Ruta donde guardar
        """
        asignaciones_formateadas = (
            self.secret_santa_service.obtener_asignaciones_formateadas(asignaciones)
        )
        FileHandler.guardar_asignaciones(ruta, asignaciones_formateadas)
        logger.info(f"Asignaciones guardadas en {ruta}")
    
    def enviar_emails(self, asignaciones: dict, simular: bool = True) -> tuple:
        """
        Envía los emails con las asignaciones.
        
        Args:
            asignaciones: Diccionario de asignaciones
            simular: Si True, solo simula sin enviar
            
        Returns:
            Tupla (exitosos, fallidos)
        """
        asignaciones_formateadas = (
            self.secret_santa_service.obtener_asignaciones_formateadas(asignaciones)
        )
        
        # Crear diccionario {nombre: email}
        personas_dict = {p.nombre: p.email for p in self.config.personas}
        
        return self.email_service.enviar_asignaciones_masivas(
            asignaciones_formateadas,
            personas_dict,
            simular=simular
        )
    
    def ejecutar_completo(self, enviar: bool = False) -> None:
        """
        Ejecuta el flujo completo de la aplicación.
        
        Args:
            enviar: Si True, envía los emails (por defecto solo simula)
        """
        try:
            logger.info("="*50)
            logger.info("INICIANDO FLUJO COMPLETO DE AMIGO INVISIBLE")
            logger.info("="*50)
            
            # Generar asignaciones
            logger.info("PASO 1: Generando asignaciones...")
            asignaciones = self.generar_asignaciones()
            
            # Mostrar asignaciones
            logger.info("PASO 2: Mostrando asignaciones...")
            self.mostrar_asignaciones(asignaciones)
            
            # Guardar asignaciones
            logger.info("PASO 3: Guardando asignaciones...")
            self.guardar_asignaciones(asignaciones)
            
            # Enviar emails (o simular)
            logger.info(f"PASO 4: {'Simulando envío de' if not enviar else 'Enviando'} emails...")
            exitosos, fallidos = self.enviar_emails(asignaciones, simular=not enviar)
            print(f"\n✓ Emails enviados: {exitosos}")
            if fallidos > 0:
                print(f"✗ Emails fallidos: {fallidos}")
            
            logger.info("="*50)
            logger.info("FLUJO COMPLETADO EXITOSAMENTE")
            logger.info("="*50)
            
        except InvisibleFriendError as e:
            logger.error(f"Error en flujo: {e}")
            print(f"❌ Error: {e}")
            raise


def main() -> None:
    """Función principal."""
    try:
        app = InvisibleFriendApp()
        # Ejecutar con envío de emails simulado (cambiar a True para enviar de verdad)
        app.ejecutar_completo(enviar=False)

    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
        print(f"❌ Error fatal: {e}")
        exit(1)


if __name__ == "__main__":
    main()
