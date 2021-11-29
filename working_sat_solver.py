import random
import datetime
import pandas as pd
from Sudoku_rstring_reader import *
import numpy as np
from tqdm import tqdm
from SAT_helper_functions import has_empty_clause, print_assignments_as_sudoku


def read_cnf_from_dimac(filename):
    cnf_formula = []
    # Go through each line in file
    for line in open(filename):
        # In our case skip lines starting with both p and c if I understand the file structure correctly
        if not line.startswith("p") and not line.startswith("c"):
            # gathering clauses as integers for every line in the document, also removes '0's
            clause = [int(x) for x in line[:-2].split()]
            cnf_formula.append(clause)
    return cnf_formula

def remove_var_from_cnf(cnf_formula, var):
    new_formula = []
    for clause in cnf_formula:
        if var in clause:
            continue
        if get_negated(var) in clause:
            new_var = [i for i in clause if i!= get_negated(var)]
            if not new_var:
                return -1
            new_formula.append(new_var)
        else:
            new_formula.append(clause)
    return new_formula

def get_tautologies(cnf_formula): # niet nodig 
    tautologies = []
    for clause in cnf_formula:
        for term in clause:
            if term * -1 in clause:
                tautologies.append(clause) 
    return tautologies 

def get_counter(formula):
    counter = {}
    for clause in formula:
        for literal in clause:
            if literal in counter:
                counter[literal] += 1
            else:
                counter[literal] = 1
    return counter

def get_negated(variable):
    if variable[0]=="-":
        # print(variable, variable[1:])
        return variable[1:]
    else:
        # print(variable, "-" + variable)
        return "-" + variable

def get_and_remove_pure_literal(formula):
    counter = get_counter(formula)
    assignment = []
    pures = []
    for literal, _ in counter.items():
        if get_negated(literal) not in counter:
            pures.append(literal)
    for pure in pures:
        formula = remove_var_from_cnf(formula, pure)
    assignment += pures
    return formula, assignment

def get_and_remove_unit_clauses(formula):
    assignment = []
    unit_clauses = [c for c in formula if len(c) == 1]
    while unit_clauses:
        # if len(unit_clauses) % 10 == 0:
        # print("unit clauses left", len(unit_clauses))
        unit = unit_clauses[0]
        formula = remove_var_from_cnf(formula, unit[0])
        assignment += [unit[0]]
        if formula == -1:
            return -1, []
        if not formula:
            return formula, assignment
        unit_clauses = [c for c in formula if len(c) == 1]
        
    return formula, assignment

def get_jw_counted_terms(cnf_formula): # ONE sided jw heuristic
    count_literals = {}
    for clauses in cnf_formula: 
        for terms in clauses:
            if terms in count_literals:
                count_literals[terms] += 2 ** -len(clauses)
            else:
                count_literals[terms] = 2 ** -len(clauses)
    return count_literals

def sudoku_heuristic(cnf_formula):
    longest = None
    length = 0
    for clause in cnf_formula:
        if not clause[0][0]=="-":
            if len(clause) > length:
                if all(i[0] != "-" for i in clause):
                    length = len(clause)
                    longest = clause
    return longest[random.randint(0, len(longest)-1)]

def jw_var_picker(cnf_formula): 
    counts = get_jw_counted_terms(cnf_formula)
    return max(counts, key = counts.get)

def pick_literal_in_shortest_all_positive_clause(cnf_formula):
    clause_length = 9999999999 # initial length to compare to
    winner = 0
    for clauses in cnf_formula:
        negative_count = len(list(filter(lambda x: (x<0), clauses))) # iterate over all clauses and count how many negative literals are in them
        if negative_count == False and len(clauses) < clause_length:
            winner = clauses[0]
            clause_length = len(clauses) # keep updating clause length to always select from shortest clause
    if not winner:
        winner = cnf_formula[0][0] # if no clauses with all positive literals, return first element of the formula
        return winner
    return winner

def get_rand_var_abs(cnf_formula):
    """Internal, use get_varaible_by_heuristic instead. Returns random variable
    without regard for heuristic or if it was already checked for"""
    # Return a random variable from random clause
    clause = cnf_formula[random.randint(0, len(cnf_formula) - 1)]
    variable = clause[random.randint(0, len(clause) - 1)]
    #Return abs
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

def backtracking(formula, assignment, heuristic, num_decisions, num_backtracks):
    # formula, pure_assignment = get_and_remove_pure_literal(formula)
    formula, unit_assignment = get_and_remove_unit_clauses(formula)

    assignment = assignment + unit_assignment
    print_assignments_as_sudoku(assignment, header="CURRENT RESULT", flush=True,hexadecimal=True)
    # print(assignment)
    if formula == -1:
        return [], num_decisions, num_backtracks
    if not formula:
        return assignment, num_decisions, num_backtracks
    if has_empty_clause(formula, log_level=-1):
        return [], num_decisions, num_backtracks

    variable = heuristic(formula)
    num_decisions +=1 

    
    solution, num_decisions, num_backtracks = backtracking(remove_var_from_cnf(formula, variable), assignment + [variable], heuristic, num_decisions, num_backtracks)
    if not solution:
        num_backtracks+=1
        solution, num_decisions, num_backtracks = backtracking(remove_var_from_cnf(formula, get_negated(variable)), assignment + [get_negated(variable)], heuristic, num_decisions, num_backtracks)
    
    return solution, num_decisions, num_backtracks

def main():
    starttime_all_sudokus = datetime.datetime.now()
    heuristic = get_rand_var

    #clauses = read_cnf_from_dimac('sudoku-rules.txt')
    #example_sudoku = read_cnf_from_dimac('sudoku-example.txt')
    #clauses.extend(example_sudoku)
    #n_vars = 999

    individual_solve_times = []
    for i in range(1,20):
        starttime_per_sudoku = datetime.datetime.now()
        # this seems like an excessively slow step, to read from the file over and over  
        cnf_formula = read_cnf_from_dimac('dimac_files/sudoku-rules.txt') # added the folder to resolve an error
        cnf_formula.extend(int_sudokus_lol[i])
        solution = backtracking(cnf_formula, [], heuristic)
        print('Satisfiable configuration found, printing solution as a sudoku')  
        print_assignments_as_sudoku(solution)  
        if solution:
            endtime_per_sudoku = datetime.datetime.now()
            time_per_sudoku = endtime_per_sudoku - starttime_per_sudoku
            individual_solve_times.append(time_per_sudoku)
        else:
            print('Given formula has no satisfiable configuration')
    print(np.mean(individual_solve_times))


    #if solution:
    #solution += [x for x in range(1, n_vars + 1) if x not in solution and -x not in solution]
    #    solution.sort(key=abs)
    #    solution = [pos for pos in solution if pos > 0 and pos > 110]
    #    no_delete = {'0'}
    #    solution = [no_zero for no_zero in solution if not no_delete & set(str(no_zero))]
    #    solution = solution 
    #    print(solution)
    #    print('SATISFIABLE')
    #    #print('v ' + ' '.join([str(x) for x in solution]) + ' 0')
    #else:
    #    print('s UNSATISFIABLE')

    endtime_all_sudokus = datetime.datetime.now()
    time_to_solve_all_input_sudokus = endtime_all_sudokus - starttime_all_sudokus
    print(time_to_solve_all_input_sudokus)

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
    

# if __name__ == '__main__':
#     main()
