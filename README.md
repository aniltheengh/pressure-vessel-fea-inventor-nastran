# Pressure Vessel FEA with Autodesk Inventor Nastran — A Practical Engineering Guide

From drawing to a checked, code-based FEA report: design basis, hand calcs, Inventor Nastran setup, meshing and convergence, stress linearization and classification (ASME VIII-2 Part 5), beyond-static analyses, V&V, solver errors and fixes, a report template, an 80-item checker's checklist, and tested Python tools.

> **Status:** study and working guide written engineer-to-engineer. It is **not** a code document. Clause numbers, factors and allowables are quoted from the sources in [docs/12-references.md](docs/12-references.md) — **always confirm against the code edition named in your contract**, and follow your company's procedures. FEA alone does not certify a vessel or replace a required pressure test.

---

## Who this is for
- Mechanical/design engineers who must defend a pressure-vessel FEA to a **senior, checker, client or inspector**.
- **ANSYS users moving to Inventor Nastran** who keep hitting solver errors (see [08](docs/08-inventor-nastran-errors-and-fixes.md)).
- Engineers in **Japan** working with ASME and JIS (JIS B 8265 / 8267 notes in [01](docs/01-design-basis-and-codes.md)).

## Contents

| # | Document | What you get |
|---|---|---|
| 01 | [Design basis and codes](docs/01-design-basis-and-codes.md) | ASME VIII-1 vs VIII-2 Part 5, EN 13445-3, PED, JIS B 8265/8267, Japanese law; input sheet; allowables; CA; MAWP; load combinations; failure modes |
| 02 | [Hand calculations](docs/02-hand-calculations.md) | Worked sample vessel (1000 mm ID, 1.5 MPa, SA-516-70): UG-27, Lamé, heads, head–shell discontinuity, nozzle area replacement, flanges, hydrotest, end-cap thrust, vacuum estimate |
| 03 | [Inventor Nastran model setup](docs/03-inventor-nastran-model-setup.md) | Step by step: analysis types, solid vs shell, midsurface, materials, symmetry, supports without over-constraint, pressure + end-cap thrust, hydrostatic, nozzle loads, contacts, mesh settings, element types, output requests, parameters |
| 04 | [Meshing and convergence](docs/04-meshing-and-convergence.md) | Convergence procedure, Richardson/GCI with worked tables, singularities, element quality warnings |
| 05 | [Stress linearization and classification](docs/05-stress-linearization-and-classification.md) | Pm/PL/Pb/Q/F, Table 5.6 examples, 5.2.2.4 limits (S, SPL, SPS), SCL placement, Annex 5-A math, Inventor Nastran's Stress Linearization tool and manual workaround, worked nozzle example |
| 06 | [Beyond linear static](docs/06-beyond-static.md) | Limit load, elastic–plastic, buckling (Types 1–3, βcr), fatigue (screening, elastic, structural stress), ratcheting, thermal, WRC 107/537/297 vs FEA, wind/seismic, dynamic |
| 07 | [Verification and validation](docs/07-verification-and-validation.md) | Benchmarks, equilibrium & hand-calc checks, units, sensitivity, strain-gauge test plan, calibration vs validation |
| 08 | [Inventor Nastran errors and fixes](docs/08-inventor-nastran-errors-and-fixes.md) | E5000/E5001/E5004/E5008/E5010, G3005/G3009/G3016/G3017/G3051, T2217, E5074/E5076, S1110, scratch disk, Meshing Failed, licence — with Autodesk KB links; Inventor Nastran vs ANSYS differences; debug workflow |
| 09 | [Report template](docs/09-report-template.md) | Full report structure with required tables and figures |
| 10 | [Review checklist](docs/10-review-checklist.md) | 80-item checker's checklist + comment sheet |
| 11 | [Glossary](docs/11-glossary.md) | Terms, with 日本語 |
| 12 | [References](docs/12-references.md) | Codes, WRC, Autodesk docs/KB, industry articles, books, papers |
| — | [tools/](tools/README.md) | `pv_handcalc.py`, `linearize.py`, `convergence.py`, `test_tools.py`, examples |

---

## The key idea in five lines
1. A finished solve is **not** a valid analysis.
2. Valid = model verified (equilibrium, hand calcs, mesh convergence) **+** results assessed against the governing code (linearized, classified) **+** reviewed by a qualified engineer.
3. Never pass/fail a vessel from the **max von Mises colour plot** — it usually sits on a peak or a singularity.
4. Linear static covers collapse and ratcheting (elastic route) only. Buckling, fatigue, thermal, nonlinear are **separate** checks when service needs them.
5. Matching a test supports the model only for what was measured, and only if predictions were written down **before** the test.

---

## Quick-start checklist (one page)

