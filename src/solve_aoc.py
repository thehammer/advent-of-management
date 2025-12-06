"""
Standalone AoC solver that saves all artifacts for later review.

Saves to solutions/{year}/day{N}/:
  - puzzle.md       # The puzzle description
  - input.txt       # Your puzzle input
  - prompt.md       # The prompt sent to Claude
  - solution.md     # Claude's full response with code
  - answer_part1.txt
  - answer_part2.txt (if solved)
"""

import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from .aoc_client import AoCClient, AoCPuzzle
from .solver import AoCSolver

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class AoCSolverWithArtifacts:
    def __init__(self, output_dir: str = "solutions"):
        load_dotenv()

        self.year = int(os.getenv("AOC_YEAR", "2025"))
        self.output_dir = Path(output_dir)

        self.aoc = AoCClient(
            os.environ["AOC_SESSION_COOKIE"],
            year=self.year,
        )
        self.solver = AoCSolver(os.environ["ANTHROPIC_API_KEY"])

    def _get_day_dir(self, day: int) -> Path:
        """Get the output directory for a specific day."""
        day_dir = self.output_dir / str(self.year) / f"day{day:02d}"
        day_dir.mkdir(parents=True, exist_ok=True)
        return day_dir

    def _save_puzzle(self, day_dir: Path, puzzle: AoCPuzzle) -> None:
        """Save puzzle description."""
        content = f"# Day {puzzle.day}: {puzzle.title}\n\n"
        content += puzzle.description_text
        (day_dir / "puzzle.md").write_text(content)

    def _save_input(self, day_dir: Path, puzzle: AoCPuzzle) -> None:
        """Save puzzle input."""
        (day_dir / "input.txt").write_text(puzzle.input_data)

    def _save_prompt(self, day_dir: Path, prompt: str, part: int) -> None:
        """Save the prompt sent to Claude."""
        filename = f"prompt_part{part}.md"
        (day_dir / filename).write_text(prompt)

    def _save_solution(self, day_dir: Path, response: str, part: int) -> None:
        """Save Claude's full response."""
        filename = f"solution_part{part}.md"
        (day_dir / filename).write_text(response)

    def _save_answer(self, day_dir: Path, answer: str, part: int) -> None:
        """Save the extracted answer."""
        filename = f"answer_part{part}.txt"
        (day_dir / filename).write_text(answer)

    def _extract_code(self, response: str) -> str | None:
        """Extract Python code blocks from response."""
        # Find all Python code blocks
        pattern = r"```python\n(.*?)```"
        matches = re.findall(pattern, response, re.DOTALL)
        if matches:
            # Return the longest code block (usually the main solution)
            return max(matches, key=len)
        return None

    def _save_code(self, day_dir: Path, response: str, part: int) -> None:
        """Extract and save the solution code."""
        code = self._extract_code(response)
        if code:
            filename = f"code_part{part}.py"
            (day_dir / filename).write_text(code)

    def _build_prompt(self, puzzle: AoCPuzzle, part: int) -> str:
        """Build the prompt (same as solver but exposed for saving)."""
        prompt_parts = [
            f"# Advent of Code {puzzle.year} - Day {puzzle.day}: {puzzle.title}",
            "",
            "## Puzzle Description",
            puzzle.description_text,
            "",
            "## Your Input",
            "```",
            puzzle.input_data.strip(),
            "```",
            "",
            f"## Task",
            f"Solve Part {part} of this puzzle. Show your work and reasoning.",
            "",
            "Remember to end your response with: ANSWER: <your_answer>",
        ]
        return "\n".join(prompt_parts)

    def solve_day(self, day: int, submit: bool = True) -> dict:
        """
        Solve a day's puzzle and save all artifacts.
        Returns dict with results.
        """
        logger.info(f"=== Day {day} ===")
        day_dir = self._get_day_dir(day)
        results = {"day": day, "parts": {}}

        # Fetch puzzle
        logger.info("Fetching puzzle...")
        puzzle = self.aoc.get_puzzle(day)
        logger.info(f"  Title: {puzzle.title}")

        # Save puzzle and input
        self._save_puzzle(day_dir, puzzle)
        self._save_input(day_dir, puzzle)
        logger.info(f"  Saved puzzle and input to {day_dir}")

        # Solve Part 1
        logger.info("Solving Part 1...")
        prompt1 = self._build_prompt(puzzle, 1)
        self._save_prompt(day_dir, prompt1, 1)

        answer1, response1 = self.solver.solve(puzzle, part=1)
        self._save_solution(day_dir, response1, 1)
        self._save_code(day_dir, response1, 1)

        if answer1:
            self._save_answer(day_dir, answer1, 1)
            logger.info(f"  Part 1 answer: {answer1}")
            results["parts"][1] = {"answer": answer1, "submitted": False, "correct": None}

            if submit:
                success, message = self.aoc.submit_answer(day, 1, answer1)
                results["parts"][1]["submitted"] = True
                results["parts"][1]["correct"] = success
                results["parts"][1]["message"] = message

                if success:
                    logger.info(f"  Part 1 correct!")
                elif "already" in message.lower():
                    logger.info(f"  Part 1 already solved")
                    results["parts"][1]["correct"] = True
                else:
                    logger.warning(f"  Part 1: {message}")
        else:
            logger.error("  Could not extract Part 1 answer")
            results["parts"][1] = {"answer": None, "error": "Could not extract answer"}

        # Check for Part 2
        import time
        time.sleep(2)
        puzzle = self.aoc.get_puzzle(day)

        if puzzle.part2_unlocked:
            logger.info("Solving Part 2...")
            prompt2 = self._build_prompt(puzzle, 2)
            self._save_prompt(day_dir, prompt2, 2)

            answer2, response2 = self.solver.solve(puzzle, part=2)
            self._save_solution(day_dir, response2, 2)
            self._save_code(day_dir, response2, 2)

            if answer2:
                self._save_answer(day_dir, answer2, 2)
                logger.info(f"  Part 2 answer: {answer2}")
                results["parts"][2] = {"answer": answer2, "submitted": False, "correct": None}

                if submit:
                    success, message = self.aoc.submit_answer(day, 2, answer2)
                    results["parts"][2]["submitted"] = True
                    results["parts"][2]["correct"] = success
                    results["parts"][2]["message"] = message

                    if success:
                        logger.info(f"  Part 2 correct!")
                    elif "already" in message.lower():
                        logger.info(f"  Part 2 already solved")
                        results["parts"][2]["correct"] = True
                    else:
                        logger.warning(f"  Part 2: {message}")
            else:
                logger.error("  Could not extract Part 2 answer")
                results["parts"][2] = {"answer": None, "error": "Could not extract answer"}
        else:
            logger.info("  Part 2 not yet unlocked")

        # Save summary
        self._save_summary(day_dir, results)
        logger.info(f"  All artifacts saved to {day_dir}")

        return results

    def _save_summary(self, day_dir: Path, results: dict) -> None:
        """Save a summary of the solve attempt."""
        lines = [
            f"# Day {results['day']} Summary",
            f"",
            f"Solved: {datetime.now().isoformat()}",
            "",
        ]

        for part, data in results.get("parts", {}).items():
            lines.append(f"## Part {part}")
            lines.append(f"- Answer: {data.get('answer', 'N/A')}")
            if data.get("submitted"):
                status = "Correct" if data.get("correct") else f"Incorrect ({data.get('message', '')})"
                lines.append(f"- Status: {status}")
            lines.append("")

        (day_dir / "SUMMARY.md").write_text("\n".join(lines))

    def solve_all_available(self, submit: bool = True) -> list[dict]:
        """Solve all available days."""
        available = self.aoc.get_available_days()
        logger.info(f"Available days: {available}")

        results = []
        for day in available:
            day_dir = self._get_day_dir(day)
            # Skip if already solved (has summary)
            if (day_dir / "SUMMARY.md").exists():
                logger.info(f"Day {day} already solved, skipping")
                continue

            result = self.solve_day(day, submit=submit)
            results.append(result)

            import time
            time.sleep(5)  # Be nice to AoC

        return results


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="AoC Solver with Artifacts")
    parser.add_argument(
        "--day",
        type=int,
        help="Solve a specific day",
    )
    parser.add_argument(
        "--no-submit",
        action="store_true",
        help="Don't submit answers to AoC",
    )
    parser.add_argument(
        "--output",
        default="solutions",
        help="Output directory for artifacts (default: solutions)",
    )

    args = parser.parse_args()

    solver = AoCSolverWithArtifacts(output_dir=args.output)

    if args.day:
        solver.solve_day(args.day, submit=not args.no_submit)
    else:
        solver.solve_all_available(submit=not args.no_submit)


if __name__ == "__main__":
    main()
