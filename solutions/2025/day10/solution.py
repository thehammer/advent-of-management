#!/usr/bin/env python3
"""Advent of Code 2025 Day 10: Factory"""

import re
from pathlib import Path
from itertools import product


def parse_input(data: str):
    """Parse the puzzle input."""
    machines = []
    for line in data.strip().split('\n'):
        # Extract target pattern
        target_match = re.search(r'\[([.#]+)\]', line)
        target = target_match.group(1)
        target_bits = [1 if c == '#' else 0 for c in target]

        # Extract button wirings
        buttons = []
        for btn_match in re.finditer(r'\(([0-9,]+)\)', line):
            indices = [int(x) for x in btn_match.group(1).split(',')]
            buttons.append(indices)

        # Extract joltage requirements
        joltage_match = re.search(r'\{([0-9,]+)\}', line)
        joltage = [int(x) for x in joltage_match.group(1).split(',')]

        machines.append((target_bits, buttons, joltage))
    return machines


def solve_machine_brute(target_bits, buttons):
    """Brute force: try all combinations of button presses."""
    n_lights = len(target_bits)
    n_buttons = len(buttons)

    # Create button effect vectors
    button_vectors = []
    for btn in buttons:
        vec = [0] * n_lights
        for idx in btn:
            if idx < n_lights:
                vec[idx] = 1
        button_vectors.append(vec)

    min_presses = float('inf')

    # Try all 2^n_buttons combinations
    for combo in product([0, 1], repeat=n_buttons):
        # Calculate resulting state
        state = [0] * n_lights
        for i, pressed in enumerate(combo):
            if pressed:
                for j in range(n_lights):
                    state[j] ^= button_vectors[i][j]

        # Check if matches target
        if state == target_bits:
            presses = sum(combo)
            min_presses = min(min_presses, presses)

    return min_presses if min_presses != float('inf') else -1


def gaussian_elimination_gf2(matrix, target):
    """Solve system over GF(2) using Gaussian elimination.
    Returns all solutions as a list of basis vectors for null space + particular solution."""
    n_rows = len(matrix)
    n_cols = len(matrix[0]) if matrix else 0

    # Augmented matrix
    aug = [row[:] + [target[i]] for i, row in enumerate(matrix)]

    pivot_cols = []
    row = 0

    for col in range(n_cols):
        # Find pivot
        pivot_row = None
        for r in range(row, n_rows):
            if aug[r][col] == 1:
                pivot_row = r
                break

        if pivot_row is None:
            continue

        pivot_cols.append(col)

        # Swap rows
        aug[row], aug[pivot_row] = aug[pivot_row], aug[row]

        # Eliminate
        for r in range(n_rows):
            if r != row and aug[r][col] == 1:
                for c in range(n_cols + 1):
                    aug[r][c] ^= aug[row][c]

        row += 1

    # Check consistency
    for r in range(row, n_rows):
        if aug[r][n_cols] == 1:
            return None  # No solution

    # Find free variables
    free_vars = [c for c in range(n_cols) if c not in pivot_cols]

    # Build particular solution (all free vars = 0)
    particular = [0] * n_cols
    for i, pc in enumerate(pivot_cols):
        particular[pc] = aug[i][n_cols]

    # Build null space basis
    null_basis = []
    for fv in free_vars:
        vec = [0] * n_cols
        vec[fv] = 1
        for i, pc in enumerate(pivot_cols):
            vec[pc] = aug[i][fv]
        null_basis.append(vec)

    return particular, null_basis


def min_weight_solution(particular, null_basis):
    """Find minimum weight solution by trying all combinations of null space vectors."""
    if not null_basis:
        return sum(particular)

    min_weight = sum(particular)
    n_basis = len(null_basis)
    n_vars = len(particular)

    # Try all 2^n_basis combinations
    for combo in product([0, 1], repeat=n_basis):
        sol = particular[:]
        for i, use in enumerate(combo):
            if use:
                for j in range(n_vars):
                    sol[j] ^= null_basis[i][j]
        weight = sum(sol)
        min_weight = min(min_weight, weight)

    return min_weight


