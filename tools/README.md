# tools/ — small, tested Python scripts (standard library only, Python ≥ 3.8)

| Script | Purpose | Run |
|---|---|---|
| `pv_handcalc.py` | Hand calcs for FEA verification: UG-27 shell, UG-32 / App. 1-4 heads, App. 1-2 thick wall, Lamé, hemi–cylinder discontinuity, UG-37 area replacement (simplified, optional pad), hydrotest (ASME VIII-1/VIII-2, JIS B 8265/8267, PED), external-pressure estimate, end-cap thrust | `python3 tools/pv_handcalc.py tools/examples/sample_vessel.json --markdown` |
| `linearize.py` | Stress linearization along an SCL from a CSV (local N/T/H or global XYZ components), membrane / bending / peak, von Mises & Tresca, ASME VIII-2 5.2.2.4 limit check | `python3 tools/linearize.py tools/examples/lame_scl_local.csv --S 138 --category PL` |
| `convergence.py` | Mesh convergence: observed order, Richardson extrapolation, GCI, singularity flag | `python3 tools/convergence.py tools/examples/convergence_example.csv` |
| `test_tools.py` | Self-tests against exact solutions | `python3 tools/test_tools.py` |

## Examples (`tools/examples/`)

| File | What |
|---|---|
| `sample_vessel.json` | 1000 mm ID, 1.5 MPa, SA-516-70 (S = 138 MPa typical), CA 3 mm, 12 mm shell, DN200 nozzle without pad |
| `sample_vessel_with_pad.json` | Same, with 340 OD × 10 mm reinforcing pad |
| `make_lame_examples.py` | Writes the two Lamé SCL CSVs and prints the exact answers |
| `lame_scl_local.csv` | Thick cylinder SCL in local frame (s, Snn, Stt, Shh, Snt, Sth, Shn) |
| `lame_scl_global_rot30.csv` | Same SCL in global XYZ, rotated 30° (tests the rotation) |
| `convergence_example.csv` | 4-mesh study that converges (p ≈ 1.8) |
| `convergence_singularity.csv` | 4-mesh study at a sharp corner (p ≈ 0.35 → flagged) |
| `*_output.txt` | Saved outputs of the commands above |

## Using your own Inventor Nastran data with `linearize.py`

1. Inventor Nastran *Results > Stress Linearization* → green button → CSV. Rename/map its local tensor columns to `s,Snn,Stt,Shh,Snt,Sth,Shn` (n = along the SCL, t = hoop, h = meridional) and use `--frame local`.
2. Or split a face so an edge lies on the SCL, query nodal stresses (global components) and save `x,y,z,Sxx,Syy,Szz,Sxy,Syz,Szx`, ordered inside → outside; use `--frame global --tdir hx hy hz` with the hoop direction (for axis along z at point (x, y): `--tdir -y x 0`).
3. Use **corroded** geometry and at least 3 parabolic elements through the wall.

## Limits
- These scripts are **checks**, not code-calculation software. They implement simplified forms (stated in each docstring). Use certified software or full code calculations for design.
- `linearize.py` uses straight SCLs and the Annex 5-A integral method without thick-axisymmetric curvature corrections.
