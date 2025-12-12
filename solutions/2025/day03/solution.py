#!/usr/bin/env python3
"""Advent of Code 2025 Day 3: Lobby"""

from pathlib import Path


def max_joltage_from_bank(bank: str) -> int:
    """
    Find the maximum 2-digit joltage from a bank.
    Pick exactly 2 batteries (digits) to form the largest number.
    The digits keep their relative order.
    """
    best = 0
    n = len(bank)

    # Try all pairs of positions (i, j) where i < j
    for i in range(n):
        for j in range(i + 1, n):
            joltage = int(bank[i] + bank[j])
            if joltage > best:
                best = joltage

    return best


def part1(data: str) -> int:
    """Sum the maximum joltage from each bank."""
    total = 0
    for line in data.strip().split('\n'):
        line = line.strip()
        if line:
            total += max_joltage_from_bank(line)
    return total


def max_joltage_from_bank_k(bank: str, k: int) -> int:
    """
    Find the maximum k-digit joltage from a bank using greedy algorithm.
    At each position, pick the largest digit that still leaves enough
    digits remaining to complete the selection.
    """
    n = len(bank)
    if k > n:
        return 0

    result = []
    start = 0

    for i in range(k):
        # Need to pick (k - i) more digits
        # The latest position we can pick from is n - (k - i)
        remaining_needed = k - i
        last_valid_pos = n - remaining_needed

        # Find the largest digit in range [start, last_valid_pos]
        best_digit = '0'
        best_pos = start
        for pos in range(start, last_valid_pos + 1):
            if bank[pos] > best_digit:
                best_digit = bank[pos]
                best_pos = pos

        result.append(best_digit)
        start = best_pos + 1

    return int(''.join(result))


def part2(data: str) -> int:
    """Sum the maximum 12-digit joltage from each bank."""
    total = 0
    for line in data.strip().split('\n'):
        line = line.strip()
        if line:
            total += max_joltage_from_bank_k(line, 12)
    return total


if __name__ == "__main__":
    input_file = Path(__file__).parent / "input.txt"
    data = input_file.read_text()

    # Test with example
    EXAMPLE = """987654321111111
811111111111119
234234234234278
818181911112111"""

    result = part1(EXAMPLE)
    assert result == 357, f"Expected 357, got {result}"
    print("Part 1 example passed!")

    result2 = part2(EXAMPLE)
    assert result2 == 3121910778619, f"Expected 3121910778619, got {result2}"
    print("Part 2 example passed!")

    print(f"Part 1: {part1(data)}")
    print(f"Part 2: {part2(data)}")
