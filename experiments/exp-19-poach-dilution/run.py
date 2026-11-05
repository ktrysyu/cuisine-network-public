"""Exp-19: 酢とポーチドエッグに対照（同じ量の水・多めの差し水）を足す。

    uv run python experiments/exp-19-poach-dilution/run.py

計画は plan.md（実行前にコミット、e6b6ebc）。結果は results/output.md・output.json。
通説ページ（experiments/myths/poached_vinegar.py）は output.json を読む。
Exp-14 の sim・rules.yaml は変えない（egg_kinetic の節点数だけこの中で一時的に変える）。
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP14 = HERE.parent / "exp-14"
sys.path.insert(0, str(EXP14))

from sim import params  # noqa: E402
from sim import egg_kinetic as EK  # noqa: E402

OUT = HERE / "results"

# ---------------- 物性値（出典は plan.md・SOURCES） ----------------
RHO_100 = 958.35      # kg/m³ 水 100℃（Engineering ToolBox, Water - Density）
RHO_20 = 998.21       # kg/m³ 水 20℃（同）
CP_100 = 4.2157       # kJ/(kg·K) 水 100℃（Engineering ToolBox, Water - Specific Heat）
CP_20 = 4.1844        # kJ/(kg·K) 水 20℃（同）
CP_ACETIC = 123.1 / 60.052   # kJ/(kg·K) 酢酸（液体）298 K（NIST WebBook、Martin & Andon 1982）
ACID_MASS_FRAC = 0.042       # 穀物酢の酸度の例（近似の差を見積もるだけ）
RHO_VINEGAR = 1010.0         # kg/m³ 酢（近似の差を見積もるだけ、仮定）

WATER_L = 1.0
T_BOIL = 100.0
T_ADD = 20.0
EGG_G = 60.0
EGG_T0 = 20.0
POWERS_KW = [1.0, 1.5, 2.0]   # 仮定（湯に入る正味の加熱量）
POT_J_K = 500.0               # 感度（仮定）
H_WATER = 800.0               # 感度（rules.yaml egg_sphere.Bi_air の注記の湯の例題）
NODES = 240
DT_S = 0.5
T_END_S = 240.0
DEPTH_AT_S = [5, 10, 30, 60]

SOURCES = {
    "etb_water_cp": "Engineering ToolBox, \"Water - Specific Heat vs. Temperature\" https://www.engineeringtoolbox.com/specific-heat-capacity-water-d_660.html（20℃ 4.1844・100℃ 4.2157 kJ/(kg·K)）",
    "etb_water_rho": "Engineering ToolBox, \"Water - Density, Specific Weight and Thermal Expansion Coefficients\" https://www.engineeringtoolbox.com/water-density-specific-weight-d_595.html（20℃ 998.21・100℃ 958.35 kg/m³）",
    "nist_acetic": "NIST Chemistry WebBook, Acetic acid, Condensed phase thermochemistry data https://webbook.nist.gov/cgi/cbook.cgi?ID=C64197&Mask=2（液体の Cp 123.1 J/(mol·K), 298.15 K, Martin and Andon 1982）",
}


def conditions() -> list[dict]:
    m_w = WATER_L * 1e-3 * RHO_100   # kg
    # ④ 湯が 85℃ になる差し水の量（鍋なし・卵なし）
    ml85 = m_w * CP_100 * (T_BOIL - 85) / (CP_20 * (85 - T_ADD)) / RHO_20 * 1e6
    rows = [{"id": "1", "key": "none", "label": "① 何も足さない", "what": "なし", "ml": 0.0}]
    for pct in (3.0, 4.5):
        rows.append({"id": "2", "key": f"vinegar{pct:g}", "label": f"② 酢 {pct:g}%", "what": "酢", "ml": WATER_L * pct * 10})
    for pct in (3.0, 4.5):
        rows.append({"id": "3", "key": f"water{pct:g}", "label": f"③ 水 {WATER_L * pct * 10:g} mL（② と同じ量）", "what": "水", "ml": WATER_L * pct * 10})
    for ml in (100.0, 150.0, 200.0, round(ml85)):
        rows.append({"id": "4", "key": f"more{ml:g}", "label": f"④ 差し水 {ml:g} mL", "what": "水", "ml": ml})
    return rows


def mix(ml: float, cp_add: float = CP_20, rho_add: float = RHO_20, pot: float = 0.0) -> dict:
    """足した直後の湯温（一様に混ざる）と湯の熱容量 J/K。"""
    m_w = WATER_L * 1e-3 * RHO_100   # kg
    m_a = ml * 1e-6 * rho_add       # kg
    Cw, Ca = m_w * CP_100 * 1000, m_a * cp_add * 1000
    T = (Cw * T_BOIL + Ca * T_ADD + pot * T_BOIL) / (Cw + Ca + pot)
    return {"T": T, "C": Cw + Ca + pot, "m_add_g": m_a * 1000,
            "reheat_kJ": (Cw + Ca + pot) * (T_BOIL - T) / 1000}


def set_nodes(n: int) -> None:
    params.rules()["sim"]["egg_kinetic"]["nodes"]["value"] = n


def depth_set_mm(g: EK.EggGrid, gel=0.9) -> float:
    """表面から続けて X ≥ gel になっている厚さ（mm）。"""
    i = g.n - 1
    while i >= 0 and g.X[i] >= gel:
        i -= 1
    inner = (i + 1) * g.dr
    return (g.R - inner) * 1000


def egg_heat(g: EK.EggGrid) -> float:
    return sum(EK._props(g.coef[i], g.T[i])[1] * g.coef[i]["cp"] * g.vol[i] * g.T[i] for i in range(g.n))


def simulate(ml: float, P_kW: float, pot: float = 0.0, h: float | None = None, cp_add=CP_20, rho_add=RHO_20,
             egg: bool = True, nodes: int | None = None) -> dict:
    mx = mix(ml, cp_add, rho_add, pot)
    Tw, C = mx["T"], mx["C"]
    set_nodes(nodes or NODES)
    g = EK.EggGrid(EGG_G, EGG_T0) if egg else None
    H0 = egg_heat(g) if egg else 0.0
    t = 0.0
    t_boil = 0.0 if Tw >= T_BOIL - 1e-9 else None
    Tmin = Tw
    hist = [(0.0, Tw)]
    depth = {}
    t_1mm = t_g50 = t_g90 = None
    Q_total = 0.0
    while t < T_END_S - 1e-9:
        if egg:
            g.step(Tw, DT_S / 60, h=h, sub_s=DT_S)
            H1 = egg_heat(g)
            Q = H1 - H0
            H0 = H1
        else:
            Q = 0.0
        Q_total += Q
        Tw = Tw + (P_kW * 1000 * DT_S - Q) / C
        if Tw >= T_BOIL:
            Tw = T_BOIL
            if t_boil is None:
                t_boil = t + DT_S
        Tmin = min(Tmin, Tw)
        t += DT_S
        if abs(t - round(t)) < 1e-9 and (t <= 60 or t % 5 == 0):
            hist.append((round(t, 1), round(Tw, 3)))
        if egg:
            d = depth_set_mm(g)
            for s in DEPTH_AT_S:
                if abs(t - s) < 1e-9:
                    depth[s] = d
            if t_1mm is None and d >= 1.0:
                t_1mm = t
            gw, _ = g.layer_stats("white")
            if t_g50 is None and gw >= 0.5:
                t_g50 = t
            if t_g90 is None and gw >= 0.9:
                t_g90 = t
    out = {"ml": ml, "P_kW": P_kW, "pot_J_K": pot, "h": h, "T_mix": mx["T"], "C_J_K": C, "reheat_kJ": mx["reheat_kJ"],
           "T_min": Tmin, "t_boil_s": t_boil, "hist": hist}
    if egg:
        gy, xy = g.layer_stats("yolk")
        out.update({"depth_mm": depth, "t_1mm_s": t_1mm, "t_white50_s": t_g50, "t_white90_s": t_g90,
                    "yolk_mean_X_end": xy, "yolk_g_end": gy, "T_center_end": g.T_center, "Q_egg_kJ": Q_total / 1000,
                    "R_cm": g.R * 100})
    return out


def surface_rate():
    """白身の反応の速さ k(T) と、X=0.9 に達するまでの時間（一定温度）。"""
    c = EK.K("white")
    rows = []
    for T in (80, 85, 90, 95, 97, 98, 99, 100):
        k = math.exp(math.log(float(c["A"])) - float(c["Ea"]) / (EK.R_GAS * (T + 273.15)))
        rows.append({"T": T, "k_per_s": k, "t90_s": math.log(10) / k})
    return rows


def main() -> None:
    conds = conditions()
    res = {"conditions": conds, "sources": SOURCES, "powers_kW": POWERS_KW, "nodes": NODES, "dt_s": DT_S,
           "assume": {"water_L": WATER_L, "T_add": T_ADD, "egg_g": EGG_G, "egg_T0": EGG_T0, "pot_J_K_sens": POT_J_K,
                      "h_sens": H_WATER, "acid_mass_frac": ACID_MASS_FRAC, "rho_vinegar": RHO_VINEGAR,
                      "cp_vinegar": (1 - ACID_MASS_FRAC) * CP_20 + ACID_MASS_FRAC * CP_ACETIC},
           "rate": surface_rate(), "runs": {}}
    cp_v = res["assume"]["cp_vinegar"]
    for c in conds:
        r = {}
        for P in POWERS_KW:
            r[f"P{P:g}"] = simulate(c["ml"], P)
        r["noegg_P1.5"] = simulate(c["ml"], 1.5, egg=False)
        r["pot_P1.5"] = simulate(c["ml"], 1.5, pot=POT_J_K)
        r["h800_P1.5"] = simulate(c["ml"], 1.5, h=H_WATER)
        if c["what"] == "酢":
            r["vinegar_props_P1.5"] = simulate(c["ml"], 1.5, cp_add=cp_v, rho_add=RHO_VINEGAR)
        res["runs"][c["key"]] = r
        print(c["label"], f"T_mix {r['P1.5']['T_mix']:.2f}", f"boil {r['P1.5']['t_boil_s']}", f"1mm {r['P1.5']['t_1mm_s']}")
    # 格子の確かめ（節点 120 と 240、① と ④200）
    conv = {}
    for n in (120, 240, 480):
        conv[n] = {k: {kk: v for kk, v in simulate(ml, 1.5, nodes=n).items() if kk in ("t_1mm_s", "t_white50_s", "t_white90_s", "depth_mm")}
                   for k, ml in (("none", 0.0), ("more200", 200.0))}
    set_nodes(60)
    res["convergence"] = conv
    OUT.mkdir(exist_ok=True)
    (OUT / "output.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "output.md").write_text(report(res), encoding="utf-8")
    print("wrote", OUT / "output.md")


# ---------------- 表 ----------------

def f(v, d=1, unit=""):
    return "—" if v is None else f"{v:.{d}f}{unit}"


def report(res: dict) -> str:
    L = ["# Exp-19 実行結果（run.py が生成）", "",
         "Claude の記録。計画は plan.md（実行前にコミット、e6b6ebc）。1 L の沸騰した湯（100℃）に 20℃の液を足し、すぐ 60 g の卵（20℃）を落とす。", "",
         "## 1. 足した直後の湯温と、沸騰が戻るまで（火力 1.5 kW、卵あり）", "",
         "| 条件 | 足した量 | 足した直後の湯温 | 卵を入れた後の最低 | 沸騰が戻るまで（1.0 / 1.5 / 2.0 kW） | 戻すのに要る熱 |",
         "|---|---|---|---|---|---|"]
    for c in res["conditions"]:
        r = res["runs"][c["key"]]
        b = " / ".join(f(r[f"P{P:g}"]["t_boil_s"], 0, " 秒") if r[f"P{P:g}"]["t_boil_s"] is not None else f"{T_END_S:g} 秒より後" for P in res["powers_kW"])
        L.append(f"| {c['label']} | {c['ml']:g} mL | {r['P1.5']['T_mix']:.2f}℃ | {r['P1.5']['T_min']:.2f}℃ | {b} | {r['P1.5']['reheat_kJ']:.1f} kJ |")
    L += ["", "- 「沸騰が戻るまで」は 100℃ 未満での蒸発・放熱を無視した下限。① は卵が奪う熱より火力が大きく、湯は 100℃ のまま（0 秒）",
          f"- 卵が湯から奪う熱は 4 分間で {res['runs']['none']['P1.5']['Q_egg_kJ']:.1f} kJ（①）。どの条件でも毎秒の奪う熱は火力より小さく、卵を入れても湯温は足した直後より下がらない",
          f"- 卵の半径（同じ質量の球）{res['runs']['none']['P1.5']['R_cm']:.2f} cm", ""]
    L += ["## 2. 白身の固まり方（火力 1.5 kW、表面＝湯温）", "",
          "| 条件 | 固まった厚さ 5 秒 | 10 秒 | 30 秒 | 60 秒 | 外側 1 mm まで | 白身の半分 | 白身の9割 | 4 分後の黄身の平均 X |",
          "|---|---|---|---|---|---|---|---|---|"]
    for c in res["conditions"]:
        r = res["runs"][c["key"]]["P1.5"]
        d = r["depth_mm"]
        L.append(f"| {c['label']} | " + " | ".join(f(d.get(s) if s in d else d.get(str(s)), 2, " mm") for s in DEPTH_AT_S)
                 + f" | {f(r['t_1mm_s'], 1, ' 秒')} | {f(r['t_white50_s'], 0, ' 秒')} | {f(r['t_white90_s'], 0, ' 秒') if r['t_white90_s'] is not None else f'{T_END_S:g} 秒で届かない'} | {r['yolk_mean_X_end']:.2f} |")
    L += ["", "## 3. 感度", "",
          "| 条件 | 主（1.5 kW・鍋なし・表面＝湯温） 外側 1 mm / 沸騰が戻るまで | 鍋 500 J/K | 表面 h=800 | 卵なし（沸騰が戻るまで） | 酢の物性（c 4.10・ρ 1.01） |",
          "|---|---|---|---|---|---|"]
    for c in res["conditions"]:
        r = res["runs"][c["key"]]
        m, p, h, n = r["P1.5"], r["pot_P1.5"], r["h800_P1.5"], r["noegg_P1.5"]
        v = r.get("vinegar_props_P1.5")
        L.append(f"| {c['label']} | {f(m['t_1mm_s'], 1)} 秒 / {f(m['t_boil_s'], 0)} 秒 | {f(p['t_1mm_s'], 1)} / {f(p['t_boil_s'], 0)} 秒（直後 {p['T_mix']:.2f}℃） | "
                 f"{f(h['t_1mm_s'], 1)} 秒 | {f(n['t_boil_s'], 0)} 秒 | "
                 + (f"直後 {v['T_mix']:.2f}℃・1 mm {f(v['t_1mm_s'], 1)} 秒・沸騰 {f(v['t_boil_s'], 0)} 秒" if v else "—") + " |")
    L += ["", "## 4. 白身の反応の速さ（一定温度で X=0.9 に達するまで）", "", "| 温度 | k（/秒） | X=0.9 まで |", "|---|---|---|"]
    for row in res["rate"]:
        L.append(f"| {row['T']}℃ | {row['k_per_s']:.3g} | {row['t90_s']:.3g} 秒 |")
    L += ["", "## 5. 格子の確かめ（1.5 kW）", "", "| 節点 | 条件 | 外側 1 mm | 白身の半分 | 白身の9割 |", "|---|---|---|---|---|"]
    for n, d in res["convergence"].items():
        for k, r in d.items():
            L.append(f"| {n} | {k} | {f(r['t_1mm_s'], 1)} 秒 | {f(r['t_white50_s'], 0)} 秒 | {f(r['t_white90_s'], 0)} 秒 |")
    L += ["", "## 出典", ""] + [f"- {k}: {v}" for k, v in res["sources"].items()] + [""]
    return "\n".join(L)


if __name__ == "__main__":
    main()
