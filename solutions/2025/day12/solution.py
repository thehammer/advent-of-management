#!/usr/bin/env python3
"""Advent of Code 2025 Day 12: Christmas Tree Farm

Fitting presents into regions. Each shape can be rotated/flipped.
"""

from pathlib import Path
from functools import lru_cache


def parse_input(data: str):
    """Parse shapes and regions from input."""
    lines = data.strip().split('\n')

    # Parse shapes
    shapes = {}
    current_shape = None
    shape_lines = []

    region_start = 0
    for i, line in enumerate(lines):
        if line and line[0].isdigit() and ':' in line and 'x' not in line:
            if current_shape is not None:
                shapes[current_shape] = shape_lines
            current_shape = int(line.split(':')[0])
            shape_lines = []
        elif line and all(c in '.#' for c in line):
            shape_lines.append(line)
        elif 'x' in line:
            if current_shape is not None:
                shapes[current_shape] = shape_lines
            region_start = i
            break

    # Parse regions
    regions = []
    for line in lines[region_start:]:
        if 'x' in line and ':' in line:
            dims, counts_str = line.split(': ')
            w, h = map(int, dims.split('x'))
            counts = list(map(int, counts_str.split()))
            regions.append((w, h, counts))

    return shapes, regions


def count_cells(shape_lines):
    """Count # cells in a shape."""
    return sum(row.count('#') for row in shape_lines)


def get_shape_cells(shape_lines):
    """Get set of (row, col) positions that are #."""
    cells = set()
    for r, row in enumerate(shape_lines):
        for c, ch in enumerate(row):
            if ch == '#':
                cells.add((r, c))
    return cells


def normalize(cells):
    """Normalize cells to start at (0, 0)."""
    if not cells:
        return frozenset()
    min_r = min(r for r, c in cells)
    min_c = min(c for r, c in cells)
    return frozenset((r - min_r, c - min_c) for r, c in cells)


def rotate_90(cells):
    """Rotate cells 90 degrees clockwise."""
    return {(c, -r) for r, c in cells}


def flip_horizontal(cells):
    """Flip cells horizontally."""
    return {(r, -c) for r, c in cells}


def get_all_orientations(cells):
    """Get all 8 orientations (4 rotations x 2 flips)."""
    orientations = set()
    current = cells
    for _ in range(4):
        orientations.add(normalize(current))
        orientations.add(normalize(flip_horizontal(current)))
        current = rotate_90(current)
    return list(orientations)


def precompute_shape_orientations(shapes):
    """Precompute all orientations for all shapes."""
    all_orientations = {}
    for idx, shape_lines in shapes.items():
        cells = get_shape_cells(shape_lines)
        all_orientations[idx] = get_all_orientations(cells)
    return all_orientations


def can_place(grid, w, h, shape_cells, start_r, start_c):
    """Check if shape can be placed at position."""
    for dr, dc in shape_cells:
        r, c = start_r + dr, start_c + dc
        if r < 0 or r >= h or c < 0 or c >= w:
            return False
        if grid[r][c]:
            return False
    return True


def place(grid, shape_cells, start_r, start_c):
    """Place shape on grid."""
    for dr, dc in shape_cells:
        grid[start_r + dr][start_c + dc] = True


def unplace(grid, shape_cells, start_r, start_c):
    """Remove shape from grid."""
    for dr, dc in shape_cells:
        grid[start_r + dr][start_c + dc] = False


def find_first_empty(grid, w, h):
    """Find the first empty cell (top-left)."""
    for r in range(h):
        for c in range(w):
            if not grid[r][c]:
                return (r, c)
    return None


