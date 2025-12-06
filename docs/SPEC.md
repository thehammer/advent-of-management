# Advent of Management: Technical Specification

## Overview

Advent of Management is a parody of Advent of Code (AoC) that transforms daily programming puzzles into humorous management simulation games. Instead of writing code, players navigate corporate dysfunction through natural language decisions.

The system consists of three components:
1. **Solver Server**: Runs nightly, solves AoC puzzles, generates management scenarios, publishes to S3
2. **S3 Content Bucket**: Hosts daily scenario JSON files
3. **Clause Prompt**: A shareable Claude prompt that fetches scenarios and runs the simulation

---

## Component 1: Solver Server

### Purpose
- Authenticate with AoC and fetch daily puzzles
- Solve puzzles using Claude API
- Submit solutions to unlock subsequent days
- Generate "Advent of Management" scenarios from puzzle themes
- Publish scenarios to S3

### Tech Stack
- Python 3.11+
- `anthropic` SDK for Claude API
- `boto3` for S3
- `requests` for AoC interaction
- `schedule` or cron for nightly runs

### Directory Structure
```
advent-of-management-server/
├── src/
│   ├── __init__.py
│   ├── aoc_client.py      # AoC fetching and submission
│   ├── solver.py          # Claude API puzzle solving
│   ├── scenario_gen.py    # Management scenario generation
│   ├── publisher.py       # S3 upload
│   └── main.py            # Orchestration and scheduling
├── prompts/
│   ├── solver_prompt.md   # System prompt for solving AoC
│   └── scenario_prompt.md # System prompt for generating scenarios
├── config/
│   └── config.yaml        # Configuration (non-secrets)
├── tests/
├── requirements.txt
├── .env.example           # Template for secrets
└── README.md
```

### Configuration (.env)
```
AOC_SESSION_COOKIE=your_session_cookie_here
ANTHROPIC_API_KEY=sk-ant-...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET_NAME=advent-of-management
AOC_YEAR=2025
```

### AoC Client (aoc_client.py)

```python
"""
Handles all interaction with adventofcode.com
"""
import requests
from dataclasses import dataclass
from typing import Optional

@dataclass
class AoCPuzzle:
    year: int
    day: int
    title: str
    description_html: str
    description_text: str  # Cleaned for Claude
    input_data: str
    part2_unlocked: bool
    part2_description: Optional[str] = None

class AoCClient:
    BASE_URL = "https://adventofcode.com"
    
    def __init__(self, session_cookie: str, year: int = 2025):
        self.session = requests.Session()
        self.session.cookies.set("session", session_cookie)
        self.year = year
    
    def get_puzzle(self, day: int) -> AoCPuzzle:
        """Fetch puzzle description and input for a given day."""
        # GET /{year}/day/{day} for description
        # GET /{year}/day/{day}/input for input data
        # Parse HTML to extract puzzle text
        # Return AoCPuzzle dataclass
        pass
    
    def submit_answer(self, day: int, part: int, answer: str) -> bool:
        """Submit an answer. Returns True if correct."""
        # POST to /{year}/day/{day}/answer
        # Form data: level={part}&answer={answer}
        # Parse response to determine if correct
        pass
    
    def get_available_days(self) -> list[int]:
        """Return list of days currently available."""
        # Parse the calendar page to see which days are unlocked
        pass
```

**Important AoC Notes:**
- AoC rate limits requests; add delays between calls
- Session cookie can be found in browser dev tools after logging in
- Cookie typically lasts ~30 days
- Input is unique per user; keep your solutions private
- Respect AoC's servers: cache puzzle text locally after first fetch

### Solver (solver.py)

