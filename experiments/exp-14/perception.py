"""Exp-14 段2: 物理・化学の状態 → 感じ方（知覚の層）の変換。

    uv run python experiments/exp-14/perception.py

- 13品の正解のレシピ（状態で止める版 DISH_RECIPES）をシミュレータで計算し、完成時の状態と
  本人の採点 data/labels/dish_perception.csv（0〜5）を対応させる。
- 標本が13しかないので、項目ごとに rules.md §7 の候補から状態変数を1〜2個だけ選び、単純なモデルにする。
  **変数とモデルの形は下の SPEC に、状態と採点を突き合わせる前に決めて固定した**（取り替えたら
  SPEC_CHANGES に理由を書く）。
- 評価は1つ抜き交差検証（13品）。項目ごとの平均絶対誤差と順位相関（Spearman）を、
  ベースライン（残り12品の平均を返す）と比べる。
- 全13品で当てはめた変換を perception_model.json に書き出す（ページの JavaScript が読む）。
- 段3: 感じ方の6項目で一番近い料理（本人の採点とのユークリッド距離）を返し、状態の条件による判定と並べる。

変数の値の扱い（SPEC と同時に決めた）:
- その成分が無くて状態変数が None のときは 0 とみなす（肉が無い料理の meat_water_loss、でんぷんが無い料理の
  starch_gel、糖が無い料理の caramel など。「その要因が効いていない」の意味）
- 段階（ordinal）は段階の番号をそのまま数値として使う
- 予測は 0〜5 に切り詰める
"""
from __future__ import annotations

# ----------------------------------------------------------------------
# 変数の選択（2026-09-27、状態と採点を突き合わせる前に決めた）
#
# 注意: 採点の CSV は依頼の時点で読んでいる（どの品が何点かは見た）。状態の値との対応は計算していない。
# 選び方の方針: §7 の候補のうち「13品のなるべく多くで値を持つ変数」を優先する。卵だけ・肉だけの変数は
# 1つ抜きで抜いた品の係数が決まらなくなるため。
SPEC: dict[str, dict] = {
    "hardness": {
        "ja": "硬さ", "model": "linear", "vars": ["water", "meat_water_loss"],
        "why": "water は §7 の候補で唯一13品すべてが値を持つ（水が少ないほど硬い、を想定）。"
               "肉の硬さは水分量だけでは出ないので、むね肉が乾く段階（R-P04）の meat_water_loss を足す",
    },
    "thickness": {
        "ja": "とろみ", "model": "linear", "vars": ["sugar_conc", "starch_gel"],
        "why": "とろみを付ける2つの経路（糖液の濃さ R-C05、でんぷんの糊化 R-S01）。"
               "egg_gel_stage は卵の品にしか値がなく、ゲル（硬さ）ととろみを区別できないので選ばない",
    },
    "smoothness": {
        "ja": "なめらかさ", "model": "category_mean", "vars": ["gel_structure"],
        "why": "§7 の候補3つ（porosity・gel_structure・egg_gel_stage）はどれも卵の品にしか値がない。"
               "gel_structure は撹拌の有無（R-E20）でなめらかさが変わる筋を持つ。値ごとの採点の平均を返す"
               "区分関数（学習側に無い値・卵を含まない品（値なし）も1つの区分として扱い、学習側に無い区分は全体平均）",
    },
    "sweet": {
        "ja": "甘さ", "model": "isotonic", "vars": ["sugar_conc"],
        "why": "甘さは溶けている糖の濃さ（§7 の先頭）。濃さに対して頭打ちになるはずなので線形でなく"
               "単調増加の区分関数（isotonic 回帰、点の間は直線で補間、端は一定）",
    },
    "roasted": {
        "ja": "香ばしさ", "model": "linear", "vars": ["maillard", "caramel"],
        "why": "§7 の候補そのまま（メイラード R-M01 とカラメル化 R-C01 の段階）",
    },
    "warmth": {
        "ja": "温かさ", "model": "linear", "vars": ["T_serve"],
        "why": "§7 の候補そのまま（食べるときの温度＝最後の操作の後の中心温度）",
    },
}
ITEMS = list(SPEC)

