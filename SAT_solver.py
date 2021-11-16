"""SAT_solver.py: The SAT solver can be imported form this file under the definition SAT_solve.
Other methods can be imported from this file such as the simplifier of a clausal formula and
performing a single SAT step (simplify, consistency check, assign vars and backtrack.
Clauses should be in the form of a list of list (an AND of OR's) i.e. [[111, -112], [432,634,423], [-453, -211]]"""

from SAT_helper_functions import *
from SAT_deprecated_backtracking import SAT_check_consistency_and_backtrack
from clause_learning import ClauseLearner
import copy


def SAT_simplify(
    cnf_formula,
    current_variable_assignment,
    var_assignment_history,
    cnf_index_tracker,
    clause_learner,
    history,
    log_level,
):
    """Performs a full algorithm simplification step. (i.e. applying units, literals)"""
    if log_level > 1:
        print("\n Starting new simplification step")
    # (TAUT): Remove clauses that are tautologies
    tautologies = get_tautologies(cnf_formula)
    cnf_formula = remove_clauses_from_cnf(cnf_formula, tautologies)

    # LOG
    if log_level > 1:
        print(
            "Removed {0} tautologies from the CNF. CNF length reduced number of clauses to {1} clauses".format(
                len(tautologies), len(cnf_formula)
            )
        )

    # (UNIT PR): Find unit clauses and set them to true
    unit_clauses, variables_in_unit_clauses = get_unit_clauses(cnf_formula)

    # For clause learning we need to collect the indices of the original clauses
    # list of [index, [p]]
    unit_clauses_and_indices = get_unit_clauses_and_indices(cnf_index_tracker)

    # These unit clauses are now going to be set to true in the clause learner with the original clauses as their reasons
    clause_learner.update_dependencies(unit_clauses_and_indices[0])
    # Apply clause learning (learn conflict clause and backtrack)
    (
        backtracked_var,
        cnf_formula,
        cnf_index_tracker,
        history,
        var_assignment_history,
    ) = clause_learner.apply_clause_learning(
        cnf_formula, cnf_index_tracker, history, var_assignment_history
    )

    remove_clauses_from_cnf(cnf_formula, unit_clauses)
    # Change other clauses accordingly with this var from the clauses
    removed_clauses = 0
    changed_clauses = 0
    for unit_clause_var in variables_in_unit_clauses:
        num_removed, num_changed = set_variable_assignment(cnf_formula, unit_clause_var)
        removed_clauses += num_removed
        changed_clauses += num_changed

    # LOG
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
        removed_clauses == 0
        and changed_clauses == 0
        and len(unit_clauses) == 0
        and len(tautologies) == 0
    )
    return cnf_formula, nothing_changed


def full_SAT_step(
    cnf_formula,
    history,
    log_level,
    current_variable_assignment,
    var_assignment_history,
    cnf_index_tracker,
    clause_learner,
):
    # LOG
    if log_level > 1:
        print("\n Starting new SAT step")

    # Just a name shortening
    var_ass_history = var_assignment_history

    # Try to simplify repetivly until this is not possible anymore
    simplification_exhausted = False
    while not simplification_exhausted:
        # Single simplification step
        cnf_formula, simplification_exhausted = SAT_simplify(
            cnf_formula,
            current_variable_assignment,
            var_ass_history,
            cnf_index_tracker,
            clause_learner,
            history,
            log_level,
        )

        # LOG
        if log_level > 1 and not simplification_exhausted:
            print("Succesfully simplified formula. Continuing to simplify.")
        if log_level > 1 and simplification_exhausted:
            print("Formula simplified. No more simplification possible.")
        if log_level > 2:
            print("new CNF is: {0}".format(cnf_formula))

    # If the formula is empty we are SAT so don't perform any operations anymore
    if len(cnf_formula) is 0:
        return cnf_formula, history, var_assignment_history

    # Get these retrun values from checking for consistency and backtracking if needed
    (
        backtracked_variable,  # This will be none if there are no incosistencies, it will return a backtracked varaible if there are
        history,
        var_ass_history,
        backtracked_cnf_formula,  # An old version of the CNF, the version it was at the time of the assignment of the backtracked variable
    ) = SAT_check_consistency_and_backtrack(
        cnf_formula,
        history,
        var_ass_history,
        clause_learner,
        log_level,
    )

    # LOG
    if log_level > 1:
        print("\n Starting new variable assignment step")

    # Then assign a random variable or backtrack on the previous variable
    if backtracked_variable is None:
        variable_to_change = get_variable_by_heuristic(
            backtracked_cnf_formula, "random", current_variable_assignment
        )
    else:
        variable_to_change = backtracked_variable

    num_removed, num_changed = set_variable_assignment(
        backtracked_cnf_formula, variable_to_change
    )

    # Set the current variable to true or false based on what we choose
    current_variable_assignment[abs(variable_to_change)] = bool(
        variable_to_change / abs(variable_to_change) + 1
    )

    # And add the set variable to the assignment history
    var_ass_history.append(variable_to_change)

    # LOG
    if log_level > 0:
        print(
            "\n Set variable {0} to true. Removed {1} clauses from the CNF and changed {2} clauses. CNF length reduced number of clauses to {3} clauses".format(
                variable_to_change, num_removed, num_changed, len(cnf_formula)
            )
        )

    # Log variable assignment history for backtracking
    if log_level > -1:
        print("Current variable assignment history: {0}".format(var_ass_history))

    if log_level > 2:
        print("new CNF is: {0}".format(backtracked_cnf_formula))

    return backtracked_cnf_formula, history, var_ass_history


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

    # CNF_index_tracker is used for backtracking to know what caused a unit cluase to be a unit cluase
    cnf_index_tracker = []
    # Format is: [index, [clause in current form]]
    index = 0
    # Save the index for each clause
    for clause in cnf_formula:
        # This also works shallowly, which is cool, because changes resulting from a assigning variables should be reflected in the index tracker (not for complete clause removals though!)
        cnf_index_tracker.append([index, clause])
        index += 1

    # Start up the clause learner
    clause_learner = ClauseLearner(cnf_formula, 4)

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
            cnf_index_tracker,
            clause_learner,
        )