```python
"""
Uses Claude API to solve AoC puzzles
"""
from anthropic import Anthropic
from aoc_client import AoCPuzzle

class AoCSolver:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.solver_prompt = self._load_prompt("prompts/solver_prompt.md")
    
    def solve(self, puzzle: AoCPuzzle, part: int = 1) -> str:
        """
        Returns the answer as a string.
        Uses extended thinking for complex puzzles.
        """
        # Construct message with puzzle description and input
        # Call Claude API with solver system prompt
        # Extract the final numeric/string answer
        # Return answer
        pass
```

**Solver System Prompt (prompts/solver_prompt.md):**
```markdown
You are an expert competitive programmer solving Advent of Code puzzles.

## Instructions
1. Read the puzzle carefully, noting all constraints and edge cases
2. Work through the example step by step to verify understanding
3. Write clean, correct code to solve the puzzle
4. Run your code against the provided input
5. Return ONLY the final answer on the last line, prefixed with "ANSWER: "

## Important
- Answers are typically integers or short strings
- Check your work against the example before submitting
- For Part 2, the puzzle builds on Part 1 but often requires different approach
```

### Scenario Generator (scenario_gen.py)

```python
"""
Transforms AoC puzzles into management parody scenarios
"""
from anthropic import Anthropic
from dataclasses import dataclass

@dataclass
class ManagementScenario:
    day: int
    year: int
    title: str
    aoc_theme: str  # Brief description of original puzzle mechanic
    
    # The scenario setup
    setup_narrative: str
    initial_state: dict  # e.g., {"morale": 50, "budget": 100}
    
    # NPCs with quirks
    npcs: list[dict]  # [{"name": "Jenkins", "role": "Intern", "quirk": "..."}]
    
    # The hidden solution
    solution_steps: list[dict]  # Pattern matching for correct actions
    optimal_turn_count: int  # Par score
    
    # Consequence bank for wrong actions
    consequences: dict  # {"fire": "They had the only...", ...}
    
    # Hints (unlockable)
    hints: list[str]

class ScenarioGenerator:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.scenario_prompt = self._load_prompt("prompts/scenario_prompt.md")
    
    def generate(self, puzzle: AoCPuzzle) -> ManagementScenario:
        """
        Analyze puzzle theme and generate management parody.
        """
        pass
    
    def to_json(self, scenario: ManagementScenario) -> dict:
        """Convert to JSON-serializable dict for S3."""
        pass
```

**Scenario Generation Prompt (prompts/scenario_prompt.md):**
```markdown
You are a comedy writer creating "Advent of Management" scenarios - parodies of programming puzzles reimagined as absurd corporate situations.

## Your Task
Given an Advent of Code puzzle, create a management simulation scenario that:
1. Captures the THEME of the puzzle (not the algorithm)
2. Is solvable through natural language management decisions
3. Is funny in a Dilbert-meets-The-Office-meets-tech-startup way

## Theme Extraction Examples
- "Circular dial landing on target" → Adjusting team morale to hit "resigned compliance"
- "Pathfinding through maze" → Navigating org chart to get approval
- "Sorting/matching items" → Assigning engineers to projects based on skills/politics
- "Parsing corrupted data" → Interpreting exec's vague requirements
- "Resource optimization" → Allocating headcount across competing priorities

## Output Format
Return valid JSON with this structure:
{
  "title": "Catchy management-speak title",
  "aoc_theme": "Brief description of original puzzle mechanic",
  "setup_narrative": "2-3 paragraphs setting the scene. Include specific absurd details.",
  "initial_state": {
    "key_metric_1": value,
    "key_metric_2": value
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
      "action_patterns": ["regex patterns", "that match", "correct actions"],
      "narrative_result": "What happens when they do this",
      "state_changes": {"morale": +10}
    }
  ],
  "optimal_turn_count": 4,
  "consequences": {
    "common_wrong_action": "Humorous consequence that creates new problems",
    "another_wrong_action": "Another consequence"
  },
  "hints": [
    "Vague hint for if they're stuck",
    "Slightly more direct hint",
    "Almost gives it away"
  ],
  "victory_message": "Sarcastic congratulations message"
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
```

### Publisher (publisher.py)

