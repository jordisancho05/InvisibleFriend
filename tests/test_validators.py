"""Tests for PairValidator: symmetric restrictions and cycle validation."""

import pytest

from invisible_friend.exceptions import ValidationError
from invisible_friend.models import Person
from invisible_friend.validators import PairValidator


def find(participants: list[Person], name: str) -> Person:
    """Return the participant with that name (readability helper)."""
    return next(p for p in participants if p.name == name)


def test_allowed_pair_is_valid(validator: PairValidator, participants: list[Person]) -> None:
    """Two participants with no restriction between them may be paired."""
    assert validator.is_valid_pair(find(participants, "Alice"), find(participants, "Charlie"))
    assert validator.is_valid_pair(find(participants, "Bob"), find(participants, "Diana"))


@pytest.mark.parametrize(
    ("one", "other"),
    [
        ("Alice", "Bob"),
        ("Bob", "Alice"),
        ("Charlie", "Diana"),
        ("Diana", "Charlie"),
    ],
)
def test_forbidden_pair_is_rejected_both_ways(
    validator: PairValidator, participants: list[Person], one: str, other: str
) -> None:
    """The restriction is symmetric: A-B and B-A are rejected alike."""
    assert not validator.is_valid_pair(find(participants, one), find(participants, other))


def test_nobody_can_be_their_own_secret_friend(
    validator: PairValidator, participants: list[Person]
) -> None:
    """A person with themselves is never a valid pair."""
    alice = find(participants, "Alice")
    assert not validator.is_valid_pair(alice, alice)


def test_cycle_without_forbidden_pairs_is_valid(
    validator: PairValidator, participants: list[Person]
) -> None:
    """Alice → Charlie → Bob → Diana → Alice violates no restriction."""
    cycle = [
        find(participants, "Alice"),
        find(participants, "Charlie"),
        find(participants, "Bob"),
        find(participants, "Diana"),
    ]
    assert validator.validate_cycle(cycle)


def test_cycle_with_forbidden_pair_is_invalid(
    validator: PairValidator, participants: list[Person]
) -> None:
    """A single forbidden edge invalidates the whole cycle."""
    cycle = [
        find(participants, "Alice"),
        find(participants, "Bob"),
        find(participants, "Charlie"),
        find(participants, "Diana"),
    ]
    assert not validator.validate_cycle(cycle)


def test_cycle_checks_the_wrap_around(validator: PairValidator, participants: list[Person]) -> None:
    """The last edge wraps back to the start and is validated too."""
    # Charlie → Alice → Diana → ... → Charlie: the closing Diana→Charlie is forbidden.
    cycle = [
        find(participants, "Charlie"),
        find(participants, "Alice"),
        find(participants, "Diana"),
    ]
    assert not validator.validate_cycle(cycle)


def test_empty_cycle_raises_validation_error(validator: PairValidator) -> None:
    """Validating an empty list is a usage error, not a valid cycle."""
    with pytest.raises(ValidationError):
        validator.validate_cycle([])


def test_add_restriction(validator: PairValidator, participants: list[Person]) -> None:
    """A restriction added at runtime starts being rejected."""
    validator.add_restriction("Alice", "Charlie")

    assert not validator.is_valid_pair(find(participants, "Alice"), find(participants, "Charlie"))


def test_remove_restriction(validator: PairValidator, participants: list[Person]) -> None:
    """Removing a restriction makes the pair valid again."""
    validator.remove_restriction("Alice", "Bob")

    assert validator.is_valid_pair(find(participants, "Alice"), find(participants, "Bob"))


def test_get_restrictions_returns_sorted_tuples(validator: PairValidator) -> None:
    """Restrictions are exposed as sorted tuples, independent of input order."""
    assert sorted(validator.get_restrictions()) == [
        ("Alice", "Bob"),
        ("Charlie", "Diana"),
    ]