# 変数を取り替えた記録（取り替えていなければ空）
SPEC_CHANGES: dict[str, str] = {}

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run import NO_MATCH_BELOW  # noqa: E402
from sim import DISH_RECIPES, PAIRS, THIRTEEN, params, verdict  # noqa: E402

LABELS_PATH = HERE.parent.parent / "data" / "labels" / "dish_perception.csv"
MODEL_PATH = HERE / "perception_model.json"
OUT = HERE / "results"
NONE_CAT = "（値なし）"
BIG_MISS = 2.0  # 1つ抜きの誤差がこれ以上の品・項目を「大きく外れた」とする（結果を見る前に決めた）


def load_labels() -> dict[str, dict[str, float]]:
    with open(LABELS_PATH, encoding="utf-8") as f:
        return {r["dish"]: {k: float(r[k]) for k in ITEMS} for r in csv.DictReader(f)}


def feature(state, var: str):
    """状態変数を数値に。None は 0（成分が無い＝その要因が効いていない）。カテゴリはそのまま返す。"""
    v = state.get(var)
    if v is None:
        return 0.0
    if isinstance(v, bool):
        return float(v)
    if isinstance(v, (int, float)):
        return float(v)
    return v


def category(v) -> str:
    return NONE_CAT if v is None or v == 0.0 else str(v)


def clip(x: float) -> float:
    return min(5.0, max(0.0, x))


# ----------------------------------------------------------------------
# モデル
def _pava(y: list[float], w: list[float]) -> list[float]:
    """単調増加の当てはめ（pool adjacent violators）。"""
    blocks = [[yi, wi, 1] for yi, wi in zip(y, w)]
    i = 0
    while i < len(blocks) - 1:
        if blocks[i][0] > blocks[i + 1][0] + 1e-12:
            a, b = blocks[i], blocks[i + 1]
            wt = a[1] + b[1]
            blocks[i] = [(a[0] * a[1] + b[0] * b[1]) / wt, wt, a[2] + b[2]]
            del blocks[i + 1]
            i = max(i - 1, 0)
        else:
            i += 1
    out = []
    for v, _, n in blocks:
        out += [v] * n
    return out


def fit(item: str, rows: list[dict], ys: list[float]) -> dict:
    sp = SPEC[item]
    kind, vars_ = sp["model"], sp["vars"]
    if kind == "linear":
        X = np.array([[1.0] + [r[v] for v in vars_] for r in rows])
        coef, *_ = np.linalg.lstsq(X, np.array(ys), rcond=None)  # 列が全部 0 なら最小ノルム解（係数 0）
        return {"type": "linear", "vars": vars_, "intercept": float(coef[0]),
                "coef": [float(c) for c in coef[1:]]}
    if kind == "isotonic":
        v = vars_[0]
        pts: dict[float, list[float]] = {}
        for r, y in zip(rows, ys):
            pts.setdefault(r[v], []).append(y)
        xs = sorted(pts)
        fitted = _pava([sum(pts[x]) / len(pts[x]) for x in xs], [len(pts[x]) for x in xs])
        return {"type": "isotonic", "vars": vars_, "x": xs, "y": fitted}
    if kind == "category_mean":
        v = vars_[0]
        groups: dict[str, list[float]] = {}
        for r, y in zip(rows, ys):
            groups.setdefault(category(r[v]), []).append(y)
        return {"type": "category_mean", "vars": vars_,
                "means": {k: sum(g) / len(g) for k, g in groups.items()},
                "counts": {k: len(g) for k, g in groups.items()},
                "fallback": sum(ys) / len(ys)}
    raise ValueError(kind)


def predict(model: dict, row: dict) -> float:
    t = model["type"]
    if t == "linear":
        y = model["intercept"] + sum(c * row[v] for c, v in zip(model["coef"], model["vars"]))
    elif t == "isotonic":
        x, xs, ys = row[model["vars"][0]], model["x"], model["y"]
        if x <= xs[0]:
            y = ys[0]
        elif x >= xs[-1]:
            y = ys[-1]
        else:
            j = next(j for j in range(1, len(xs)) if x <= xs[j])
            y = ys[j - 1] + (ys[j] - ys[j - 1]) * (x - xs[j - 1]) / (xs[j] - xs[j - 1])
    elif t == "category_mean":
        y = model["means"].get(category(row[model["vars"][0]]), model["fallback"])
    else:
        raise ValueError(t)
    return clip(y)


