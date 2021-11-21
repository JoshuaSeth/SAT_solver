"""SAT_helper_functions.py: Provides all kind of cnf manipulation functions and functions for retrieving pure literals, unit clauses, consistency, etc. These functions are used by the SAT_solver class but can be used independently."""

import warnings
import numpy as np
import random
import math
import pandas as pd

def read_cnf_from_dimac(filename):
    """Reads dimacs form a filename to a cnf formula in the form of
    [[clause1], [clause2], [clause3], etc.].
    This representation might change in the future"""
    formula = []
    # Go through each line in file
    for line in open(filename):
        # In our case skip lines starting with both p and c if I understand the file structure correctly
        if not line.startswith("p") and not line.startswith("c"):
            # gathering clauses as integers for every line in the document, also removes '0's
            clause = [int(x) for x in line[:-2].split()]
            formula.append(clause)
    return formula


def get_clause_dictionary(cnf_formula):
    """Returns a dictionary where the variables are the keys and the
    clause indices containing these keys the values.
    This way all clauses containing a certain variable can be quickly found"""
    dictionary = {}
    clause_index = -1
    # Loop through all clauses in CNF
    for clause in cnf_formula:
        clause_index += 1
        # Loop through all terms in clause
        for variable in clause:
            # Remove - if present
            variable_name = abs(variable)
            # If term/variable is in dict add this clause index to it's references,
            if variable_name in dictionary:
                dictionary[variable_name].append(clause_index)
            # Else add it to the dict referring to this clause
            else:
                dictionary[variable_name] = [clause_index]
    return dictionary


def get_tautologies(cnf_formula):
    """Returns the tautologic clauses (i.e. [p ^ -p]) from the cnf"""
    # Collect tautologies to remove later so we don't modify a list we are looping
    # through. Might give concurrency issues
    tautologies = []
    # Loop through clauses and their terms
    for clause in cnf_formula:
        for term in clause:
            # Check if the negation of this term is also present
            # i.e. if term is 111 check if -111 also is present and vice versa
            if term * -1 in clause:
                tautologies.append(clause)
    return tautologies


def remove_clauses_from_cnf(cnf_formula, clauses_to_remove):
    """Removes the clauses from the cnf formula and returns the modified formula"""
    for clause in clauses_to_remove:
        cnf_formula.remove(clause)
    return cnf_formula


def get_unit_clauses(cnf_formula):
    """Get all the unit clauses [p] from the cnf formula. These can be set
    immediately to true or else the formula is unsat"""
    # collect unit clauses to return
    unit_clauses = []
    variables = []
    # Loop through clauses in the formula
    for clause in cnf_formula:
        # If there is only 1 term in the clause it is an unit clause
        if len(clause) is 1:
            unit_clauses.append(clause)
            variables.append(clause[0])
    return unit_clauses, variables


def flatten(list_of_lists):
    """Helper function to flatten a list of list to a 1-demnsional list of numbers.
    needed for optimization"""
    return [element for sublist in list_of_lists for element in sublist]


def get_pure_literal_clauses(cnf_formula):
    """Gets all pure literals (i.e. variables that occur solely positive or solely
    negative in the formula) and the clauses in which they appear"""
    # Collect all clause of which some literal occurs only pure
    pure_literal_clauses = []
    # Check which terms we already checked (via dict since much faster for 'in' than list)
    checked_terms = {}
    # We flatten the cnf (i.e. [[p or q] ^ [-q or r]] => [p, q, -q, r])
    # This decreases literal check-up times by about 30 times
    flattened_cnf = flatten(cnf_formula)
    for clause in cnf_formula:
        # for all terms in the clause
        for term in clause:
            # Check if we didn't check this term already in another cluase
            if not abs(term) in checked_terms:
                # check if we didn't do this clause already by the previous terms
                if not clause in pure_literal_clauses:
                    # Since we're here officially checing the term we set it to checked
                    checked_terms[abs(term)] = True
                    # If it occurs in negated form nowhere else it is literal
                    if not term * -1 in flattened_cnf:
                        pure_literal_clauses.append(clause)
    return pure_literal_clauses, checked_terms


