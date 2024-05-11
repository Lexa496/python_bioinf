import numpy as np

def solve_ode(start, end, h, max_calls, eps, fs, initial_conditions):
    t = start
    v = np.array(initial_conditions)
    kounter = [0]
    print(f"{t_0:13.6f}{h:13.6f}{0:13d}{0:13d}", *[f"{x:12.6f}" for x in v])

    def heun_step(t, v, h):
        k1 = fs(t, v, kounter)
        k2 = fs(t + h, v + h * k1, kounter)
        return v + (h / 2) * (k1 + k2)

    while t < end and kounter[0] < max_calls:
        k1 = fs(t, v, kounter)
        k2 = fs(t + h, v + h * k1, kounter)
        v1 = v + (h / 2) * (k1 + k2)

        k2 = fs(t + h/2, v + h/2 * k1, kounter)
        v2 = v + (h / 4) * (k1 + k2)
 
        v2 = heun_step(t + h/2, v2, h/2)

        r = np.linalg.norm(v2 - v1) / 3

        if r > eps:
            h /= 2

        elif r < eps / 64:
            h *= 2

        if r < eps:
            t += h
            v = v1
            print(f"{t:13.6f}{h:13.6f}{r:13.5e}{kounter[0]:13d}", *[f"{x:12.6f}" for x in v])


t_0 = float(input())
T = float(input())
h_0 = float(input())
N_x = int(input())
eps = float(input())
n = int(input())
function_code = []
for i in range(n+3):
    line = input()
    function_code.append(line)

function_definition = "\n".join(function_code)
exec(function_definition)

input_string = input()
initial_conditions = [float(x) for x in input_string.split()]

solve_ode(t_0, T, h_0, N_x, eps, fs, initial_conditions)