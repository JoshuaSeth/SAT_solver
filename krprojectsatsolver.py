import numpy as np
import warnings
import random
import sys
import copy

# opening files
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

sudoku_rules_dimac = open(sudoku_rules_path, "r")
sudoku_example = open(sudoku_example_path, "r")

# DEPRECATED clause representation. Better not use!
def to_relative_index(index, removed_clause_indices):
    """The indices of the vlauses in whoch the variables appear may shift since
    some clauses might be removed. This function translate the absolute index
    returned by the variable_dictionary to the relative one pointing to the actual
    clause location in the cnf formula. Removed clause indices is a list containing
    the indices of removed clauses."""
    # For each index of clauses removed from the CNF
    for rm_clause_index in removed_clause_indices:
        # If it was before this clause shift this clause 1 index back
        if index > rm_clause_index:
            index -= 1
    return index


# DEPRECATED
def get_clauses_with_variable_deprecated(variable_location_dict, cnf_formula, variable):
    """Helper function to return clauses that contain this variable If these are
    shallow copies we can modify these directly. But not sure if they are."""
    # Get indices of clauses with this variable
    clauses_with_test_num = variable_location_dict[variable]
    clauses = []
    # Retrieve clauses by index from cnf formula and return
    for clause_index in clauses_with_test_num:
        clauses.append(cnf_formula[clause_index])
    return clauses


# DEPRECATED
def remove_terms_from_clauses(pure_literal_clauses, pure_literals):
    """Takes a list of clauses and a dict of pure literals and removes these
    literals from the clauses (i.e. sets them to True). Returns the cleaned
    clauses"""
    # Loop through these clauses and remove the terms that were pure
    for clause in pure_literal_clauses:
        for term in clause:
            if abs(term) in pure_literals:
                clause.remove(term)


def read_dimac(filename):
    num_vars = []
    clauses = []
    num_clauses = []
    for line in open(filename):
        if line.startswith("c"):  # ignore comment lines starting with 'c'
            continue
        if line.startswith(
            "p"
        ):  # gathering number of variables and number of clauses from line starting with 'p'
            num_vars = line.split()[2]
            num_clauses = line.split()[3]
            num_vars, num_clauses = int(num_vars), int(
                num_clauses
            )  # transforming into integers
            continue
        c = [
            int(x) for x in line[:-2].split()
        ]  # gathering clauses as integers for every line in the document, also removes '0's
        clauses.append(c)
    return clauses, num_vars, num_clauses


test_read = read_dimac(
    sudoku_example_path
)  # reads the example sudoku as integers in lists.
# print(test_read[0]) # for visualisation of the returned list

clauses, num_vars, num_clauses = read_dimac(sudoku_rules_path)
# print(clauses) # for visualisation of the returned list of the sudoku-rules.txt file

"""
this next bit is some test code to attempt to make a dictionary with the location of all the variables,
we probably need this because we will have to remove redundant clauses, i heard this in the lecture.
"""

cnf_formula = dict(
    zip(range(1, num_clauses + 1), clauses)
)  # making a dictionary with the numbers of clauses

var_clause = [list() for i in range(1, num_vars + 2)]

j = 1
for c in clauses:
    for var in c:
        if var >= 0:
            var_clause[abs(var)] += [j]
        elif var < 0:
            var_clause[-var] += [-j]
    j = j + 1

VARS = dict(zip(range(1, num_vars + 1), var_clause[1:]))


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
    """Returns whether the cnf has some empty clause)"""
    for clause in cnf_formula:
        if len(clause) is 0:
            if log_level > 2:
                print("Found an empty clause: {0}.".format(clause))
            return True
    return False


