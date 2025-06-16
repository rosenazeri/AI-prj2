from myCSP.myVariable import *
from typing import *

from abc import ABC, abstractmethod
from queue import Queue


class myConstraint(ABC):
    """
    Abstract base class for constraints.
    """
    @abstractmethod
    def is_satisfied(self) -> bool:
        pass

    def __str__(self) -> str:
        pass


class myUnaryConstraint(myConstraint):
    """
    A class representing a unary constraint on a single variable.
    """
    def __init__(self, var: myVariable, relation: Callable[[int], bool], relation_name: str = None) -> None:
        if relation_name is not None:
            self.relation_name = relation_name
        else:
            self.relation_name = "?"
        self.var = var
        self.relation = relation
        self.num = None

    def __init__(self, var: myVariable, num: int, relation: Union[str, Callable[[int, int], bool]], relation_name: str = None) -> None:
        if relation_name is not None:
            self.relation_name = relation_name
        elif isinstance(relation, str):
            self.relation_name = relation
        else:
            self.relation_name = "?"
        self.var = var
        if callable(relation):
            self.relation = lambda a: relation(a, self.num)
        else:
            self.relation = lambda a: self._get_relation_function(relation)(a, self.num)
        self.num = num
        
    
    def _get_relation_function(self, relation: str) -> Callable[[int, int], bool]:
        """
        Convert a string relation into a corresponding function.
        """
        operators = {
            "=": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            "<": lambda a, b: a < b,
            "<=": lambda a, b: a <= b,
            ">": lambda a, b: a > b,
            ">=": lambda a, b: a >= b,
        }
        return operators.get(relation, lambda a, b: False)
    
    def is_satisfied(self) -> bool:
        """
        Check if the unary constraint is satisfied.
        """
        return self.var.value is None or self.relation(self.var.value)
    
    def is_value_satisfied(self, x: int) -> bool:
        return self.relation(x)
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        if self.num is None:
            return f"{self.var} {self.relation_name}"
        else:
            return f"{self.var} {self.relation_name} {self.num}"


class myBinaryConstraint(myConstraint):
    """
    A class representing a binary constraint between two variables.
    The relation can be equality, inequality, or a function returning True/False.
    """
    def __init__(self, var1: myVariable, var2: myVariable, relation: Union[str, Callable[[int, int], bool]] ,relation_name: str = None) -> None:
        """
        Initialize the binary constraint with two variables and a relation.
        """
        if relation_name is not None:
            self.relation_name = relation_name
        elif isinstance(relation, str):
            self.relation_name = relation
        else:
            self.relation_name = "?"
        self.var1 = var1
        self.var2 = var2
        self.relation = relation if callable(relation) else self._get_relation_function(relation)
        
    
    def _get_relation_function(self, relation: str) -> Callable[[int, int], bool]:
        """
        Convert a string relation into a corresponding function.
        """
        operators = {
            "=": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            "<": lambda a, b: a < b,
            "<=": lambda a, b: a <= b,
            ">": lambda a, b: a > b,
            ">=": lambda a, b: a >= b,
        }
        return operators.get(relation, lambda a, b: False)
    
    def is_satisfied(self) -> bool:
        """
        Check if the binary constraint is satisfied.
        """
        if self.var1.value is None or self.var2.value is None:
            return True  # Constraint is not violated if variables are unassigned
        return self.relation(self.var1.value, self.var2.value)
    
    def is_value_satisfied(self, x1: int, x2: int) -> bool:
        return self.relation(x1, x2)
    
    def is_value_order_satisfied(self, v1: myVariable, v2: myVariable, x1: int, x2: int) -> bool:
        if v1 == self.var1 and v2 == self.var2:
            return self.relation(x1, x2)
        elif v1 == self.var2 and v2 == self.var1:
            return self.relation(x2, x1)
        return True # TODO: throw exception
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return f"{self.var1} {self.relation_name} {self.var2}"
    
