#!/usr/bin/env python3
"""
pv_handcalc.py - hand-calculation checks for a simple cylindrical pressure vessel.

Purpose: give independent numbers to compare against Inventor Nastran results
(verification), NOT to replace a code calculation package.

Formulas (ASME BPVC Section VIII Division 1, internal pressure, inside-radius form):
  Cylinder, circumferential stress (UG-27(c)(1)):   t = P R / (S E - 0.6 P)
  Cylinder, longitudinal stress  (UG-27(c)(2)):     t = P R / (2 S E + 0.4 P)
  Hemispherical head (UG-32, inside radius L):      t = P L / (2 S E - 0.2 P)
  2:1 ellipsoidal head (UG-32(d)):                  t = P D / (2 S E - 0.2 P)
  General ellipsoidal (App. 1-4(c)):                t = P D K / (2 S E - 0.2 P),  K = (2 + (D/2h)^2)/6
  Torispherical head (App. 1-4(d)):                 t = P L M / (2 S E - 0.2 P),  M = (3 + sqrt(L/r))/4
  Thin-wall limits for UG-27: t <= R/2 and P <= 0.385 S E (otherwise use App. 1-2 / Lame)
Hydrotest pressures (check your code edition):
  ASME VIII-1 UG-99(b):  1.3 * MAWP * (S_test / S_design)
  ASME VIII-2 8.2.1:     max(1.43 * MAWP, 1.25 * MAWP * (S_test / S_design))
  JIS B 8267:2015 8.5 b): 1.3 * P * (sigma_t / sigma_a)   (pneumatic factor 1.1)
  JIS B 8265:2017 8.5 b): 1.5 * P * (sigma_t / sigma_a)   (pneumatic factor 1.25)
  PED 2014/68/EU Annex I 7.4 / EN 13445-5: max(1.25 * PS * f_test/f_design, 1.43 * PS)
Thick wall (Lame), discontinuity at hemi-head/cylinder junction (beam on elastic
foundation, equal thickness, same material) and UG-37 area replacement (simplified:
F = 1, fr = 1, no reinforcing pad) are also reported.

Usage:
  python3 pv_handcalc.py examples/sample_vessel.json
  python3 pv_handcalc.py examples/sample_vessel.json --markdown > out.md
All units: N, mm, MPa.
"""
import argparse
import json
import math
import sys


def shell_thickness(P, R, S, E):
    t_circ = P * R / (S * E - 0.6 * P)
    t_long = P * R / (2 * S * E + 0.4 * P)
    return t_circ, t_long


def shell_mawp(t, R, S, E):
    """Inverse of UG-27: MAWP from available (corroded) thickness."""
    p_circ = S * E * t / (R + 0.6 * t)
    p_long = 2 * S * E * t / (R - 0.4 * t)
    return min(p_circ, p_long), p_circ, p_long


def head_thickness(kind, P, D, S, E, L=None, r=None, h=None):
    if kind == "hemispherical":
        Lh = D / 2.0
        return P * Lh / (2 * S * E - 0.2 * P)
    if kind == "ellipsoidal_2to1":
        return P * D / (2 * S * E - 0.2 * P)
    if kind == "ellipsoidal":
        K = (2 + (D / (2 * h)) ** 2) / 6.0
        return P * D * K / (2 * S * E - 0.2 * P)
    if kind == "torispherical":
        M = (3 + math.sqrt(L / r)) / 4.0
        return P * L * M / (2 * S * E - 0.2 * P)
    raise ValueError(kind)


def lame(P, ri, ro):
    """Lame thick-cylinder stresses, closed ends, internal pressure only."""
    k2 = (ro / ri) ** 2
    s_hoop_in = P * (k2 + 1) / (k2 - 1)
    s_hoop_out = P * 2 / (k2 - 1)
    s_rad_in = -P
    s_axial = P / (k2 - 1)
    # Tresca stress intensity at bore = hoop - radial
    si_in = s_hoop_in - s_rad_in
    vm_in = math.sqrt(0.5 * ((s_hoop_in - s_rad_in) ** 2 + (s_rad_in - s_axial) ** 2 + (s_axial - s_hoop_in) ** 2))
    return dict(hoop_in=s_hoop_in, hoop_out=s_hoop_out, radial_in=s_rad_in,
                axial=s_axial, tresca_in=si_in, vonmises_in=vm_in,
                hoop_mean=P * ri / (ro - ri))


def membrane_check(P, Rm, t):
    """Thin-shell membrane stresses at mean radius (what FEA should show far from discontinuities)."""
    return dict(hoop=P * Rm / t, long=P * Rm / (2 * t), sphere=P * Rm / (2 * t))


