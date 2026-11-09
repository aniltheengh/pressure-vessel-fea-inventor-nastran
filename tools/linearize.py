#!/usr/bin/env python3
"""
linearize.py - stress linearization along a Stress Classification Line (SCL).

Follows the integral method described in ASME BPVC Section VIII Division 2,
Part 5 Annex 5-A (check your edition):
  membrane  s_ij,m = (1/t) * Int_0^t s_ij dx
  bending   s_ij,b = (6/t^2) * Int_0^t s_ij (t/2 - x) dx    (value at x = 0, inside end;
                                                                 opposite sign at x = t)
  peak      s_ij,F = s_ij(total) - s_ij,m - s_ij,b              (at each end)
By default bending is computed only for the two normal components tangent to the wall
(hoop 'tt' and meridional 'hh'), which is the Annex 5-A recommendation; use
--bend-all to compute bending for every component (some analysts and tools do this).

Stress along the SCL is treated as piecewise linear between the points you give,
and integrals are exact for that assumption. Points can be unevenly spaced.

INPUT CSV (header row required), one row per point from the INSIDE surface to the
OUTSIDE surface (order is checked by distance):
  Local frame (--frame local, default):
     s, Snn, Stt, Shh, Snt, Sth, Shn
     s = distance along SCL from the first point (mm)
     n = along the SCL (through-thickness), t = hoop / in-plane direction 1,
     h = meridional / in-plane direction 2
     (These are the N, T, H components that the Inventor Nastran Stress Linearization
      dialog exports to CSV; check its column names and map them.)
  Global frame (--frame global):
     x, y, z, Sxx, Syy, Szz, Sxy, Syz, Szx
     plus --tdir tx ty tz   (a vector in the hoop direction; it is orthogonalised
                             against the SCL direction automatically)
     (Typical source: Inventor Nastran "Nodes > Query" or a probe/CSV export of nodal
      stresses along a split edge.)

OUTPUT: membrane, bending, peak tensors; von Mises and Tresca (stress intensity) of
  membrane, membrane+bending and total at both ends; optional check against limits.

Examples:
  python3 linearize.py examples/lame_scl_local.csv
  python3 linearize.py examples/lame_scl_global_rot30.csv --frame global --tdir -0.5 0.8660254 0
  python3 linearize.py examples/lame_scl_local.csv --S 138 --category PL
"""
import argparse
import csv
import math
import sys

LOCAL = ["Snn", "Stt", "Shh", "Snt", "Sth", "Shn"]
GLOBAL = ["Sxx", "Syy", "Szz", "Sxy", "Syz", "Szx"]


def unit(v):
    m = math.sqrt(sum(c * c for c in v))
    if m == 0:
        raise ValueError("zero-length vector")
    return [c / m for c in v]


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def tensor(c):
    """c = [s11, s22, s33, s12, s23, s31] -> 3x3."""
    s11, s22, s33, s12, s23, s31 = c
    return [[s11, s12, s31], [s12, s22, s23], [s31, s23, s33]]


def rotate_to_local(c_global, n, t, h):
    """sigma_local_ab = e_a . sigma . e_b with e = (n, t, h)."""
    S = tensor(c_global)
    def comp(a, b):
        return sum(a[i] * S[i][j] * b[j] for i in range(3) for j in range(3))
    return [comp(n, n), comp(t, t), comp(h, h), comp(n, t), comp(t, h), comp(h, n)]


def principal(c):
    """Principal stresses of symmetric tensor (closed-form, trigonometric)."""
    S = tensor(c)
    I1 = S[0][0] + S[1][1] + S[2][2]
    p1 = S[0][1] ** 2 + S[0][2] ** 2 + S[1][2] ** 2
    if p1 < 1e-30 * max(1.0, I1 * I1):
        e = sorted([S[0][0], S[1][1], S[2][2]], reverse=True)
        return e
    q = I1 / 3
    p2 = sum((S[i][i] - q) ** 2 for i in range(3)) + 2 * p1
    p = math.sqrt(p2 / 6)
    B = [[(S[i][j] - (q if i == j else 0)) / p for j in range(3)] for i in range(3)]
    detB = (B[0][0] * (B[1][1] * B[2][2] - B[1][2] * B[2][1])
            - B[0][1] * (B[1][0] * B[2][2] - B[1][2] * B[2][0])
            + B[0][2] * (B[1][0] * B[2][1] - B[1][1] * B[2][0]))
    r = max(-1.0, min(1.0, detB / 2))
    phi = math.acos(r) / 3
    e1 = q + 2 * p * math.cos(phi)
    e3 = q + 2 * p * math.cos(phi + 2 * math.pi / 3)
    e2 = 3 * q - e1 - e3
    return sorted([e1, e2, e3], reverse=True)


