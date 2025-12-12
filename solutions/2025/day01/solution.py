#!/usr/bin/env python3
"""Advent of Code 2025 Day 1: Secret Entrance"""

from pathlib import Path


def parse_input(data: str) -> list[tuple[str, int]]:
    """Parse the puzzle input into list of (direction, amount) tuples."""
    rotations = []
    for line in data.strip().split('\n'):
        line = line.strip()
        if line:
            direction = line[0]  # 'L' or 'R'
            amount = int(line[1:])
            rotations.append((direction, amount))
    return rotations


def part1(data: str) -> int:
    """
    Solve Part 1.
    Count how many times the dial lands on 0 after executing rotations.
    Dial starts at 50, wraps 0-99.
    L = rotate left (subtract), R = rotate right (add).
    """
    rotations = parse_input(data)
    position = 50
    zero_count = 0

    for direction, amount in rotations:
        if direction == 'L':
            position = (position - amount) % 100
        else:  # 'R'
            position = (position + amount) % 100

        if position == 0:
            zero_count += 1

    return zero_count


def count_zero_crossings(start: int, direction: str, amount: int) -> int:
    """
    Count how many times the dial passes through or lands on 0 during a rotation.

    Key insight: we hit 0 when our cumulative movement crosses a multiple of 100
    that aligns with hitting position 0.

    For direction L (going down): we hit 0 after moving (start + 1), (start + 101), (start + 201), ...
    For direction R (going up): we hit 0 after moving (100 - start), (200 - start), (300 - start), ...
    """
    if amount == 0:
        return 0

    if direction == 'L':
        # Going left from start, we hit 0 after moving: start, start+100, start+200, ...
        # (if start=50, we hit 0 after 50 steps, 150 steps, 250 steps, ...)
        # But if start=0, first hit is at 100 steps (we leave 0 immediately)
        if start == 0:
            first_hit = 100
        else:
            first_hit = start
    else:  # 'R'
        # Going right from start, we hit 0 after moving: 100-start, 200-start, 300-start, ...
        # (if start=50, we hit 0 after 50 steps, 150 steps, 250 steps, ...)
        # If start=0, first hit is at 100 steps
        if start == 0:
            first_hit = 100
        else:
            first_hit = 100 - start

    if first_hit > amount:
        return 0

    # Count how many times we hit 0: first_hit, first_hit+100, first_hit+200, ...
    # up to amount
    return (amount - first_hit) // 100 + 1


def part2(data: str) -> int:
    """
    Solve Part 2.
    Count every time the dial points at 0, including during rotations.
    """
    rotations = parse_input(data)
    position = 50
    zero_count = 0

    for direction, amount in rotations:
        if direction == 'L':
            new_position = (position - amount) % 100
        else:  # 'R'
            new_position = (position + amount) % 100

        zero_count += count_zero_crossings(position, direction, amount)
        position = new_position

    return zero_count


if __name__ == "__main__":
    input_file = Path(__file__).parent / "input.txt"
    data = input_file.read_text()

    # Test with example
    EXAMPLE = """L68
L30
R48
L5
R60
L55
L1
L99
R14
L82"""

    assert part1(EXAMPLE) == 3, f"Expected 3, got {part1(EXAMPLE)}"
    print("Part 1 example passed!")

    assert part2(EXAMPLE) == 6, f"Expected 6, got {part2(EXAMPLE)}"
    print("Part 2 example passed!")

    print(f"Part 1: {part1(data)}")
    print(f"Part 2: {part2(data)}")
