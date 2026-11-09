# 02 — Hand Calculations (with a worked sample vessel)

> Hand calcs come **before** FEA. They (1) size the vessel by code rules, (2) give you numbers the FEA must reproduce in plain regions, and (3) catch unit and load errors in minutes instead of days.

All numbers on this page are produced by [`tools/pv_handcalc.py`](../tools/pv_handcalc.py) with [`tools/examples/sample_vessel.json`](../tools/examples/sample_vessel.json). Re-run it for your vessel.

```bash
python3 tools/pv_handcalc.py tools/examples/sample_vessel.json --markdown
```

---

## 0. Sample vessel (used throughout this guide)

| Item | Value |
|---|---|
| Code | ASME VIII-1 (formulas), VIII-2 Part 5 (FEA acceptance) |
| Inside diameter $D_i$ | 1000 mm |
| Design pressure $P$ | 1.5 MPa (internal) |
| Design temperature | 100 °C |
| Material | SA-516 Gr 70 |
| Allowable stress $S$ | 138 MPa — **typical II-D Table 1A value at this temperature; confirm in your edition** |
| Joint efficiency $E$ | 1.0 (full radiography) |
| Corrosion allowance $CA$ | 3.0 mm |
| Nominal shell thickness $t_n$ | 12 mm; mill under-tolerance 0.3 mm |
| Available (corroded, minimum) thickness | $t = 12 - 3 - 0.3 = 8.7$ mm |
| Corroded inside radius | $R = 500 + 3 = 503$ mm |
| Nozzle N1 | 200 mm ID, 8 mm wall, set-on radial, on shell |
| $E_{mod}$, $\nu$ | 200 000 MPa, 0.3 |

Units everywhere: **N, mm, MPa (N/mm²)**. This is also the unit system to choose in Inventor Nastran (see [03](03-inventor-nastran-model-setup.md)).

---

## 1. Cylindrical shell — ASME VIII-1 UG-27

### 1.1 Formulas (inside radius, corroded)
Circumferential (longitudinal seams), UG-27(c)(1):
$$t = \frac{PR}{SE - 0.6P} \qquad P = \frac{SEt}{R + 0.6t}$$
Longitudinal (circumferential seams), UG-27(c)(2):
$$t = \frac{PR}{2SE + 0.4P} \qquad P = \frac{2SEt}{R - 0.4t}$$
Valid when $t \le R/2$ and $P \le 0.385SE$; otherwise use Appendix 1-2 (thick shells).

### 1.2 Numbers

| Quantity | Calculation | Result |
|---|---|---|
| $t_{circ}$ required | $1.5 \times 503 / (138 - 0.9)$ | **5.50 mm** |
| $t_{long}$ required | $1.5 \times 503 / (276 + 0.6)$ | 2.73 mm |
| + CA | 5.50 + 3.0 | 8.50 mm |
| + under-tolerance | 8.50 + 0.3 | 8.80 mm → 10 mm plate would be enough; 12 mm chosen (nozzle reinforcement, stiffness, stock) |
| Thin-wall validity | $P = 1.5 \le 0.385 \times 138 = 53$ ✓; $t \le R/2$ ✓ | OK |
| MAWP (corroded, circ) | $138 \times 8.7 / (503 + 5.22)$ | **2.36 MPa** |
| MAWP (long) | $2 \times 138 \times 8.7 / (503 - 3.48)$ | 4.81 MPa |

Check with Appendix 1-2 thick-wall formula $t = R(\sqrt{Z} - 1)$, $Z = \frac{SE + P}{SE - P}$: $t$ = 5.497 mm — same as UG-27 (thin-wall formula is an excellent approximation here).

### 1.3 What the FEA should show in the plain shell (≥ $2.5\sqrt{Rt}$ away from heads, nozzles, supports)

Membrane stresses at mean radius $R_m = 503 + 8.7/2 = 507.35$ mm:

| Stress | Formula | Value (MPa) |
|---|---|---|
| Hoop $\sigma_\theta$ | $PR_m/t$ | **87.5** |
| Longitudinal $\sigma_z$ | $PR_m/(2t)$ | **43.7** |
| Radial $\sigma_r$ | $-P$ (inside) → 0 (outside) | −1.5 → 0 |
| von Mises (membrane, $\sigma_r$≈0) | $\sqrt{\sigma_\theta^2 - \sigma_\theta\sigma_z + \sigma_z^2}$ | 75.8 |
| Tresca (stress intensity) | $\sigma_\theta - \sigma_r$ | ≈ 88.2 (mid-wall) |

