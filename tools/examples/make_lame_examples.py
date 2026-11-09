#!/usr/bin/env python3
"""Generate SCL example CSVs from the exact Lame thick-cylinder solution so that
linearize.py can be checked against closed-form answers.
Cylinder: ri = 100 mm, ro = 150 mm, P = 20 MPa internal, closed ends.
Exact membrane hoop = P*ri/t = 40.000 MPa; exact membrane radial = -P*ri/(ro+ri)... see README."""
import csv, math, os
here = os.path.dirname(os.path.abspath(__file__))
P, ri, ro, N = 20.0, 100.0, 150.0, 21
A = P * ri**2 / (ro**2 - ri**2)
B = P * ri**2 * ro**2 / (ro**2 - ri**2)
rows = []
for i in range(N):
    r = ri + (ro - ri) * i / (N - 1)
    s_t = A + B / r**2      # hoop
    s_n = A - B / r**2      # radial (along SCL)
    s_h = A                 # axial (closed ends)
    rows.append((r, s_n, s_t, s_h))
with open(os.path.join(here, "lame_scl_local.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["s", "Snn", "Stt", "Shh", "Snt", "Sth", "Shn"])
    for r, sn, st, sh in rows:
        w.writerow([f"{r - ri:.6f}", f"{sn:.6f}", f"{st:.6f}", f"{sh:.6f}", 0, 0, 0])
# same SCL in a global frame: cylinder axis = z, SCL at 30 deg from x axis
th = math.radians(30)
n = (math.cos(th), math.sin(th), 0.0); t = (-math.sin(th), math.cos(th), 0.0)
with open(os.path.join(here, "lame_scl_global_rot30.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["x", "y", "z", "Sxx", "Syy", "Szz", "Sxy", "Syz", "Szx"])
    for r, sn, st, sh in rows:
        sxx = sn * n[0]**2 + st * t[0]**2
        syy = sn * n[1]**2 + st * t[1]**2
        sxy = sn * n[0] * n[1] + st * t[0] * t[1]
        w.writerow([f"{r*n[0]:.6f}", f"{r*n[1]:.6f}", "250.0", f"{sxx:.6f}", f"{syy:.6f}",
                    f"{sh:.6f}", f"{sxy:.6f}", 0, 0])
# exact reference values
t_w = ro - ri
mem_hoop = P * ri / t_w
mem_rad = (1 / t_w) * (A * t_w + B * (1 / ro - 1 / ri))   # int (A - B/r^2) dr = A t + B(1/ro - 1/ri)
f = lambda r: (A + B / r**2) * (t_w / 2 - (r - ri))
# bending hoop exact via fine Simpson
M = 20000; hh = t_w / M
I = f(ri) + f(ro) + sum((4 if k % 2 else 2) * f(ri + k * hh) for k in range(1, M))
bend_hoop = 6 / t_w**2 * I * hh / 3
print(f"exact: membrane hoop = {mem_hoop:.4f}, membrane radial = {mem_rad:.4f}, "
      f"membrane axial = {A:.4f}, bending hoop (inside) = {bend_hoop:.4f} MPa")
