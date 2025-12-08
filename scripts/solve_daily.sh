#!/bin/bash
# Automatically solve the latest AoC puzzle with Claude Code

set -e

cd "$(dirname "$0")/.."
PROJECT_DIR="$(pwd)"

# Get current day (AoC releases at midnight EST)
# If running right after midnight EST, use today's date
DAY=$(TZ="America/New_York" date +%-d)
YEAR=$(TZ="America/New_York" date +%Y)

# Only run during December 1-25
MONTH=$(TZ="America/New_York" date +%-m)
if [ "$MONTH" -ne 12 ] || [ "$DAY" -gt 25 ]; then
    echo "Not during AoC season (Dec 1-25)"
    exit 0
fi

LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/solve_day${DAY}_$(date +%Y%m%d_%H%M%S).log"

echo "=== Solving AoC $YEAR Day $DAY ===" | tee "$LOG_FILE"
echo "Started at $(date)" | tee -a "$LOG_FILE"

# Check if already solved
SOLUTION_DIR="$PROJECT_DIR/solutions/$YEAR/day$(printf '%02d' $DAY)"
if [ -f "$SOLUTION_DIR/solution.py" ]; then
    echo "Day $DAY already has a solution, skipping" | tee -a "$LOG_FILE"
    exit 0
fi

# Run Claude Code to solve the puzzle
# Using --print to avoid interactive mode, -p for prompt
claude -p "Read prompts/solver_prompt.md then solve day $DAY. Submit both parts using the AoCClient.submit_answer() method. Be concise." \
    --allowedTools "Bash(*)" "Read(*)" "Write(*)" "Edit(*)" "Glob(*)" "Grep(*)" "WebFetch(*)" \
    2>&1 | tee -a "$LOG_FILE"

echo "Finished at $(date)" | tee -a "$LOG_FILE"