Lamé thick-wall check (exact elasticity, closed ends), corroded $r_i$ = 503, $r_o$ = 511.7:

| Location | Hoop | Radial | Axial | von Mises |
|---|---|---|---|---|
| Inside surface | 87.48 | −1.50 | 42.99 | 77.06 |
| Outside surface | 85.98 | 0 | 42.99 | — |
| Through-wall mean hoop | $Pr_i/t$ = 86.72 | | | |

**Acceptance for FEA verification:** FEA hoop stress at mid-wall in the plain shell should be within **±2–3 %** of 86.7–87.5 MPa. If it is 10× off, your units are wrong; if it is ~2× off, the end-cap thrust or the constraint is wrong (see [07](07-verification-and-validation.md)).

> Note why the thin-wall value 87.47 and Lamé mean 86.72 differ: thin-wall uses $R_m$, the exact membrane value is $P r_i/t$. Both are "right"; quote which one you compare to.

---

## 2. Formed heads — ASME VIII-1 UG-32 and Appendix 1-4

### 2.1 Formulas (inside dimensions, corroded, seamless head or E for head seams)

| Head | Required thickness | Notes |
|---|---|---|
| Hemispherical | $t = \dfrac{PL}{2SE - 0.2P}$, $L = D/2$ | Valid $t \le 0.356L$, $P \le 0.665SE$ |
| 2:1 Ellipsoidal | $t = \dfrac{PD}{2SE - 0.2P}$ | $D/2h = 2$ |
| General ellipsoidal | $t = \dfrac{PDK}{2SE - 0.2P}$, $K = \frac{1}{6}\left[2 + \left(\frac{D}{2h}\right)^2\right]$ | App. 1-4(c) |
| Torispherical (general) | $t = \dfrac{PLM}{2SE - 0.2P}$, $M = \frac{1}{4}\left(3 + \sqrt{L/r}\right)$ | App. 1-4(d); L = crown radius, r = knuckle radius |
| Torispherical ASME standard F&D ($L = D_o$, $r = 0.06D_o$) | $t = \dfrac{0.885PL}{SE - 0.1P}$ | UG-32(e) |

Also check: torispherical heads with $t_s/L < 0.002$ need App. 1-4(f) (knuckle buckling / plastic collapse rules). Thin large-diameter torispherical heads are a classic FEA buckling case.

### 2.2 Numbers (corroded $D$ = 1006 mm)

| Head | Required $t$ (mm) | + CA (mm) | Comment |
|---|---|---|---|
| Hemispherical ($L$ = 503) | **2.74** | 5.74 | Half the cylinder thickness |
| 2:1 Ellipsoidal | **5.47** | 8.47 | ≈ same as shell |
| Torispherical $L$ = 1003, $r$ = 63 (≈6 %), $M$ = 1.748 | **9.54** | 12.54 | Knuckle bending makes it thickest |

**Head forming thinning:** order the head with minimum thickness after forming ≥ required + CA. Head makers typically need 10–15 % extra plate at the knuckle — ask them, don't assume.

### 2.3 Membrane stress pattern in a 2:1 ellipsoidal head (what FEA must show)

From classical membrane theory (Timoshenko & Woinowsky-Krieger; Bednar; Jawad & Farr), semi-axes $a$ (= R) and $b$ (= a/2), uniform thickness:

| Location | Meridional $\sigma_\phi$ | Hoop $\sigma_\theta$ |
|---|---|---|
| Crown (pole) | $\dfrac{Pa^2}{2bt} = \dfrac{PR}{t}$ (for a/b = 2) | same as meridional |
| Equator (knuckle/tangent line) | $\dfrac{Pa}{2t}$ | $\dfrac{Pa}{t}\left(1 - \dfrac{a^2}{2b^2}\right) = -\dfrac{PR}{t}$ **(compressive)** |

So at the tangent line of a 2:1 head the hoop membrane stress is **compressive**, ~ −87 MPa for the sample vessel — the cylinder is pulling the head out and the head is pulling the cylinder in. FEA must show this sign change; if not, check the head geometry (a true ellipse vs. a torispherical approximation of it).