def get_clauses_with_var(cnf_formula, variable):
    """Returns clauses containing variable
    Naive implementation of returning clauses containing a var.
    Basically an expensive list look-up."""
    clauses_with_var = []
    # Loop through clauses in cnf
    for clause in cnf_formula:
        # If the clause contains the variables in either positive or negative form
        if variable in clause or variable * -1 in clause:
            clauses_with_var.append(clause)
    return clauses_with_var


def get_rand_var(cnf_formula):
    """Internal, use get_varaible_by_heuristic instead. Returns random variable
    without regard for heuristic or if it was already checked for"""
    # Return a random variable from random clause
    clause = []
    while len(clause) == 0:
        warnings.warn(
            "Empty clause when retrieving random varaible. Will be found in the next consistency check."
        )
        clause = cnf_formula[random.randint(0, len(cnf_formula) - 1)]
    variable = clause[random.randint(0, len(clause) - 1)]
    return variable

def get_jw_counted_terms(cnf_formula): # 2 sided jw heuristic
    count_literals = {}
    for clauses in cnf_formula:
        for terms in clauses:
            abs(terms)
            if terms in count_literals:
                count_literals[terms] = 0.2 ** -len(clauses)
            else:
                count_literals[terms] = 0.2 ** -len(clauses)
    return count_literals

def jw_var_picker(cnf_formula): 
    counts = get_jw_counted_terms(cnf_formula)
    return max(counts, key = counts.get)

def get_variable_by_heuristic(cnf_formula, heuristic, current_variable_assignment):
    if heuristic is "random":
        # Try to selct a variable we did not check yet, send it if it was not in assignment
        # Otherwise retry
        while True:
            variable = get_rand_var(cnf_formula)
            if not variable in current_variable_assignment:
                return abs(variable)
    if heuristic is "jw_var_picker": #Of hoe je dat ook schrijft
        variable = jw_var_picker(cnf_formula)
        if not variable in current_variable_assignment:
            return abs(variable)
        return variable
    
    # If no heuristic was matched it was probably not implemented
    warnings.warn(
        "{0} was not implemented yet or an invalid heuristic. Falling back to random varaible selecion".format(
            heuristic
        )
    )
    while True:
        variable = get_rand_var(cnf_formula)
        if not variable in current_variable_assignment:
            return abs(variable)


def set_variable_assignment(cnf_formula, random_variable):
    """Sets a given variable to true in the formula.
    If given the negated version of the variable it sets the varible to false.
    This means: (1) removing the
    clauses where this variable was true (i.e. clause is satisfied), and (2) removing
    the variable form the vlauses where it was not satisfied (i.e. this variable
    cannot be true anymore in this clause).
    returns num removed clauses and num changed clauses"""
    # Keep track of numbers
    num_changed = 0
    num_removed = 0
    # Get all clauses with this variable
    clauses_with_var = get_clauses_with_var(cnf_formula, random_variable)
    clauses_to_remove = []
    for clause in clauses_with_var:
        # If the variable is true in this clause the clause is true and we remove it
        if random_variable in clause:
            clauses_to_remove.append(clause)
            num_removed += 1
        # Else if the variable was false in this clause we remove the var from the clause since this var cannot be satisfied anymore
        if random_variable * -1 in clause:
            clause.remove(random_variable * -1)
            num_changed += 1
    remove_clauses_from_cnf(cnf_formula, clauses_to_remove)
    return num_removed, num_changed


def is_consistent(unit_clauses):
    """Checks if there are no incosistencies (i.e. [c ^ -c]) in the formula.
    returns false at the first found incosistency. Requires unit clauses as input
    since only these can give incosistencies"""
    for clause in unit_clauses:
        # If the opposite of this term is also in these unit cluases
        if [clause[0] * -1] in unit_clauses:
            # then it is incosistent
            return False
    return True


def has_empty_clause(cnf_formula, log_level):
    """Returns whether the cnf has some empty clause)"""
    for clause in cnf_formula:
        if len(clause) is 0:
            if log_level > 2:
                print("Found an empty clause: {0}.".format(clause))
            return True
    return False

