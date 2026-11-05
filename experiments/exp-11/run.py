"""Exp-11 食感の層の作り直し: Exp-14 の状態 → 組織の型と物性値 → 硬さ・なめらかさ。

    uv run python experiments/exp-11/run.py

- 物性値と出典は texture_rules.yaml（plan.md 2026-09-29 の節で、実行前に決めた）
- 他の4項目（とろみ・甘さ・香ばしさ・温かさ）は Exp-14 の perception.py の変換をそのまま使う
- 結果は results/texture_output.md・texture_output.json
"""
from __future__ import annotations

import copy
import json
import math
import sys
from pathlib import Path

import numpy as np
import yaml

HERE = Path(__file__).resolve().parent
EXP14 = HERE.parent / "exp-14"
sys.path.insert(0, str(EXP14))  # exp-14 の run・sim・perception を先に見つける

import perception as P14  # noqa: E402
from run import NO_MATCH_BELOW  # noqa: E402  (exp-14/run.py)
from sim import DISH_RECIPES, PAIRS, THIRTEEN, params, verdict  # noqa: E402
from sim.state import EGG_BEATEN, GEL_CURD, GEL_SHELL  # noqa: E402

RULES = yaml.safe_load((HERE / "texture_rules.yaml").read_text(encoding="utf-8"))
OUT = HERE / "results"
ITEMS = P14.ITEMS
NEW = ("hardness", "smoothness")
OTHERS = [i for i in ITEMS if i not in NEW]


def V(R, group, key):
    return R[group][key]["value"]


def conc_exponent(R) -> float:
    return math.log(V(R, "egg", "E_whole_ref") / V(R, "egg", "E_whole_60pct")) / math.log(1 / 0.6)


# ----------------------------------------------------------------------
# 状態 → 組織の型と物性値
def texture(s, R) -> dict:
    """組織の型・E（Pa、弾性のもの）・σ_c（壊すのに要る応力 Pa）・d（口の中で感じる要素の大きさ µm）。"""
    fs = V(R, "bite", "fracture_strain")
    m = s.masses

    def elastic(kind, E, d, why):
        return {"type": kind, "E": E, "sigma": E * fs, "d": d, "why": why}

    # 上ほど優先（plan.md の表の下の行＝組織が大きいもの）
    if "flour" in m and (s.co2 or 0) >= 2 and (s.starch_gel or 0) >= 0.9:
        E = V(R, "baked", "E_solid") * V(R, "baked", "rel_density") ** V(R, "baked", "density_exponent")
        return elastic("焼いた生地", E, V(R, "baked", "pore_d"), "Gibson–Ashby")
    if "rice" in m and (s.starch_gel or 0) >= 0.9:
        return elastic("炊いた米粒", V(R, "rice", "E_cooked"), V(R, "rice", "grain_d"), "米粒")
    if s.cell_wall is not None:
        E = {"生": V(R, "vegetable", "E_raw"), "硬化（PME）": V(R, "vegetable", "E_raw"),
             "軟化": V(R, "vegetable", "E_soft"), "崩壊（煮崩れ）": V(R, "vegetable", "E_collapse")}[s.cell_wall]
        return elastic("野菜の組織", E, V(R, "vegetable", "cell_d"), f"cell_wall={s.cell_wall}")
    if (s.meat_myosin or 0) >= 1 or (s.meat_actin or 0) >= 1:
        return elastic("加熱した肉", V(R, "meat", "E_cooked"), V(R, "meat", "fiber_d"), "ミオシン・アクチン変性")
    if (s.foam_stage or 0) >= 2 or s.cream_network is not None:
        sig = V(R, "whipped", "G") * V(R, "whipped", "yield_strain")
        return {"type": "ホイップ", "E": 3 * V(R, "whipped", "G"), "sigma": sig,
                "d": V(R, "whipped", "bubble_d"), "why": "降伏応力 = G × 降伏ひずみ"}
    if s.gelatin_state == "ゲル":
        c = s.gelatin_conc or 0.0
        E = V(R, "gelatin", "E_ref") * (c / V(R, "gelatin", "c_ref")) ** V(R, "gelatin", "conc_exponent")
        return elastic("ゼラチンのゲル", E, 0.0, f"濃度 {c:.2f}%")
    if s.egg_white_stage is not None:
        n = conc_exponent(R)
        yf = V(R, "egg", "yolk_fraction")
        py, pw = V(R, "egg", "protein_yolk"), V(R, "egg", "protein_white")
        wf2 = V(R, "egg", "white_frac_stage2")
        if s.egg_form == EGG_BEATEN:
            stage = s.egg_gel_stage or 0
            if s.gel_structure == GEL_SHELL and V(R, "egg", "outer_layer_decides"):
                stage = s.egg_gel_stage_surface or 0
            f = {3: 1.0, 4: 1.0, 2: (yf * py + (1 - yf) * pw * wf2) / (yf * py + (1 - yf) * pw)}.get(stage, 0.0)
            c = (s.egg_dilution or 100.0) / 100.0
            if f == 0.0:
                return {"type": "卵液（固まっていない）", "E": 0.0, "sigma": 0.0, "d": 0.0, "why": f"段階 {stage}"}
            E = V(R, "egg", "E_whole_ref") * (c * f) ** n
            d = V(R, "egg", "curd_size") if s.gel_structure == GEL_CURD else 0.0
            return elastic("卵のゲル（溶き卵）", E, d, f"段階 {stage}・卵の割合 {c:.2f}・固まった割合 {f:.2f}")
        # 殻付き・割った卵: 外側の卵白で決める
        st = s.egg_white_stage or 0
        f = {3: 1.0, 2: wf2}.get(st, 0.0)
        if f == 0.0:
            return {"type": "卵（固まっていない）", "E": 0.0, "sigma": 0.0, "d": 0.0, "why": f"卵白 {st}"}
        return elastic("卵（卵白が外側）", V(R, "egg", "E_white_ref") * f ** n, 0.0, f"卵白 {st}・固まった割合 {f:.2f}")
    if (s.starch_gel or 0) >= 0.5:
        return {"type": "でんぷんの糊", "E": 0.0, "sigma": 0.0, "d": V(R, "starch_paste", "granule_d"), "why": "ゾル"}
    return {"type": "液体", "E": 0.0, "sigma": 0.0, "d": 0.0, "why": ""}


