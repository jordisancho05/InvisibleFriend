"""Gestor centralizado de configuración."""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml
from dotenv import load_dotenv
from invisible_friend.exceptions import ConfigError
from invisible_friend.models import Persona, ConfigData


class Config:
    """Gestiona la configuración del proyecto desde YAML y variables de entorno."""
    
    def __init__(self, config_path: Optional[Path] = None) -> None:
        """
        Inicializa la configuración.
        
        Args:
            config_path: Ruta al archivo YAML de configuración
        """
        self.config_path = config_path or Path("config/settings.yaml")
        self._config: ConfigData = ConfigData()
        self._load_environment()
        self._load_config()

    def _load_environment(self) -> None:
        """Carga variables de entorno desde el primer .env que encuentre.

        Busca en config/.env y, si no existe, en el .env de la raíz.
        """
        for env_path in (Path("config/.env"), Path(".env")):
            if env_path.exists():
                load_dotenv(env_path)
                return
    
    def _load_config(self) -> None:
        """Carga configuración desde YAML."""
        if not self.config_path.exists():
            raise ConfigError(f"Archivo de configuración no encontrado: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self._parse_config(data)
        except yaml.YAMLError as e:
            raise ConfigError(f"Error al parsear YAML: {e}")
        except Exception as e:
            raise ConfigError(f"Error al cargar configuración: {e}")
    
    def _parse_config(self, data: Dict[str, Any]) -> None:
        """Parsea los datos YAML a ConfigData."""
        if not data:
            raise ConfigError("Archivo de configuración vacío")
        
        # Configuración de la app
        app_config = data.get('app', {})
        self._config.max_intentos = app_config.get('max_attempts', 100)
        
        # Configuración de SMTP
        email_config = data.get('email', {})
        self._config.smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
        self._config.smtp_port = email_config.get('smtp_port', 465)
        
        # Personas
        personas_data = data.get('personas', [])
        self._config.personas = [
            Persona(nombre=p['nombre'], email=p.get('email', ''))
            for p in personas_data
        ]
        
        # Restricciones (pares prohibidos)
        self._config.restricciones = data.get('restricciones', [])
    
    @property
    def personas(self) -> List[Persona]:
        """Retorna la lista de personas."""
        return self._config.personas
    
    @property
    def restricciones(self) -> List[List[str]]:
        """Retorna las restricciones (pares prohibidos)."""
        return self._config.restricciones
    
    @property
    def max_intentos(self) -> int:
        """Retorna el número máximo de intentos."""
        return self._config.max_intentos
    
    @property
    def smtp_server(self) -> str:
        """Retorna el servidor SMTP."""
        return self._config.smtp_server
    
    @property
    def smtp_port(self) -> int:
        """Retorna el puerto SMTP."""
        return self._config.smtp_port
    
    @property
    def email_sender(self) -> str:
        """Obtiene el email del remitente desde variables de entorno."""
        email = os.getenv("MAILSENDER")
        if not email:
            raise ConfigError("Variable de entorno MAILSENDER no configurada")
        return email
    
    @property
    def email_password(self) -> str:
        """Obtiene la contraseña desde variables de entorno."""
        password = os.getenv("PASSWORD")
        if not password:
            raise ConfigError("Variable de entorno PASSWORD no configurada")
        return password
