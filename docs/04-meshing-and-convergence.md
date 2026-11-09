# 04 — Meshing and Convergence

> A stress result is only reportable if you have shown that refining the mesh no longer changes it meaningfully. NAFEMS calls this the single most important check an analyst can do ([NAFEMS: the importance of mesh convergence](https://www.nafems.org/publications/knowledge-base/the-importance-of-mesh-convergence-part-1/)).

Tool: [`tools/convergence.py`](../tools/convergence.py) — Richardson extrapolation + GCI.

---

## 1. What converges and what never will

| Quantity | Converges? | Use for acceptance? |
|---|---|---|
| Displacements, reactions | Yes, fast | Sanity check |
| Membrane stress in plain shell | Yes, fast | Verification vs hand calc |
| **Linearized Pm, PL, Pm+Pb on an SCL** | Yes (integrals smooth out local error) | **Yes — this is what ASME elastic limits use** |
| Peak stress at a **finite** fillet radius | Yes, but needs fine mesh (≥ 4–8 elements around the fillet arc) | Fatigue (with care) |
| Stress at a **sharp re-entrant corner** (zero radius) | **No — singular, grows without bound** | No |
| Stress at a **point load / point constraint / edge constraint** | **No — singular** | No |
| Stress at a **fixed-face edge** | No (artificial singularity) | No |
| Contact pressure at a sharp contact edge | No | No |

Theory: at a re-entrant corner of angle $\alpha$ (> 180° material angle), elastic stress varies as $\sigma \propto r^{\lambda - 1}$ with $\lambda < 1$ (Williams 1952). At a 90° re-entrant corner (270° material) $\lambda \approx 0.545$ → $\sigma \propto r^{-0.455}$. Halving the element size raises the corner stress by $2^{0.455} \approx 1.37$ — forever.

**Practical rule:** if you see the hot-spot value rise by roughly the same percentage at every refinement, it's a singularity. The [`convergence.py`](../tools/convergence.py) tool flags observed order $p < 0.5$ as a likely singularity.

---

## 2. Convergence study procedure (pressure vessel)

1. **Pick the quantities** you will report: e.g. Pm+Pb on SCL-1 (nozzle junction), Pm on SCL-2 (plain shell), max displacement. Not "max von Mises anywhere".
2. **Mesh 1**: your best-guess mesh (from [03 §8.1](03-inventor-nastran-model-setup.md#81-starting-sizes-then-prove-by-convergence)).
3. **Mesh 2 and 3**: refine **in the evaluation region** by a constant ratio $r = h_{coarse}/h_{fine} \ge 1.3$ (2 is ideal). Global refinement is not necessary — local refinement where gradients are, plus a smooth transition.
4. **Keep everything else identical**: geometry, loads, constraints, SCL end-point coordinates (type them in, don't pick), element order.
5. **Tabulate**: element size $h$, number of nodes, value.
6. **Compute** observed order $p$, extrapolated value, GCI (below).
7. **Accept** when change between the two finest meshes ≤ ~2–5 % (company criterion) **and** GCI ≤ target **and** $p$ is plausible (0.8–3 for parabolic tet stresses).
8. **Report** the finest-mesh value (or the extrapolated, if you state it) ± GCI.

In Inventor Nastran:
- Use *Mesh Model > Add Mesh Control* on the faces/edges at the SCL; change only that size between runs.
- Duplicate the analysis (right-click *Analysis > Duplicate*) for each mesh so results stay side by side.
- Fix SCL points by **coordinates** in the Stress Linearization dialog (start, end, reference point) so the line is identical each run.

---

## 3. Formulas (Roache GCI method, as used in ASME V&V 20)

Three meshes $h_1 < h_2 < h_3$, results $f_1, f_2, f_3$:

$$r_{21} = h_2/h_1, \quad r_{32} = h_3/h_2, \quad \varepsilon_{21} = f_2 - f_1, \quad \varepsilon_{32} = f_3 - f_2$$

Observed order (constant $r$):
$$p = \frac{\ln(\varepsilon_{32}/\varepsilon_{21})}{\ln r}$$
(non-constant $r$: iterate $p = \frac{1}{\ln r_{21}}\left|\ln|\varepsilon_{32}/\varepsilon_{21}| + q(p)\right|$, $q(p) = \ln\frac{r_{21}^p - s}{r_{32}^p - s}$, $s = \operatorname{sign}(\varepsilon_{32}/\varepsilon_{21})$)

Richardson extrapolation:
$$f_{ext} = \frac{r_{21}^p f_1 - f_2}{r_{21}^p - 1}$$

Grid Convergence Index (fine mesh, safety factor $F_s$ = 1.25 for 3+ meshes):
$$GCI_{21} = \frac{F_s\,|(f_1 - f_2)/f_1|}{r_{21}^p - 1}$$

Asymptotic-range check: $GCI_{32} / (r_{21}^p\,GCI_{21}) \approx 1$.

If $\varepsilon_{32}/\varepsilon_{21} < 0$ → **oscillatory** convergence; extrapolation invalid; add meshes.

---

## 4. Worked example — nozzle junction SCL

Linearized Pm+Pb (von Mises) at the N1–shell junction SCL, solid parabolic tets, local size varied:

| Mesh | Local size $h$ (mm) | Elements through 8.7 mm wall | Pm+Pb (MPa) | Change |
|---|---|---|---|---|
| M4 | 20 | <1 | 101.2 | — |
| M3 | 10 | ~1 | 108.9 | +7.6 % |
| M2 | 5 | ~2 | 111.0 | +1.9 % |
| M1 | 2.5 | ~3.5 | 111.6 | +0.5 % |

```text
$ python3 tools/convergence.py tools/examples/convergence_example.csv
Observed order of convergence p = 1.807
Richardson extrapolated value  = 111.84
Fine-mesh error estimate       = 0.21 %
GCI_fine (Fs = 1.25)           = 0.27 %  -> report as 111.6 +/- 0.3
Asymptotic range ratio         = 1.005  (close to 1.0 = in asymptotic range)
Target GCI <= 2.0 %       : MET
```

Conclusion: converged; report 111.6 MPa (GCI 0.3 %). Note that the M3 mesh (1 element through thickness) was **7 % low — unconservative.** Coarse meshes under-predict stress.

### Counter-example — singular corner (unfilleted nozzle–shell intersection, peak von Mises)

| $h$ (mm) | Peak (MPa) |
|---|---|
| 8 | 180 |
| 4 | 231 |
| 2 | 296 |
| 1 | 379 |

```text
$ python3 tools/convergence.py tools/examples/convergence_singularity.csv
Observed order of convergence p = 0.353
GCI_fine (Fs = 1.25)           = 98.85 %
DIAGNOSIS: p < 0.5 -> value is probably at a SINGULARITY ...
```

Each halving adds ~22–28 % — classic singularity ($2^{0.36} \approx 1.28$). **Do not report this number.** Instead: linearize on an SCL a short distance from the corner (membrane + bending converge), or model the real weld fillet, or use a structural-stress method for fatigue.

---

## 5. Dealing with singularities — decision table

| Cause | Fix |
|---|---|
| Sharp corner in CAD (nozzle-shell intersection without weld) | Add the **weld fillet** as modelled geometry (actual leg size per drawing); for fatigue, model weld toe radius or use hot-spot / structural stress (VIII-2 5.5.5) |
| Point constraint (3-2-1) | Move away from evaluation regions; ignore local peak |
| Fixed face edge | Replace with realistic support; or move evaluation ≥ $2.5\sqrt{Rt}$ away |
| Point force / edge force | Distribute over a realistic area (*Remote Force* or connector) |
| Contact edge | Accept as local; check contact pressure distribution, not peak |
| Bonded contact edge between dissimilar meshes | Match mesh sizes; or merge bodies |

ASME VIII-2 explicitly classifies stress at sharp local discontinuities as **peak (F)** for fatigue; primary/secondary checks use **linearized** values on SCLs, which by definition exclude the nonlinear (peak) part of the through-wall distribution (Annex 5-A). That is why a singular peak does not invalidate the primary stress assessment, as long as SCLs are placed correctly (see [05](05-stress-linearization-and-classification.md)).

---

## 6. Element quality

Inventor Nastran solver warnings that mean "bad elements" (from the Autodesk KB, [E5004 article](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Error-FATAL-ERROR-E5004-STIFFNESS-MATRIX-SINGULAR-OR-NON-POSITIVE-DEFINITE-when-running-an-analysis-in-Nastran-In-CAD.html)):

| Warning | Meaning |
|---|---|
| G3005 | Grids collocated on element (two nodes at the same place) |
| G3009 | Element has singular geometry (collapsed/distorted) |
| G3016 / G3017 | Edge-point (mid-side node) ratio greater / less than limit — mid-side node badly placed |
| G3051 | Secondary grid position modified on contact element (interference being removed → can distort) |
| T2217 | Element orientation problem (collapsed / inverted / incorrectly defined) |

General quality metrics (common guidance, e.g. NAFEMS "How to" books and solver docs; thresholds vary by code — treat as targets):

| Metric | Target for parabolic tets in stress regions |
|---|---|
| Aspect ratio | < 5 (accept < 10 away from evaluation areas) |
| Jacobian ratio (at Gauss points) | > 0.6 (never negative) |
| Mid-side node deviation (edge-point ratio) | near 0.5 of edge; flagged by G3016/G3017 |
| Dihedral / face angles | avoid < 5° or > 170° |
| Size transition | growth rate ≤ 1.2–1.5 between neighbours |

Use *Mesh Model > Check Quality for all Meshes* and look at where the poor elements are. A few bad elements far from the SCLs are usually harmless; **any bad element on an SCL is not**.

---

## 7. Shell vs solid convergence specifics

**Shells**
- Converge with element size relative to $\sqrt{Rt}$ (bending wavelength). Rule of thumb: element ≤ $0.1$–$0.2\sqrt{Rt}$ in the discontinuity zone.
- Stresses at intersection lines are mesh-dependent (mid-surface overlap). Read stresses at $0.5t$–$1.0t$ from the intersection or use structural-stress extrapolation.
- Inventor recommends **linear** shells (CQUADR/CTRIAR). Use quads where possible (mapped regions on cylinders).

**Solids (10-node tets)**
- ≥ 3 elements through thickness on SCLs (more for steep bending, e.g. torispherical knuckle).
- Linear 4-node tets: very stiff in bending, under-predict stress; do not use for code assessment.
- Check linearized values, not nodal peaks, for convergence.

---

## 8. Convergence in nonlinear / buckling analyses

| Analysis | What to converge |
|---|---|
| Linear buckling | First eigenvalue (load factor); also check mode shape doesn't change |
| Elastic–plastic collapse (5.2.4) | Collapse load factor vs mesh; equivalent plastic strain at critical location (local strain criterion 5.3.3) |
| Limit load (5.2.3) | Limit load factor |
| Fatigue | Peak/structural stress range at the hot spot |

Load-step convergence (Newton iterations) is a different thing from mesh convergence. Both must be shown for nonlinear runs.

---

## 9. What to write in the report

| Item | Example |
|---|---|
| Quantities studied | Pm+Pb at SCL-1, Pm at SCL-2, max radial displacement |
| Meshes | 4 meshes, local size 20/10/5/2.5 mm at N1, global 15 mm |
| Table | as §4 |
| Result | p = 1.81, GCI = 0.27 % on finest mesh |
| Conclusion | Mesh M1 used for all results; values converged within 0.3 % |
| Singularities | Peak at unfilleted corner (modelled without weld) identified as singular (p = 0.35) and not used for acceptance |

Next: [05 — Stress linearization and classification](05-stress-linearization-and-classification.md).
