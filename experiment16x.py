from Sudoku_rstring_reader import *
from SAT_helper_functions import *
from working_sat_solver import sat_experiment_connector
import pickle
from scipy import stats
import copy
from tqdm import tqdm
from distribution_test import get_best_distribution 
import warnings
warnings.filterwarnings("ignore")

import sys
sys.setrecursionlimit(10**5) 

# Experiment variables:
experiment_log_level = 0 #Can be anything depending on what you want
max_sudokus_tested = 10 # How many sudoku points we collect per test category (i.e. run 10 sudoku's though the sat solver for 4x4, heuristic 2)

#These are the sudoku rules in CNF form (list of lists)
#We can load the rulesets directly since they are coded as dimac instead of ... point files
sudoku_rules_4x4_cnf = read_cnf_from_dimac("sudoku_resources/sudoku-rules-4x4.txt") 
sudoku_rules_9x9_cnf = read_cnf_from_dimac("sudoku_resources/sudoku-rules-9x9.txt") 
sudoku_rules_16x16_cnf = read_cnf_from_dimac("sudoku_resources/sudoku-rules-16x16.txt")

sudoku_rules_16x16_cnf= rules_to_hexadecimal(sudoku_rules_16x16_cnf)

# print(sudoku_rules_16x16_cnf)

#Load the sudokus themselves (will be more than 10 so we run max of range 10)
# sudokus_4x4_cnf = get_sudoku_from_dots("sudoku_resources/4x4.txt", 4)
# sudokus_9x9_cnf = get_sudoku_from_dots("sudoku_resources/9x9.txt", 9)
sudokus_16x16_cnf = get_sudoku_from_dots("sudoku_resources/16x16.txt", 9, as_string=True)

test = [[3785]]
res = rules_to_hexadecimal(test)
print(test, res)

# Collect all sudokus and rules in one big list so we can iterate over it in 1 experiment instead of repeating code
sudokus_and_rules_collection =[(sudokus_16x16_cnf, sudoku_rules_16x16_cnf)]
# ,, 
#Save the result of the 6 runs (2 heuristics x 3 sudoku sizes (x max_sudokus_tested datapoint))
#So the results will be in the form [[x datapoints], [x datapoints], [x datapoints], [x datapoints], etc.]
results = {}

#RUNNING EXPERIMENTS
# Run though sudoku collections along with their riles
ind =0

for sudoku_collection, rules in sudokus_and_rules_collection:
    #Test against the 2 heuristic
    for heuristic in [ "sdk","shortest_pos","moms","random","random_abs", "jw"]:
        
        #Save the name of the collection (i.e. sudokus_16x16_cnf) as a string. 
        python_var_name_as_string = ["16x16"][ind]
        print("Experimenting heuristic: " + heuristic + python_var_name_as_string)
        #Track the resulting time
        times = []
        decisions = []
        backtracks = []
        index=0
        #Go through sudoku in sudko collection
        for i in tqdm(range(max_sudokus_tested)):
            sudoku = sudoku_collection[i] #read_cnf_from_dimac("easy_sudoku_dimac.txt")
            # print(sudoku)
            # sudoku = hexadecimal_to_9_padded(sudoku, 9)
            #Remove 30% random clauses
            # for i in range (180):
            #     sudoku.pop(random.randint(0, len(sudoku)-1))
            print(sudoku)
            print_assignments_as_sudoku(flatten(sudoku), hexadecimal=True)


            sudoku_and_rules_as_cnf = []
            sudoku_and_rules_as_cnf.extend(sudoku)
            sudoku_and_rules_as_cnf.extend(copy.deepcopy(rules))
            #Attempt to SAT solve
            sat, time_spent, num_decisions, num_backtracks =  sat_experiment_connector(sudoku_and_rules_as_cnf, heuristic_name=heuristic)
            #Save to sudoku times
            times.append(time_spent.total_seconds() * 1000)
            decisions.append(num_backtracks)
            backtracks.append(num_decisions)

            index+=1
            #Stop when we have done as many tests as we wanted for the category we are in
            if index == max_sudokus_tested:
                break
        
        print("\n"+python_var_name_as_string + "_" + heuristic)
        try:
            print(get_best_distribution(times))
            print(get_best_distribution(decisions))
            print(get_best_distribution(backtracks))

            print("\n")
        except Exception as e: print("no distrubution", times, decisions, backtracks)

        results[python_var_name_as_string+"_" + heuristic+"_times"] = times
        results[python_var_name_as_string+"_" + heuristic+"_decisions"] = decisions
        results[python_var_name_as_string+"_" + heuristic+"_backtracks"] = backtracks
        with open("new_experiment_results/"+python_var_name_as_string + "_" + heuristic+ "_" + "times.txt", "wb") as fp:   #Pickling
            pickle.dump(times, fp)
        with open("new_experiment_results/"+python_var_name_as_string + "_" + heuristic+ "_" + "decisions.txt", "wb") as fp:   #Pickling
            pickle.dump(decisions, fp)
        with open("new_experiment_results/"+python_var_name_as_string + "_" + heuristic+ "_" + "backtracks.txt", "wb") as fp:   #Pickling
            pickle.dump(backtracks, fp)
    ind+=1

print(results)

# #T-TESTS
# #Since we now have a collection with results we might as well do the t-tests immediately
# # Note that you can compare 6 x 5 values (compare each result against the others)
# for key, result_times in results:
#     #Compare against all other results
#     for compare_key, compare_against_result_times in results:
#         if not compare_against_result_times is result_times:
#             #Does a UNPAIRED t-test returns t and p values
#             t_test_result = stats.ttest_ind(result_times, compare_against_result_times, equal_var=False)
#             #Use the KEY names to nicely format and now what we actually tested
#             print("Compared {0} and {1}. T-test result is {2}".format(key, compare_key, t_test_result))
#             print("Standard deviations", stats.std(result_times), stats.std(compare_against_result_times))