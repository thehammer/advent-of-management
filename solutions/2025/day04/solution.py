#!/usr/bin/env python3
"""Advent of Code 2025 Day 4: Printing Department"""

from pathlib import Path


def parse_grid(data: str) -> list[str]:
    """Parse input into a list of strings (grid rows)."""
    return [line for line in data.strip().split('\n') if line]


def count_adjacent_rolls(grid: list[str], row: int, col: int) -> int:
    """Count the number of adjacent rolls (@) in 8 directions."""
    rows, cols = len(grid), len(grid[0])
    count = 0

    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = row + dr, col + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == '@':
                count += 1

    return count


def part1(data: str) -> int:
    """Count rolls accessible by forklift (fewer than 4 adjacent rolls)."""
    grid = parse_grid(data)
    accessible = 0

    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if cell == '@':
                if count_adjacent_rolls(grid, r, c) < 4:
                    accessible += 1

    return accessible


def count_adjacent_rolls_set(rolls: set[tuple[int, int]], row: int, col: int) -> int:
    """Count adjacent rolls using a set for efficient lookup."""
    count = 0
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            if (row + dr, col + dc) in rolls:
                count += 1
    return count


def part2(data: str) -> int:
    """Count total rolls that can be removed iteratively."""
    grid = parse_grid(data)

    # Build set of all roll positions
    rolls = set()
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if cell == '@':
                rolls.add((r, c))

    total_removed = 0

    while True:
        # Find all accessible rolls (< 4 neighbors)
        accessible = []
        for r, c in rolls:
            if count_adjacent_rolls_set(rolls, r, c) < 4:
                accessible.append((r, c))

        if not accessible:
            break

        # Remove all accessible rolls
        for pos in accessible:
            rolls.remove(pos)
        total_removed += len(accessible)

    return total_removed


if __name__ == "__main__":
    input_file = Path(__file__).parent / "input.txt"
    data = input_file.read_text()

    # Test with example
    EXAMPLE = """..@@.@@@@.
@@@.@.@.@@
@@@@@.@.@@
@.@@@@..@.
@@.@@@@.@@
.@@@@@@@.@
.@.@.@.@@@
@.@@@.@@@@
.@@@@@@@@.
@.@.@@@.@."""

    result = part1(EXAMPLE)
    assert result == 13, f"Expected 13, got {result}"
    print("Part 1 example passed!")

    result2 = part2(EXAMPLE)
    assert result2 == 43, f"Expected 43, got {result2}"
    print("Part 2 example passed!")

    print(f"Part 1: {part1(data)}")
    print(f"Part 2: {part2(data)}")
