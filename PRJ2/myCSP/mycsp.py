from myCSP.myVariable import *
from myCSP.myVarArray import *
from myCSP.myConstraint import *
from myCSP.AllDifferent import *
from board import Board
from refresher import Refresher
import time
from queue import Queue

# my_variables = [] is declared in myVariable.py
constraint_list = []
g: myConstraintGraph


def my_satisfy(*constraints: Union[myConstraint, myAllDifferent]) -> None:
    """
    Adds constraints to the constraint list and initializes the constraint graph.
    
    :param constraints: A variable number of constraint objects (either myConstraint or myAllDifferent).
    """
    for constraint in constraints:
        if isinstance(constraint, myAllDifferent):
            constraint_list.extend(constraint.get_constraints())
        else:
            constraint_list.append(constraint)

    global g
    g = myConstraintGraph(constraint_list)


def my_solve(do_unary_check: bool,
             do_arc_consistency: bool,
             do_mrv: bool,
             do_lcv: bool,
             refresher: Refresher) -> bool:
    """
    Solves the CSP problem using backtracking with optional heuristics.
    
    :param do_unary_check: If True, performs node consistency.
    :param do_arc_consistency: If True, applies arc consistency during backtracking.
    :param do_mrv: If True, applies Minimum Remaining Values (MRV) heuristic.
    :param do_lcv: If True, applies Least Constraining Value (LCV) heuristic.
    :param refresher: A Refresher object to update the UI during solving.
    Use `refresher.refresh_screen()` in middle of your code to update the sudoku on screen.
    :return: True if a solution is found, False otherwise.
    :raises: `StopAlgorithmException` if user clicks on 'Stop' or exit button.
    You do not need to handle this; it's handled in `main.py`.
    """

    # node consistency
    if do_unary_check:
        if not node_consistency(refresher):
            return False

    # backtrack 
    if not backtrack(do_arc_consistency, do_mrv, do_lcv, refresher):
        return False

    return True


def my_clear():
    global my_variables, constraint_list, g
    my_variables.clear()
    constraint_list.clear()
    g = None


def node_consistency(refresher: Refresher) -> bool:
    """
    Applies node consistency by filtering values that do not satisfy unary constraints.

    Use `g.is_node_satisfied(v, d)` to check if `d` is satisfied for variable `v`
    
    :param refresher: A Refresher object to update the UI.
    :return: True if node consistency is maintained, False otherwise.
    """
    global my_variables
    for var in my_variables:
        current_domain = var.remaining_domain.copy()
        filtered_values = set()

        for value in current_domain:
            if g.is_node_satisfied(var, value):
                filtered_values.add(value)

        if len(filtered_values) == 0:
            return False

        if filtered_values != current_domain:
            var.remaining_domain = filtered_values
            refresher.refresh_screen()

    return True


def backtrack(do_arc_consistency: bool, do_mrv: bool, do_lcv: bool, refresher: Refresher):
    """
    Implements backtracking search with optional heuristics.

    Use `g.is_assignment_complete()` to check if every variable has been assigned a value.
    Use `g.is_assignment_consistent(v)` to check if the value assigned to v satisfies all the constrains
    between v and its neighbors. It also checks the unary constraints.
    Use `extract_domains()` and  `restore_domains()` to backup and restore domains of all the variables.
    Use `set_doms_to_values()` to set remaining_domain=value for any variable that has been assigned a value. This
    can be useful before calling `inference()` since inference works with only remaining domains and not
    assigned values.
    
    :param do_arc_consistency: If True, use arc consistency forwarding algorithm inside `inference()` method.
    :param do_mrv: If True, apply Minimum Remaining Values (MRV) heuristic inside `select_unassigned_variable()` method.
    :param do_lcv: If True, apply Least Constraining Value (LCV) heuristic inside `order_domain_values()` method.
    :param refresher: A Refresher object to update the UI during solving.
    Use `refresher.refresh_screen()` in middle of your code to update the sudoku on screen.
    :return: True if a solution is found, False otherwise.
    """
    if g.is_assignment_complete():
        return True

    variable = select_unassigned_variable(do_mrv)
    possible_values = order_domain_values(variable, do_lcv)

    for val in possible_values:
        variable.value = val
        refresher.refresh_screen()

        if g.is_assignment_consistent(variable):
            saved_domains = extract_domains()
            set_doms_to_values()

            inference_successful = inference(do_arc_consistency, refresher)
            if inference_successful:
                solved = backtrack(do_arc_consistency, do_mrv, do_lcv, refresher)
                if solved:
                    return True

            restore_domains(saved_domains)
            refresher.refresh_screen()

        variable.value = None
        refresher.refresh_screen()

    return False