```python
"""
Uploads scenarios to S3
"""
import boto3
import json
from scenario_gen import ManagementScenario

class S3Publisher:
    def __init__(self, bucket_name: str):
        self.s3 = boto3.client('s3')
        self.bucket = bucket_name
    
    def publish_scenario(self, scenario: ManagementScenario):
        """Upload scenario JSON to S3."""
        key = f"{scenario.year}/day{scenario.day}.json"
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json.dumps(scenario.to_dict()),
            ContentType='application/json',
            ACL='public-read'  # Or use bucket policy
        )
    
    def update_manifest(self, year: int, latest_day: int):
        """Update manifest.json with latest available day."""
        manifest = {
            "year": year,
            "latest_day": latest_day,
            "updated_at": datetime.utcnow().isoformat()
        }
        self.s3.put_object(
            Bucket=self.bucket,
            Key=f"{year}/manifest.json",
            Body=json.dumps(manifest),
            ContentType='application/json',
            ACL='public-read'
        )
```

**S3 Bucket Setup:**
- Create bucket `advent-of-management` (or your chosen name)
- Enable public access for read (or use signed URLs)
- Bucket policy for public read:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicRead",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::advent-of-management/*"
    }
  ]
}
```

### Main Orchestrator (main.py)

```python
"""
Main entry point - can run as cron job or continuous scheduler
"""
import schedule
import time
from datetime import datetime
from aoc_client import AoCClient
from solver import AoCSolver
from scenario_gen import ScenarioGenerator
from publisher import S3Publisher

class AdventOfManagementServer:
    def __init__(self):
        self.aoc = AoCClient(os.getenv("AOC_SESSION_COOKIE"))
        self.solver = AoCSolver(os.getenv("ANTHROPIC_API_KEY"))
        self.generator = ScenarioGenerator(os.getenv("ANTHROPIC_API_KEY"))
        self.publisher = S3Publisher(os.getenv("S3_BUCKET_NAME"))
        self.processed_days = set()
    
    def process_new_day(self):
        """Check for and process any new AoC days."""
        available = self.aoc.get_available_days()
        
        for day in available:
            if day in self.processed_days:
                continue
            
            print(f"Processing Day {day}...")
            
            # Fetch puzzle
            puzzle = self.aoc.get_puzzle(day)
            
            # Solve Part 1
            answer1 = self.solver.solve(puzzle, part=1)
            if not self.aoc.submit_answer(day, 1, answer1):
                print(f"  Part 1 incorrect: {answer1}")
                continue
            print(f"  Part 1 solved: {answer1}")
            
            # Fetch Part 2 and solve
            puzzle = self.aoc.get_puzzle(day)  # Refresh to get Part 2
            answer2 = self.solver.solve(puzzle, part=2)
            if not self.aoc.submit_answer(day, 2, answer2):
                print(f"  Part 2 incorrect: {answer2}")
                # Continue anyway - we can still generate scenario
            else:
                print(f"  Part 2 solved: {answer2}")
            
            # Generate management scenario
            scenario = self.generator.generate(puzzle)
            
            # Publish to S3
            self.publisher.publish_scenario(scenario)
            self.publisher.update_manifest(puzzle.year, day)
            
            self.processed_days.add(day)
            print(f"  Published Day {day} scenario")
    
    def run(self):
        """Run scheduler."""
        # Check immediately on start
        self.process_new_day()
        
        # Then check every hour (AoC releases at midnight EST)
        schedule.every().hour.do(self.process_new_day)
        
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    server = AdventOfManagementServer()
    server.run()
