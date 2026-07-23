"""Demonstration script for the package's functionality.

It is not part of the application: it shows the API in action without sending
any email. Run it from the project root, because `demo_config()` resolves
`config/settings.yaml` relative to the current directory:

    python scripts/demo.py
"""

from pathlib import Path

from invisible_friend.config import Config
from invisible_friend.models import Person
from invisible_friend.services.secret_santa import SecretSantaService
from invisible_friend.utils.logger import get_logger
from invisible_friend.validators import PairValidator

logger = get_logger(__name__)


def demo_basic() -> None:
    """Basic feature demonstration."""
    print("\n" + "=" * 60)
    print("🎁 DEMO - INVISIBLE FRIEND")
    print("=" * 60 + "\n")

    # 1. Create participants manually.
    print("1️⃣  Creating participants...")
    participants = [
        Person("Alice", "alice@example.com"),
        Person("Bob", "bob@example.com"),
        Person("Charlie", "charlie@example.com"),
        Person("Diana", "diana@example.com"),
    ]
    print(f"   ✓ {len(participants)} participants created\n")

    # 2. Create a validator with restrictions.
    print("2️⃣  Configuring restrictions...")
    restrictions = [["Alice", "Bob"]]
    validator = PairValidator(restrictions)
    print(f"   ✓ {len(restrictions)} restriction(s) configured\n")

    # 3. Validate pairs.
    print("3️⃣  Validating pairs...")
    print(f"   Alice - Bob: {validator.is_valid_pair(participants[0], participants[1])}")
    print(f"   Alice - Charlie: {validator.is_valid_pair(participants[0], participants[2])}\n")

    # 4. Generate assignments.
    print("4️⃣  Generating assignments...")
    service = SecretSantaService(validator, max_attempts=100)
    assignments = service.generate_assignments(participants)
    print("   ✓ Assignments generated!\n")

    # 5. Show assignments.
    print("5️⃣  Showing assignments:")
    service.print_assignments(assignments)
    print()


def demo_config() -> None:
    """Demonstration loading configuration from YAML."""
    print("\n" + "=" * 60)
    print("⚙️  DEMO - LOADING CONFIGURATION")
    print("=" * 60 + "\n")

    try:
        config = Config(Path("config/settings.yaml"))

        print(f"📋 Participants loaded: {len(config.participants)}")
        for person in config.participants[:3]:
            print(f"   - {person.name} ({person.email or 'no email'})")

        print(f"\n🚫 Restrictions: {len(config.restrictions)}")
        for restriction in config.restrictions[:2]:
            print(f"   - {restriction[0]} ≠ {restriction[1]}")

        print("\n⚡ SMTP configuration:")
        print(f"   - Server: {config.smtp_server}")
        print(f"   - Port: {config.smtp_port}")
        print(f"   - Max attempts: {config.max_attempts}\n")

    except Exception as e:
        print(f"❌ Error loading configuration: {e}\n")


def demo_errors() -> None:
    """Demonstration of error handling."""
    print("\n" + "=" * 60)
    print("🔴 DEMO - ERROR HANDLING")
    print("=" * 60 + "\n")

    from invisible_friend.exceptions import ValidationError

    # Try to create a person with an invalid email.
    print("1️⃣  Trying to create a person with an invalid email...")
    try:
        Person("Juan", "invalid_email")
    except ValidationError as e:
        print(f"   ✓ Error caught: {e}\n")

    # Try to assign a person to themselves.
    print("2️⃣  Trying to assign a person to themselves...")
    try:
        from invisible_friend.models import Assignment

        p = Person("Juan", "juan@example.com")
        Assignment(p, p)
    except ValidationError as e:
        print(f"   ✓ Error caught: {e}\n")


if __name__ == "__main__":
    demo_basic()
    demo_config()
    demo_errors()

    print("✅ Demonstrations complete!\n")