### 2.4 Torispherical heads
- Knuckle region: high meridional **bending** + compressive hoop membrane.
- Typical FEA result: max $P_L + P_b + Q$ in the knuckle, inside surface, meridional direction.
- Large thin heads ($D/t > 500$ or so) can **buckle** in the knuckle under internal pressure (wrinkling) — App. 1-4(f), VIII-2 4.3.6 rules exist for this; FEA must use buckling/elastic–plastic analysis, not just linear stress.

---

## 3. Discontinuity stresses at a head–shell junction (shell theory)

Where two shells with different free radial growth are welded, a shear force $Q_0$ and moment $M_0$ develop. Beam-on-elastic-foundation theory (Timoshenko; Hetényi; Roark Table 13.2) gives:

$$\beta = \left[\frac{3(1-\nu^2)}{R_m^2 t^2}\right]^{1/4} \qquad D = \frac{E t^3}{12(1-\nu^2)}$$

Free radial growth under pressure:
- Cylinder (closed end): $\delta_c = \dfrac{PR_m^2}{Et}\left(1 - \dfrac{\nu}{2}\right)$
- Hemisphere: $\delta_s = \dfrac{PR_m^2}{2Et}(1 - \nu)$
- Mismatch $\delta_c - \delta_s = \dfrac{PR_m^2}{2Et}$

For **equal thickness hemi head + cylinder**, symmetry gives $M_0 \approx 0$ and

$$Q_0 = \frac{P}{8\beta}$$

The cylinder moment distribution is $M(x) = \dfrac{Q_0}{\beta}e^{-\beta x}\sin\beta x$, maximum at $\beta x = \pi/4$.

### Sample vessel numbers (corroded, equal thickness 8.7 mm assumed)

| Quantity | Value |
|---|---|
| $\beta$ | 0.01935 mm⁻¹ |
| Characteristic length $1/\beta$ | 51.7 mm |
| $\sqrt{R_m t}$ | 66.4 mm |
| $Q_0$ | 9.69 N/mm |
| Location of max moment $x = \pi/(4\beta)$ | 40.6 mm from junction |
| $M_{max}$ | 161.5 N·mm/mm |
| Bending stress $6M/t^2$ | **12.8 MPa** |
| Longitudinal membrane $PR_m/2t$ | 43.7 MPa |
| Max longitudinal surface stress | 56.5 MPa (= membrane + bending) |
| Hoop stress at junction (cylinder) | 65.6 MPa (reduced from 87.5 by inward pull) |

### What this teaches for FEA
- Discontinuity effects **decay** within about $2.5\sqrt{Rt}$ (≈ 166 mm here). This is why ASME VIII-2 5.6 / Annex 5-A and EN 13445-3 Annex C define a "local" region of $\sqrt{Rt}$-order size: stresses there are classified as $P_L$ (local primary) or $Q$ (secondary).
- Bending at a junction caused by **compatibility** (deformation mismatch) is **secondary (Q)**, because it is self-limiting. Bending that is needed for **equilibrium** (e.g. a flat head centre) is **primary (Pb)**.
- Your mesh must have **several elements within $1/\beta$** to capture this (≥ 4–6 through the decay length along the axis, ≥ 3–4 through thickness for solids, see [04](04-meshing-and-convergence.md)).
- Ellipsoidal and torispherical junctions have no simple closed form — this is exactly where FEA is useful. Compare against published results (e.g. PVRC / WRC bulletins; Bednar Ch. 4).

---

## 4. Nozzle reinforcement — area replacement (UG-37), concept and numbers

### 4.1 Concept
Metal removed by the hole must be replaced within a reinforcement zone:
- Along the shell: limit = larger of $d$ or $R_n + t_n + t$ on each side of the opening centreline.
- Normal to the shell: limit = smaller of $2.5t$ or $2.5t_n + t_e$.

Required area (F = 1 for internal pressure on cylinder in the longitudinal plane):
$$A = d\,t_r\,F + 2t_n t_r F(1 - f_{r1})$$
Available:
- $A_1$ (excess in shell) = larger of $d(E_1t - Ft_r) - \dots$ and $2(t + t_n)(E_1t - Ft_r) - \dots$
- $A_2$ (excess in nozzle wall) = smaller of $5(t_n - t_{rn})f_{r2}t$ and $5(t_n - t_{rn})f_{r2}t_n$
- $A_{41}, A_{42}, A_{43}$ welds; $A_5$ pad = $(D_p - d - 2t_n)t_e f_{r4}$

