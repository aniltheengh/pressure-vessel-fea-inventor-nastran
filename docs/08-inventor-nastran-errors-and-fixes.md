# 08 — Inventor Nastran Errors and Fixes (and Why ANSYS Users Hit Them)

> Inventor Nastran is a real Nastran solver (Autodesk Nastran, formerly NEi Nastran) inside a CAD add-in. It is **less forgiving** than ANSYS Workbench about connectivity and stability, and its messages use **Autodesk Nastran codes (E5000, G3009, S1110 …)**, not MSC/NX codes (e.g. MSC "USER FATAL MESSAGE 9050" / NX "9137" are the equivalent family in other Nastrans). Almost every fatal error in a static pressure-vessel run is one of: **unconnected part, unconstrained rigid-body motion, bad material input, distorted mesh, or contact problem.**

Every fix below is taken from **Autodesk Knowledge Base articles** or **Autodesk Community forum** answers, linked in each entry. Read the first fatal message in the log — later messages are often consequences.

---

## 0. Where to read errors

| File / place | What's in it |
|---|---|
| *Nastran Output* tab in Inventor (during/after run) | Live log |
| `<model folder>\<model name>\InCAD\FEA\*.log` | Summary log, warnings, fatal errors |
| `...\InCAD\FEA\*.out` | Full output: model summary, **Grid Point Singularity Table**, OLOAD resultant, SPC force summation, contact penetration, parameter values used |
| `...\InCAD\FEA\*.nas` | The Nastran input deck that Inventor wrote (materials, properties, loads — check units here!) |

