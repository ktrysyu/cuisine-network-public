"""Exp-18 の下準備: 肉片を厚み方向の熱伝導で解く（slab）・揚げ物の吸油（oil_uptake）。

    uv run python experiments/exp-18-more-dishes/run.py

計画は plan.md の「採点を待たずにやる下準備」（実装前にコミット、11c83b1）。結果は results/output.md・output.json。
Exp-14 の sim の既定（rules.yaml sim.meat_model = tau、sim.oil_uptake.enabled = false）は変えない。ここで切り替える。
採点・料理の状態の条件・感じ方の変換はしない。
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
from sim import DISH_RECIPES, DISH_RECIPES_TIMED, PAIRS, maps, ops, params, verdict  # noqa: E402
from sim import meat_slab as MS  # noqa: E402
from sim.state import State  # noqa: E402

import overlay as OV  # noqa: E402  (exp-15-recipes/overlay.py)

OUT = HERE / "results"
DJ = {k: d["ja"] for k, d in params.dishes().items()}
P_MED, P_MED_LO, P_MED_HI = 175, 150, 190   # Exp-15 extraction_rules.md P-MED（弱い根拠）
P_HIGH, P_LOW = 230, 130                     # 同 P-HIGH・P-LOW（出典なし）
T_ROOM = 20


def nm(k):
    return {None: "該当なし", maps.NONE: "該当なし", maps.RAW: "生のまま"}.get(k, DJ.get(k, k))


class switch:
    """meat_model と oil_uptake を一時的に切り替える。"""

    def __init__(self, meat=None, oil=None, params_=None):
        self.meat, self.oil, self.params_ = meat, oil, params_

    def __enter__(self):
        MS.set_model(self.meat)
        MS.set_params(self.params_)
        node = params.rules()["sim"]["oil_uptake"]["enabled"]
        self.saved = node["value"]
        if self.oil is not None:
            node["value"] = self.oil
        return self

    def __exit__(self, *exc):
        MS.set_model(None)
        MS.set_params(None)
        params.rules()["sim"]["oil_uptake"]["enabled"]["value"] = self.saved
        return False


# ----------------------------------------------------------------------
# 1. 熱物性
def props_table():
    rows = []
    for k in ("beef", "chicken", "potato"):
        x = MS.mass_fractions({k: 100})
        for T in (20, 60):
            kk, rho, cp = MS.mix_props(x, T)
            rows.append({"food": k, "T": T, "k": kk, "rho": rho, "cp": cp, "alpha": kk / rho / cp,
                         "x": {c: round(v, 3) for c, v in x.items()}})
    return rows


# ----------------------------------------------------------------------
# 2. 焼き時間: 決まった間隔で返しながら、中心が target に達するまで
def time_to(target, T_pan, flip_min, thickness=20, mass=250, T0=T_ROOM, limit=30):
    s = State.from_ingredients({"beef": mass}, T0=T0, thickness_mm=thickness)
    t = 0.0
    while t < limit:
        s = ops.bake(s, T=T_pan, form="piece", until={"var": "T_core", "ge": target}, max_time=flip_min)
        st = s.stops[-1]
        t += st["minutes"]
        if st["reached"]:
            return round(t, 2), s
    return None, s


def after_rest(s, minutes=5):
    before = s.T_core
    r = ops.rest(s, T=T_ROOM, time=minutes)
    peak = max(h[1] for h in r.history[len(s.history):])
    return {"pull": before, "peak": peak, "rise": peak - before, "end": r.T_core}


def tokyogas():
    rows = []
    for T in (P_MED_LO, P_MED, P_MED_HI):
        for fl in (1.5, 0.25):
            t, s = time_to(55, T, fl)
            rows.append({"T": T, "flip": fl, "min": t, **after_rest(s)})
    return rows


AUSSIE_STEPS = [  # ミディアム（aussiebeef_steak）。弱火は後半の長さ 2・2.5・3分
    ("bake", {"T": P_HIGH, "time": 1.0, "form": "piece"}),
    ("bake", {"T": P_LOW, "time": 2.0, "form": "piece", "flip": False}),
    ("bake", {"T": P_HIGH, "time": 0.5, "form": "piece"}),
]


def aussie():
    rows = []
    for last in (2.0, 2.5, 3.0):
        s = State.from_ingredients({"beef": 250}, T0=T_ROOM, thickness_mm=20)
        s = ops.apply(s, AUSSIE_STEPS + [("bake", {"T": P_LOW, "time": last, "form": "piece", "flip": False})])
        rest = {m: after_rest(s, m) for m in (3, 5)}
        rows.append({"last": last, "total": 3.5 + last, "center": s.T_core, "flips": s.meat_slab.flips,
                     "rest3": rest[3], "rest5": rest[5]})
    return rows


def grid_check():
    out = {}
    for n in (40, 80):
        with switch("slab", params_={"nodes": n}):
            t, s = time_to(55, P_MED, 1.5)
            out[n] = {"min": t, **after_rest(s)}
    return out


def sens():
    rows = []
    for label, p in (("基準", {}), ("h_contact=150", {"h_contact": 150}), ("h_contact=600", {"h_contact": 600}),
                     ("h_top=10", {"h_top": 10})):
        with switch("slab", params_=p):
            t90, _ = time_to(55, P_MED, 1.5)
            t15, _ = time_to(55, P_MED, 0.25)
            ans = answers()
        rows.append({"label": label, "t90": t90, "t15": t15, "answers": {k: v["answer"] for k, v in ans.items()}})
    return rows


# ----------------------------------------------------------------------
# 3. 既存の答え
def answers():
    out = {}
    for name, D in (("状態で止める版", DISH_RECIPES), ("時間の版", DISH_RECIPES_TIMED)):
        for k, r in D.items():
            s = r.run()
            out[f"{name}: {r.name}"] = {"expected": r.expected, "answer": verdict(s, NO_MATCH_BELOW).answer,
                                       "T_core_max": round(s.T_core_max, 1), "meat": s.meat_slab is not None,
                                       "stops": [(x["until"], x["minutes"], x["reached"]) for x in s.stops]}
    for i, p in enumerate(PAIRS, 1):
        for side, r in (("A", p.a), ("B", p.b)):
            s = r.run()
            out[f"組{i}{side}: {r.name}"] = {"expected": r.expected, "answer": verdict(s, NO_MATCH_BELOW).answer,
                                           "T_core_max": round(s.T_core_max, 1), "meat": s.meat_slab is not None,
                                           "stops": []}
    return out


def overlay_tally():
    d = OV.build()
    pts = d["points"] if isinstance(d, dict) and "points" in d else d
    by, ok, rows = Counter(), Counter(), []
    for p in pts:
        dish = p.get("dish")
        by[dish] += 1
        ok[dish] += bool(p.get("match"))
        rows.append({"id": p.get("row_id"), "dish": dish, "answer": p.get("answer"), "match": bool(p.get("match"))})
    return {"by": dict(by), "ok": dict(ok), "rows": rows}


def chicken_detail():
    """鶏むね肉のソテーの正解のレシピ（両版）の中心温度と止まった時間。"""
    out = {}
    for m in ("tau", "slab"):
        with switch(m):
            out[m] = {"until": DISH_RECIPES["sauteed_chicken"].run(), "timed": DISH_RECIPES_TIMED["sauteed_chicken"].run()}
    return {m: {k: {"T_core_max": round(s.T_core_max, 1), "T_core": round(s.T_core, 1), "maillard": s.maillard,
                    "stops": [(x["until"], x["minutes"], x["reached"]) for x in s.stops],
                    "meat": s.summary()} for k, s in v.items()} for m, v in out.items()}


# ----------------------------------------------------------------------
# 4. 揚げ物の吸油
def fries():
    rows = []
    with switch(oil=True):
        for T in (150, 170, 190):
            for m in (3, 5, 7, 10):
                s0 = State.from_ingredients({"potato": 100}, T0=T_ROOM)
                s = ops.deep_fry(s0, T=T, time=m, form="thin")
                rows.append({"T": T, "min": m, "water_lost": s.water_lost, "oil": s.masses.get("vegetable_oil", 0.0),
                             "mass_ratio": s.mass / 100.0, "water": s.water, "fat": s.fat,
                             "cell_wall": s.cell_wall, "starch_gel": s.starch_gel})
    return rows


# ----------------------------------------------------------------------
# 5. 3品を今の規則で作ってみた状態（採点・判定の条件づけはしない）
def three_dishes():
    out = {}
    with switch("slab", True):
        s = State.from_ingredients({"beef": 250, "salt": 2}, T0=T_ROOM, thickness_mm=20)
        s = ops.apply(s, AUSSIE_STEPS + [("bake", {"T": P_LOW, "time": 2.5, "form": "piece", "flip": False}),
                                         ("rest", {"T": T_ROOM, "time": 5})])
        out["beef_steak"] = {"how": "牛肉 250g・厚さ20mm・塩 2g。強火1分→弱火2分→返して強火30秒→弱火2.5分→5分休ませる（aussiebeef_steak のミディアム）",
                             "state": s.summary()}
        s = State.from_ingredients({"potato": 150, "salt": 1}, T0=T_ROOM)
        s = ops.deep_fry(s, T=170, time=6, form="thin")
        out["french_fries"] = {"how": "じゃがいも 150g・塩 1g を 170℃の油で6分（form thin。温度・時間は仮）", "state": s.summary()}
        s = State.from_ingredients({"potato": 200, "salt": 1}, T0=T_ROOM)
        s = ops.simmer(s, T=100, time=15, form="pot")
        s = ops.bake(s, T=150, time=2, stirring=True, form="thin")
        out["boiled_potato"] = {"how": "じゃがいも 200g・塩 1g を 100℃で15分ゆで、鍋で2分ゆすって水気を飛ばす（ゆで湯は材料に入れない。時間は仮）",
                                "state": s.summary()}
    return out


# ----------------------------------------------------------------------
def main():
    t0 = time.time()
    OUT.mkdir(exist_ok=True)
    res = {"props": props_table()}
    with switch("slab"):
        res["tokyogas"] = tokyogas()
        res["aussie"] = aussie()
    res["grid"] = grid_check()
    res["chicken"] = chicken_detail()
    for label, meat, oil in (("tau", "tau", False), ("slab", "slab", False), ("slab+oil", "slab", True)):
        with switch(meat, oil):
            res[label] = {"answers": answers(), "overlay": overlay_tally()}
    res["sens"] = sens()
    res["fries"] = fries()
    res["dishes"] = three_dishes()
    res["elapsed_s"] = time.time() - t0
    (OUT / "output.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    write(res)


def f(v, d=1):
    return "—" if v is None else f"{v:.{d}f}"


def write(res):
    L = ["# Exp-18 下準備の結果（run.py が生成）", "",
         "計画: plan.md「採点を待たずにやる下準備」。既定（meat_model = tau・oil_uptake off）は変えず、ここで切り替えた。", ""]
    L += ["## 1. 熱物性（Choi & Okos の式、成分は成分表）", "",
          "| 食材 | ℃ | k W/(m·K) | ρ kg/m³ | cp J/(kg·K) | 熱拡散率 m²/s |", "|---|---|---|---|---|---|"]
    for r in res["props"]:
        L.append(f"| {r['food']} | {r['T']} | {r['k']:.3f} | {r['rho']:.0f} | {r['cp']:.0f} | {r['alpha']:.2e} |")
    L += ["", "実測（ashrae_thermal）: 牛赤身 k 0.40〜0.51（表5）、牛もも 1.3×10⁻⁷・牛肩 1.2×10⁻⁷ m²/s（表7）、じゃがいも 1.3×10⁻⁷（表7）", ""]
    L += ["## 2. 焼き時間（牛肉 250g・厚さ20mm・20℃から、tokyogas_steak の条件）", "",
          "中心が 55℃ に達するまでの時間。東京ガスの実測は 90秒ごとに返して 6分30秒〜7分、15秒ごとに返して 5分30秒〜6分。",
          "", "| 鍋 ℃ | 返す間隔 | 55℃まで（分） | 休ませる5分の中心の最高 | 上昇 |", "|---|---|---|---|---|"]
    for r in res["tokyogas"]:
        L.append(f"| {r['T']} | {r['flip'] * 60:.0f}秒 | {f(r['min'], 2)} | {f(r['peak'])} | +{f(r['rise'])} |")
    g = res["grid"]
    L += ["", f"節点 40・80（175℃・90秒）: {f(g[40]['min'], 2)}分・{f(g[80]['min'], 2)}分、休ませた後の最高 {f(g[40]['peak'])}・{f(g[80]['peak'])}℃", ""]
    L += ["### オージー・ビーフのミディアムの手順（強火 230℃・弱火 130℃、どちらも出典なしの推定）", "",
          "記載: 強火1分→弱火2分→返して強火30秒→弱火2〜3分で中心 約55℃、3〜5分休ませる。", "",
          "| 最後の弱火 | 合計 | 焼き上がりの中心 | 3分休ませた最高（上昇） | 5分休ませた最高（上昇） |", "|---|---|---|---|---|"]
    for r in res["aussie"]:
        L.append(f"| {r['last']:g}分 | {r['total']:g}分 | {f(r['center'])} | {f(r['rest3']['peak'])}（+{f(r['rest3']['rise'])}） | "
                 f"{f(r['rest5']['peak'])}（+{f(r['rest5']['rise'])}） |")
    L += ["", "ミディアムの中心温度（出典ごとにばらつく）: aussiebeef_steak 約55℃／thermoworks_medium 57〜63℃／wiki_doneness 60〜65℃／ebara_steak 65〜70℃。",
          "休ませる間の上昇: thermoworks_medium 約 1.7℃（3°F）、amsa2015 は速く焼くと 5℃ を超えることがある。", ""]
    L += ["## 3. 既存の答え（正解のレシピ 2版＋順番を変えた7組）", ""]
    A, B, C = res["tau"]["answers"], res["slab"]["answers"], res["slab+oil"]["answers"]
    ch = [k for k in A if A[k]["answer"] != B[k]["answer"]]
    ch2 = [k for k in A if A[k]["answer"] != C[k]["answer"]]
    L += [f"- tau → slab で答えが変わったもの: {len(ch)}/{len(A)}" + ("（" + "、".join(ch) + "）" if ch else ""),
          f"- tau → slab＋吸油 で答えが変わったもの: {len(ch2)}/{len(A)}" + ("（" + "、".join(ch2) + "）" if ch2 else ""),
          f"- 肉片の計算が slab になったもの: " + "、".join(k for k in B if B[k]["meat"]), ""]
    L += ["| レシピ | 期待 | tau | slab |", "|---|---|---|---|"]
    for k in A:
        L.append(f"| {k} | {nm(A[k]['expected'])} | {nm(A[k]['answer'])} | {nm(B[k]['answer'])}{' ← 変化' if k in ch else ''} |")
    c = res["chicken"]
    L += ["", "鶏むね肉のソテー（厚さ20mm、書いていないときの値）の中心:", ""]
    for m in ("tau", "slab"):
        for k, v in c[m].items():
            st = "、".join(f"{u} {mm:g}分{'' if ok else '（未到達）'}" for u, mm, ok in v["stops"]) or "時間で止める（5分＋5分）"
            L.append(f"- {m}・{'状態で止める版' if k == 'until' else '時間の版'}: 中心の最高 {v['T_core_max']}℃、maillard {v['maillard']}。{st}")
    oa, ob = res["tau"]["overlay"], res["slab"]["overlay"]
    L += ["", f"世の中のレシピの重ね合わせ（Exp-15）: tau {sum(oa['ok'].values())}/{sum(oa['by'].values())}・slab {sum(ob['ok'].values())}/{sum(ob['by'].values())}・"
          f"slab＋吸油 {sum(res['slab+oil']['overlay']['ok'].values())}/{sum(res['slab+oil']['overlay']['by'].values())}"]
    diff = [(a, b) for a, b in zip(oa["rows"], ob["rows"]) if a["answer"] != b["answer"]]
    if diff:
        L.append("答えが変わった点: " + "、".join(f"{a['id']}（{a['dish']}）{nm(a['answer'])}→{nm(b['answer'])}" for a, b in diff))
    L += ["", "## 4. 感度（175℃、牛肉 20mm、中心 55℃まで）", "", "| 条件 | 90秒ごと | 15秒ごと | 答えが変わった数（tau と比べて） |", "|---|---|---|---|"]
    for r in res["sens"]:
        chg = [f"{k}→{nm(r['answers'][k])}" for k in A if r["answers"][k] != A[k]["answer"]]
        L.append(f"| {r['label']} | {f(r['t90'], 2)} | {f(r['t15'], 2)} | {len(chg)}{'（' + '、'.join(chg) + '）' if chg else ''} |")
    L += ["", "## 5. 揚げ物の吸油（じゃがいも 100g、form thin、oil_uptake on）", "",
          "成分表（02067、くし形 1.5×1.5×5.0cm・二度揚げ）: 水分 64.2%・脂質 5.9%・重量変化率 71%・吸油量 4.0g／生 100g・水の減り 34.2g。", "",
          "| 油 ℃ | 分 | 水の減り g | 吸油 g | 重量比 | 水分 % | 脂質 % | 細胞壁 |", "|---|---|---|---|---|---|---|---|"]
    for r in res["fries"]:
        L.append(f"| {r['T']} | {r['min']} | {r['water_lost']:.1f} | {r['oil']:.2f} | {r['mass_ratio']:.2f} | {r['water']:.1f} | {r['fat']:.1f} | {r['cell_wall']} |")
    L += ["", "## 6. 3品を今の規則で作ってみた状態（slab＋吸油。採点・判定の条件づけはしていない）", ""]
    keys = ["T_core_max", "T_serve", "water", "fat", "salt_conc", "mass_ratio", "maillard", "cell_wall", "starch_gel",
            "meat_myosin", "meat_actin", "meat_myoglobin", "meat_water_loss"]
    for k, v in res["dishes"].items():
        st = v["state"]
        L.append(f"- **{k}**: {v['how']}")
        L.append("  - " + "、".join(f"{x} {st[x]}" for x in keys if x in st))
    L += ["", f"（計算 {res['elapsed_s']:.0f}秒）", ""]
    (OUT / "output.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