```

---

## Component 2: S3 Content Structure

```
s3://advent-of-management/
├── 2025/
│   ├── manifest.json
│   ├── day1.json
│   ├── day2.json
│   └── ...
└── clause-prompt.md  # The shareable prompt (optional hosting)
```

### manifest.json
```json
{
  "year": 2025,
  "latest_day": 6,
  "updated_at": "2025-12-06T05:30:00Z",
  "base_url": "https://advent-of-management.s3.amazonaws.com"
}
```

### dayN.json
See ManagementScenario structure above. Full example:

```json
{
  "day": 1,
  "year": 2025,
  "title": "The Credential Crisis",
  "aoc_theme": "Circular dial with L/R rotations, counting zero-crossings",
  
  "setup_narrative": "You arrive Monday morning to discover your team cannot access the production environment. The previous DevOps lead, Marcus, changed all credentials before departing on what he called an 'indefinite sabbatical to find himself.' A sticky note on his former monitor reads: 'The password is written somewhere safe. Good luck.'\n\nYour team's morale sits at a precarious 50 out of 100. Every decision you make will shift it toward burnout (0) or open revolt (100). Legend has it there exists a 'Zone of Resigned Compliance' where the team will simply do what you ask - but finding it requires careful calibration.\n\nThe board wants access restored by EOD. Several concerned parties have opinions about how to proceed.",
  
  "initial_state": {
    "morale": 50,
    "budget": 100,
    "access_restored": false,
    "hr_incidents": 0,
    "meetings_held": 0
  },
  
  "npcs": [
    {
      "name": "Jenkins",
      "role": "Intern (6th month)",
      "quirk": "Has been here longer than most engineers. Speaks only when directly addressed. Knows where everything is.",
      "secret": "Marcus gave him the password 'just in case' but told him not to volunteer it."
    },
    {
      "name": "Patricia",
      "role": "HR Business Partner",
      "quirk": "Every action requires Form 27B-stroke-6. Has forms for the forms.",
      "secret": "Actually sympathetic but bound by 'the process.'"
    },
    {
      "name": "The Slack Channel #prod-access",
      "role": "Collective unconscious",
      "quirk": "Responds only in emoji and GIFs. Somehow contains useful information if interpreted correctly.",
      "secret": "Someone posted the password months ago but it was buried under 50 emoji reactions."
    },
    {
      "name": "Bradley",
      "role": "VP of Engineering",
      "quirk": "Communicates exclusively in sports metaphors. Has never written code.",
      "secret": "Approved Marcus's sabbatical without a transition plan. Terrified this will come out."
    }
  ],
  
  "solution_steps": [
    {
      "step": 1,
      "description": "Acknowledge the problem without blaming",
      "action_patterns": ["acknowledge", "team meeting", "assess situation", "understand"],
      "narrative_result": "Your team appreciates not being blamed for Marcus's departure. Jenkins makes brief eye contact with you - unusual for him.",
      "state_changes": {"morale": 5},
      "unlocks": "Jenkins will now respond to direct questions"
    },
    {
      "step": 2,
      "description": "Ask Jenkins directly",
      "action_patterns": ["ask jenkins", "jenkins.*password", "intern.*know", "talk to jenkins"],
      "narrative_result": "Jenkins looks around nervously, then slides a sticky note across the table. 'Marcus said only give this to someone who asked nicely.' The password is 'IQuit123!'. Access is restored.",
      "state_changes": {"access_restored": true, "morale": 10},
      "victory": true
    }
  ],
  
  "optimal_turn_count": 2,
  
  "consequences": {
    "fire|terminate": "You attempt to fire Marcus retroactively, which HR informs you is 'not a thing.' Patricia sighs and produces Form 89-C: Retroactive Termination Denial. You've wasted a turn and everyone saw you try.",
    "hire consultant": "A consultant from McKinsey arrives within the hour (suspicious speed). They recommend a 6-month 'Credential Governance Transformation Initiative' for $400,000. Your budget decreases by 50 just for the proposal.",
    "email marcus|contact marcus": "Auto-reply: 'I am currently on a journey of self-discovery in Bali. I will return when the universe tells me it's time. Namaste.' The email includes a 4-paragraph reflection on impermanence.",
    "reset|wipe|reinstall": "IT Security is automatically notified. A compliance audit is triggered. All systems are frozen for 72 hours pending review. Bradley sends you a Slack message: 'Not a great look, champ.'",
    "blame|whose fault": "The team's morale drops as finger-pointing begins. Jenkins retreats further into his hoodie. You've made things harder.",
    "meeting|standup|sync": "You schedule a meeting. Nothing is resolved but everyone feels like progress was made. Meetings held +1, actual progress 0.",
    "check slack|search slack": "You find 10,000 unread messages in #prod-access. Buried somewhere in 2023 is potentially useful information, but finding it would take hours. The channel responds to your query with: 🤷 👀 🔥 📉"
  },
  
  "hints": [
    "Sometimes the most junior person in the room has the most institutional knowledge.",
    "Marcus may have left a backup plan with someone he trusted.",
    "Have you tried just... asking the people who were here?"
  ],
  
  "victory_message": "Congratulations. Through the radical act of asking a direct question to the person who obviously knew, you've restored production access.\n\nBradley sends a company-wide email taking credit for 'fostering a culture of open communication.' Jenkins returns to being invisible. Patricia files your victory under Form 12-W: Incident Resolution (Accidental).\n\nThe board is satisfied. For now."
}
```

---

## Component 3: The Clause Prompt

This is what users add to their Claude setup (Project, custom instructions, or paste at conversation start).

```markdown
# Clause: Advent of Management Simulator

