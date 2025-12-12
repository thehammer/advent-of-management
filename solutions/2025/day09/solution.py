#!/usr/bin/env python3
"""Advent of Code 2025 Day 9: Movie Theater"""

from pathlib import Path


def parse_input(data: str):
    """Parse the puzzle input."""
    lines = data.strip().split('\n')
    points = []
    for line in lines:
        x, y = map(int, line.split(','))
        points.append((x, y))
    return points


def part1(data) -> int:
    """Solve Part 1: Find maximum rectangle area."""
    points = parse_input(data)

    max_area = 0
    n = len(points)

    # Try all pairs of points as opposite corners
    for i in range(n):
        for j in range(i + 1, n):
            x1, y1 = points[i]
            x2, y2 = points[j]

            # Calculate area (width * height) - inclusive counting
            width = abs(x2 - x1) + 1
            height = abs(y2 - y1) + 1
            area = width * height

            max_area = max(max_area, area)

    return max_area


def part2(data) -> int:
    """Solve Part 2: Rectangle must only contain red/green tiles.

    Uses geometric approach - checks if rectangle is fully contained
    in the polygon without iterating over individual tiles.
    """
    points = parse_input(data)
    n = len(points)

    # Build horizontal and vertical segments of the polygon boundary
    h_segments = []  # (y, x1, x2)
    v_segments = []  # (x, y1, y2)

    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        if y1 == y2:  # horizontal
            h_segments.append((y1, min(x1, x2), max(x1, x2)))
        else:  # vertical
            v_segments.append((x1, min(y1, y2), max(y1, y2)))

    def point_in_polygon(px, py):
        """Ray casting algorithm."""
        inside = False
        j = n - 1
        for i in range(n):
            xi, yi = points[i]
            xj, yj = points[j]
            if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        return inside

    def on_boundary(px, py):
        """Check if point is on the polygon boundary."""
        for y, x1, x2 in h_segments:
            if y == py and x1 <= px <= x2:
                return True
        for x, y1, y2 in v_segments:
            if x == px and y1 <= py <= y2:
                return True
        return False

    def is_valid_point(px, py):
        """Check if point is inside polygon or on boundary."""
        return on_boundary(px, py) or point_in_polygon(px, py)

    def rect_edges_cross_polygon(min_x, max_x, min_y, max_y):
        """Check if any polygon edge enters the rectangle interior."""
        # Check horizontal polygon segments
        for y, x1, x2 in h_segments:
            if min_y < y < max_y:  # Segment at y-level inside rect's y-range
                # Check if segment enters rect from left or right
                if x1 < min_x < x2 or x1 < max_x < x2:
                    return True
                # Check if segment completely crosses through rect horizontally
                if x1 < min_x and x2 > max_x:
                    return True

        # Check vertical polygon segments
        for x, y1, y2 in v_segments:
            if min_x < x < max_x:  # Segment at x-level inside rect's x-range
                if y1 < min_y < y2 or y1 < max_y < y2:
                    return True
                if y1 < min_y and y2 > max_y:
                    return True

        return False

    def is_valid_rectangle(x1, y1, x2, y2):
        """Check if rectangle is fully contained in the polygon."""
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)

        # Check all 4 corners are valid (inside or on boundary)
        corners = [(min_x, min_y), (min_x, max_y), (max_x, min_y), (max_x, max_y)]
        for cx, cy in corners:
            if not is_valid_point(cx, cy):
                return False

        # Check no polygon edges cross into rectangle interior
        if rect_edges_cross_polygon(min_x, max_x, min_y, max_y):
            return False

        return True

    # Sort pairs by potential area (descending) to find large valid ones early
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            x1, y1 = points[i]
            x2, y2 = points[j]
            area = (abs(x2 - x1) + 1) * (abs(y2 - y1) + 1)
            pairs.append((area, i, j))

    pairs.sort(reverse=True)

    max_area = 0
    for area, i, j in pairs:
        if area <= max_area:
            break  # No more can beat current best

        x1, y1 = points[i]
        x2, y2 = points[j]

        if is_valid_rectangle(x1, y1, x2, y2):
            max_area = area

    return max_area


if __name__ == "__main__":
    # Test with example
    EXAMPLE = """7,1
11,1
11,7
9,7
9,5
2,5
2,3
7,3"""

    example_result = part1(EXAMPLE)
    print(f"Example Part 1: {example_result}")
    assert example_result == 50, f"Expected 50, got {example_result}"

    example_result2 = part2(EXAMPLE)
    print(f"Example Part 2: {example_result2}")
    assert example_result2 == 24, f"Expected 24, got {example_result2}"

    # Solve with real input
    input_file = Path(__file__).parent / "input.txt"
    data = input_file.read_text()

    print(f"Part 1: {part1(data)}")
    print(f"Part 2: {part2(data)}")
