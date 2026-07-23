"""Core service that generates the Secret Santa assignments."""

import random

from invisible_friend.exceptions import AssignmentError
from invisible_friend.models import Person
from invisible_friend.utils.logger import get_logger
from invisible_friend.validators import PairValidator

logger = get_logger(__name__)


class SecretSantaService:
    """Generates valid Secret Santa assignments."""

    def __init__(self, validator: PairValidator, max_attempts: int = 100) -> None:
        """
        Initialize the service.

        Args:
            validator: Pair validator
            max_attempts: Maximum number of attempts to generate assignments
        """
        self.validator = validator
        self.max_attempts = max_attempts

    def generate_assignments(self, participants: list[Person]) -> dict[Person, Person]:
        """
        Generate a valid cycle of assignments.

        Each person has exactly one secret friend and is the secret friend of exactly one.
        It forms a cycle: person[i] -> person[(i+1) % n].

        Args:
            participants: List of participants

        Returns:
            Dict {person: secret_friend}

        Raises:
            AssignmentError: If no valid cycle can be generated
        """
        if len(participants) < 2:
            raise AssignmentError("At least 2 participants are required")

        logger.info(f"Generating assignments for {len(participants)} participants")

        for attempt in range(self.max_attempts):
            # Copy and shuffle.
            shuffled = participants.copy()
            random.shuffle(shuffled)

            # Validate that the cycle is valid.
            if self.validator.validate_cycle(shuffled):
                # Build the assignments dict.
                assignments = {
                    shuffled[i]: shuffled[(i + 1) % len(shuffled)] for i in range(len(shuffled))
                }

                logger.info(f"Assignments generated successfully on attempt {attempt + 1}")
                return assignments

        error_msg = f"Could not generate valid assignments after {self.max_attempts} attempts"
        logger.error(error_msg)
        raise AssignmentError(error_msg)

    def get_formatted_assignments(self, assignments: dict[Person, Person]) -> dict[str, str]:
        """
        Convert assignments to a name -> name mapping.

        Args:
            assignments: Assignments dict

        Returns:
            Dict of names
        """
        return {giver.name: receiver.name for giver, receiver in assignments.items()}

    def print_assignments(self, assignments: dict[Person, Person]) -> None:
        """
        Print the assignments in a readable format.

        Args:
            assignments: Assignments dict
        """
        logger.info("=== SECRET SANTA ASSIGNMENTS ===")
        for giver, receiver in assignments.items():
            email = giver.email if giver.email else "[no email]"
            print(f"  {giver.name} (email: {email}) -> {receiver.name}")
            logger.debug(f"Assignment: {giver.name} -> {receiver.name}")
