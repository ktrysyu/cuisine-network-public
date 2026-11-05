"""Exp-17: 殻付き卵を熱伝導と変性の速さで解いた場合（kinetic）と、今の形（stage）を並べる。

    uv run python experiments/exp-17-egg-kinetics/run.py

計画は plan.md（実行前にコミット、d1668ef）。結果は results/output.md・output.json。
両方を set_model で明示して並べる（Exp-14 の sim の既定 rules.yaml sim.egg_model は 2026-09-30 に kinetic に切り替えた）。
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP14 = HERE.parent / "exp-14"
EXP15 = HERE.parent / "exp-15-recipes"
sys.path.insert(0, str(EXP14))
sys.path.insert(1, str(EXP15))

from run import NO_MATCH_BELOW  # noqa: E402  (exp-14/run.py)
from sim import DISH_RECIPES, DISH_RECIPES_TIMED, PAIRS, maps, params, verdict  # noqa: E402
from sim import egg_kinetic as EK  # noqa: E402
from sim.recipes import AFTER_ICE, AFTER_REST, Recipe  # noqa: E402
from sim.state import EGG_SHELL  # noqa: E402

import overlay as OV  # noqa: E402  (exp-15-recipes/overlay.py)

OUT = HERE / "results"
DJ = {k: d["ja"] for k, d in params.dishes().items()}


def nm(k):
    return {None: "該当なし", maps.NONE: "該当なし", maps.RAW: "生のまま"}.get(k, DJ.get(k, k))


def with_model(name, fn):
    EK.set_model(name)
    try:
        return fn()
    finally:
        EK.set_model(None)


def set_nodes(n):
    params.rules()["sim"]["egg_kinetic"]["nodes"]["value"] = n


# ----------------------------------------------------------------------
def grid_run(T, minutes, T0=20.0, **kw):
    g = EK.EggGrid(kw.pop("mass", 60.0), T0, **kw)
    for _ in range(int(round(minutes * 10))):
        g.step(T, 0.1)
    return g


def check_impl():
    rows = []
    for n in (60, 120):
        set_nodes(n)
        for T, t in ((100, 6.5), (100, 12), (68, 30)):
            g = grid_run(T, t)
            gw, xw = g.layer_stats("white")
            gy, xy = g.layer_stats("yolk")
            rows.append({"nodes": n, "T": T, "t": t, "Tc": g.T_center, "gw": gw, "xw": xw, "gy": gy, "xy": xy})
    set_nodes(60)
    # tatsu2019: 20℃ → 68℃ の湯で中心が 67℃ に達する時間
    g = EK.EggGrid(60.0, 20.0)
    t = 0.0
    while g.T_center < 67.0 and t < 120:
        g.step(68, 0.1)
        t += 0.1
    tatsu = t
    # Di Lorenzo et al. 2025 の形（7×5cm の楕円と同じ体積の球、黄身の半径 1.5cm）
    R = (3.5 * 2.5 * 2.5) ** (1 / 3) / 100
    dm = []
    for T, t in ((100, 12), (100, 6), (65, 60)):
        g = grid_run(T, t, radius_m=R, yolk_radius_m=0.015)
        wi = [g.X[i] for i in range(g.n) if g.layer[i] == "white"]
        dm.append({"T": T, "t": t, "Tc": g.T_center, "Xy_center": g.X[0], "Xw_min": min(wi),
                   "xw": g.layer_stats("white")[1], "xy": g.layer_stats("yolk")[1]})
    Rm = EK.EggGrid(60.0, 20.0)
    k, rho, cp = EK._props("white", 20.0)
    alpha = k / (rho * cp)
    return {"conv": rows, "tatsu_min": tatsu, "dimonaco": dm, "R_cm": Rm.R * 100, "a_cm": Rm.a * 100,
            "alpha_white": alpha, "R2_over_alpha_min": (Rm.R ** 2) / alpha / 60}


def timeline(T, after, times):
    out = []
    for t in times:
        r = Recipe("t", {"egg_whole": 60}, [("simmer", {"T": T, "time": t, "form": "shell"}), after], egg_form=EGG_SHELL)
        s = r.run()
        v = verdict(s, NO_MATCH_BELOW)
        row = {"t": t, "answer": v.answer, "top": v.candidates[0].dish if v.candidates else None,
               "white": s.egg_white_stage, "yolk": s.egg_yolk_stage, "Tc_max": s.T_core_max}
        if s.egg_kin is not None:
            row["gw"], row["xw"] = s.egg_kin.layer_stats("white")
            row["gy"], row["xy"] = s.egg_kin.layer_stats("yolk")
        out.append(row)
    return out


def answers():
    out = {}
    for name, D in (("状態で止める版", DISH_RECIPES), ("時間の版", DISH_RECIPES_TIMED)):
        for k, r in D.items():
            s = r.run()
            out[f"{name}: {r.name}"] = {"expected": r.expected, "answer": verdict(s, NO_MATCH_BELOW).answer,
                                       "white": s.egg_white_stage, "yolk": s.egg_yolk_stage, "shell": s.egg_form == EGG_SHELL}
    for i, p in enumerate(PAIRS, 1):
        for side, r in (("A", p.a), ("B", p.b)):
            s = r.run()
            out[f"組{i}{side}: {r.name}"] = {"expected": r.expected, "answer": verdict(s, NO_MATCH_BELOW).answer,
                                           "white": s.egg_white_stage, "yolk": s.egg_yolk_stage, "shell": s.egg_form == EGG_SHELL}
    return out


def shell_maps():
    return {p["id"]: maps.preset_grid(p, NO_MATCH_BELOW) for p in maps.PRESETS if p["id"].startswith("shell")}


def overlay_tally():
    d = OV.build()
    pts = d["points"] if isinstance(d, dict) and "points" in d else d
    by = Counter()
    ok = Counter()
    rows = []
    for p in pts:
        dish = p.get("dish")
        match = bool(p.get("match"))
        by[dish] += 1
        ok[dish] += match
        rows.append({"id": p.get("row_id"), "dish": dish, "answer": p.get("answer"), "match": match})
    return {"by": dict(by), "ok": dict(ok), "rows": rows}


def main():
    t0 = time.time()
    OUT.mkdir(exist_ok=True)
    impl = check_impl()
    res = {"impl": impl}
    for m in ("stage", "kinetic"):
        res[m] = with_model(m, lambda: {
            "answers": answers(),
            "tl_100_ice": timeline(100, AFTER_ICE, [1, 2, 3, 4, 5, 6, 6.5, 7, 8, 9, 10, 11, 12, 13, 15]),
            "tl_100_rest": timeline(100, AFTER_REST, [4, 5, 6, 6.5, 7, 8, 10, 12]),
            "tl_68_ice": timeline(68, AFTER_ICE, [10, 15, 20, 25, 30, 40, 50, 60]),
            "maps": shell_maps(),
            "overlay": overlay_tally(),
        })
    # 感度（事前に決めた代わりの値）: 正解のレシピと組の答え、重ね合わせ
    sens = []
    for label, vals in (("gel_X=0.5", {"gel_X": 0.5}), ("gel_X=0.99", {"gel_X": 0.99}),
                        ("stage2_g=0.3", {"stage2_g": 0.3}), ("stage2_g=0.7", {"stage2_g": 0.7})):
        EK.set_params(vals)
        a = with_model("kinetic", answers)
        ov = with_model("kinetic", overlay_tally)
        EK.set_params(None)
        base = res["kinetic"]["answers"]
        sens.append({"label": label, "changed": [k for k in a if a[k]["answer"] != base[k]["answer"]],
                     "overlay_ok": sum(ov["ok"].values()), "overlay_n": sum(ov["by"].values()),
                     "answers": {k: a[k]["answer"] for k in a}})
    res["sens"] = sens
    res["elapsed_s"] = time.time() - t0
    write(res)


def f(v, d=2):
    return "—" if v is None else f"{v:.{d}f}"


def write(res):
    I = res["impl"]
    L = ["# Exp-17 実行結果（run.py が生成）", "",
         "Claude の記録。計画は plan.md（実行前にコミット、d1668ef）。stage = Exp-14 の今の形、kinetic = 2層の球の差分＋変性の一次反応。",
         "", "## 1. 実装の確かめ", "",
         f"- 60g の卵: 半径 {I['R_cm']:.2f} cm、黄身の半径 {I['a_cm']:.2f} cm。白身の熱拡散率（20℃）{I['alpha_white']:.3g} m²/s、R²/α = {I['R2_over_alpha_min']:.1f} 分（Exp-14 が tatsu2019 に合わせた値は 60.5 分）",
         f"- **tatsu2019（照合、合わせ込みなし）**: 20℃の卵を 68℃の湯に入れて中心が 67℃に達するのは **{I['tatsu_min']:.1f} 分**（論文 約28分）",
         "", "### 格子の細かさ（60 と 120 節点）", "",
         "| 節点 | 条件 | 中心の温度 | 白身 固まった割合 / 平均 X | 黄身 固まった割合 / 平均 X |", "|---|---|---|---|---|"]
    for r in I["conv"]:
        L.append(f"| {r['nodes']} | {r['T']}℃ {r['t']}分（湯の中の終わり） | {r['Tc']:.1f} | {r['gw']:.2f} / {r['xw']:.2f} | {r['gy']:.2f} / {r['xy']:.2f} |")
    L += ["", "### Di Lorenzo et al. 2025 の条件（7×5cm の楕円と同じ体積の球、黄身の半径 1.5cm、20℃から）", "",
          "| 条件 | 論文の本文 | 計算: 中心の温度 | 黄身の中心の X | 白身の X の最小 | 平均 X 白身 / 黄身 |", "|---|---|---|---|---|---|"]
    txt = {(100, 12): "全体が 100℃、白身・黄身とも X=1", (100, 6): "白身は X=1、黄身は中心で 0.5 まで下がる",
           (65, 60): "黄身は X=1、白身は 1 に届かない"}
    for r in I["dimonaco"]:
        L.append(f"| {r['T']}℃ {r['t']}分 | {txt[(r['T'], r['t'])]} | {r['Tc']:.1f} | {r['Xy_center']:.2f} | {r['Xw_min']:.2f} | {r['xw']:.2f} / {r['xy']:.2f} |")

    for key, title in (("tl_100_ice", "沸騰した湯 → 氷水 15分"), ("tl_100_rest", "沸騰した湯 → 室温に置く 15分"), ("tl_68_ice", "68℃の湯 → 氷水 15分")):
        L += ["", f"## 2. 時間ごとの答え（{title}、60g・冷蔵庫ではなく 20℃から）", "",
              "| 分 | stage: 答え（白身/黄身の段階） | kinetic: 答え（白身/黄身の段階） | kinetic: 白身 固まった割合・平均X | kinetic: 黄身 固まった割合・平均X | 中心の最高温度 stage / kinetic |",
              "|---|---|---|---|---|---|"]
        for a, b in zip(res["stage"][key], res["kinetic"][key]):
            L.append(f"| {a['t']:g} | {nm(a['answer'])}（{a['white']}/{a['yolk']}） | {nm(b['answer'])}（{b['white']}/{b['yolk']}） | "
                     f"{f(b.get('gw'))}・{f(b.get('xw'))} | {f(b.get('gy'))}・{f(b.get('xy'))} | {a['Tc_max']:.1f} / {b['Tc_max']:.1f} |")

    A, B = res["stage"]["answers"], res["kinetic"]["answers"]
    changed = [k for k in A if A[k]["answer"] != B[k]["answer"]]
    L += ["", "## 3. 正解のレシピと順番を変えた組", "",
          f"答えが変わったもの: **{len(changed)}/{len(A)}**", ""]
    L += ["| 入力 | 期待 | stage | kinetic |", "|---|---|---|---|"]
    for k in A:
        if A[k]["shell"] or k in changed:
            L.append(f"| {k} | {nm(A[k]['expected'])} | {nm(A[k]['answer'])}（{A[k]['white']}/{A[k]['yolk']}） | "
                     f"{nm(B[k]['answer'])}（{B[k]['white']}/{B[k]['yolk']}）{' ← 変化' if k in changed else ''} |")
    L += ["", "（殻付き卵の行と、答えが変わった行だけ。括弧は白身/黄身の段階）", "", "## 4. 殻付き卵の地図の変化", "",
          "| 地図 | マス | 変わったマス | 主な変化（stage → kinetic） |", "|---|---|---|---|"]
    for pid in res["stage"]["maps"]:
        Ga, Gb = res["stage"]["maps"][pid], res["kinetic"]["maps"][pid]
        ch, n = Counter(), 0
        for j in range(len(Ga["ys"])):
            for i in range(len(Ga["xs"])):
                n += 1
                x, y = Ga["cells"][j][i]["cls"], Gb["cells"][j][i]["cls"]
                if x != y:
                    ch[(x, y)] += 1
        L.append(f"| {pid} | {n} | {sum(ch.values())} | " + "、".join(f"{nm(x)}→{nm(y)} {c}" for (x, y), c in ch.most_common(8)) + " |")
    for pid in res["stage"]["maps"]:
        for m in ("stage", "kinetic"):
            G = res[m]["maps"][pid]
            cnt = Counter(c["cls"] for row in G["cells"] for c in row)
            L.append(f"- {pid}（{m}）: " + "、".join(f"{nm(k)} {v}" for k, v in cnt.most_common()))
    L += ["", "## 5. 世の中のレシピとの一致（Exp-15 の重ね合わせ、28点）", "", "| 料理 | stage | kinetic |", "|---|---|---|"]
    oa, ob = res["stage"]["overlay"], res["kinetic"]["overlay"]
    for d in oa["by"]:
        L.append(f"| {OV.DISH_JA.get(d, d)} | {oa['ok'].get(d, 0)}/{oa['by'][d]} | {ob['ok'].get(d, 0)}/{ob['by'][d]} |")
    L.append(f"| **計** | **{sum(oa['ok'].values())}/{sum(oa['by'].values())}** | **{sum(ob['ok'].values())}/{sum(ob['by'].values())}** |")
    diffrows = [(a, b) for a, b in zip(oa["rows"], ob["rows"]) if a["match"] != b["match"] or a["answer"] != b["answer"]]
    if diffrows:
        L += ["", "答えが変わった点: " + "、".join(f"{a['id']}（{OV.DISH_JA.get(a['dish'], a['dish'])}）{nm(a['answer'])}→{nm(b['answer'])}" for a, b in diffrows)]
    L += ["", "## 6. 感度（事前に決めた代わりの値、kinetic）", "", "| 値 | 答えが変わった正解のレシピ・組 | 重ね合わせの一致 |", "|---|---|---|"]
    for s in res["sens"]:
        ch = "、".join(f"{k}→{nm(s['answers'][k])}" for k in s["changed"]) or "なし"
        L.append(f"| {s['label']} | {ch} | {s['overlay_ok']}/{s['overlay_n']} |")
    L += ["", f"計算時間 {res['elapsed_s']:.0f} 秒"]
    (OUT / "output.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    def slim(m):
        return {k: v for k, v in res[m].items() if k != "maps"}
    J = {"impl": res["impl"], "stage": slim("stage"), "kinetic": slim("kinetic"), "sens": res["sens"]}
    (OUT / "output.json").write_text(json.dumps(J, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
