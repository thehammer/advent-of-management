# Advent of Management

A parody of Advent of Code where programming puzzles become corporate dysfunction scenarios.

## Play Now

Copy the contents of [`prompts/clause_prompt.md`](prompts/clause_prompt.md) into a Claude.ai conversation as a Project prompt, then say "start" to play!

Scenarios are hosted at: `https://advent-of-management.s3.us-east-1.amazonaws.com/2025/`

## How It Works

1. **Scenario Generator** fetches AoC puzzles and generates management parody scenarios using Claude
2. **Scenarios** are published to S3 as JSON files
3. **Clause Prompt** is a Claude system prompt that fetches scenarios and runs the text-based management simulation
4. **Nightly Automation** via launchd publishes new scenarios each night when AoC releases new puzzles

## Quick Start

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your credentials

# Generate scenarios (without solving puzzles)
python -m src.main --generate-only

# Generate and publish to S3
python -m src.main --s3 --generate-only

# Generate for specific day
python -m src.main --day 1 --s3 --generate-only
```

## Configuration

Create `.env` with:

```
AOC_SESSION_COOKIE=your_session_cookie_here
ANTHROPIC_API_KEY=sk-ant-...
AOC_YEAR=2025

# Required for S3 publishing
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
S3_BUCKET_NAME=advent-of-management
```

## Getting AoC Session Cookie

1. Go to https://adventofcode.com and log in
2. Open browser DevTools (F12)
3. Go to Application > Cookies > adventofcode.com
4. Copy the `session` cookie value

## Nightly Automation (macOS)

The project includes launchd plists for nightly scenario generation:

```bash
# Install the launchd job
cp com.hammer.advent-of-management.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.hammer.advent-of-management.plist

# Check status
launchctl list | grep advent
```

## Project Structure

```
advent-of-management/
├── src/
│   ├── aoc_client.py      # AoC puzzle fetching
│   ├── solver.py          # Claude API puzzle solving (optional)
│   ├── scenario_gen.py    # Management scenario generation
│   ├── publisher.py       # S3/local publishing
│   ├── main.py            # Main orchestration
│   └── solve_aoc.py       # Standalone puzzle solver with artifacts
├── prompts/
│   ├── solver_prompt.md   # System prompt for solving AoC
│   ├── scenario_prompt.md # System prompt for generating scenarios
│   └── clause_prompt.md   # The playable game prompt (use this!)
├── scenarios/             # Local scenario JSON files
├── solutions/             # Puzzle solutions and artifacts (gitignored)
└── logs/                  # Runtime logs (gitignored)
```
