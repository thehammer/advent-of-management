"""
Uses Claude API to solve AoC puzzles
"""

import re
from pathlib import Path

import anthropic

from .aoc_client import AoCPuzzle


class AoCSolver:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.solver_prompt = self._load_prompt("prompts/solver_prompt.md")

    def _load_prompt(self, path: str) -> str:
        """Load system prompt from file."""
        prompt_path = Path(path)
        if prompt_path.exists():
            return prompt_path.read_text()
        # Fallback to default prompt
        return self._default_solver_prompt()

    def _default_solver_prompt(self) -> str:
        return """You are an expert competitive programmer solving Advent of Code puzzles.

## Instructions
1. Read the puzzle carefully, noting all constraints and edge cases
2. Work through the example step by step to verify understanding
3. Write clean, correct Python code to solve the puzzle
4. Run your code mentally against the provided input
5. Return ONLY the final answer on the last line, prefixed with "ANSWER: "

## Important
- Answers are typically integers or short strings
- Check your work against the example before finalizing
- For Part 2, the puzzle builds on Part 1 but often requires a different approach
- Show your reasoning, then provide the answer

## Output Format
After your analysis and solution, end with exactly:
ANSWER: <your_answer>
"""

    def _build_puzzle_prompt(self, puzzle: AoCPuzzle, part: int) -> str:
        """Build the user prompt with puzzle details."""
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

    def _extract_answer(self, response_text: str) -> str | None:
        """Extract the answer from Claude's response."""
        # Look for ANSWER: pattern
        patterns = [
            r"ANSWER:\s*(.+?)(?:\n|$)",
            r"The answer is[:\s]+(.+?)(?:\n|$)",
            r"Final answer[:\s]+(.+?)(?:\n|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                answer = match.group(1).strip()
                # Clean up common artifacts
                answer = answer.strip("`'\"")
                # Remove trailing punctuation
                answer = answer.rstrip(".,!")
                return answer

        # Last resort: look for the last number or word on its own line
        lines = response_text.strip().split("\n")
        for line in reversed(lines):
            line = line.strip()
            if line and not line.startswith("#") and len(line) < 50:
                # Could be an answer
                return line.strip("`'\".,!")

        return None

    def solve(self, puzzle: AoCPuzzle, part: int = 1, use_extended_thinking: bool = True) -> tuple[str | None, str]:
        """
        Solve a puzzle part.
        Returns: (answer, full_response)
        """
        user_prompt = self._build_puzzle_prompt(puzzle, part)

        if use_extended_thinking:
            # Use Claude with extended thinking for complex puzzles
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=16000,
                thinking={
                    "type": "enabled",
                    "budget_tokens": 10000
                },
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                system=self.solver_prompt,
            )
        else:
            # Standard request
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8000,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                system=self.solver_prompt,
            )

        # Extract text from response
        full_response = ""
        for block in response.content:
            if block.type == "text":
                full_response += block.text
            elif block.type == "thinking":
                # Include thinking in logs but not in answer extraction
                pass

        answer = self._extract_answer(full_response)
        return answer, full_response

    def solve_with_retry(
        self,
        puzzle: AoCPuzzle,
        part: int = 1,
        max_retries: int = 3,
        feedback: str | None = None
    ) -> tuple[str | None, str]:
        """
        Solve with retries, optionally incorporating feedback from wrong answers.
        """
        user_prompt = self._build_puzzle_prompt(puzzle, part)

        if feedback:
            user_prompt += f"\n\n## Previous Attempt Feedback\n{feedback}\n\nPlease try again with this information."

        for attempt in range(max_retries):
            answer, response = self.solve(puzzle, part, use_extended_thinking=True)

            if answer:
                return answer, response

            # If no answer extracted, try again with more explicit instruction
            if attempt < max_retries - 1:
                user_prompt += "\n\nIMPORTANT: Make sure to end your response with 'ANSWER: <your_answer>'"

        return None, response