def von_mises(c):
    s11, s22, s33, s12, s23, s31 = c
    return math.sqrt(0.5 * ((s11 - s22) ** 2 + (s22 - s33) ** 2 + (s33 - s11) ** 2)
                     + 3 * (s12 ** 2 + s23 ** 2 + s31 ** 2))


def tresca(c):
    e = principal(c)
    return e[0] - e[2]


def integrate(xs, fs, weight=None):
    """Exact integral of piecewise-linear f (optionally times linear weight w(x))."""
    total = 0.0
    for i in range(len(xs) - 1):
        h = xs[i + 1] - xs[i]
        f0, f1 = fs[i], fs[i + 1]
        if weight is None:
            total += 0.5 * h * (f0 + f1)
        else:
            g0, g1 = weight(xs[i]), weight(xs[i + 1])
            total += h / 6.0 * (2 * f0 * g0 + f0 * g1 + f1 * g0 + 2 * f1 * g1)
    return total


def read_csv(path, frame, tdir):
    with open(path, newline="") as f:
        rows = [r for r in csv.DictReader(f) if any(v.strip() for v in r.values() if v)]
    if len(rows) < 3:
        raise SystemExit("need at least 3 points along the SCL (use 5-11 or more)")
    if frame == "local":
        xs = [float(r["s"]) for r in rows]
        comps = [[float(r[k]) for k in LOCAL] for r in rows]
        info = "local frame (n along SCL, t hoop, h meridional)"
    else:
        pts = [[float(r["x"]), float(r["y"]), float(r["z"])] for r in rows]
        n = unit([pts[-1][i] - pts[0][i] for i in range(3)])
        if tdir is None:
            raise SystemExit("--frame global needs --tdir (hoop direction vector)")
        t = [tdir[i] - dot(tdir, n) * n[i] for i in range(3)]
        t = unit(t)
        h = cross(n, t)
        xs = [math.sqrt(sum((p[i] - pts[0][i]) ** 2 for i in range(3))) for p in pts]
        # check collinearity
        L = xs[-1]
        for p, s in zip(pts, xs):
            off = [p[i] - pts[0][i] - s * n[i] for i in range(3)]
            if math.sqrt(dot(off, off)) > 1e-3 * L + 1e-9:
                print(f"WARNING: point {p} is {math.sqrt(dot(off, off)):.4g} mm off the straight SCL",
                      file=sys.stderr)
        comps = [rotate_to_local([float(r[k]) for k in GLOBAL], n, t, h) for r in rows]
        info = (f"global -> local: n={[round(v, 4) for v in n]}, t={[round(v, 4) for v in t]}, "
                f"h={[round(v, 4) for v in h]}")
    for a, b in zip(xs, xs[1:]):
        if b <= a:
            raise SystemExit("points must be ordered from inside to outside with increasing distance")
    return xs, comps, info


def linearize(xs, comps, bend_all=False):
    x0 = xs[0]
    xs = [x - x0 for x in xs]
    t = xs[-1]
    mem, ben = [], []
    for k in range(6):
        f = [c[k] for c in comps]
        m = integrate(xs, f) / t
        bendable = bend_all or k in (1, 2)  # Stt, Shh
        b = 6.0 / t ** 2 * integrate(xs, f, weight=lambda x: t / 2 - x) if bendable else 0.0
        mem.append(m)
        ben.append(b)
    res = {"thickness": t, "membrane": mem, "bending_inside": ben,
           "bending_outside": [-b for b in ben]}
    for end, idx, bsign in (("inside", 0, 1), ("outside", -1, -1)):
        tot = comps[idx]
        mb = [mem[k] + bsign * ben[k] for k in range(6)]
        peak = [tot[k] - mb[k] for k in range(6)]
        res[end] = {"total": tot, "m_plus_b": mb, "peak": peak}
    return res


