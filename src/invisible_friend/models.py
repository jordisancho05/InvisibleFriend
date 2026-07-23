"""Data models for Invisible Friend."""

from dataclasses import dataclass, field

from invisible_friend.exceptions import ValidationError


@dataclass
class Person:
    """A participant in the Secret Santa draw."""

    name: str
    email: str  # Email is REQUIRED

    def __post_init__(self) -> None:
        """Validate the data right after initialization."""
        if not self.name or not isinstance(self.name, str):
            raise ValidationError("Name must be a non-empty string")
        if not self.email or not isinstance(self.email, str):
            raise ValidationError("Email is required")
        if not self._is_valid_email(self.email):
            raise ValidationError(f"Invalid email: {self.email}")

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Check the basic shape of an email address."""
        return "@" in email and "." in email.split("@")[1]

    def __repr__(self) -> str:
        return f"Person(name='{self.name}', email='{self.email}')"

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Person):
            return self.name == other.name
        return False


@dataclass
class Assignment:
    """A Secret Santa assignment: who gives to whom."""

    giver: Person
    receiver: Person

    def __post_init__(self) -> None:
        """Reject a person assigned to themselves."""
        if self.giver == self.receiver:
            raise ValidationError("A person cannot be their own secret friend")

    def __repr__(self) -> str:
        return f"{self.giver.name} → {self.receiver.name}"


@dataclass
class ConfigData:
    """Container for the parsed configuration."""

    participants: list[Person] = field(default_factory=list)
    restrictions: list[list[str]] = field(default_factory=list)
    max_attempts: int = 100
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 465
