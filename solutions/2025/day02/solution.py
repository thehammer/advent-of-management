#!/usr/bin/env python3
"""Advent of Code 2025 Day 2: Gift Shop"""

from pathlib import Path


def is_invalid_id(n: int) -> bool:
    """
    Check if a number is an "invalid ID" - made of a digit sequence repeated twice.
    Examples: 55 (5+5), 6464 (64+64), 123123 (123+123)
    """
    s = str(n)
    length = len(s)

    # Must have even length to be a repeated pattern
    if length % 2 != 0:
        return False

    half = length // 2
    return s[:half] == s[half:]


def parse_input(data: str) -> list[tuple[int, int]]:
    """Parse ranges from comma-separated input."""
    ranges = []
    # Handle potential whitespace/newlines in input
    data = data.replace('\n', '').replace(' ', '')

    for part in data.strip().split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            start, end = part.split('-')
            ranges.append((int(start), int(end)))
    return ranges


def find_invalid_ids_in_range(start: int, end: int) -> list[int]:
    """
    Find all invalid IDs in a range efficiently.
    Instead of checking every number, generate candidates.
    """
    invalid = []

    # Determine the digit lengths we need to check
    min_digits = len(str(start))
    max_digits = len(str(end))

    for total_digits in range(min_digits, max_digits + 1):
        # Invalid IDs must have even digit count
        if total_digits % 2 != 0:
            continue

        half_digits = total_digits // 2

        # Generate all half-patterns and check if doubled version is in range
        # Half pattern ranges from 10^(half_digits-1) to 10^half_digits - 1
        # (except for 1-digit half which is 1-9)
        if half_digits == 1:
            half_start, half_end = 1, 9
        else:
            half_start = 10 ** (half_digits - 1)
            half_end = 10 ** half_digits - 1

        for half in range(half_start, half_end + 1):
            # Create the invalid ID by repeating the half
            half_str = str(half)
            invalid_id = int(half_str + half_str)

            if start <= invalid_id <= end:
                invalid.append(invalid_id)

    return invalid


def part1(data: str) -> int:
    """Sum all invalid IDs across all ranges."""
    ranges = parse_input(data)
    total = 0

    for start, end in ranges:
        invalid_ids = find_invalid_ids_in_range(start, end)
        total += sum(invalid_ids)

    return total


def find_invalid_ids_in_range_v2(start: int, end: int) -> set[int]:
    """
    Find all invalid IDs in a range for Part 2.
    Invalid = digit sequence repeated at least twice.
    """
    invalid = set()

    min_digits = len(str(start))
    max_digits = len(str(end))

    for total_digits in range(min_digits, max_digits + 1):
        # For each possible pattern length (1, 2, 3, ...) that divides total_digits
        # and repeats at least twice
        for pattern_len in range(1, total_digits // 2 + 1):
            if total_digits % pattern_len != 0:
                continue

            repeat_count = total_digits // pattern_len
            if repeat_count < 2:
                continue

            # Generate all patterns of this length
            if pattern_len == 1:
                pattern_start, pattern_end = 1, 9
            else:
                pattern_start = 10 ** (pattern_len - 1)
                pattern_end = 10 ** pattern_len - 1

            for pattern in range(pattern_start, pattern_end + 1):
                pattern_str = str(pattern)
                invalid_id = int(pattern_str * repeat_count)

                if start <= invalid_id <= end:
                    invalid.add(invalid_id)

    return invalid


def part2(data: str) -> int:
    """Sum all invalid IDs (repeated at least twice) across all ranges."""
    ranges = parse_input(data)
    total = 0

    for start, end in ranges:
        invalid_ids = find_invalid_ids_in_range_v2(start, end)
        total += sum(invalid_ids)

    return total


if __name__ == "__main__":
    input_file = Path(__file__).parent / "input.txt"
    data = input_file.read_text()

    # Test with example
    EXAMPLE = """11-22,95-115,998-1012,1188511880-1188511890,222220-222224,
1698522-1698528,446443-446449,38593856-38593862,565653-565659,
824824821-824824827,2121212118-2121212124"""

    result = part1(EXAMPLE)
    assert result == 1227775554, f"Expected 1227775554, got {result}"
    print("Part 1 example passed!")

    result2 = part2(EXAMPLE)
    assert result2 == 4174379265, f"Expected 4174379265, got {result2}"
    print("Part 2 example passed!")

    print(f"Part 1: {part1(data)}")
    print(f"Part 2: {part2(data)}")
