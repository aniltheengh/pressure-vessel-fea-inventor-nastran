# 03 — Inventor Nastran Model Setup (step by step)

> Goal: a model that is **statically stable, correctly loaded, realistically supported, and meshed fine enough where you evaluate** — and nothing else. Most "Inventor Nastran is crappy" moments are actually one of the ten problems in this file.

Menu names are from Autodesk Inventor Nastran 2023–2026 help ([User's Guide](https://help.autodesk.com/view/NINCAD/2025/ENU/)). Older Nastran In-CAD (≤ 2019) is similar. If a command is missing in your version, search the help for its name.

---

## 0. Before you start — Inventor housekeeping

- [ ] Geometry matches the **current drawing revision** (write the revision in the analysis name, e.g. `V-101_RevC_Design`).
- [ ] Use **one consistent unit system**. Recommended: **mm, N, MPa, tonne, s** (see §12). Check: *Tools > Document Settings > Units* in Inventor, and the units shown in the Nastran material dialog.
- [ ] Use **Model States** (Inventor 2022+) or iParts for *New* vs *Corroded* thickness and for *defeatured* analysis geometry. Never edit the fabrication model just to make the mesh work.
- [ ] Remove: name plates, small lifting lugs not in load path, chamfers < 1 mm, threads, text, cosmetic welds. Keep: real fillet weld throats at locations you will assess, nozzle–shell intersections, reinforcing pads, head knuckles, saddle wear plates.
- [ ] One body per real part. Overlapping/duplicate bodies make meshing fail (see [08 — Meshing failed](08-inventor-nastran-errors-and-fixes.md#29-meshing-failed)).
- [ ] Split faces now (*3D Model > Modify > Split*) where you will need: symmetry planes, saddle contact areas, SCL locations (an edge along the SCL gives you nodes exactly on it), pressure boundaries at nozzle cut ends.
- [ ] Enter the Nastran environment: *Environments > Autodesk Inventor Nastran*.

---

## 1. Analysis type and subcases

*Analysis panel > New / Edit*.

| Need | Inventor Nastran analysis type |
|---|---|
| Pressure + weight, stresses (normal case) | **Linear Static** |
| Find unconstrained parts / natural frequencies | **Normal Modes** |
| Eigenvalue buckling (vacuum, axial compression) | **Linear Buckling** |
| Plasticity, contact with separation, large deflection, limit load | **Nonlinear Static** |
| Nonlinear collapse / post-buckling | **Nonlinear Buckling** or Nonlinear Static with large displacement |
| Temperature field for thermal stress | **Heat Transfer** (steady state / transient), then map temperatures |
| Pressure pulsation, seismic time history | Direct / Modal Transient, Response Spectrum (check licence level) |
| Fatigue (S–N based) | Fatigue analysis types exist, but **ASME fatigue (VIII-2 5.5) is normally done by hand/script from linear stress ranges** — see [06](06-beyond-static.md) |

**Subcases:** one analysis can hold several subcases (load cases). Use:
- Subcase 1 — Design (P + Ps + D)
- Subcase 2 — Hydrotest
- Subcase 3 — Nozzle loads only (for superposition and P+Q range)

Loads and constraints are assigned per subcase in their dialogs. Linear static results superpose — that is how you build stress **ranges** for P+Q and fatigue.

---

## 2. Idealization: solid vs shell

*Prepare > Idealizations*.

### 2.1 Decision table

| Use **shell** (2D, mid-surface) when | Use **solid** (3D tetrahedra) when |
|---|---|
| $R/t > 10$ (thin wall) and you need membrane + bending directly | $R/t < 10$, thick forgings, flanges, tubesheets |
| Large vessels, global behaviour, saddles, skirts, buckling | Nozzle–shell intersections with fillet welds you must assess |
| You want linearized results without SCL extraction (shell top/bottom = membrane ± bending) | Weld toe, local geometry, peak stress for fatigue |
| Fast convergence studies | Through-thickness (radial) stress matters (thick wall, Lamé) |

**Hybrid** (shell globally + solid submodel at nozzle) is the professional standard for large vessels. Inventor Nastran has no automatic submodel cut-boundary interpolation like ANSYS; do it manually: run global shell model, read displacements at the cut, apply them as *Enforced Motion* on the solid submodel's cut faces, or simply make the solid region big enough (≥ $2.5\sqrt{Rt}$ beyond the feature) and connect it to the shell with *Shell-to-Solid* connection.

### 2.2 Shell modelling in Inventor Nastran
- *Prepare > Midsurface* converts thin solids to mid-surfaces and creates shell idealizations automatically.
- Or model surfaces in Inventor and create an idealization: *Type = Shell*, select faces, enter **thickness** (enter the **corroded** thickness for design case).
- Shell **offset**: if you mesh the inside or outside surface instead of the mid-surface, apply offset (or the diameter is wrong by t). Check radius = $R_i + t/2$.
- **Linear shells (CQUADR/CTRIAR, with drilling DOF)** are recommended by Autodesk for most analyses ([Self-training §7 Meshing](https://help.autodesk.com/cloudhelp/2025/ENU/NINCAD-SelfTraining/files/GUID-2CB5E408-C795-41EE-9F83-B311BFD99FB0.htm)).
- **Membrane/bending output for shells** is controlled by Nastran parameters **DIRSTRESSTYPE** and **EQVSTRESSTYPE** (0 = total, 1 = bending only, 2 = membrane only). To see membrane and bending separately you run the analysis once per setting ([Autodesk article](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Extracting-membrane-and-bending-stresses-from-results-in-Nastran.html)). Note: Inventor labels both bending-only and membrane-only as "SHELL VON MISES-M STRESS" — "-M" does not mean membrane.
- Shell junctions (nozzle–shell, head–shell): mid-surfaces must **touch** and share edges. Use *Continuous Meshing* in Mesh Settings so nodes match, instead of bonded contact.
- Shells cannot model fillet weld size properly; they over-predict stiffness at T-joints (overlap of mid-surfaces) — a known limitation; the stress at the intersection line is not usable for fatigue. Use solid submodel or extrapolate to $0.4t$/$1.0t$ (hot-spot method, IIW / VIII-2 5.5.5 structural stress).

### 2.3 Solid modelling in Inventor Nastran
- *Idealization Type = Solid* (default for solid bodies). Assign material.
- Mesher produces **tetrahedra only** (CTETRA 4-node linear or **10-node parabolic**). Inventor Nastran's built-in mesher does **not** create hexahedral (CHEXA) meshes for CAD solids. If you need hex/swept meshes, use Autodesk Nastran with a pre-processor (e.g. Femap, external mesher) — not covered here.
- Always use **Parabolic** (10-node) tets for stress. Linear 4-node tets are "mathematically stiff" — Autodesk itself says use them only for trend studies ([Self-training §7](https://help.autodesk.com/cloudhelp/2025/ENU/NINCAD-SelfTraining/files/GUID-2CB5E408-C795-41EE-9F83-B311BFD99FB0.htm)).
- Through-thickness: at least **3 parabolic elements through the wall** where you linearize (more where bending gradient is steep). Default global size will often give only 1 — you must use local mesh control.
- Solid nodes have only translational DOF (1–3). Rotations at solid nodes are auto-constrained by AUTOSPC; that is normal and not an error.

### 2.4 Axisymmetric?
- Vessel and loads axisymmetric (no nozzles off-axis, no saddles)? In ANSYS you would use a 2D axisymmetric model. **Inventor Nastran has no 2D elements that represent the cross-section of a solid** — only plane stress / plane strain via shell elements ([Autodesk KB: How to represent 2D solid elements](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-represent-2D-solid-elements-in-Nastran-In-CAD.html)), which is not axisymmetric. Practical substitute: a **thin 3D wedge** (e.g. 5–10°) of solid elements with the hoop-direction translation constrained on both cut faces (use a cylindrical coordinate system on the vessel axis), plus one axial restraint.

---

## 3. Materials

*Prepare > Materials*.

| Property | Sample (SA-516-70) | Notes |
|---|---|---|
| E | 200 000 MPa (II-D Table TM-1 gives the temperature-dependent value; ≈ 202 GPa at 20 °C, lower at temperature) | Use value at design temperature for stress; matters little for linear pressure stress, matters for thermal, buckling, flange |
| ν | 0.3 | **Leave G blank** — Nastran computes $G = E/2(1+\nu)$. Entering an inconsistent G causes errors (E5000 series) |
| Density | 7.85e-9 tonne/mm³ (= 7850 kg/m³) | Only needed for gravity, modal. In mm–N–MPa system density is in **tonne/mm³** |
| α (thermal expansion) | 1.2e-5 /°C (typical C-steel; II-D TE tables) | Needed for thermal stress |
| Yield / UTS | 260 / 485 MPa (spec minimum) | Used by Inventor for "safety factor" plots — **ignore those plots for code assessment** |
| Stress–strain curve | Annex 3-D true stress–strain for elastic–plastic | Nonlinear only |

Common mistakes:
- Using Inventor's "Generic" material or "Steel" with unknown values → Autodesk KB lists this as an E5000 cause.
- Wrong density units (7850 entered in a mm system = 10¹² times too heavy → huge gravity loads).
- Different parts with different materials but forgotten assignment (default material).

---

## 4. Symmetry

Use symmetry only if **geometry, loads, constraints and expected response** are all symmetric. Nozzle loads usually are not → model full nozzle region.

| Model | Symmetry plane constraint (plane normal = n) |
|---|---|
| **Solid** | Translation along n = 0. (*Constraint type: Frictionless* on the planar cut face, or custom constraint with only that translation fixed.) |
| **Shell** | Translation along n = 0 **and** the two rotations about in-plane axes = 0 (i.e., rotations about the axes lying in the plane). Custom constraint: fix $T_n$, $R_{t1}$, $R_{t2}$. |

- Half model (one plane): still needs rigid-body restraint in the in-plane directions → add a weak point restraint or use the real support.
- Quarter / eighth models of a vessel with closed heads: symmetry planes alone restrain everything except translation along the axis if only longitudinal planes are used → add a symmetry plane at mid-length or a single axial restraint at a node where there is no stress of interest.
- **Do not** put a symmetry plane through a nozzle with off-plane loads.

---

## 5. Constraints (supports) and rigid-body motion

*Setup > Constraints*. Types include **Fixed**, **Pinned** (cylindrical faces: radial/axial/tangential), **Frictionless** (normal to face), and **user-defined DOF** (any of $T_x, T_y, T_z, R_x, R_y, R_z$, optionally in a local coordinate system).

### 5.1 The rule
A static model must have **zero rigid-body modes** (6 for each unconnected part) and **no artificial stiffening**. Pressure loads on a closed vessel are self-equilibrated — reactions should be ~0 for pressure alone.

### 5.2 Minimum (3-2-1) restraint for a pressure-only closed vessel
For a vessel loaded only by internal pressure (self-equilibrated):
- Node A: fix $T_x, T_y, T_z$
- Node B (on the axis direction from A): fix two translations perpendicular to AB
- Node C: fix one translation to stop rotation about AB
- Put A, B, C at locations **away from** evaluation areas; reactions should be ≈ 0 (check SPC force summary). If the reactions are not ≈ 0, the pressure loading is not closed (missing face, missing end-cap thrust).

Alternative: use symmetry planes (which give no singular point loads).

### 5.3 Real supports

| Support | Good modelling | Over-constraint to avoid |
|---|---|---|
| **Saddles** (horizontal vessel) | Model saddle + wear plate; contact (separation or bonded at wear plate weld) to shell; constrain saddle base. One saddle fixed, the other **sliding axially** (frictionless / free $T_{axial}$) — like the real slotted holes | Fixing the shell bottom strip at both saddles (blocks thermal + pressure axial growth; creates fake axial stress) |
| **Legs** | Model legs as solids or beams; constrain feet; release horizontal translation on all but one if baseplates are slotted | Fixing the shell where legs attach |
| **Skirt** (vertical) | Model skirt to a base ring; fix base ring bottom (or anchor-bolt locations) | Fixing bottom head directly |
| **Lugs on structure** | Constrain lug bolt holes with *Pinned*; release thermal direction where real | Fixed full lug faces |
| **Nozzle end (pipe attached)** | Leave free + apply piping loads; or model pipe length ≥ $2.5\sqrt{r t}$ … $5\sqrt{rt}$ and apply loads at end via connector | Fixing the nozzle flange face (makes nozzle a support!) |

- **Fixed on a face** = infinitely stiff wall. Pressure makes the shell grow; the fixed face can't → artificial bending + singular peak at the constraint edge. Never evaluate stresses within ~$2.5\sqrt{Rt}$ of a fixed face.
- Point constraints → infinite stress at the point (singularity). Fine for rigid-body control, don't evaluate there.

### 5.4 Check
- Run **Normal Modes** with the same constraints: the first frequencies should be physically sensible (not ≈ 0 Hz). Near-zero modes show which part is free — this is Autodesk's own recommended diagnostic for E5000/E5004 ([KB article](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Error-FATAL-ERROR-E5004-STIFFNESS-MATRIX-SINGULAR-OR-NON-POSITIVE-DEFINITE-when-running-an-analysis-in-Nastran-In-CAD.html)).
- After a static run, read the **SPC force summation / OLOAD resultant** in the `.out` file — applied load resultant must equal reaction resultant (see [07](07-verification-and-validation.md)).

---

## 6. Loads

*Setup > Loads*. Types: Force, Moment, Distributed Load, **Pressure**, **Hydrostatic Load**, **Gravity**, **Remote Force**, Bearing Load, Rotational Force, Enforced Motion, Temperature, etc. ([Loads help](https://help.autodesk.com/cloudhelp/2026/ENU/NINCAD-UsersGuide/files/GUID-48CFFD48-7BDB-4CA8-B603-508C42EC687F.htm)).

### 6.1 Internal pressure
- Select **all wetted faces**: shell inside, head insides, **nozzle bores**, pad? (no — pad is outside), internal flanges' wetted faces up to the gasket.
- Use *Face Chain* to select tangent faces in one click; then **rotate the model and check nothing is missed** (a missed nozzle bore or a small fillet face = unbalanced load + local error).
- Direction: positive pressure in Inventor Nastran acts **into** the face (compressive on the selected face). Verify arrows point **outward from the fluid into the wall**. Check by deformed shape: shell must grow radially.
- Corroded vs new: pressure is applied to the inner surface of whichever geometry you are analysing.

### 6.2 End-cap (blow-off) thrust — the #1 missed load
If the model is **cut** anywhere the fluid continues (truncated nozzle, cut-off pipe, a shell segment model), the pressure on the missing closure must be applied as a load on the cut:

| Cut location | Load to apply on cut annulus |
|---|---|
| Nozzle cut end (pipe not modelled) | Axial tensile pressure $p_{eq} = P\,\dfrac{r_i^2}{r_o^2 - r_i^2}$, or force $F = P\pi r_i^2$ as distributed load. Sample N1 (corroded $r_i$ = 103, $r_o$ = 108): **15.1 MPa** or **50.0 kN** |
| Shell segment model with open end | $p_{eq} = P\dfrac{R_i^2}{R_o^2 - R_i^2}$ on the cut ring. Sample: $1.5\times503^2/(511.7^2-503^2)$ = **43.0 MPa** (≈ $\sigma_z$, as expected) |
| Blind flange / cover modelled | Nothing extra — pressure on the cover face does it |

In Inventor Nastran apply it as a **Pressure** with negative sign (tension, pulling away), or as a **Force/Distributed Load** in the axial direction on the cut face. Check the resulting longitudinal membrane stress in the nozzle ≈ $P r_i / (2t_n)$… away from the junction.

If you **fix** the nozzle end instead, the fixed constraint absorbs the thrust: results near the nozzle are wrong. If you leave it free **without** thrust, longitudinal stresses in the nozzle are zero — also wrong.

### 6.3 Hydrostatic head
*Hydrostatic Load* type: select wetted faces, define a point on the free surface, the depth direction, and fluid weight density ([How to define a hydrostatic pressure](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-define-a-hydrostatic-pressure-in-Nastran-In-CAD.html)). In mm–N: water $\rho g$ = 9.81e-6 N/mm³.

### 6.4 Gravity
*Gravity*: 9810 mm/s² in mm–N–tonne units. Requires density. Contents weight: either hydrostatic pressure (correct distribution) or non-structural mass (approximate).

### 6.5 Nozzle (piping) loads
- Apply at the nozzle flange face via a **rigid connector** to a centre node, then Force + Moment at that node; or *Remote Force*.
- **RBE2 (rigid)** makes the nozzle end perfectly rigid (no ovalisation) → OK if the flange is there anyway; the flange is very stiff.
- **RBE3 (interpolation)** distributes load without adding stiffness — better when the end is a pipe cut. In Inventor Nastran the rigid-body connector has rigid vs. interpolation options (check your version's *Connectors > Rigid Body* dialog).
- Keep the load point **≥ $2.5\sqrt{r_n t_n}$** from the junction, so the connector stiffening doesn't affect junction stresses.
- Sign convention: piping loads are usually given in the **nozzle local axes** (WRC 107: P, Vc, VL, Mc, ML, MT) — create a local coordinate system at the nozzle.

### 6.6 Thermal
- Uniform temperature on a uniform-material vessel with free supports → **zero stress**. If you see thermal stress, a constraint is blocking growth.
- Real thermal stress: temperature gradients (through wall, nozzle hot fluid, skirt junction "hot box"), dissimilar materials (SS nozzle in CS shell). Run Heat Transfer → use the temperature field in the structural subcase.
- Reference temperature: set correctly (stress-free temperature, usually 20–21 °C).

---

## 7. Contacts and connections

*Setup > Contacts > Automatic / Manual / Solver*. Inventor Nastran contact types include **Bonded**, **Separation**, **Sliding/No Separation**, **Separation/No Sliding**, **Offset Bonded**, **Shrink Fit** variants, **Welded** (check list in your version).

| Situation | Contact choice |
|---|---|
| Parts welded together (nozzle to shell, pad fully welded around edge?) | Prefer **one body / shared topology** or **Continuous Meshing** for shells. Bonded contact is acceptable for linear static if mesh sizes on both sides are similar |
| Reinforcing pad | Pad is welded only on its outer edge and at the nozzle; between pad and shell there is a gap. Linear: bonded at the welds only (split faces); nonlinear: separation on the faying surface. Fully bonded pad over-predicts reinforcement |
| Saddle wear plate to shell | Welded edges → bonded at welds; or fully bonded (common, slightly unconservative for bending) |
| Saddle on concrete | Constraint, not contact |
| Bolted flanges, gaskets | Separation + bolt preload → **nonlinear** |

Key facts from Autodesk KB:
- **Parts are not connected by default.** No contact = free part = E5000/E5004 ([KB](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Error-FATAL-ERROR-E5004-STIFFNESS-MATRIX-SINGULAR-OR-NON-POSITIVE-DEFINITE-when-running-an-analysis-in-Nastran-In-CAD.html)).
- **Maximum activation distance**: for manual contact ≈ 1.1–1.2 × the distance between adjacent nodes (element size + gap); for solver contact slightly larger than the gap and smaller than the thinnest solid (same KB).
- Each contact pair should include only faces that actually touch; mixing faces causes distorted elements (G3051 warnings).
- Separation contact in a *linear static* analysis still iterates and can leave a part unstable in some iteration → add weak springs or ground the part (KB).
- Contact elements can outnumber structural elements and cause S1110 out-of-memory errors ([KB](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Fatal-error-S110-insufficient-memory-to-continue.html)) — merge same-material bodies, use symmetry.

---

## 8. Mesh

*Mesh > Mesh Settings* (Global): **Element Size**, **Element Order** (Linear / Parabolic), Continuous Meshing, *Settings* (advanced: max element growth rate, **Project Midside Nodes**, tolerance), **Mesh Table** (per-part settings), and local refinement via *Mesh Model > Add Mesh Control* (vertex, edge — by size or number of elements — and face) ([Self-training §7](https://help.autodesk.com/cloudhelp/2025/ENU/NINCAD-SelfTraining/files/GUID-2CB5E408-C795-41EE-9F83-B311BFD99FB0.htm)). Mesh control can only make elements **smaller** than the global size.

### 8.1 Starting sizes (then prove by convergence)

| Region | Solid (parabolic tet) | Shell |
|---|---|---|
| Plain shell far from features | $\approx t$ to $2t$ | $\approx \sqrt{Rt}/4$ to $\sqrt{Rt}/2$ |
| Within $2.5\sqrt{Rt}$ of head junction / nozzle | $t/3$ (≥ 3 through thickness) | $\le \sqrt{Rt}/8$ |
| Nozzle–shell weld region, SCL location | $t/4$ to $t/6$ | $\le t$ along intersection |
| Knuckle of torispherical head | $t/3$, ≥ 6–8 elements around knuckle arc | ≥ 8 around knuckle arc |

Sample vessel: $\sqrt{R_m t} = \sqrt{507\times8.7}$ = 66 mm → near-junction shell elements ≤ 8 mm; solid elements through 8.7 mm wall ≤ 2.9 mm.

### 8.2 Settings that matter
- **Parabolic** for solids. **Project Midside Nodes**: improves curved surfaces, but can distort elements on thin curved parts → G3005/G3009 warnings → E5000 ([KB](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/FATAL-ERROR-E5000-in-Nastran-Analysis.html)); if that happens, turn it off or refine.
- **Max element growth rate** lower (e.g. 1.1–1.2) → smoother transition from fine to coarse.
- *Check Quality for all Meshes* (right-click Mesh Model) before solving ([Self-training §7](https://help.autodesk.com/cloudhelp/2025/ENU/NINCAD-SelfTraining/files/GUID-2CB5E408-C795-41EE-9F83-B311BFD99FB0.htm)).
- **Mesh Troubleshooter** when meshing fails ([help](https://help.autodesk.com/cloudhelp/2025/ENU/NINCAD-UsersGuide/files/GUID-DC088A72-D59A-4CC3-B884-9D379E4E673D.htm)).

### 8.3 Element types written to the Nastran deck

| Inventor setting | Nastran element | Use |
|---|---|---|
| Solid, Linear | CTETRA (4-node) | Trend only |
| **Solid, Parabolic** | **CTETRA (10-node)** | Stress (default choice) |
| Shell, Linear | CQUADR / CTRIAR (with drilling DOF) — or CQUAD4/CTRIA3 | Recommended shells |
| Shell, Parabolic | CQUAD8 / CTRIA6 | Curved shells; Autodesk recommends linear |
| Line | CBAR / CBEAM / pipe | Legs, stiffeners, piping stubs |
| Connectors | RBE2 / RBE3 / CELAS (springs) / CBUSH | Load introduction, stabilisation |

CHEXA / CPENTA exist in the solver but the Inventor mesher won't create them for CAD solids (see §2.3).

---

## 9. Output requests and parameters

*Analysis > Edit > Output Controls*:
- Displacement, Stress, Strain — on.
- **SPC Forces** (reactions) — on. Needed for equilibrium check.
- **Applied Load / OLOAD** resultant — on (printed in `.out`).
- **Grid Point Force (GPFORCE)** — on for free-body / load-path checks (e.g. force through a saddle).
- Stress at **corner nodes** (not just centroid) — needed for SCL extraction.

*Parameters* (second-last branch of the model tree; Autodesk Nastran solver parameters):

| Parameter | Use |
|---|---|
| `AUTOSPC` | Auto-constrains DOF with no stiffness (e.g. rotations at solid nodes). Leave ON. Doesn't fix real rigid-body motion |
| `SPCGEN` | Prints the auto-applied constraints → see what AUTOSPC did |
| `PRGPST` | Grid Point Singularity Table printout (on by default) |
| `DIRSTRESSTYPE`, `EQVSTRESSTYPE` | Shell output: 0 total, 1 bending only, 2 membrane only |
| `SOLUTIONERROR`, `FACTDIAG` | Debug only: lets a singular model run to show *where* it's singular. Autodesk: set OFF for production ([solver reference](https://help.autodesk.com/cloudhelp/2025/DEU/NSTRN-Reference/files/GUID-5943826F-72A0-49C1-8344-BFFA1535304D.htm)) |
| `CONTACTSTAB` | Stabilises separation contact in nonlinear runs |
| `RAM` | Memory; `AUTO` recommended when S1110 occurs |
| `FILESPEC` / scratch folder | Move scratch to a drive with free space (disk errors) |

Files: the solver writes `model.nas` (input deck), `.log`, `.out` (full output; tables, warnings, SPC sums), `.fno` (binary results) into the model's `InCAD\FEA\` folder next to your `.ipt/.iam` ([forum, Autodesk staff](https://forums.autodesk.com/t5/inventor-nastran-forum/troubleshooting-grid-point-singularity-e5010/td-p/8649855)). **Read the `.log` and `.out` after every run** — not just the coloured plot.

---

## 10. Run, then look at results in this order

1. **Log / Nastran Output tab**: any FATAL? any WARNING G3005/G3009/G3016/G3017/G3051/T2217? (meanings: [08](08-inventor-nastran-errors-and-fixes.md)).
2. **Load/reaction balance** in `.out` (OLOAD resultant vs SPC force resultant).
3. **Deformed shape** (exaggerated): cylinder grows, heads bulge, nozzles grow and pull. Animate.
4. **Displacement magnitude** vs hand calc: radial growth of plain shell $\delta = \dfrac{PR_m^2}{Et}\left(1-\dfrac{\nu}{2}\right)$ → sample: $1.5\times507.35^2/(200000\times8.7)\times0.85$ = **0.189 mm**.
5. **Hoop stress** (cylindrical coordinate system!) in plain shell vs 86.7–87.5 MPa.
6. Only then: von Mises / stress-intensity contours → locate SCLs → linearize ([05](05-stress-linearization-and-classification.md)).

Inventor Nastran tips:
- Create a **cylindrical coordinate system** on the vessel axis (*Setup > Coordinate Systems*) and display stress components in it — hoop = θ component.
- *Results > Probe* / *Nodes > Query* for values at nodes.
- *Results > Stress Linearization* for SCLs (see [05](05-stress-linearization-and-classification.md)).
- Use *Section View* to see through-thickness contours on solids.
- Turn off "average nodal stresses across parts" style smoothing if comparing across material boundaries (check result options).

---

## 11. Model-setup checklist (print this)

- [ ] Drawing rev / model state recorded
- [ ] Units mm–N–MPa–tonne confirmed in material & load dialogs
- [ ] Corroded thickness for design case; new for test case
- [ ] Idealization choice justified (solid/shell/hybrid)
- [ ] Every part has a real material (no Generic), G blank
- [ ] Every part connected (contact or shared mesh) or constrained
- [ ] Symmetry constraints correct for element type (shell: + rotations)
- [ ] Supports realistic; one saddle sliding; no fixed nozzle flanges
- [ ] Pressure on ALL wetted faces incl. nozzle bores; arrows checked
- [ ] End-cap thrust applied at every cut
- [ ] Hydrostatic head / gravity with correct density units
- [ ] Nozzle loads in nozzle local coordinate system, applied ≥ $2.5\sqrt{rt}$ from junction
- [ ] Parabolic solids, ≥ 3 elements through thickness at SCLs
- [ ] Mesh quality check run; no distorted elements in evaluation zones
- [ ] SPC forces, OLOAD, GPFORCE output on; corner stresses on
- [ ] Normal-modes sanity run (no ≈ 0 Hz modes) for new models/assemblies

---

## 12. Units table (mm–N–MPa–tonne–s)

| Quantity | Unit | Example |
|---|---|---|
| Length | mm | 1000 |
| Force | N | 50 000 |
| Stress / pressure | MPa = N/mm² | 1.5 |
| Mass | tonne (10³ kg) | 1.2 t |
| Density | tonne/mm³ | steel 7.85e-9 |
| Gravity | mm/s² | 9810 |
| Weight density (hydrostatic) | N/mm³ | water 9.81e-6 |
| E | MPa | 200 000 |
| Moment | N·mm | 1 kN·m = 1e6 N·mm |
| Thermal expansion | 1/°C | 1.2e-5 |
| Temperature | °C | 100 |

Mixing a kN·m moment into an N·mm model is a 10⁶ error. Always convert piping loads before entering them.

Next: [04 — Meshing and convergence](04-meshing-and-convergence.md).
