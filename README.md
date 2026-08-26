# AI-prj2 — Sudoku as a Constraint Satisfaction Problem

Solving Sudoku puzzles by modeling them as Constraint Satisfaction Problems (CSPs), first using the `pycsp3` library and then via a custom-built CSP library (`mycsp`) implementing backtracking search with heuristics and arc-consistency — coursework for *Foundations and Applications of Artificial Intelligence*, Amirkabir University of Technology, Spring 2026.

## Overview

A Sudoku board is modeled as a CSP triple (X, D, C): each cell is a variable with domain {1..9}, constrained by the given clues (unary constraints) and the row/column/box `AllDifferent` rules (binary constraints after decomposition). The project has two parts:

1. **`pycsp3`**: Learning and using an existing open-source Python CSP library (which compiles a model to an XCSP3 instance and dispatches it to a solver such as ACE or Choco) to define and solve the Sudoku CSP.
2. **`mycsp`**: Implementing a small, from-scratch CSP library supporting backtracking search, node/arc consistency, and variable/value-ordering heuristics, then using it to solve the same Sudoku puzzles.

A graphical interface visualizes the live solving process, showing given clues, guessed values, final answers, and remaining domains for each cell.

## Features

- **Node consistency**: Removes domain values that violate a variable's own unary (clue) constraints.
- **Backtracking search**: Standard `Backtrack(csp, assignment)` recursive search with pluggable variable-selection and value-ordering strategies.
- **Static ordering heuristics**: Baseline "in-order" variable selection and "in-order" value ordering.
- **Arc consistency (AC-3)**: Propagates binary constraints to prune inconsistent domain values early, detecting unsolvable boards faster and shrinking the search tree.
- **Minimum Remaining Values (MRV)**: Selects the next variable with the smallest remaining domain to reduce branching factor.
- **Least Constraining Value (LCV)**: Orders candidate values by how few options they eliminate for neighboring variables, trying the least-restrictive value first.
- **Live visualization**: A `Refresher` object that pushes assignment/domain updates to the UI in real time (toggleable), alongside buttons to enable/disable each heuristic (Unary Checker, Arc Consistency, MRV, LCV) for direct performance comparison.

## Project Structure

| Path | Description |
|---|---|
| `main.py` | Graphical interface (no changes needed) |
| `sudoku.py` | `Layout` class (reads puzzle clues); `solve_pycsp()` and `solve_mycsp()` entry points |
| `board.py` | `Board` class holding the empty/layout/guess/answer boards and remaining domains |
| `refresher.py` | `Refresher` class for live UI updates during solving |
| `exceptions.py` | Custom exceptions |
| `example.py` | Standalone `pycsp3` usage example (N-Queens) |
| `myCSP/` | Custom CSP library: variables, constraints, and the `backtrack`, `consistency_node`, `consistency_arc`, MRV, and LCV implementations |
| `layouts/` | Sudoku puzzles in `.sudoku` format, at varying difficulty (e.g. Medium, Evil, Solution Without) |

## Setup & Running

Requires Python 3.10+ (3.11 recommended) and Java 11+ (required by the `pycsp3` solvers ACE/Choco).

```bash
pip install -r requirements.txt
python main.py
```

If using a virtual environment (venv/conda) causes issues with `pycsp3`, install and run with a specific Python version explicitly:

```bash
# macOS/Linux
python3.11 -m pip install pycsp3
python3.11 main.py

# Windows
py -3.11 -m pip install pycsp3
py -3.11 main.py
```

From the UI: load a puzzle, choose the solver (`pycsp` or `mycsp`) from the dropdown, toggle heuristics (Unary Checker, Arc Consistency, MRV, LCV) and real-time visualization, then press **Solve**.

## Acknowledgements

Coursework project for the AI course at Amirkabir University of Technology, built around the open-source [PyCSP3](https://pycsp.org/) library.
