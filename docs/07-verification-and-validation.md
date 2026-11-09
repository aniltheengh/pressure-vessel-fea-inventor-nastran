# 07 — Verification and Validation (V&V)

> **Verification**: did we solve the equations right? (model built and solved correctly)
> **Validation**: did we solve the right equations? (model represents the real vessel)
> Definitions follow ASME V&V 10 (computational solid mechanics) and NAFEMS usage.

A senior reviewer will trust your result only if this file's checks are in the report.

---

## 1. The V&V ladder

| Level | Question | Evidence |
|---|---|---|
| Code verification | Does the software solve standard problems correctly? | Vendor verification manual; your own benchmark (Lamé cylinder, sphere) once per software version |
| Calculation verification | Is *this* model numerically correct? | Mesh convergence, equilibrium, units, sanity checks, hand calcs |
| Validation | Does the model match reality? | Test data: strain gauges, displacement, hydrotest, previous similar vessel |
| Code acceptance | Does the design meet the code? | Linearized stress vs limits, load factors, fatigue damage |
| Certification | Is the vessel legally acceptable? | AI / Notified Body / Japanese inspection body sign-off, hydrotest, stamping |

FEA reports usually provide calculation verification + code acceptance. **Validation by test is rare for one-off vessels** — the hydrotest is a proof test, not a validation of the stress field (§6).

---

## 2. Code verification — run once per software version

Benchmarks (hand-solvable):

| Benchmark | Model | Exact answer | Acceptable error |
|---|---|---|---|
| Thick cylinder (Lamé) | $r_i$ = 100, $r_o$ = 150, $P$ = 20 MPa, closed end (wedge or quarter model) | Hoop inside 52.0, outside 32.0, axial 16.0, radial −20 → 0 MPa | < 1 % with parabolic tets, ≥ 4 through wall |
| Thin sphere | $R$ = 500, $t$ = 5, $P$ = 1 | $\sigma = PR/2t$ = 50 MPa | < 1 % |
| Hemi-head/cylinder junction | sample vessel | $\sigma_b$ ≈ 12.8 MPa at 40.6 mm from junction ([02 §3](02-hand-calculations.md)) | < 5 % |
| Cantilever (beam/shell) | any | $\delta = FL^3/3EI$ | < 1 % |
| Plate with hole | $K_t$ = 3.0 (infinite plate) | Peterson | < 3 % with fine mesh |

Autodesk publishes Nastran verification/test problems (see Autodesk Nastran documentation and the "Testing the Autodesk Nastran Installation" help page). Run `tools/examples/make_lame_examples.py` to get the exact Lamé values for comparison.

---

## 3. Calculation verification — checklist for every model

### 3.1 Solver output
- [ ] No FATAL messages. All WARNINGs read and explained (G3005, G3009, G3016/17, G3051, T2217, E5010 → [08](08-inventor-nastran-errors-and-fixes.md)).
- [ ] Grid point singularity table: only expected DOFs (rotations 4–6 at solid nodes) auto-constrained (`SPCGEN` on to see them).
- [ ] Contact: initial penetration reported in `.out` ("INITIAL MAXIMUM CONTACT SURFACE PENETRATION") is small.

### 3.2 Equilibrium (load balance)
- [ ] **Applied load resultant (OLOAD) = − reaction resultant (SPC forces)** within 0.1 %.
- [ ] Pressure-only closed vessel: reactions ≈ 0 (< 0.1 % of $P\pi R^2$). Sample vessel: $P\pi R^2$ = 1.19 MN → reactions should be < ~1 kN.
- [ ] Gravity: vertical reaction = total mass × g. Compare to Inventor iProperties mass.
- [ ] Hydrostatic: vertical reaction = water mass × g + vessel weight.
- [ ] Saddle split: each saddle ≈ half the weight (if symmetric).
- [ ] Nozzle load case: reactions = applied F, M (with lever arm).

### 3.3 Hand-calc comparison table (in every report)