def solve_machine(target_bits, buttons):
    """Solve using Gaussian elimination over GF(2)."""
    n_lights = len(target_bits)
    n_buttons = len(buttons)

    if n_buttons == 0:
        return 0 if all(t == 0 for t in target_bits) else -1

    # Create matrix where each column is a button's effect
    # Each row is a light
    # matrix[i][j] = 1 if button j affects light i
    matrix = [[0] * n_buttons for _ in range(n_lights)]
    for j, btn in enumerate(buttons):
        for idx in btn:
            if idx < n_lights:
                matrix[idx][j] = 1

    result = gaussian_elimination_gf2(matrix, target_bits)

    if result is None:
        return -1

    particular, null_basis = result
    return min_weight_solution(particular, null_basis)


def part1(data) -> int:
    """Solve Part 1."""
    machines = parse_input(data)
    total = 0
    for target_bits, buttons, joltage in machines:
        presses = solve_machine(target_bits, buttons)
        if presses == -1:
            raise ValueError("No solution found!")
        total += presses
    return total


def solve_joltage(joltage, buttons):
    """Solve Part 2 using Gaussian elimination + enumeration of null space.

    Solve Ax = b where A is the incidence matrix, b = joltage.
    Find minimum sum(x) with x >= 0 and integral.
    """
    from fractions import Fraction

    n_counters = len(joltage)
    n_buttons = len(buttons)

    if n_buttons == 0:
        return 0 if all(j == 0 for j in joltage) else -1

    # Build constraint matrix [A | b]
    matrix = [[Fraction(0)] * (n_buttons + 1) for _ in range(n_counters)]
    for j, btn in enumerate(buttons):
        for idx in btn:
            if idx < n_counters:
                matrix[idx][j] = Fraction(1)
    for i in range(n_counters):
        matrix[i][n_buttons] = Fraction(joltage[i])

    # Gaussian elimination
    pivot_cols = []
    row = 0
    for col in range(n_buttons):
        pivot_row = None
        for r in range(row, n_counters):
            if matrix[r][col] != 0:
                pivot_row = r
                break
        if pivot_row is None:
            continue
        pivot_cols.append(col)
        matrix[row], matrix[pivot_row] = matrix[pivot_row], matrix[row]
        pivot_val = matrix[row][col]
        for c in range(n_buttons + 1):
            matrix[row][c] /= pivot_val
        for r in range(n_counters):
            if r != row and matrix[r][col] != 0:
                factor = matrix[r][col]
                for c in range(n_buttons + 1):
                    matrix[r][c] -= factor * matrix[row][c]
        row += 1

    # Check consistency
    for r in range(row, n_counters):
        if matrix[r][n_buttons] != 0:
            return -1

    free_vars = [c for c in range(n_buttons) if c not in pivot_cols]

    # Map pivot cols to rows
    pivot_to_row = {pc: i for i, pc in enumerate(pivot_cols)}

    # Particular solution (free vars = 0)
    x_part = [Fraction(0)] * n_buttons
    for pc in pivot_cols:
        x_part[pc] = matrix[pivot_to_row[pc]][n_buttons]

    # Null space basis vectors
    null_basis = []
    for fv in free_vars:
        vec = [Fraction(0)] * n_buttons
        vec[fv] = Fraction(1)
        for pc in pivot_cols:
            vec[pc] = -matrix[pivot_to_row[pc]][fv]
        null_basis.append(vec)

    # If no free variables, check if particular solution is valid
    if not null_basis:
        if all(xi >= 0 and xi.denominator == 1 for xi in x_part):
            return sum(int(xi) for xi in x_part)
        return -1

    # Search over null space to find minimum weight non-negative integer solution
    # x = x_part + sum(t_i * null_basis[i])
    # Need all components >= 0 and integers

    from math import gcd, ceil, floor

    def lcm(a, b):
        return a * b // gcd(a, b)

    # Compute the LCM of denominators
    all_denoms = set()
    for vec in null_basis:
        for v in vec:
            all_denoms.add(v.denominator)
    for v in x_part:
        all_denoms.add(v.denominator)
    common_denom = 1
    for d in all_denoms:
        common_denom = lcm(common_denom, d)

    # Scale everything to integers
    x_part_scaled = [int(xi * common_denom) for xi in x_part]
    null_basis_scaled = [[int(v * common_denom) for v in vec] for vec in null_basis]

    max_t = max(max(joltage), 300) + 50
    best = float('inf')

    # For 1-2 free variables, use efficient search
    n_free = len(null_basis_scaled)

    if n_free == 1:
        vec = null_basis_scaled[0]
        t_lower, t_upper = -max_t, max_t

        for i in range(n_buttons):
            if vec[i] > 0:
                bound = ceil(-x_part_scaled[i] / vec[i])
                t_lower = max(t_lower, bound)
            elif vec[i] < 0:
                bound = floor(-x_part_scaled[i] / vec[i])
                t_upper = min(t_upper, bound)

        for t in range(t_lower, t_upper + 1):
            x = [x_part_scaled[i] + t * vec[i] for i in range(n_buttons)]
            if all(xi >= 0 and xi % common_denom == 0 for xi in x):
                total = sum(xi // common_denom for xi in x)
                best = min(best, total)

    elif n_free == 2:
        vec0, vec1 = null_basis_scaled

        # First, find bounds for t1 based only on vec1
        for t1 in range(-max_t, max_t + 1):
            x_after_t1 = [x_part_scaled[i] + t1 * vec1[i] for i in range(n_buttons)]

            # Now find bounds for t0
            t0_lower, t0_upper = -max_t, max_t
            for i in range(n_buttons):
                if vec0[i] > 0:
                    bound = ceil(-x_after_t1[i] / vec0[i])
                    t0_lower = max(t0_lower, bound)
                elif vec0[i] < 0:
                    bound = floor(-x_after_t1[i] / vec0[i])
                    t0_upper = min(t0_upper, bound)

            if t0_lower > t0_upper:
                continue

            for t0 in range(t0_lower, t0_upper + 1):
                x = [x_after_t1[i] + t0 * vec0[i] for i in range(n_buttons)]
                if all(xi >= 0 and xi % common_denom == 0 for xi in x):
                    total = sum(xi // common_denom for xi in x)
                    best = min(best, total)

    else:
        # For 3+ free variables, use recursive search
        # Only apply bounds at the last level
        def search(idx, current_x_scaled):
            nonlocal best

            if idx == n_free:
                if all(xs >= 0 and xs % common_denom == 0 for xs in current_x_scaled):
                    total = sum(xs // common_denom for xs in current_x_scaled)
                    best = min(best, total)
                return

            vec = null_basis_scaled[idx]

            if idx == n_free - 1:
                # Last variable - use tight bounds
                t_lower, t_upper = -max_t, max_t
                for i in range(n_buttons):
                    if vec[i] > 0:
                        bound = ceil(-current_x_scaled[i] / vec[i])
                        t_lower = max(t_lower, bound)
                    elif vec[i] < 0:
                        bound = floor(-current_x_scaled[i] / vec[i])
                        t_upper = min(t_upper, bound)

                if t_lower > t_upper:
                    return

                for t in range(t_lower, t_upper + 1):
                    new_x = [current_x_scaled[i] + t * vec[i] for i in range(n_buttons)]
                    search(idx + 1, new_x)
            else:
                # Earlier variables - search full range
                for t in range(-max_t, max_t + 1):
                    new_x = [current_x_scaled[i] + t * vec[i] for i in range(n_buttons)]
                    search(idx + 1, new_x)

        search(0, x_part_scaled)

    return best if best != float('inf') else -1


def part2(data) -> int:
    """Solve Part 2."""
    machines = parse_input(data)
    total = 0
    for idx, (target_bits, buttons, joltage) in enumerate(machines):
        presses = solve_joltage(joltage, buttons)
        if presses == -1:
            print(f"Machine {idx}: joltage={joltage}, buttons={buttons}")
            raise ValueError("No solution found!")
        total += presses
    return total


if __name__ == "__main__":
    input_file = Path(__file__).parent / "input.txt"
    data = input_file.read_text()

    print(f"Part 1: {part1(data)}")
    print(f"Part 2: {part2(data)}")
