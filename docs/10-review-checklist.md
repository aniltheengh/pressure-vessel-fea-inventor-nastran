# 10 — Checker's Review Checklist (80 items)

> For the analyst before submitting, and for the senior / independent checker. Mark each: ✓ OK, ✗ not OK (comment), N/A (with reason). A report with any open ✗ is not approved.

Reference: compiled from ASME VIII-2 Part 5 requirements, PVEng FEA guidelines, NAFEMS good-practice guidance and the files in this guide.

---

## A. Scope and design basis (1–12)

| # | Check | ✓/✗/NA | Comment |
|---|---|---|---|
| 1 | Report purpose and scope clearly stated; excluded items listed with where they are covered | | |
| 2 | Governing code, edition and addenda named; DBA route agreed (App. 46 / U-2(g) / EN 13445 Annex C / JIS) | | |
| 3 | Drawing numbers and revisions match the latest issued drawings | | |
| 4 | Design pressure (internal and external) and design temperatures match datasheet | | |
| 5 | Static head included where relevant | | |
| 6 | Material specs/grades match drawing & material list | | |
| 7 | Allowable stress S from correct II-D table (1A for VIII-1, 5A for VIII-2) at correct temperature | | |
| 8 | Sy, Su, E, α at correct temperature; source table quoted | | |
| 9 | Corrosion allowance applied on correct side(s); corroded geometry for design case | | |
| 10 | Mill under-tolerance and forming thinning considered | | |
| 11 | Joint efficiency / weld factors consistent with NDE extent | | |
| 12 | Cyclic service defined (cycles, ranges) or explicitly "non-cyclic" | | |

## B. Load cases (13–22)

| # | Check | ✓/✗/NA | Comment |
|---|---|---|---|
| 13 | All Table 5.3 (or applicable) combinations considered or justified as non-governing | | |
| 14 | Hydrotest case included, test pressure per correct clause, test orientation correct | | |
| 15 | Nozzle loads from current piping revision; units converted; coordinate convention matches piping | | |
| 16 | ± sign combinations of nozzle loads checked for worst case | | |
| 17 | Dead weight, contents, insulation, internals included where relevant | | |
| 18 | Wind / seismic local effects on supports addressed or referenced | | |
| 19 | Vacuum / external pressure considered | | |
| 20 | Thermal loads considered (gradients, dissimilar materials) | | |
| 21 | Lifting / transport cases if in scope | | |
| 22 | Load-case table complete and matches subcases in model | | |

## C. Geometry and idealization (23–32)

| # | Check | ✓/✗/NA | Comment |
|---|---|---|---|
| 23 | Model geometry matches drawing (key dimensions spot-checked: D, t, nozzle size/projection, pad size, weld sizes) | | |
| 24 | Simplifications listed and justified; none in the load path near evaluated regions | | |
| 25 | Weld geometry modelled where stresses are evaluated (fillet legs) | | |
| 26 | Extent of model sufficient (cut boundaries ≥ 2.5√(Rt) from evaluated features) | | |
| 27 | Shell/solid choice justified; R/t considered | | |
| 28 | Shell models: mid-surface location / offsets correct; thickness per region correct | | |
| 29 | Symmetry used only where geometry, loads and response are symmetric | | |
| 30 | Symmetry constraints correct for element type (shell rotations) | | |
| 31 | Reinforcing pad modelled realistically (welds only / separation) or conservatism justified | | |
| 32 | Model state / configuration (new vs corroded) recorded for each analysis | | |

## D. Materials, constraints, loads, contacts (33–48)

