#!/usr/bin/env python3
"""Advent of Code 2025 Day 7: Laboratories"""

from pathlib import Path
from collections import defaultdict


def parse_grid(data: str) -> tuple[list[str], int, int]:
    """Parse grid and find starting position S."""
    grid = [line for line in data.strip().split('\n')]
    start_row, start_col = 0, 0
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch == 'S':
                start_row, start_col = r, c
                break
    return grid, start_row, start_col


def part1(data: str) -> int:
    """
    Count total beam splits.
    Beams move downward. When hitting ^, the beam splits left and right.
    Multiple beams at same location merge (count as one).
    """
    grid, start_row, start_col = parse_grid(data)
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    # Track beams: set of (row, col) for active downward beams
    # Start with beam at S position, moving downward
    active_beams = {(start_row, start_col)}
    total_splits = 0

    while active_beams:
        # Move all beams down one step
        new_beams = set()
        for r, c in active_beams:
            nr = r + 1
            if nr >= rows:
                # Beam exits bottom
                continue
            if c < 0 or c >= cols:
                # Beam exits side
                continue

            ch = grid[nr][c]
            if ch == '^':
                # Split: create beams left and right
                total_splits += 1
                # Left beam starts at (nr, c-1), right at (nr, c+1)
                if c - 1 >= 0:
                    new_beams.add((nr, c - 1))
                if c + 1 < cols:
                    new_beams.add((nr, c + 1))
            else:
                # Continue downward
                new_beams.add((nr, c))

        active_beams = new_beams

    return total_splits


def part2(data: str) -> int:
    """
    Count total timelines.
    Each particle at a position represents some number of timelines.
    When hitting a splitter, each timeline splits into two.
    Track timeline counts per position.
    """
    grid, start_row, start_col = parse_grid(data)
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    # Track particles with timeline counts: dict of (row, col) -> timeline_count
    active = {(start_row, start_col): 1}
    total_timelines = 0

    while active:
        new_active = defaultdict(int)

        for (r, c), count in active.items():
            nr = r + 1
            if nr >= rows:
                # Particle exits - these timelines are done
                total_timelines += count
                continue
            if c < 0 or c >= cols:
                # Particle exits side - done
                total_timelines += count
                continue

            ch = grid[nr][c]
            if ch == '^':
                # Split: each timeline becomes two
                if c - 1 >= 0:
                    new_active[(nr, c - 1)] += count
                else:
                    # Left exit
                    total_timelines += count
                if c + 1 < cols:
                    new_active[(nr, c + 1)] += count
                else:
                    # Right exit
                    total_timelines += count
            else:
                # Continue downward
                new_active[(nr, c)] += count

        active = dict(new_active)

    return total_timelines


if __name__ == "__main__":
    input_file = Path(__file__).parent / "input.txt"
    data = input_file.read_text()

    # Test with example
    EXAMPLE = """.......S.......
...............
.......^.......
...............
......^.^......
...............
.....^.^.^.....
...............
....^.^...^....
...............
...^.^...^.^...
...............
..^...^.....^..
...............
.^.^.^.^.^...^.
..............."""

    result = part1(EXAMPLE)
    assert result == 21, f"Expected 21, got {result}"
    print("Part 1 example passed!")

    result2 = part2(EXAMPLE)
    assert result2 == 40, f"Expected 40, got {result2}"
    print("Part 2 example passed!")

    print(f"Part 1: {part1(data)}")
    print(f"Part 2: {part2(data)}")
