# 01 — Design Basis and Codes

> Before you open Inventor Nastran, you need a **design basis**: which code, which edition, which loads, which allowables. An FEA without a design basis is a picture, not an assessment.

**Status of numbers in this file:** formulas and factors are quoted from the codes listed in [12-references](12-references.md). Code editions change. **Always confirm against the edition named in your contract / design specification.** Where a value is only "typical", it is labelled so.

---

## 1. Which code governs?

The jurisdiction (where the vessel is installed) decides, not the analyst's preference.

| Situation | Usual governing document | DBA (FEA) route inside it |
|---|---|---|
| USA / Canada / many Asian, Middle-East EPC projects | ASME BPVC Section VIII Div. 1 (rules) or Div. 2 (alternative rules) | VIII-2 Part 5; VIII-1 via U-2(g) and Mandatory Appendix 46 |
| EU / EEA (CE marking) | Pressure Equipment Directive 2014/68/EU (PED) + harmonised EN 13445 (unfired vessels) | EN 13445-3 Annex B (direct route) and Annex C (stress categorisation) |
| UK | Pressure Equipment (Safety) Regulations 2016 + PD 5500 or EN 13445 | PD 5500 Annex A |
| Japan — vessels under the Industrial Safety and Health Act (労働安全衛生法; ボイラー及び圧力容器安全規則, 圧力容器構造規格) | JIS B 8265 / JIS B 8267 cited as technical basis, plus MHLW notices | JIS B 8266 (特定規格) style DBA, or ASME VIII-2 Part 5 when accepted |
| Japan — High Pressure Gas Safety Act (高圧ガス保安法) | METI technical standards (特定設備検査規則 / 例示基準), which reference JIS B 8265/8267 | As accepted by the inspection body (KHK etc.) |
| Atmospheric storage tank | API 650 / API 620 / JIS B 8501 — **not** a pressure-vessel code | Usually formula-based; FEA for nozzles/settlement |

**Japan-specific notes (you work in Japan):**
- **JIS B 8265:2017** 「圧力容器の構造－一般事項」— design pressure < 30 MPa; allowable stress basis historically more conservative; **hydrotest 1.5 × P × (σt/σa)**, pneumatic factor 1.25 (clause 8.5 b)).
- **JIS B 8267:2015 (amended 2020)** 「圧力容器の設計」— allowable stresses aligned with ASME VIII-1 style safety factor; **hydrotest 1.3 × P × (σt/σa)**, pneumatic 1.1 (clause 8.5 b)). Cylinder formula Annex E.2.2: $t = \dfrac{P D_i}{2\sigma_a\eta - 1.2P}$ for $P \le 0.385\sigma_a\eta$ — identical to ASME UG-27 written in diameter form.
- JIS B 8267 4.3.1 f): "specific materials" (特定材料) taken from ASME use ASME II-D allowables.
- JIS B 8266:2006 「圧力容器の構造－特定規格」— the Japanese design-by-analysis style standard (higher allowables with mandatory detailed analysis). Check whether your customer/inspector accepts it; many Japanese fabricators now follow ASME VIII-2 Part 5 for DBA.
- Which law applies (労安法 vs 高圧ガス保安法 vs 電気事業法 for power plants) decides who inspects and which standard is legally binding. Ask your QA/licensing team — do not guess.

---

## 2. ASME VIII-1 vs VIII-2 vs EN 13445 — what changes for the FEA engineer

| Topic | ASME VIII-1 | ASME VIII-2 (2007 rewrite onward) | EN 13445-3 |
|---|---|---|---|
| Philosophy | Design-by-rule (formulas). FEA only where rules don't cover (U-2(g)) | Design-by-rule (Part 4) **or** design-by-analysis (Part 5) | Design-by-formula (DBF) or design-by-analysis (DBA) |
| Allowable stress basis (carbon steel, below creep) | $S = \min(S_u/3.5,\ 2S_y/3)$ (II-D Appendix 1) | $S = \min(S_u/2.4,\ 2S_y/3)$ (II-D Annex 1 for Div 2 tables) | $f = \min(R_{eH,T}/1.5,\ R_{m,20}/2.4)$ for non-austenitic steels |
| Stress tables | II-D Table 1A / 1B | II-D Table 5A / 5B | EN 13445-2 materials + clause 6 |
| FEA acceptance | Not explicit; usually VIII-2 Part 5 limits applied with VIII-1 S (App. 46) | Part 5: elastic (5.2.2), limit load (5.2.3), elastic–plastic (5.2.4), local failure (5.3), buckling (5.4), fatigue (5.5), ratcheting (5.5.6/5.5.7) | Annex C (stress categories, limits like Pm ≤ f), Annex B (direct route: GPD, PD, I, F, SD design checks) |
| Hydrotest | UG-99(b): $1.3 \times MAWP \times (S_{test}/S_{design})$ | 8.2.1: $\max(1.43\,MAWP,\ 1.25\,MAWP\,(S_T/S))$ | EN 13445-5 / PED Annex I 7.4: $\max(1.25\,P_d\,f_{test}/f_d,\ 1.43\,PS)$ |
| Documentation | Manufacturer's data report | User's Design Specification (UDS) + Manufacturer's Design Report (MDR), certified | Technical file to Notified Body |

