"""Modelos de datos para Invisible Friend."""

from dataclasses import dataclass, field

from invisible_friend.exceptions import ValidationError


@dataclass
class Persona:
    """Representa una persona que participa en el amigo invisible."""

    nombre: str
    email: str  # Email es OBLIGATORIO

    def __post_init__(self) -> None:
        """Valida los datos después de la inicialización."""
        if not self.nombre or not isinstance(self.nombre, str):
            raise ValidationError("El nombre debe ser una cadena no vacía")
        if not self.email or not isinstance(self.email, str):
            raise ValidationError("El email es obligatorio")
        if not self._is_valid_email(self.email):
            raise ValidationError(f"Email inválido: {self.email}")

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Valida formato básico de email."""
        return "@" in email and "." in email.split("@")[1]

    def __repr__(self) -> str:
        return f"Persona(nombre='{self.nombre}', email='{self.email}')"

    def __hash__(self) -> int:
        return hash(self.nombre)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Persona):
            return self.nombre == other.nombre
        return False


@dataclass
class Asignacion:
    """Representa una asignación de amigo invisible."""

    de: Persona
    para: Persona

    def __post_init__(self) -> None:
        """Valida que no sea la misma persona."""
        if self.de == self.para:
            raise ValidationError("Una persona no puede ser su propio amigo invisible")

    def __repr__(self) -> str:
        return f"{self.de.nombre} → {self.para.nombre}"


@dataclass
class ConfigData:
    """Estructura de datos de configuración."""

    personas: list = field(default_factory=list)
    restricciones: list = field(default_factory=list)
    max_intentos: int = 100
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 465
