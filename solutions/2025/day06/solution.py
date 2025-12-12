#!/usr/bin/env python3
"""Advent of Code 2025 Day 6: Trash Compactor"""

from pathlib import Path
from functools import reduce
from operator import mul


def parse_problems(data: str) -> list[tuple[list[int], str]]:
    """
    Parse the worksheet into problems.
    Returns list of (numbers, operation) tuples.
    """
    lines = data.rstrip('\n').split('\n')

    # Last line contains operations
    ops_line = lines[-1]
    num_lines = lines[:-1]

    # Pad all lines to same length
    max_len = max(len(line) for line in lines)
    num_lines = [line.ljust(max_len) for line in num_lines]
    ops_line = ops_line.ljust(max_len)

    # Find problem boundaries by looking at columns
    # Problems are separated by columns that are all spaces (in number rows)
    problems = []
    col = 0

    while col < max_len:
        # Skip separator columns (all spaces in number rows)
        while col < max_len:
            all_space = all(line[col] == ' ' for line in num_lines)
            if not all_space:
                break
            col += 1

        if col >= max_len:
            break

        # Find end of this problem (next all-space column or end)
        start_col = col
        while col < max_len:
            all_space = all(line[col] == ' ' for line in num_lines)
            if all_space:
                break
            col += 1
        end_col = col

        # Extract numbers from this column range
        numbers = []
        for line in num_lines:
            segment = line[start_col:end_col].strip()
            if segment and segment.isdigit():
                numbers.append(int(segment))

        # Find operation (look in ops_line for this column range)
        op_segment = ops_line[start_col:end_col].strip()
        # Operation should be + or *
        op = '+' if '+' in op_segment else '*'

        if numbers:
            problems.append((numbers, op))

    return problems


def solve_problem(numbers: list[int], op: str) -> int:
    """Solve a single problem."""
    if op == '+':
        return sum(numbers)
    else:  # '*'
        return reduce(mul, numbers, 1)


def part1(data: str) -> int:
    """Sum all problem answers."""
    problems = parse_problems(data)
    total = 0
    for numbers, op in problems:
        total += solve_problem(numbers, op)
    return total


def parse_problems_v2(data: str) -> list[tuple[list[int], str]]:
    """
    Parse problems reading numbers column-wise, right-to-left.
    Each column within a problem forms a number (top=most significant).
    """
    lines = data.rstrip('\n').split('\n')

    ops_line = lines[-1]
    num_lines = lines[:-1]

    max_len = max(len(line) for line in lines)
    num_lines = [line.ljust(max_len) for line in num_lines]
    ops_line = ops_line.ljust(max_len)

    problems = []
    col = 0

    while col < max_len:
        # Skip separator columns
        while col < max_len:
            all_space = all(line[col] == ' ' for line in num_lines)
            if not all_space:
                break
            col += 1

        if col >= max_len:
            break

        # Find end of this problem
        start_col = col
        while col < max_len:
            all_space = all(line[col] == ' ' for line in num_lines)
            if all_space:
                break
            col += 1
        end_col = col

        # Read numbers column by column, right to left
        numbers = []
        for c in range(end_col - 1, start_col - 1, -1):
            # Read digits top to bottom in this column
            digits = []
            for line in num_lines:
                ch = line[c]
                if ch.isdigit():
                    digits.append(ch)
            if digits:
                numbers.append(int(''.join(digits)))

        # Find operation
        op_segment = ops_line[start_col:end_col].strip()
        op = '+' if '+' in op_segment else '*'

        if numbers:
            problems.append((numbers, op))

    return problems


def part2(data: str) -> int:
    """Sum all problem answers using column-wise right-to-left reading."""
    problems = parse_problems_v2(data)
    total = 0
    for numbers, op in problems:
        total += solve_problem(numbers, op)
    return total


if __name__ == "__main__":
    input_file = Path(__file__).parent / "input.txt"
    data = input_file.read_text()

    # Test with example
    EXAMPLE = """123 328  51 64
 45 64  387 23
  6 98  215 314
*   +   *   +"""

    result = part1(EXAMPLE)
    assert result == 4277556, f"Expected 4277556, got {result}"
    print("Part 1 example passed!")

    result2 = part2(EXAMPLE)
    assert result2 == 3263827, f"Expected 3263827, got {result2}"
    print("Part 2 example passed!")

    print(f"Part 1: {part1(data)}")
    print(f"Part 2: {part2(data)}")
