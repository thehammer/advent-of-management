# Advent of Management

A parody of Advent of Code where programming puzzles become corporate dysfunction scenarios at North Pole Operations, Inc.

## Play Now

Copy the contents of [`prompts/clause_prompt.md`](prompts/clause_prompt.md) into a Claude.ai conversation as a Project prompt, then say "start" to play!

Scenarios are hosted at: `https://advent-of-management.s3.us-east-1.amazonaws.com/2025/`

## How It Works

1. **Scenario Generator** fetches AoC puzzles and generates management parody scenarios using Claude
2. **Scenarios** are published to S3 as JSON files with 6 difficulty levels each
3. **Clause Prompt** is a Claude system prompt that fetches scenarios and runs the text-based management simulation
4. **Career Track** lets players progress from Team Lead to C-Suite based on performance

## Quick Start

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
# Install uv (if needed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/thehammer/advent-of-management.git
cd advent-of-management
uv sync

# Configure
cp .env.example .env
# Edit .env with your credentials

# Generate scenarios locally
uv run python -m src.main

# Generate and publish to S3
uv run python -m src.main --s3

# Generate for specific day
uv run python -m src.main --day 8 --s3
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

## Solving AoC Puzzles

To solve the actual AoC puzzles (separate from scenario generation), use Claude Code:

```bash
claude "Read prompts/solver_prompt.md then solve day 8"
```

Solutions are saved to `solutions/` (gitignored).

## Project Structure

```
advent-of-management/
├── src/
│   ├── aoc_client.py      # AoC puzzle fetching & submission
│   ├── scenario_gen.py    # Management scenario generation
│   ├── publisher.py       # S3/local publishing
│   └── main.py            # Main orchestration
├── prompts/
│   ├── solver_prompt.md   # Guide for solving AoC with Claude Code
│   ├── scenario_prompt.md # System prompt for generating scenarios
│   └── clause_prompt.md   # The playable game prompt (use this!)
├── s3_content/            # Game rules, tone guide (uploaded to S3)
├── scripts/               # Automation scripts
├── scenarios/             # Local scenario JSON files
├── solutions/             # Puzzle solutions (gitignored)
└── logs/                  # Runtime logs (gitignored)
```

## License

MIT