def report(res, info, S=None, category=None, sps=None, out=sys.stdout):
    w = out.write
    names = ["nn", "tt", "hh", "nt", "th", "hn"]
    w(f"SCL length (wall thickness used) t = {res['thickness']:.4f} mm\n")
    w(f"Frame: {info}\n\n")
    w("Component        " + "".join(f"{n:>11}" for n in names) + "\n")
    def row(label, c):
        w(f"{label:<17}" + "".join(f"{v:11.3f}" for v in c) + "\n")
    row("Membrane", res["membrane"])
    row("Bending (inside)", res["bending_inside"])
    for end in ("inside", "outside"):
        row(f"Total {end}", res[end]["total"])
        row(f"M+B {end}", res[end]["m_plus_b"])
        row(f"Peak {end}", res[end]["peak"])
    w("\nEquivalent stresses (MPa)       von Mises     Tresca(SI)\n")
    vm_m, tr_m = von_mises(res["membrane"]), tresca(res["membrane"])
    w(f"  Membrane                      {vm_m:10.3f}   {tr_m:10.3f}\n")
    worst_mb = 0.0
    for end in ("inside", "outside"):
        vm, tr = von_mises(res[end]["m_plus_b"]), tresca(res[end]["m_plus_b"])
        worst_mb = max(worst_mb, vm)
        w(f"  Membrane+Bending ({end:<7})    {vm:10.3f}   {tr:10.3f}\n")
    for end in ("inside", "outside"):
        vm, tr = von_mises(res[end]["total"]), tresca(res[end]["total"])
        w(f"  Total            ({end:<7})    {vm:10.3f}   {tr:10.3f}\n")
    if S:
        w("\nCheck vs ASME VIII-2 5.2.2.4 elastic limits (von Mises; confirm edition):\n")
        if category in (None, "Pm"):
            w(f"  Pm      = {vm_m:8.2f} <= S    = {S:8.2f}  -> {'PASS' if vm_m <= S else 'FAIL'}"
              f"  (ratio {vm_m / S:.3f})\n")
        if category in (None, "PL"):
            w(f"  PL      = {vm_m:8.2f} <= 1.5S = {1.5 * S:8.2f}  -> {'PASS' if vm_m <= 1.5 * S else 'FAIL'}"
              f"  (ratio {vm_m / (1.5 * S):.3f})\n")
        if category in (None, "Pm", "PL"):
            w(f"  P(L)+Pb = {worst_mb:8.2f} <= 1.5S = {1.5 * S:8.2f}  -> "
              f"{'PASS' if worst_mb <= 1.5 * S else 'FAIL'}  (ratio {worst_mb / (1.5 * S):.3f})\n")
        if category == "PQ":
            lim = sps if sps else 3 * S
            w(f"  P+Q range = {worst_mb:8.2f} <= SPS = {lim:8.2f}  -> "
              f"{'PASS' if worst_mb <= lim else 'FAIL'}  (ratio {worst_mb / lim:.3f})\n"
              "  NOTE: P+Q must be evaluated as a RANGE between two load states.\n")
        w("  Classification (Pm vs PL vs Q) is YOUR engineering decision, not the script's.\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--frame", choices=["local", "global"], default="local")
    ap.add_argument("--tdir", nargs=3, type=float, help="hoop direction vector for --frame global")
    ap.add_argument("--bend-all", action="store_true", help="compute bending for all 6 components")
    ap.add_argument("--S", type=float, help="allowable stress S (MPa) to print limit checks")
    ap.add_argument("--category", choices=["Pm", "PL", "PQ"], help="what this SCL is classified as")
    ap.add_argument("--sps", type=float, help="SPS limit for P+Q range (default 3S)")
    a = ap.parse_args()
    xs, comps, info = read_csv(a.csv, a.frame, a.tdir)
    res = linearize(xs, comps, a.bend_all)
    report(res, info, a.S, a.category, a.sps)


if __name__ == "__main__":
    main()
