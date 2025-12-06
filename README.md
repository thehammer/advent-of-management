# Advent of Management

A parody of Advent of Code where programming puzzles become corporate dysfunction scenarios.

## How It Works

1. **Solver Server** fetches AoC puzzles nightly, solves them with Claude, and generates management parody scenarios
2. **Scenarios** are published to S3 (or local files for testing)
3. **Clause Prompt** is a Claude system prompt that runs the text-based management simulation

## Quick Start

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your credentials

# Run once (local mode)
python -m src.main

# Run for specific day
python -m src.main --day 1

# Run as scheduler
python -m src.main --scheduler

# Publish to S3
python -m src.main --s3
```

## Configuration

Create `.env` with:

```
AOC_SESSION_COOKIE=your_session_cookie_here
ANTHROPIC_API_KEY=sk-ant-...
AOC_YEAR=2025

# Optional for S3
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET_NAME=advent-of-management
```

## Getting AoC Session Cookie

1. Go to https://adventofcode.com and log in
2. Open browser DevTools (F12)
3. Go to Application > Cookies > adventofcode.com
4. Copy the `session` cookie value

## Playing the Game

Copy `prompts/clause_prompt_local.md` into a Claude conversation and play!

Or use the S3-hosted version once deployed.

## Project Structure

```
advent-of-management/
├── src/
│   ├── aoc_client.py      # AoC fetching and submission
│   ├── solver.py          # Claude API puzzle solving
│   ├── scenario_gen.py    # Management scenario generation
│   ├── publisher.py       # S3/local upload
│   └── main.py            # Orchestration
├── prompts/
│   ├── solver_prompt.md   # System prompt for solving AoC
│   ├── scenario_prompt.md # System prompt for generating scenarios
│   └── clause_prompt*.md  # The playable game prompts
├── scenarios/             # Generated scenario JSON files
└── .cache/                # Cached AoC puzzle data
```
