"""Validators for pairs and restrictions."""

from invisible_friend.exceptions import ValidationError
from invisible_friend.models import Person


class PairValidator:
    """Decides whether two people may be assigned as secret friends."""

    def __init__(self, restrictions: list[list[str]]) -> None:
        """
        Initialize the validator.

        Args:
            restrictions: List of name pairs that must not be assigned together
        """
        # Store as frozensets for efficient bidirectional lookup.
        self.restrictions: set[frozenset[str]] = {frozenset(pair) for pair in restrictions}

    def is_valid_pair(self, person1: Person, person2: Person) -> bool:
        """
        Check whether two people may be assigned together.

        Args:
            person1: First person
            person2: Second person

        Returns:
            True if the pair is valid, False otherwise
        """
        if person1 == person2:
            return False

        pair = frozenset([person1.name, person2.name])
        return pair not in self.restrictions

    def validate_cycle(self, ordered_participants: list[Person]) -> bool:
        """
        Validate that a full cycle is valid.

        Args:
            ordered_participants: People in cyclic assignment order

        Returns:
            True if every assignment is valid
        """
        if not ordered_participants:
            raise ValidationError("Empty participant list")

        for i, person in enumerate(ordered_participants):
            next_person = ordered_participants[(i + 1) % len(ordered_participants)]
            if not self.is_valid_pair(person, next_person):
                return False

        return True

    def add_restriction(self, person1: str, person2: str) -> None:
        """Add a new restriction."""
        self.restrictions.add(frozenset([person1, person2]))

    def remove_restriction(self, person1: str, person2: str) -> None:
        """Remove an existing restriction."""
        self.restrictions.discard(frozenset([person1, person2]))

    def get_restrictions(self) -> list[tuple[str, ...]]:
        """Return every restriction as a sorted tuple."""
        return [tuple(sorted(pair)) for pair in self.restrictions]
