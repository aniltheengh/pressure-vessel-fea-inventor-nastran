# 09 — FEA Report Template (for seniors, checkers, clients, inspectors)

> A reviewer should be able to (1) see exactly what was analysed, (2) reproduce the key numbers, and (3) find a pass/fail for every load case and failure mode — **without opening your model**. Screenshots support tables; they never replace them.

Copy this file into your report and fill the brackets. Delete guidance lines in *italics*.

---

## Cover page

| Field | Entry |
|---|---|
| Document no. / revision | [e.g. FEA-V101-001 Rev 0] |
| Title | Finite Element Analysis of [component] of [vessel tag] |
| Project / client | |
| Vessel tag / drawing no. / drawing rev | [V-101 / GA-1234 Rev C] |
| Code & edition | [ASME VIII-1 2023 with VIII-2 Part 5 2023 (App. 46)] |
| Software / version | Autodesk Inventor Nastran [2025.x], Autodesk Nastran solver [version from .log] |
| Prepared / checked / approved | names, dates, signatures |
| Revision history | Rev, date, description, by |

---

## 1. Summary (one page)

- **Purpose:** *e.g. demonstrate N1 (DN200) nozzle–shell junction with 340×10 pad meets ASME VIII-2 Part 5 elastic stress limits for design, hydrotest and nozzle loads.*
- **Conclusion:** ACCEPTABLE / NOT ACCEPTABLE / ACCEPTABLE WITH CONDITIONS.
- **Governing result:** *e.g. PL+Pb+Q range at SCL-C = 262 MPa vs 414 MPa (ratio 0.63).*
- **Key assumptions/limitations** (3–5 bullets).
- **Actions required** (design changes, operating limits, tests).

Summary acceptance table:

| Load case | Failure mode | Method | Governing location | Value | Allowable | Ratio | Result |
|---|---|---|---|---|---|---|---|
| LC1 Design | Plastic collapse | 5.2.2 elastic | SCL-C | PL = 145 MPa | 207 | 0.70 | PASS |
| LC1 Design | Local failure | 5.3.2 | SCL-C | Σσ = … | 4S = 552 | … | PASS |
| LC2 Design + nozzle loads | Collapse | 5.2.2 | SCL-B | … | … | … | |
| LC3 Hydrotest | Test limits | 4.1.6.2 | … | … | 0.95 Sy | … | |
| LC4 Cyclic | Ratcheting | 5.5.6.1 | … | ΔSn = … | SPS | … | |
| LC4 Cyclic | Fatigue | 5.5.2 screening | — | — | — | — | Not required / Df = … |
| LC5 Vacuum | Buckling | 5.4 Type 1 + UG-28 | Shell | λ = … | ΦB = 2.5 | … | |

---

## 2. Scope

### 2.1 Included
*List components, load cases, failure modes.*

### 2.2 Excluded (and why / where covered)
*e.g. Shell and heads by code formulas (calc ref XXX); flanges are B16.5 rated; brittle fracture per UCS-66 (calc ref); wind/seismic by PV Elite report YYY.*

---

## 3. References

| Ref | Document | Rev |
|---|---|---|
| [1] | GA drawing | |
| [2] | Nozzle detail drawing | |
| [3] | Process datasheet / UDS | |
| [4] | Code calculation (PV Elite / Compress / hand) | |
| [5] | Piping load table | |
| [6] | ASME BPVC VIII-1 / VIII-2 / II-D, edition | |
| [7] | Company FEA procedure | |

---

## 4. Design basis (inputs)

Copy the signed table from [01 §3](01-design-basis-and-codes.md). Must include: pressures (int/ext), temperatures, materials and allowables (with II-D table & edition), CA, tolerances, joint efficiency, loads, cycles.

### 4.1 Material properties used in FEA

| Material | Part | E (MPa) | ν | ρ (t/mm³) | α (1/°C) | S (MPa) | Sy (MPa) | Su (MPa) | Source |
|---|---|---|---|---|---|---|---|---|---|
| SA-516-70 | Shell, heads, pad | 200 000 | 0.3 | 7.85e-9 | 1.2e-5 | 138 | 260 | 485 | II-D [ed.] Table 1A, Y-1, U, TM-1 |

### 4.2 Allowable limits

| Category | Limit | Value (MPa) |
|---|---|---|
| Pm | S | 138 |
| PL | SPL (1.5S used) | 207 |
| PL+Pb | SPL | 207 |
| ΔSn (P+Q) | SPS (3S used) | 414 |
| Triaxial | 4S | 552 |
| Test Pm | 0.95 Sy | 247 |

---

## 5. Load cases

| LC | Description | P (MPa) | Other loads | Thickness | Subcase | Combination per Table 5.3 # |
|---|---|---|---|---|---|---|
| LC1 | Design | 1.5 | Ps, D | Corroded | 1 | (1) |
| LC2 | Design + nozzle loads | 1.5 | + F, M (Table 5.x) | Corroded | 1 + 3 | (2) |
| LC3 | Hydrotest | 1.95 + head | Water weight | New | 2 | test |
| … | | | | | | |

Nozzle load table (with **coordinate system figure**):

| Nozzle | FA (N) | FC (N) | FL (N) | MT (N·mm) | MC (N·mm) | ML (N·mm) | Source |
|---|---|---|---|---|---|---|---|

---

## 6. Hand calculations (independent check)

*Table from [02 §9](02-hand-calculations.md) and the verification comparison from [07 §3.3](07-verification-and-validation.md).* Attach `pv_handcalc.py` output.

