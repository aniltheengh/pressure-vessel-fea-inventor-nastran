#!/usr/bin/env python3
"""Self-tests for the tools. Run: python3 tools/test_tools.py  (no dependencies)."""
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import linearize as L          # noqa: E402
import pv_handcalc as H        # noqa: E402
import convergence as C        # noqa: E402

fails = 0


def check(name, got, exp, tol):
    global fails
    ok = abs(got - exp) <= tol * max(1.0, abs(exp))
    print(f"{'PASS' if ok else 'FAIL'}  {name}: got {got:.5g}, expected {exp:.5g}")
    fails += 0 if ok else 1


# 1. Linearization vs exact Lame (ri=100, ro=150, P=20)
subprocess.run([sys.executable, os.path.join(HERE, "examples", "make_lame_examples.py")],
               check=True, capture_output=True)
for fname, frame, tdir in (("lame_scl_local.csv", "local", None),
                           ("lame_scl_global_rot30.csv", "global", [-0.5, math.sqrt(3) / 2, 0])):
    xs, comps, _ = L.read_csv(os.path.join(HERE, "examples", fname), frame, tdir)
    r = L.linearize(xs, comps)
    check(f"{fname} membrane hoop", r["membrane"][1], 40.0, 1e-3)
    check(f"{fname} membrane radial", r["membrane"][0], -8.0, 2e-3)
    check(f"{fname} membrane axial", r["membrane"][2], 16.0, 1e-6)
    check(f"{fname} bending hoop", r["bending_inside"][1], 9.6781, 2e-3)

# 2. Principal stresses / von Mises of a known tensor
c = [100.0, 0, 0, 0, 0, 0]
check("von Mises uniaxial", L.von_mises(c), 100.0, 1e-12)
c = [50.0, -50.0, 0, 0, 0, 0]
check("Tresca pure shear-equivalent", L.tresca(c), 100.0, 1e-12)
c = [10, 20, 30, 5, 6, 7]
e = L.principal(c)
check("principal sum = trace", sum(e), 60.0, 1e-9)

# 3. Hand calcs for the sample vessel
cfg = json.load(open(os.path.join(HERE, "examples", "sample_vessel.json")))
out = H.run(cfg)
check("UG-27 t circ", out["shell"]["t_req_circ"], 1.5 * 503 / (138 - 0.9), 1e-12)
check("MAWP", out["shell"]["MAWP"], 138 * 8.7 / (503 + 0.6 * 8.7), 1e-12)
check("2:1 head t", out["heads_t_required"]["ellipsoidal_2to1"], 1.5 * 1006 / (276 - 0.3), 1e-12)
check("Lame mean hoop = P ri / t", out["lame_corroded"]["hoop_mean"], 1.5 * 503 / 8.7, 1e-12)
check("Q0 = P/(8 beta)", out["hemi_cyl_junction"]["Q0"],
      1.5 / (8 * out["hemi_cyl_junction"]["beta"]), 1e-12)
check("VIII-1 hydro", out["hydrotest_MPa"]["ASME VIII-1 UG-99(b)"], 1.95, 1e-12)
check("JIS B 8265 hydro", out["hydrotest_MPa"]["JIS B 8265 8.5"], 2.25, 1e-12)

# 4. Convergence: exact 2nd-order data must give p = 2 and exact extrapolation
p, _ = C.observed_order(1, 2, 4, 100 - 1 * 1, 100 - 1 * 4, 100 - 1 * 16)
check("observed order p=2", p, 2.0, 1e-9)

print("\nALL TESTS PASSED" if fails == 0 else f"\n{fails} TEST(S) FAILED")
sys.exit(1 if fails else 0)