def indices(t: dict, R) -> dict:
    sig = max(t["sigma"], V(R, "bite", "sigma_floor"))
    lim = V(R, "bite", "tongue_crush_limit")
    dth = V(R, "bite", "d_soft_threshold") if sig <= lim else V(R, "bite", "d_hard_threshold")
    size = max(0.0, math.log10(t["d"] / dth)) if t["d"] > 0 else 0.0
    chew = max(0.0, math.log10(sig / lim))
    return {"log_sigma": math.log10(sig), "rough": size + chew, "rough_size": size, "rough_chew": chew}


def prior(ix: dict, R) -> dict[str, float]:
    k = V(R, "prior_scale", "per_decade")
    z = math.log10(V(R, "prior_scale", "hard_zero_kPa") * 1000)
    return {"hardness": P14.clip(k * (ix["log_sigma"] - z)), "smoothness": P14.clip(5 - k * ix["rough"])}


def lin_fit(x: list[float], y: list[float]) -> tuple[float, float]:
    X = np.array([[1.0, v] for v in x])
    c, *_ = np.linalg.lstsq(X, np.array(y), rcond=None)
    return float(c[0]), float(c[1])


XVAR = {"hardness": "log_sigma", "smoothness": "rough"}


# ----------------------------------------------------------------------
def evaluate(R, labels, states, rows14, verbose=True, dishes=None) -> dict:
    """dishes を渡さなければ 13品（Exp-18 で 16品を渡すために引数にした。13品の結果は変わらない）。"""
    dishes = list(dishes) if dishes is not None else THIRTEEN
    tex = {k: texture(states[k], R) for k in dishes}
    ix = {k: indices(tex[k], R) for k in dishes}
    pri = {k: prior(ix[k], R) for k in dishes}

    # Exp-14 の変換（全体・1つ抜き）
    full14 = {i: P14.fit(i, [rows14[d] for d in dishes], [labels[d][i] for d in dishes]) for i in ITEMS}
    p14_full = {k: {i: P14.predict(full14[i], rows14[k]) for i in ITEMS} for k in dishes}
    p14_loo, base = {k: {} for k in dishes}, {k: {} for k in dishes}
    for k in dishes:
        tr = [d for d in dishes if d != k]
        for i in ITEMS:
            p14_loo[k][i] = P14.predict(P14.fit(i, [rows14[d] for d in tr], [labels[d][i] for d in tr]), rows14[k])
            base[k][i] = sum(labels[d][i] for d in tr) / len(tr)

    # (B) 全体で当てはめ・(C) 1つ抜き
    newfit_full = {i: lin_fit([ix[d][XVAR[i]] for d in dishes], [labels[d][i] for d in dishes]) for i in NEW}
    pB = {k: {i: P14.clip(newfit_full[i][0] + newfit_full[i][1] * ix[k][XVAR[i]]) for i in NEW} for k in dishes}
    pC = {}
    for k in dishes:
        tr = [d for d in dishes if d != k]
        pC[k] = {}
        for i in NEW:
            a, b = lin_fit([ix[d][XVAR[i]] for d in tr], [labels[d][i] for d in tr])
            pC[k][i] = P14.clip(a + b * ix[k][XVAR[i]])

    def mae(pred, i):
        return float(np.mean([abs(pred[k][i] - labels[k][i]) for k in dishes]))

    metrics = {}
    for i in NEW:
        y = [labels[k][i] for k in dishes]
        x = [ix[k][XVAR[i]] for k in dishes]
        rho = P14.spearman(x, y)
        metrics[i] = {
            "rho_index": (None if rho is None else (rho if i == "hardness" else -rho)),
            "mae_A": mae(pri, i), "mae_B": mae(pB, i), "mae_C": mae(pC, i),
            "mae_14_loo": mae(p14_loo, i), "mae_14_full": mae(p14_full, i), "mae_base": mae(base, i),
            "rho_A": P14.spearman([pri[k][i] for k in dishes], y),
            "rho_C": P14.spearman([pC[k][i] for k in dishes], y),
            "rho_14_loo": P14.spearman([p14_loo[k][i] for k in dishes], y),
            "coef_full": newfit_full[i],
        }

    def combo(new, others):
        return {k: {**{i: others[k][i] for i in OTHERS}, **{i: new[k][i] for i in NEW}} for k in dishes}

    variants = {
        "Exp-14（全体で当てはめ）": p14_full,
        "Exp-14（1つ抜き）": p14_loo,
        "(A) 変換なし＋他は全体": combo(pri, p14_full),
        "(A) 変換なし＋他は1つ抜き": combo(pri, p14_loo),
        "(B) 一次式を全体で＋他は全体": combo(pB, p14_full),
        "(C) 一次式を1つ抜き＋他は1つ抜き": combo(pC, p14_loo),
        # 参考（モデルではない）: 硬さ・なめらかさが完全に当たったとき、他の4項目が1つ抜きのままだと何品か
        "参考: 硬さ・なめらかさ＝本人の採点＋他は1つ抜き": combo({k: labels[k] for k in dishes}, p14_loo),
    }
    nearest = {name: {k: P14.nearest(v[k], labels) for k in dishes} for name, v in variants.items()}
    hits = {name: sum(nearest[name][k][0][0] == k for k in dishes) for name in variants}
    # Exp-14 と同じ数え方: 状態の条件による判定の答えと一致した数（炒め玉ねぎは状態の判定が「該当なし」）
    state_ans = {k: verdict(states[k], NO_MATCH_BELOW).answer for k in dishes}
    hits_v = {name: sum(nearest[name][k][0][0] == state_ans[k] for k in dishes) for name in variants}
    return {"hits_v": hits_v, "state_ans": state_ans, "tex": tex, "ix": ix, "prior": pri, "pB": pB, "pC": pC, "p14_full": p14_full, "p14_loo": p14_loo,
            "base": base, "metrics": metrics, "nearest": nearest, "hits": hits, "variants": list(variants)}