def SAT_simplify(
    cnf_formula, current_variable_assignment, var_assignment_history, log_level
):
    """Performs a full algorithm simplification step. (i.e. applying units, literals)"""
    if log_level > 1:
        print("\n Starting new simplification step")
    # (TAUT): Remove clauses that are tautologies
    tautologies = get_tautologies(cnf_formula)
    cnf_formula = remove_clauses_from_cnf(cnf_formula, tautologies)
    if log_level > 1:
        print(
            "Removed {0} tautologies from the CNF. CNF length reduced number of clauses to {1} clauses".format(
                len(tautologies), len(cnf_formula)
            )
        )

    # (UNIT PR): Find unit clauses and set them to true
    unit_clauses, variables_in_unit_clauses = get_unit_clauses(cnf_formula)
    remove_clauses_from_cnf(cnf_formula, unit_clauses)
    # Change other clauses accordingly with this var from the clauses
    removed_clauses = 0
    changed_clauses = 0
    for unit_clause_var in variables_in_unit_clauses:
        num_removed, num_changed = set_variable_assignment(cnf_formula, unit_clause_var)
        removed_clauses += num_removed
        changed_clauses += num_changed
        # current_variable_assignment[abs(unit_clause_var)] = bool(unit_clause_var/abs(unit_clause_var)+1)
        # var_assignment_history.append(unit_clause_var)
    if log_level > 1:
        print(
            "Removed {0} unit clauses from the CNF. Removed {1} clauses that became true by setting the unitclause to true. Changed {2} clauses according to the unit clause varaible. CNF length reduced number of clauses to {3} clauses".format(
                len(unit_clauses), removed_clauses, changed_clauses, len(cnf_formula)
            )
        )

    # (PURE): Find pure literals and set them to true
    pure_literal_clauses, pure_literals = get_pure_literal_clauses(cnf_formula)
    # One of the variables in these clauses is now true so can be removed
    remove_clauses_from_cnf(cnf_formula, pure_literal_clauses)
    if log_level > 1:
        print(
            "Removed {0} pure literal clauses from the CNF. CNF length reduced number of clauses to {1} clauses".format(
                len(pure_literal_clauses), len(cnf_formula)
            )
        )

    nothing_changed = (
        removed_clauses is 0
        and changed_clauses is 0
        and len(unit_clauses) is 0
        and len(tautologies) is 0
    )
    return cnf_formula, nothing_changed


def full_SAT_step(
    cnf_formula, history, log_level, current_variable_assignment, var_assignment_history
):
    if log_level > 1:
        print("\n Starting new SAT step")
    history_copy = copy.deepcopy(history)
    var_ass_history = copy.deepcopy(var_assignment_history)
    # Try to simplify repetivly until this is not possible anymore
    simplification_exhausted = False
    while not simplification_exhausted:
        cnf_formula, simplification_exhausted = SAT_simplify(
            cnf_formula, current_variable_assignment, var_ass_history, log_level
        )
        if log_level > 1 and not simplification_exhausted:
            print("Succesfully simplified formula. Continuing to simplify.")
        if log_level > 1 and simplification_exhausted:
            print("Formula simplified. No more simplification possible.")
        if log_level > 2:
            print("new CNF is: {0}".format(cnf_formula))

    if len(cnf_formula) is 0:
        return cnf_formula, history_copy, var_assignment_history

    # This will be none if there are no incosistencies, it will return a backtracked varaible if there are
    (
        random_variable,
        history_copy,
        var_ass_history,
        backtracked_cnf_formula,
    ) = SAT_check_and_backtrack(
        cnf_formula,
        history_copy,
        current_variable_assignment,
        var_ass_history,
        log_level,
    )

    # Then assign a random variable or backtrack on the previous variable
    if log_level > 1:
        print("\n Starting new variable assignment step")
    if random_variable is None:
        random_variable = get_variable_by_heuristic(
            backtracked_cnf_formula, "random", current_variable_assignment
        )
    num_removed, num_changed = set_variable_assignment(
        backtracked_cnf_formula, random_variable
    )
    # Set the current variable to true or false based on what we choose
    current_variable_assignment[abs(random_variable)] = bool(
        random_variable / abs(random_variable) + 1
    )
    var_ass_history.append(random_variable)
    if log_level > 0:
        print(
            "\n Set variable {0} to true. Removed {1} clauses from the CNF and changed {2} clauses. CNF length reduced number of clauses to {3} clauses".format(
                random_variable, num_removed, num_changed, len(cnf_formula)
            )
        )

    # Log variable assignment history for backtracking
    if log_level > -1:
        print("Current variable assignment history: {0}".format(var_ass_history))

    if log_level > 2:
        print("new CNF is: {0}".format(backtracked_cnf_formula))

    return backtracked_cnf_formula, history_copy, var_ass_history


