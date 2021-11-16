"""This file provides functions to send the changed variables to and keeps track of a dependency graph. When having a conflict ir returns the conflict clause and the backtracking variable for this conflict clause."""
import copy
from SAT_helper_functions import *


class ClauseLearner:
    def __init__(self, cnf_formula, log_level):
        """Set ups the clause learner for use. 1. Remembers original formula. 2. Constructs dictionary from this formula"""
        self.start_formula = self.copy_starting_cnf(cnf_formula)
        self.dictionary = self.create_clause_dictionary(self.start_formula)
        self.dependency_graph = {}
        self.log_level = log_level

    def copy_starting_cnf(self, cnf_formula):
        """The clause learner needs a copy of the original CNF for dependencies and making a dictionary."""
        # Save copy of the start formula
        start_formula = copy.deepcopy(cnf_formula)
        return start_formula

    def create_clause_dictionary(self, cnf_formula):
        """Returns a dictionary where the variables are the keys and the
        clauses containing these keys the values.
        This way all clauses containing a certain variable can be quickly found"""
        dictionary = {}
        # Loop through all clauses in CNF
        for clause in cnf_formula:
            # Loop through all terms in clause
            for variable in clause:
                # Remove - if present
                # If term/variable is in dict add this clause index to it's references,
                if variable in dictionary:
                    dictionary[variable].append(clause)
                # Else add it to the dict referring to this clause
                else:
                    dictionary[variable] = [clause]
        return dictionary

    def update_dependencies(self, unit_clauses_and_indices):
        """Updates the dependency graph by the given unit clauses from the last varaible assignment and the orignal formula."""
        # Loop through unit clauses
        for unit_clause in unit_clauses_and_indices:
            if unit_clause[0] in self.dependency_graph:
                warnings.warn(
                    "Received {0}. However, this should already have been a unit clause and shold already have been set to true.".format(
                        unit_clause
                    )
                )
            else:
                # So p: [-q OR p OR r] from the original formula. SO set the value by the original cluase from the formula
                self.dependency_graph[unit_clause[1][0]] = self.start_formula[
                    unit_clause[0]
                ]

                if self.log_level > 2:
                    print("Added {0} to dependency graph".format(unit_clause))
                    print(
                        "Now {0} being set is dependept on the assignments of {1}".format(
                            unit_clause[1][0], self.dependency_graph[unit_clause[1][0]]
                        )
                    )

    def add_learned_conflict_clauses(self, cnf_formula, cnf_index_tracker):
        """Searches for conflict. Learns a new clause from this conflict and adds this to the original CNF, current CNF and CNF index tracker. Needs to be added to all of these to function. Returns cnf_formula and cnf_index_tracker"""
        # Get learned clauses
        learned_clauses = self.learn_clauses_from_conflicts()
        for learned_clause in learned_clauses:
            # Shallow
            cnf_formula.append(learned_clause)
            # Shallow
            cnf_index_tracker.append([len(self.start_formula), learned_clause])
            # Deep
            self.start_formula.append(copy.deepcopy(learned_clause))
        return cnf_formula, cnf_index_tracker

    def learn_clauses_from_conflicts(self):
        """Returns the combination of variable assignments that has caused a conflict."""
        learned_clauses = []
        conflicts = self.get_conflict_clauses()
        for conflict in conflicts:
            # Unpack elements of conflict
            conflict_var = conflict[0]
            clause_1 = conflict[1]
            clause_2 = conflict[2]
            # Remove the conflict var from the clause (this was effect of conflict not cause)
            if conflict_var in clause_1:
                clause_1.remove(conflict_var)
            if conflict_var * -1 in clause_1:
                clause_1.remove(conflict_var * -1)
            if conflict_var in clause_2:
                clause_2.remove(conflict_var)
            if conflict_var * -1 in clause_2:
                clause_2.remove(conflict_var * -1)
            # Now everything remaining in these clauses was set to false in the assignment history causing the conflict
            problem_vars = []
            problem_vars.extend(clause_1)
            problem_vars.extend(clause_2)
            addendum_clause = []
            # Add the inverse of these assignments to the addendum clause
            # This is the clause that is learned
            for var in problem_vars:
                addendum_clause.append(var * -1)

            # We want to add this addendum to the cnf but also to the index tracker so that we can now treat it as just another part of the formula
            learned_clauses.append(addendum_clause)
        return learned_clauses

    def get_conflict_clauses(self):
        """Get the clauses of the conflicts if any. Returns a list of list of conflicting clauses so. [[conflict_var, clause_1, clause_2]]"""
        conflict_clauses = []
        # Loop through all keys
        dict_as_list = self.dependency_graph.keys()
        for variable in dict_as_list:
            # If the opposite is also in the dependency graph there is a conflict
            if variable * -1 in dict_as_list:
                # Add the 2 clauses to conflict clauses
                clause_1 = self.dependency_graph[variable]
                clause_2 = self.dependency_graph[variable * -1]
                if (
                    not [variable, clause_1, clause_2] in conflict_clauses
                    and not [variable, clause_2, clause_1] in conflict_clauses
                ):
                    conflict_clauses.append([variable, clause_1, clause_2])
        return conflict_clauses
