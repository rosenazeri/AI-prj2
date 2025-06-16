from myCSP.myVariable import *
from typing import *

class myVarArray:
    """
    A class to represent an N-dimensional array of variables, each with a domain of possible values.
    """
    def __init__(self, name: str, size: List[int], dom: range) -> None:
        """
        Initialize the variable array with the given size and domain.
        """
        self.name = name
        self.size = size
        self.dom = dom
        self.variables = self._create_array(name, size, dom)
    
    def _create_array(self, name: str, size: List[int], dom: range, depth: int = 0) -> Union[List, 'myVariable']:
        """
        Recursively create the N-dimensional array of variables.
        """
        if depth == len(size) - 1:
            return [myVariable(f"{name}[{i}]", dom) for i in range(size[depth])]
        return [self._create_array(f"{name}[{i}]", size, dom, depth + 1) for i in range(size[depth])]
    
    def _get_recursive(self, array: Union[List, 'myVariable'], indices: Tuple[Union[int, slice], ...]) -> Union['myVariable', List]:
        """
        Retrieve a variable or a sub-array from the array using the given indices.
        """
        if len(indices) == 1:
            if isinstance(indices[0], slice):
                return [array[i] for i in range(*indices[0].indices(len(array)))]
            return array[indices[0]]
        
        if isinstance(indices[0], slice):
            return [self._get_recursive(array[i], indices[1:]) for i in range(*indices[0].indices(len(array)))]
        
        return self._get_recursive(array[indices[0]], indices[1:])
    
    def __getitem__(self, index: Union[int, Tuple[int, ...]]) -> 'myVariable':
        """
        Overload the indexing operator to access variables in the array.
        """
        if not isinstance(index, tuple):
            index = (index,)
        return self._get_recursive(self.variables, index)
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return self.name
    
def my_values(v):
    if isinstance(v, myVariable):
        return my_value(v)
    if isinstance(v, (myVarArray, List)):
        return [my_values(u) for u in v]
    
def my_remaining_domains(v):
    if isinstance(v, myVariable):
        return my_remaining_domain(v)
    if isinstance(v, (myVarArray, List)):
        return [my_remaining_domains(u) for u in v]