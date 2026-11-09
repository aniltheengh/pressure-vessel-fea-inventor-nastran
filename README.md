# Pressure Vessel FEA with Inventor Nastran: Workflow and Report Checklist

A practical checklist for taking a pressure vessel or tank from drawing to a reviewed FEA report.
It is a study and working guide, not a code document. Always follow the governing code, its current edition, and your company's procedures.

## 1. Key idea

- A finished solve is **not** a valid analysis.
- Valid means: the model is checked, the results are assessed against the governing code, and a qualified engineer has reviewed it.
- FEA alone does **not** certify a vessel or replace a required pressure test.

## 2. Design basis (before modelling)

- Is it a pressure vessel or an atmospheric storage tank? They can fall under different codes (for example ASME Section VIII versus API 650).
- Governing code, edition, and jurisdiction.
- Design and operating pressure, vacuum or external pressure.
- Design temperature and material allowable stress at that temperature.
- Corrosion allowance; model the **corroded** thickness.
- Materials and weld details.
- Expected number of pressure and temperature cycles.

**Output:** an approved input sheet.

## 3. Load cases

List every one that applies:

- Internal pressure, including closed-end thrust on open nozzles
- Liquid head and self-weight
- Nozzle and piping loads
- Supports: saddles, legs, skirt, lugs
- Wind and seismic
- Thermal expansion
- Hydrotest condition
- Vacuum or external pressure

**Output:** a load-case table.

## 4. Hand calculations first

- Use the code formulas for standard shells, heads, and nozzles.
- Use FEA for what formulas do not cover: heavily loaded or closely spaced nozzles, supports, unusual geometry, cyclic or thermal loads.
- Quick check in a plain shell region away from discontinuities:
  - Hoop stress is about `P·D / (2t)`
  - Longitudinal stress is about `P·D / (4t)`

## 5. Building the model in Inventor Nastran

- Geometry matches the current drawing revision.
- Units are consistent; check them twice.
- Materials have the right modulus, Poisson's ratio, and allowable values.
- Shell or solid elements chosen with a stated reason. Use shells for thin walls and solids for thick details and welds.
- Restraints are realistic and do not over-stiffen the vessel. Avoid fixing whole faces unless the real support does that.
- Pressure applied to all wetted faces, plus end thrust where a nozzle or open end is cut off.
- Contacts (pads, bolted parts) defined deliberately.

## 6. Checks before trusting any plot

- The solver finished without errors or fatal warnings. Read the log.
- Reaction forces balance the applied loads.
- The deformed shape looks physically right (cylinder grows, heads bulge).
- Hand-calc stress matches FEA in a quiet shell region.
- **Mesh convergence:** refine and confirm the stresses used for acceptance stop changing.
- Sharp re-entrant corners give singularities. Those peaks grow forever with refinement; don't chase them.

## 7. Assessing results (not just peak von Mises)

Do **not** pass or fail a vessel from the maximum von Mises colour plot.

For a linear elastic static run (the usual Inventor Nastran case), ASME VIII-2 Part 5 approach:

- Take stress along lines through the wall thickness (stress classification lines).
- Split them into membrane, bending, and peak parts (linearization).
- Compare with code limits. Typical elastic limits, with `S` the allowable stress:
  - General primary membrane: no more than `S`
  - Local primary membrane: no more than `1.5S`
  - Primary membrane plus bending: no more than `1.5S`
  - Primary plus secondary range: no more than about `3S`
- Peak stresses go into the fatigue check, not the primary limits.

Failure modes to cover as applicable:

- Plastic collapse
- Local failure
- Buckling (vacuum, external pressure, compressive loads)
- Fatigue and ratcheting (cyclic service)

Check the exact limits and factors in your governing code edition.

## 8. Is static enough?

| Service condition | Analysis needed |
|---|---|
| Slow pressure and weight loads | Linear static |
| Vacuum, external pressure, compression | Buckling |
| Repeated pressure or temperature cycles | Fatigue |
| Restrained thermal expansion | Thermal stress |
| Vibration, impact, rapid pressure change | Dynamic |
| Large plasticity or changing contact | Nonlinear |

Choose from the real service conditions and the code, not from what the software offers.

## 9. When to stop analysing

- Every agreed load case and failure mode has a documented pass or fail.
- Mesh refinement and reasonable changes to uncertain assumptions don't change the conclusion.
- Remaining uncertainties are listed for review or testing.

## 10. What the report should contain

1. Purpose and scope: what was and wasn't assessed
2. Design basis and inputs, with drawing revision
3. Model description, simplifications, mesh, restraints, loads
4. Verification: reaction balance, hand-calc comparison, mesh convergence
5. Results table: load case, location, criterion, value, margin, pass or fail
6. Conclusions: acceptable, redesign needed, or more evidence needed
7. Limitations
8. Recommendations: design changes, operating limits, proposed tests

Screenshots support the table; they don't replace it.

## 11. After submitting the report

- A senior or independent engineer reviews it.
- Fix comments; rerun if the design changes.
- Before any test, agree a test plan: loading, supports, gauge locations, **predicted values written down first**, and comparison tolerances.
- After the test, add a correlation section: where it matched, where it didn't, and why.
- Final acceptance follows the code, inspection (for a code-stamped vessel, often an Authorized Inspector), and company approval.

## 12. Does matching the test validate the analysis?

- **Yes, partly.** It is validation evidence for the conditions and locations measured, if predictions were made before testing.
- "Held pressure with no leak" proves integrity at that test, not the full stress field, fatigue life, or buckling margin.
- Tuning the model to match one test is calibration. A second, independent test condition gives stronger evidence.

## 13. Verification, validation, acceptance, certification

| Term | Question it answers |
|---|---|
| Verification | Did we solve the model correctly? |
| Validation | Does the model represent the real vessel? |
| Code acceptance | Does the design meet the code criteria? |
| Certification | Is construction, inspection, and approval complete? |

## 14. Inventor Nastran troubleshooting log

Record every error you hit so the fixes become experience:

| # | Error message (exact) | Cause | Fix | Date |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

Tips:

- Read the first error in the log; later ones are often caused by it.
- Common causes in static runs: missing material, unconstrained rigid-body motion, bad or tiny mesh elements, contact problems, or geometry gaps.

## Sources

- [Pressure Vessel Engineering: Guidelines for FEA in ASME designs](https://www.pveng.com/wp-content/uploads/2024/10/Guidelines-for-FEA-STI.pdf)
- [ASME: Design by analysis in Section VIII, Division 2](https://www.asme.org/learning-development/find-course/ippd121-design-by-analysis-requirements-in-asme-bpv-code-section-viii-division-2-alternative-rules)
- [NAFEMS: The importance of mesh convergence](https://www.nafems.org/publications/knowledge-base/the-importance-of-mesh-convergence-part-1/)
- [NAFEMS: Commercial analysis validation](https://www.nafems.org/publications/knowledge-base/commercial-analysis-validation/)
- [Pressure Vessel Engineering: ASME VIII-2 permissible cycle life example](https://www.pveng.com/home/fea-stress-analysis/asme-viii-2-permissible-cycle-life/)
- [Solvo Engineers: Pressure vessel FEA to ASME VIII-2](https://solvoengineers.com/blogs/pressure-vessel-fea-asme-section-viii-division-2)
