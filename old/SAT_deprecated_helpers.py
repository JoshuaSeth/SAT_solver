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