def row_of(state) -> dict:
    vars_ = sorted({v for sp in SPEC.values() for v in sp["vars"]})
    return {v: feature(state, v) for v in vars_}


def perceive(models: dict, state) -> dict[str, float]:
    r = row_of(state)
    return {k: predict(models[k], r) for k in ITEMS}


def nearest(pvec: dict[str, float], labels: dict[str, dict[str, float]], top: int = 3):
    d = [(k, math.sqrt(sum((pvec[i] - lab[i]) ** 2 for i in ITEMS))) for k, lab in labels.items()]
    d.sort(key=lambda t: (t[1], list(labels).index(t[0])))
    return d[:top]


# ----------------------------------------------------------------------
def rankdata(a: list[float]) -> np.ndarray:
    a = np.asarray(a, float)
    order = np.argsort(a, kind="mergesort")
    r = np.empty(len(a))
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and a[order[j + 1]] == a[order[i]]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(x, y) -> float | None:
    rx, ry = rankdata(x), rankdata(y)
    if rx.std() == 0 or ry.std() == 0:
        return None
    return float(np.corrcoef(rx, ry)[0, 1])


def f2(v) -> str:
    return "—" if v is None else f"{v:+.2f}" if isinstance(v, float) and v < 0 else f"{v:.2f}"


