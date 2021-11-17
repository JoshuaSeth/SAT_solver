import time
import sys
from SAT_solver import SAT_solve
from SAT_helper_functions import *
from scipy import stats

# Experiment variables:
experiment_log_level = 0 #Can be anything depending on what you want
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

#Save the result of the 6 runs (2 heuristics x 3 sudoku sizes (x max_sudokus_tested datapoint))
#So the results will be in the form [[x datapoints], [x datapoints], [x datapoints], [x datapoints], etc.]
results = {}

# Run though sudoku collections along with their riles
for sudoku_collection, rules in sudokus_and_rules_collection:
    #Test against the 2 heuristic
    for heuristic in ["cdcvi", "jeroslaw-wang"]:
        #Track the resulting time
        times_for_sudokus = []
        index=0
        #Go through sudoku in sudko collection
        for sudoku in sudoku_collection:
            sudoku_and_rules_as_cnf = sudoku.extend(rules)
            #Attempt to SAT solve
            sat, time_spent =  SAT_solve(sudoku_and_rules_as_cnf, log_level=experiment_log_level, heuristic=heuristic)
            #Save to sudoku times
            times_for_sudokus.append(time_spent)
            index+=1
            #Stop when we have done as many tests as we wanted for the category we are in
            if index == max_sudokus_tested:
                break
    #Save the name of the collection (i.e. sudokus_16x16_cnf) as a string. ONLY WORKS python3.8+
    python_var_name_as_string = f'{sudoku_collection=}'.split('=')[0]
    #Save to results under appropriate name so we cna find back alter
    results[python_var_name_as_string + "_" + heuristic] = times_for_sudokus

#Since we now have a collection with results we might as well do the t-tests immediately
# Note that you can compare 6 x 5 values (compare each result against the others)
for key, result_times in results:
    #Compare against all other results
    for compare_key, compare_against_result_times in results:
        if not compare_against_result_times is result_times:
            #Does a UNPAIRED t-test returns t and p values
            t_test_result = stats.ttest_ind(result_times, compare_against_result_times, equal_var=False)
            #Use the KEY names to nicely format and now what we actually tested
            print("Compared {0} and {1}. T-test result is {2}".format(key, compare_key, t_test_result))