class myConstraintGraph:
    """
    Represents a constraint graph for a Constraint Satisfaction Problem (CSP).
    Manages unary and binary constraints between variables and provides methods
    for checking constraint satisfaction and retrieving graph structure.
    """
    def __init__(self, constraint_list: List['myConstraint']):
        """
        Initializes the constraint graph with the given list of constraints.

        Args:
            constraint_list (List[myConstraint]): A list of constraints to be applied in the graph.
        """
        # stores all the edges (v1,v2) and the constraints between them
        self.binary_graph: Dict[
                            myVariable, 
                            Dict[
                                myVariable, 
                                List[myBinaryConstraint]
                                ]
                            ] = {}
        
        # stores all the unary constraints for each v
        self.unary_graph: Dict[
                            myVariable,
                            List[myUnaryConstraint]
                            ] = {}
        
        # Initialize empty adjacency lists for all variables.
        for v in my_variables:
            self.binary_graph[v] = {}
            self.unary_graph[v] = []
            
        # Populate the graph with the given constraints.
        for c in constraint_list:
            if isinstance(c, myUnaryConstraint):
                v = c.var
                self.unary_graph[v].append(c)
            elif isinstance(c, myBinaryConstraint): 
                self._add_directed_edge(c.var1, c.var2, c)
                self._add_directed_edge(c.var2, c.var1, c)

    def _add_directed_edge(self, v1: myVariable, v2: myVariable, c: myBinaryConstraint):
        """
        Adds a directed edge between two variables with a binary constraint.

        Args:
            v1 (myVariable): The first variable.
            v2 (myVariable): The second variable.
            c (myBinaryConstraint): The constraint between the two variables.
        """
        if v2 not in self.binary_graph[v1].keys():
            self.binary_graph[v1][v2] = [c]
        else:
            self.binary_graph[v1][v2].append(c)

    def is_arc_satisfied(self, v1: myVariable, v2: myVariable, x1:int, x2:int):
        """
        Checks if the assignment (x1, x2) satisfies all binary constraints between v1 and v2.

        Args:
            v1 (myVariable): The first variable.
            v2 (myVariable): The second variable.
            x1 (int): The assigned value of v1.
            x2 (int): The assigned value of v2.

        Returns:
            bool: True if all constraints are satisfied, False otherwise.
        """
        # If there is no edge between v1 and v2, the arc is trivially satisfied.
        if v2 not in self.binary_graph[v1].keys():
            return True
        
        # Check the satisfaction of all constraints on the edge (v1, v2).
        result = True
        for c in self.binary_graph[v1][v2]:
            result = result and c.is_value_order_satisfied(v1, v2, x1, x2)
        return result
    
    def is_node_satisfied(self, v: myVariable, x: int):
        """
        Checks if the assignment x satisfies all unary constraints on variable v.

        Args:
            v (myVariable): The variable being checked.
            x (int): The assigned value of v.

        Returns:
            bool: True if all unary constraints are satisfied, False otherwise.
        """
        return all(c.is_value_satisfied(x) for c in self.unary_graph[v])
    
    def neighbors(self, v: myVariable) -> List[myVariable]:
        """
        Retrieves all neighboring variables of v.

        Args:
            v (myVariable): The variable whose neighbors are to be retrieved.

        Returns:
            List[myVariable]: A list of neighboring variables.
        """
        return self.binary_graph[v].keys()
    
    def get_arcs(self) -> Queue[Tuple[myVariable, myVariable]]:
        """
        Retrieves all arcs (variable pairs) in the constraint graph.

        Returns:
            Queue[Tuple[myVariable, myVariable]]: A queue containing all arcs in the graph.
        """
        # Initialize a queue with a size of O(DV^2), where D is the domain size.
        arcs = Queue(max_domain_size * len(my_variables) ** 2)
        for v1 in self.binary_graph.keys():
            for v2 in self.binary_graph[v1].keys():
                arcs.put((v1, v2))
        
        return arcs
    
    def is_assignment_complete(self):
        """
        Checks if all variables have been assigned a value.

        Returns:
            bool: True if all variables are assigned, False otherwise.
        """
        for v in my_variables:
            if v.value is None:
                return False
        return True
    
    def is_assignment_consistent(self, v: myVariable):
        """
        Checks if the current assignment of variable v is consistent with all its constraints.

        Args:
            v (myVariable): The variable to check.

        Returns:
            bool: True if the assignment is consistent, False otherwise.
        """
        for c in self.unary_graph[v]:
            if not c.is_satisfied():
                return False
            
        for u in self.binary_graph[v].keys():
            for c in self.binary_graph[v][u]:
                if not c.is_satisfied():
                    return False
                
        return True