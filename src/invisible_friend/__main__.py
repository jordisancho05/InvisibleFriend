"""Application entry point.

    python -m invisible_friend            # simulate the delivery (default)
    python -m invisible_friend --send     # actually send the emails

Real delivery is always explicit: without `--send` no SMTP connection is opened.
"""

import argparse
import sys
from pathlib import Path

from invisible_friend import __version__
from invisible_friend.config import Config
from invisible_friend.exceptions import InvisibleFriendError
from invisible_friend.services.email_service import EmailService
from invisible_friend.services.secret_santa import SecretSantaService
from invisible_friend.utils.file_handler import FileHandler
from invisible_friend.utils.logger import get_logger
from invisible_friend.validators import PairValidator

logger = get_logger(__name__)

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
        self.email_service = EmailService(
            self.config.smtp_server,
            self.config.smtp_port,
            self.config.email_sender,
            self.config.email_password,
        )

    def generate_assignments(self) -> dict:
        """
        Generate the Secret Santa assignments.

        Returns:
            Assignments dict
        """
        try:
            return self.secret_santa_service.generate_assignments(self.config.participants)
        except InvisibleFriendError as e:
            logger.error(f"Error generating assignments: {e}")
            raise

    def show_assignments(self, assignments: dict) -> None:
        """
        Print the assignments to the console.

        Args:
            assignments: Assignments dict
        """
        self.secret_santa_service.print_assignments(assignments)

    def save_assignments(self, assignments: dict, path: Path = DEFAULT_OUTPUT) -> None:
        """
        Save the assignments to a JSON file.

        Args:
            assignments: Assignments dict
            path: Where to save
        """
        formatted = self.secret_santa_service.get_formatted_assignments(assignments)
        FileHandler.save_assignments(path, formatted)
        logger.info(f"Assignments saved to {path}")

    def send_emails(self, assignments: dict, simulate: bool = True) -> tuple[int, int]:
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

        return self.email_service.send_assignments(formatted, emails, simulate=simulate)

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

        logger.info(f"STEP 4: {'Sending' if send else 'Simulating'} emails...")
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
    try:
        app = InvisibleFriendApp(args.config)
        app.run(send=args.send, output_path=args.output)
    except InvisibleFriendError as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        return 1
    except Exception as e:  # noqa: BLE001 - last-resort CLI safety net
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"❌ Fatal error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
