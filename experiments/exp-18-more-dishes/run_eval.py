"""Exp-18 採点の後: 16品で Exp-11 と同じ評価（1品抜き・感じ方の距離 x/16、硬さ・なめらかさの誤差）。

    uv run python experiments/exp-18-more-dishes/run_eval.py

計画は plan.md の「採点の後」（計算する前にコミット、51f0849）。結果は results/eval_output.md・eval_output.json。
- 本人の採点: data/labels/dish_perception_v2_input.csv（16品）
- 状態: 13品は Exp-14 の正解のレシピ（状態で止める版）、追加3品は sim/recipes.py の EXP18_RECIPES
- 肉の計算と吸油は2通り（tau＋吸油 off＝今の既定／slab＋吸油 on）で回して並べる。rules.yaml の既定は変えない
- 物性値・変換は Exp-11 のまま（texture_rules.yaml を変えない）
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
EXP14 = HERE.parent / "exp-14"
EXP11 = HERE.parent / "exp-11"
sys.path.insert(0, str(EXP14))

import importlib.util  # noqa: E402

import perception as P14  # noqa: E402
from run import NO_MATCH_BELOW  # noqa: E402  (exp-14/run.py)
from sim import DISH_RECIPES, THIRTEEN, meat_slab as MS, params, verdict  # noqa: E402
from sim.recipes import EXP18_RECIPES, EXP18_RECIPES_TIMED  # noqa: E402

_spec = importlib.util.spec_from_file_location("exp11_run", EXP11 / "run.py")
E11 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E11)

LABELS = ROOT / "data" / "labels" / "dish_perception_v2_input.csv"
NEW3 = list(EXP18_RECIPES)
SIXTEEN = THIRTEEN + NEW3
OUT = HERE / "results"
CONFIGS = [("tau＋吸油 off（今の既定）", "tau", False), ("slab＋吸油 on", "slab", True)]


def load_labels() -> dict[str, dict[str, float]]:
    with LABELS.open(encoding="utf-8") as f:
        return {r["dish"]: {k: float(r[k]) for k in P14.ITEMS} for r in csv.DictReader(f)}


class switch:
    def __init__(self, meat, oil):
        self.meat, self.oil = meat, oil

    def __enter__(self):
        MS.set_model(self.meat)
        node = params.rules()["sim"]["oil_uptake"]["enabled"]
        self.saved = node["value"]
        node["value"] = self.oil

    def __exit__(self, *exc):
        MS.set_model(None)
        params.rules()["sim"]["oil_uptake"]["enabled"]["value"] = self.saved
        return False


def recipe(k):
    return DISH_RECIPES[k] if k in DISH_RECIPES else EXP18_RECIPES[k]


def summary(ev, n) -> dict:
    M = ev["metrics"]
    return {
        "n": n,
        "mae": {i: {"A": M[i]["mae_A"], "C": M[i]["mae_C"], "base": M[i]["mae_base"], "e14_loo": M[i]["mae_14_loo"]} for i in E11.NEW},
        "rho_index": {i: M[i]["rho_index"] for i in E11.NEW},
        "hits": ev["hits"], "hits_v": ev["hits_v"],
    }


def main() -> None:
    labels = load_labels()
    dj = {k: d["ja"] for k, d in params.dishes().items()}
    nm = lambda k: "該当なし" if k is None else dj.get(k, k)  # noqa: E731
    res = {}
    for name, meat, oil in CONFIGS:
        with switch(meat, oil):
            states = {k: recipe(k).run() for k in SIXTEEN}
            timed = {k: EXP18_RECIPES_TIMED[k].run() for k in NEW3}
            rows = {k: P14.row_of(states[k]) for k in SIXTEEN}
            lab13 = {k: labels[k] for k in THIRTEEN}
            ev13 = E11.evaluate(E11.RULES, lab13, states, rows, dishes=THIRTEEN)
            ev16 = E11.evaluate(E11.RULES, labels, states, rows, dishes=SIXTEEN)
            res[name] = {
                "ev13": ev13, "ev16": ev16,
                "s13": summary(ev13, 13), "s16": summary(ev16, 16),
                "states": {k: {"answer": verdict(states[k], NO_MATCH_BELOW).answer, "T_core_max": states[k].T_core_max,
                               "maillard": states[k].maillard, "cell_wall": states[k].cell_wall, "starch_gel": states[k].starch_gel,
                               "water": states[k].nutrient_g("water") / states[k].mass * 100, "fat": states[k].nutrient_g("fat") / states[k].mass * 100,
                               "myoglobin": states[k].meat_myoglobin, "ops": states[k].ops} for k in NEW3 + ["sauteed_chicken"]},
                "timed": {k: {"answer": verdict(timed[k], NO_MATCH_BELOW).answer, "T_core_max": timed[k].T_core_max, "maillard": timed[k].maillard}
                          for k in NEW3},
            }

    V = ["Exp-14（1つ抜き）", "(A) 変換なし＋他は1つ抜き", "(C) 一次式を1つ抜き＋他は1つ抜き", "Exp-14（全体で当てはめ）",
         "(B) 一次式を全体で＋他は全体", "参考: 硬さ・なめらかさ＝本人の採点＋他は1つ抜き"]
    L = ["# Exp-18 16品の評価（run_eval.py が生成）", "",
         "Claude の記録。計画は plan.md「採点の後」（計算する前にコミット、51f0849）。評価の仕組み・物性値は Exp-11 のまま。",
         "肉の計算と吸油は2通りで回した。rules.yaml の既定（tau・吸油 off）は変えていない。", ""]
    L += ["## 1. 追加3品の状態と判定（正解のレシピ）", "",
          "| 計算 | 料理 | 判定（状態で止める版） | 判定（時間の版） | 中心の最高℃（状態／時間） | 焼き色 | 細胞壁 | 糊化 | 水分% | 脂質% | ミオグロビン |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, *_ in CONFIGS:
        for k in NEW3 + ["sauteed_chicken"]:
            s, t = res[name]["states"][k], res[name]["timed"].get(k)
            L.append(f"| {name} | {dj.get(k, k)} | {nm(s['answer'])} | {nm(t['answer']) if t else '—'} | {s['T_core_max']:.1f}／{t['T_core_max']:.1f} | {s['maillard']} | "
                     f"{s['cell_wall'] or '—'} | {s['starch_gel'] if s['starch_gel'] is not None else '—'} | {s['water']:.1f} | {s['fat']:.1f} | "
                     f"{s['myoglobin'] if s['myoglobin'] is not None else '—'} |" if t else
                     f"| {name} | {dj.get(k, k)} | {nm(s['answer'])} | — | {s['T_core_max']:.1f} | {s['maillard']} | — | — | {s['water']:.1f} | {s['fat']:.1f} | {s['myoglobin']} |")
    L += ["", "## 2. 硬さ・なめらかさの誤差（MAE、1品抜き）", "",
          "| 計算 | 品数 | 硬さ (A) | 硬さ (C) | 硬さ ベースライン | なめらかさ (A) | なめらかさ (C) | なめらかさ ベースライン | 順位相関 硬さ／なめらかさ（指数） |",
          "|---|---|---|---|---|---|---|---|---|"]
    for name, *_ in CONFIGS:
        for key in ("s13", "s16"):
            S = res[name][key]
            h, sm = S["mae"]["hardness"], S["mae"]["smoothness"]
            L.append(f"| {name} | {S['n']} | {h['A']:.2f} | {h['C']:.2f} | {h['base']:.2f} | {sm['A']:.2f} | {sm['C']:.2f} | {sm['base']:.2f} | "
                     f"{S['rho_index']['hardness']:.2f}／{S['rho_index']['smoothness']:.2f} |")
    L += ["", "## 3. 感じ方の距離で一番近い料理（料理そのものが当たった数）", "",
          "| 計算 | 変換 | 13品 | 16品 | 16品のうち元の13品 | 16品のうち追加3品 |", "|---|---|---|---|---|---|"]
    for name, *_ in CONFIGS:
        e13, e16 = res[name]["ev13"], res[name]["ev16"]
        for v in V:
            hit16 = {k: e16["nearest"][v][k][0][0] == k for k in SIXTEEN}
            L.append(f"| {name} | {v} | {e13['hits'][v]}/13 | **{e16['hits'][v]}/16** | {sum(hit16[k] for k in THIRTEEN)}/13 | {sum(hit16[k] for k in NEW3)}/3 |")
    name = CONFIGS[1][0]
    e16 = res[name]["ev16"]
    L += ["", f"### 品ごと（{name}、16品、1位の料理と距離）", "",
          "| 料理 | " + " | ".join(V[:3]) + " |", "|---|" + "---|" * 3]
    for k in SIXTEEN:
        cells = []
        for v in V[:3]:
            top = e16["nearest"][v][k][0]
            cells.append(("✔ " if top[0] == k else "✘ ") + f"{nm(top[0])} {top[1]:.2f}")
        L.append(f"| {dj.get(k, k)} | " + " | ".join(cells) + " |")
    L += ["", f"### 追加3品の硬さ・なめらかさ（{name}。本人 → (A) / (C) / Exp-14 の1つ抜き）", "", "| 料理 | 組織の型 | 硬さ | なめらかさ |", "|---|---|---|---|"]
    for k in NEW3:
        cells = [f"{labels[k][i]:g} → {e16['prior'][k][i]:.1f} / {e16['pC'][k][i]:.1f} / {e16['p14_loo'][k][i]:.1f}" for i in E11.NEW]
        L.append(f"| {dj.get(k, k)} | {e16['tex'][k]['type']} | " + " | ".join(cells) + " |")

    OUT.mkdir(exist_ok=True)
    (OUT / "eval_output.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    J = {name: {"s13": r["s13"], "s16": r["s16"], "states": r["states"], "timed": r["timed"],
                "nearest16": {v: {k: r["ev16"]["nearest"][v][k][:3] for k in SIXTEEN} for v in V}} for name, r in res.items()}
    (OUT / "eval_output.json").write_text(json.dumps(J, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
