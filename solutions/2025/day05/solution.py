#!/usr/bin/env python3
"""Advent of Code 2025 Day 5: Cafeteria"""

from pathlib import Path


def parse_input(data: str) -> tuple[list[tuple[int, int]], list[int]]:
    """Parse input into ranges and available IDs."""
    parts = data.strip().split('\n\n')
    ranges_str, ids_str = parts[0], parts[1]

    ranges = []
    for line in ranges_str.strip().split('\n'):
        start, end = line.split('-')
        ranges.append((int(start), int(end)))

    available_ids = [int(line) for line in ids_str.strip().split('\n')]

    return ranges, available_ids


def is_fresh(ingredient_id: int, ranges: list[tuple[int, int]]) -> bool:
    """Check if an ingredient ID falls within any fresh range."""
    for start, end in ranges:
        if start <= ingredient_id <= end:
            return True
    return False


def part1(data: str) -> int:
    """Count how many available ingredient IDs are fresh."""
    ranges, available_ids = parse_input(data)

    # Sort ranges for potential early termination
    ranges.sort()

    fresh_count = 0
    for ingredient_id in available_ids:
        if is_fresh(ingredient_id, ranges):
            fresh_count += 1

    return fresh_count


def merge_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Merge overlapping ranges into non-overlapping ranges."""
    if not ranges:
        return []

    # Sort by start
    sorted_ranges = sorted(ranges)
    merged = [sorted_ranges[0]]

    for start, end in sorted_ranges[1:]:
        last_start, last_end = merged[-1]
        # Check if overlapping or adjacent
        if start <= last_end + 1:
            # Extend the last range
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))

    return merged


def part2(data: str) -> int:
    """Count total unique ingredient IDs covered by all ranges."""
    ranges, _ = parse_input(data)

    # Merge overlapping ranges
    merged = merge_ranges(ranges)

    # Count total IDs
    total = 0
    for start, end in merged:
        total += end - start + 1

    return total


if __name__ == "__main__":
    input_file = Path(__file__).parent / "input.txt"
    data = input_file.read_text()

    # Test with example
    EXAMPLE = """3-5
10-14
16-20
12-18

1
5
8
11
17
32"""

    result = part1(EXAMPLE)
    assert result == 3, f"Expected 3, got {result}"
    print("Part 1 example passed!")

    result2 = part2(EXAMPLE)
    assert result2 == 14, f"Expected 14, got {result2}"
    print("Part 2 example passed!")

    print(f"Part 1: {part1(data)}")
    print(f"Part 2: {part2(data)}")
