"""Custom exceptions for Invisible Friend."""


class InvisibleFriendError(Exception):
    """Base exception for the Invisible Friend project."""

    pass


class ConfigError(InvisibleFriendError):
    """Configuration error."""

    pass


class EmailError(InvisibleFriendError):
    """Error while sending an email."""

    pass


class ValidationError(InvisibleFriendError):
    """Validation error."""

    pass


class AssignmentError(InvisibleFriendError):
    """Error while generating the assignments."""

    pass
