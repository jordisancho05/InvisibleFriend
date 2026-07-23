"""Excepciones personalizadas para Invisible Friend."""


class InvisibleFriendError(Exception):
    """Excepción base para el proyecto Invisible Friend."""
    pass


class ConfigError(InvisibleFriendError):
    """Error en la configuración."""
    pass


class EmailError(InvisibleFriendError):
    """Error al enviar email."""
    pass


class ValidationError(InvisibleFriendError):
    """Error de validación."""
    pass


class AssignmentError(InvisibleFriendError):
    """Error al generar asignaciones."""
    pass
