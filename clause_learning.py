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
            for clause in self.dependency_graph[key]:
                for variable in clause:
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
            # If the unit already has dependencies add these dependenvies 
            if unit_clause[1][0] in self.dependency_graph:
                #Add the clause from the original starting formula
                self.dependency_graph[unit_clause[1][0]].append(self.start_formula[unit_clause[0]])
            else:
                # So p: [-q OR p OR r] from the original formula. SO set the value by the original cluase from the formula
                # If it wasnt a unit clause right from the start
                # if len(self.start_formula[unit_clause[0]]) > 1:
                clause_var = unit_clause[1][0]
                self.dependency_graph[clause_var] = [self.start_formula[unit_clause[0]]]

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
            ) = self.get_lowest_index_conflict_var(
                learned_clauses, var_assignment_history, 0
            )
            # if earliest_problem_var_index == 999999:
            #     earliest_problem_var_index=0
            #     backtracked_var=var_assignment_history[0]

        if self.log_level > 1 and len(conflicts) > 0:
            print(
                "\n\nFound {0} conflicts, namely: {6}, Learned {1} clauses from this. First of these is {2}, originating from {7} and {8}. Backtracked to variable {3}. Reset history and assignment to history to index {4}. Length of CNF is now {5}. CNF is {9}".format(
                    len(conflicts),
                    len(learned_clauses),
                    learned_clauses[0] if len(learned_clauses) > 0 else "-",
                    backtracked_var,
                    earliest_problem_var_index,
                    len(cnf_formula),
                    [conflict[0] for conflict in conflicts],
                    conflicts[0][1] if len(conflicts) > 0 else "-",
                    conflicts[0][2] if len(conflicts) > 0 else "-",
                    cnf_formula,
                )
            )

        if len(conflicts) > 0:
            print("index " + str(earliest_problem_var_index))

            cnf_formula, history, var_assignment_history = self.backtrack(
                cnf_formula,
                history,
                var_assignment_history,
                learned_clauses,
                earliest_problem_var_index,
            )

        # self.draw_dependency_graph()

        # Return the whole modified packet
        return (
            backtracked_var,
            cnf_formula,
            history,
            var_assignment_history,
        )

    def backtrack(
        self,
        cnf_formula,
        history,
        var_assignment_history,
        learned_clauses,
        earliest_problem_var_index,
    ):
        # Add learned clauses to the relevant formulae

        print("CNF len before: {0}".format(len(cnf_formula)))
        cnf_formula = history[earliest_problem_var_index]
        print("CNF len after: {0}".format(len(cnf_formula)))

        cnf_formula.extend(learned_clauses)

        print("Dependency graph before: {0}".format(self.dependency_graph))
        print("len before", len(self.dependency_graph))
        # Don't forget to backtrack our own dependency graph also
        self.dependency_graph = self.dependency_history[earliest_problem_var_index]
        print("len after", len(self.dependency_graph))
        print("Dependency graph after: {0}".format(self.dependency_graph))

        # Now backtrack to this variable and backtrack the history and varaible assignment history accordingly
        history = history[:earliest_problem_var_index]
        var_assignment_history = var_assignment_history[:earliest_problem_var_index]
        print("depdndency history before:{0}".format(
            len(self.dependency_history)))
        self.dependency_history = self.dependency_history[:earliest_problem_var_index]
        print("depdndency history after:{0}".format(
            len(self.dependency_history)))
        return cnf_formula, history, var_assignment_history

    def get_lowest_index_conflict_var(self, learned_clauses, var_assignments, depth, precedent_vars = None, previous_vars=[]):
        """Gets the index in the list of assignments of the varaibles causing the conflicts. Returns the earliest index in the list of assignments"""
        if precedent_vars is None:
            # Convert conflicts to a list of problem variables
            problem_vars = []
            #The learned clauses are why we need to backtrack to a certain point to satisfy these
            for learned_clause in learned_clauses:
                for var in learned_clause:
                    problem_vars.append(var*-1)
        else: problem_vars = precedent_vars


        # Get a backtracked variable for these conflicts
        # This is a variable matching to lowest assignment index for all the conflict variables
        lowest_found_var_index = 999999
        lowest_found_var = None
        # Go through problem vars
        for problem_var in problem_vars:
            print("\n\nASSIGNMETNS:", var_assignments, "'\nlooking for var", problem_var)

            assign_index = 0
            found = False
            for assignment in var_assignments:
                # If we assigned the problem var in the assignment here
                if assignment * -1 == problem_var:
                    found = True
                    # If it is the earliest problem causing var from what we recorded set it
                    if assign_index < lowest_found_var_index:
                        lowest_found_var_index = assign_index
                        lowest_found_var = assignment
                assign_index += 1
            # It was not found in assignmetns this means that this in turn was also a dependency

            
            print("found", found, problem_var, "index should be", assign_index, " is ", lowest_found_var_index)

            if not found and problem_var not in previous_vars and depth < 16 and lowest_found_var_index > 0: #If it is equal to the previous var we have this situation 19: [20, 19, 33]
                try:
                    copy_prev = []
                    copy_prev.extend(previous_vars)
                    copy_prev.append(problem_var)
                    print("These vars were already looked for",previous_vars, copy_prev)
                    vars_it_depends_on = self.get_dependence_variables_for_var(problem_var)
                    index, var = self.get_lowest_index_conflict_var(
                        None, var_assignments, depth+1, precedent_vars=vars_it_depends_on,previous_vars=copy_prev
                    )
                    if index < lowest_found_var_index:
                        lowest_found_var_index = index
                        lowest_found_var = var
                    print(
                        "Var not found in variable assignments: {0}. Found as item in dependency graph: {1}, index:{2}, final var: {3}".format(problem_var, problem_var in self.dependency_graph, index, var))
                except Exception as e:
                    print(e)


        # For some reason var is not found in assignments revert to normal backtracking
        return lowest_found_var_index, lowest_found_var

    def get_learned_conflict_clauses(self, cnf_formula, learned_clauses):
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
        #Conflicts is a list of [var, [pos_clauses], [neg_clauses]]
        for conflict in conflicts:
            # Unpack elements of conflict
            conflict_var = conflict[0]
            pos_clauses = conflict[1]
            neg_clauses = conflict[2]
            
            learned_clauses_for_this_conflict = []

            #Get a cartesian product of the positive and negative competing clauses (none of them is matching)
            for pos_clause in pos_clauses:
                #And the negatives
                for neg_clause in neg_clauses:
                    learned_clause_cartesian_vars = []
                    for var in pos_clause:
                        learned_clause_cartesian_vars.append(var*-1)
                    for var in neg_clause:
                        learned_clause_cartesian_vars.append(var*-1)
                    learned_clauses_for_this_conflict.append(learned_clause_cartesian_vars)
           

            learned_clauses.extend(learned_clauses_for_this_conflict)
        #Learned clauses shoulld be of form [[learned var combination], [learned_var_combination]]
        return learned_clauses

    def get_conflict_clauses(self):
        """Get the clauses of the conflicts if any. Returns a list of list of conflicting clauses so. [[conflict_var, pos_clauses, neg_clauses]]"""
        conflict_clauses = []
        # Loop through all keys
        dict_as_list = self.dependency_graph.keys()
        for variable in dict_as_list:
            #Dont add everything twice
            if variable == abs(variable):
                conflicting_clauses_for_var = [variable, [], []]
                # If the opposite is also in the dependency graph there is a conflict
                if variable * -1 in dict_as_list:
                    # Add ALL the clauses to conflict clauses
                    for clause in self.dependency_graph[variable]:
                        conflicting_clauses_for_var[1].append(clause)
                    for clause in self.dependency_graph[variable*-1]:
                        conflicting_clauses_for_var[2].append(clause)
                    conflict_clauses.append(conflicting_clauses_for_var)
        return conflict_clauses


    def get_dependence_variables_for_var(self, variable):
        precedent_vars = []
        for clause in self.dependency_graph[variable]:
            for var in clause:
                precedent_vars.append(var)
        return precedent_vars

