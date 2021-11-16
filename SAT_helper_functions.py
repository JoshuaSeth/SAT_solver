"""SAT_helper_functions.py: Provides all kind of cnf manipulation functions and functions for retrieving pure literals, unit clauses, consistency, etc. These functions are used by the SAT_solver class but can be used independently."""

import warnings
import numpy as np
import random
import math


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


def get_unit_clauses_and_indices(cnf_index_tracker):
    """Get all the unit clauses together with their indices (i.e.  [index,[p]]) from the cnf formula. These can be set immediately to true or else the formula is unsat"""
    # collect unit clauses to return
    unit_clauses_and_indices = []
    variables = []
    # Loop through clauses in the formula
    for clause in cnf_index_tracker:
        # If there is only 1 term in the clause part it is an unit clause
        if len(clause[1]) is 1:
            unit_clauses_and_indices.append(clause)
            variables.append(clause[1][0])
    return unit_clauses_and_indices, variables


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


def get_variable_by_heuristic(cnf_formula, heuristic, current_variable_assignment):
    if heuristic is "random":
        # Try to selct a variable we did not check yet, send it if it was not in assignment
        # Otherwise retry
        while True:
            variable = get_rand_var(cnf_formula)
            if not variable in current_variable_assignment:
                return abs(variable)

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
    """Returns whether the cnf has some empty clause"""
    for clause in cnf_formula:
        if len(clause) is 0:
            if log_level > 2:
                print("Found an empty clause: {0}.".format(clause))
            return True
    return False


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
