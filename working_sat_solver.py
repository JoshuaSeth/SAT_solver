import random
import datetime
import pandas as pd
from Sudoku_rstring_reader import *
import numpy as np

def print_assignments_as_sudoku(assignments):
    #Only keep positives
    assignments = [item for item in assignments if item >= 0]
    #Sort from low to high
    assignments = sorted(assignments)
    #print them left to right
    grid = []
    for i in range(9):
        grid.append([0]*9)
    for item in assignments:
        index_x = int(str(item)[0])-1
        index_y=int(str(item)[1])-1
        value = int(str(item)[2])
        grid[index_x][index_y]= value
    df = pd.DataFrame.from_records(grid)
    print("\nFilled in sudoku")
    print(df.to_string(index=False, header=False))

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
        if -var in clause:
            new_var = [i for i in clause if i!= -var]
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

def get_and_remove_pure_literal(formula):
    counter = get_counter(formula)
    assignment = []
    pures = []
    for literal, _ in counter.items():
        if -literal not in counter:
            pures.append(literal)
    for pure in pures:
        formula = remove_var_from_cnf(formula, pure)
    assignment += pures
    return formula, assignment

def get_and_remove_unit_clauses(formula):
    assignment = []
    unit_clauses = [c for c in formula if len(c) == 1]
    while unit_clauses:
        unit = unit_clauses[0]
        formula = remove_var_from_cnf(formula, unit[0])
        assignment += [unit[0]]
        if formula == -1:
            return -1, []
        if not formula:
            return formula, assignment
        unit_clauses = [c for c in formula if len(c) == 1]
    return formula, assignment

def get_jw_counted_terms(cnf_formula): # 2 sided jw heuristic
    count_literals = {}
    for clauses in cnf_formula:
        for terms in clauses:
            abs(terms)
            if terms in count_literals:
                count_literals[terms] = 2 ** -len(clauses)
            else:
                count_literals[terms] = 2 ** -len(clauses)
    return count_literals

def jw_var_picker(cnf_formula): 
    counts = get_jw_counted_terms(cnf_formula)
    return max(counts, key = counts.get)

def get_rand_var(cnf_formula):
    """Internal, use get_varaible_by_heuristic instead. Returns random variable
    without regard for heuristic or if it was already checked for"""
    # Return a random variable from random clause
    clause = []
    while len(clause) == 0:
        clause = cnf_formula[random.randint(0, len(cnf_formula) - 1)]
    variable = clause[random.randint(0, len(clause) - 1)]
    return variable

def backtracking(formula, assignment, heuristic):
    formula, pure_assignment = get_and_remove_pure_literal(formula)
    formula, unit_assignment = get_and_remove_unit_clauses(formula)
    assignment = assignment + unit_assignment + pure_assignment
    if formula == -1:
        return []
    if not formula:
        return assignment

    variable = heuristic(formula)
    solution = backtracking(remove_var_from_cnf(formula, variable), assignment + [variable], heuristic)
    if not solution:
        solution = backtracking(remove_var_from_cnf(formula, -variable), assignment + [-variable], heuristic)
    return solution

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
        cnf_formula = read_cnf_from_dimac('sudoku-rules.txt') # this seems like an excessively slow step, to read from the file over and over  
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


if __name__ == '__main__':
    main()