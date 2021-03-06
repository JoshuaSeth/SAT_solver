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

        unit_vars_set_true = []

        # Start up the clause learner
        clause_learner = ClauseLearner(cnf_formula, 3)

        could_simplify = True

        # Continuously apply rules sequentially
        while True:
            # (SAT): If formula is empty it is satisfied
            if len(cnf_formula) is 0:
                return "SAT"

            # Does a full SAT step (Backtrack, simplification, var_assignment)
            (
                cnf_formula,
                clause_learner,
                history,
                var_assignments,
                unit_vars_set_true,
                dep_graph,
                could_simplify,
            ) = self.SAT_step(
                cnf_formula,
                clause_learner,
                history,
                var_assignments,
                unit_vars_set_true,
                could_simplify,
            )

            clause_learner.dependency_graph = copy.deepcopy(dep_graph)

    def SAT_step(
        self,
        formula,
        clause_learner,
        history,
        var_assignments,
        unit_vars_set_true,
        could_simplify_further,
    ):
        """Performs a full algorithm SAT step."""

        # ------------------------------------------------------------------
        # BACKTRACKING: Check if consistent else backtrack to time in history
        # Design the index tracker on the fly ao we have a single source of truth
        cnf_index_tracker = get_cnf_index_tracker(formula)
        unit_indices, vars = get_unit_clauses_and_indices(cnf_index_tracker)

        unit_clauses, varss = get_unit_clauses(formula)
        clause_learner.update_dependencies(unit_indices)  # FOr some
        # Apply clause learning (learn conflict clause and backtrack)

        (
            backtracked_var,
            formula,
            history,
            var_assignments,
        ) = clause_learner.apply_clause_learning(
            formula,
            history,
            var_assignments,
        )
        print(
            "has empty clause after applying clause learning", has_empty_clause(
                formula)
        )

        # If we backtracked and got a var from this
        if backtracked_var is not None:
            if self.log_level > 1:
                print(
                    "Variable assignments after backtrack: {0}".format(
                        var_assignments)
                )
            # Set backtracked variavle
            formula, var_assignments, history = set_and_track_variable_assignment(
                formula,
                backtracked_var * -1,
                var_assignments,
                history,
                clause_learner,
            )

            # For future code
            backtracked_var = None

            if self.log_level > 1:
                print(
                    "Variable assignments after new backtrack variable: {0}".format(
                        var_assignments
                    )
                )
            print(
                "has empty clauses after backtracked after applied",
                has_empty_clause(formula),
            )

        # ------------------------------------------------------------------
        # VARIABLE ASSIGNMENT: If nothing changed we select but not backtracking select a var by heuristic
        else:
            if not could_simplify_further:

                random_var = get_variable_by_heuristic(
                    formula, "random", var_assignments
                )

                formula, var_assignments, history = set_and_track_variable_assignment(
                    formula,
                    random_var,
                    var_assignments,
                    history,
                    clause_learner,
                )
                if self.log_level > 1:
                    print(
                        "Variable assignments after var by heuristic: {0}".format(
                            var_assignments
                        )
                    )
                print(
                    "has empty clauses after heuristic var", has_empty_clause(
                        formula)
                )

        # ------------------------------------------------------------------
        # SIMPLIFICATION
        # (TAUT): Remove clauses that are tautologies
        # tautologies = get_tautologies(formula)
        # formula = remove_clauses_from_cnf(formula, tautologies)

        old_cnf = copy.deepcopy(formula)
        # (UNIT PR): Find unit clauses and set them to true
        unit_clauses, variables_in_unit_clauses = get_unit_clauses(formula)
        # Change other clauses accordingly with this var from the clauses
        remove_clauses_from_cnf(formula, unit_clauses)
        for unit_clause_var in variables_in_unit_clauses:
            # We do not register the setting of the unit clauses since it was necessary hence not set_and_track
            set_and_track_variable_assignment(
                formula,
                unit_clause_var,
                var_assignments,
                history,
                clause_learner,
            )
            # REMOVING UNIT CLAUSES CAN GIVE EMPTY VARS WHEN REMOVING MULTIPLE UNTRUE UNIT CLAUSES AT ONCE
            unit_indices, vars = get_unit_clauses_and_indices(
                cnf_index_tracker)
            clause_learner.update_dependencies(unit_indices)  # FOr some
            # Apply clause learning (learn conflict clause and backtrack)

            (
                backtracked_var,
                formula,
                history,
                var_assignments,
            ) = clause_learner.apply_clause_learning(
                formula,
                history,
                var_assignments,
            )
            # break the unit clause setting if an conflict erupted
            if backtracked_var is not None:
                break

        empty = has_empty_clause(formula)
        print("unit", empty)

        if empty:
            ind = index_empty_clause(formula)
            print(ind)
            print(old_cnf[ind])
            print(formula[ind])
        if self.log_level > 1 and len(unit_clauses) > 0:
            print(
                "Variable assignments after unit clause assignment: {0}".format(
                    var_assignments
                )
            )

        pure_literal_clauses = []
        if backtracked_var is None:
            # (PURE): Find pure literals and set them to true
            pure_literal_clauses, pure_literals = get_pure_literal_clauses(
                formula)
            # One of the variables in these clauses is now true so can be removed
            for pure_literal in pure_literals:
                formula, var_assignments, history = set_and_track_variable_assignment(
                    formula,
                    pure_literal,
                    var_assignments,
                    history,
                    clause_learner,
                )

            print("has empty clause after literal", has_empty_clause(formula))

            if self.log_level > 1 and len(pure_literals) > 0:
                print(
                    "Variable assignments after literal assignment: {0}".format(
                        var_assignments
                    )
                )

        could_simplify_further = (
            len(unit_clauses) != 0
            # or len(tautologies) != 0
            or len(pure_literal_clauses) != 0
        )

        if self.log_level > 1:
            print(
                "\n\nCould simplify: {0}. Formula length: {1}. Unit claues: {2}. Literals: {3}".format(
                    could_simplify_further,
                    len(formula),
                    len(unit_clauses),
                    len(pure_literal_clauses),
                )
            )

        return (
            formula,
            clause_learner,
            history,
            var_assignments,
            unit_vars_set_true,
            clause_learner.dependency_graph,
            could_simplify_further,
        )