def inference(do_arc_consistency: bool, refresher: Refresher) -> bool:
    """
    Uses forward-checking methods to eliminate variable domains that cause contradiction in the future. 
    """
    if do_arc_consistency:
        return arc_consistency(refresher)
    return True


def arc_consistency(refresher: Refresher) -> bool:
    """
    Implements the AC-3 algorithm for arc consistency.

    Use `g.get_arcs()` to get a queue containing all arcs in the graph.
    
    :param refresher: A Refresher object to update the UI.
    Use `refresher.refresh_screen()` in middle of your code to update the sudoku on screen.
    :return: True if arc consistency is maintained, False otherwise.
    """
    arc_queue = g.get_arcs()

    while not arc_queue.empty():
        x, y = arc_queue.get()

        if revise(x, y):
            refresher.refresh_screen()

            if len(x.remaining_domain) == 0:
                return False

            for nbr in g.neighbors(x):
                if nbr != y:
                    arc_queue.put((nbr, x))

    return True


def revise(v1: myVariable, v2: myVariable):
    """
    Revises the domain of v1 by removing values that do not satisfy arc consistency with v2.

    For checking the satisfiability of any arc, use g.is_arc_satisfied(v1, v2, x1, x2) so 
    the order of values for variables remains consistent.
    
    :param v1: First variable.
    :param v2: Second variable.
    :return: True if the domain of v1 was revised, False otherwise.
    """

    values_to_eliminate = []
    revised = False

    for x_val in v1.remaining_domain:
        compatible = False
        for y_val in v2.remaining_domain:
            if g.is_arc_satisfied(v1, v2, x_val, y_val):
                compatible = True
                break

        if not compatible:
            values_to_eliminate.append(x_val)

    if values_to_eliminate:
        v1.remaining_domain.difference_update(values_to_eliminate)
        revised = True

    return revised


def select_unassigned_variable(do_mrv: bool) -> myVariable:
    if do_mrv:
        return minimum_remaining_values()
    else:
        return select_static_order_variable()


def select_static_order_variable() -> myVariable:
    for v in my_variables:
        if v.value is None:
            return v
    return None


def minimum_remaining_values() -> myVariable:
    """
    Returns a variable with the lowest remaining domain count.
    """
    unassigned_vars = [v for v in my_variables if v.value is None]

    if not unassigned_vars:
        return None

    return min(unassigned_vars, key=lambda v: len(v.remaining_domain))


def order_domain_values(v: myVariable, do_lcv: bool) -> List[int]:
    if do_lcv:
        return least_constraining_value(v)
    else:
        return static_order_domains(v)


def static_order_domains(v: myVariable) -> List[int]:
    return list(v.remaining_domain)


def least_constraining_value(v: myVariable) -> List[int]:
    """
    Orders the values in the domain of `v` based on how few constraints they impose on neighboring variables.  
    Values that allow the most options for neighboring variables are prioritized.
    """
    score_map = dict()

    for val in v.remaining_domain:
        conflict_score = 0

        for adjacent in g.neighbors(v):
            if adjacent.value is not None:
                continue

            conflict_score += sum(
                not g.is_arc_satisfied(v, adjacent, val, other_val)
                for other_val in adjacent.remaining_domain
            )

        score_map[val] = conflict_score

    sorted_vals = sorted(score_map.items(), key=lambda item: item[1])
    return [item[0] for item in sorted_vals]


def extract_domains() -> Dict[myVariable, List[int]]:
    """
    Backups all the remaining domains of every variable and returns them.

    :return: The becked-up domains as a dictionary {v:[d]}.
    """
    backup_domains = {}
    for v in my_variables:
        backup_domains[v] = set(v.remaining_domain)

    return backup_domains


def restore_domains(backup_domains: Dict[myVariable, List[int]]):
    """
    Sets back the remaining domains of every variable to their becked-up domains.

    :param backup_domains: The previous remaining_domains of all variables.
    """
    for v in my_variables:
        v.remaining_domain = backup_domains[v]


def set_doms_to_values():
    """
    Sets remaining_domain of all variables with assigned value to their value.

    Use this function after a variable has been assigned a value
    and inference() needs to be called.
    """
    for v in my_variables:
        if v.value is not None:
            v.remaining_domain = set([v.value])
