# 05 — Stress Linearization and Classification

> Elastic FEA gives you the **total** stress at every point. ASME VIII-2 5.2.2 (and EN 13445-3 Annex C, JIS B 8266-style DBA) limits **categories** of stress — membrane, bending, secondary, peak — each with its own allowable. Linearization splits the total through-wall stress into those parts; **classification** (deciding whether a part is primary or secondary) is an engineering judgement you must document.

Tool: [`tools/linearize.py`](../tools/linearize.py) (Annex 5-A integration method, verified against Lamé exact solution below).

---

## 1. Why not just compare max von Mises to the allowable?

- Max von Mises usually sits at a peak (fillet, corner) or singularity → too conservative or meaningless (it never converges, [04](04-meshing-and-convergence.md)).
- A vessel can carry local yielding at a discontinuity safely (shakedown); it cannot carry **average** (membrane) stress above yield over a section (collapse).
- So the code limits **membrane** strictly ($S$), **membrane + bending** less strictly ($1.5S$), **primary + secondary range** at about twice yield ($3S$ / $S_{PS}$), and puts **peak** into fatigue.

---

## 2. Stress categories (ASME VIII-2 5.2.2 terminology)

| Symbol | Name | Definition (short) | Typical example |
|---|---|---|---|
| $P_m$ | General primary membrane | Average through-wall stress needed for equilibrium, **not** at a discontinuity | Hoop stress in plain cylinder from pressure |
| $P_L$ | Local primary membrane | Membrane stress at a discontinuity, limited extent (see §2.1), still needed for equilibrium | Membrane at nozzle–shell junction, at saddle horn |
| $P_b$ | Primary bending | Linear-through-wall part needed for equilibrium | Bending at centre of a flat head; bending in a flat wall |
| $Q$ | Secondary (membrane + bending) | Self-equilibrating, from compatibility / constraint; self-limiting | Bending at head–shell junction; thermal gradient stresses; nozzle junction bending from pressure |
| $F$ | Peak | Non-linear part of the through-wall distribution + local concentration | Weld toe, small fillet, thermal skin stress |

