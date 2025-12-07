"""
Transforms AoC puzzles into management parody scenarios with 6 difficulty levels
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
class LevelScenario:
    """A scenario variant for a specific career level."""
    career_title: str
    setup_narrative: str
    initial_state: dict[str, Any]
    npcs: list[NPC]
    solution_steps: list[SolutionStep]
    optimal_turn_count: int
    consequences: dict[str, str]
    hints: list[str]
    victory_message: str


@dataclass
class MultiLevelScenario:
    """A complete scenario with all 6 difficulty levels."""
    day: int
    year: int
    title: str
    aoc_theme: str
    levels: dict[str, LevelScenario]  # level_1 through level_6
    continuity_hooks: dict[str, str] | None = None

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        data = {
            "day": self.day,
            "year": self.year,
            "title": self.title,
            "aoc_theme": self.aoc_theme,
            "levels": {},
            "continuity_hooks": self.continuity_hooks or {}
        }

        for level_key, level in self.levels.items():
            data["levels"][level_key] = {
                "career_title": level.career_title,
                "setup_narrative": level.setup_narrative,
                "initial_state": level.initial_state,
                "npcs": [asdict(npc) for npc in level.npcs],
                "solution_steps": [asdict(step) for step in level.solution_steps],
                "optimal_turn_count": level.optimal_turn_count,
                "consequences": level.consequences,
                "hints": level.hints,
                "victory_message": level.victory_message
            }

        return data

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> "MultiLevelScenario":
        """Create from dictionary."""
        levels = {}
        for level_key, level_data in data.get("levels", {}).items():
            npcs = [NPC(**npc) for npc in level_data.get("npcs", [])]
            steps = []
            for step_data in level_data.get("solution_steps", []):
                step_data.setdefault("unlocks", None)
                step_data.setdefault("victory", False)
                step_data.setdefault("state_changes", {})
                steps.append(SolutionStep(**step_data))

            levels[level_key] = LevelScenario(
                career_title=level_data.get("career_title", ""),
                setup_narrative=level_data.get("setup_narrative", ""),
                initial_state=level_data.get("initial_state", {}),
                npcs=npcs,
                solution_steps=steps,
                optimal_turn_count=level_data.get("optimal_turn_count", 4),
                consequences=level_data.get("consequences", {}),
                hints=level_data.get("hints", []),
                victory_message=level_data.get("victory_message", "")
            )

        return cls(
            day=data.get("day", 0),
            year=data.get("year", 0),
            title=data.get("title", ""),
            aoc_theme=data.get("aoc_theme", ""),
            levels=levels,
            continuity_hooks=data.get("continuity_hooks")
        )


# Keep legacy class for backwards compatibility
@dataclass
class ManagementScenario:
    """Legacy single-level scenario (for backwards compatibility)."""
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
        self.cast_document = self._load_prompt("prompts/north_pole_cast.md")

    def _load_prompt(self, path: str) -> str:
        """Load prompt from file."""
        prompt_path = Path(path)
        if prompt_path.exists():
            return prompt_path.read_text()
        raise FileNotFoundError(f"Required prompt file not found: {path}")

    def _build_generation_prompt(self, puzzle: AoCPuzzle) -> str:
        """Build the prompt for scenario generation."""
        return f"""## OFFICIAL CAST DOCUMENT

You MUST use ONLY characters from this document. Use their EXACT names and titles.

{self.cast_document}

---

## SCENARIO PARAMETERS

**Day**: {puzzle.day} (This scenario takes place on December {puzzle.day})
**Days until Big Delivery**: {25 - puzzle.day}

---

## SOURCE PUZZLE: Day {puzzle.day} - {puzzle.title}

{puzzle.description_text}

---

## YOUR TASK

1. Analyze the core THEME of this puzzle (the conceptual mechanic, not the code)
2. Create 6 management parody scenario variants set on December {puzzle.day} at North Pole Operations
3. Each variant is for a different career level (Team Lead through C-Suite)
4. Use characters from the OFFICIAL CAST DOCUMENT above (exact names and titles!)
5. Scale difficulty appropriately for each level

Return ONLY valid JSON matching the specified format with ALL 6 LEVELS. No markdown code blocks, no explanation - just the JSON object."""

    def _extract_json(self, response_text: str) -> dict:
        """Extract JSON from response, handling various formats."""
        text = response_text.strip()

        # Remove markdown code blocks if present
        if text.startswith("```"):
            lines = text.split("\n")
            start = 1
            end = len(lines)
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == "```":
                    end = i
                    break
            text = "\n".join(lines[start:end])

        # Try to find JSON object
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

    def generate(self, puzzle: AoCPuzzle, max_retries: int = 3) -> MultiLevelScenario:
        """Generate a multi-level management scenario from an AoC puzzle."""
        user_prompt = self._build_generation_prompt(puzzle)

        last_error = None
        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=16000,  # Increased for 6 levels
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

            except (json.JSONDecodeError, ValueError) as e:
                last_error = e
                if attempt < max_retries - 1:
                    print(f"  Attempt {attempt + 1} failed: {e}. Retrying...")
                continue

        raise last_error

    def _validate_and_build(self, data: dict) -> MultiLevelScenario:
        """Validate data and build MultiLevelScenario object."""
        required_fields = ["title", "aoc_theme", "levels", "day", "year"]

        for field_name in required_fields:
            if field_name not in data:
                raise ValueError(f"Missing required field: {field_name}")

        # Validate we have all 6 levels
        expected_levels = ["level_1", "level_2", "level_3", "level_4", "level_5", "level_6"]
        for level_key in expected_levels:
            if level_key not in data["levels"]:
                raise ValueError(f"Missing required level: {level_key}")

        # Build levels
        levels = {}
        for level_key in expected_levels:
            level_data = data["levels"][level_key]

            # Ensure at least one solution step has victory=True
            solution_steps = level_data.get("solution_steps", [])
            has_victory = any(step.get("victory", False) for step in solution_steps)
            if not has_victory and solution_steps:
                solution_steps[-1]["victory"] = True

            # Build NPCs
            npcs = [NPC(**npc) for npc in level_data.get("npcs", [])]

            # Build solution steps
            steps = []
            for step_data in solution_steps:
                step_data.setdefault("unlocks", None)
                step_data.setdefault("victory", False)
                step_data.setdefault("state_changes", {})
                steps.append(SolutionStep(**step_data))

            levels[level_key] = LevelScenario(
                career_title=level_data.get("career_title", ""),
                setup_narrative=level_data.get("setup_narrative", ""),
                initial_state=level_data.get("initial_state", {"morale": 50, "budget": 100}),
                npcs=npcs,
                solution_steps=steps,
                optimal_turn_count=level_data.get("optimal_turn_count", 4),
                consequences=level_data.get("consequences", {}),
                hints=level_data.get("hints", []),
                victory_message=level_data.get("victory_message", "Congratulations!")
            )

        return MultiLevelScenario(
            day=data["day"],
            year=data["year"],
            title=data["title"],
            aoc_theme=data["aoc_theme"],
            levels=levels,
            continuity_hooks=data.get("continuity_hooks")
        )

    def regenerate_with_feedback(
        self,
        puzzle: AoCPuzzle,
        previous_scenario: MultiLevelScenario,
        feedback: str
    ) -> MultiLevelScenario:
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
            max_tokens=16000,
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