| # | Quantity | Location | Hand calc | FEA | Diff | Accept? (±5 %) |
|---|---|---|---|---|---|---|
| 1 | Hoop membrane | Shell, remote (SCL-A) | 86.7 (Lamé mean) / 87.5 (thin) | (fill) | | |
| 2 | Longitudinal membrane | Shell, remote | 43.7 (thin) / 43.0 (Lamé) | | | |
| 3 | Radial displacement | Shell, remote | 0.189 mm | | | |
| 4 | Hoop membrane | Nozzle remote (SCL-E) | 31.7 | | | |
| 5 | Head crown membrane (2:1) | Crown | $PR/t$ (a/b = 2) | | | |
| 6 | Hoop at 2:1 head tangent | Equator | ≈ $-PR/t$ (compressive) | | | |
| 7 | Reaction sum | Supports | weight | | | |
| 8 | Buckling eigenvalue | Shell | ≈ 11.9 for 0.101 MPa (elastic estimate) | | | (±20 %) |

### 3.4 Sanity of deformation and stress pattern
- [ ] Deformed shape: shell grows; heads bulge; nozzle grows radially and rotates outward at junction.
- [ ] Max displacement magnitude in a plausible range (0.1–1 mm typical for ~1 m vessels at design P). 10³ off = units.
- [ ] Stress contours continuous across bonded/contact interfaces (jumps → bad contact).
- [ ] Symmetric model + symmetric loads → symmetric results.
- [ ] Hoop stress in a **cylindrical coordinate system** (not global X/Y) is ≈ uniform away from features.

### 3.5 Units
- [ ] E = 200 000 (MPa) — not 200 (GPa) or 2.0e11 (Pa).
- [ ] Density 7.85e-9 t/mm³ in mm–N system.
- [ ] Pressure 1.5 (MPa) — not 15 (bar) or 1.5e6 (Pa).
- [ ] Piping moments converted kN·m → N·mm (×10⁶).

### 3.6 Mesh
- [ ] Convergence study for reported quantities ([04](04-meshing-and-convergence.md)), GCI reported.
- [ ] ≥ 3 parabolic elements through thickness on SCLs.
- [ ] No bad-quality elements on SCLs.

### 3.7 Sensitivity to assumptions (robustness)
- [ ] Support stiffness: fixed vs sliding saddle — does the conclusion change?
- [ ] Pad: bonded vs separation — does the conclusion change?
- [ ] Corroded vs new.
- [ ] ±10 % on uncertain loads (nozzle loads).
If the conclusion flips, the model isn't decisive — report it.

---

## 4. Typical "the result is wrong" signatures

| Symptom | Likely cause |
|---|---|
| Hoop stress ~2× too high/low | Pressure on wrong faces / both sides; shell offset wrong; thickness wrong |
| Longitudinal stress ≈ 0 in nozzle | Missing end-cap thrust |
| Longitudinal stress high near a fixed end | Constraint blocking Poisson/pressure growth |
| Stress 10⁶ off | Pa vs MPa |
| Stress 10³ off | mm vs m, or kPa vs MPa |
| Huge stress at supports, tiny elsewhere | Point constraint / over-constraint |
| Asymmetric results on symmetric model | Missing symmetry constraint; mesh asymmetry (small effect); contact asymmetry |
| Results change a lot with mesh at hot spot | Singularity |
| Displacement huge, stresses tiny | Near-mechanism: weak spring/contact holding a part |

---

## 5. Validation — testing and correlation

