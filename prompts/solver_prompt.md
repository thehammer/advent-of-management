# Solving Advent of Code Puzzles with Claude Code

This guide is for Claude Code to solve AoC puzzles. Read this before attempting to solve a puzzle.

## Workflow

1. **Fetch the puzzle** - Read the puzzle description from adventofcode.com
2. **Save input** - Save input to `solutions/{year}/day{NN}/input.txt`
3. **Analyze complexity** - Before coding, analyze input size and plan algorithm complexity
4. **Understand first** - Work through the example by hand before coding
5. **Write solution** - Create `solutions/{year}/day{NN}/solution.py`
6. **Test with example** - Verify your code produces the example answer
7. **Run with timeout** - Execute with 30s timeout; if it times out, optimize
8. **Submit** - Use AoCClient.submit_answer() to submit

## CRITICAL: Performance Planning

**Before writing any code**, analyze:

1. **Input size** - Count lines, check coordinate ranges, estimate data volume
   ```python
   # Always check input characteristics first
   lines = data.strip().split('\n')
   print(f"Lines: {len(lines)}")
   # For coordinate problems:
   coords = [parse(line) for line in lines]
   xs = [c[0] for c in coords]
   print(f"X range: {min(xs)} to {max(xs)}")
   ```

2. **Complexity requirements** - Based on input size, determine acceptable complexity:
   | Input size | Max acceptable | Approach |
   |------------|----------------|----------|
   | N ≤ 20 | O(2^N) | Brute force, backtracking |
   | N ≤ 1,000 | O(N²) | Nested loops OK |
   | N ≤ 100,000 | O(N log N) | Sorting, binary search |
   | N ≤ 10,000,000 | O(N) | Single pass, hashing |
   | Coordinates > 10,000 | Geometric | Don't iterate over grid cells |

3. **Red flags that require smart algorithms**:
   - Coordinate ranges in thousands/millions → Use geometric checks, not iteration
   - "after 1000000000 iterations" → Find cycle
   - Grid larger than 1000x1000 → Don't iterate all cells
   - "all pairs" with N > 1000 → Need pruning or better algorithm

## Timeout-Based Iteration

Run solutions with a **30-second timeout**. If it times out:

1. **Don't just wait longer** - the algorithm is wrong
2. **Analyze why it's slow**:
   - Are you iterating over something huge? (coordinates, grid cells)
   - Are you recomputing the same thing? (add memoization)
   - Is there a mathematical shortcut?
3. **Rewrite with better complexity**, don't micro-optimize

```bash
# Run with timeout
timeout 30s python solution.py || echo "TIMEOUT - need optimization"
```

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
| Polygon containment | "inside", "boundary", large coords | Ray casting, DON'T iterate cells |
| Rectangle in polygon | Find largest rect in shape | Geometric checks on corners/edges |

## Geometric Problem Approaches

When coordinates are large (>1000), **never iterate over individual cells**. Use geometry:

### Point in Polygon (Ray Casting)
```python
def point_in_polygon(px, py, vertices):
    """O(n) where n = number of vertices, NOT grid size."""
    inside = False
    j = len(vertices) - 1
    for i in range(len(vertices)):
        xi, yi = vertices[i]
        xj, yj = vertices[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside
```

### Rectangle Fully Inside Polygon
Instead of checking every cell in the rectangle:
1. Check all 4 corners are inside/on polygon boundary
2. Check no polygon edges cross INTO the rectangle interior
3. This is O(n) per rectangle, not O(area)

### Polygon Boundary Segments
For rectilinear polygons (axis-aligned edges):
```python
h_segments = []  # (y, x_min, x_max)
v_segments = []  # (x, y_min, y_max)
# Use these for fast boundary/intersection checks
```

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
