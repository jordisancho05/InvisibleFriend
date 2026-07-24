"""Application entry point.

    python -m invisible_friend            # simulate the delivery (default)
    python -m invisible_friend --send     # actually send the emails
    python -m invisible_friend --debug    # also record the draw in the log

Real delivery is always explicit: without `--send` no SMTP connection is opened,
and no credential is read.
"""

import argparse
import sys
from pathlib import Path

from invisible_friend import __version__
from invisible_friend.config import Config
from invisible_friend.exceptions import InvisibleFriendError
from invisible_friend.models import Person
from invisible_friend.services.email_service import EmailService
from invisible_friend.services.secret_santa import SecretSantaService
from invisible_friend.utils.file_handler import FileHandler
from invisible_friend.utils.logger import configure_logging, get_logger
from invisible_friend.validators import PairValidator

# Named explicitly rather than with __name__: `python -m invisible_friend` runs
# this file as "__main__", which is not a child of the package logger, so its
# records would reach no handler and the whole flow would vanish from the log.
logger = get_logger("invisible_friend.__main__")

DEFAULT_CONFIG = Path("config/settings.yaml")
DEFAULT_OUTPUT = Path("output/assignments.json")


class InvisibleFriendApp:
    """Orchestrates the full flow: generate, show, save and deliver."""

    def __init__(self, config_path: Path = DEFAULT_CONFIG) -> None:
        """
        Initialize the application.

        Args:
            config_path: Path to the YAML configuration
        """
        logger.info("Initializing Invisible Friend application")
        self.config = Config(config_path)
        self.validator = PairValidator(self.config.restrictions)
        self.secret_santa_service = SecretSantaService(self.validator, self.config.max_attempts)

    def _build_email_service(self, simulate: bool) -> EmailService:
        """
        Build the email service for this run.

        The credentials are read here and nowhere else, so a simulated run works
        on a checkout with no `.env` at all — it never opens a connection, so it
        has no business demanding a password.

        Args:
            simulate: If True, no credential is read from the environment

        Returns:
            An EmailService, without credentials when simulating
        """
        if simulate:
            return EmailService(self.config.smtp_server, self.config.smtp_port, "", "")

        return EmailService(
            self.config.smtp_server,
            self.config.smtp_port,
            self.config.email_sender,
            self.config.email_password,
        )

    def generate_assignments(self) -> dict[Person, Person]:
        """
        Generate the Secret Santa assignments.

        Returns:
            Assignments dict
        """
        try:
            return self.secret_santa_service.generate_assignments(self.config.participants)
        except InvisibleFriendError as e:
            logger.error("Error generating assignments: %s", e)
            raise

    def show_assignments(self, assignments: dict[Person, Person]) -> None:
        """
        Print the assignments to the console.

        Args:
            assignments: Assignments dict
        """
        self.secret_santa_service.print_assignments(assignments)

    def save_assignments(
        self, assignments: dict[Person, Person], path: Path = DEFAULT_OUTPUT
    ) -> None:
        """
        Save the assignments to a JSON file.

        Args:
            assignments: Assignments dict
            path: Where to save
        """
        formatted = self.secret_santa_service.get_formatted_assignments(assignments)
        FileHandler.save_assignments(path, formatted)
        logger.info("Assignments saved to %s", path)

    def send_emails(
        self, assignments: dict[Person, Person], simulate: bool = True
    ) -> tuple[int, int]:
        """
        Send the assignment emails.

        Args:
            assignments: Assignments dict
            simulate: If True, only simulate without sending

        Returns:
            Tuple (successful, failed)
        """
        formatted = self.secret_santa_service.get_formatted_assignments(assignments)
        emails = {p.name: p.email for p in self.config.participants}
        email_service = self._build_email_service(simulate)

        return email_service.send_assignments(formatted, emails, simulate=simulate)

    def run(self, send: bool = False, output_path: Path = DEFAULT_OUTPUT) -> None:
        """
        Run the full application flow.

        Args:
            send: If True, actually send the emails; otherwise only simulate
            output_path: Where to save the assignments JSON
        """
        logger.info("=" * 50)
        logger.info("STARTING FULL SECRET SANTA FLOW")
        logger.info("=" * 50)

        logger.info("STEP 1: Generating assignments...")
        assignments = self.generate_assignments()

        logger.info("STEP 2: Showing assignments...")
        self.show_assignments(assignments)

        logger.info("STEP 3: Saving assignments...")
        self.save_assignments(assignments, output_path)

        logger.info("STEP 4: %s emails...", "Sending" if send else "Simulating")
        successful, failed = self.send_emails(assignments, simulate=not send)
        print(f"\n✓ Emails {'sent' if send else 'simulated'}: {successful}")
        if failed > 0:
            print(f"✗ Failed emails: {failed}")

        logger.info("=" * 50)
        logger.info("FLOW COMPLETED SUCCESSFULLY")
        logger.info("=" * 50)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """
    Define and parse the command-line arguments.

    Args:
        argv: Arguments to parse (None = sys.argv)

    Returns:
        Namespace with send, config and output
    """
    parser = argparse.ArgumentParser(
        prog="invisible-friend",
        description="Generate the Secret Santa assignments and deliver them by email.",
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="actually send the emails (by default it only simulates)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="record the draw itself in the log file (off by default, so a normal run "
        "logs only that a message went out, never who was drawn for whom)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help=f"path to the participants YAML (default: {DEFAULT_CONFIG})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"where to save the assignments JSON (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """
    Run the application from the command line.

    Args:
        argv: Arguments to parse (None = sys.argv)

    Returns:
        0 on success, 1 on a controlled failure
    """
    args = parse_args(argv)
    # First thing, so even a failure while loading the config is logged at the
    # level the user asked for.
    configure_logging(debug=args.debug)
    try:
        app = InvisibleFriendApp(args.config)
        app.run(send=args.send, output_path=args.output)
    except InvisibleFriendError as e:
        logger.error("Error: %s", e)
        print(f"❌ Error: {e}")
        return 1
    except Exception as e:  # noqa: BLE001 - last-resort CLI safety net
        logger.exception("Fatal error: %s", e)
        print(f"❌ Fatal error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
