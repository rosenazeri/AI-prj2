from pycsp3 import *


n = 8

q = VarArray(size=n, dom=range(n))

satisfy(
   AllDifferent(q),
   AllDifferent(q[i] + i for i in range(n)),
   AllDifferent(q[i] - i for i in range(n))
)
if solve(verbose=2) is SAT:
    print(values(q))