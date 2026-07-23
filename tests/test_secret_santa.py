"""Tests for SecretSantaService.

The service shuffles at random, so these tests pin **invariants** over many
runs, never one concrete expected mapping.
"""

import pytest

from invisible_friend.exceptions import AssignmentError
from invisible_friend.models import Person
from invisible_friend.services.secret_santa import SecretSantaService
from invisible_friend.validators import PairValidator

REPETITIONS = 25


def test_everyone_gives_and_receives_exactly_once(
    service: SecretSantaService, participants: list[Person]
) -> None:
    """n participants produce n edges, with no repeated giver or receiver."""
    for _ in range(REPETITIONS):
        assignments = service.generate_assignments(participants)

        assert len(assignments) == len(participants)
        assert set(assignments.keys()) == set(participants)
        assert sorted(p.name for p in assignments.values()) == sorted(p.name for p in participants)


def test_nobody_is_assigned_to_themselves(
    service: SecretSantaService, participants: list[Person]
) -> None:
    """There are no fixed points in the permutation."""
    for _ in range(REPETITIONS):
        assignments = service.generate_assignments(participants)

        for giver, receiver in assignments.items():
            assert giver != receiver


def test_no_assignment_violates_the_restrictions(
    service: SecretSantaService, validator: PairValidator, participants: list[Person]
) -> None:
    """No generated edge is a forbidden pair."""
    for _ in range(REPETITIONS):
        assignments = service.generate_assignments(participants)

        for giver, receiver in assignments.items():
            assert validator.is_valid_pair(giver, receiver)


def test_the_result_is_a_single_cycle(
    service: SecretSantaService, participants: list[Person]
) -> None:
    """Following n hops from anyone returns to the start having seen everyone.

    This rules out the permutation splitting into sub-cycles (e.g. two pairs
    gifting each other and ignoring the rest).
    """
    for _ in range(REPETITIONS):
        assignments = service.generate_assignments(participants)

        start = participants[0]
        visited = []
        current = start
        for _hop in range(len(participants)):
            current = assignments[current]
            visited.append(current)

        assert current == start, "the walk does not return to the starting point"
        assert len(set(visited)) == len(participants), "there are sub-cycles"


def test_fewer_than_two_participants_raises_assignment_error(
    service: SecretSantaService,
) -> None:
    """With a single person there is no possible secret friend."""
    with pytest.raises(AssignmentError, match="[Aa]t least 2"):
        service.generate_assignments([Person("Alice", "alice@example.com")])


def test_empty_list_raises_assignment_error(service: SecretSantaService) -> None:
    """With no participants there is nothing to assign either."""
    with pytest.raises(AssignmentError):
        service.generate_assignments([])


def test_unsatisfiable_restrictions_raise_assignment_error() -> None:
    """If the restrictions make the problem impossible, it fails instead of hanging."""
    two = [Person("Alice", "alice@example.com"), Person("Bob", "bob@example.com")]
    validator = PairValidator([["Alice", "Bob"]])
    service = SecretSantaService(validator, max_attempts=20)

    with pytest.raises(AssignmentError, match="20 attempts"):
        service.generate_assignments(two)


def test_get_formatted_assignments_returns_names(
    service: SecretSantaService, participants: list[Person]
) -> None:
    """The formatted version maps name → name, ready for JSON and email."""
    assignments = service.generate_assignments(participants)

    formatted = service.get_formatted_assignments(assignments)

    assert set(formatted) == {p.name for p in participants}
    assert all(isinstance(k, str) and isinstance(v, str) for k, v in formatted.items())


def test_print_assignments_shows_every_pair(
    service: SecretSantaService,
    participants: list[Person],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The console output includes one line per participant."""
    assignments = service.generate_assignments(participants)

    service.print_assignments(assignments)

    output = capsys.readouterr().out
    for person in participants:
        assert person.name in output
