import sys
from z3 import Solver, BoolRef, Bool, Int, And, Or, Sum, sat

row_constraints = [[1, 1, 2, 4], [1, 1, 1, 1], [2, 4, 1, 2, 2], [1, 2, 2, 1], [3, 1, 1, 3, 2], [2, 2, 1, 2], [1, 6, 2, 1],
                   [1, 1, 2, 3, 2], [1, 2, 1, 2, 2], [2, 1, 2, 2], [1, 1, 1, 1, 2, 2], [2, 1, 1, 1, 1, 3], [1, 1, 2, 6],
                   [4, 2, 5], [1, 5, 4, 1]]
col_constraints = [[1, 1, 3, 3, 1], [1, 1, 1, 1, 1], [1, 1, 2, 3], [4, 2, 2, 2], [1, 3, 1, 2, 2], [1, 1, 1, 1, 1], [1, 6, 5],
                   [1, 4, 2], [1, 1, 1, 1, 1], [1, 2, 3, 3], [1, 3, 3, 5], [1, 1, 4, 1, 3], [2, 1, 3], [1, 4, 8], [2, 5, 3]]

ROW_COUNT = len(row_constraints)
COL_COUNT = len(col_constraints)


def cell(x: int, y: int):
    return Bool(f"cell_{x}_{y}")


def row(y: int):
    return list(map(lambda x: cell(x, y), range(ROW_COUNT)))


def column(x: int):
    return list(map(lambda y: cell(x, y), range(COL_COUNT)))


def add_stripe_constraints(solver: Solver, name: str, constraints: list[int], stripe: list[BoolRef]):
    cell_count = len(stripe)
    group_count = len(constraints)
    group_start = list(map(lambda i: Int(f"{name}_{i}_start"), range(group_count)))
    group_end = list(map(lambda i: Int(f"{name}_{i}_end"), range(group_count)))

    for i in range(group_count):
        solver.add(group_start[i] >= 0, group_start[i] <= cell_count)
        solver.add(group_end[i] >= 0, group_end[i] <= cell_count)
        solver.add(group_end[i] - group_start[i] == constraints[i] - 1)

    for i, j in zip(range(group_count), range(1, group_count)):
        solver.add(group_start[j] > group_end[i] + 1)

    for k in range(cell_count):
        is_cell_in_group = list(map(lambda i: And(k >= group_start[i], k <= group_end[i]), range(group_count)))  # pylint: disable=cell-var-from-loop
        solver.add(stripe[k] == Or(*is_cell_in_group))

    solver.add(Sum(*constraints) == Sum(*stripe))


if __name__ == "__main__":
    solver = Solver()

    for x, col_constraint in enumerate(col_constraints):
        add_stripe_constraints(solver, f"column_{x}", col_constraint, column(x))

    for y, row_constraint in enumerate(row_constraints):
        add_stripe_constraints(solver, f"row_{y}", row_constraint, row(y))

    if (solver.check() != sat):
        print("unsat")
        sys.exit(1)

    result = solver.model()
    for y in range(ROW_COUNT):
        for x in range(COL_COUNT):
            if result[cell(x, y)]:
                print(f"{y * COL_COUNT + x + 1}", end=" ")
