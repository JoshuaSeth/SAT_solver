import random
import datetime
import sys
import os
#from SAT_helper_functions import print_assignments_as_sudoku
#import pandas as pd
#from Sudoku_rstring_reader import *
#import numpy as np
#from tqdm import tqdm

def read_cnf_from_dimac(filename):
    cnf_formula = []
    text = open(filename, 'r').read()
    lines = text.split("0")
    # Go through each line in file
    for line in lines:
        line =line.replace("\n", "").strip()
        # In our case skip lines starting with both p and c if I understand the file structure correctly
        if not line.startswith("p") and not line.startswith("c") and len(line)>2:
            # gathering clauses as integers for every line in the document, also removes '0's
            clause = [int(x) for x in line.split()]
            cnf_formula.append(clause)
    return cnf_formula

def remove_var_from_cnf(cnf_formula, var):
    new_formula = []
    for clauses in cnf_formula:
        if var in clauses:
            continue
        if -var in clauses:
            new_var = [i for i in clauses if i != -var]
            if not new_var:
                return -1
            new_formula.append(new_var)
        else:
            new_formula.append(clauses)
    return new_formula

def get_tautologies(cnf_formula): # unused, expensive and no return of investment
    tautologies = []
    for clause in cnf_formula:
        for term in clause:
            if term * -1 in clause:
                tautologies.append(clause) 
    return tautologies 

def count_all_literals(cnf_formula): # counting all the literals, used for the pure literal removal
    literal_count = {}
    for clauses in cnf_formula:
        for literal in clauses:
            if literal in literal_count:
                literal_count[literal] += 1
            else:
                literal_count[literal] = 1
    return literal_count 

def get_and_remove_pure_literal(cnf_formula): # removing all pure literals, 
    literal_count = count_all_literals(cnf_formula)
    assignments = []
    pure_literals = []
    for literal, _ in literal_count.items():
        if -literal not in literal_count:
            pure_literals.append(literal)
    for pure in pure_literals:
        cnf_formula = remove_var_from_cnf(cnf_formula, pure)
    assignments += pure_literals
    return cnf_formula, assignments

def get_and_remove_unit_clauses(cnf_formula):
    assignments = []
    unit_clauses = [clause for clause in cnf_formula if len(clause) == 1]
    while unit_clauses:
        # if len(unit_clauses) % 10 == 0:
        # print("unit clauses left", len(unit_clauses))
        unit_clause = unit_clauses[0]
        cnf_formula = remove_var_from_cnf(cnf_formula, unit_clause[0])
        assignments += [unit_clause[0]]
        if cnf_formula == -1:
            return -1, []
        if not cnf_formula:
            return cnf_formula, assignments
        unit_clauses = [clause for clause in cnf_formula if len(clause) == 1]
    return cnf_formula, assignments

def jw_var_picker(cnf_formula): # ONE sided jw heuristic
    count_literals = {}
    for clauses in cnf_formula: 
        for terms in clauses:
            if terms in count_literals:
                count_literals[terms] += 2 ** -len(clauses)
            else:
                count_literals[terms] = 2 ** -len(clauses)
    return max(count_literals, key = count_literals.get)

def sudoku_heuristic(cnf_formula):
    longest = None
    length = 0
    for clause in cnf_formula:
        if clause[0]>0:
            if len(clause) > length:
                if all(i >= 0 for i in clause):
                    length = len(clause)
                    longest = clause
    return longest[random.randint(0, len(longest)-1)]

def pick_literal_in_shortest_all_positive_clause(cnf_formula):
    clause_length = 9999999999 # initial length to compare to
    winner = 0
    for clauses in cnf_formula:
        negative_count = len(list(filter(lambda x: (x<0), clauses))) # iterate over all clauses and count how many negative literals are in them
        if negative_count == False and len(clauses) < clause_length: # if no negative literals and the length of the clause is less compared to the previous one
            winner = clauses[0]
            clause_length = len(clauses) # keep updating clause length to always select from shortest clause
    if not winner:
        winner = cnf_formula[0][0] # if no clauses with all positive literals, return first element of the formula
        return winner
    return winner

def get_rand_var_abs(cnf_formula): # Return a random variable from random clause
    clause = cnf_formula[random.randint(0, len(cnf_formula) - 1)]
    variable = clause[random.randint(0, len(clause) - 1)]
    return abs(variable)

def get_rand_var(cnf_formula):
    """Internal, use get_varaible_by_heuristic instead. Returns random variable
    without regard for heuristic or if it was already checked for"""
    # Return a random variable from random clause
    clause = cnf_formula[random.randint(0, len(cnf_formula) - 1)]
    variable = clause[random.randint(0, len(clause) - 1)]
    return variable

def MOMS_heuristic(current_CNF): 
    '''Checks current state of CNF and chooses a next variable to set based on 
    the number of occurences of each variable in the smallest leftover clauses'''
    # determine total length of CNF to set as a largest possible clause length 
    length_smallest = 0 # variable name may be confusing, but is necessary to avoid extra work later on
    for clause in current_CNF:
        length_smallest += len(clause)
    
    # check the length of the smallest clause 
    for clause in current_CNF: 
        if len(clause) < length_smallest:
            length_smallest = len(clause)
    
    # keep track of occurences of variables in a dictionary 
    dict_abs = {}
    dict_both = {}

    # count occurences of every variable in the smallest clauses 
    for clause in current_CNF:
        if len(clause) == length_smallest:
            for variable in clause:
                
                # count occurences for instances
                if not variable in dict_both:
                    dict_both[variable] = 1
                else:
                    dict_both[variable] += 1
                
                # count occurences for variable in total 
                if not abs(variable) in dict_abs:
                    dict_abs[abs(variable)] = 1
                else:
                    dict_abs[abs(variable)] += 1 
    
    '''Tune this parameter'''
    k=1 

    for item in dict_abs.keys():
        if item not in dict_both:
            dict_both[item] = 0 
        if -item not in dict_both:
            dict_both[-item] = 0

        dict_abs[item] = dict_abs[item] * 2 ** k + dict_both[item] * dict_both[-item]
    
    # get value with highest score 
    winning_variable = max(dict_abs, key=dict_abs.get) 
    '''Note that we take the FIRST encountered element with the highest score here, there can be more variables with the same number of counts. Maybe we want to add some code that randomly determines which variable out of the ones with the highest number of counts we take.'''

    return winning_variable 

