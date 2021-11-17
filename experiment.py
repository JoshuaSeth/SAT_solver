import time
import sys
from SAT_solver import SAT_solve
from SAT_helper_functions import *

# Experiment variables:

max_sudokus_tested = 10 # How many sudoku points we collect per test category (i.e. run 10 sudoku's though the sat solver for 4x4, heuristic 2)

#These are the sudoku rules in CNF form (list of lists)
#We can load the rulesets directly since they are coded as dimac instead of ... point files
sudoku_rules_4x4_cnf = read_cnf_from_dimac("sudoku_resources/sudoku-rules-4x4.txts") 
sudoku_rules_9x9_cnf = read_cnf_from_dimac("sudoku_resources/sudoku-rules-9x9.txts") 
sudoku_rules_16x16_cnf = read_cnf_from_dimac("sudoku_resources/sudoku-rules-16x16.txts")

#Load the sudokus themselves (will be more than 10 so we run max of range 10)
sudokus_4x4_cnf = demis_future_function("sudoku_resources/4x4.txt")
sudokus_9x9_cnf = demis_future_function("sudoku_resources/9x9.txt")
sudokus_16x16_cnf = demis_future_function("sudoku_resources/16x16.txt")

# Collect all sudokus and rules in one big list so we can iterate over it in 1 experiment instead of repeating code
sudokus_and_rules_collection =[(sudokus_4x4_cnf, sudoku_rules_4x4_cnf), (sudokus_9x9_cnf, sudoku_rules_9x9_cnf), (sudokus_16x16_cnf, sudoku_rules_16x16_cnf)]

# Run though sudoku collections along with their riles
for sudoku_collection, rules in sudokus_and_rules_collection:
    index=0
    #Go through sudoku in sudko collection
    for sudoku in sudoku_collection:
        sudoku_and_rules_as_cnf = sudoku.extend(rules)
        sat, time_spent =  SAT_solve(sudoku_and_rules_as_cnf)
        index+=1
        #Stop when we have done as many tests as we wanted for the category we are in
        if index == max_sudokus_tested:
            break