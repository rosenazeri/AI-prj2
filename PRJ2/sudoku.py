import numpy as np 
from pycsp3 import * 
from myCSP.mycsp import *
from board import Board
from refresher import *
import time
class Layout:
    """
    Represents a Sudoku puzzle layout and provides methods to solve it using different CSP algorithms.

    This class reads a Sudoku layout from a file, initializes the puzzle grid, and provides solving functions
    using both PyCSP and a our csp solver, mycsp (YAY!!!). The solutions enforce constraints such as row, 
    column, and 3x3 block uniqueness, and allow for various heuristic optimizations.

    Attributes:
        clues (list[list[int]]): A 9x9 grid representing the initial Sudoku puzzle state.
    """
    def __init__(self, path):
        """Initializes the Sudoku layout by reading a file and parsing the puzzle grid."""
        with open(path, "r") as file:
            text = file.read()
            words = text.split()
            numbers = []
            for w in words:
                if w == "_":
                    numbers.append(0)
                else:
                    numbers.append(int(w))

        self.clues = np.reshape(numbers, (9, 9)).tolist()

    def get_clues(self):
        """Returns the initial Sudoku clues."""
        return self.clues

    def pycsp_solve (self, puzzle: Board) -> bool:
        """
        Solves the Sudoku puzzle using a Constraint Satisfaction Problem (CSP) solver.
        Returns True if a solution is found, otherwise False.
        """
        clear()

        grid = VarArray(size=[9, 9], dom=range(1, 10))

        for row_idx in range(9):
            for col_idx in range(9):
                if self.clues[row_idx][col_idx] != 0:
                    satisfy(grid[row_idx][col_idx] == self.clues[row_idx][col_idx])

        for row in grid:
            satisfy(AllDifferent(row))

        for col_idx in range(9):
            satisfy(AllDifferent([grid[row_idx][col_idx] for row_idx in range(9)]))

        for block_row in range(0, 9, 3):
            for block_col in range(0, 9, 3):
                block_cells = [grid[row_idx][col_idx] for row_idx in range(block_row, block_row + 3)
                               for col_idx in range(block_col, block_col + 3)]
                satisfy(AllDifferent(block_cells))

        if solve():
            solution_values = values(grid)

            puzzle.answer_board = [[solution_values[row_idx][col_idx] for col_idx in range(9)] for row_idx in range(9)]

            return True
        else:
            return False

    def mycsp_solve(self, puzzle: Board,
                    use_unary_check: bool,
                    use_arc_consistency: bool,
                    use_mrv: bool,
                    use_lcv: bool,
                    real_time: bool,
                    refresh_callback: Callable[[], None],
                    stop_condition: Callable[[], bool]) -> bool:
        my_clear()

        variables_grid = myVarArray("SudokuGrid", (9, 9), set(range(1, 10)))

        for row_idx in range(9):
            for col_idx in range(9):
                clue_value = self.clues[row_idx][col_idx]
                if clue_value != 0:
                    unary_constraint = myUnaryConstraint(variables_grid[row_idx][col_idx], clue_value,
                                                         lambda a, b: a == b)
                    constraint_list.append(unary_constraint)

        for row in variables_grid:
            my_satisfy(myAllDifferent(row))

        for col_idx in range(9):
            my_satisfy(myAllDifferent([variables_grid[row_idx][col_idx] for row_idx in range(9)]))

        for block_row_idx in range(0, 9, 3):
            for block_col_idx in range(0, 9, 3):
                block_cells = [variables_grid[row_idx][col_idx] for row_idx in range(block_row_idx, block_row_idx + 3)
                               for col_idx in range(block_col_idx, block_col_idx + 3)]
                my_satisfy(myAllDifferent(block_cells))

        refresher_instance = Refresher(variables_grid, puzzle, real_time, refresh_callback, stop_condition)

        solution_found = my_solve(use_unary_check, use_arc_consistency, use_mrv, use_lcv, refresher_instance)

        if solution_found:
            puzzle.answer_board = [[variables_grid[row_idx][col_idx].value for col_idx in range(9)] for row_idx in
                                   range(9)]

        return solution_found
    def solve(self, 
              algorithm: str, 
              do_unary_check: bool, 
              do_arc_consistency: bool, 
              do_mrv: bool,
              do_lcv: bool,
              real_time: bool, 
              board: Board,
              refresh: Callable[[],bool],
              get_stop_event: Callable[[], bool]):
        """Solves the Sudoku puzzle using the selected CSP algorithm."""
        if algorithm == 'p':
            return self.pycsp_solve(board)
        else:
            return self.mycsp_solve(board, do_unary_check, 
                                    do_arc_consistency, 
                                    do_mrv, 
                                    do_lcv, 
                                    real_time, 
                                    refresh,
                                    get_stop_event)
        