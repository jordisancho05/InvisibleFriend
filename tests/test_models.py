"""Tests for the domain models: Person, Assignment and ConfigData."""

import pytest

from invisible_friend.exceptions import ValidationError
from invisible_friend.models import Assignment, ConfigData, Person


def test_valid_person_keeps_its_data() -> None:
    """A well-formed person stores name and email as given."""
    person = Person("Alice", "alice@example.com")

    assert person.name == "Alice"
    assert person.email == "alice@example.com"


@pytest.mark.parametrize(
    ("name", "email"),
    [
        ("", "alice@example.com"),
        ("Alice", ""),
        ("Alice", "no-at-sign"),
        ("Alice", "domain@without-dot"),
        ("Alice", "a@b."),
        ("Alice", "a@ .c"),
        ("Alice", '"@.'),
        ("Alice", "two@at@signs.com"),
        ("Alice", "spaced address@example.com"),
    ],
    ids=[
        "empty name",
        "empty email",
        "email without @",
        "domain without dot",
        "domain without TLD",
        "space in the domain",
        "quote as local part",
        "two @ signs",
        "space in the local part",
    ],
)
def test_invalid_person_raises_validation_error(name: str, email: str) -> None:
    """Both the name and a reasonably shaped email are required."""
    with pytest.raises(ValidationError):
        Person(name, email)


@pytest.mark.parametrize(
    "email",
    [
        "alice\n@example.com",
        "alice@example.com\nBcc: victim@example.com",
        "alice@example.com\rBcc: victim@example.com",
    ],
    ids=["newline in local part", "injected Bcc header", "carriage return"],
)
def test_email_with_a_line_break_is_rejected(email: str) -> None:
    """A line break in an address is an SMTP header-injection attempt.

    It must fail when the participant is built, not later when the stdlib
    refuses to fold the header at send time.
    """
    with pytest.raises(ValidationError, match="[Ll]ine break"):
        Person("Alice", email)


@pytest.mark.parametrize(
    "email",
    [
        "alice@example.com",
        "alice+santa@example.com",
        "alice.smith@mail.example.co.uk",
        "alice_2026@example-mail.org",
    ],
    ids=["plain", "plus addressing", "subdomain and two-part TLD", "underscore and dash"],
)
def test_ordinary_addresses_are_accepted(email: str) -> None:
    """The stricter check must not reject the shapes real people use."""
    assert Person("Alice", email).email == email


def test_two_people_with_the_same_name_are_the_same() -> None:
    """Identity is the name: the email does not distinguish participants."""
    one = Person("Alice", "alice@example.com")
    other = Person("Alice", "another-address@example.com")

    assert one == other
    assert len({one, other}) == 1


def test_people_with_different_names_are_not_equal() -> None:
    """Different names are different participants."""
    assert Person("Alice", "alice@example.com") != Person("Bob", "bob@example.com")


def test_person_is_not_equal_to_another_type() -> None:
    """Comparing with a non-Person returns False, it does not blow up."""
    assert Person("Alice", "alice@example.com") != "Alice"


def test_person_repr_is_readable() -> None:
    """The repr shows name and email, useful in test failures."""
    assert repr(Person("Alice", "alice@example.com")) == (
        "Person(name='Alice', email='alice@example.com')"
    )


def test_assignment_between_different_people() -> None:
    """A normal assignment is built without issues."""
    alice = Person("Alice", "alice@example.com")
    bob = Person("Bob", "bob@example.com")

    assignment = Assignment(alice, bob)

    assert assignment.giver == alice
    assert assignment.receiver == bob
    assert repr(assignment) == "Alice → Bob"


def test_assignment_to_oneself_raises_validation_error() -> None:
    """Nobody can be their own secret friend."""
    alice = Person("Alice", "alice@example.com")

    with pytest.raises(ValidationError):
        Assignment(alice, alice)


def test_config_data_has_sensible_defaults() -> None:
    """An empty ConfigData starts with the project defaults."""
    data = ConfigData()

    assert data.participants == []
    assert data.restrictions == []
    assert data.max_attempts == 100
    assert data.smtp_server == "smtp.gmail.com"
    assert data.smtp_port == 465
