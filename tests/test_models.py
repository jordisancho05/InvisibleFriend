"""Tests for the domain models: Person, Assignment, GiftDetails and ConfigData."""

import pytest

from invisible_friend.exceptions import ValidationError
from invisible_friend.models import Assignment, ConfigData, GiftDetails, Person


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
    assert data.gift == GiftDetails()


def test_gift_details_default_to_24_december_and_a_30_minimum() -> None:
    """Without a gift section the email keeps the details it already had."""
    gift = GiftDetails()

    assert (gift.exchange_day, gift.exchange_month) == (24, 12)
    assert gift.min_budget == 30
    assert gift.max_budget is None


@pytest.mark.parametrize(
    ("day", "month"),
    [(24, 0), (24, 13), (0, 12), (32, 12), (31, 4), (30, 2)],
    ids=["month 0", "month 13", "day 0", "day 32", "31 April", "30 February"],
)
def test_gift_details_reject_a_date_that_does_not_exist(day: int, month: int) -> None:
    """An impossible exchange date fails at load time, not in every inbox."""
    with pytest.raises(ValidationError):
        GiftDetails(exchange_day=day, exchange_month=month)


def test_gift_details_accept_29_february() -> None:
    """No year is configured, so a leap day is a valid exchange day."""
    assert GiftDetails(exchange_day=29, exchange_month=2).exchange_day == 29


def test_gift_details_reject_a_minimum_below_one() -> None:
    """A minimum of zero would print a budget that means nothing."""
    with pytest.raises(ValidationError, match="minimum"):
        GiftDetails(min_budget=0)


def test_gift_details_reject_a_maximum_below_the_minimum() -> None:
    """A range upside down is a typo, not a budget."""
    with pytest.raises(ValidationError, match="maximum"):
        GiftDetails(min_budget=30, max_budget=20)


def test_gift_details_accept_a_maximum_equal_to_the_minimum() -> None:
    """Minimum == maximum is a fixed budget, a legitimate choice."""
    assert GiftDetails(min_budget=30, max_budget=30).max_budget == 30
