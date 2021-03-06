"""main.py: The main file from which we run our experiments and tests. For example here we import a dimacs and run it through the SAT solver we con import or apply some helper functions on it."""

from CDCL_solver import CDCL_Solver
from SAT_helper_functions import *

# opening files any of these objects can be chosen to run the sat solver on
# Satisfiable assignment of variables satifies all these rules
sudoku_rules_path = "dimac_files/sudoku-rules.txt"
# Example sudoku setup to test with
sudoku_example_path = "dimac_files/sudoku-example.txt"
# The full collection of dimac sudoku setups
sudoku_collection_path = "dimac_files/sudokus/"
# Test problem for debugging
test_problem = "dimac_files/test_problem.txt"
test_problem_2 = "dimac_files/test_problem_2.txt"
test_problem_3 = "dimac_files/test_problem_3.txt"
test_problem_4 = "dimac_files/test_problem_4.txt"

sudoku_rules_dimac = open(sudoku_rules_path, "r")
sudoku_example = open(sudoku_example_path, "r")


# Load sudoku rules and a sudoku
cnf_formula = read_cnf_from_dimac(sudoku_rules_path)
example_sudoku_clauses = read_cnf_from_dimac(sudoku_example_path)

# Merge the sudoku clauses with the game rules
cnf_formula.extend(example_sudoku_clauses)

voorbeeld = read_cnf_from_dimac(test_problem_2)

# Try some sat solving
solver = CDCL_Solver(log_level=4)
sat = solver.SAT_solve(voorbeeld)
print(sat)