def SAT_check_and_backtrack(
    cnf_formula, history, current_variable_assignment, var_assignment_history, log_level
):
    if log_level > 1:
        print("\n Starting new consistency step")
    history_copy = copy.deepcopy(history)
    # Cannot modify paramter objects in python
    var_ass_history = copy.deepcopy(var_assignment_history)
    # (CONSISTENT & BACKTRACK): check of formula consistent else backtrack
    # INcosistency can only be present in unit clauses
    unit_clauses, variables_in_unit_clauses = get_unit_clauses(cnf_formula)
    consistent = is_consistent(unit_clauses)
    has_empty_clauses = has_empty_clause(cnf_formula, log_level)
    if log_level > 1:
        print(
            "\n Formula is consistent: {0}, has empty clauses: {1} backtracking: {2}".format(
                consistent, has_empty_clauses, not consistent or has_empty_clauses
            )
        )

    # If no incosistencies do a normal step
    random_variable = None
    backtracked_cnf_formula = cnf_formula

    # Backtracking if necessary
    if not consistent or has_empty_clauses:
        if log_level > 0:
            print("\n Backtracking:")

        # Try to switch around the last assigned variable
        # If bot P and -P don't work backtrack further back
        if len(var_ass_history) > 1:
            if (
                abs(var_ass_history[len(var_ass_history) - 1])
                - abs(var_ass_history[len(var_ass_history) - 2])
                == 0
            ):
                if log_level > 1:
                    print(
                        "\n\n Annuling var assignments before: {0}".format(
                            var_ass_history
                        )
                    )

                # Remove the last P and -p for the next value reassignment
                var_ass_history = var_ass_history[: len(var_ass_history) - 2]
                history_copy = history_copy[: len(history_copy) - 2]
                if log_level > 1:
                    print("Annuling var assignments AFTER: {0}".format(var_ass_history))
                    print(
                        "History AFTER: {0} \n\n".format(
                            history_copy[len(history_copy) - 1]
                        )
                    )

    if log_level > 2:
        print("history length: {0}".format(len(history)))

        # Length of list might jave changed because of previous action
        if len(var_ass_history) > 0:
            # reload the cnf formula state from before this assignment
            backtracked_cnf_formula = history_copy[len(history_copy) - 2]
            random_variable = var_ass_history[len(var_ass_history) - 1] * -1

        # If the history is to short (ie. we backtracked to step 1 again, choose a random var)
        if len(var_ass_history) is 0:
            random_variable = None

    return random_variable, history_copy, var_ass_history, backtracked_cnf_formula


def SAT_solve(cnf_formula, log_level=0):
    """SAT solves a formula that is already in CNF. Returns SAT, variable assignment
    if it is satisfiable. Returns UNSAT if no satisfiable assignments exist"""
    # Track the assigned variables (i.e. p=true q=flase, r=true, etc.)
    current_variable_assignment = {}
    var_assignment_history = []
    implicit_assignment_history = []
    # A simple and naive way to keep history
    # A sudoku CNF is at most 22kB so should be alright for smaller problems like these
    # Might want to implemented backtracking data in a more sophisticated manner later
    history = []

    # Continuously apply rules sequentially
    while True:
        # (SAT): If formula is empty it is satisfied
        if len(cnf_formula) is 0:
            return "SAT"

        # Save current cnf formula to history
        history.append(copy.deepcopy(cnf_formula))

        cnf_formula, history, var_assignment_history = full_SAT_step(
            cnf_formula,
            history,
            log_level,
            current_variable_assignment,
            var_assignment_history,
        )


"""This cell contains some testing with all the foredefined formulae. """
# Test clauses for debugging
test_clauses = read_cnf_from_dimac(test_problem_3)
if has_empty_clause(test_clauses, log_level=3):
    print(
        "File already has empty clauses. Will never terminate. Something wrong with file loading"
    )
    sys.exit()


# Load sudoku rules and a sudoku
cnf_formula = read_cnf_from_dimac(sudoku_rules_path)
example_sudoku_clauses = read_cnf_from_dimac(sudoku_example_path)

# Merge the sudoku clauses with the game rules
cnf_formula.extend(example_sudoku_clauses)


# Try some sat solving
sat = SAT_solve(cnf_formula, log_level=2)
print(sat)

# When implementing DPLL let's see if this is a smart representation (var lookup-wise) otherwise will modify