Simplified in the tool: $F = 1$, $f_r = 1$ (same material), weld areas ignored (conservative). **Use full UG-37 (or VIII-2 4.5, which uses a different pressure-area method since 2007) for the code calc.**

### 4.2 Numbers for N1 (200 mm ID, 8 mm wall, corroded $d$ = 206 mm, $t_n$ = 5 mm)

| Item | Value (mm²) |
|---|---|
| $t_r$ (shell, E = 1) | 5.50 mm |
| $t_{rn}$ (nozzle) | 1.13 mm |
| Required $A$ | 1134 |
| $A_1$ shell excess | 658.5 |
| $A_2$ nozzle excess | 96.8 |
| **Available (no pad)** | **755 → NOT ADEQUATE** |
| With 340 OD × 10 mm pad, $A_5$ | 1240 |
| **Available (with pad)** | **1995 → OK** |

Run: `python3 tools/pv_handcalc.py tools/examples/sample_vessel_with_pad.json --markdown`

### 4.3 What area replacement does NOT check (→ FEA or WRC)
- External nozzle loads (piping F, M) → WRC 107/537, WRC 297, or FEA (see [06](06-beyond-static.md)).
- Fatigue at the nozzle–shell weld toe.
- Large openings ($d > D/2$) — App. 1-7 or FEA.
- Closely spaced nozzles with overlapping limits (UG-42).
- Hillside / tangential nozzles beyond rule limits.
- Pad weld strength (UG-41) and the pad tell-tale hole (UG-37(g)) — pads trap a crevice; FEA should model the pad either as contact (separation) or bonded only at the welds.

### 4.4 Pressure–area method (VIII-2 4.5, EN 13445-3 clause 9)
The modern rule is equilibrium: pressure × pressurised area ≤ allowable × metal area:
$$P\,(A_p) \le \left(S - \tfrac{P}{2}\right)(A_{f,shell} + A_{f,nozzle} + A_{f,pad})$$
(EN 13445-3 9.4 form, written with $f$; check exact terms in your code). It is easy to verify with FEA: the linearized membrane stress across the nozzle-shell section should be close to $P A_p / A_f$.

---

## 5. Flanges — basics you need for a vessel FEA

- **Prefer standard flanges** (ASME B16.5 ≤ NPS 24, B16.47 above; JIS B 2220 in Japan): pressure–temperature rating tables replace stress analysis. FEA of a standard flange is usually unnecessary.
- **Non-standard body flanges**: ASME VIII-1 Appendix 2 (Taylor-Forge method) or EN 1591-1.
- App. 2 bolt loads:
  - Operating: $W_{m1} = H + H_p = 0.785G^2P + 2b\pi G m P$
  - Seating: $W_{m2} = \pi b G y$
  - Required bolt area $A_m = \max(W_{m1}/S_b,\ W_{m2}/S_a)$
  - $m$, $y$ = gasket factors (App. 2 Table 2-5.1), $b$ = effective gasket width, $G$ = gasket reaction diameter.
- Flange stresses (hub longitudinal $S_H \le 1.5S_f$, radial $S_R \le S_f$, tangential $S_T \le S_f$, and averages).
- **Flange rigidity** (App. 2-14) — often governs leak tightness, not strength.
- **FEA of flanges**: needs bolt pretension, gasket non-linearity and contact → nonlinear analysis. Linear bonded models give meaningless flange stresses. Use ASME PCC-1 for assembly bolt stress targets.

---

## 6. Hydrotest pressure and test stresses

| Code | Formula | Sample vessel ($P$ = 1.5, stress ratio 1.0) |
|---|---|---|
| ASME VIII-1 UG-99(b) | $1.3 \times MAWP \times LSR$ | 1.95 MPa if design P used; **3.07 MPa if MAWP 2.36 is used** |
| ASME VIII-2 8.2.1 | $\max(1.43\,MAWP,\ 1.25\,MAWP\,S_T/S)$ | 2.15 MPa (with P) |
| JIS B 8267 8.5 b) | $1.3P\,\sigma_t/\sigma_a$ (pneumatic 1.1) | 1.95 MPa |
| JIS B 8265 8.5 b) | $1.5P\,\sigma_t/\sigma_a$ (pneumatic 1.25) | 2.25 MPa |
| PED Annex I 7.4 / EN 13445-5 | $\max(1.25P_d f_{test}/f_d,\ 1.43PS)$ | 2.15 MPa |