Location confirmed by an expert on the Autodesk forum ([E5010 thread](https://forums.autodesk.com/t5/inventor-nastran-forum/troubleshooting-grid-point-singularity-e5010/td-p/8649855)).

**Procedure for any error:**
1. Find the **first** FATAL ERROR and all WARNINGs before it.
2. Note GRID (node) and COMPONENT numbers (1 = Tx, 2 = Ty, 3 = Tz, 4 = Rx, 5 = Ry, 6 = Rz).
3. Locate the node in the model (*Nodes > Query* / find node).
4. Apply the fix from the table below.
5. Record it in your troubleshooting log (§5).

---

## 1. Quick lookup table

| Message | Meaning | Most likely cause in a vessel model | First fix |
|---|---|---|---|
| **FATAL ERROR E5000: SINGULARITY DETECTED AT GRID id COMPONENT n** | Stiffness matrix can't be solved at that DOF | A part not connected/constrained; material missing/very low; distorted elements | Run **Normal Modes** to find the free part; check contacts and materials |
| **FATAL ERROR E5001: NON-POSITIVE DEFINITE DETECTED AT GRID id COMPONENT n** | Same family | Same | Same |
| **FATAL ERROR E5004: STIFFNESS MATRIX SINGULAR OR NON-POSITIVE DEFINITE** | Same family, location not given | Same | Same |
| **FATAL ERROR E5008: NON ZERO STIFFNESS MATRIX REQUIRED** | No stiffness at all | Material values missing/misread (regional number format), all parts unconnected | Check material in `.nas`; Windows number format; contacts |
| **WARNING E5010** (grid point singularity) | DOFs with no stiffness auto-constrained (AUTOSPC) | Rotational DOF 4–6 at solid nodes — **normal** | Only investigate if translational DOF 1–3 listed |
| **WARNING G3005: GRIDS – AND – ARE COLLOCATED ON – ELEMENT –** | Two nodes at same location in one element | Thin/sliver geometry; midside projection | Finer mesh, linear mesh, or fix CAD |
| **WARNING G3009: – ELEMENT – HAS SINGULAR GEOMETRY** | Distorted element | Sliver faces; Project Midside Nodes on thin curved part; contact interference moving nodes | Turn off Project Midside Nodes, refine, fix CAD |
| **WARNING G3016 / G3017: EDGE POINT RATIO GREATER / LESS THAN –** | Midside node badly placed | Curved thin geometry | Same as G3009 |
| **WARNING G3051: MODIFYING SECONDARY GRID – POSITION ON CONTACT ELEMENT –** | Contact removing initial interference by moving nodes | CAD interference; coarse mesh on curved contact | Remove interference; contact pairs only on touching faces |
| **WARNING T2217** | Element orientation problem | Collapsed / inverted elements | Remesh; fix geometry |
| **WARNING E5074** then **FATAL ERROR E5076: MAXIMUM NUMBER OF BISECTIONS PERMITTED REACHED** | Nonlinear run didn't converge | Unstable part, separation contact gap, buckling/snap, collapse | See §2.6 |
| **FATAL ERROR S1110: INSUFFICIENT MEMORY AVAILABLE TO CONTINUE** | Out of RAM / virtual memory | Too many elements/contact elements | Symmetry, fewer contacts, RAM=AUTO, more virtual memory |
| **"Meshing Failed"** (dialog) | Mesher couldn't create surface or volume mesh | Mismatched edges, overlapping bodies, too coarse settings | Mesh Troubleshooter, tolerance, Repair Bodies, split faces |
| Licence / "Failed to launch Nastran" | Solver didn't start | Add-in not loaded, licence service, Single Sign-On | Launch per Autodesk article; update licensing service |

---

## 2. Details, with sources

### 2.1 E5000, E5001, E5004 — singular / non-positive-definite stiffness

**Sources:** [Autodesk KB — E5004/E5001/E5000](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Error-FATAL-ERROR-E5004-STIFFNESS-MATRIX-SINGULAR-OR-NON-POSITIVE-DEFINITE-when-running-an-analysis-in-Nastran-In-CAD.html); [How to resolve FATAL ERROR E5000](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/FATAL-ERROR-E5000-in-Nastran-Analysis.html); [E5000 Singularity detected](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/FATAL-ERROR-E5000-SINGULARITY-DETECTED-in-Nastran-In-CAD.html); [forum: E5004 solved](https://forums.autodesk.com/t5/inventor-nastran-forum/fatal-error-e5004/td-p/9442747).

**Meaning:** the solver cannot invert the stiffness matrix. The solver can't tell *why*; Autodesk lists these causes:
- A component not properly constrained (statically unstable).
- Highly distorted elements (G3005, G3009 warnings; T2217).
- Incorrect material properties (Generic material; very low E; Poisson = 0.5; inconsistent G).
- Connectors causing instability (e.g. a single ROD connector carries only axial force and torsion → mechanism).
- Duplicated contacts.
- Rarely: the PSS DECOMPMETHOD solver; thermal analysis with only convection loads.

**Fix sequence (Autodesk's):**
1. If the message gives GRID and COMPONENT, locate that node; the component is the unstable direction.
2. **Every part must be restrained in Tx, Ty, Tz, Rx, Ry, Rz** — by constraints or by being connected to constrained parts. **Parts are not bonded by default** — define contact (manual, automatic, or *Solver contact*, typically Bonded).
3. Check **maximum activation distance** of contacts: manual contact ≈ 1.1–1.2 × node spacing (element size + gap); solver contact slightly larger than the gap and smaller than the thinnest solid.
4. Multibody parts: contacts between bodies are needed too.
5. Separation contact restrains in one direction only and iterates → a part can go unstable in some iteration → add **springs with low stiffness** to ground, or use bonded where physically acceptable.
6. Connectors must attach to the **CAD geometry of the part** (not a work point floating nearby).
7. Mesh: if *Project Midside Nodes* is on, turn it off and remesh; otherwise use a finer mesh (or linear for speed while debugging).
8. Material: Poisson < 0.5 (0.48 if near-incompressible); **delete G** and let Nastran compute $G = E/2(1+\nu)$; keep max/min E ratio between parts reasonable (≈ 1000 is usually enough for "rigid").
9. Check interference (G3051), and disabled derived parts that still get meshed.
10. **Run Normal Modes** (*Analysis > Edit > Type = Normal Modes*): modes near 0 Hz (e.g. 1e-4 Hz) show the free part and direction. If Normal Modes **also** fails with E5000-series, the problem is distorted elements, not constraints. Note: Normal Modes converts separation contact to bonded, so a part unstable in static (with separation) may look fine in modal.

**Pressure-vessel specific causes I see most:**
- Reinforcing pad, saddle, wear plate or lifting lug **not in contact** (no contact defined or activation distance too small for the modelled gap).
- Vessel loaded only by pressure with **no constraints at all** ("pressure is self-balanced, so I didn't constrain it") — static still needs the 3-2-1 minimum ([03 §5.2](03-inventor-nastran-model-setup.md)).
- Shell model with symmetry constraints missing rotations.
- Nozzle modelled as separate part with a tiny gap to the shell hole.
- Internal parts (baffles) floating.

**Debug-only switch:** parameter `SOLUTIONERROR = ON` with `FACTDIAG` lets the run continue past a singularity so you can see what moves; Autodesk says to keep it **OFF for production runs** ([Autodesk Nastran reference](https://help.autodesk.com/cloudhelp/2025/DEU/NSTRN-Reference/files/GUID-5943826F-72A0-49C1-8344-BFFA1535304D.htm)). Never report results from a run with these switches on.

### 2.2 E5008 — Non zero stiffness matrix required
**Source:** [Autodesk forum thread](https://forums.autodesk.com/t5/inventor-nastran-forum/fatal-error-e5008-non-zero-stiffness-matrix-required/td-p/6262611).
- Causes given in the thread: material properties missing or **misread** (check in the `.out` that E and ν are what you entered), distorted mesh (G3005/G3009), parts not connected.
- One user's case: it happened only in SI units and was suspected to be the **Windows regional number format** (thousands/decimal separator). If you use a Japanese/European Windows locale with non-standard separators, check that `1.5` and `200000` appear correctly in the `.nas` file.

### 2.3 E5010 — grid point singularity (warning)
**Source:** [Autodesk forum thread](https://forums.autodesk.com/t5/inventor-nastran-forum/troubleshooting-grid-point-singularity-e5010/td-p/8649855).
- Solid (tet) nodes have no rotational stiffness → DOF 4, 5, 6 always appear in the Grid Point Singularity Table and are auto-constrained by **AUTOSPC**. **Normal, harmless.**
- Turn on `SPCGEN` to print what was auto-constrained.
- Investigate only if **translational** DOF (1, 2, 3) appear, or for shells (rotation about the normal is the drilling DOF).

### 2.4 G3005 / G3009 / G3016 / G3017 / T2217 — bad elements
**Sources:** [E5004 KB](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Error-FATAL-ERROR-E5004-STIFFNESS-MATRIX-SINGULAR-OR-NON-POSITIVE-DEFINITE-when-running-an-analysis-in-Nastran-In-CAD.html), [E5000 KB](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/FATAL-ERROR-E5000-in-Nastran-Analysis.html).
- Remesh finer at the reported elements; disable **Project Midside Nodes** if on; use linear mesh for G3005 as a test; fix CAD slivers (tiny faces from fillets meeting chamfers, weld bead remnants).
- In vessels: thin sliver faces where a nozzle bore meets a head with a tiny fillet, saddle horn edges, pad edges at nozzle.
- In Inventor: use *Simplify* (not *Create Simplified Part*, which can make meshing fail — [KB](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Meshing-fails-in-Nastran-after-using-Create-Simplified-Part-function-in-Inventor.html)).

### 2.5 G3051 — contact modifying secondary grid position
**Source:** [E5004 KB](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Error-FATAL-ERROR-E5004-STIFFNESS-MATRIX-SINGULAR-OR-NON-POSITIVE-DEFINITE-when-running-an-analysis-in-Nastran-In-CAD.html).
- Search `.out` for "INITIAL MAXIMUM CONTACT SURFACE PENETRATION" — if larger than expected, the contact is moving nodes and distorting elements.
- Each contact pair should include only faces that are actually in contact. Split a multi-face contact into separate pairs.
- In vessels: pad–shell faying surface (CAD pad radius not exactly shell OD + 0), saddle–shell.

### 2.6 E5074 / E5076 — nonlinear non-convergence
**Source:** [Autodesk KB — E5074 followed by E5076](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Fatal-error-E5076-in-an-Autodesk-Nastran-In-CAD-analysis.html).
- First check the model is **statically stable** (same as E5000).
- Separation contact with an initial gap + force load → infinite rigid displacement at step 0 → set parameter **`CONTACTSTAB = ON`**, add weak springs, or remove the gap.
- Buckling / snap-through → confirm with nonlinear buckling; a static solver can't follow snap-through.
- Enforced motion with an initial gap → remove gap or disable the *Load* convergence criterion.
- Force/pressure loads are harder to converge than enforced displacement; replacing with enforced motion (+ constraint on the same face) adds stability; reaction = load.
- In a **limit-load or elastic–plastic** vessel analysis, non-convergence may be **real collapse** — that's the answer you were looking for. Distinguish: plot load–displacement; collapse shows a flattening curve and growing plastic zone through the wall; numerical failure shows sudden stop with small plasticity.
- Note from the E5004 KB: Inventor Nastran nonlinear static uses **large-displacement theory**; contacts are treated differently than in linear static/modal.

### 2.7 S1110 — insufficient memory
**Source:** [Autodesk KB — S1110](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Fatal-error-S110-insufficient-memory-to-continue.html).
- Contact elements can outnumber real elements (count is in the `.log`).
- Use **symmetry**; **combine same-material bonded parts** into one body; set a **maximum activation distance** instead of default; use **unsymmetric** contact where appropriate.
- Add physical RAM; increase Windows **virtual memory** (Control Panel > Advanced System Settings > Performance > Settings > Advanced > Virtual memory); set parameter **`RAM = AUTO`**.

### 2.8 Disk space / scratch files
**Source:** [Autodesk KB — modify default parameters (NASTRAN.INI)](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-modify-the-default-parameters-for-all-new-Nastran-InCAD-analyses.html).
- Temporary files go to the folder in **`FILESPEC`**. Point it to a local drive with free space (e.g. `D:\NastranScratch`). Set per model in *Parameters*, or for all new analyses in `NASTRAN.INI` (2020+: `C:\Program Files\Autodesk\Inventor Nastran YYYY\Nastran\`).
- `NPROCESSORS` in the same file sets CPU count.
- Don't run from network drives / OneDrive-synced folders (sync locks files mid-run).
- Delete old scratch files.

### 2.9 "Meshing Failed"
**Sources:** [KB — Meshing Failed when solid meshing](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Meshing-Failed-when-solid-meshing-with-Nastran-In-CAD.html); [KB — Overlapping geometry](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Overlapping-geometry-causes-meshing-to-fail-in-Nastran-In-CAD.html); [Mesh Troubleshooter help](https://help.autodesk.com/cloudhelp/2025/ENU/NINCAD-UsersGuide/files/GUID-DC088A72-D59A-4CC3-B884-9D379E4E673D.htm).
- **Causes:** mesh too coarse for the part; adjacent faces with mathematically different edges (don't "knit"); overlapping/duplicate geometry (an edge shared by more than two faces — Autodesk's example is literally **a pressure vessel** whose inside faces didn't mesh).
- **Diagnose:** temporarily switch idealization to Shell → unmatched edges show as heavy (white) edges. Or open **Mesh Troubleshooter** (from Mesh panel or the *Troubleshoot* button in the failure dialog).
- **Fix:** adjust **mesh tolerance** (order 0.1–1 mm for a part tens of mm in size, per KB example); *Manage > Update > Rebuild All*; *Surface > Repair Bodies*; **split** cylindrical faces in half; stitch/patch faces; split a multi-piece single part into an assembly or overlap the pieces so they merge; *Exclude from Analysis* duplicates.

### 2.10 Licence / solver doesn't start
**Sources:** [KB — How to launch or activate Inventor Nastran](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-do-I-launch-Autodesk-Nastran-In-Cad-after-the-installation.html); [Installation help — Licensing](https://help.autodesk.com/cloudhelp/2022/ENU/NINCAD-Installation/files/GUID-6027D784-8B24-4469-84CB-17615D17667B.htm); [Testing the Autodesk Nastran installation](https://help.autodesk.com/cloudhelp/2026/ENU/NINCAD-Installation/files/GUID-0FB18AEE-0E38-4751-A59C-0DA0F4A8F33C.htm).
- Start Inventor → load the Inventor Nastran add-in → *Environments > Autodesk Inventor Nastran*. Run from Inventor, not from the stand-alone editor.
- Update Autodesk Desktop Licensing Service / sign in again; for network licences check server and port.
- Run the installation test from the help page above to confirm the solver works independent of your model.

### 2.11 Silent errors (no message, wrong answer) — the dangerous ones

| Silent error | How to detect |
|---|---|
| Wrong units (Pa vs MPa, density) | Hand-calc hoop stress, reaction = weight ([07](07-verification-and-validation.md)) |
| Pressure on wrong side / missing faces | Load resultant in `.out`; deformed shape; reactions ≠ 0 for closed vessel |
| Missing end-cap thrust | Nozzle longitudinal stress ≈ 0 |
| Shell thickness = default | Check property table in `.nas` |
| Uncorroded geometry in design case | Model state name in report |
| Bonded pad (over-stiff) | Sensitivity run with separation |
| Over-constrained saddles | Axial stress near saddles; reaction forces in axial direction |
| Singular peak reported as result | Convergence study |
| Linear tets used | Mesh settings screenshot; element count ÷ node count ratio (linear tets ~ 5–6 elements per node, parabolic ~ 0.7) |

---

## 3. Inventor Nastran vs ANSYS Workbench — differences that trip ANSYS users

| Topic | ANSYS Workbench (Mechanical) | Inventor Nastran | What to do |
|---|---|---|---|
| Contacts between touching bodies | **Auto-created** as Bonded on import | **None by default** ("Parts are not bonded together by default" — Autodesk KB). *Automatic contacts* command exists but you must run it | Always define/check contacts; run *Automatic* then review every pair |
| Mesh connectivity | Shared topology (SpaceClaim/DM) → conformal mesh | *Continuous Meshing* for shells; for solids it only merges coincident nodes within tolerance ([KB](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Does-Nastran-In-CAD-have-continuous-meshing-of-solid-elements.html)) | Merge same-material bodies into one solid in Inventor where possible |
| Solid elements | SOLID187 tets / SOLID186 hex; sweep / multizone hex meshing | Tets only from the Inventor mesher (CTETRA 4/10) | Use parabolic tets and more elements through thickness |
| Unstable model handling | Can add **weak springs** automatically; error "rigid body motion / pivot" | Error E5000/E5004; **AUTOSPC** handles zero-stiffness DOF only, not mechanisms | Constrain properly; springs manually only to stabilise |
| Symmetry | Symmetry region / Frictionless support | Frictionless constraint (solids) or custom DOF; shells need rotations too | §4 of [03](03-inventor-nastran-model-setup.md) |
| Stress linearization | *Linearized Stress* along a *Path*, membrane/bending/peak, multiple outputs | *Results > Stress Linearization* (Pm, Pb, Pm+Pb; Tresca and von Mises; CSV) | Same concept — define SCL by coordinates |
| Shell membrane/bending outputs | Top/Bottom/Middle selectable in result | Parameters DIRSTRESSTYPE / EQVSTRESSTYPE, one run per type | Plan extra runs or compute (top ± bottom)/2 |
| Units | Unit system menu; consistent conversions | Document units + Nastran units; material density units easy to get wrong | Check `.nas` deck |
| Messages | Text descriptions | Codes (E, G, S, T + number) | Search Autodesk KB with the code |
| Nonlinear default | Large deflection off unless set | Nonlinear static uses **large displacement** theory (per KB) | For strict limit-load (small displacement), check nonlinear settings |
| Remote loads | Remote force/displacement with deformable/rigid behaviour | Remote Force; Rigid Body connectors (rigid/interpolation) | Choose RBE3-type for loads that shouldn't stiffen |
| Results averaging | Nodal averaging across bodies options | Averaged nodal contours; results only at corner nodes | Use SCL integrals; don't read mid-side "values" |
| Solver logs | Solution Information | `.log`, `.out` in `InCAD\FEA` folder | Read them every run |

**Why "five errors on a simple static" in Inventor Nastran but none in ANSYS?** Typically: (1) assembly parts not in contact (ANSYS bonded them automatically), (2) a part only touching through separation contact, (3) Generic material on one part, (4) sliver faces producing G3009 → E5000, (5) one of the above making E5004 appear several times per subcase. Fix the first cause and the rest often disappear.

---

## 4. Debug workflow that solves 90 % of static-run failures

1. **Simplify**: suppress everything except the main shell + heads. Run. If it works, add parts back one at a time.
2. **Normal Modes** with your constraints → any ≈ 0 Hz mode? Animate it → that's the free part/direction.
3. **Contacts**: *Automatic* contacts → open each pair → type Bonded (for welded joints) → check activation distance > gap.
4. **Materials**: every part has a real material; G blank; check `.out` echo of MAT1 cards.
5. **Mesh**: *Check Quality*; turn off *Project Midside Nodes* if G3009; refine slivers; fix CAD.
6. **Constraints**: at least 3-2-1; no conflicting constraints (two constraints on one node in different coordinate systems).
7. Run again; read `.log` top to bottom.

---

## 5. Your troubleshooting log (fill this as you go)

Keep this table in your project folder. Every fix you record is experience you won't need to rediscover.

| # | Date | Model / rev | Exact message (copy from .log) | Grid / element | Root cause | Fix applied | Source (KB/forum link) | Time lost |
|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | |
| 2 | | | | | | | | |
| 3 | | | | | | | | |
| 4 | | | | | | | | |
| 5 | | | | | | | | |

Next: [09 — Report template](09-report-template.md).
