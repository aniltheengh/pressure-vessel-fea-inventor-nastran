#!/usr/bin/env python3
"""
convergence.py - mesh convergence check with Richardson extrapolation and the
Grid Convergence Index (GCI, Roache 1994/1998; ASME V&V 20 uses the same idea).

INPUT CSV columns: h, value  (h = representative element size, any order; >= 3 rows)
  Use a quantity that SHOULD converge: linearized Pm / Pm+Pb on an SCL, hoop stress in a
  plain shell region, displacement, reaction. NOT a peak at a sharp corner/point load
  (a singularity never converges - the "observed order" will be ~0 or negative).

Method (three finest meshes, h1 < h2 < h3, values f1, f2, f3):
  r21 = h2/h1, r32 = h3/h2
  observed order p solved iteratively (non-constant refinement ratio supported):
      p = |ln|e32/e21| + q(p)| / ln(r21),  q(p) = ln((r21^p - s)/(r32^p - s)), s = sign(e32/e21)
  extrapolated f_ext = (r21^p f1 - f2) / (r21^p - 1)
  GCI_fine = Fs * |(f1 - f2)/f1| / (r21^p - 1),  Fs = 1.25
  asymptotic check: GCI_32 / (r21^p * GCI_21) ~ 1.0
Usage: python3 convergence.py examples/convergence_example.csv [--target-pct 2]
"""
import argparse
import csv
import math


def observed_order(h1, h2, h3, f1, f2, f3, iters=100):
    e21, e32 = f2 - f1, f3 - f2
    if e21 == 0:
        return float("inf"), "f1 == f2 (converged or insensitive)"
    ratio = e32 / e21
    if ratio <= 0:
        return None, "oscillatory convergence (sign change) - refine further or use more meshes"
    r21, r32 = h2 / h1, h3 / h2
    s = 1.0
    p = abs(math.log(abs(ratio))) / math.log(r21)
    for _ in range(iters):
        try:
            q = math.log((r21 ** p - s) / (r32 ** p - s))
        except ValueError:
            break
        p_new = abs(math.log(abs(ratio)) + q) / math.log(r21)
        if abs(p_new - p) < 1e-10:
            p = p_new
            break
        p = p_new
    return p, "monotonic"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--target-pct", type=float, default=2.0, help="acceptable GCI in percent")
    a = ap.parse_args()
    with open(a.csv, newline="") as f:
        data = sorted(((float(r["h"]), float(r["value"])) for r in csv.DictReader(f)), key=lambda x: x[0])
    if len(data) < 3:
        raise SystemExit("need >= 3 meshes")
    print("Mesh table (fine -> coarse):")
    print(f"{'h':>10} {'value':>12} {'change vs next finer':>22}")
    for i, (h, v) in enumerate(data):
        ch = "" if i == 0 else f"{100 * (v - data[i - 1][1]) / data[i - 1][1]:+.2f} %"
        print(f"{h:10.4g} {v:12.5g} {ch:>22}")
    (h1, f1), (h2, f2), (h3, f3) = data[:3]
    p, kind = observed_order(h1, h2, h3, f1, f2, f3)
    print(f"\nUsing three finest meshes: h = {h1}, {h2}, {h3}")
    print(f"Convergence type: {kind}")
    if p is None or p == float("inf"):
        return
    print(f"Observed order of convergence p = {p:.3f}"
          "  (expect ~1-2 for stresses with parabolic elements; p << 1 suggests a singularity)")
    r21, r32 = h2 / h1, h3 / h2
    f_ext = (r21 ** p * f1 - f2) / (r21 ** p - 1)
    gci21 = 1.25 * abs((f1 - f2) / f1) / (r21 ** p - 1)
    gci32 = 1.25 * abs((f2 - f3) / f2) / (r32 ** p - 1)
    asym = gci32 / (r21 ** p * gci21)
    print(f"Richardson extrapolated value  = {f_ext:.5g}")
    print(f"Fine-mesh error estimate       = {100 * abs(f_ext - f1) / abs(f_ext):.2f} %")
    print(f"GCI_fine (Fs = 1.25)           = {100 * gci21:.2f} %  -> report as {f1:.4g} +/- {abs(f1) * gci21:.3g}")
    print(f"Asymptotic range ratio         = {asym:.3f}  (close to 1.0 = in asymptotic range)")
    ok = 100 * gci21 <= a.target_pct
    print(f"Target GCI <= {a.target_pct} %       : {'MET' if ok else 'NOT MET'}")
    if p < 0.5:
        print("DIAGNOSIS: p < 0.5 -> value is probably at a SINGULARITY (sharp corner, point load,\n"
              "  point/edge constraint). Refining will never converge it. Move the SCL away, model the\n"
              "  real fillet/weld radius, or evaluate it as a peak (fatigue) quantity only.")
    elif not ok:
        print("ACTION: refine locally at the evaluation location and add a 4th mesh.")


if __name__ == "__main__":
    main()
