#!/usr/bin/env python3
"""Advent of Code 2025 Day 11: Reactor"""

from functools import cache
from pathlib import Path


def parse_input(data: str) -> dict[str, list[str]]:
    """Parse the puzzle input into a graph (adjacency list)."""
    graph = {}
    for line in data.strip().split('\n'):
        parts = line.split(': ')
        node = parts[0]
        if len(parts) > 1:
            children = parts[1].split()
        else:
            children = []
        graph[node] = children
    return graph


def part1(data: str) -> int:
    """Count all paths from 'you' to 'out'."""
    graph = parse_input(data)

    @cache
    def count_paths(node: str) -> int:
        if node == 'out':
            return 1
        if node not in graph:
            return 0
        return sum(count_paths(child) for child in graph[node])

    return count_paths('you')


def part2(data: str) -> int:
    """Count paths from 'svr' to 'out' that visit both 'dac' and 'fft'."""
    graph = parse_input(data)

    @cache
    def count_paths(node: str, visited_dac: bool, visited_fft: bool) -> int:
        # Update visited flags based on current node
        if node == 'dac':
            visited_dac = True
        if node == 'fft':
            visited_fft = True

        if node == 'out':
            # Only count if we've visited both dac and fft
            return 1 if (visited_dac and visited_fft) else 0
        if node not in graph:
            return 0

        return sum(count_paths(child, visited_dac, visited_fft) for child in graph[node])

    return count_paths('svr', False, False)


# Example from the problem
EXAMPLE = """aaa: you hhh
you: bbb ccc
bbb: ddd eee
ccc: ddd eee fff
ddd: ggg
eee: out
fff: out
ggg: out
hhh: ccc fff iii
iii: out"""

EXAMPLE2 = """svr: aaa bbb
aaa: fft
fft: ccc
bbb: tty
tty: ccc
ccc: ddd eee
ddd: hub
hub: fff
eee: dac
dac: fff
fff: ggg hhh
ggg: out
hhh: out"""


if __name__ == "__main__":
    # Test with example
    result = part1(EXAMPLE)
    print(f"Example Part 1: {result}")
    assert result == 5, f"Expected 5, got {result}"
    print("Example passed!")

    # Test Part 2 with example
    result2 = part2(EXAMPLE2)
    print(f"Example Part 2: {result2}")
    assert result2 == 2, f"Expected 2, got {result2}"
    print("Example 2 passed!")

    # Run on actual input
    input_file = Path(__file__).parent / "input.txt"
    data = input_file.read_text()

    print(f"\nPart 1: {part1(data)}")
    print(f"Part 2: {part2(data)}")