| # | Check | ✓/✗/NA | Comment |
|---|---|---|---|
| 33 | Every part has the correct material; no "Generic"; G left blank | | |
| 34 | Units consistent (mm–N–MPa–tonne); density units correct | | |
| 35 | Constraints represent the real supports; justification given | | |
| 36 | No over-constraint (fixed faces blocking growth, both saddles fixed, fixed nozzle flanges) | | |
| 37 | Rigid-body motion fully prevented (3-2-1 minimum where needed) | | |
| 38 | Reaction forces at artificial constraints ≈ 0 for self-equilibrated loads | | |
| 39 | Pressure applied to ALL wetted faces (nozzle bores, small fillets) — figure checked | | |
| 40 | Pressure direction correct (deformed shape shows growth) | | |
| 41 | End-cap thrust applied at every cut boundary; calculation shown | | |
| 42 | Hydrostatic load: free surface point, direction, weight density correct | | |
| 43 | Gravity direction and magnitude correct | | |
| 44 | Nozzle loads applied via appropriate connector (RBE2/RBE3) at adequate distance from junction | | |
| 45 | Contacts defined for every interface; type justified; activation distance adequate | | |
| 46 | No duplicated contacts; pairs include only touching faces | | |
| 47 | Thermal: reference temperature and temperature field correct | | |
| 48 | Parameters changed from defaults are listed and justified (no SOLUTIONERROR in production) | | |

## E. Mesh (49–56)

| # | Check | ✓/✗/NA | Comment |
|---|---|---|---|
| 49 | Parabolic solid elements (or justified shells); no linear tets for stress assessment | | |
| 50 | ≥ 3 elements through thickness at each SCL | | |
| 51 | Local refinement at all evaluated locations | | |
| 52 | Mesh quality check run; no poor elements on SCLs | | |
| 53 | Mesh convergence study for reported quantities; table and GCI given | | |
| 54 | Singularities identified and not used for acceptance | | |
| 55 | Same mesh used for all reported load cases (or each converged) | | |
| 56 | Contact interface meshes of similar size | | |

## F. Solution and verification (57–66)

| # | Check | ✓/✗/NA | Comment |
|---|---|---|---|
| 57 | No fatal errors; all warnings listed and explained | | |
| 58 | Grid point singularity table: only expected DOF auto-constrained | | |
| 59 | Applied load resultant = reaction resultant | | |
| 60 | Gravity reaction = mass × g (compare iProperties) | | |
| 61 | Hand-calc comparison table: plain shell hoop/long membrane within ±5 % | | |
| 62 | Displacements plausible; deformed shape physical | | |
| 63 | Results symmetric where expected | | |
| 64 | Sensitivity of conclusion to key assumptions checked | | |
| 65 | Independent re-calculation of at least one SCL (e.g. `linearize.py` vs built-in tool) | | |
| 66 | Software version and solver version recorded | | |

## G. Assessment (67–76)

| # | Check | ✓/✗/NA | Comment |
|---|---|---|---|
| 67 | SCLs placed at all critical locations (incl. multiple angular positions around nozzles) | | |
| 68 | SCLs normal to mid-surface, full thickness, not through singular points | | |
| 69 | Linearization done on stress **components**, equivalent stress computed after | | |
| 70 | Classification (Pm/PL/Pb/Q/F) justified per Table 5.6; conservative where ambiguous | | |
| 71 | Correct equivalent stress (von Mises for VIII-2 ≥ 2007; Tresca if required by code edition/company) | | |
| 72 | Correct limits (S, SPL, SPS) with stated basis (1.5S/3S or Sy-based) | | |
| 73 | P+Q evaluated as a range between correct load states | | |
| 74 | Local failure (triaxial) check done | | |
| 75 | Buckling addressed where compressive stresses exist | | |
| 76 | Fatigue screening documented; fatigue analysis if required | | |

## H. Report quality (77–80)

| # | Check | ✓/✗/NA | Comment |
|---|---|---|---|
| 77 | Summary table with pass/fail for each load case & failure mode | | |
| 78 | Figures have legends with units, load case titles, scale factors | | |
| 79 | Limitations and recommendations stated | | |
| 80 | Prepared/checked/approved signatures and revision history present | | |

---

## Checker's comment sheet

| Comment # | Item # | Comment | Analyst response | Closed (Y/N) | Checker initials |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

## Top 10 common checker findings (consistent with published FEA guidance)
1. Missing end-cap thrust on nozzles.
2. Uncorroded geometry in design case.
3. Max von Mises at a singularity used as the result.
4. One element through thickness.
5. Fixed constraints creating artificial stresses.
6. Misclassified junction bending (Q vs Pb) without justification.
7. Nozzle loads in wrong units or coordinate system.
8. Pad fully bonded (over-stiff).
9. No mesh convergence evidence.
10. Hydrotest case missing or wrong test pressure.

Next: [11 — Glossary](11-glossary.md).
