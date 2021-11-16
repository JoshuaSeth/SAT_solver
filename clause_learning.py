"""This file provides functions to send the changed variables to and keeps track of a dependency graph. When having a conflict ir returns the conflict clause and the backtracking variable for this conflict clause."""
import copy
from SAT_helper_functions import *


class ClauseLearner:
    def __init__(self, cnf_formula):
        """Set ups the clause learner for use. 1. Remembers original formula. 2. Constructs dictionary from this formula"""
        self.start_formula = self.set_starting_cnf(cnf_formula)
        self.dictionary = self.set_clause_dictionary(self.start_formula)
        self.dependency_graph = {}

    def set_starting_cnf(self, cnf_formula):
        """The clause learner needs a copy of the original CNF for dependencies and making a dictionary."""
        # Save copy of the start formula
        start_formula = copy.deepcopy(cnf_formula)
        return start_formula

    def get_clause_dictionary(self, cnf_formula):
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

    def update_dependency_graph(self, var_assignment, unit_clauses):
        """Updates the dependency graph by the given unit clauses from the last varaible assignment and the orignal formula."""
        # Loop through unit clauses
        for unit_clause in unit_clauses:
            if unit_clause in self.dependency_graph:
                # This unit clause became a unit clause because all other variables were false in the original clause
                # So how do we know what the original variables were?
                # Maybe give each clause an original index? So we can look it up in the original formula
                return
