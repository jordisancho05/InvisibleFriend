"""Data models for Invisible Friend."""

import re
from dataclasses import dataclass, field

from invisible_friend.exceptions import ValidationError

# One local part, one @, one dotted domain with an alphabetic TLD. Deliberately
# conservative rather than RFC-complete: it only has to catch typos and the
# shapes that would be dangerous downstream.
_EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[A-Za-z]{2,}")


# eq=False: the dunders below are hand-written because identity is the name
# alone, not the (name, email) pair the dataclass would generate.
@dataclass(eq=False)
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
        if "\n" in self.email or "\r" in self.email:
            # A line break in an address is how SMTP headers get injected. Fail
            # here, not later when the stdlib refuses to fold the header.
            raise ValidationError("Email cannot contain a line break")
        if not self._is_valid_email(self.email):
            raise ValidationError(f"Invalid email: {self.email}")

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Check the shape of an email address."""
        return _EMAIL_PATTERN.fullmatch(email) is not None

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
