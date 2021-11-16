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