---

## 7. Finite element model

### 7.1 Geometry
- Source CAD and model state (e.g. "V101_N1.iam, Model State: Corroded").
- Simplifications and justification (each one!): *e.g. "M20 lifting lug removed: > 1 m from N1, no load in analysed cases."*
- Figure: model overview with dimensions; figure: section through nozzle.

### 7.2 Idealization and elements

| Region | Idealization | Element | Order | Thickness / material |
|---|---|---|---|---|
| Shell, heads near N1 | Solid | CTETRA | Parabolic (10-node) | per CAD (corroded) |
| Remote shell | Shell (if hybrid) | CQUADR | Linear | 8.7 mm |

### 7.3 Mesh
- Global size, local sizes and where (table), total nodes/elements, elements through thickness at each SCL.
- Mesh quality summary (Check Quality output; no poor elements on SCLs).
- Figures: overall mesh; close-up at each SCL.

### 7.4 Boundary conditions
- Table of constraints: location, type, DOF fixed, coordinate system, **justification**.
- Figure with constraint symbols visible.

### 7.5 Loads
- Table of loads per subcase: type, faces, magnitude, direction, CS.
- **End-cap thrust calculation** shown (formula + value).
- Figure(s) with pressure arrows visible on all wetted faces, including nozzle bore.

### 7.6 Contacts / connections
- Table: pair, type, activation distance, justification. Figure.

### 7.7 Solver settings
- Analysis type, subcases, parameters changed from default (list them all; e.g. `DIRSTRESSTYPE`), output requests.

---

## 8. Verification

| Check | Criterion | Result | OK |
|---|---|---|---|
| Solver messages | No FATAL; warnings explained | *list warnings & explanation* | |
| Load balance | OLOAD = SPC sum (±0.1 %) | *values* | |
| Hand-calc comparison | ±5 % | *table from 07 §3.3* | |
| Deformed shape | Physical | Figure | |
| Mesh convergence | GCI ≤ 2 % on reported SCL quantities | *table, p, GCI* | |
| Units | Echo check in .out | | |
| Sensitivity | Conclusion unchanged for … | | |

---

## 9. Results

### 9.1 Overview plots (per load case)
- Displacement magnitude (with scale factor stated).
- von Mises (or stress intensity) contour, **with legend in MPa and max/min locations labelled**.
- Hoop stress in cylindrical CS (verification).

### 9.2 SCL locations
- Figure: SCLs labelled A … F on the geometry (section view).
- Table:

| SCL | Location description | Start (x, y, z) | End (x, y, z) | Length = t (mm) |
|---|---|---|---|---|

### 9.3 Linearized results and assessment

| LC | SCL | Category | Membrane (MPa) | M+B (MPa) | Limit (MPa) | Ratio | Result | Classification note |
|---|---|---|---|---|---|---|---|---|
| LC1 | A | Pm | | | S | | | Remote shell |
| LC1 | B | PL / PL+Pb+Q | | | 1.5S / 3S | | | Junction bending = Q (Table 5.6) |
| … | | | | | | | | |

Include: linearization plots (component vs distance) for governing SCLs, CSV in appendix.

### 9.4 Local failure (5.3.2)

| LC | SCL | σ1 | σ2 | σ3 | Σ | 4S | Ratio | Result |
|---|---|---|---|---|---|---|---|---|

### 9.5 Ratcheting / P+Q range (5.5.6)
State the load states used for the range (e.g. 0 → LC2) and the result table.

### 9.6 Fatigue (5.5)
Screening result (method, numbers) or full fatigue table: cycle type, n, ΔSP, Ke, Kf, Salt, N, n/N, Df.

### 9.7 Buckling (5.4)
Eigenvalues, mode shape figure, ΦB, Type used; UG-28 comparison.

### 9.8 Hydrotest case
Test pressure derivation, results vs test limits.

---

## 10. Discussion
- Where peaks occur and why they are acceptable (classified F; fatigue screening covers).
- Sensitivities and how robust the conclusion is.
- Comparison with WRC 537/297 or code formula where possible.

## 11. Limitations
*e.g. Linear elastic; residual stresses from welding not included; pad modelled bonded at welds only; nozzle loads per piping Rev B — re-check if loads change; corrosion assumed uniform.*

## 12. Conclusions
Clear statement per load case / failure mode; overall acceptability.

## 13. Recommendations
- Design changes (with predicted effect).
- Operating limits (pressure, temperature, cycles).
- Inspection focus areas (e.g. weld toe at N1 inside corner → MT/UT at in-service inspection).
- Testing: strain-gauge locations and predicted values if validation is required ([07 §5](07-verification-and-validation.md)).

## Appendices
- A. Hand calculations (`pv_handcalc.py` output)
- B. Linearization CSVs and `linearize.py` outputs
- C. Mesh convergence data (`convergence.py` output)
- D. Solver `.log` summary (warnings list)
- E. Additional plots
- F. Checker's comments and responses (see [10](10-review-checklist.md))

---

## Figure checklist (every figure must have)
- Title with load case and quantity
- Legend with units (MPa, mm)
- Deformation scale factor (or "undeformed")
- Coordinate system triad
- Max/min markers or labels for values discussed in text
- View orientation stated (e.g. "section at 0° plane")

## Writing rules
- Numbers in tables, not only in images.
- Every assumption has a reason.
- State the **code clause** for every limit.
- One conclusion per load case; no "seems OK".
- Report what you **didn't** check.

Next: [10 — Review checklist](10-review-checklist.md).
