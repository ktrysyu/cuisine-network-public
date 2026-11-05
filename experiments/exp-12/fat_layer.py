"""Exp-12（CLA-130）: 油分の層を共起・味・香りの層と比べる（Exp-10 と同じ比べ方）。

    uv run python experiments/exp-12/fat_layer.py

計画は plan.md の「2026-10-22 夜: 油分の層」（計算する前にコミット）。結果は results/fat_layer.md・fat_layer.json。
"""
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "results"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


E10 = load_module("exp10_run", ROOT / "experiments" / "exp-10" / "run.py")


def main() -> None:
    from scipy.stats import spearmanr
    from scipy.spatial.distance import pdist

    fat = {r["ingredient"]: r for r in csv.DictReader((ROOT / "data" / "labels" / "fat_content.csv").open(encoding="utf-8"))}
    taste = {r["ingredient"]: r for r in csv.DictReader(E10.TASTE_PATH.open(encoding="utf-8"))}
    mapping = list(csv.DictReader(E10.MAP_PATH.open(encoding="utf-8")))
    amap = {r["ingredient"]: r["aroma_source_name"] for r in mapping if r["method"] != "none"}
    _, comp_all = E10.load_ahn()
    comp = {k: v for k, v in comp_all.items() if k != "farnesol"}
    log = {}
    recipes = E10.B.load_recipes(log)
    wv = E10.B.load_vectors(recipes, log)
    W0 = E10.unit(wv.vectors).astype(np.float64)
    vocab = list(wv.index_to_key)
    P, _, _ = E10.ppmi_matrix(recipes, vocab)
    vi = {t: k for k, t in enumerate(vocab)}

    def fat_ok(t):
        r = fat.get(t)
        return r is not None and r["fat_g_per_100g"] not in ("", None) and r["match"] != "対応なし"

    T = {t: np.array([float(taste[t][a]) for a in E10.AXES]) for t in taste}
    items = [t for t in taste if fat_ok(t) and T[t].any() and t in amap and t in wv.key_to_index]
    n = len(items)
    iu = np.triu_indices(n, 1)
    F = np.array([float(fat[t]["fat_g_per_100g"]) for t in items])
    s_fat_lin = -pdist(F[:, None])
    s_fat_log = -pdist(np.log10(F + 1)[:, None])
    Tm = np.array([T[t] for t in items])
    Tu = E10.unit(Tm)
    s_taste = (Tu @ Tu.T)[iu]
    src = [amap[t] for t in items]
    uniq = sorted(set(src))
    _, _, cos_u, _ = E10.aroma_matrices(uniq, comp)
    si = np.array([uniq.index(x) for x in src])
    s_aroma = cos_u[si[iu[0]], si[iu[1]]]
    wi = np.array([wv.key_to_index[t] for t in items])
    s_w2v = (W0[wi] @ W0[wi].T)[iu]
    pi = np.array([vi[t] for t in items])
    pa, pb = pi[iu[0]], pi[iu[1]]
    s_ppmi = P[pa, pb]
    s_ctx = E10.ctx_cos(P, pa, pb)
    s_sub = s_ctx / (1 + s_ppmi)
    canon = np.array([taste[t]["canonical"] for t in items])
    same_c = canon[iu[0]] == canon[iu[1]]
    same_s = si[iu[0]] == si[iu[1]]
    masks = {"全ペア": np.ones(len(s_fat_lin), bool), "同じ canonical を除く": ~same_c, "さらに香りの対応先が同じペアも除く": ~same_c & ~same_s}
    others = {"共起（word2vec cos）": s_w2v, "補い合う（PPMI）": s_ppmi, "代わりに使える（sub）": s_sub, "味（6 軸 cos）": s_taste, "香り（化合物 cos）": s_aroma}
    fats = {"油分（−|差|）": s_fat_lin, "油分（−|log の差|）": s_fat_log}
    res = {mk: {f"{fk} × {ok}": float(spearmanr(fv[M], ov[M]).statistic) for fk, fv in fats.items() for ok, ov in others.items()} for mk, M in masks.items()}
    res_ref = {mk: {"味 × 香り（参考、Exp-10 と同じ）": float(spearmanr(s_taste[M], s_aroma[M]).statistic),
                    "共起 × 味（参考）": float(spearmanr(s_w2v[M], s_taste[M]).statistic)} for mk, M in masks.items()}
    # 油分が近いのにほかの層で遠い例（参考）
    M = masks["さらに香りの対応先が同じペアも除く"]
    idx = np.where(M)[0]
    rk = lambda v: (np.argsort(np.argsort(v[idx])) / len(idx))  # noqa: E731
    gap = rk(s_fat_log) - rk(s_w2v)
    top = idx[np.argsort(-gap)[:10]]
    ex = [(items[iu[0][q]], items[iu[1][q]], float(F[iu[0][q]]), float(F[iu[1][q]]), float(s_w2v[q])) for q in top]

    OUT.mkdir(exist_ok=True)
    L = ["# Exp-12 油分の層（CLA-130）実行結果（fat_layer.py が生成）", "",
         "Claude の記録。計画は plan.md「2026-10-22 夜: 油分の層」（計算の前にコミット）。比べ方は Exp-10 と同じ。", "",
         f"対象: 脂質量・味（全軸 0 でない）・香りの対応・word2vec の語彙がそろう {n} 食材、ペア数 " + "・".join(f"{k} {int(m.sum())}" for k, m in masks.items()), "",
         "## 順位相関（Spearman ρ）", "", "| 比較 | " + " | ".join(masks) + " |", "|---|" + "---|" * len(masks)]
    for key in res["全ペア"]:
        L.append(f"| {key} | " + " | ".join(f"{res[mk][key]:+.3f}" for mk in masks) + " |")
    for key in res_ref["全ペア"]:
        L.append(f"| {key} | " + " | ".join(f"{res_ref[mk][key]:+.3f}" for mk in masks) + " |")
    L += ["", "## 油分は近いが共起では遠い組み合わせ（参考、上位 10）", "", "| 食材 | 食材 | 脂質量 | 脂質量 | 共起 cos |", "|---|---|---|---|---|"]
    L += [f"| {a} | {b} | {fa:g} | {fb:g} | {w:.2f} |" for a, b, fa, fb, w in ex]
    (OUT / "fat_layer.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (OUT / "fat_layer.json").write_text(json.dumps({"n": n, "spearman": res, "reference": res_ref, "examples": ex}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
