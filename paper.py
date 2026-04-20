import sympy as sp
import numpy as np


n = 10
x = sp.symbols(" ".join(f"x{i + 1}" for i in range(n)))
X = []
for i in range(n):
    for j in range(i, n):
        X.append(x[i] * x[j])
dic = dict((x[i], i) for i in range(n))
print(np.array(list(map(lambda x: x.subs(dic), X))))

x0 = np.random.randn(6) * 0.1
print(x0)