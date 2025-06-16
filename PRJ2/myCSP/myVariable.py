from typing import *

my_variables: List['myVariable'] = []
max_domain_size = 0

class myVariable:
    """
    A class representing a single variable with a domain of possible values.
    """
    def __init__(self, name: str, domain: List[int]) -> None:
        """
        Initialize the variable with its domain and set its remaining domain.
        """
        self.name = name
        self.domain = set(domain)               # It stores the initial domain and it never changes.
        self.remaining_domain = set(domain)     # Remaining domain starts as the full domain.
        self.value: Union[int, None] = None
        my_variables.append(self)
        global max_domain_size
        max_domain_size = max(max_domain_size, len(domain))
    
    def assign(self, value: int) -> None:
        """
        Assign a value to the variable if it is within the domain.
        """
        if value in self.remaining_domain:
            self.value = value
        else:
            raise ValueError("Value not in remaining domain")
    
    def remove_from_domain(self, value: int) -> None:
        """
        Remove a value from the remaining domain.
        """
        if value in self.remaining_domain:
            self.remaining_domain.remove(value)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.name
    
def my_value(v: 'myVariable'):
    return v.value

def my_remaining_domain(v: 'myVariable'):
    return v.remaining_domain