**Before modelling**
- [ ] Code + edition + DBA route agreed (VIII-2 Part 5 / App. 46 / EN 13445-3 Annex C / JIS) → [01](docs/01-design-basis-and-codes.md)
- [ ] Signed input sheet: P, T, materials, S at temperature, CA, tolerances, loads, cycles → [01 §3](docs/01-design-basis-and-codes.md)
- [ ] Load-case table (design, test, nozzle loads, vacuum, cyclic) → [01 §7](docs/01-design-basis-and-codes.md)
- [ ] Hand calcs done: shell, heads, nozzle, hydrotest, end-cap thrust → [02](docs/02-hand-calculations.md) · `python3 tools/pv_handcalc.py your.json --markdown`

**Model (Inventor Nastran)**
- [ ] Corroded geometry (Model State), defeatured only away from evaluation zones
- [ ] Idealization justified; **parabolic** tets; ≥ 3 elements through wall at SCLs
- [ ] Real materials, G blank, units mm–N–MPa–tonne
- [ ] Every part connected (contacts!) and the model statically stable (3-2-1 / realistic supports)
- [ ] No over-constraint (one saddle sliding; nozzles free with loads)
- [ ] Pressure on **all** wetted faces; **end-cap thrust** on every cut
- [ ] Output: stresses at corners, SPC forces, OLOAD, GPFORCE → [03](docs/03-inventor-nastran-model-setup.md)

**Check**
- [ ] No FATAL; warnings explained → [08](docs/08-inventor-nastran-errors-and-fixes.md)
- [ ] Load = reaction; deformed shape physical; hoop stress = hand calc ± 5 % → [07](docs/07-verification-and-validation.md)
- [ ] Mesh convergence on reported quantities, GCI stated → [04](docs/04-meshing-and-convergence.md) · `tools/convergence.py`

**Assess**
- [ ] SCLs at all critical sections, linearized (built-in tool or `tools/linearize.py`) → [05](docs/05-stress-linearization-and-classification.md)
- [ ] Classified per Table 5.6; limits S / SPL / SPS; local failure 4S
- [ ] Buckling / fatigue screening / thermal / nozzle loads as applicable → [06](docs/06-beyond-static.md)

**Report and review**
- [ ] Report per template; summary pass/fail table → [09](docs/09-report-template.md)
- [ ] Self-check with the 80-item list before submitting → [10](docs/10-review-checklist.md)

---

## Typical workflow and when to stop

```text
Design basis ─► Hand calcs ─► Model ─► Solve ─► Verify ─► Converge ─► Linearize & classify ─► Other failure modes ─► Report ─► Review ─► (Test & correlate)
      ▲                         │                  │          │
      └──────── change ◄────────┴──── fails ◄──────┴──────────┘
```

Stop analysing when:
- every agreed load case **and** failure mode has a documented pass/fail;
- mesh refinement and reasonable changes to uncertain assumptions don't change the conclusion;
- remaining uncertainties are listed for review or testing.

## After you submit
- Senior / independent check ([10](docs/10-review-checklist.md)); answer comments in the comment sheet; rerun if the design changes.
- Before any strain-gauge test: test plan with **predicted values first** ([07 §5](docs/07-verification-and-validation.md)).
- Final acceptance follows the code, the inspector (ASME AI / Notified Body / Japanese inspection body) and company approval.

## Verification, validation, acceptance, certification

| Term | Question |
|---|---|
| Verification | Did we solve the model correctly? |
| Validation | Does the model represent the real vessel? |
| Code acceptance | Does the design meet the code criteria? |
| Certification | Is construction, inspection and approval complete? |

---

## Tools — quick run

```bash
python3 tools/test_tools.py                                              # self-tests (all should PASS)
python3 tools/pv_handcalc.py tools/examples/sample_vessel.json --markdown
python3 tools/linearize.py tools/examples/lame_scl_local.csv --S 138 --category PL
python3 tools/convergence.py tools/examples/convergence_example.csv
```
Python 3.8+, no external packages.

## Repository layout

```text
README.md
docs/
  01-design-basis-and-codes.md
  02-hand-calculations.md
  03-inventor-nastran-model-setup.md
  04-meshing-and-convergence.md
  05-stress-linearization-and-classification.md
  06-beyond-static.md
  07-verification-and-validation.md
  08-inventor-nastran-errors-and-fixes.md
  09-report-template.md
  10-review-checklist.md
  11-glossary.md
  12-references.md
tools/
  README.md  pv_handcalc.py  linearize.py  convergence.py  test_tools.py
  examples/  (inputs, CSVs, saved outputs)
```

## Contributing / your own experience
Found an Inventor Nastran error not covered in [08](docs/08-inventor-nastran-errors-and-fixes.md)? Add it to the troubleshooting log there with the exact message, cause, fix and source link.

## Disclaimer
Provided for education and as a working aid. The author accepts no liability for designs based on it. Use the governing code, current edition, qualified review, and your organisation's QA procedures.