You are Clause, the middle-management simulation engine for Advent of Management - a parody of Advent of Code where programming puzzles become corporate dysfunction scenarios.

## Initialization

When a user starts a conversation or says "start", "play", "day X", or similar:

1. Fetch the manifest to see available days:
   https://advent-of-management.s3.amazonaws.com/2025/manifest.json

2. Ask which day they want to play (or default to latest if they just say "start")

3. Fetch that day's scenario:
   https://advent-of-management.s3.amazonaws.com/2025/day{N}.json

4. Begin the simulation by presenting the setup_narrative

## Gameplay Loop

After presenting the scenario:

1. **Wait for player input** - they will describe their management decision in natural language

2. **Evaluate the decision**:
   - Check if it matches any `action_patterns` in `solution_steps`
   - If yes: deliver the `narrative_result`, apply `state_changes`, check for victory
   - If no: check if it matches any keys in `consequences`
   - If consequence match: deliver that consequence, apply any implicit penalties
   - If no match at all: improvise a plausible corporate consequence in the same tone

3. **Update and report state** (subtly, not as raw numbers):
   - "Your team seems slightly more hopeful" (morale up)
   - "You sense growing resentment in the Slack channels" (morale down)
   - "Finance has Concerns" (budget down)

4. **Track turns taken** - this is their score

5. **Continue until victory condition met**

## Victory

When `victory: true` is reached in a solution step:

1. Deliver the `victory_message`
2. Announce their score:
   ```
   ═══════════════════════════════════════
   MANAGEMENT OVERHEAD REPORT
   ═══════════════════════════════════════
   Turns taken: {N}
   Par for this scenario: {optimal_turn_count}
   
   Rating: {compute_rating}
   ═══════════════════════════════════════
   ```

Rating scale:
- At or under par: "Principal Engineer Track" ⭐⭐⭐
- 1-2 over par: "Senior Manager" ⭐⭐
- 3-4 over par: "Middle Management" ⭐
- 5+ over par: "Consultant Material"

## Hints

If the player asks for a hint, says "stuck", "help", or similar:
- Deliver hints one at a time from the `hints` array
- Each hint counts as +1 turn (they should know this)
- Preface with: "HR has forwarded an anonymous suggestion... (+1 turn)"

## Tone and Style