KARI = [("bite", "fracture_strain"), ("bite", "sigma_floor"), ("egg", "curd_size"),
        ("meat", "fiber_d"), ("vegetable", "cell_d"), ("rice", "E_cooked"), ("rice", "grain_d"),
        ("baked", "rel_density"), ("baked", "pore_d"), ("prior_scale", "per_decade"), ("prior_scale", "hard_zero_kPa")]


def main() -> None:
    labels = P14.load_labels()
    dishes = THIRTEEN
    states = {k: DISH_RECIPES[k].run() for k in dishes}
    rows14 = {k: P14.row_of(states[k]) for k in dishes}
    ja = {k: DISH_RECIPES[k].name for k in dishes}
    dj = {k: d["ja"] for k, d in params.dishes().items()}
    ev = evaluate(RULES, labels, states, rows14)
    n = conc_exponent(RULES)

    # 感度（仮の値を ×0.5・×2）
    sens = []
    for g, key in KARI:
        for f in (0.5, 2.0):
            R = copy.deepcopy(RULES)
            R[g][key]["value"] = R[g][key]["value"] * f
            e = evaluate(R, labels, states, rows14)
            sens.append({"param": f"{g}.{key}", "factor": f,
                         "rho_h": e["metrics"]["hardness"]["rho_index"], "rho_s": e["metrics"]["smoothness"]["rho_index"],
                         "mae_C_h": e["metrics"]["hardness"]["mae_C"], "mae_C_s": e["metrics"]["smoothness"]["mae_C"],
                         "hits_A_loo": e["hits"]["(A) 変換なし＋他は1つ抜き"], "hits_C": e["hits"]["(C) 一次式を1つ抜き＋他は1つ抜き"],
                         "hits_B": e["hits"]["(B) 一次式を全体で＋他は全体"]})

    # 組（Exp-14 の7組）: (B) の変換で
    pair_rows = []
    fullB = ev["metrics"]
    full14 = {i: P14.fit(i, [rows14[d] for d in dishes], [labels[d][i] for d in dishes]) for i in ITEMS}
    for pi, pair in enumerate(PAIRS, 1):
        for side, r in (("A", pair.a), ("B", pair.b)):
            s = r.run()
            t = texture(s, RULES)
            x = indices(t, RULES)
            v = {i: P14.predict(full14[i], P14.row_of(s)) for i in OTHERS}
            for i in NEW:
                a, b = fullB[i]["coef_full"]
                v[i] = P14.clip(a + b * x[XVAR[i]])
            v14 = {i: P14.predict(full14[i], P14.row_of(s)) for i in ITEMS}
            pair_rows.append({"pair": f"組{pi}{side}", "name": r.name, "expected": r.expected, "type": t["type"],
                              "near14": P14.nearest(v14, labels)[0], "nearB": P14.nearest(v, labels)[0]})

    def nm(k):
        return "該当なし" if k is None else dj.get(k, k)

    def f2(v):
        return "—" if v is None else f"{v:+.2f}" if v < 0 else f"{v:.2f}"

    M = ev["metrics"]
    L = ["# Exp-11 食感の層の作り直し 実行結果（run.py が生成）", "",
         "Claude の記録。仮説・物性値・評価の方法は plan.md（2026-09-29 の節）と texture_rules.yaml に、実行前に決めてコミットした（aece759）。",
         "状態は Exp-14 の sim の今の版（修正 B・Q6・余熱の後。本人判断 2026-09-29 は実装済みで本体は変わっていない）。",
         f"卵ゲルの濃度の指数（npj 2024 の 100%・60% から）: {n:.3f}", "",
         "## 1. 状態 → 組織の型と物性値（13品）", "",
         "| 料理 | 組織の型 | E (kPa) | σ_c (kPa) | d (µm) | log10 σ_c | 粗さ（大きさ＋噛む） | 根拠 | 本人の硬さ | 本人のなめらかさ |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for k in dishes:
        t, x = ev["tex"][k], ev["ix"][k]
        L.append(f"| {ja[k]} | {t['type']} | {t['E'] / 1000:.3g} | {t['sigma'] / 1000:.3g} | {t['d']:g} | {x['log_sigma']:.2f} | "
                 f"{x['rough']:.2f}（{x['rough_size']:.2f}＋{x['rough_chew']:.2f}） | {t['why']} | {labels[k]['hardness']:g} | {labels[k]['smoothness']:g} |")
    L += ["", "## 2. 硬さ・なめらかさの当たり（13品）", "",
          "順位相関（指数）は物性の指数そのものと本人の採点の順位相関で、当てはめを一切していない（なめらかさは粗さの符号を反転）。",
          "(A) 変換なし＝先に決めた目盛り、(B) 一次式を13品で当てはめ（参考）、(C) 同じ一次式の1つ抜き。ベースライン＝残り12品の平均。", "",
          "| 項目 | 順位相関（指数） | MAE (A) | MAE (C) | MAE Exp-14（1つ抜き） | MAE ベースライン | 順位相関 (A) | 順位相関 (C) | 順位相関 Exp-14（1つ抜き） | 参考 MAE (B) / Exp-14（全体） |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for i in NEW:
        m = M[i]
        L.append(f"| {P14.SPEC[i]['ja']} | {f2(m['rho_index'])} | **{m['mae_A']:.2f}** | **{m['mae_C']:.2f}** | {m['mae_14_loo']:.2f} | {m['mae_base']:.2f} | "
                 f"{f2(m['rho_A'])} | {f2(m['rho_C'])} | {f2(m['rho_14_loo'])} | {m['mae_B']:.2f} / {m['mae_14_full']:.2f} |")
    for i in NEW:
        a, b = M[i]["coef_full"]
        L.append(f"\n(B) の {P14.SPEC[i]['ja']} = {a:.3f} {b:+.3f} × {XVAR[i]}")
    L += ["", "### 品ごとの予測（本人 → A / C / Exp-14 の1つ抜き）", "",
          "| 料理 | 硬さ | なめらかさ |", "|---|---|---|"]
    for k in dishes:
        cells = []
        for i in NEW:
            cells.append(f"{labels[k][i]:g} → {ev['prior'][k][i]:.1f} / {ev['pC'][k][i]:.1f} / {ev['p14_loo'][k][i]:.1f}")
        L.append(f"| {ja[k]} | " + " | ".join(cells) + " |")

    L += ["", "## 3. 感じ方の距離で一番近い料理（13品）", "",
          "他の4項目（とろみ・甘さ・香ばしさ・温かさ）は Exp-14 の変換のまま。", "",
          "正解の数え方は2通り。「料理そのもの」= 一番近い料理が入力した料理と同じ。「状態の判定と一致」= Exp-14 の結果表・研究ノートの 6/13 と同じ数え方で、状態の条件による判定の答えと同じ（炒め玉ねぎは状態の判定が該当なしなので、感じ方で当たっても数えない）。", "",
          "| 変換 | 料理そのもの | 状態の判定と一致（Exp-14 の数え方） |", "|---|---|---|"]
    for name in ev["variants"]:
        L.append(f"| {name} | **{ev['hits'][name]}/13** | {ev['hits_v'][name]}/13 |")
    L += ["", "| 料理 | " + " | ".join(ev["variants"]) + " |", "|---|" + "---|" * len(ev["variants"])]
    for k in dishes:
        cells = []
        for name in ev["variants"]:
            top = ev["nearest"][name][k][0]
            cells.append(("✔ " if top[0] == k else "✘ ") + f"{nm(top[0])} {top[1]:.2f}")
        L.append(f"| {ja[k]} | " + " | ".join(cells) + " |")

    ok_h = M["hardness"]["mae_C"] < M["hardness"]["mae_base"]
    ok_s = M["smoothness"]["mae_C"] < M["smoothness"]["mae_base"]
    ok_h_a = M["hardness"]["mae_A"] < M["hardness"]["mae_base"]
    ok_s_a = M["smoothness"]["mae_A"] < M["smoothness"]["mae_base"]
    before = ev["hits"]["Exp-14（1つ抜き）"]
    before_v = ev["hits_v"]["Exp-14（1つ抜き）"]
    L += ["", "## 4. 先に決めた成功の条件", "",
          f"- 硬さの1つ抜きの MAE がベースラインを下回る: (C) {'はい' if ok_h else 'いいえ'}（{M['hardness']['mae_C']:.2f} vs {M['hardness']['mae_base']:.2f}）、(A) {'はい' if ok_h_a else 'いいえ'}（{M['hardness']['mae_A']:.2f}）",
          f"- なめらかさの1つ抜きの MAE がベースラインを下回る: (C) {'はい' if ok_s else 'いいえ'}（{M['smoothness']['mae_C']:.2f} vs {M['smoothness']['mae_base']:.2f}）、(A) {'はい' if ok_s_a else 'いいえ'}（{M['smoothness']['mae_A']:.2f}）",
          f"- 感じ方の距離（1つ抜き）が Exp-14 より増える: 料理そのもの Exp-14 {before}/13 → (C) {ev['hits']['(C) 一次式を1つ抜き＋他は1つ抜き']}/13・(A) {ev['hits']['(A) 変換なし＋他は1つ抜き']}/13。"
          f"状態の判定と一致 Exp-14 {before_v}/13 → (C) {ev['hits_v']['(C) 一次式を1つ抜き＋他は1つ抜き']}/13・(A) {ev['hits_v']['(A) 変換なし＋他は1つ抜き']}/13", ""]

    L += ["## 5. 仮の値の感度（1つずつ ×0.5・×2）", "",
          "| 仮の値 | 倍率 | 順位相関 硬さ | 順位相関 なめらかさ | MAE (C) 硬さ | MAE (C) なめらかさ | 距離 (A)＋1つ抜き | 距離 (C) | 距離 (B) |",
          "|---|---|---|---|---|---|---|---|---|"]
    L.append(f"| （採用値） | 1 | {f2(M['hardness']['rho_index'])} | {f2(M['smoothness']['rho_index'])} | {M['hardness']['mae_C']:.2f} | {M['smoothness']['mae_C']:.2f} | "
             f"{ev['hits']['(A) 変換なし＋他は1つ抜き']} | {ev['hits']['(C) 一次式を1つ抜き＋他は1つ抜き']} | {ev['hits']['(B) 一次式を全体で＋他は全体']} |")
    for r in sens:
        L.append(f"| {r['param']} | ×{r['factor']:g} | {f2(r['rho_h'])} | {f2(r['rho_s'])} | {r['mae_C_h']:.2f} | {r['mae_C_s']:.2f} | "
                 f"{r['hits_A_loo']} | {r['hits_C']} | {r['hits_B']} |")

    L += ["", "## 6. 順番・操作を変えた7組（(B) の変換、他は全体で当てはめ）", "",
          "| 組 | 入力 | 期待 | 組織の型 | Exp-14 の感じ方で一番近い | 作り直し後 |", "|---|---|---|---|---|---|"]
    for r in pair_rows:
        L.append(f"| {r['pair']} | {r['name']} | {nm(r['expected'])} | {r['type']} | {nm(r['near14'][0])} {r['near14'][1]:.2f} | {nm(r['nearB'][0])} {r['nearB'][1]:.2f} |")

    OUT.mkdir(exist_ok=True)
    (OUT / "texture_output.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    J = {"conc_exponent": n, "texture": ev["tex"], "indices": ev["ix"], "prior": ev["prior"], "pB": ev["pB"], "pC": ev["pC"],
         "p14_loo": ev["p14_loo"], "metrics": M, "hits": ev["hits"], "hits_state_verdict": ev["hits_v"], "state_answer": ev["state_ans"],
         "nearest": {name: {k: v[:3] for k, v in d.items()} for name, d in ev["nearest"].items()},
         "sensitivity": sens, "pairs": pair_rows}
    (OUT / "texture_output.json").write_text(json.dumps(J, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