### 5.1 What counts as validation evidence
- **Strain-gauge test** during hydrotest or operation, with predictions made **before** the test.
- **Displacement** measurements (dial gauges, laser, DIC — digital image correlation).
- **Burst / proof test** (UG-101 in VIII-1 — proof test to establish MAWP when design can't be calculated). UG-101 is a code route in its own right (brittle-coating, strain-gauge, displacement, burst methods).
- **Prior qualified design** with service history (weaker evidence).

### 5.2 Test plan (write before the test)
| Item | Content |
|---|---|
| Objective | e.g. validate stresses at N1 junction at hydrotest pressure |
| Pressure steps | 0, 25, 50, 75, 100 % of $P_T$, hold, unload to 0 — check linearity and zero return |
| Gauges | Rosettes (3-element) at SCL-B outer surface, 0° and 90° planes; uniaxial in plain shell (hoop, axial) as control |
| Gauge location | ≥ 1 gauge length away from weld toe (or per IIW hot-spot positions 0.4t / 1.0t); record exact positions |
| Predicted values | FEA strains **at gauge locations and directions**, at each pressure step, with expected uncertainty band |
| Acceptance | e.g. control gauges within ±5 %, junction gauges within ±15 % |
| Temperature | Record; compensate (dummy gauge / self-temp-compensated gauges) |
| Data | Raw data retained, calibration certs |

Convert FEA stress to strain at a free surface (plane stress):
$$\varepsilon_1 = \frac{\sigma_1 - \nu\sigma_2}{E}, \quad \varepsilon_2 = \frac{\sigma_2 - \nu\sigma_1}{E}$$
Sample plain shell at $P_T$ = 1.95 MPa, new thickness: hoop 84.3, axial 42.2 MPa → $\varepsilon_\theta$ = (84.3 − 0.3·42.2)/200 000 = **358 µε**, $\varepsilon_z$ = (42.2 − 0.3·84.3)/200 000 = **85 µε**.

Gauges read **surface** strains; FEA linearized values are not surface values — compare the **FEA surface nodal** result at the gauge point (averaged over gauge length).

### 5.3 Correlation report
| Gauge | Location | Predicted (µε) | Measured (µε) | Ratio | Within band? | Comment |
|---|---|---|---|---|---|---|
| G1 | Shell hoop, remote | 358 | | | | control |
| G2 | Shell axial, remote | 85 | | | | control |
| R1-a/b/c | SCL-B outer, long. plane | | | | | junction |

- If control gauges fail → test set-up/instrumentation problem, or material/thickness differs (measure actual thickness by UT!).
- If junction gauges fail but controls pass → model detail (weld size, pad contact, nozzle actual geometry).

### 5.4 Calibration vs validation — don't fool yourself
- **Calibration**: changing model parameters (weld size, contact, E) until the model matches a test. Legitimate if the parameter is genuinely uncertain and the change is physical — but **then that test can no longer validate** the model.
- **Validation**: comparing an **un-tuned** prediction against **independent** data (a different gauge, different load, different vessel).
- Record which data were used for calibration and which for validation.

### 5.5 Does "the hydrotest passed" validate the FEA?
- **No, not by itself.** A hydrotest proves the vessel didn't leak or visibly deform at $P_T$ — it says nothing about the stress distribution, fatigue life, buckling margin or nozzle-load capacity. It's a proof test of the **fabricated** vessel.
- **Yes, partially**, if you measured strains and the un-tuned predictions agreed — for those locations and that load only.

---

## 6. Independent check (by checker / senior)

The checker should be able to reproduce key numbers without your model:
- Hand-calc table (§3.3).
- Re-run of linearization CSVs with `tools/linearize.py`.
- Spot-check of one SCL with the built-in Inventor tool vs the script (should agree within ~1–2 %; differences from bending treatment of shear components and interpolation).
- Review of constraints and load screenshots with **arrows visible**.

See [10 — Review checklist](10-review-checklist.md) for the full list.

---

## 7. References for V&V
- ASME V&V 10-2019, *Standard for Verification and Validation in Computational Solid Mechanics*.
- ASME V&V 10.1-2012, *An Illustration of the Concepts of V&V in Computational Solid Mechanics*.
- ASME V&V 20 (GCI method for numerical uncertainty).
- NAFEMS knowledge base: [The importance of mesh convergence](https://www.nafems.org/publications/knowledge-base/the-importance-of-mesh-convergence-part-1/); [Commercial analysis validation](https://www.nafems.org/publications/knowledge-base/commercial-analysis-validation/).
- Roache, P.J., *Verification and Validation in Computational Science and Engineering*, Hermosa, 1998.
- Oberkampf & Roy, *Verification and Validation in Scientific Computing*, Cambridge, 2010.
- PVEng, [Guidelines for FEA in ASME designs](https://www.pveng.com/wp-content/uploads/2024/10/Guidelines-for-FEA-STI.pdf).

Next: [08 — Inventor Nastran errors and fixes](08-inventor-nastran-errors-and-fixes.md).