def has_empty_clause(cnf_formula, log_level):
    """Returns whether the cnf has some empty clause)"""
    for clause in cnf_formula:
        if len(clause) is 0:
            if log_level > 2:
                print("Found an empty clause: {0}.".format(clause))
            return True
    return False

def backtracking(cnf_formula, assignment, heuristic, num_decisions, num_backtracks):
    cnf_formula, pures = get_and_remove_pure_literal(cnf_formula)
    cnf_formula, unit_clauses = get_and_remove_unit_clauses(cnf_formula)

    assignment = assignment + unit_clauses + pures
    if cnf_formula == -1:
        return [], num_decisions, num_backtracks
    if not cnf_formula:
        return assignment, num_decisions, num_backtracks
    if has_empty_clause(cnf_formula, log_level=-1):
        return [], num_decisions, num_backtracks
    selected_variable = heuristic(cnf_formula) # selecting a variable to branch on based on the heuristic specified
    num_decisions +=1 # tracking number of decisions made during the search
    all_assignments, num_decisions, num_backtracks = backtracking(remove_var_from_cnf(cnf_formula, selected_variable), assignment + [selected_variable], heuristic, num_decisions, num_backtracks)
    if not all_assignments:
        num_backtracks += 1 # tracking number of backtracks made during the search
        all_assignments, num_decisions, num_backtracks = backtracking(remove_var_from_cnf(cnf_formula, -selected_variable), assignment + [-selected_variable], heuristic, num_decisions, num_backtracks)
    return all_assignments, num_decisions, num_backtracks

def assignments_to_DIMAC(solution):
    solution_file = open('Solution_file_DIMAC.txt', 'w')
    for assignment in solution:
        solution_file.writelines(str(assignment) + " " + "0" + "\n" )

def main(): # perhaps we can do something here with the input/output file structure?
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    
    heuristic_name = sys.argv[0]
    print("HEURISTIC: "+heuristic_name)
    if heuristic_name == "jw":
        heuristic = jw_var_picker
    if heuristic_name == "moms":
        heuristic = MOMS_heuristic
    if heuristic_name == 'shortest_pos':
        heuristic = pick_literal_in_shortest_all_positive_clause
    if heuristic_name == 'sdk':
        heuristic = sudoku_heuristic
    if heuristic_name == 'random_abs':
        heuristic = get_rand_var_abs
    if heuristic_name == 'random':
        heuristic = get_rand_var
    else:
        print("No heuristic name or invalid heuristic name given. Falling back to JW. Give a heuristic argument as second argument to calling the scipt. Options: \n - jw\n - moms \n - shortest_pos \n - sdk \n - random_abs \n- random")
        heuristic = jw_var_picker

    cnf_formula = read_cnf_from_dimac(cur_dir+ '/sudoku-rules.txt')
    test_sudoku = read_cnf_from_dimac(cur_dir+  '/sudoku-example.txt')
    cnf_formula.extend(test_sudoku)


    #Actual running of the thing
    all_assignments, num_decisions, num_backtracks = backtracking(cnf_formula, [], heuristic, 0, 0)
    if all_assignments:
        print('SAT' + "\n" + "Number of backtrack steps taken: " + str(num_backtracks))
        assignments_to_DIMAC(all_assignments) # printing the solution assignments to a txt file in dimacs format
    else:
        print('UNSAT')
        solution_file = open('Solution_file_DIMAC.txt', 'w')
        solution_file.write(' ') # check if this works

def sat_experiment_connector(cnf_formula, heuristic_name):
    '''Quick connector function to easily connect the SAT solver with the experiment.py
    Basically the same as main() but now with the formula and heuristic as parameters and with return vars'''
    num_decisions = 0
    num_backtracks = 0
    if heuristic_name == "jw":
        heuristic = jw_var_picker
    if heuristic_name == "moms":
        heuristic = MOMS_heuristic
    if heuristic_name == 'shortest_pos':
        heuristic = pick_literal_in_shortest_all_positive_clause
    if heuristic_name == 'sdk':
        heuristic = sudoku_heuristic
    if heuristic_name == 'random_abs':
        heuristic = get_rand_var_abs
    if heuristic_name == 'random':
        heuristic = get_rand_var
    start_time = datetime.datetime.now()
    
    solution, num_decisions, num_backtracks = backtracking(cnf_formula, [], heuristic, num_decisions, num_backtracks)
    if solution:
        end_time = datetime.datetime.now()
        return "sat", end_time - start_time, num_decisions, num_backtracks
    else:
        print('Given formula has no satisfiable configuration')
        end_time = datetime.datetime.now()
        return "unsat", end_time - start_time, num_decisions, num_backtracks
    # except Exception as e:
    #     print("SUDOKU LIEP VAST< WSS RECURSION ERROR. \n\n ERROR:", e)
    #     end_time = datetime.datetime.now()
    #     return "recursion exceeded", end_time - start_time, num_decisions, num_backtracks
    
if __name__ == '__main__':
    main()