def hemi_cyl_discontinuity(P, Rm, t, E_mod, nu):
    """Equal-thickness hemispherical head welded to cylinder.
    Free radial growth mismatch is carried by a shear Q0 = P/(8 beta); M0 ~ 0.
    Returns max cylinder bending stress and the location (distance from junction)."""
    beta = (3 * (1 - nu ** 2) / (Rm ** 2 * t ** 2)) ** 0.25
    Q0 = P / (8 * beta)                      # N/mm per mm of circumference
    x_max = math.pi / (4 * beta)             # location of max moment
    M_max = Q0 / beta * math.exp(-math.pi / 4) * math.sin(math.pi / 4)
    sb = 6 * M_max / t ** 2
    s_long_m = P * Rm / (2 * t)
    # radial deflection of cylinder end due to Q0 (inward), reduces hoop stress at junction
    D_flex = E_mod * t ** 3 / (12 * (1 - nu ** 2))
    w0 = Q0 / (2 * beta ** 3 * D_flex)
    hoop_free = P * Rm / t
    hoop_junction = hoop_free - E_mod * w0 / Rm
    decay = 1 / beta                         # characteristic length
    sqrt_rt = math.sqrt(Rm * t)
    return dict(beta=beta, Q0=Q0, x_max=x_max, M_max=M_max, sigma_b=sb,
                long_membrane=s_long_m, long_surface_max=s_long_m + sb,
                hoop_free=hoop_free, hoop_at_junction=hoop_junction,
                decay_length=decay, sqrt_Rt=sqrt_rt, w0=w0)


def external_pressure_elastic(E_mod, nu, t, Do, L):
    """Windenburg-Trilling (simplified von Mises) elastic collapse pressure of a cylinder
    with simply supported ends - the basis of the ASME UG-28 'factor A/B' charts in the
    elastic range. ESTIMATE ONLY: use UG-28 / VIII-2 4.4 charts for the code check."""
    pc = (2.42 * E_mod * (t / Do) ** 2.5 /
          ((1 - nu ** 2) ** 0.75 * (L / Do - 0.45 * (t / Do) ** 0.5)))
    return dict(Pc_elastic=pc, Pc_div3=pc / 3.0, Do_over_t=Do / t, L_over_Do=L / Do)


def nozzle_area(P, R_shell, S, E1, t_shell_avail, d_open, t_nozzle_avail, Rn, Sn, h_out, ca,
                pad_od=0.0, pad_t=0.0):
    """Simplified UG-37 area replacement (F=1, fr1=fr2=fr4=1, nozzle not inward, weld areas
    ignored - conservative). Optional reinforcing pad: A5 = (Dp - d - 2 tn) te, Dp <= 2d.
    Thickness values are corroded. Returns required and available areas (mm^2)."""
    tr = P * R_shell / (S * 1.0 - 0.6 * P)            # required shell thickness with E=1 (UG-37 definition)
    trn = P * Rn / (Sn * 1.0 - 0.6 * P)                # required nozzle wall thickness
    A = d_open * tr                                     # required area (F = 1)
    A1 = max(d_open * (E1 * t_shell_avail - tr),
             2 * (t_shell_avail + t_nozzle_avail) * (E1 * t_shell_avail - tr))
    A2 = min(5 * (t_nozzle_avail - trn) * t_shell_avail,
             5 * (t_nozzle_avail - trn) * t_nozzle_avail)
    A5 = 0.0
    if pad_t > 0:
        Dp = min(pad_od, 2 * d_open)
        A5 = max(0.0, (Dp - d_open - 2 * t_nozzle_avail) * pad_t)
    return dict(tr=tr, trn=trn, A_required=A, A1_shell=A1, A2_nozzle=A2, A5_pad=A5,
                A_available=A1 + A2 + A5, ok=(A1 + A2 + A5) >= A)


def hydro(code, P, S_test, S_design):
    ratio = S_test / S_design
    if code == "ASME VIII-1 UG-99(b)":
        return 1.3 * P * ratio
    if code == "ASME VIII-2 8.2.1":
        return max(1.43 * P, 1.25 * P * ratio)
    if code == "JIS B 8267 8.5":
        return 1.3 * P * ratio
    if code == "JIS B 8265 8.5":
        return 1.5 * P * ratio
    if code == "PED Annex I 7.4 / EN 13445-5":
        return max(1.25 * P * ratio, 1.43 * P)
    raise ValueError(code)


