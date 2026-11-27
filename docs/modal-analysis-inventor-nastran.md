# Modal Analysis in Inventor Nastran: Setup, Mesh, Results

How to set up a modal (natural frequency) analysis in Inventor Nastran 2025/2026, following the applied-edition training book's Chapter 1 (eigenvalue analysis of single parts).

> **Note:** The values below are typical starting points. Change them to suit your own part or assembly.

Related: translated Applied Edition book Chapter 1 (eigenvalue analysis).

## 1. Create the analysis

- In the Nastran tab, open **Analysis** and pick **New**.
- **Type:** Modal (Normal Modes).
- **Solver:** Nastran (SOL 103).
- **Contact:** Bonded, for an assembly.

## 2. Analysis settings (Options or Output Set)

| Parameter | Typical starting value | Notes |
|---|---|---|
| Number of modes | 10 | 6–20 is common |
| Frequency range, lower | 0 Hz | |
| Frequency range, upper | blank, or e.g. 2000 Hz | |
| Method | Lanczos | default |
| Mass | Coupled | default; Lumped is faster |

For a free-free check, leave out constraints and set modes to 12. The first 6 will be about 0 Hz (rigid-body modes).

## 3. Material

**Density is required.** Without it, the modal analysis fails or gives wrong frequencies.

| Material | Young's modulus *E* | Poisson's ratio *ν* | Density *ρ* |
|---|---|---|---|
| Steel | 210,000 MPa | 0.3 | 7.85×10⁻⁹ t/mm³ (7850 kg/m³) |
| Aluminium | 70,000 MPa | 0.33 | 2.7×10⁻⁹ t/mm³ |

Keep units consistent with the model (typically mm–N–MPa–tonne).

## 4. Constraints and loads

- **Constraint:** Fixed (all 6 DOF) on the mounting faces or bolt holes.
- **Loads:** none, because modal analysis does not use them.
- **Prestress (optional):** to include load stiffening, add a load and turn on **Include Preload**.

## 5. Mesh settings

| Setting | Typical starting value |
|---|---|
| Element order | Parabolic (2nd order, 10-node tet). Always use this for modal. |
| Element size | About 1/10 to 1/20 of the part's smallest main dimension. For a 100 mm part, use about 5 mm. |
| Min/Max ratio | 0.2 |
| Grading | 1.5 |
| Max turn angle | 60° |
| Thin walls | At least 2 elements through the thickness, or a shell mesh |
| Local refinement | On fillets, holes and thin ribs (**Mesh Control:** Face, half the global size) |

## 6. Mesh check

- **Mesh Table:** right-click Mesh and open **Mesh Table** to see the node and element counts.
- **Quality:** open Mesh, then Mesh Quality / Check:
  - Aspect ratio under 10 is good; over 30 needs fixing.
  - Jacobian over 0.6.
  - Skew under 60°.
- **Convergence:**
  - Run at size *h*, then at *h*/2.
  - If the 1st frequency changes by less than 2–5%, the mesh is good enough.

## 7. Run

- Right-click the analysis, then **Run**, then check the **.f06** file for errors.
- Common errors:
  - "Fatal: mass" means density is missing.
  - Many modes near 0 Hz mean an unconstrained or disconnected part (check contacts).

## 8. Result output (Results tree)

- **Modes:** open each **Mode 1…N** to see the frequency in Hz in the title.
- **Displacement:** plot Total Displacement, which shows the mode shape. The values are normalized, so read the shape, not the size.
- **Animate:** play each mode shape (**Animate**, 20 frames).
- **Frequency list:** Results, then **Modal Frequency Table**, or read it in the **.f06** under `REAL EIGENVALUES`. Export to CSV or Excel.
- **Effective mass:** turn on **Modal Effective Mass** in Output Set Options. Aim for at least 80–90% total mass in X, Y and Z to capture enough modes.
- **Report:** Report Wizard, include Modes 1–6 with images.

## 9. What to check

- Is the 1st frequency above the excitation frequency, for example motor RPM ÷ 60? Aim for at least 1.5× (sometimes 2×) margin.
- Do the mode shapes make physical sense (bending, torsion)?
- Compare with a simple hand formula. A cantilever's first natural frequency is

$$ f_1 = \frac{1.875^2}{2\pi} \sqrt{\frac{EI}{\rho A L^4}} $$
