"""
Transforms AoC puzzles into management parody scenarios
"""

import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

import anthropic

from .aoc_client import AoCPuzzle


@dataclass
class NPC:
    name: str
    role: str
    quirk: str
    secret: str


@dataclass
class SolutionStep:
    step: int
    description: str
    action_patterns: list[str]
    narrative_result: str
    state_changes: dict[str, Any]
    unlocks: str | None = None
    victory: bool = False


@dataclass
class ManagementScenario:
    day: int
    year: int
    title: str
    aoc_theme: str

    setup_narrative: str
    initial_state: dict[str, Any]

    npcs: list[NPC]
    solution_steps: list[SolutionStep]
    optimal_turn_count: int

    consequences: dict[str, str]
    hints: list[str]
    victory_message: str

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        data = asdict(self)
        # Convert NPC and SolutionStep objects
        data["npcs"] = [asdict(npc) for npc in self.npcs]
        data["solution_steps"] = [asdict(step) for step in self.solution_steps]
        return data

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> "ManagementScenario":
        """Create from dictionary."""
        npcs = [NPC(**npc) for npc in data.pop("npcs")]
        steps = [SolutionStep(**step) for step in data.pop("solution_steps")]
        return cls(npcs=npcs, solution_steps=steps, **data)


class ScenarioGenerator:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.scenario_prompt = self._load_prompt("prompts/scenario_prompt.md")

    def _load_prompt(self, path: str) -> str:
        """Load system prompt from file."""
        prompt_path = Path(path)
        if prompt_path.exists():
            return prompt_path.read_text()
        return self._default_scenario_prompt()

    def _default_scenario_prompt(self) -> str:
        return """You are a comedy writer creating "Advent of Management" scenarios - parodies of programming puzzles reimagined as absurd corporate situations.

## Your Task
Given an Advent of Code puzzle, create a management simulation scenario that:
1. Captures the THEME of the puzzle (not the algorithm)
2. Is solvable through natural language management decisions
3. Is funny in a Dilbert-meets-The-Office-meets-tech-startup way

## Theme Extraction Examples
- "Finding path through maze" → Navigating org chart to get approval
- "Sorting/matching items" → Assigning engineers to projects based on skills/politics
- "Parsing corrupted data" → Interpreting exec's vague requirements
- "Resource optimization" → Allocating headcount across competing priorities
- "State machine simulation" → Managing through a reorg
- "Pattern matching" → Decoding passive-aggressive Slack messages

## Output Format
Return valid JSON matching this exact structure (no markdown, just JSON):
{
  "title": "Catchy management-speak title",
  "aoc_theme": "Brief description of original puzzle mechanic",
  "setup_narrative": "2-3 paragraphs setting the scene with specific absurd details.",
  "initial_state": {
    "morale": 50,
    "budget": 100
  },
  "npcs": [
    {
      "name": "Human name",
      "role": "Corporate role",
      "quirk": "Their defining absurd characteristic",
      "secret": "Hidden knowledge or capability they have"
    }
  ],
  "solution_steps": [
    {
      "step": 1,
      "description": "What the player needs to do",
      "action_patterns": ["pattern1", "pattern2"],
      "narrative_result": "What happens when they do this",
      "state_changes": {"morale": 5},
      "unlocks": "What this enables (optional)",
      "victory": false
    }
  ],
  "optimal_turn_count": 3,
  "consequences": {
    "wrong_action_pattern": "Humorous consequence"
  },
  "hints": [
    "Vague hint",
    "Medium hint",
    "Almost gives it away"
  ],
  "victory_message": "Sarcastic congratulations"
}

## Tone Guidelines
- Middle management is always the problem
- The intern secretly runs everything
- HR requires forms for everything
- Executives communicate only in sports metaphors or emoji
- "Best practices" are always counterproductive
- The solution often involves admitting something obvious that politics prevented
- Technical solutions are never the answer; people/political solutions are

## Important
- The scenario must be WINNABLE in 3-6 optimal moves
- Wrong moves should create complications, not dead ends
- Include at least 3 NPCs with distinct personalities
- The "correct" path should be satisfying when discovered
- Make action_patterns generous (multiple ways to express same intent)
"""

    def _build_generation_prompt(self, puzzle: AoCPuzzle) -> str:
        """Build the prompt for scenario generation."""
        return f"""Create an Advent of Management scenario based on this Advent of Code puzzle:

## Puzzle: Day {puzzle.day} - {puzzle.title}

{puzzle.description_text}

---

Analyze the core THEME of this puzzle (the conceptual mechanic, not the code), then create a management parody scenario that captures that theme in corporate dysfunction.

Return ONLY valid JSON matching the specified format. No markdown code blocks, no explanation - just the JSON object."""

    def _extract_json(self, response_text: str) -> dict:
        """Extract JSON from response, handling various formats."""
        text = response_text.strip()

        # Remove markdown code blocks if present
        if text.startswith("```"):
            # Find the end of the code block
            lines = text.split("\n")
            # Skip first line (```json or ```)
            start = 1
            # Find closing ```
            end = len(lines)
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == "```":
                    end = i
                    break
            text = "\n".join(lines[start:end])

        # Try to find JSON object
        # Look for outermost { }
        start = text.find("{")
        if start == -1:
            raise ValueError("No JSON object found in response")

        # Find matching closing brace
        depth = 0
        end = start
        for i, char in enumerate(text[start:], start):
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break

        json_str = text[start:end]
        return json.loads(json_str)

    def generate(self, puzzle: AoCPuzzle) -> ManagementScenario:
        """Generate a management scenario from an AoC puzzle."""
        user_prompt = self._build_generation_prompt(puzzle)

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            system=self.scenario_prompt,
        )

        # Extract text
        response_text = ""
        for block in response.content:
            if block.type == "text":
                response_text += block.text

        # Parse JSON
        data = self._extract_json(response_text)

        # Add day/year
        data["day"] = puzzle.day
        data["year"] = puzzle.year

        # Validate and build scenario
        return self._validate_and_build(data)

    def _validate_and_build(self, data: dict) -> ManagementScenario:
        """Validate data and build ManagementScenario object."""
        required_fields = [
            "title", "aoc_theme", "setup_narrative", "initial_state",
            "npcs", "solution_steps", "optimal_turn_count", "consequences",
            "hints", "victory_message", "day", "year"
        ]

        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Ensure at least one solution step has victory=True
        has_victory = any(step.get("victory", False) for step in data["solution_steps"])
        if not has_victory:
            # Mark last step as victory
            data["solution_steps"][-1]["victory"] = True

        # Build NPCs
        npcs = [NPC(**npc) for npc in data["npcs"]]

        # Build solution steps
        steps = []
        for step_data in data["solution_steps"]:
            # Ensure all required fields
            step_data.setdefault("unlocks", None)
            step_data.setdefault("victory", False)
            step_data.setdefault("state_changes", {})
            steps.append(SolutionStep(**step_data))

        return ManagementScenario(
            day=data["day"],
            year=data["year"],
            title=data["title"],
            aoc_theme=data["aoc_theme"],
            setup_narrative=data["setup_narrative"],
            initial_state=data["initial_state"],
            npcs=npcs,
            solution_steps=steps,
            optimal_turn_count=data["optimal_turn_count"],
            consequences=data["consequences"],
            hints=data["hints"],
            victory_message=data["victory_message"],
        )

    def regenerate_with_feedback(
        self,
        puzzle: AoCPuzzle,
        previous_scenario: ManagementScenario,
        feedback: str
    ) -> ManagementScenario:
        """Regenerate scenario with human feedback."""
        user_prompt = self._build_generation_prompt(puzzle)
        user_prompt += f"""

## Previous Attempt

{previous_scenario.to_json()}

## Feedback

{feedback}

Please generate an improved version addressing this feedback."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            system=self.scenario_prompt,
        )

        response_text = ""
        for block in response.content:
            if block.type == "text":
                response_text += block.text

        data = self._extract_json(response_text)
        data["day"] = puzzle.day
        data["year"] = puzzle.year

        return self._validate_and_build(data)
