#!/usr/bin/env python3
"""Advent of Code 2025 Day 8: Playground"""

from pathlib import Path
from collections import Counter
import heapq


class UnionFind:
    """Union-Find data structure for tracking connected components."""

    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.size = [1] * n

    def find(self, x: int) -> int:
        """Find root with path compression."""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        """Union two sets. Returns True if they were in different sets."""
        px, py = self.find(x), self.find(y)
        if px == py:
            return False  # Already in same set

        # Union by rank
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        self.size[px] += self.size[py]
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True

    def get_sizes(self) -> list[int]:
        """Get sizes of all components."""
        roots = set(self.find(i) for i in range(len(self.parent)))
        return [self.size[r] for r in roots]


def parse_input(data: str) -> list[tuple[int, int, int]]:
    """Parse the puzzle input into list of 3D coordinates."""
    points = []
    for line in data.strip().split('\n'):
        x, y, z = map(int, line.split(','))
        points.append((x, y, z))
    return points


def distance_squared(p1: tuple[int, int, int], p2: tuple[int, int, int]) -> int:
    """Calculate squared Euclidean distance (avoid sqrt for comparison)."""
    return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 + (p1[2] - p2[2])**2


def part1(data: str, num_connections: int = 1000) -> int:
    """
    Connect the num_connections closest pairs of junction boxes.
    Return product of sizes of 3 largest circuits.
    """
    points = parse_input(data)
    n = len(points)

    # Calculate all pairwise distances
    # Use heap to efficiently get smallest distances
    distances = []
    for i in range(n):
        for j in range(i + 1, n):
            dist_sq = distance_squared(points[i], points[j])
            distances.append((dist_sq, i, j))

    # Sort by distance
    distances.sort()

    # Union-Find to track circuits
    uf = UnionFind(n)

    # Process connections (closest first)
    connections_made = 0
    for dist_sq, i, j in distances:
        if connections_made >= num_connections:
            break
        # Try to connect - union returns True if they were separate
        uf.union(i, j)
        connections_made += 1

    # Get sizes of all circuits
    sizes = sorted(uf.get_sizes(), reverse=True)

    # Multiply top 3
    result = 1
    for i in range(min(3, len(sizes))):
        result *= sizes[i]

    return result


def part2(data: str) -> int:
    """
    Part 2: Connect until all in one circuit.
    Return product of X coordinates of the last two junction boxes connected.
    """
    points = parse_input(data)
    n = len(points)

    # Calculate all pairwise distances
    distances = []
    for i in range(n):
        for j in range(i + 1, n):
            dist_sq = distance_squared(points[i], points[j])
            distances.append((dist_sq, i, j))

    # Sort by distance
    distances.sort()

    # Use Kruskal's MST - connect until we have a single circuit
    uf = UnionFind(n)
    connections_made = 0
    last_i, last_j = 0, 0

    for dist_sq, i, j in distances:
        if uf.union(i, j):
            connections_made += 1
            last_i, last_j = i, j
            if connections_made == n - 1:
                # All connected into one circuit
                break

    # Return product of X coordinates
    return points[last_i][0] * points[last_j][0]


if __name__ == "__main__":
    input_file = Path(__file__).parent / "input.txt"
    data = input_file.read_text()

    # Test with example
    EXAMPLE = """162,817,812
57,618,57
906,360,560
592,479,940
352,342,300
466,668,158
542,29,236
431,825,988
739,650,466
52,470,668
216,146,977
819,987,18
117,168,530
805,96,715
346,949,466
970,615,88
941,993,340
862,61,35
984,92,344
425,690,689"""

    result = part1(EXAMPLE, num_connections=10)
    assert result == 40, f"Expected 40, got {result}"
    print("Part 1 example passed!")

    print(f"Part 1: {part1(data)}")
    print(f"Part 2: {part2(data)}")
