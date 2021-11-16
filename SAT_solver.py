"""SAT_solver.py: The SAT solver can be imported form this file under the definition SAT_solve.
Other methods can be imported from this file such as the simplifier of a clausal formula and
performing a single SAT step (simplify, consistency check, assign vars and backtrack.
Clauses should be in the form of a list of list (an AND of OR's) i.e. [[111, -112], [432,634,423], [-453, -211]]"""

from SAT_helper_functions import *
import copy


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


def SAT_check_consistency_and_backtrack(
    cnf_formula, history, var_assignment_history, log_level
):
    """Checks if the formula is consistent. If not it returns a backtracked varaible. Else it returns nothing."""
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


def full_SAT_step(
    cnf_formula, history, log_level, current_variable_assignment, var_assignment_history
):
    # LOG
    if log_level > 1:
        print("\n Starting new SAT step")

    # I thought I was having some shallow dopy issues. THis might not be necessary anymore. Currently the largest time-consumer
    history_copy = copy.deepcopy(history)
    var_ass_history = copy.deepcopy(var_assignment_history)

    # Try to simplify repetivly until this is not possible anymore
    simplification_exhausted = False
    while not simplification_exhausted:
        # Single simplification step
        cnf_formula, simplification_exhausted = SAT_simplify(
            cnf_formula, current_variable_assignment, var_ass_history, log_level
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
        return cnf_formula, history_copy, var_assignment_history

    # Get these retrun values from checking for consistency and backtracking if needed
    (
        backtracked_variable,  # This will be none if there are no incosistencies, it will return a backtracked varaible if there are
        history_copy,
        var_ass_history,
        backtracked_cnf_formula,  # An old version of the CNF, the version it was at the time of the assignment of the backtracked variable
    ) = SAT_check_consistency_and_backtrack(
        cnf_formula,
        history_copy,
        var_ass_history,
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

    return backtracked_cnf_formula, history_copy, var_ass_history


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
