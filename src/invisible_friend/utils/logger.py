"""Logger centralizado para el proyecto."""

import logging
import sys
from pathlib import Path
from typing import Optional


class LoggerConfig:
    """Configura el logging del proyecto."""
    
    _logger: Optional[logging.Logger] = None
    
    @classmethod
    def get_logger(cls, name: str = "invisible_friend") -> logging.Logger:
        """
        Obtiene o crea el logger principal.
        
        Args:
            name: Nombre del logger
            
        Returns:
            Logger configurado
        """
        if cls._logger is None:
            cls._logger = cls._configure_logger(name)
        return cls._logger
    
    @staticmethod
    def _configure_logger(name: str) -> logging.Logger:
        """Configura el logger con handlers y formatters."""
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # Evitar duplicar handlers
        if logger.handlers:
            return logger
        
        # Formato del log (sin caracteres especiales en logs)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para consola (con UTF-8 en Windows)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        # Forzar UTF-8 en Windows
        if hasattr(console_handler.stream, 'reconfigure'):
            console_handler.stream.reconfigure(encoding='utf-8', errors='replace')
        logger.addHandler(console_handler)
        
        # Handler para archivo (UTF-8)
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "invisible_friend.log", encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger


# Exportar función global para usar en toda la aplicación
def get_logger(name: str = "invisible_friend") -> logging.Logger:
    """Retorna el logger configurado."""
    return LoggerConfig.get_logger(name)