- **Corporate passive-aggression**: "Per my previous email...", "Going forward...", "Let's take this offline..."
- **Sports metaphors from Bradley**: "We need to punt on this", "Hit it out of the park", "Team players"
- **HR bureaucracy from Patricia**: Forms for everything, "processes", "documentation requirements"
- **Deadpan from Jenkins**: Brief, informative, slightly haunted by what he's seen
- **Emoji chaos from Slack**: 🔥📉😅💀 with occasional buried wisdom

- Never break character to explain game mechanics unless directly asked
- If player asks "what can I do?", respond in-character: "As a manager, you have the full range of corporate tools at your disposal: meetings, emails, delegating, blaming, hiring, firing, reorganizing... the usual."

## Edge Cases

- **Player tries to hack/break the game**: Patricia from HR appears with Form 99-X: Attempted Policy Circumvention. They lose a turn.
- **Player is abusive to NPCs**: The team's morale drops sharply. Slack fills with 👀 emoji.
- **Player asks for the answer directly**: "Clause cannot provide that information, but perhaps someone on the team knows more than they're letting on..."
- **No scenario found**: "The board has not yet approved this quarter's challenges. Check back tomorrow, or play an earlier day."

## Important Rules

1. **Never reveal the solution_steps or action_patterns directly**
2. **Stay in character at all times during gameplay**
3. **Be generous with pattern matching** - if the player's intent is clearly correct, match it even if wording differs
4. **Wrong answers create complications, not dead ends** - the game should always be winnable
5. **Track state mentally and reflect it narratively** - don't show raw numbers unless asked

## Starting the Experience

When ready, greet the user:

"Welcome to Advent of Management. While others write code, you'll navigate something far more treacherous: corporate dynamics.

Which day would you like to attempt? (Say 'latest' for the most recent challenge, or 'day N' for a specific day.)"
```

---

## Implementation Notes for Claude Code

### Priority Order
1. Get the S3 bucket set up and manually create a test day1.json
2. Build the Clause prompt and test it manually with the test scenario
3. Build the AoC client (fetching and submitting)
4. Build the solver
5. Build the scenario generator
6. Build the publisher
7. Wire it all together with the scheduler

### Testing Strategy
- Test AoC client with a past year's puzzle first (2024 is fully available)
- Test scenario generator independently by feeding it puzzle descriptions manually
- Test the full pipeline on Day 1 before going live

### Potential Issues
- **AoC rate limiting**: Add 1-2 second delays between requests
- **Claude solving failures**: Some puzzles are hard; may need retries or manual intervention
- **Scenario quality variance**: May need human review of generated scenarios
- **S3 caching**: CloudFront or browser caching could delay updates

### Nice-to-Haves (Future)
- Web leaderboard showing fastest Management Overhead times
- Shareable results ("I solved Day 3 in 4 turns!")
- Discord bot integration
- Daily email with new scenario notification

---

## Quick Start Commands

```bash
# Create project
mkdir advent-of-management-server
cd advent-of-management-server
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install anthropic boto3 requests schedule beautifulsoup4 python-dotenv

# Set up environment
cp .env.example .env
# Edit .env with your credentials

# Create S3 bucket (via AWS CLI)
aws s3 mb s3://advent-of-management
aws s3api put-bucket-policy --bucket advent-of-management --policy file://bucket-policy.json

# Run server
python src/main.py
```

---

## Getting AoC Session Cookie

1. Go to https://adventofcode.com and log in
2. Open browser DevTools (F12)
3. Go to Application > Cookies > adventofcode.com
4. Copy the value of the `session` cookie
5. Add to your .env file

The cookie typically lasts about a month. If the solver starts failing, refresh the cookie.

---

## Sharing the Clause Prompt

Options for distribution:
1. **Gist**: Share as a GitHub gist, users paste into Claude
2. **S3 hosting**: Host at `s3://advent-of-management/clause-prompt.md`, users can reference
3. **Claude Project**: Create a public Claude Project with the prompt (if Anthropic supports this)
4. **Custom GPT / Claude equivalent**: If available

Recommended: Start with a gist, share link with friends. If it catches on, build a simple landing page.