def run(cfg):
    P = cfg["design_pressure_MPa"]
    Di = cfg["inside_diameter_mm"]
    ca = cfg["corrosion_allowance_mm"]
    S = cfg["allowable_stress_MPa"]
    S_test = cfg.get("allowable_stress_test_temp_MPa", S)
    E = cfg["joint_efficiency"]
    t_nom = cfg["shell_nominal_thickness_mm"]
    undertol = cfg.get("mill_undertolerance_mm", 0.0)
    E_mod = cfg.get("youngs_modulus_MPa", 200000.0)
    nu = cfg.get("poisson", 0.3)

    R_corr = Di / 2 + ca                        # corroded inside radius
    t_avail = t_nom - ca - undertol             # corroded, minimum thickness
    out = {}
    tc, tl = shell_thickness(P, R_corr, S, E)
    out["shell"] = dict(R_corroded=R_corr, t_req_circ=tc, t_req_long=tl,
                        t_req_plus_ca=max(tc, tl) + ca, t_available=t_avail,
                        thin_wall_ok=(tc <= R_corr / 2 and P <= 0.385 * S * E))
    mawp, pc, pl = shell_mawp(t_avail, R_corr, S, E)
    out["shell"].update(MAWP=mawp, MAWP_circ=pc, MAWP_long=pl)

    heads = {}
    D_corr = Di + 2 * ca
    for kind in ["hemispherical", "ellipsoidal_2to1"]:
        heads[kind] = head_thickness(kind, P, D_corr, S, E)
    tor = cfg.get("torispherical", {"crown_radius_mm": Di, "knuckle_radius_mm": 0.06 * Di})
    L = tor["crown_radius_mm"] + ca
    r = tor["knuckle_radius_mm"] + ca
    heads["torispherical"] = head_thickness("torispherical", P, D_corr, S, E, L=L, r=r)
    heads["torispherical_M"] = (3 + math.sqrt(L / r)) / 4
    out["heads_t_required"] = heads

    Rm = R_corr + t_avail / 2
    out["membrane_check_corroded"] = membrane_check(P, Rm, t_avail)
    out["lame_corroded"] = lame(P, R_corr, R_corr + t_avail)
    out["hemi_cyl_junction"] = hemi_cyl_discontinuity(P, Rm, t_avail, E_mod, nu)
    out["thick_wall_app_1_2"] = dict(
        t_req=R_corr * (math.sqrt((S * E + P) / (S * E - P)) - 1),
        note="ASME VIII-1 App. 1-2(a)(1): t = R(Z^0.5 - 1), Z = (SE+P)/(SE-P)")
    if cfg.get("unsupported_length_mm"):
        Do = Di + 2 * t_nom
        out["external_pressure_estimate"] = external_pressure_elastic(
            E_mod, nu, t_avail, Do, cfg["unsupported_length_mm"])

    nz = cfg.get("nozzle")
    if nz:
        d_open = nz["inside_diameter_mm"] + 2 * ca
        Rn = d_open / 2
        tn_avail = nz["nominal_thickness_mm"] - ca - nz.get("undertolerance_mm", 0.0)
        out["nozzle_area_replacement"] = nozzle_area(
            P, R_corr, S, 1.0, t_avail, d_open, tn_avail, Rn,
            nz.get("allowable_stress_MPa", S), nz.get("projection_mm", 150), ca,
            nz.get("pad_od_mm", 0.0), nz.get("pad_thickness_mm", 0.0))

    out["hydrotest_MPa"] = {c: hydro(c, P, S_test, S) for c in
                            ["ASME VIII-1 UG-99(b)", "ASME VIII-2 8.2.1",
                             "JIS B 8267 8.5", "JIS B 8265 8.5", "PED Annex I 7.4 / EN 13445-5"]}
    # pressure-area thrust on a cut nozzle (end-cap load for FEA)
    if nz:
        out["nozzle_end_cap_thrust"] = dict(
            force_N=P * math.pi * (d_open / 2) ** 2,
            equivalent_axial_pressure_on_cut_face_MPa=P * (d_open / 2) ** 2 /
            ((d_open / 2 + tn_avail) ** 2 - (d_open / 2) ** 2))
    out["vessel_end_cap_thrust_N"] = P * math.pi * R_corr ** 2
    return out


def fmt(v):
    if isinstance(v, bool):
        return "yes" if v else "NO"
    if isinstance(v, float):
        return f"{v:.4g}" if abs(v) < 1e5 else f"{v:.4e}"
    return str(v)


def print_markdown(cfg, out, stream=sys.stdout):
    w = stream.write
    w(f"# Hand-calculation results: {cfg.get('name', 'vessel')}\n\n")
    w("Units: mm, MPa, N. Corroded dimensions used unless noted.\n\n")
    for section, data in out.items():
        w(f"## {section}\n\n")
        if isinstance(data, dict):
            w("| Item | Value |\n|---|---|\n")
            for k, v in data.items():
                w(f"| {k} | {fmt(v)} |\n")
        else:
            w(f"{fmt(data)}\n")
        w("\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config", help="JSON input file (see examples/sample_vessel.json)")
    ap.add_argument("--markdown", action="store_true", help="print a markdown report")
    a = ap.parse_args()
    with open(a.config) as f:
        cfg = json.load(f)
    out = run(cfg)
    if a.markdown:
        print_markdown(cfg, out)
    else:
        print(json.dumps(out, indent=2, default=fmt))


if __name__ == "__main__":
    main()
