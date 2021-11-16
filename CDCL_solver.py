from SAT_helper_functions import *
from SAT_deprecated_backtracking import SAT_check_consistency_and_backtrack
from clause_learning import ClauseLearner
import copy


class CDCL_Solver:
    def __init__(self, log_level):
        self.log_level = log_level

    def SAT_solve(self, cnf_formula):
        """SAT solves a formula that is already in CNF. Returns SAT, variable assignment
        if it is satisfiable. Returns UNSAT if no satisfiable assignments exist"""
        # Track the assigned variables (i.e. p=true q=flase, r=true, etc.)
        var_assignments = []
        history = []

        # CNF_index_tracker is used for backtracking to know what caused a unit cluase to be a unit cluase
        cnf_index_tracker = get_cnf_index_tracker(cnf_formula)

        # Start up the clause learner
        clause_learner = ClauseLearner(cnf_formula, 2)

        could_simplify = True

        # Continuously apply rules sequentially
        while True:
            # (SAT): If formula is empty it is satisfied
            if len(cnf_formula) is 0:
                return "SAT"

            # Does a full SAT step (Backtrack, simplification, var_assignment)
            (
                cnf_formula,
                cnf_index_tracker,
                clause_learner,
                history,
                var_assignments,
                could_simplify,
            ) = self.SAT_step(
                cnf_formula,
                cnf_index_tracker,
                clause_learner,
                history,
                var_assignments,
                could_simplify,
            )

    def SAT_step(
        self,
        formula,
        cnf_index_tracker,
        clause_learner,
        history,
        var_assignments,
        could_simplify_further,
    ):
        """Performs a full algorithm SAT step."""
        # ------------------------------------------------------------------
        # BACKTRACKING: Check if consistent else backtrack to time in history
        unit_indices = get_unit_clauses_and_indices(cnf_index_tracker)
        clause_learner.update_dependencies(unit_indices[0])  # FOr some
        # Apply clause learning (learn conflict clause and backtrack)
        (
            backtracked_var,
            formula,
            cnf_index_tracker,
            history,
            var_assignments,
        ) = clause_learner.apply_clause_learning(
            formula, cnf_index_tracker, history, var_assignments
        )

        # If we backtracked and got a var from this
        if backtracked_var is not None:
            # Set backtracked variavle
            formula, var_assignments, history = set_and_track_variable_assignment(
                formula, backtracked_var * -1, var_assignments, history
            )

        # ------------------------------------------------------------------
        # VARIABLE ASSIGNMENT: If nothing changed we select but not backtracking select a var by heuristic
        else:
            if not could_simplify_further:
                random_var = get_variable_by_heuristic(
                    formula, "random", var_assignments
                )
                formula, var_assignments, history = set_and_track_variable_assignment(
                    formula, random_var, var_assignments, history
                )

        # ------------------------------------------------------------------
        # SIMPLIFICATION
        # (TAUT): Remove clauses that are tautologies
        tautologies = get_tautologies(formula)
        formula = remove_clauses_from_cnf(formula, tautologies)

        # (UNIT PR): Find unit clauses and set them to true
        unit_clauses, variables_in_unit_clauses = get_unit_clauses(formula)
        # Redundant but probably speeds it up a bit
        remove_clauses_from_cnf(formula, unit_clauses)
        # Change other clauses accordingly with this var from the clauses
        rm_clauses, change_clauses = 0, 0
        for unit_clause_var in variables_in_unit_clauses:
            # We do not register the setting of the unit clauses since it was necessary hence not set_and_track
            x, y = set_variable_assignment(formula, unit_clause_var)
            rm_clauses += x
            change_clauses += y

        # (PURE): Find pure literals and set them to true
        pure_literal_clauses, pure_literals = get_pure_literal_clauses(formula)
        # One of the variables in these clauses is now true so can be removed
        for pure_literal in pure_literals:
            formula, var_assignments, history = set_and_track_variable_assignment(
                formula, pure_literal, var_assignments, history
            )

        could_simplify_further = (
            rm_clauses == 0
            and change_clauses == 0
            and len(unit_clauses) == 0
            and len(tautologies) == 0
        )
        return (
            formula,
            cnf_index_tracker,
            clause_learner,
            history,
            var_assignments,
            could_simplify_further,
        )
