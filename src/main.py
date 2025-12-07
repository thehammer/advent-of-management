"""
Main entry point - orchestrates scenario generation from AoC puzzles
"""

import logging
import os
import sys
import time
from pathlib import Path

import schedule
from dotenv import load_dotenv

from .aoc_client import AoCClient
from .scenario_gen import ScenarioGenerator
from .publisher import LocalPublisher, S3Publisher

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("advent-of-management.log"),
    ],
)
logger = logging.getLogger(__name__)


class AdventOfManagementServer:
    def __init__(self, use_s3: bool = False):
        load_dotenv()

        # Validate required environment variables
        self._validate_env()

        self.year = int(os.getenv("AOC_YEAR", "2025"))
        self.aoc = AoCClient(
            os.environ["AOC_SESSION_COOKIE"],
            year=self.year,
        )
        self.generator = ScenarioGenerator(os.environ["ANTHROPIC_API_KEY"])

        if use_s3:
            self.publisher = S3Publisher(
                bucket_name=os.environ["S3_BUCKET_NAME"],
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region=os.getenv("AWS_REGION", "us-east-1"),
            )
        else:
            self.publisher = LocalPublisher("scenarios")

        self.processed_days: set[int] = set()
        self._load_processed_days()

    def _validate_env(self) -> None:
        """Validate required environment variables."""
        required = ["AOC_SESSION_COOKIE", "ANTHROPIC_API_KEY"]
        missing = [var for var in required if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    def _load_processed_days(self) -> None:
        """Load already processed days from publisher."""
        if isinstance(self.publisher, LocalPublisher):
            self.processed_days = set(self.publisher.list_scenarios(self.year))
            if self.processed_days:
                logger.info(f"Found existing scenarios for days: {sorted(self.processed_days)}")

    def process_day(self, day: int, force: bool = False) -> bool:
        """
        Process a single day: fetch puzzle and generate scenario.
        Returns True if successful.
        """
        if day in self.processed_days and not force:
            logger.info(f"Day {day} already processed, skipping")
            return True

        logger.info(f"Processing Day {day}...")

        try:
            # Fetch puzzle
            puzzle = self.aoc.get_puzzle(day)
            logger.info(f"  Fetched: {puzzle.title}")

            # Generate management scenario
            logger.info("  Generating management scenario...")
            scenario = self.generator.generate(puzzle)
            logger.info(f"  Generated: {scenario.title}")

            # Publish
            url = self.publisher.publish_scenario(scenario)
            logger.info(f"  Published to: {url}")

            # Update manifest
            self.processed_days.add(day)
            self.publisher.update_manifest(self.year, max(self.processed_days))

            logger.info(f"  Day {day} complete!")
            return True

        except Exception as e:
            logger.exception(f"  Error processing Day {day}: {e}")
            return False

    def process_new_days(self) -> None:
        """Check for and process any new AoC days."""
        try:
            available = self.aoc.get_available_days()
            logger.info(f"Available days: {available}")

            new_days = [d for d in available if d not in self.processed_days]

            if not new_days:
                logger.info("No new days to process")
                return

            for day in sorted(new_days):
                self.process_day(day)
                # Delay between days to be nice to AoC
                time.sleep(5)

        except Exception as e:
            logger.exception(f"Error checking for new days: {e}")

    def run_scheduler(self) -> None:
        """Run as a continuous scheduler."""
        logger.info(f"Starting Advent of Management server for {self.year}")

        # Check immediately on start
        self.process_new_days()

        # Then check every hour
        schedule.every().hour.do(self.process_new_days)

        logger.info("Scheduler running. Checking every hour for new puzzles.")
        while True:
            schedule.run_pending()
            time.sleep(60)

    def run_once(self, day: int | None = None) -> None:
        """Process a specific day or all available days once."""
        if day:
            self.process_day(day, force=True)
        else:
            self.process_new_days()


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Advent of Management Server")
    parser.add_argument(
        "--day",
        type=int,
        help="Process a specific day (overrides scheduler)",
    )
    parser.add_argument(
        "--scheduler",
        action="store_true",
        help="Run as continuous scheduler",
    )
    parser.add_argument(
        "--s3",
        action="store_true",
        help="Publish to S3 instead of local files",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reprocessing even if already done",
    )

    args = parser.parse_args()

    server = AdventOfManagementServer(use_s3=args.s3)

    if args.scheduler:
        server.run_scheduler()
    elif args.day:
        server.process_day(args.day, force=args.force)
    else:
        server.run_once()


if __name__ == "__main__":
    main()