"Primary" = load-controlled (doesn't relax when material yields). "Secondary" = displacement-controlled (relaxes with yielding).

### 2.1 What makes a membrane stress "local" ($P_L$)?
Commonly applied definition (VIII-2 Part 5 definitions / 5.6; originally from old VIII-2 Appendix 4; check wording in your edition):
- region where the membrane equivalent stress exceeds $1.1S$ does not extend more than $\sqrt{R t}$ in the meridional direction, **and**
- such regions are separated by at least $2.5\sqrt{R t}$ (with $R$, $t$ averaged per the code's definition).
Otherwise the membrane stress is **general** ($P_m$) and must be ≤ S.

Sample vessel: $\sqrt{Rt} = \sqrt{507\times8.7}$ = 66 mm → a high-membrane zone longer than 66 mm around N1 is $P_m$, not $P_L$.

### 2.2 Classification examples
ASME VIII-2 **Table 5.6** ("Examples of Stress Classification") is the reference. Paraphrased, representative rows (verify against your edition):

| Component / location | Origin | Membrane | Bending | Peak |
|---|---|---|---|---|
| Cylindrical/spherical shell, plate remote from discontinuities | Internal pressure | $P_m$ | $Q$ (through-wall gradient) | — |
| | Axial thermal gradient | $Q$ | $Q$ | — |
| Shell junction with head or flange | Internal pressure | $P_L$ | $Q$ | — |
| Any shell or head, any section across entire vessel | External load or moment (from piping, wind) | $P_m$ (general, averaged across section) | $P_m$ (as beam bending across the section) | — |
| Near nozzle or other opening | External load / moment or internal pressure | $P_L$ | $Q$ | $F$ |
| Any location | Temperature difference between shell and head | $Q$ | $Q$ | — |
| Dished head or conical head — crown | Internal pressure | $P_m$ | $P_b$ | — |
| Dished head — knuckle or junction to shell | Internal pressure | $P_L$ (see note) | $Q$ | — |
| Flat head — centre region | Internal pressure | $P_m$ | $P_b$ | — |
| Flat head — junction to shell | Internal pressure | $P_L$ | $Q$ (note: if the flat-head design relies on edge moment, it is $P_b$) | — |
| Nozzle neck within limits of reinforcement | Pressure + external loads | $P_L$ (or $P_m$ per edition) | $Q$ | $F$ |
| Nozzle neck outside limits of reinforcement | Pressure / external loads | $P_m$ | $P_b$ (beam bending of nozzle) | — |
| Cladding | Differential expansion | $F$ | $F$ | — |
| Any | Stress concentration (notch) | — | — | $F$ |

**Note on knuckles:** bending in a torispherical knuckle can be large enough that treating it as $Q$ is unconservative for collapse. VIII-2 notes that if bending at a discontinuity is needed to resist the load (i.e. collapse could occur if it relaxed), classify it primary. When in doubt: (a) classify conservatively, or (b) use limit-load / elastic–plastic analysis (5.2.3/5.2.4), which removes the need to classify at all.

---

## 3. Elastic acceptance limits — ASME VIII-2 5.2.2.4 (and ratcheting 5.5.6)

| Check | Limit | Sample: SA-516-70, VIII-1 S = 138 MPa (App. 46 route) |
|---|---|---|
| General primary membrane | $P_m \le S$ | 138 |
| Local primary membrane | $P_L \le S_{PL}$ | 207 |
| Primary membrane + bending | $P_L + P_b \le S_{PL}$ | 207 |
| Primary + secondary **range** (ratcheting, elastic) | $\Delta(P_L + P_b + Q) \le S_{PS}$ (5.5.6.1) | 414 or $2S_y$ = 520, see below |
| Triaxial (local failure, elastic) | $\sigma_1 + \sigma_2 + \sigma_3 \le 4S$ on $P_L + P_b$ principal stresses (5.3.2) | 552 |
| Peak ($P+Q+F$) range | Fatigue: 5.5.3 alternating stress vs design curve | [06](06-beyond-static.md) |

Where (VIII-2 5.2.2.4 and 5.5.6.1(d); confirm wording in your edition):
- $S_{PL}$ = larger of $1.5S$ and $S_y$ — **but** $S_{PL} = 1.5S$ when $S_y/S_u > 0.70$ or when $S$ is governed by time-dependent properties.
- $S_{PS}$ = larger of $3S$ and $2S_y$ (at average temperature of the cycle extremes) — **but** $S_{PS} = 3S$ when $S_y/S_u > 0.70$ or when $S$ is time-dependent.
- SA-516-70: $S_y/S_u$ = 260/485 = 0.54 < 0.70 → $S_{PL} = \max(207, 260)$ = 260 MPa, $S_{PS} = \max(414, 520)$ = 520 MPa at room temperature (use $S_y$ at temperature!). **Many companies conservatively use 1.5S and 3S only** — state which you used.
- Stress measure: **von Mises** equivalent stress (VIII-2 2007 onward). Older VIII-2 (pre-2007) and ASME Section III use **Tresca stress intensity**. Tresca is up to 15 % higher; using Tresca with von Mises-based limits is conservative.
- Load cases: Table 5.3 combinations (see [01 §7](01-design-basis-and-codes.md)).

EN 13445-3 Annex C uses the same structure with $f$: $P_m \le f$, $P_L \le 1.5f$, $P_m(P_L) + P_b \le 1.5f$, $\Delta(P+Q) \le 3f$ (check Annex C table).

---

## 4. Stress Classification Lines (SCLs) — where to put them

Guidance: ASME VIII-2 Annex 5-A (5-A.3), WRC Bulletin 429 (Hechmer & Hollinger, "3D Stress Criteria Guidelines for Application"), PVEng ["The Nuts and Bolts of Stress Linearization"](https://www.pveng.com/home/fea-stress-analysis/the-nuts-and-bolts-of-stress-linearization/).

Rules of thumb:
1. **Straight line through the wall, normal to the mid-surface** (within ~10–20° is acceptable — Autodesk staff on the forum note the integration doesn't care about exact perpendicularity as long as both ends see "the same bending" ([forum](https://forums.autodesk.com/t5/inventor-nastran-forum/stress-linearization-accuracy-issue-with-fem-idealised-as-solids/td-p/14109698))).
2. At **gross structural discontinuities** (head–shell, nozzle–shell, cone junction, flange hub) and at the **location of max membrane** and **max bending**.
3. **Not through a singular point.** Start/end the SCL at least one element away from a sharp corner, or model the fillet.
4. Avoid SCLs where through-thickness stress is dominated by local contact / point loads.
5. For nozzle intersections, a standard set:

| SCL | Location | Typical classification |
|---|---|---|
| A | Shell, remote (≥ $2.5\sqrt{Rt}$ from nozzle) | $P_m$ — compare to hand calc |
| B | Shell, at nozzle weld toe (outside) | $P_L$, $P_L+P_b$, $P+Q$ |
| C | Shell, at inside corner (crotch) — diagonal through the corner region | $P_L$, $P+Q$; peak at inside corner → fatigue |
| D | Nozzle neck at junction | $P_L$, $P+Q$ |
| E | Nozzle neck remote (≥ $2.5\sqrt{r_n t_n}$) | $P_m$ (pressure hoop in nozzle) |
| F | Pad edge on shell (if pad) | $P_L$, $P+Q$ |

6. Check **several angular positions** around the nozzle (0°, 45°, 90° — longitudinal vs circumferential planes). For pressure only, the max is usually in the **longitudinal plane** (hoop stress concentration ≈ 2.5–3.3× at the corner of a radial nozzle in a cylinder).
7. **Thickness**: SCL length = local wall thickness (corroded).
8. **3D effects**: WRC 429 warns that linearization works best when the SCL is in a region where stresses vary mainly through the thickness; in highly 3D regions (crotch corners), results depend on SCL orientation — try 2–3 orientations and report the worst, or move to elastic–plastic analysis.

---

## 5. Linearization math (Annex 5-A integration method)

Coordinate $x$ from inside ($x = 0$) to outside ($x = t$) along the SCL. For each stress component $\sigma_{ij}$ in the **local SCL frame** (n = along SCL / through-thickness; t = hoop; h = meridional):

$$\sigma_{ij,m} = \frac{1}{t}\int_0^t \sigma_{ij}\,dx$$

$$\sigma_{ij,b} = \frac{6}{t^2}\int_0^t \sigma_{ij}\left(\frac{t}{2} - x\right)dx \quad\text{(value at } x = 0\text{; } -\sigma_{ij,b} \text{ at } x = t)$$

$$\sigma_{ij,F}(x) = \sigma_{ij}(x) - \sigma_{ij,m} - \sigma_{ij,b}\left(1 - \frac{2x}{t}\right)$$

- Annex 5-A recommends computing **bending only for the hoop and meridional normal components** (not for the through-thickness normal or the shear components) — the tool does this by default; `--bend-all` computes bending for all six (used by some software; slightly different).
- Then form the tensors $\boldsymbol\sigma_m$ and $\boldsymbol\sigma_m + \boldsymbol\sigma_b$ at each end, compute principal stresses and von Mises: that equivalent stress is what you compare with the limits — **not** the sum of separately computed von Mises values.
- Curved SCLs / axisymmetric corrections (Annex 5-A has refinements for thick axisymmetric shells, using $R_c$ centroid) are not implemented in the script — for $R/t > 10$ they are negligible.

### 5.1 Verification of `linearize.py` against the exact Lamé solution

Thick cylinder $r_i$ = 100, $r_o$ = 150 mm, $P$ = 20 MPa, closed ends; 21 points across the wall (`tools/examples/make_lame_examples.py`):

| Quantity | Exact | `linearize.py` | Error |
|---|---|---|---|
| Membrane hoop $= Pr_i/t$ | 40.000 | 40.005 | 0.01 % |
| Membrane radial | −8.000 | −8.005 | 0.06 % |
| Membrane axial | 16.000 | 16.000 | 0 |
| Bending hoop (inside) | 9.678 | 9.682 | 0.04 % |

```text
$ python3 tools/linearize.py tools/examples/lame_scl_local.csv --S 138 --category PL
Component                 nn         tt         hh   ...
Membrane              -8.005     40.005     16.000
Bending (inside)       0.000      9.682      0.000
Total inside         -20.000     52.000     16.000
M+B inside            -8.005     49.688     16.000
Peak inside          -11.995      2.312      0.000
...
Equivalent stresses (MPa)       von Mises     Tresca(SI)
  Membrane                          41.578       48.011
  Membrane+Bending (inside )        50.197       57.693
  Total            (inside )        62.354       72.000
Check vs ASME VIII-2 5.2.2.4 elastic limits (von Mises; confirm edition):
  PL      =    41.58 <= 1.5S =   207.00  -> PASS  (ratio 0.201)
  P(L)+Pb =    50.20 <= 1.5S =   207.00  -> PASS  (ratio 0.242)
```

The same SCL rotated 30° in a global frame (`lame_scl_global_rot30.csv`, `--frame global --tdir -0.5 0.8660254 0`) gives identical results — the rotation logic works.

Observations worth knowing:
- Even in a "plain" thick cylinder there is **bending** (9.7 MPa) and **peak** (the non-linear part, 2.3 MPa hoop, 12 MPa radial at inside). Pure pressure in a thick shell: the through-wall gradient is classified **Q** per Table 5.6 ("plate remote from discontinuities — gradient through thickness"), so only membrane goes to $P_m$.
- Radial stress (−P at inside) is mostly "peak" by this decomposition, because bending is not computed for the through-thickness component.

---

## 6. Linearization in Inventor Nastran — three ways

### 6.1 Built-in *Results > Stress Linearization* (recommended first)
From the Autodesk help ([Stress Linearization](https://help.autodesk.com/cloudhelp/2023/ENU/NINCAD-UsersGuide/files/GUID-7F2C9CF2-E809-4716-9D09-992A306B75A5.htm)):
- Available after results are loaded, for all linear and nonlinear analyses that produce stresses.
- You define the SCL **first and last point** and a **third point** that orients the local stress-tensor coordinate system.
- It plots local stress tensors along the SCL and reports **Pm, Pb, Pm+Pb** based on **both** maximum shear (Tresca) and von Mises.
- The green button saves the numeric results as **CSV**.

Step by step:
1. Show a stress contour on the result (*Results > Contour*).
2. *Results > Stress Linearization*.
3. Pick (or type coordinates of) the inside point and outside point of the SCL. **Typing coordinates** makes the SCL repeatable for mesh-convergence runs. Get the coordinates from an Inventor sketch line drawn normal to the surface ([Autodesk staff tip](https://forums.autodesk.com/t5/inventor-nastran-forum/stress-linearization-accuracy-issue-with-fem-idealised-as-solids/td-p/14109698)).
4. Pick the reference (third) point to set the local axes (e.g. a point on the vessel axis so one axis is radial).
5. Read Pm / Pb / Pm+Pb (von Mises column for VIII-2 2007+).
6. Export CSV → keep it in the report appendix; optionally run `linearize.py` on it as an independent check.

Caveats (from Autodesk forum threads with Autodesk/expert answers):
- Nastran outputs stress at **corner nodes**; Inventor shows mid-side node values by **linear interpolation**, and the SCL values between nodes are interpolated ([forum thread](https://forums.autodesk.com/t5/nastran-forum-read-only/stress-linearization-results-not-corresponding-to-computed/td-p/11781189)). With one parabolic element through the wall you only have 2 real data points → use ≥ 3 elements through thickness.
- The tool's output label "Pm" means *membrane of this SCL*. Whether it is $P_m$, $P_L$ or part of $Q$ is **your** classification.
- For **shell** models, an SCL "through thickness" isn't meaningful (one element); use shell top/bottom/membrane outputs instead (§6.3).
- The tool computes on the current result set; make sure the right subcase is active and stresses are in the right units.

### 6.2 Manual: extract nodal stresses along a path → `linearize.py`
Use when you need full control, Tresca vs von Mises comparisons, or a check of the built-in tool.
1. In Inventor, **split the face** (or the body) so an edge lies exactly on the SCL. The mesher then puts nodes on it (forum advice from an expert user).
2. Mesh, solve.
3. Right-click *Nodes > Query* (model tree) / probe to list stress components $\sigma_{xx}, \sigma_{yy}, \sigma_{zz}, \tau_{xy}, \tau_{yz}, \tau_{zx}$ at the nodes on that edge; copy to Excel/CSV with x, y, z coordinates. (Or read the binary `.fno` results with a script — see the Autodesk forum thread on reading FNO files.)
4. Save as CSV with header `x,y,z,Sxx,Syy,Szz,Sxy,Syz,Szx`, ordered inside → outside.
5. Run:
   ```bash
   python3 tools/linearize.py my_scl.csv --frame global --tdir <hoop direction vector> --S 138 --category PL
   ```
   For a cylinder with axis along z at a point $(x, y)$: hoop direction = $(-y, x, 0)$ normalised.
6. If you have the Stress Linearization CSV already in local components, map its columns to `s,Snn,Stt,Shh,Snt,Sth,Shn` and use `--frame local`.

### 6.3 Shell models: membrane and bending directly
- Shell elements carry membrane and bending explicitly. With parameter **DIRSTRESSTYPE / EQVSTRESSTYPE** = 2 → membrane only; = 1 → bending only; = 0 → total (top/bottom surfaces) ([Autodesk article](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Extracting-membrane-and-bending-stresses-from-results-in-Nastran.html)). One run per setting.
- Membrane equivalent ↔ $P_m$ / $P_L$; total at top/bottom ↔ $P_L + P_b$ (+ $Q$). Shells have **no peak** stress — fatigue needs a stress concentration factor or solid submodel.
- Manual alternative: membrane = (top + bottom)/2, bending = (top − bottom)/2 **per component**, then compute von Mises of the combined tensors.

---

## 7. Worked classification example — N1 on the sample vessel (pressure only, design case)

Illustrative values (what a correct model typically shows; your run will differ):

| SCL | Location | Linearized (von Mises, MPa) | Category | Limit (MPa) | Ratio | Result |
|---|---|---|---|---|---|---|
| A | Shell remote | Pm = 76 | $P_m$ | S = 138 | 0.55 | PASS |
| A | Hand-calc check | Pm (thin wall vM) = 75.8 | — | — | 1.00 | FEA verified |
| B | Shell at nozzle toe, long. plane | membrane 128 | $P_L$ | 1.5S = 207 | 0.62 | PASS |
| B | " | m+b 205 | $P_L + P_b + Q$ (range from 0) | 3S = 414 | 0.50 | PASS |
| C | Inside crotch, diagonal | membrane 145 | $P_L$ | 207 | 0.70 | PASS |
| C | " | m+b 262 | $P + Q$ range | 414 | 0.63 | PASS |
| D | Nozzle neck at junction | membrane 110; m+b 230 | $P_L$; $P+Q$ | 207; 414 | 0.53; 0.56 | PASS |
| E | Nozzle remote | Pm = 33 ≈ $Pr/t_n$ = 1.5×105.5/5 = 31.7 | $P_m$ | 138 | 0.24 | PASS |

Decisions documented:
- The bending at B, C, D is from compatibility of nozzle and shell → $Q$ (Table 5.6 "near nozzle — pressure — bending Q"). Hence m+b is checked against $3S$ for the range, and $P_L$ alone against $1.5S$. If you choose to be conservative and call it $P_b$, check against $1.5S$ (205 < 207 just passes — note the small margin).
- For pressure only from 0 to $P$, the range equals the value.
- Peak at C inside corner → fatigue screening ([06](06-beyond-static.md)).

---

## 8. Common linearization mistakes

| Mistake | Effect | Fix |
|---|---|---|
| SCL through a singular corner | Bending/peak grow with mesh; no convergence | Start one element away or model fillet |
| One element through thickness | Linear field only; bending under-predicted | ≥ 3 parabolic elements |
| Linearizing von Mises (a scalar) instead of components | Wrong; not allowed | Linearize **components**, then combine |
| Combining Pm vM + Pb vM by adding scalars | Over/under-estimates | Combine tensors, then vM |
| Global components without rotation | Bending mixed between components | Use local frame (tool / `--frame global`) |
| Using uncorroded thickness for design case | Unconservative | Model corroded geometry |
| Calling everything at a junction "Q" | Possibly unconservative for collapse | Justify; or elastic–plastic route |
| Only checking one angular position around nozzle | Miss the max | Check 0/45/90° planes and contour max |
| Forgetting the stress **range** for P+Q | Wrong check when loads reverse | Build ranges by superposition of subcases |

---

## 9. When elastic linearization is not enough
- 3D regions where classification is ambiguous (crotch corners, saddle horns, lug welds).
- Thick sections where Q is large and you want to avoid conservatism.
- Components that fail elastic limits by a small margin.

→ Use **limit-load (5.2.3)** or **elastic–plastic (5.2.4)** analysis: no classification needed, load factors replace stress categories. See [06](06-beyond-static.md).

Next: [06 — Beyond static](06-beyond-static.md).
