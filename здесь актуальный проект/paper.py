import sympy as sp
import numpy as np
from sympy import parse_expr, Eq, Function, symbols, diff, sympify
from scipy.integrate import solve_ivp


def get_R(arr):
    n = len(arr)
    exprs = list()
    a, b, t = sp.symbols("a b t")
    arr_a = list(Function(("x" + str(i + 1)))(a, t) for i in range(n))
    arr_b = list(Function(("x" + str(i + 1)))(a, t) for i in range(n))
    for eq in arr:
        left, right = eq.split('=')
        expr = sympify(left) - sympify(right)
        exprs.append(expr)
    #print(arr_a)
    R_x = list([[diff(exppr, x) for x in arr_a] for exppr in exprs])
    R_y = list([[diff(exppr, x) for x in arr_a] for exppr in exprs])
    return R_x





def find_x(system, a, b, p):
    n = len(system)
    variables = sp.symbols(" ".join(f"x{i + 1}" for i in range(n)))
    p_sym = sp.symbols(" ".join(f"p{i + 1}" for i in range(n)))
    system_for_solve = sp.Matrix(system)
    f = sp.lambdify(variables, system_for_solve, 'numpy')
    t_span = (a, b)
    t_eval = np.array([a, b])
    def ode_system(t, y):
        result = f(*y)
        return np.array(result).flatten()

    return solve_ivp(ode_system, t_span, t_eval=t_eval, y0=p).y.T


def get_A(system_f):
    n = len(system)
    variables = sp.symbols(" ".join(f"x{i + 1}" for i in range(n)))
    return sp.Matrix([system_f]).jacobian(variables)


def find_X(system_f, a, b):
    n = len(system)
    variables = sp.symbols(" ".join(f"x{i + 1}" for i in range(n)))
    A = get_A(system_f)
    X0 = np.eye(n)

    def f(t, y):
        nn = A.shape[0]
        Y = y.reshape(nn, nn)
        return (A @ Y).flatten()


    x0_flat = X0.flatten()
    t_span = (a, b)
    t_eval = np.linspace(a, b, 2)
    solution = solve_ivp(f, t_span, x0_flat, t_eval=t_eval)
    print(solution.y.T)
    return solution.y.T


def get_a_b_R(arr):
    set_a_b = set()
    arr_for_R = list()
    for st in arr:
        br_l_i = 0
        f = False
        arr_for_R.append("")
        for i, sym in enumerate(st):
            if not f:
                arr_for_R[-1] += sym
            if (sym == '(') and (i != 0) and (st[i - 1].isdigit()):
                br_l_i = i
                f = True
            elif sym == ')' and f:
                num = float(st[br_l_i + 1:i])
                set_a_b.add(num)
                arr_for_R[-1] += str(num) + ")"
                f = False
    a, b = sorted(list(set_a_b))
    return a, b, arr_for_R


#arr = ["x1(a)+x(b)=0", "x2(b) * x2(a)=7", "x3(a)=0", "x4(b)=5"]
#a, b = 0., 2
#arr = ["x3", "x4", "-x1*(x1^2+x2^2)^(-3/2)", "-x2*(x1^2+x2^2)^(-3/2)"]
#n = len(arr)
#p0 = np.array(np.random.randn(n))
#system = get_f(arr)
#print(find_x(system, a, b, p0))
#X_a, X_b = find_X(system, a, b, p0)
#print(R(arr))

#arr = ["x1(1) - (43)=x(2)", "(4)-x2(3)=0"]
#print(get_a_b_R(arr))\
n = 5

print(f"{n:.{n}f}")