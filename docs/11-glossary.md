# 11 — Glossary (English / 日本語 where useful)

| Term | 日本語 | Meaning |
|---|---|---|
| AI (Authorized Inspector) | 検査員 (ASME) | Inspector employed by an Authorized Inspection Agency who accepts ASME code work |
| Allowable stress, S | 許容引張応力 (σa) | Code maximum design stress at temperature (II-D tables) |
| AUTOSPC | — | Nastran parameter that auto-constrains DOF without stiffness |
| Bonded contact | 結合接触 | Contact that ties two surfaces together (no separation or sliding) |
| Buckling | 座屈 | Instability under compressive stress |
| CA (corrosion allowance) | 腐れ代 | Extra thickness for corrosion/erosion over life |
| Calibration | 校正 / キャリブレーション | Adjusting model parameters to match test data |
| Classification (stress) | 応力分類 | Assigning linearized stresses to Pm, PL, Pb, Q, F |
| CTETRA | — | Nastran tetrahedral solid element (4 or 10 nodes) |
| CQUAD4/CQUADR/CQUAD8 | — | Nastran quadrilateral shell elements |
| DBA (design by analysis) | 解析による設計 | Design acceptance from stress analysis (VIII-2 Part 5, EN 13445-3 Annex B/C) |
| DBR / DBF (design by rule/formula) | 公式による設計 | Code formulas (UG-27, UG-32 …) |
| Design pressure | 設計圧力 | Pressure used to design (≥ max operating) |
| Discontinuity (gross / local) | 構造不連続部 | Change of geometry/material that disturbs membrane stress field |
| Elastic–plastic analysis | 弾塑性解析 | Analysis with real stress–strain curve (VIII-2 5.2.4) |
| End-cap thrust | 端面推力 | Axial force from pressure on a closure not modelled ($P\pi r^2$) |
| Equivalent stress (von Mises) | ミーゼス相当応力 | $\sqrt{\tfrac12[(\sigma_1-\sigma_2)^2+(\sigma_2-\sigma_3)^2+(\sigma_3-\sigma_1)^2]}$ |
| F (peak stress) | ピーク応力 | Non-linear part + concentrations; fatigue only |
| Fatigue | 疲労 | Damage from cyclic stress |
| GCI | — | Grid Convergence Index — numerical uncertainty estimate from mesh study |
| GPFORCE | — | Grid point force output (free-body forces at nodes) |
| Hoop stress | 周方向応力 / フープ応力 | Circumferential stress, $PR/t$ in cylinder |
| Hydrotest | 水圧試験 | Pressure test with water at code test pressure |
| Idealization | イデアライゼーション | Inventor Nastran property definition (solid/shell/line + material) |
| Jacobian ratio | ヤコビアン比 | Element distortion measure |
| Knuckle | ナックル部 | Toroidal transition of a torispherical head |
| Lamé solution | ラメの式 | Exact thick-cylinder elasticity solution |
| Limit load | 極限荷重 | Collapse load of elastic–perfectly plastic structure, small displacement |
| Linearization | 応力の線形化 | Splitting through-wall stress into membrane + bending + peak |
| Load case / subcase | 荷重ケース / サブケース | Set of loads analysed together |
| LSR | — | Lowest stress ratio (test / design allowable) for hydrotest pressure |
| MAWP | 最高許容使用圧力 | Max allowable working pressure at top of vessel, corroded, at design temperature |
| MDMT | 最低設計金属温度 | Minimum design metal temperature |
| Membrane stress | 膜応力 | Average stress through thickness |
| Mid-surface | 中立面 / 板厚中央面 | Surface at half thickness used for shell models |
| Mode shape | 固有モード | Deformation pattern of a natural frequency or buckling eigenvalue |
| Normal Modes | 固有値解析 | Natural frequency analysis |
| Nozzle | 管台 / ノズル | Branch connection on shell or head |
| OLOAD | — | Nastran applied-load resultant printout |
| Pb | 一次曲げ応力 | Primary bending stress |
| PL | 局部一次膜応力 | Local primary membrane stress |
| Pm | 一次一般膜応力 | General primary membrane stress |
| Parabolic element | 2次要素 | Element with mid-side nodes |
| PED | 圧力機器指令 | EU Pressure Equipment Directive 2014/68/EU |
| PWHT | 溶接後熱処理 | Post-weld heat treatment |
| Q (secondary stress) | 二次応力 | Self-limiting stress from compatibility / thermal |
| Ratcheting | ラチェット | Progressive incremental plastic deformation under cyclic load |
| RBE2 / RBE3 | 剛体要素 / 補間要素 | Rigid / interpolation multipoint constraint elements |
| Reinforcing pad | 補強板 | Plate around nozzle to replace removed area |
| Richardson extrapolation | リチャードソン補外 | Estimate of mesh-independent value |
| Saddle | サドル | Support for horizontal vessels |
| SCL | 応力分類線 | Stress Classification Line through the wall |
| Shell element | シェル要素 | 2D element with thickness property |
| Singularity | 特異点 | Point where elastic stress is theoretically infinite |
| Skirt | スカート | Cylindrical support for vertical vessels |
| SPC | 単点拘束 | Single-point constraint (Nastran) |
| SPL, SPS | — | VIII-2 allowable for PL(+Pb) and for P+Q range |
| Stress intensity (Tresca) | 応力強さ | $\max|\sigma_i-\sigma_j|$ — used in older VIII-2 and Section III |
| Structural stress | 構造応力 | Membrane + bending at weld toe (mesh-insensitive), VIII-2 5.5.5 |
| Torispherical head | 皿形鏡板 | Head with crown radius + knuckle radius |
| 2:1 Ellipsoidal head | 半だ円形鏡板 (2:1) | Head with semi-ellipse profile, ratio 2:1 |
| Hemispherical head | 全半球形鏡板 | Half sphere |
| UDS | 設計仕様書 | User's Design Specification (VIII-2) |
| Validation | 妥当性確認 | Showing the model represents reality |
| Verification | 検証 | Showing the model is solved correctly |
| WRC 107/537/297 | — | Welding Research Council bulletins for local loads on shells/nozzles |
| Weld toe | 溶接止端 | Junction of weld face and base metal; fatigue hot spot |

Next: [12 — References](12-references.md).
