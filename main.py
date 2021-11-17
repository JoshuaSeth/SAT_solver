"""main.py: The main file from which we run our experiments and tests. For example here we import a dimacs and run it through the SAT solver we con import or apply some helper functions on it."""
import sys
from SAT_solver import SAT_solve
from SAT_helper_functions import *
import glob
import datetime

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

voorbeeld = read_cnf_from_dimac(test_problem_4)

start_time = datetime.datetime.now()  # record time before program is executed
# Try some sat solving
sat, time = SAT_solve(cnf_formula, log_level=1)
print(sat)

# Reading multiple sudoku.txt files. Assumes we name our files 'sudoku_*.txt' where * = a number for each individual sudoku.
# Also assumes 'sudoku_*.txt' are located in a folder named 'cnf_sudokus'
"""
sudoku_path = 'cnf_sudokus'
for path in glob.iglob(sudoku_path + 'sudoku_*.txt'):
    SAT_solve(cnf_formula, log_level = 0)
"""
delta_time = (
    datetime.datetime.now() - start_time
)  # check and save time after the code is ran minus time before the code is ran.
# delta_time is the time it took to complete
print(delta_time)
