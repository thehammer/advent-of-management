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

# Use Opus for better reasoning on complex AoC problems
# Sonnet is faster but makes more algorithmic mistakes
MODEL="opus"

# Run Claude Code to solve the puzzle
# Using --print to avoid interactive mode, -p for prompt
# Key instructions:
# 1. Read the solver guide with performance planning advice
# 2. Analyze input size BEFORE coding
# 3. Use 30s timeout to detect slow solutions
# 4. Submit answers via AoCClient
claude -p "Read prompts/solver_prompt.md carefully, especially the CRITICAL: Performance Planning section.

Solve AoC $YEAR Day $DAY following this process:
1. Fetch puzzle and save input
2. BEFORE CODING: Analyze input size and coordinate ranges
3. Plan algorithm complexity based on input size
4. Write solution with example tests
5. Run with 30s timeout - if it times out, the algorithm is wrong, optimize
6. Submit both parts using AoCClient.submit_answer()

Be concise. If a solution times out, analyze why and rewrite with better complexity." \
    --model "$MODEL" \
    --allowedTools "Bash(*)" "Read(*)" "Write(*)" "Edit(*)" "Glob(*)" "Grep(*)" "WebFetch(*)" \
    2>&1 | tee -a "$LOG_FILE"

echo "Finished at $(date)" | tee -a "$LOG_FILE"
