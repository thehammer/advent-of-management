# Solving Advent of Code Puzzles with Claude Code

This guide is for Claude Code to solve AoC puzzles. Read this before attempting to solve a puzzle.

## Workflow

1. **Fetch the puzzle** - Read the puzzle description from adventofcode.com
2. **Save input** - Save input to `solutions/{year}/day{NN}/input.txt`
3. **Understand first** - Work through the example by hand before coding
4. **Write solution** - Create `solutions/{year}/day{NN}/solution.py`
5. **Test with example** - Verify your code produces the example answer
6. **Run on input** - Execute against the real input
7. **Submit** - Copy the answer to adventofcode.com

## Directory Structure

```
solutions/
└── 2025/
    └── day01/
        ├── input.txt      # Your puzzle input
        ├── solution.py    # Your solution code
        └── notes.md       # Optional: approach notes, gotchas
```

## Solution Template

```python
#!/usr/bin/env python3
"""Advent of Code {YEAR} Day {DAY}: {TITLE}"""

from pathlib import Path


def parse_input(data: str):
    """Parse the puzzle input."""
    lines = data.strip().split('\n')
    # TODO: parse appropriately
    return lines


def part1(data) -> int:
    """Solve Part 1."""
    parsed = parse_input(data)
    # TODO: implement
    return 0


def part2(data) -> int:
    """Solve Part 2."""
    parsed = parse_input(data)
    # TODO: implement
    return 0


if __name__ == "__main__":
    input_file = Path(__file__).parent / "input.txt"
    data = input_file.read_text()

    print(f"Part 1: {part1(data)}")
    print(f"Part 2: {part2(data)}")
```

## Problem-Solving Strategy

1. **Read carefully** - AoC puzzles hide details in the prose. Read twice.
2. **Work the example** - Manually trace through the example to verify understanding.
3. **Identify the pattern** - What's the core algorithm? (BFS, DP, simulation, math?)
4. **Start simple** - Get Part 1 working before optimizing.
5. **Part 2 twist** - Expect Part 2 to break naive approaches. Look for:
   - Much larger numbers (need math, not brute force)
   - State space explosion (need memoization/pruning)
   - Hidden cycles (need cycle detection)

## Common Patterns

| Pattern | Indicators | Approach |
|---------|-----------|----------|
| Grid traversal | 2D coordinates, directions | Store as dict `{(x,y): value}` |
| Pathfinding | "shortest path", "minimum steps" | BFS for unweighted, Dijkstra for weighted |
| Cycle detection | "after N iterations" (large N) | Floyd's or track seen states |
| Parsing nested | Brackets, recursive structure | Stack or actual recursion |
| Large numbers | "1000000000 times" | Find cycle, use modular arithmetic |
| Constraint satisfaction | "all rules must be satisfied" | Backtracking or reduce constraints |

## Debugging Tips

- **Wrong example answer**: Re-read the problem. You missed something.
- **Correct example, wrong input**: Edge cases. Check for:
  - Off-by-one errors
  - Integer overflow (use Python, so rare)
  - Assumptions that hold for example but not input
- **Too slow**: Need algorithmic improvement, not micro-optimization.
  - Can you memoize repeated work?
  - Can you prune the search space?
  - Is there a mathematical shortcut?

## Testing

Always test with the example first:

```python
EXAMPLE = """
<paste example input here>
""".strip()

# Test
assert part1(EXAMPLE) == <expected_answer>
```

## Submitting

After getting the answer:
1. Copy just the number/string (no extra text)
2. Paste into adventofcode.com
3. Wait at least 1 minute before resubmitting if wrong (rate limit)

## Notes

- AoC puzzle input is unique per user - don't share it publicly
- Solutions go in `solutions/` which is gitignored
- If stuck, take a break. Fresh eyes often see the trick.