- **LSR** (lowest stress ratio) = min over all pressure parts of $S_{test}/S_{design}$. For carbon steel at 100 °C, often 1.0.
- ASME permits using design pressure instead of MAWP when MAWP is not calculated (UG-99(b) footnote) — the vessel nameplate then shows the design pressure as MAWP.
- **Add hydrostatic head** of the test water at the point you check (vertical vessel tested vertical: +0.0098 MPa per metre).
- **Test stress check** (new thickness, $t$ = 11.7 mm, $R$ = 500 mm, $P_T$ = 1.95 MPa): hoop $= 1.95 \times 505.85/11.7$ ≈ **84 MPa** ≪ yield 260 MPa. VIII-2 4.1.6.2 limits test membrane to $0.95S_y$ — check edition. Common practice for VIII-1 is to keep general membrane ≤ 0.9 $S_y$ during test.
- Test case in FEA: water weight + pressure + supports in **test position** (e.g. vertical vessel tested horizontal on saddles — the saddle FEA governs!).

---

## 7. Loads that FEA must include — compute them here first

| Load | Formula | Sample value |
|---|---|---|
| End-cap thrust on vessel (if you cut the model at a symmetry plane, no thrust needed; if you model only a shell segment with free end, apply it) | $P\pi R^2$ | $1.5\pi(503)^2$ = **1.19 MN** |
| End-cap thrust on a cut nozzle (nozzle truncated, pipe not modelled) | $P\pi r_n^2$ | $1.5\pi(103)^2$ = **50.0 kN** |
| Same as axial pressure on the nozzle cut annulus | $P r_n^2 / (r_o^2 - r_n^2)$ | **15.1 MPa** (tension, outward normal) |
| Liquid head at bottom (2 m water) | $\rho g h$ | 0.0196 MPa |
| Vessel + water weight (for saddles) | mass × g | compute from Inventor iProperties |

Inventor Nastran applies pressure normal to faces. It does **not** automatically add the thrust from the pipe you didn't model. See [03 §6](03-inventor-nastran-model-setup.md#6-loads).

---

## 8. External pressure (vacuum) — quick estimate

UG-28 uses factor A / B charts. Behind them, for elastic collapse of a cylinder between stiffeners (Windenburg–Trilling, simplified):
$$P_c \approx \frac{2.42E\,(t/D_o)^{2.5}}{(1-\nu^2)^{3/4}\left[L/D_o - 0.45(t/D_o)^{1/2}\right]}$$

Sample vessel, $t$ = 8.7 mm (corroded), $D_o$ = 1024 mm, $L$ = 3000 mm (tangent-to-tangent + 1/3 head depths, per UG-28 definition — compute properly):

| Quantity | Value |
|---|---|
| $D_o/t$ | 117.7 |
| $L/D_o$ | 2.93 |
| Elastic collapse $P_c$ | ≈ 1.20 MPa |
| $P_c/3$ (≈ VIII-1 margin in elastic range) | ≈ 0.40 MPa > 0.101 MPa (full vacuum) |

**Estimate only.** The code check is UG-28 (VIII-1) or 4.4 (VIII-2). FEA buckling (eigenvalue) gives a perfect-geometry value that is **unconservative** — see [06 §3](06-beyond-static.md#3-buckling-viii-2-54).

---

## 9. Hand-calc summary sheet for the report

| # | Component | Code clause | Required t (mm) | Provided t corroded (mm) | MAWP (MPa) | OK? |
|---|---|---|---|---|---|---|
| 1 | Shell | UG-27(c)(1) | 5.50 | 8.70 | 2.36 | ✓ |
| 2 | 2:1 head | UG-32(d) | 5.47 | (fill) | (fill) | |
| 3 | Nozzle N1 + pad | UG-37 | A = 1134 mm² | 1995 mm² | — | ✓ with pad |
| 4 | Hydrotest | UG-99(b) | — | — | $P_T$ = 1.95 (or 3.07 on MAWP) | |
| 5 | Vacuum | UG-28 | — | — | estimate 0.40 allowable | ✓ (confirm with UG-28) |

Next: [03 — Inventor Nastran model setup](03-inventor-nastran-model-setup.md).
