"""The original method which backtracks 1 step to rwesolve direct conflicts or more steps if the conflict remains. Still usable."""

from SAT_helper_functions import *


def SAT_check_consistency_and_backtrack(
    cnf_formula, history, var_assignment_history, clause_learner, log_level
):
    """Checks if the formula is consistent. If not it returns a backtracked varaible. Else it returns nothing."""
    if log_level > 1:
        print("\n Starting new consistency step")

    has_empty_clauses = has_empty_clause(cnf_formula, log_level)
    if log_level > 1:
        print(
            "\n Has empty clauses: {0} backtracking: {1}".format(
                has_empty_clauses, has_empty_clauses
            )
        )

    # If no incosistencies do a normal step
    random_variable = None
    backtracked_cnf_formula = cnf_formula

    # Backtracking if necessary
    if has_empty_clauses:
        if log_level > 0:
            print("\n Backtracking:")

        # Try to switch around the last assigned variable
        # If bot P and -P don't work backtrack further back
        if len(var_assignment_history) > 1:
            if (
                abs(var_assignment_history[len(var_assignment_history) - 1])
                - abs(var_assignment_history[len(var_assignment_history) - 2])
                == 0
            ):
                if log_level > 1:
                    print(
                        "\n\n Annuling var assignments before: {0}".format(
                            var_assignment_history
                        )
                    )

                # Remove the last P and -p for the next value reassignment
                var_assignment_history = var_assignment_history[
                    : len(var_assignment_history) - 2
                ]
                history = history[: len(history) - 2]
                if log_level > 1:
                    print(
                        "Annuling var assignments AFTER: {0}".format(
                            var_assignment_history
                        )
                    )
                    print("History AFTER: {0} \n\n".format(history[len(history) - 1]))

        if log_level > 2:
            print("history length: {0}".format(len(history)))

        # Length of list might jave changed because of previous action
        if len(var_assignment_history) > 0:
            # reload the cnf formula state from before this assignment
            backtracked_cnf_formula = history[len(history) - 2]
            random_variable = (
                var_assignment_history[len(var_assignment_history) - 1] * -1
            )

        # If the history is to short (ie. we backtracked to step 1 again, choose a random var)
        if len(var_assignment_history) is 0:
            random_variable = None

    return random_variable, history, var_assignment_history, backtracked_cnf_formula