def main() -> None:
    labels = load_labels()
    assert sorted(labels) == sorted(THIRTEEN), "採点の品と13品が一致しない"
    dishes = THIRTEEN
    states = {k: DISH_RECIPES[k].run() for k in dishes}
    rows = {k: row_of(states[k]) for k in dishes}
    ja = {k: DISH_RECIPES[k].name for k in dishes}

    # 1つ抜き
    loo: dict[str, dict[str, float]] = {k: {} for k in dishes}
    base: dict[str, dict[str, float]] = {k: {} for k in dishes}
    loo_models: dict[str, dict[str, dict]] = {k: {} for k in dishes}
    for k in dishes:
        train = [d for d in dishes if d != k]
        for item in ITEMS:
            m = fit(item, [rows[d] for d in train], [labels[d][item] for d in train])
            loo_models[k][item] = m
            loo[k][item] = predict(m, rows[k])
            base[k][item] = sum(labels[d][item] for d in train) / len(train)
    full = {item: fit(item, [rows[d] for d in dishes], [labels[d][item] for d in dishes]) for item in ITEMS}
    insample = {k: {i: predict(full[i], rows[k]) for i in ITEMS} for k in dishes}

    metrics = {}
    for item in ITEMS:
        y = [labels[k][item] for k in dishes]
        p = [loo[k][item] for k in dishes]
        b = [base[k][item] for k in dishes]
        q = [insample[k][item] for k in dishes]
        metrics[item] = {
            "mae_loo": float(np.mean(np.abs(np.array(p) - y))),
            "mae_base": float(np.mean(np.abs(np.array(b) - y))),
            "rho_loo": spearman(p, y), "rho_base": spearman(b, y),
            "mae_insample": float(np.mean(np.abs(np.array(q) - y))), "rho_insample": spearman(q, y),
        }
    misses = [(k, item, labels[k][item], loo[k][item]) for k in dishes for item in ITEMS
              if abs(loo[k][item] - labels[k][item]) >= BIG_MISS]

    # 段3: 感じ方で一番近い料理 vs 状態の条件による判定
    cmp_rows = []
    for k in dishes:
        r = DISH_RECIPES[k]
        v = verdict(states[k], NO_MATCH_BELOW)
        pf = perceive(full, states[k])
        pl = {i: loo[k][i] for i in ITEMS}
        cmp_rows.append({"group": "13品の正解のレシピ", "name": r.name, "expected": k,
                         "state": v.answer, "state_top": [(c.dish, round(c.fraction, 3)) for c in v.candidates[:3]],
                         "perc_full": nearest(pf, labels), "perc_loo": nearest(pl, labels),
                         "pvec": pf, "pvec_loo": pl})
    for pi, pair in enumerate(PAIRS, 1):
        for side, r in (("A", pair.a), ("B", pair.b)):
            s = r.run()
            v = verdict(s, NO_MATCH_BELOW)
            pf = perceive(full, s)
            cmp_rows.append({"group": f"組{pi} {side}: {pair.title}", "name": r.name, "expected": r.expected,
                             "state": v.answer, "state_top": [(c.dish, round(c.fraction, 3)) for c in v.candidates[:3]],
                             "perc_full": nearest(pf, labels), "perc_loo": None, "pvec": pf, "pvec_loo": None})

    # ---- 書き出し ----
    model_json = {
        "about": "Exp-14 段2: 状態 → 感じ方（0〜5）。perception.py が生成。全13品（状態で止める版の正解のレシピ）で当てはめた。",
        "labels_source": "data/labels/dish_perception.csv",
        "none_as_zero": True, "none_category": NONE_CAT, "clip": [0, 5],
        "items": {i: {"ja": SPEC[i]["ja"], "why": SPEC[i]["why"], **full[i]} for i in ITEMS},
        "spec_changes": SPEC_CHANGES,
        "labels": labels,
        "dish_ja": {k: d["ja"] for k, d in params.dishes().items() if k in dishes},
        "cv": metrics,
    }
    MODEL_PATH.write_text(json.dumps(model_json, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    J = {"metrics": metrics, "rows": rows, "labels": labels, "loo": loo, "baseline": base, "insample": insample,
         "misses": misses, "compare": cmp_rows, "spec": SPEC, "spec_changes": SPEC_CHANGES}
    (OUT / "perception_output.json").write_text(json.dumps(J, ensure_ascii=False, indent=1, default=str) + "\n",
                                                encoding="utf-8")

    L = ["# Exp-14 段2 実行結果（perception.py が生成）", "",
         "13品の正解のレシピ（状態で止める版）の完成時の状態 → 本人の採点（0〜5）。変数とモデルの形は `perception.py` の `SPEC`（突き合わせる前に固定、f62715f）。",
         f"変数を取り替えた記録: {'なし' if not SPEC_CHANGES else SPEC_CHANGES}", "",
         "## 1. 1つ抜き交差検証（13品）", "",
         "ベースライン = 残り12品の採点の平均を返す。ベースラインの順位相関は、抜いた品の採点が高いほど平均が下がるので作りのうえで負になる（参考）。", "",
         "| 項目 | 変数 | モデル | MAE（1つ抜き） | MAE（ベースライン） | 順位相関（1つ抜き） | 順位相関（ベースライン） | 参考: 全13品で当てはめた MAE / 順位相関 |",
         "|---|---|---|---|---|---|---|---|"]
    for i in ITEMS:
        m = metrics[i]
        L.append(f"| {SPEC[i]['ja']} | {', '.join(SPEC[i]['vars'])} | {SPEC[i]['model']} | **{m['mae_loo']:.2f}** | {m['mae_base']:.2f} | "
                 f"{f2(m['rho_loo'])} | {f2(m['rho_base'])} | {m['mae_insample']:.2f} / {f2(m['rho_insample'])} |")
    mean_loo = np.mean([metrics[i]["mae_loo"] for i in ITEMS])
    mean_base = np.mean([metrics[i]["mae_base"] for i in ITEMS])
    L += ["", f"6項目の平均: 1つ抜き {mean_loo:.2f} / ベースライン {mean_base:.2f}", "",
          "## 2. 状態変数の値と採点（13品）", "",
          "| 料理 | " + " | ".join(sorted(rows[dishes[0]])) + " | " + " | ".join(SPEC[i]["ja"] for i in ITEMS) + " |",
          "|---|" + "---|" * (len(rows[dishes[0]]) + len(ITEMS))]
    for k in dishes:
        vals = [f"{v:.2f}" if isinstance(v, float) else str(v) for v in (rows[k][c] for c in sorted(rows[k]))]
        L.append(f"| {ja[k]} | " + " | ".join(vals) + " | " +
                 " | ".join(f"{labels[k][i]:g}→{loo[k][i]:.1f}" for i in ITEMS) + " |")
    L += ["", "感じ方の列は「本人の採点→1つ抜きの予測」。", "",
          f"## 3. 大きく外れた品・項目（1つ抜きの誤差 ≧ {BIG_MISS}）", "",
          "| 料理 | 項目 | 本人の採点 | 予測（1つ抜き） | 誤差 |", "|---|---|---|---|---|"]
    for k, i, y, p in sorted(misses, key=lambda t: (ITEMS.index(t[1]), -abs(t[3] - t[2]))):
        L.append(f"| {ja[k]} | {SPEC[i]['ja']} | {y:g} | {p:.2f} | {p - y:+.2f} |")
    L += ["", "## 4. 全13品で当てはめた変換（perception_model.json）", ""]
    for i in ITEMS:
        m = full[i]
        if m["type"] == "linear":
            L.append(f"- **{SPEC[i]['ja']}** = {m['intercept']:.3f} " +
                     " ".join(f"{c:+.4f}×{v}" for c, v in zip(m["coef"], m["vars"])) + "（0〜5 に切り詰め）")
        elif m["type"] == "isotonic":
            L.append(f"- **{SPEC[i]['ja']}**: {m['vars'][0]} の単調な区分関数 " +
                     ", ".join(f"({x:.2f}→{y:.2f})" for x, y in zip(m["x"], m["y"])))
        else:
            L.append(f"- **{SPEC[i]['ja']}**: {m['vars'][0]} の区分ごとの平均 " +
                     ", ".join(f"{c}={v:.2f}（{m['counts'][c]}品）" for c, v in m["means"].items()) +
                     f"、学習に無い区分は {m['fallback']:.2f}")
    dj = {k: d["ja"] for k, d in params.dishes().items()}

    def nm(k):
        return "該当なし" if k is None else dj.get(k, k)

    L += ["", "## 5. 一番近い料理: 状態の条件による判定 vs 感じ方の距離", "",
          f"状態の条件 = 満たした条件の割合（下限 {NO_MATCH_BELOW} 未満は該当なし）。感じ方の距離 = 計算した感じ方6項目と本人の採点のユークリッド距離が最小の料理（該当なしは設けていない）。",
          "13品の行は、全13品で当てはめた変換（自分の採点を学習に含む）と、1つ抜きの変換（自分の採点を含まない）の両方。組の行は全13品で当てはめた変換。", "",
          "| 入力 | 期待 | 状態の条件（1位） | 感じ方の距離（1位、距離） | 一致 | 感じ方 2位・3位 | 1つ抜きの変換で（1位、距離） | 一致 |",
          "|---|---|---|---|---|---|---|---|"]
    agree_full = agree_loo = n_loo = 0
    for r in cmp_rows:
        pf = r["perc_full"]
        a1 = r["state"] == pf[0][0]
        agree_full += a1
        loo_cell, a2c = "—", "—"
        if r["perc_loo"]:
            n_loo += 1
            a2 = r["state"] == r["perc_loo"][0][0]
            agree_loo += a2
            loo_cell = f"{nm(r['perc_loo'][0][0])} {r['perc_loo'][0][1]:.2f}"
            a2c = "✔" if a2 else "✘"
        st = nm(r["state"]) + (f" {r['state_top'][0][1]:.2f}" if r["state_top"] else "")
        if r["state"] is None and r["state_top"]:
            st += f"（1位 {nm(r['state_top'][0][0])}）"
        L.append(f"| {r['group']}: {r['name']} | {nm(r['expected'])} | {st} | {nm(pf[0][0])} {pf[0][1]:.2f} | "
                 f"{'✔' if a1 else '✘'} | {', '.join(f'{nm(k)} {d:.2f}' for k, d in pf[1:])} | {loo_cell} | {a2c} |")
    L += ["", f"一致: 全体で当てはめた変換 {agree_full}/{len(cmp_rows)}（うち13品 "
          f"{sum(r['state'] == r['perc_full'][0][0] for r in cmp_rows[:13])}/13）、1つ抜きの変換（13品）{agree_loo}/{n_loo}", ""]
    (OUT / "perception_output.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
