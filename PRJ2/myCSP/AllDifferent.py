from myCSP.myVariable import *
from myCSP.myConstraint import *
from typing import *

class myAllDifferent:
    """
    A class representing an all-different constraint on a set of variables.
    """
    def __init__(self, vars: List[myVariable]) -> None:
        """
        Initialize the all-different constraint with a list of variables.
        Creates binary constraints for each pair of variables to enforce distinct values.
        """
        self.vars = vars
        self.constraints = [
            myBinaryConstraint(vars[i], vars[j], "!=")
            for i in range(len(vars)) for j in range(i + 1, len(vars))
        ]
    
    def get_constraints(self) -> List[myBinaryConstraint]:
        """
        Return the list of binary constraints enforcing the all-different condition.
        """
        return self.constraints

    def is_satisfied(self) -> bool:
        """
        Check if all binary constraints are satisfied.
        """
        return all(constraint.is_satisfied() for constraint in self.constraints)
