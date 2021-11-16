"""This file provides functions to send the changed variables to and keeps track of a dependency graph. When having a conflict ir returns the conflict clause and the backtracking variable for this conflict clause."""
import copy
from SAT_helper_functions import *
import sys
import matplotlib.pyplot as plt
import networkx as nx
import time
import pylab as p


class ClauseLearner:
    def __init__(self, cnf_formula, log_level):
        """Set ups the clause learner for use. 1. Remembers original formula. 2. Constructs dictionary from this formula"""
        self.start_formula = self.copy_starting_cnf(cnf_formula)
        self.dictionary = self.create_clause_dictionary(self.start_formula)
        self.dependency_graph = {}
        self.log_level = log_level
        self.dependency_history = []

    def draw_dependency_graph(self):
        Weights = []

        G = nx.DiGraph()
        # each edge is a tuple of the form (node1, node2, {'weight': weight})
        for key in self.dependency_graph.keys():
            for variable in self.dependency_graph[key]:
                if not variable == key:
                    G.add_edge(variable, key)

        pos = nx.spring_layout(G)  # positions for all nodes

        # nodes
        # nx.draw_networkx_nodes(G, pos, node_size=700)
        nx.draw(G, with_labels=True)

        plt.show()

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
            # [0] is the index of the unit clause, [1] is the index clause
            if unit_clause[1][0] in self.dependency_graph:
                # warnings.warn(
                #     "Received {0}. However, this should already have been a unit clause and shold already have been set to true.".format(
                #         unit_clause
                #     )
                # )
                pass
            else:
                # So p: [-q OR p OR r] from the original formula. SO set the value by the original cluase from the formula
                # If it wasnt a unit clause right from the start
                # if len(self.start_formula[unit_clause[0]]) > 1:
                clause_var = unit_clause[1][0]
                self.dependency_graph[clause_var] = self.start_formula[unit_clause[0]]

                if self.log_level > 3:
                    print("Added {0} to dependency graph".format(unit_clause))
                    print(
                        "Now {0} being set is dependept on the assignments of {1}".format(
                            unit_clause[1][0], self.dependency_graph[unit_clause[1][0]]
                        )
                    )

    def apply_clause_learning(
        self,
        cnf_formula,
        history,
        var_assignment_history,
    ):
        """Applies clause learning. If no conflicts returns no backtracked variable and the orignal cnf and cnf_index. If a conflict is found, the conflict is added as a new 'learned' clause to the CNF and the backtracked variable and time in history is returned."""

        # Get the current conflicts
        print(
            "dependcy graph right before conflict finding: {0}".format(
                self.dependency_graph
            )
        )
        conflicts = self.get_conflict_clauses()

        # Learn clauses from these conflicts
        learned_clauses = self.learn_clauses_from_conflicts(conflicts)

        backtracked_var = None
        earliest_problem_var_index = None
        # LOG

        # Get index of earliest occuring problem var
        if len(conflicts) > 0:
            (
                earliest_problem_var_index,
                backtracked_var,
            ) = self.get_earliest_conflict_causing_var_index(
                conflicts, var_assignment_history
            )

        if self.log_level > 1 and len(conflicts) > 0:
            print(
                "\n\nFound {0} conflicts, namely: {6}, Learned {1} clauses from this. First of these is {2}, originating from {7} and {8}. Backtracked to variable {3}. Reset history and assignment to history to index {4}. Length of CNF is now {5}.".format(
                    len(conflicts),
                    len(learned_clauses),
                    learned_clauses[0] if len(learned_clauses) > 0 else "-",
                    backtracked_var,
                    earliest_problem_var_index,
                    len(cnf_formula),
                    [conflict[0] for conflict in conflicts],
                    conflicts[0][1] if len(conflicts) > 0 else "-",
                    conflicts[0][2] if len(conflicts) > 0 else "-",
                )
            )

        if self.log_level > 0:
            print(
                "history length: {0}, dependencies length: {1}, should be equal".format(
                    len(history), len(self.dependency_history)
                )
            )

        if len(conflicts) > 0:
            print("index " + str(earliest_problem_var_index))

            print("CNF len before: {0}".format(len(cnf_formula)))
            cnf_formula = history[earliest_problem_var_index]
            print("CNF len after: {0}".format(len(cnf_formula)))

            # Add learned clauses to the relevant formulae
            cnf_formula = self.add_learned_conflict_clauses(
                cnf_formula, learned_clauses
            )

            print("Dependency graph before: {0}".format(self.dependency_graph))
            print("len before", len(self.dependency_graph))
            # Don't forget to backtrack our own dependency graph also
            self.dependency_graph = self.dependency_history[earliest_problem_var_index]
            print("len after", len(self.dependency_graph))
            print("Dependency graph after: {0}".format(self.dependency_graph))

            # Now backtrack to this variable and backtrack the history and varaible assignment history accordingly
            history = history[:earliest_problem_var_index]
            var_assignment_history = var_assignment_history[:earliest_problem_var_index]
            print("depdndency history before:{0}".format(len(self.dependency_history)))
            self.dependency_history = self.dependency_history[
                :earliest_problem_var_index
            ]
            print("depdndency history after:{0}".format(len(self.dependency_history)))

        # self.draw_dependency_graph()

        # Return the whole modified packet
        return (
            backtracked_var,
            cnf_formula,
            history,
            var_assignment_history,
        )

    def get_earliest_conflict_causing_var_index(self, conflicts, var_assignments):
        """Gets the index in the list of assignments of the varaibles causing the conflicts. Returns the earliest index in the list of assignments"""
        # Convert conflicts to a list of problem variables
        problem_vars = []
        for conflict in conflicts:
            for var in conflict[1]:
                if (
                    var != conflict[0]
                    and var != conflict[0] * -1
                    and len(conflict[1]) > 1
                ):
                    problem_vars.append(var)
            if len(conflict) > 2:
                for var in conflict[2]:
                    if (
                        var != conflict[0]
                        and var != conflict[0] * -1
                        and len(conflict[2]) > 1
                    ):
                        problem_vars.append(var)

        # Get a backtracked variable for these conflicts
        # This is a variable matching to lowest assignment index for all the conflict variables
        lowest_found_var_index = 999999
        lowest_found_var = None
        # Go through problem vars
        for problem_var in problem_vars:
            assign_index = 0
            found = False
            for assignment in var_assignments:
                # If we assigned the problem var in the assignment here
                if assignment * -1 == problem_var:
                    # If it is the earliest problem causing var from what we recorded set it
                    if assign_index < lowest_found_var_index:
                        lowest_found_var_index = assign_index
                        lowest_found_var = assignment
                        found = True
                assign_index += 1
            # It was not found in assignmetns this means that this in turn was also a dependency
            if not found:
                conflicts = self.get_clauses_for_var(problem_var)
                index, var = self.get_earliest_conflict_causing_var_index(
                    [conflicts], var_assignments
                )
                # print(
                #     "index and vars after recursive search for ",
                #     problem_var,
                #     index,
                #     var,
                # )
                if index < lowest_found_var_index:
                    lowest_found_var_index = index
                    lowest_found_var = var

        return lowest_found_var_index, lowest_found_var

    def add_learned_conflict_clauses(self, cnf_formula, learned_clauses):
        """Searches for conflict. Learns a new clause from this conflict and adds this to the original CNF, current CNF and CNF index tracker. Needs to be added to all of these to function. Returns cnf_formula."""
        # Get learned clauses

        for learned_clause in learned_clauses:
            # Shallow
            cnf_formula.append(learned_clause)
            # Deep
            self.start_formula.append(copy.deepcopy(learned_clause))
        return cnf_formula

    def learn_clauses_from_conflicts(self, conflicts):
        """Returns the combination of variable assignments that has caused a conflict."""
        learned_clauses = []
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
                    and not [variable * -1, clause_2, clause_1] in conflict_clauses
                    and not [variable * -1, clause_1, clause_2] in conflict_clauses
                ):
                    conflict_clauses.append([variable, clause_1, clause_2])
        return conflict_clauses

    def get_clauses_for_var(self, variable):
        # Add the 2 clauses to conflict clauses
        if variable in self.dependency_graph:
            clause_1 = self.dependency_graph[variable]
            if variable * -1 in self.dependency_graph:
                clause_2 = self.dependency_graph[variable * -1]
                return [variable, clause_1, clause_2]
        else:
            if variable * -1 in self.dependency_graph:
                clause_1 = self.dependency_graph[variable * -1]
                return [variable, clause_1]
        return [variable, [variable]]