def print_assignments_as_sudoku(assignments, header="Finished Sudoku"):
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
    print("\n"+header)
    print(df.to_string(index=False, header=False))


def sudoku_to_DIMACS(sudoku):
    """Prints set of clauses given a sudoku as a string"""  # code needs to be cleaned up after it is finished
    count = 0

    for element in sudoku:
        count = count + 1

        if element != ".":
            row = math.ceil(count / 9)
            column = count - (row - 1) * 9
            # print('element:', element, 'count:', count, 'row:', row, 'column:', column)
            variable = str(row) + str(column) + str(element)
            print(variable, "0")  # needs to be saved to a file instead of being printed

    # output only contains clauses containing numbers for specific sudoku, no constraints
    # need to edit: what kind of input needs to be processed? how should output be presented?
    # following string can be used as a test sudoku:
    teststring = ".94...13..............76..2.8..1.....32.........2...6.....5.4.......8..7..63.4..8"


def get_num_vars(filename):
    num_vars = []
    for line in open(filename):
        if line.startswith(
            "p"
        ):  # gathering number of variables and number of clauses from line starting with 'p'
            num_vars = line.split()[2]
            num_vars = int(num_vars)  # transforming into integers
            return num_vars


def init_VSIDS(
    num_vars, cnf_formula
):  # making an initial dictionary of all the literals
    literal_count = {}
    for x in range(-num_vars, num_vars + 1):
        literal_count[x] = 0
    for clause in cnf_formula:
        for literal in clause:
            literal_count[literal] += 1
    return literal_count


def increase_VSIDS_counter(
    conflict, literal_count
):  # increasing the counter of the literals in the dictionary if they are present in a conflict
    for literal in conflict:
        literal_count[literal] += 1
    return literal_count


def decrement_VSIDS(
    num_vars, literal_count, decrement_step_size
):  # decrement_step_size is how fast the value is decreased
    # (in a range of 0-100, where 95 is a standard value)
    for x in range(-num_vars, num_vars + 1):
        literal_count[x] = (decrement_step_size * literal_count[x]) / 100
    return literal_count


def choose_var_VSIDS(
    literal_count, unit_clauses, num_vars
):  # choosing the literal with the highest value in the dictionary to branch on
    maximum = 0
    VSIDS_variable = 0
    for j in range(-num_vars, num_vars + 1):
        if (
            literal_count[j] >= maximum
            and j not in unit_clauses
            and -j not in unit_clauses
        ):
            maximum = literal_count[j]
            VSIDS_variable = j
    return VSIDS_variable


# comments about conflict: I couldnt find conflict clauses anywhere, we need to keep track of conflicts to add to their counter
# unit clauses in the last function is helpful because it does not make sense to pick the next variable from a set of unit clauses, its just a waste of time.
chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ" #these are the digits you will use for conversion back and forth
charsLen = len(chars)

def get_sudoku_from_dots(file_path, sudoku_size):
    """Returns a list of sudokus from file path. (i.e. list of list of lists)""" 
    with open(file_path, 'r') as sudokus:
        count = 0
        all_formulas = []
        num_characters_per_part = len(str(sudoku_size)) #4 = 1, 9= 1, 16 = 2, 100=3
        #print(sudoku_size, num_characters_per_part)
        for line in sudokus:
            cnf_formula=[]
            count = 0
            for character in line:
                count+=1
                if character != "." and character != "\n":
                    row = math.ceil(count / sudoku_size)
                    column = str(count - (row - 1) * sudoku_size)
                    row = str(row)
                    if row.isalpha():
                        row = chars.index(row)
                    #Pad the number with 9s if we have 16+ size sudokus
                    row = row.rjust(num_characters_per_part, '9')
                    if column.isalpha():
                        column = chars.index(column)
                    column = column.rjust(num_characters_per_part, '9')
                    if character.isalpha():
                        character = str(chars.index(character))
                    character = character.rjust(num_characters_per_part, '9')
                    variable = str(row) + str(column) + str(character)
                    cnf_formula.append([int(variable)])
            all_formulas.append(cnf_formula)
        return all_formulas