**Practical consequence:** if a VIII-1 vessel has a non-standard detail, the common approach is "FEA per VIII-2 Part 5, using VIII-1 allowable S". Get that agreed in writing with the client and the Authorized Inspector **before** you start, because the AI must accept it under U-2(g).

**Mandatory Appendix 46 (VIII-1)** formalises this: Division 2 methods may be used for Division 1 vessels **only where Division 1 has no applicable rules**; Division 1 (UG-23) allowable stresses generally apply, and Part 5 cannot be used to reduce a thickness that a Division 1 formula requires (summary: [Hedderman Consulting — Overview of Appendix 46](https://www.heddermanconsulting.com/blog-1/2020/6/4/an-overview-of-asme-section-viii-division-1-appendix-46); jurisdictions may add conditions, e.g. [ABSA Alberta interpretation IB23-045](https://www.absa.ca/media/2484/ib23-045.pdf)). Read the appendix in your edition.

---

## 3. Design inputs you must collect (input sheet)

Fill this table and get it signed **before** modelling. Copy it into your report (see [09-report-template](09-report-template.md)).

| # | Input | Example (sample vessel used in this repo) | Source document |
|---|---|---|---|
| 1 | Governing code + edition + addenda | ASME VIII-1 2023, Part 5 of VIII-2 2023 for DBA | Contract / UDS |
| 2 | Design pressure (internal), $P$ | 1.5 MPa(g) at top | Process datasheet |
| 3 | Static head at bottom (liquid) | $\rho g h$ = 1000·9.81·2.0 m ≈ 0.020 MPa | Datasheet |
| 4 | External pressure / vacuum | Full vacuum 0.101 MPa? (yes/no) | Datasheet |
| 5 | Design temperature (max / MDMT) | 100 °C / −10 °C | Datasheet |
| 6 | Material spec, grade, product form | SA-516 Gr 70 plate (shell, heads), SA-106 Gr B (nozzle) | Material list |
| 7 | Allowable stress at design temp, $S$ | 138 MPa (20.0 ksi) — **typical II-D Table 1A value for SA-516-70 at moderate temperature; read your edition** | ASME II-D |
| 8 | Allowable at test temp | 138 MPa | ASME II-D |
| 9 | Yield $S_y$, tensile $S_u$ (for DBA) | 260 MPa / 485 MPa minimum (SA-516-70 room temp spec minimums) | Material spec / II-D Table Y-1, U |
| 10 | E-modulus, Poisson, density, expansion | 200 GPa (≈ 202 GPa at 20 °C in II-D TM-1 for C-steel; check), 0.3, 7850 kg/m³ | II-D TM tables |
| 11 | Corrosion allowance (CA) | 3.0 mm internal | Process / client spec |
| 12 | Mill under-tolerance | 0.3 mm for plate (SA-20 allows 0.3 mm or 6 %, whichever smaller — check) | Material spec |
| 13 | Forming thinning of heads | e.g. 10–15 % at knuckle — get from head supplier | Head maker |
| 14 | Joint efficiency $E$ | 1.0 (full RT) or 0.85 (spot RT) | UW-12 |
| 15 | Nozzle loads (F, M) | Piping vendor table or WRC 107/537 standard loads | Piping stress report |
| 16 | Supports | 2 saddles at 0.2L from tangent / legs / skirt | GA drawing |
| 17 | Wind, seismic | ASCE 7 / JIS / Building Standard Law of Japan seismic coefficient | Site data |
| 18 | Cyclic service | e.g. 10 cycles/day × 20 years = 73,000 cycles | Operating philosophy |
| 19 | Lethal / toxic service, PWHT | yes/no | Process |
| 20 | Hydrotest position & fluid | Horizontal in shop, water 15 °C | Fabrication plan |

---

## 4. Allowable stress — where it really comes from

### ASME VIII-1 (II-D Table 1A)
- Below the creep range, carbon steel: lowest of
  - $S_u/3.5$ (tensile at room temp and at temperature, with factor 1.1 on trend curve),
  - $\tfrac{2}{3}S_y$ at room temp and at temperature.
- SA-516 Gr 70: $S_u$ = 485 MPa (70 ksi) → $485/3.5$ = 138.6 MPa; $\tfrac{2}{3}\times 260$ = 173 MPa → **S ≈ 138 MPa** at low/moderate temperature. As temperature rises, the time-dependent and $S_y(T)$ terms reduce it. **Read the actual table row for your temperature — never interpolate from memory.**

### ASME VIII-2 (II-D Table 5A)
- Lowest of $S_u/2.4$ and $\tfrac{2}{3}S_y$ (time-independent).
- SA-516-70: $485/2.4$ = 202 MPa; $\tfrac{2}{3}\times260$ = 173 MPa → **S ≈ 173 MPa** (≈ 25.3 ksi) at room temp; lower at temperature. Check Table 5A.
- Part 5 elastic limits use this **S**. Do **not** mix VIII-2 S with VIII-1 rules or vice versa unless the code says so (App. 46 explicitly tells you which S to use).

### EN 13445-3
- Non-austenitic steels: $f_d = \min\left(\dfrac{R_{p0.2/T}}{1.5},\ \dfrac{R_{m/20}}{2.4}\right)$; test: $f_{test} = R_{p0.2/T_{test}}/1.05$.
- Austenitic steels have different formulas depending on elongation (A ≥ 30 % / 35 %).

### Which S in FEA?
| Situation | Use |
|---|---|
| Design condition, VIII-2 Part 5 elastic | $S$ at design temperature (Table 5A) |
| Design condition, VIII-1 + App. 46 | $S$ from Table 1A at design temperature (check App. 46 wording) |
| Hydrotest condition, VIII-2 | 4.1.6.2 test limits: $P_m \le 0.95 S_y$, $P_m+P_b \le 1.43 S_y$ ... (check edition; for $P_m + P_b$ the limit depends on $P_m$) |
| Elastic–plastic (5.2.4) | No S; uses true stress–strain curve (Annex 3-D) with load factors |
| Fatigue | Design fatigue curves (Annex 3-F) with $E$ correction |

---

## 5. Corrosion allowance, tolerances, and what thickness to model

**Rule: model the thickness that exists at the end of life for the strength check.**

| Check | Thickness to model | Why |
|---|---|---|
| Design condition (primary stress, collapse) | Nominal − CA − mill under-tolerance − forming thinning | Weakest credible state |
| Hydrotest (new vessel) | Usually **uncorroded** (new) thickness | Test is done on new vessel; ASME UG-99 uses MAWP based on corroded thickness to set pressure |
| Weight, wind, seismic | Uncorroded for mass (heavier), corroded for strength | Conservative both ways |
| Fatigue | Corroded (or justify) | Stress range higher |
| Stiffness for nozzle loads from piping | Report both if piping analyst needs stiffness | |

- Corrosion allowance is applied on the **wetted side**: internal CA increases inside radius $R \to R + CA$ and reduces $t$.
- In Inventor, keep **two configurations** (iParts / Model States: "New" and "Corroded"). Model States (Inventor 2022+) are the cleanest way to keep both in one file.

---

## 6. MAWP, design pressure, operating pressure

| Term | Meaning |
|---|---|
| Operating pressure | Normal running pressure |
| Design pressure | Set by process: typically operating + margin (e.g. +10 % or +0.18 MPa, whichever greater — company practice, not code) |
| MAWP | Max allowable pressure at **top of vessel**, in **corroded** condition at design temperature, calculated from the weakest part |
| Set pressure of relief valve | ≤ MAWP (UG-125 / ASME VIII-1 overpressure rules; Part 9 in VIII-2) |
| Test pressure | From code formula (Section 1 table above) |

- MAWP is calculated **backwards** from the actual thickness of each component, minus static head at that component. The lowest one governs.
- FEA can establish MAWP for a non-standard component: run at design $P$, read the linearized stress ratio, or (better) run limit-load / elastic–plastic analysis to get the collapse pressure and divide by the load factor.

Sample vessel (see [02-hand-calculations](02-hand-calculations.md)): shell MAWP from UG-27 with 8.7 mm available thickness = **2.36 MPa**; design pressure 1.5 MPa.

---

## 7. Load cases and combinations

### 7.1 Loads (ASME VIII-2 Table 5.1 terminology)

| Symbol | Load |
|---|---|
| P | Internal / external design pressure |
| Ps | Static head from liquid |
| D | Dead weight: vessel, contents, insulation, internals, attached equipment |
| L | Live loads: e.g. platforms, people, snow |
| E | Earthquake |
| W | Wind |
| S | Snow |
| T | Self-restraining thermal loads / displacements |
| F | Loads from fluid flow / surge (where applicable) |

### 7.2 Combinations
- **Elastic analysis (5.2.2): Table 5.3** — load case combinations such as:
  1. $P + P_s + D$
  2. $P + P_s + D + L$
  3. $P + P_s + D + L + T$
  4. $P + P_s + D + S$
  5. … further combinations adding wind W, earthquake E and snow S with reduced (less than 1.0) companion factors, and an uplift-type case with reduced dead load.
  (List is illustrative and paraphrased — **copy the exact Table 5.3 from your edition into the report**; the factors have changed between editions.)
- **Limit-load (5.2.3): Table 5.4** — factored, e.g. $1.5(P + P_s + D)$.
- **Elastic–plastic (5.2.4): Table 5.5** — global criterion first combination $2.4(P + P_s + D)$; local (strain) criterion $1.7(P + P_s + D)$; serviceability $1.0$. (Source: VIII-2 Table 5.5; also summarised by E2G "Fundamentals of Design by Analysis".)
- Thermal stresses T are **secondary**: they do not enter primary (collapse) checks but enter $P+Q$ range, ratcheting and fatigue.

### 7.3 Load-case table template

| LC | Name | P (MPa) | Ps | D | Nozzle loads | Wind/Seismic | T | Assessment |
|---|---|---|---|---|---|---|---|---|
| LC1 | Design | 1.5 | yes | yes | yes | — | — | Primary (Pm, PL, PL+Pb) |
| LC2 | Design + nozzle | 1.5 | yes | yes | max F/M | — | — | Primary + P+Q |
| LC3 | Hydrotest | 1.95 | water full | yes | none | — | — | Test limits |
| LC4 | Operating cycle | 0 ↔ 1.2 | yes | yes | yes | — | yes | P+Q range, fatigue |
| LC5 | Vacuum | −0.101 | — | yes | — | — | — | Buckling |
| LC6 | Seismic | 1.5 | yes | yes | yes | 0.7E | — | Primary with occasional factors |

---

## 8. Failure modes the design basis must address

ASME VIII-2 5.1.1.2 lists the failure modes Part 5 protects against:
1. **Plastic collapse** (gross distortion) — Pm, PL, Pb limits or limit-load / elastic–plastic.
2. **Local failure** (triaxial strain exhaustion) — 5.3: elastic $\sigma_1+\sigma_2+\sigma_3 \le 4S$, or elastic–plastic strain limit.
3. **Collapse from buckling** — 5.4.
4. **Failure from cyclic loading** — fatigue (5.5) and ratcheting (5.5.6/5.5.7).

The design basis states **which** of these apply and **why** the others don't (e.g. "fatigue screening per 5.5.2 shows fatigue analysis not required").

---

## 9. Other inputs people forget

- **Weld joint category and NDE extent** → joint efficiency E and fatigue weld factor.
- **PWHT**: required by thickness (UCS-56) or service; affects material properties, not linear FEA directly, but affects fatigue (residual stress) and the test plan.
- **Impact testing / MDMT** (UCS-66) — FEA doesn't cover brittle fracture; say so in scope.
- **Nozzle loads**: get the actual piping loads; "zero nozzle loads" is rarely true.
- **Lifting and transport** (tailing lugs, trunnions): often a separate FEA case with dynamic factor (e.g. 1.5–2.0, company/transport spec).
- **Fluid density for hydrotest when vessel is vertical but tested horizontal** — head is different.
- **Internals**: trays, baffles, demisters — weight and attachment local stress.

---

## 10. Output of this step
- Signed design-basis sheet (Section 3 table).
- Load-case table (Section 7.3).
- List of failure modes to check and methods (Section 8).
- Agreement with the client/AI/inspector on the DBA route (VIII-2 Part 5 / EN 13445-3 Annex C / JIS).

Next: [02 — Hand calculations](02-hand-calculations.md).
