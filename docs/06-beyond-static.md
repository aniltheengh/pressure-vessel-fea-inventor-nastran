# 06 — Beyond Linear Static: When It Is Required and How to Do It

> A linear static run with linearized stresses covers **plastic collapse (elastic route)** and **ratcheting (elastic route)** only. Buckling, fatigue, thermal, dynamic and nonlinear behaviour each need their own analysis — **when the service conditions or the code require it**, not because the software offers it.

ASME VIII-2 Part 5 sections referenced (check your edition): 5.2.2 elastic, 5.2.3 limit-load, 5.2.4 elastic–plastic, 5.3 local failure, 5.4 buckling, 5.5 fatigue (5.5.2 screening, 5.5.3 elastic, 5.5.4 elastic–plastic, 5.5.5 elastic structural stress), 5.5.6 elastic ratcheting, 5.5.7 elastic–plastic ratcheting. Good overview: E2G, ["Fundamentals of Design by Analysis"](https://e2g.com/industry-insights-ar/fundamentals-of-design-by-analysis/).

---

## 0. Decision table — what analysis is needed?

| Condition | Required check | Inventor Nastran analysis | Section |
|---|---|---|---|
| Static pressure + weight, non-standard detail | Plastic collapse, local failure | Linear Static + linearization | 5.2.2, 5.3.2 |
| Elastic limits fail, or classification ambiguous | Collapse without classification | Nonlinear Static (elastic-perfectly-plastic) or elastic–plastic with true curve | 5.2.3 / 5.2.4, 5.3.3 |
| Vacuum, external pressure, axial compression, wind/seismic compression in tall columns, compressive hoop in heads | Buckling | Linear Buckling; Nonlinear Static with imperfections | 5.4 |
| Pressure / temperature cycles (start-ups, batch, pulsation) | Fatigue screening → fatigue | Linear Static (stress ranges) + post-processing | 5.5.2 → 5.5.3/5.5.5 |
| Repeated thermal + pressure loading, high P+Q | Ratcheting | Linear Static (elastic) or Nonlinear (elastic–plastic, cycles) | 5.5.6 / 5.5.7 |
| Thermal gradients, dissimilar metals, hot nozzles, skirt junctions | Thermal stress (Q, F) | Heat Transfer → Linear Static with temperature | 5.2.2, 5.5 |
| Piping loads on nozzles | Local stresses | Linear Static, or WRC 107/537/297 | — |
| Wind, seismic | Global + local (saddles, skirt, anchor) | Linear Static (equivalent static), Normal Modes + response spectrum | Load combinations Table 5.3 |
| Rapid pressure change, water hammer, explosion, vibration | Dynamic | Modal / Transient / Frequency Response | Beyond Part 5 scope; use client spec |
| Creep range temperatures | Creep | Not Part 5 elastic rules — use VIII-2 creep provisions / API 579 Part 10 | — |

---

## 1. Limit-load analysis (VIII-2 5.2.3)

- Material: **elastic–perfectly plastic**, yield strength = $1.5S$ (VIII-2 5.2.3.1 — the "yield" used in limit analysis; check edition), small-displacement theory.
- Loads: factored per **Table 5.4** (e.g. $1.5(P + P_s + D)$ for the first combination).
- Acceptance: the analysis **converges** at the factored load → design acceptable. Non-convergence = collapse load reached below factored load.
- Doesn't cover buckling (small displacement) — check 5.4 separately.
- Inventor Nastran: *Nonlinear Static*, material nonlinear "elasto-plastic" (bilinear with tangent modulus ≈ 0 or very small), **large displacement off** for strict limit-load (Autodesk Nastran nonlinear analysis uses large-displacement theory by default — check the nonlinear settings and the KB note in [08](08-inventor-nastran-errors-and-fixes.md)). Ramp load in increments (e.g. 20–50 steps), with bisection allowed.

Practical tips:
- Report load–displacement curve at a monitored node; the curve flattening shows collapse.
- Non-convergence for numerical reasons (contact, poor mesh) is not collapse → see [08: E5074/E5076](08-inventor-nastran-errors-and-fixes.md#26-e5074--e5076--nonlinear-non-convergence).

## 2. Elastic–plastic analysis (VIII-2 5.2.4) — the modern preferred method

- Material: **true stress–strain curve** per Annex 3-D (temperature-dependent yield and tensile), with **large displacement** (geometric nonlinearity) on.
- Loads: **Table 5.5**:
  - Global criterion (collapse): first combination $2.4(P + P_s + D)$; other combinations with wind, seismic, etc. Use your edition's factors.
  - Local criterion (strain): $1.7(P + P_s + D)$ — evaluate 5.3.3 local strain limit.
  - Serviceability: as specified by user (e.g. deformation limits).
- Acceptance: converged solution at factored load (global); strain limit satisfied (local).
- **Local strain limit (5.3.3)**: $\varepsilon_{peq} + \varepsilon_{cf} \le \varepsilon_L$, where $\varepsilon_L = \varepsilon_{Lu}\exp\left[-\left(\dfrac{\alpha_{sl}}{1+m_2}\right)\left(\dfrac{\sigma_1+\sigma_2+\sigma_3}{3\sigma_e} - \dfrac{1}{3}\right)\right]$; $\varepsilon_{Lu}$, $m_2$, $\alpha_{sl}$ from Table 5.7; $\varepsilon_{cf}$ = forming strain (Table 6.1). (Formula from VIII-2 5.3.3 — check edition.)
- Avoids stress classification entirely; usually gives **higher** capacity than elastic route for thick/complex details.
- Inventor Nastran: *Nonlinear Static*, nonlinear material with multilinear (true) stress–strain curve, large displacement on, load steps, output equivalent plastic strain and triaxiality (compute from principal stresses).

## 3. Buckling (VIII-2 5.4)

Three analysis types (5.4.1.2, quoted by [PVEng — Buckling of Dished Heads](https://www.pveng.com/home/fea-stress-analysis/buckling-of-dished-heads/)):

| Type | Method | Design factor |
|---|---|---|
| Type 1 | Linear (eigenvalue) bifurcation, elastic pre-stress | $\Phi_B = 2/\beta_{cr}$ |
| Type 2 | Bifurcation with elastic–plastic pre-stress and nonlinear geometry | $\Phi_B = 1.667/\beta_{cr}$ |
| Type 3 | Collapse analysis (5.2.4) with **imperfections explicitly modelled** | Load factors of Table 5.5 |

Capacity reduction factors $\beta_{cr}$ (5.4.1.3): 0.80 for unstiffened and ring-stiffened cylinders and cones under external pressure (and, per several summaries, axial compression — check your edition, older texts give lower values for axial compression); **0.124 for spherical shells and spherical, torispherical and elliptical heads under external pressure** → $\Phi_B$ = 2.5 for cylinders under external pressure, **16.13 for formed heads**.

**Warning from PVEng's worked example:** for a 24" F&D head under external pressure, Type 1 indicated 237 psi acceptable, while Type 3 (with imperfection from the first buckling mode) gave 76 psi — **Type 1 was unconservative**, and UG-28 hand calc (135 psi) matched Type 3 with factor 2.0. Use Type 3 (or code formulas) for heads.

Inventor Nastran workflow:
1. *Linear Buckling* analysis: apply 1 MPa (unit) external pressure + dead load; request ≥ 5 modes. The eigenvalue $\lambda$ × applied load = elastic buckling load.
2. Check: $\lambda \ge \Phi_B$ (for applied = design load). Sample vessel shell (hand estimate 1.20 MPa collapse, [02 §8](02-hand-calculations.md)): eigenvalue for 0.101 MPa should be ~ 11–13; required $\Phi_B$ = 2.5 → OK by Type 1; confirm with UG-28.
3. For Type 3: create imperfect geometry — scale the first mode shape to the fabrication tolerance (VIII-2 4.4.4 out-of-roundness, e.g. $e$ from Fig. 4.4.x, or 0.5 % of D — use code value), apply it to the mesh (Inventor Nastran has no direct "update geometry from mode shape" button in all versions — options: Nonlinear Buckling analysis type, or export the deformed mesh and re-import via the Nastran deck), then *Nonlinear Static* with large displacement and elastic–plastic material; increase load until non-convergence.
4. Mesh: buckling needs finer mesh than stress (≥ 8–12 elements per buckling half-wave). Shells strongly preferred.
5. Supports: buckling is very sensitive to boundary conditions — model stiffening rings and head stiffness realistically.

Other buckling cases on vessels:
- **Internal pressure knuckle buckling** of large thin torispherical heads (wrinkling due to compressive hoop in knuckle).
- **Axial compression** in tall columns (wind/seismic moment + weight) — check skirt and shell.
- **Saddle horn** and **lug** local buckling (compressive membrane).
- **Vacuum during steam-out** — often forgotten.

## 4. Fatigue (VIII-2 5.5)

### 4.1 Screening first (5.5.2)
VIII-2 5.5.2 provides screening methods (Method A: based on experience with comparable equipment / simple cycle counts — e.g. criteria in Table 5.9 / 5.10; Method B: based on design fatigue curves with limits on pressure-cycle range, thermal cycles, etc.). If the vessel passes screening, a detailed fatigue analysis is not required. Document which method and the numbers. (Example walk-through: PVEng ["ASME VIII-2 Permissible Cycle Life"](https://www.pveng.com/home/fea-stress-analysis/asme-viii-2-permissible-cycle-life/).)

Typical triggers for detailed fatigue: > ~1000 full-pressure cycles over life for integral construction with welds (depends on method and $S_u$), frequent thermal transients, pulsating service, cyclic nozzle loads, batch reactors, PSA vessels, autoclaves, hydrogen storage.

### 4.2 Elastic fatigue analysis (5.5.3) — outline
1. Define the cycle histogram (e.g. 73 000 cycles 0 → 1.2 MPa; 200 start-up cycles 20 → 100 °C).
2. Linear static runs for each load state; build stress **ranges** of all six components at the critical point ($\Delta\sigma_{ij}$). Superposition of subcases is valid for linear analysis.
3. Effective equivalent stress range: $\Delta S_{P,k}$ (von Mises of the component ranges, including peak $F$).
4. Fatigue penalty factor $K_{e,k}$ if $\Delta S_{n,k}$ (primary + secondary, i.e. linearized) $> S_{PS}$ (5.5.3 / Eq. 5.36–5.38 region; check).
5. Alternating stress $S_{alt,k} = \dfrac{K_f K_{e,k} \Delta S_{P,k}}{2}$ ($K_f$ = fatigue strength reduction factor for welds, Table 5.11/5.12 depending on weld quality and NDE; if the FEA already models the weld toe geometry with notch, $K_f$ may be 1 — follow 5.5.3).
6. Correct for modulus: $S_{alt}\times(E_{FC}/E_T)$.
7. Read allowable cycles $N_k$ from design fatigue curve (Annex 3-F, smooth bar curves with polynomial fits).
8. Miner's rule: $D_f = \sum n_k/N_k \le 1.0$.

### 4.3 Structural stress method (5.5.5) — for welds
- Uses **mesh-insensitive structural stress** (Battelle/Dong method) at the weld toe from nodal forces (needs **GPFORCE** output in Inventor Nastran) or linearized membrane + bending at the toe.
- Master S–N curve, thickness and bending-ratio corrections.
- Recommended for welded joints — less sensitive to mesh than peak stress.

### 4.4 Inventor Nastran notes
- Inventor Nastran's built-in fatigue analysis uses generic S–N/ε–N approaches; **it does not implement VIII-2 5.5 directly.** Use it only for trends. Do the code calculation in a spreadsheet/script from the linear stress results.
- Export the six components at the hot spot for each subcase (Probe / Nodes > Query → CSV).

## 5. Ratcheting (VIII-2 5.5.6 elastic, 5.5.7 elastic–plastic)

- **Elastic (5.5.6.1):** primary + secondary equivalent stress **range** $\Delta S_{n,k} \le S_{PS}$ (see [05 §3](05-stress-linearization-and-classification.md)). If violated, either simplified elastic–plastic (5.5.6.3, with $K_e$ penalty for fatigue) or elastic–plastic ratcheting analysis.
- **Thermal stress ratchet in shells (5.5.6.3 / Bree diagram concept):** for combined steady pressure + cyclic linear thermal gradient: the allowable thermal range depends on $x = \sigma_m/S_y$ (pressure membrane over yield): $\Delta Q_{allow}$ = $S_y(1/x)$ for $0 < x < 0.5$, $4S_y(1 - x)$ for $0.5 < x < 1.0$ (VIII-2 5.5.6.3; check — this is the classic Bree result written in code form).
- **Elastic–plastic (5.5.7):** apply ≥ 3 complete cycles with elastic–perfectly plastic material ($S_y$ at temperature), small displacement. Pass if any of: no plastic strain in the 3rd cycle; elastic core in the primary-load-bearing boundary; no permanent change in overall dimensions over the last cycles.
- Inventor Nastran: Nonlinear Static with multiple load steps that load and unload (time-dependent load curves), elastic–perfectly plastic material.

## 6. Thermal stress

| Source | Classification | How to model |
|---|---|---|
| Uniform temperature, free expansion | No stress | — |
| Linear gradient through wall | $Q$ (bending part), $F$ (non-linear part) | Heat Transfer → Linear Static |
| Axial gradient (e.g. skirt-to-head junction "hot box") | $Q$ | Heat Transfer, fine mesh in skirt |
| Hot nozzle in cold shell | $Q$ + $F$ | Transient thermal for start-up |
| Dissimilar materials (SS nozzle in CS shell, cladding) | $Q$ / $F$ | Two materials, α difference |
| Restrained by supports (fixed saddles!) | Often **artificial** | Fix the support model |

Through-wall linear gradient bending stress (flat plate approximation): $\sigma = \dfrac{E\alpha\Delta T}{2(1-\nu)}$ (surface, from mean). Example: CS, $\Delta T$ = 20 °C: $200000\times1.2\text{e-}5\times20/(2\times0.7)$ = **34 MPa** — significant for fatigue.

Inventor Nastran workflow: Heat Transfer analysis (steady-state or transient) → in the structural analysis, apply *Temperature > From Output* (load type listed in Loads help) to use the computed temperature field; set reference (stress-free) temperature; materials need α and temperature-dependent E if significant.

## 7. Nozzle external loads — WRC 107 / 537 / 297 vs FEA

| Method | Scope | Limits / notes |
|---|---|---|
| **WRC 107** (1965, rev. 1979) | Local stresses in **cylindrical and spherical shells** from radial load, moments, torsion, shear on rigid attachments | Empirical curves (Bijlaard); parameters $\beta = 0.875\,r_o/R_m$, $\gamma = R_m/T$; limits on $\beta$, $\gamma$; ignores nozzle flexibility; no pressure interaction; no stresses in nozzle |
| **WRC 537** (2010) | Same method as WRC 107 with digitised curves and clarifications (precision equations) | Replaces WRC 107 in most software (PV Elite, Compress) |
| **WRC 297** (1984) | Cylinder-to-cylinder (nozzle in shell), includes **nozzle** stresses, flexible nozzle | $d/D \le 0.5$ (approx.) and other parameter limits |
| **WRC 368** | Pressure stresses at nozzles (complements 297 for P + loads) | |
| **PD 5500 Annex G** | Local loads on cylinders/spheres | UK practice |
| **EN 13445-3 Clause 16** | Local loads on nozzles in cylinders/spheres; interaction formula with pressure | EN practice |
| **FEA** | Any geometry, combined with pressure, pads, closely spaced nozzles, hillside | Needs linearization and classification; preferred when outside WRC limits, $d/D > 0.5$, pads with large loads, thin shells ($\gamma$ > 300), or loads near other discontinuities |

FEA set-up for nozzle loads (Inventor Nastran):
- Local coordinate system at nozzle (axial = radial direction of shell; C = circumferential, L = longitudinal — match the piping engineer's convention!).
- Load at end of nozzle via RBE3 (interpolation) or RBE2 at flange; nozzle length ≥ $2.5\sqrt{r_n t_n}$ (use more to be safe).
- Separate subcases: pressure only; each nozzle load component → combine by superposition; check sign combinations (± loads) for the worst case.
- Classification near nozzle (Table 5.6): membrane from external loads = $P_L$; bending = $Q$ — **but** for external loads, many companies classify bending as primary ($P_b$) near the nozzle if it is needed for equilibrium — state your choice.
- Compare against WRC 537 for one load case as a benchmark (difference within ~20–30 % is typical where both are valid).

## 8. Wind and seismic

- Global: column/skirt bending moment from wind (ASCE 7, EN 1991-1-4, Japanese Building Standard Law / AIJ) or seismic (ASCE 7, Japanese High Pressure Gas seismic standard 高圧ガス設備等耐震設計基準, if applicable). Usually done by hand/PV software → gives longitudinal stress, check vs allowable / buckling.
- FEA needed for: saddle supports under seismic, lug/leg supports, skirt opening (access openings), anchor chair/base ring.
- Equivalent static method: apply horizontal acceleration $k_h g$ as gravity component, plus vertical $k_v g$.
- Response spectrum: Normal Modes → Response Spectrum analysis (licence-dependent in Inventor Nastran).
- Code combination factors (e.g. $0.7E$ in some combinations) from Table 5.3 / ASCE 7.

## 9. Dynamic loads

- **Natural frequency check** (Normal Modes): tall columns vs vortex shedding; vessels near reciprocating compressors (pulsation); stay away from excitation frequencies (common target: ±20 %).
- **Transient pressure** (water hammer, deflagration): ASME VIII-2 Part 5 is static; for impulsive loads use dynamic analysis and dynamic load factors; for explosion containment see VIII-3 Article KD-12 or client spec.
- **Earthquake time history**: rarely for ordinary vessels; follow project spec.

## 10. Summary — minimum set for a typical non-standard vessel detail

| Check | Usually required? |
|---|---|
| Linear static + linearization (5.2.2), all Table 5.3 combinations | Yes |
| Local failure triaxial check (5.3.2) | Yes (quick) |
| Hydrotest case | Yes |
| Fatigue screening (5.5.2) | Yes — documented even if "not required" |
| Buckling | If any compressive membrane (vacuum, external P, axial compression, knuckle) |
| Ratcheting elastic check (5.5.6) | Yes when P+Q is computed |
| Thermal | If gradients or dissimilar materials |
| Elastic–plastic / limit load | If elastic route fails or classification ambiguous |
| Nozzle loads | If piping attached |
| Wind / seismic local effects | For supports |

Next: [07 — Verification and validation](07-verification-and-validation.md).