def solve_backtrack(w, h, all_orientations, pieces_to_place):
    """Try to place all pieces using backtracking.

    pieces_to_place: list of (shape_idx, count) for pieces still to place
    """
    grid = [[False] * w for _ in range(h)]

    # Flatten pieces list - group identical shapes together for symmetry breaking
    pieces = []
    for shape_idx, count in pieces_to_place:
        for _ in range(count):
            pieces.append(shape_idx)

    if not pieces:
        return True

    def backtrack(piece_idx, min_pos=0):
        if piece_idx >= len(pieces):
            return True

        shape_idx = pieces[piece_idx]
        orientations = all_orientations[shape_idx]

        # Try all positions from min_pos onward
        # If next piece is same type, use symmetry breaking (start from same position)
        next_min_pos = 0
        if piece_idx + 1 < len(pieces) and pieces[piece_idx + 1] == shape_idx:
            same_type = True
        else:
            same_type = False

        for pos in range(min_pos, w * h):
            r, c = pos // w, pos % w
            for o_idx, orientation in enumerate(orientations):
                if can_place(grid, w, h, orientation, r, c):
                    place(grid, orientation, r, c)
                    # Symmetry breaking: if next piece is same type, don't try earlier positions
                    next_start = pos if same_type else 0
                    if backtrack(piece_idx + 1, next_start):
                        return True
                    unplace(grid, orientation, r, c)

        return False

    return backtrack(0, 0)


def can_fit_region(w, h, shapes, counts, all_orientations):
    """Check if shapes with given counts can fit in w x h region."""
    # First, simple area check
    cells_per_shape = [count_cells(shapes[i]) for i in range(len(shapes))]
    area = w * h
    needed = sum(c * cells_per_shape[i] for i, c in enumerate(counts))

    if needed > area:
        return False

    # Build pieces list
    pieces_to_place = [(i, counts[i]) for i in range(len(counts)) if counts[i] > 0]

    if not pieces_to_place:
        return True

    # Use backtracking
    return solve_backtrack(w, h, all_orientations, pieces_to_place)


def part1(data) -> int:
    """Count regions that can fit all their presents."""
    shapes, regions = parse_input(data)
    all_orientations = precompute_shape_orientations(shapes)

    count = 0
    for i, (w, h, shape_counts) in enumerate(regions):
        if can_fit_region(w, h, shapes, shape_counts, all_orientations):
            count += 1
        if (i + 1) % 100 == 0:
            print(f"Processed {i+1}/{len(regions)} regions, {count} fit so far")

    return count


def part2(data) -> int:
    """Solve Part 2."""
    shapes, regions = parse_input(data)
    # TODO: implement Part 2
    return 0


# Example from puzzle
EXAMPLE = """0:
###
##.
##.

1:
###
##.
.##

2:
.##
###
##.

3:
##.
###
##.

4:
###
#..
###

5:
###
.#.
###

4x4: 0 0 0 0 2 0
12x5: 1 0 1 0 2 2
12x5: 1 0 1 0 3 2
"""


if __name__ == "__main__":
    # Test with example
    print("Testing with example...")
    shapes, regions = parse_input(EXAMPLE)
    print(f"Shapes: {len(shapes)}")
    print(f"Regions: {len(regions)}")
    for i, shape in shapes.items():
        print(f"  Shape {i}: {count_cells(shape)} cells")

    # For example, analyze each region
    all_orientations = precompute_shape_orientations(shapes)
    cells_per = [count_cells(shapes[i]) for i in range(6)]
    print(f"\nAnalyzing example regions:")
    for w, h, counts in regions:
        area = w * h
        needed = sum(c * cells_per[i] for i, c in enumerate(counts))
        slack = (area - needed) / area * 100
        result = can_fit_region(w, h, shapes, counts, all_orientations)
        print(f"  {w}x{h}: needed={needed}, area={area}, slack={slack:.1f}%, fits={result}")

    print(f"\nExample Part 1 (backtracking): {part1(EXAMPLE)}")
    print("(Expected: 2)")

    # Run on real input
    input_file = Path(__file__).parent / "input.txt"
    if input_file.exists():
        data = input_file.read_text()
        print(f"\nReal input Part 1 (simple check): {part1(data)}")
