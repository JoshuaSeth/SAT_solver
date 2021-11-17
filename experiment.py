import time
import sys
from SAT_solver import SAT_solve
from SAT_helper_functions import *

# Experiment variables:

num_test_sudokus = 10 # How many sudoku points we collect per test category (i.e. run 10 sudoku's though the sat solver for 4x4, heuristic 2)

sudoku_rules_4x4 = read_cnf_from_dimac("")