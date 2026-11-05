"""Exp-02: 味覚スコアと学習空間を比べる。

実行: リポジトリ直下で `uv run python experiments/exp-02/run.py`

入力
- Exp-01 の食材ベクトル（data/processed/exp01_word2vec.kv。無ければ Exp-01 と同じ設定で再生成）
- data/labels/taste_scores.csv（本人確認済み 303 食材。正とする）
- data/labels/taste_scores_draft.csv（Claude の下書き。7 の比較にだけ使う）

手順
1. 食材ベクトル → 6 軸の味覚スコアをリッジ回帰で予測（5-fold CV）。ランダムベクトル・国籍プロファイルと比べる
2. Exp-01b の重心差方向 k=5/10/19 を除いた後のベクトルで同じ予測
3. 食材ベクトル・料理ベクトルの PCA 第1〜10成分と、味覚・国籍の対応
4. 味の方向（リッジ係数 / 上位−下位の平均差）に料理を射影し、国籍の並びと η² を出す
5. mirin − japanese + french を、通常 / 重心差除去 / 味の方向を保存した重心差除去 で比べる
6. 味覚スコアのコサイン類似と空間のコサイン類似の順位相関、一致例・ずれ例
7. 下書きと本人確認版の差（draft_vs_final.md）

Exp-01 / Exp-01b の成果物は読むだけで書き換えない。成果物は results/ に置く。
"""

from __future__ import annotations

import collections
import csv
import hashlib
import importlib.util
import json
import platform
import time
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# 設定
# ---------------------------------------------------------------------------
SEED = 42
AXES = ["sweet", "salty", "sour", "bitter", "umami", "spicy"]
AXES_JA = {"sweet": "甘", "salty": "塩", "sour": "酸", "bitter": "苦", "umami": "旨", "spicy": "辛"}

CV_FOLDS = 5
CV_REPEATS = 5                            # 分割の乱数を変えて繰り返す回数（平均±標準偏差を出す）
RIDGE_ALPHAS = np.logspace(-3, 4, 15)     # RidgeCV（学習 fold 内の GCV で軸ごとに選ぶ）
REMOVE_K = [5, 10, 19]                    # Exp-01b の重心差 SVD の本数
N_PCA = 10
N_RANDOM_SUBSPACES = 10                   # 2 の対照: 同じ本数のランダムな正規直交方向を除いた場合（引き直し回数）

# 4 の平均差方向: 上位 = スコア >= DIFF_HIGH、下位 = スコア 0。上位が DIFF_MIN_N 未満なら閾値を 1 下げる
DIFF_HIGH = 3
DIFF_MIN_N = 5
DISH_MIN_SCORED = 3                       # 料理の味（構成食材スコアの平均）を出す最小の採点済み食材数

# 3 の判定規則（結果を見る前に決めた）: 成分スコアを 6 軸 / 20 国籍プロファイルで線形回帰した
# 自由度調整済み R²（以下 R²_taste, R²_nation）で判定する
VERDICT_MIN = 0.10                        # 両方これ未満なら「どちらも弱い」
VERDICT_RATIO = 2.0                       # 一方が他方の 2 倍以上なら「味寄り」「地域寄り」、それ以外は「両方」

ARITH_TOP_K = 10
ARITH_PRESERVE_K = [5, 19]
SIM_EXAMPLES = 10

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = HERE / "results"
TASTE_PATH = ROOT / "data" / "labels" / "taste_scores.csv"
DRAFT_PATH = ROOT / "data" / "labels" / "taste_scores_draft.csv"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


M1B = load_module("exp01b_methods", ROOT / "experiments" / "exp-01b" / "run_methods.py")
B = M1B.B      # Exp-01b run.py
E1 = M1B.E1    # Exp-01 run.py
unit = E1.unit


# ---------------------------------------------------------------------------
# 読み込み
# ---------------------------------------------------------------------------
def read_scores(path):
    rows = list(csv.DictReader(path.open()))
    return {r["ingredient"]: r for r in rows}, [r["ingredient"] for r in rows]


def nation_profile(recipes, cuisines, ings):
    """P(cuisine | 食材): その食材を含むレシピのうち各国籍の割合（20 次元、和 1）。"""
    cnt = collections.defaultdict(collections.Counter)
    for r in recipes:
        for t in r["ingredients"]:
            cnt[t][r["cuisine"]] += 1
    P = np.array([[cnt[t][c] for c in cuisines] for t in ings], dtype=np.float64)
    return P / P.sum(axis=1, keepdims=True)


# ---------------------------------------------------------------------------
# 1, 2: 予測
# ---------------------------------------------------------------------------
def make_model():
    from sklearn.linear_model import RidgeCV
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    return make_pipeline(StandardScaler(), RidgeCV(alphas=RIDGE_ALPHAS, alpha_per_target=True))


def cv_predict(F, T, groups, grouped, rep):
    from sklearn.model_selection import GroupKFold, KFold

    pred = np.zeros_like(T, dtype=np.float64)
    if grouped:
        splits = GroupKFold(n_splits=CV_FOLDS, shuffle=True, random_state=SEED + rep).split(F, T, groups)
    else:
        splits = KFold(n_splits=CV_FOLDS, shuffle=True, random_state=SEED + rep).split(F)
    for tr, te in splits:
        pred[te] = make_model().fit(F[tr], T[tr]).predict(F[te])
    return pred


def score_pred(T, P):
    from scipy.stats import spearmanr

    r2 = 1 - ((T - P) ** 2).sum(axis=0) / ((T - T.mean(axis=0)) ** 2).sum(axis=0)
    rho = np.array([spearmanr(T[:, j], P[:, j]).statistic for j in range(T.shape[1])])
    return r2, rho


def evaluate_features(F_fn, T, groups):
    """F_fn(rep) -> 特徴行列。反復ごとに分割を変え、KFold と GroupKFold（canonical 単位）の両方で評価。"""
    out = {}
    for grouped in (False, True):
        r2s, rhos = [], []
        for rep in range(CV_REPEATS):
            F = F_fn(rep)
            r2, rho = score_pred(T, cv_predict(F, T, groups, grouped, rep))
            r2s.append(r2)
            rhos.append(rho)
        r2s, rhos = np.array(r2s), np.array(rhos)
        out["group" if grouped else "kfold"] = {
            "r2_mean": r2s.mean(0).tolist(), "r2_std": r2s.std(0).tolist(),
            "rho_mean": rhos.mean(0).tolist(), "rho_std": rhos.std(0).tolist(),
            "r2_axis_avg": float(r2s.mean(1).mean()), "rho_axis_avg": float(rhos.mean(1).mean()),
        }
    return out


# ---------------------------------------------------------------------------
# 3: PCA
# ---------------------------------------------------------------------------
def adj_r2(y, X):
    """y を X（定数項込み）で最小二乗回帰した自由度調整済み R²。"""
    n, p = X.shape
    A = np.hstack([np.ones((n, 1)), X])
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    r2 = 1 - ((y - A @ coef) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return float(1 - (1 - r2) * (n - 1) / (n - p - 1)), float(r2)


def verdict(rt, rn):
    if rt < VERDICT_MIN and rn < VERDICT_MIN:
        return "どちらも弱い"
    if rt >= VERDICT_RATIO * max(rn, 1e-9):
        return "味寄り"
    if rn >= VERDICT_RATIO * max(rt, 1e-9):
        return "地域寄り"
    return "両方"


def corr_cols(z, M):
    zc = (z - z.mean()) / z.std()
    Mc = (M - M.mean(0)) / np.where(M.std(0) == 0, 1, M.std(0))
    return (zc[:, None] * Mc).mean(0)


# ---------------------------------------------------------------------------
# 4: η²
# ---------------------------------------------------------------------------
def eta2(v, labels, cuisines):
    g = v.mean()
    between = sum((labels == c).sum() * (v[labels == c].mean() - g) ** 2 for c in cuisines)
    return float(between / ((v - g) ** 2).sum())


# ---------------------------------------------------------------------------
# 図
# ---------------------------------------------------------------------------
def plot_pca_heatmap(ing_corr, dish_corr, cuisines, ing_verdicts, dish_verdicts, ev_ing, ev_dish):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    INK, MUTED = "#0b0b0b", "#52514e"
    cols = [f"{a}" for a in AXES] + list(cuisines)
    fig, axes = plt.subplots(2, 1, figsize=(13, 10.5), dpi=150)
    vmax = max(np.abs(ing_corr).max(), np.abs(dish_corr).max())
    VERD_EN = {"味寄り": "taste", "地域寄り": "region", "両方": "both", "どちらも弱い": "weak"}
    titles = [
        "(a) ingredient vectors (303 scored ingredients): PCA component vs taste score (left 6) / "
        "P(cuisine | ingredient) (right 20), Pearson r",
        "(b) dish vectors (39,774 recipes): PCA component vs dish taste (mean of scored ingredients, left 6) / "
        "cuisine one-hot (right 20), Pearson r",
    ]
    for ax, C, verd, ev, title in zip(axes, [ing_corr, dish_corr], [ing_verdicts, dish_verdicts],
                                      [ev_ing, ev_dish], titles):
        im = ax.imshow(C, cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
        ax.set_xticks(range(len(cols)))
        ax.set_xticklabels(cols, rotation=60, ha="right", fontsize=8, color=INK)
        ax.set_yticks(range(C.shape[0]))
        ax.set_yticklabels([f"PC{i+1} ({ev[i]*100:.1f}%) [{VERD_EN[verd[i]]}]" for i in range(C.shape[0])],
                           fontsize=8, color=INK)
        ax.axvline(len(AXES) - 0.5, color=INK, lw=1.5)
        ax.set_title(title, fontsize=9, loc="left", color=INK)
        for sp in ax.spines.values():
            sp.set_visible(False)
        cb = fig.colorbar(im, ax=ax, fraction=0.02, pad=0.01)
        cb.ax.tick_params(labelsize=7)
    fig.text(0.01, 0.005, "[verdict] from adjusted R² of the component on 6 taste axes vs 20 cuisine columns "
             "(rule in run.py: >=2x and >=0.10). Sign of each PC is arbitrary.", fontsize=7.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(RESULTS / "pca_taste_nation_heatmap.png", metadata={"Software": None})
    plt.close(fig)


def plot_direction_order(panels):
    """panels: [(title, {cuisine: z(space)}, {cuisine: z(score)} or None)]"""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    INK, MUTED, BLUE, ORANGE = "#0b0b0b", "#52514e", "#2a78d6", "#d55e00"
    fig, axes = plt.subplots(2, 4, figsize=(17, 11), dpi=140)
    axes = axes.ravel()
    for ax, (title, zs, zt) in zip(axes, panels):
        order = sorted(zs, key=lambda c: zs[c])
        y = np.arange(len(order))
        ax.axvline(0, color="#d4d3cf", lw=1)
        ax.scatter([zs[c] for c in order], y, s=28, color=BLUE, zorder=3, label="space: dish projection")
        if zt is not None:
            ax.scatter([zt[c] for c in order], y, s=28, facecolors="none", edgecolors=ORANGE, lw=1.3, zorder=3,
                       label="scores: dish mean taste")
        ax.set_yticks(y)
        ax.set_yticklabels(order, fontsize=8, color=INK)
        ax.set_title(title, fontsize=9, loc="left", color=INK)
        ax.tick_params(axis="x", labelsize=7)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    axes[len(panels) - 1].set_xlabel("cuisine mean, in SD of all dishes", fontsize=8, color=MUTED)
    h, l = axes[0].get_legend_handles_labels()
    axes[-1].axis("off")
    axes[-1].legend(h, l, loc="center", frameon=False, fontsize=10)
    axes[-1].text(0.5, 0.25, "x = (cuisine mean − overall mean) / SD over dishes\n"
                  "space: dish vector · taste direction (ridge coef)\n"
                  "scores: mean of human taste scores of the dish's\n"
                  f"scored ingredients (dishes with >= {DISH_MIN_SCORED})\n"
                  "each panel sorted by the space value",
                  ha="center", va="center", fontsize=8.5, color=MUTED, transform=axes[-1].transAxes)
    fig.tight_layout()
    fig.savefig(RESULTS / "taste_direction_cuisine_order.png", metadata={"Software": None})
    plt.close(fig)


# ---------------------------------------------------------------------------
def fmt_pm(m, s):
    return f"{m:.2f}±{s:.2f}"


def main():
    import gensim, sklearn, scipy, matplotlib
    from scipy.stats import spearmanr
    from sklearn.decomposition import PCA

    RESULTS.mkdir(parents=True, exist_ok=True)
    t_all = time.perf_counter()
    log, metrics = {}, {}
    L = []   # summary.md

    # ---------------- データ ----------------
    recipes = B.load_recipes(log)
    wv = B.load_vectors(recipes, log)
    recs_idx, recs = [], []
    for r in recipes:
        idx = [wv.key_to_index[t] for t in r["ingredients"] if t in wv.key_to_index]
        if idx:
            recs_idx.append(idx)
            recs.append(r)
    labels = np.array([r["cuisine"] for r in recs])
    cuisines = sorted(set(labels))
    y = np.array([cuisines.index(c) for c in labels])
    W0 = unit(wv.vectors)
    X0 = B.dish_vectors(W0, recs_idx)
    tags = B.culture_tags(recipes, cuisines)
    dessert = np.array([sum(m in set(r["ingredients"]) for m in B.DESSERT_MARKERS) >= B.DESSERT_MIN_MARKERS
                        for r in recs])

    final, ings = read_scores(TASTE_PATH)
    draft, _ = read_scores(DRAFT_PATH)
    missing = [t for t in ings if t not in wv.key_to_index]
    assert not missing, missing
    assert set(draft) == set(final)
    ing_idx = np.array([wv.key_to_index[t] for t in ings])
    T = np.array([[float(final[t][a]) for a in AXES] for t in ings])
    Td = np.array([[float(draft[t][a]) for a in AXES] for t in ings])
    ja = {t: final[t]["ja"] for t in ings}
    canon = np.array([final[t]["canonical"] for t in ings])
    groups = np.unique(canon, return_inverse=True)[1]
    V = W0[ing_idx].astype(np.float64)
    Pn = nation_profile(recipes, cuisines, ings)
    log["n_ingredients"] = len(ings)
    log["n_canonical_groups"] = int(groups.max() + 1)

    # Exp-01b の重心差 SVD（同じ関数）
    Q_cen, s_cen, Mcen = M1B.centroid_basis(X0, y, len(cuisines))
    assert Q_cen.shape[1] == 19
    Q_cen = Q_cen.astype(np.float64)

    # ---------------- 1. 予測可能性 ----------------
    rng_dim = V.shape[1]
    feats = {
        "vec": ("食材ベクトル（100 次元）", lambda rep: V),
        "random": ("ランダムベクトル（100 次元、正規乱数。反復ごとに引き直し）",
                   lambda rep: np.random.default_rng(SEED + 1000 + rep).standard_normal((len(ings), rng_dim))),
        "nation": ("国籍プロファイル P(国籍|食材)（20 次元）", lambda rep: Pn),
        "vec+nation": ("食材ベクトル + 国籍プロファイル（120 次元）", lambda rep: np.hstack([V, Pn])),
    }
    pred_res = {k: evaluate_features(fn, T, groups) for k, (_, fn) in feats.items()}

    # 2. 重心差除去後
    for k in REMOVE_K:
        Wk = B.remove_subspace(W0, Q_cen[:, :k].astype(np.float32)).astype(np.float64)
        Vk = Wk[ing_idx]
        feats[f"removed_{k}"] = (f"重心差 {k} 本を除いた食材ベクトル", lambda rep, Vk=Vk: Vk)
        pred_res[f"removed_{k}"] = evaluate_features(lambda rep, Vk=Vk: Vk, T, groups)
        Ck = V @ Q_cen[:, :k]
        feats[f"only_{k}"] = (f"除いた {k} 本の座標だけ（{k} 次元）", lambda rep, Ck=Ck: Ck)
        pred_res[f"only_{k}"] = evaluate_features(lambda rep, Ck=Ck: Ck, T, groups)

        # 対照 (a): 単位長に戻さない除去（戻すことによる歪みの寄与を分ける）
        Vn = V - (V @ Q_cen[:, :k]) @ Q_cen[:, :k].T
        feats[f"removed_{k}_norenorm"] = (f"重心差 {k} 本を除去（単位長に戻さない）", lambda rep, Vn=Vn: Vn)
        pred_res[f"removed_{k}_norenorm"] = evaluate_features(lambda rep, Vn=Vn: Vn, T, groups)
        # 対照 (b): ランダムな k 本を除去（Exp-01b と同じく単位長に戻す）
        rr = []
        for s_ in range(N_RANDOM_SUBSPACES):
            Qr, _ = np.linalg.qr(np.random.default_rng(SEED + 2000 + 100 * k + s_).standard_normal((V.shape[1], k)))
            Vr = B.remove_subspace(W0.astype(np.float64), Qr)[ing_idx]
            rr.append(evaluate_features(lambda rep, Vr=Vr: Vr, T, groups))
        agg = {}
        for cv in ("kfold", "group"):
            r2 = np.array([x[cv]["r2_mean"] for x in rr])
            agg[cv] = {"r2_mean": r2.mean(0).tolist(), "r2_std": r2.std(0).tolist(),
                       "rho_mean": np.array([x[cv]["rho_mean"] for x in rr]).mean(0).tolist(),
                       "rho_std": np.array([x[cv]["rho_mean"] for x in rr]).std(0).tolist(),
                       "r2_axis_avg": float(r2.mean(1).mean()),
                       "rho_axis_avg": float(np.array([x[cv]["rho_axis_avg"] for x in rr]).mean())}
        feats[f"random_removed_{k}"] = (f"ランダムな {k} 本を除去（{N_RANDOM_SUBSPACES} 回平均±回間の標準偏差）", None)
        pred_res[f"random_removed_{k}"] = agg

    # 7 用: 下書きスコアで同じ予測（食材ベクトル）
    pred_draft = evaluate_features(lambda rep: V, Td, groups)
    metrics["prediction"] = {k: {"features": feats[k][0], **v} for k, v in pred_res.items()}
    metrics["prediction_draft_scores_vec"] = pred_draft

    def pred_table(keys, cv):
        rows = ["| 特徴 | " + " | ".join(AXES_JA[a] for a in AXES) + " | 平均 |", "|---|" + "---|" * (len(AXES) + 1)]
        for k in keys:
            p = pred_res[k][cv]
            rows.append(f"| {feats[k][0]} | " + " | ".join(fmt_pm(m, s) for m, s in zip(p["r2_mean"], p["r2_std"]))
                        + f" | {p['r2_axis_avg']:.2f} |")
        return rows

    def rho_table(keys, cv):
        rows = ["| 特徴 | " + " | ".join(AXES_JA[a] for a in AXES) + " | 平均 |", "|---|" + "---|" * (len(AXES) + 1)]
        for k in keys:
            p = pred_res[k][cv]
            rows.append(f"| {feats[k][0]} | " + " | ".join(f"{m:.2f}" for m in p["rho_mean"])
                        + f" | {p['rho_axis_avg']:.2f} |")
        return rows

    # 分散の分解（group CV の R²）
    g = {k: np.array(pred_res[k]["group"]["r2_mean"]) for k in ("vec", "nation", "vec+nation")}
    shared = g["vec"] + g["nation"] - g["vec+nation"]
    uniq_vec = g["vec+nation"] - g["nation"]
    uniq_nat = g["vec+nation"] - g["vec"]
    metrics["variance_partition_group"] = {
        "shared": shared.tolist(), "vec_only": uniq_vec.tolist(), "nation_only": uniq_nat.tolist(),
        "shared_share_of_vec": (shared / np.where(g["vec"] > 0, g["vec"], np.nan)).tolist()}

    base_keys = ["vec", "random", "nation", "vec+nation"]
    L += ["# Exp-02 味覚スコアと学習空間の比較（主要結果）", "",
          f"- 味覚スコア: `data/labels/taste_scores.csv`（本人確認済み {len(ings)} 食材、canonical {log['n_canonical_groups']} 群）。"
          "0〜5 の整数、苦は 0〜3 のみ",
          "- 食材ベクトル: Exp-01 の word2vec（単位長）。料理ベクトル: Exp-01 と同じ（食材単位ベクトルの平均を単位長に）",
          "- 重心差方向: Exp-01b run_methods.py の centroid_basis（cuisine 重心 − 全体平均 の 20×100 行列の右特異ベクトル、階数 19）",
          "- 実行・設定・所要時間は run_log.md、数値の全体は metrics.json", "",
          "## 1. 食材ベクトルから味は予測できるか", "",
          f"StandardScaler → RidgeCV（α は学習 fold 内 GCV で軸ごと）。{CV_FOLDS}-fold × {CV_REPEATS} 回（分割の乱数を変える）。"
          "R² は out-of-fold 予測をまとめて計算、表は平均±標準偏差。",
          "- **KFold**: 食材単位で分割（依頼どおりの 5-fold）",
          "- **GroupKFold**: `canonical` 単位で分割。garlic / garlic cloves / minced garlic のような表記違いが学習と評価に分かれると、"
          "ほぼ同じベクトル・同じスコアが両側に入って R² が上がる。それを防いだ版で、以降の比較はこちらを主に使う", "",
          "### R²（GroupKFold）", ""] + pred_table(base_keys, "group") + [
          "", "### R²（KFold）", ""] + pred_table(base_keys, "kfold") + [
          "", "### 順位相関 ρ（GroupKFold、予測と正解の Spearman）", ""] + rho_table(base_keys, "group") + [
          "", "### 国籍で説明できる分（GroupKFold の R² を分解）", "",
          "共有 = R²(ベクトル) + R²(国籍) − R²(両方)。ベクトル固有 = R²(両方) − R²(国籍)。CV の R² なので負や和の不整合も出うる（そのまま載せる）。", "",
          "| | " + " | ".join(AXES_JA[a] for a in AXES) + " |", "|---|" + "---|" * len(AXES),
          "| R²(ベクトル) | " + " | ".join(f"{v:.2f}" for v in g["vec"]) + " |",
          "| R²(国籍) | " + " | ".join(f"{v:.2f}" for v in g["nation"]) + " |",
          "| R²(両方) | " + " | ".join(f"{v:.2f}" for v in g["vec+nation"]) + " |",
          "| 共有（国籍でも説明できる分） | " + " | ".join(f"{v:.2f}" for v in shared) + " |",
          "| ベクトル固有 | " + " | ".join(f"{v:.2f}" for v in uniq_vec) + " |",
          "| 国籍固有 | " + " | ".join(f"{v:.2f}" for v in uniq_nat) + " |",
          "| 共有 ÷ R²(ベクトル) | " + " | ".join(f"{v / gv:.2f}" if gv > 0 else "—" for v, gv in zip(shared, g["vec"])) + " |",
          ""]

    # ---------------- 2. 除去後 ----------------
    base_g = np.array(pred_res["vec"]["group"]["r2_mean"])
    rm_rows = ["| 特徴 | " + " | ".join(AXES_JA[a] for a in AXES) + " | 平均 | 平均の保持率 |",
               "|---|" + "---|" * (len(AXES) + 2)]
    for k in (["vec"] + [f"removed_{k}" for k in REMOVE_K] + [f"removed_{k}_norenorm" for k in REMOVE_K]
              + [f"random_removed_{k}" for k in REMOVE_K] + [f"only_{k}" for k in REMOVE_K]):
        p = pred_res[k]["group"]
        rm_rows.append(f"| {feats[k][0]} | " + " | ".join(fmt_pm(m, s) for m, s in zip(p["r2_mean"], p["r2_std"]))
                       + f" | {p['r2_axis_avg']:.2f} | {p['r2_axis_avg'] / base_g.mean():.2f} |")
    L += ["## 2. 重心差方向を除いた後も味は予測できるか", "",
          "Exp-01b と同じく、単位長の食材ベクトルから重心差 k 本の成分を引いて単位長に戻したもの。"
          "「除いた k 本の座標だけ」は逆に、除いた部分空間への射影（k 次元）だけで予測したもの。R² は GroupKFold。"
          "保持率 = 6 軸平均 R² ÷ 元のベクトルの 6 軸平均 R²。",
          "対照: 「単位長に戻さない」は引いたまま（Exp-01b の単位長への再正規化の影響を分ける）。"
          f"「ランダムな k 本」は同じ本数のランダムな正規直交方向を除いたもの（{N_RANDOM_SUBSPACES} 回引き直し、± は回ごとの R² の標準偏差）。"
          "重心差の除去で落ちる幅がランダム除去より大きければ、味の予測に重心差方向の成分が効いている", ""] + rm_rows + [""]

    # ---------------- 3. PCA ----------------
    pca_i = PCA(n_components=N_PCA, random_state=SEED).fit(V)
    Zi = pca_i.transform(V)
    pca_all = PCA(n_components=N_PCA, random_state=SEED).fit(W0.astype(np.float64))
    pca_d = PCA(n_components=N_PCA, random_state=SEED).fit(X0.astype(np.float64))
    Zd = pca_d.transform(X0.astype(np.float64))

    # 料理の味: 採点済み食材スコアの平均
    pos = {t: i for i, t in enumerate(ings)}
    n_scored = np.array([sum(t in pos for t in r["ingredients"]) for r in recs])
    n_invocab = np.array([len(ix) for ix in recs_idx])
    dish_T = np.full((len(recs), len(AXES)), np.nan)
    for i, r in enumerate(recs):
        rows = [pos[t] for t in r["ingredients"] if t in pos]
        if rows:
            dish_T[i] = T[rows].mean(axis=0)
    dmask = n_scored >= DISH_MIN_SCORED
    coverage = float((n_scored / n_invocab).mean())
    log["dish_scored_coverage_mean"] = round(coverage, 4)
    log["dish_with_min_scored"] = int(dmask.sum())

    onehot = np.eye(len(cuisines))[y]
    ing_rows, ing_corr, ing_verd = [], [], []
    for j in range(N_PCA):
        z = Zi[:, j]
        ct = corr_cols(z, T)
        cn = corr_cols(z, Pn)
        rt, _ = adj_r2(z, T)
        rn, _ = adj_r2(z, Pn[:, :-1])  # 和 1 なので 1 列落とす
        v = verdict(rt, rn)
        share_c = float(np.linalg.norm(Q_cen.T @ pca_i.components_[j]) ** 2)
        # 全語彙 PCA の同じ番号の成分との |cos|
        cos_all = float(np.abs(pca_all.components_ @ pca_i.components_[j]).max())
        ing_rows.append({"pc": j + 1, "explained": float(pca_i.explained_variance_ratio_[j]),
                         "corr_taste": dict(zip(AXES, ct.tolist())), "corr_nation": dict(zip(cuisines, cn.tolist())),
                         "adj_r2_taste": rt, "adj_r2_nation": rn, "verdict": v,
                         "share_in_centroid19": share_c, "max_abs_cos_with_fullvocab_pcs": cos_all})
        ing_corr.append(np.concatenate([ct, cn]))
        ing_verd.append(v)
    dish_rows, dish_corr, dish_verd = [], [], []
    for j in range(N_PCA):
        z = Zd[:, j]
        zm = z[dmask]
        ct = corr_cols(zm, dish_T[dmask])
        cn = corr_cols(z, onehot)
        rt, _ = adj_r2(zm, dish_T[dmask])
        rn = eta2(z, labels, cuisines)   # one-hot 回帰の R² = η²（n が大きく調整はほぼ不要）
        v = verdict(rt, rn)
        dish_rows.append({"pc": j + 1, "explained": float(pca_d.explained_variance_ratio_[j]),
                          "corr_taste": dict(zip(AXES, ct.tolist())), "corr_cuisine": dict(zip(cuisines, cn.tolist())),
                          "adj_r2_taste": rt, "eta2_cuisine": rn, "verdict": v,
                          "corr_dessert": float(corr_cols(z, dessert[:, None].astype(float))[0]),
                          "share_in_centroid19": float(np.linalg.norm(Q_cen.T @ pca_d.components_[j]) ** 2)})
        dish_corr.append(np.concatenate([ct, cn]))
        dish_verd.append(v)
    # 図2 の PCA と同じ成分か（Exp-01 projections の pca_2d.npy と照合）
    p2 = ROOT / "experiments" / "exp-01" / "results" / "projections" / "pca_2d.npy"
    fig2_check = None
    if p2.exists():
        P2 = np.load(p2)
        if len(P2) == len(Zd):
            fig2_check = [float(np.corrcoef(P2[:, 0], Zd[:, 0])[0, 1]), float(np.corrcoef(P2[:, 1], Zd[:, 1])[0, 1])]
    metrics["pca_ingredient"] = ing_rows
    metrics["pca_dish"] = dish_rows
    metrics["pca_dish_fig2_corr_pc1_pc2"] = fig2_check

    def top_n(d, n=3):
        return ", ".join(f"{k} {v:+.2f}" for k, v in sorted(d.items(), key=lambda kv: -abs(kv[1]))[:n])

    L += ["## 3. PCA 上位成分は味か地域か", "",
          f"判定規則（結果を見る前に固定）: 成分スコアを 6 軸味覚で回帰した自由度調整済み R²（R²_味）と、国籍側で回帰した R²（R²_国）を比べる。"
          f"両方 {VERDICT_MIN} 未満 →「どちらも弱い」、一方が他方の {VERDICT_RATIO:.0f} 倍以上 →「味寄り」/「地域寄り」、それ以外 →「両方」。"
          "相関の符号は成分の向きが任意なので意味を持たない。図: `pca_taste_nation_heatmap.png`", "",
          "### 食材ベクトル（採点済み 303 食材で PCA）", "",
          "国籍側 = P(国籍|食材) 20 列（和が 1 なので回帰では 1 列落とす）。重心差 19 = 成分の向きが重心差部分空間に入る割合（|Qᵀu|²）。"
          "全語彙 cos = 全語彙で PCA した第1〜10成分との |cos| の最大（303 食材の PCA が全語彙の成分と一致しているかの目安）。", "",
          "| 成分 | 説明分散 | R²_味 | R²_国 | 判定 | 味の相関 上位3 | 国籍の相関 上位3 | 重心差 19 | 全語彙 cos |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in ing_rows:
        L.append(f"| PC{r['pc']} | {r['explained']:.3f} | {r['adj_r2_taste']:.2f} | {r['adj_r2_nation']:.2f} | {r['verdict']} | "
                 f"{top_n({AXES_JA[a]: v for a, v in r['corr_taste'].items()})} | {top_n(r['corr_nation'])} | "
                 f"{r['share_in_centroid19']:.2f} | {r['max_abs_cos_with_fullvocab_pcs']:.2f} |")
    L += ["", "### 料理ベクトル（39,774 レシピで PCA）", "",
          f"料理の味 = そのレシピの採点済み食材のスコア平均。採点済み食材が {DISH_MIN_SCORED} 個以上のレシピ（{dmask.sum()} 件）で相関と R²_味 を出す。"
          f"語彙内食材のうち採点済みの割合はレシピ平均 {coverage:.1%}。"
          "国籍側 = cuisine one-hot での η²（= one-hot 回帰の R²）。製菓 = Exp-01b の製菓レシピ判定（マーカー 3 個以上）との相関。", ""]
    if fig2_check:
        L += [f"図2（Exp-01 projections の PCA）との照合: 第1成分 r = {fig2_check[0]:+.3f}、第2成分 r = {fig2_check[1]:+.3f}（|r|≈1 なら同じ成分）", ""]
    L += ["| 成分 | 説明分散 | R²_味 | η²_国 | 判定 | 味の相関 上位3 | 国籍の相関 上位3 | 製菓との r | 重心差 19 |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in dish_rows:
        L.append(f"| PC{r['pc']} | {r['explained']:.3f} | {r['adj_r2_taste']:.2f} | {r['eta2_cuisine']:.2f} | {r['verdict']} | "
                 f"{top_n({AXES_JA[a]: v for a, v in r['corr_taste'].items()})} | {top_n(r['corr_cuisine'])} | "
                 f"{r['corr_dessert']:+.2f} | {r['share_in_centroid19']:.2f} |")
    L += [""]
    plot_pca_heatmap(np.array(ing_corr), np.array(dish_corr), cuisines, ing_verd, dish_verd,
                     pca_i.explained_variance_ratio_, pca_d.explained_variance_ratio_)

    # ---------------- 4. 味の方向 ----------------
    from sklearn.linear_model import RidgeCV

    Vc = V - V.mean(0)
    rcv = RidgeCV(alphas=RIDGE_ALPHAS, alpha_per_target=True).fit(Vc, T)
    D_ridge = unit(rcv.coef_)                         # 6 × 100
    D_diff, diff_n = [], {}
    for j, a in enumerate(AXES):
        hi = DIFF_HIGH
        while (T[:, j] >= hi).sum() < DIFF_MIN_N:
            hi -= 1
        top, bot = T[:, j] >= hi, T[:, j] == 0
        diff_n[a] = {"high_threshold": hi, "n_high": int(top.sum()), "n_zero": int(bot.sum())}
        D_diff.append(unit(V[top].mean(0) - V[bot].mean(0)))
    D_diff = np.array(D_diff)
    soy_butter = unit(W0[wv.key_to_index["soy sauce"]] - W0[wv.key_to_index["butter"]]).astype(np.float64)

    Xd = X0.astype(np.float64)
    dir_rows, panels = {}, []
    ts_means_all = {}
    for j, a in enumerate(AXES):
        # 採点スコアでの料理の味の国籍平均（空間を使わない参照）
        tv = dish_T[dmask, j]
        tl = labels[dmask]
        t_means = {c: float(tv[tl == c].mean()) for c in cuisines}
        t_z = {c: (t_means[c] - tv.mean()) / tv.std() for c in cuisines}
        ts_means_all[a] = t_z
        rec = {"eta2_dish_taste_scores": eta2(tv, tl, cuisines)}
        for name, d in [("ridge", D_ridge[j]), ("diff", D_diff[j])]:
            proj = Xd @ d
            means = {c: float(proj[labels == c].mean()) for c in cuisines}
            z = {c: (means[c] - proj.mean()) / proj.std() for c in cuisines}
            rec[name] = {
                "eta2_cuisine": eta2(proj, labels, cuisines),
                "cuisine_mean_z": dict(sorted(z.items(), key=lambda kv: -kv[1])),
                "spearman_vs_score_order": float(spearmanr([z[c] for c in cuisines], [t_z[c] for c in cuisines]).statistic),
                "corr_with_dish_taste": float(np.corrcoef(proj[dmask], tv)[0, 1]),
                "share_in_centroid19": float(np.linalg.norm(Q_cen.T @ d) ** 2),
                "cos_with_soy_butter": float(d @ soy_butter),
                "spearman_vs_soy_butter_order": None,
            }
            if name == "ridge":
                panels.append((f"{a}  eta²={rec[name]['eta2_cuisine']:.2f}  "
                               f"rho(space,scores)={rec[name]['spearman_vs_score_order']:+.2f}", z, t_z))
        rec["cos_ridge_vs_diff"] = float(D_ridge[j] @ D_diff[j])
        dir_rows[a] = rec
    sb_proj = Xd @ soy_butter
    sb_means = {c: float(sb_proj[labels == c].mean()) for c in cuisines}
    sb_z = {c: (sb_means[c] - sb_proj.mean()) / sb_proj.std() for c in cuisines}
    sb_eta = eta2(sb_proj, labels, cuisines)
    for a in AXES:
        for name in ("ridge", "diff"):
            z = dir_rows[a][name]["cuisine_mean_z"]
            dir_rows[a][name]["spearman_vs_soy_butter_order"] = float(
                spearmanr([z[c] for c in cuisines], [sb_z[c] for c in cuisines]).statistic)
    panels.append((f"soy sauce <-> butter (Exp-01 axis)  eta²={sb_eta:.2f}", sb_z, None))
    plot_direction_order(panels)
    gram = D_ridge @ D_ridge.T
    metrics["taste_directions"] = {"per_axis": dir_rows, "diff_counts": diff_n,
                                   "soy_butter_eta2": sb_eta, "soy_butter_share_in_centroid19":
                                   float(np.linalg.norm(Q_cen.T @ soy_butter) ** 2),
                                   "ridge_alpha": dict(zip(AXES, np.atleast_1d(rcv.alpha_).tolist())),
                                   "ridge_direction_cosines": gram.tolist(),
                                   "centroid19_share_random_direction_expected": 19 / 100}

    L += ["## 4. 味の方向に料理を射影したときの国籍の並び", "",
          "- 味の方向（リッジ）: 中心化した食材ベクトル → 6 軸スコアの RidgeCV（全 303 食材で学習）の係数ベクトルを単位長にしたもの",
          f"- 味の方向（平均差）: スコア {DIFF_HIGH} 以上（{DIFF_MIN_N} 件未満なら閾値を下げる）の食材の平均 − スコア 0 の食材の平均",
          "- 料理ベクトル（39,774 件）を方向に射影し、cuisine で説明される分散の割合 η² を出す。Exp-01b の η² と同じ定義",
          "- 参照: 空間を使わず、採点スコアから作った料理の味（採点済み食材 3 個以上）自体の η²。"
          "これが大きければ、その味は実際に国籍で違う（射影の η² が大きいこと自体は絡みの証拠にならない）",
          "- ρ(スコア順) = 射影の国籍平均の並びと、スコアから作った料理の味の国籍平均の並びの順位相関。"
          "ρ(醤油↔バター) = soy sauce↔butter 軸の国籍の並びとの順位相関",
          "- 重心差 19 = 方向が重心差部分空間に入る割合。ランダムな方向なら期待値 19/100 = 0.19",
          f"- 図: `taste_direction_cuisine_order.png`（リッジ方向。青 = 空間、橙の白抜き = スコア）", "",
          "| 軸 | 方向 | η²（射影） | η²（スコアの料理の味） | ρ(スコア順) | 料理の味との r | 重心差 19 | cos(醤油↔バター) | ρ(醤油↔バター) | 上位3国籍 | 下位3国籍 |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for a in AXES:
        for name, lab in (("ridge", "リッジ"), ("diff", "平均差")):
            r = dir_rows[a][name]
            order = list(r["cuisine_mean_z"])
            L.append(f"| {AXES_JA[a]} | {lab} | {r['eta2_cuisine']:.3f} | {dir_rows[a]['eta2_dish_taste_scores']:.3f} | "
                     f"{r['spearman_vs_score_order']:+.2f} | {r['corr_with_dish_taste']:+.2f} | {r['share_in_centroid19']:.2f} | "
                     f"{r['cos_with_soy_butter']:+.2f} | {r['spearman_vs_soy_butter_order']:+.2f} | "
                     f"{', '.join(order[:3])} | {', '.join(order[::-1][:3])} |")
    sb_order = sorted(sb_z, key=lambda c: -sb_z[c])
    L += [f"| 醤油↔バター | Exp-01 | {sb_eta:.3f} | — | — | — | "
          f"{metrics['taste_directions']['soy_butter_share_in_centroid19']:.2f} | +1.00 | +1.00 | "
          f"{', '.join(sb_order[:3])} | {', '.join(sb_order[::-1][:3])} |", "",
          "リッジ方向と平均差方向の cos: " + ", ".join(f"{AXES_JA[a]} {dir_rows[a]['cos_ridge_vs_diff']:+.2f}" for a in AXES),
          "", "リッジ方向どうしの cos:", "",
          "| | " + " | ".join(AXES_JA[a] for a in AXES) + " |", "|---|" + "---|" * len(AXES)]
    for i, a in enumerate(AXES):
        L.append(f"| {AXES_JA[a]} | " + " | ".join(f"{gram[i, j]:+.2f}" for j in range(len(AXES))) + " |")
    L += [""]

    # ---------------- 5. 足し引き ----------------
    Dq, _ = np.linalg.qr(D_ridge.T)                   # 100 × 6 正規直交
    spaces = {"normal": ("通常（Exp-01）", None)}
    for k in ARITH_PRESERVE_K:
        Qk = Q_cen[:, :k]
        spaces[f"cen{k}"] = (f"重心差 {k} 本を除去（Exp-01b）", Qk)
        Qp = Qk - Dq @ (Dq.T @ Qk)                    # 味の方向 6 本の成分を抜いてから直交化
        Qp = M1B.orth_append(None, Qp)
        spaces[f"cen{k}_keep"] = (f"重心差 {k} 本を除去・味の方向 6 本を保存", Qp)
    ari = {}
    mirin_i = wv.key_to_index["mirin"]
    for key, (desc, Q) in spaces.items():
        Wq = W0.astype(np.float64) if Q is None else B.remove_subspace(W0.astype(np.float64), Q)
        Xq = B.dish_vectors(Wq, recs_idx)
        cent = {c: unit(Xq[labels == c].mean(axis=0)) for c in cuisines}
        v = Wq[mirin_i] - cent["japanese"] + cent["french"]
        sims = Wq @ unit(v)
        order = [i for i in np.argsort(-sims) if i != mirin_i]
        top = order[:ARITH_TOP_K]
        cal = wv.key_to_index.get("calvados")
        cal_rank = order.index(cal) + 1 if cal is not None else None
        # 結果ベクトルの味の予測（全 303 で学習したリッジ。その空間の食材ベクトルで学習し直す）
        Vq = Wq[ing_idx]
        mdl = RidgeCV(alphas=RIDGE_ALPHAS, alpha_per_target=True).fit(Vq, T)
        ari[key] = {
            "desc": desc,
            "n_dirs_removed": 0 if Q is None else int(Q.shape[1]),
            "mirin_norm_share_removed": 0.0 if Q is None else float(np.linalg.norm(Q.T @ W0[mirin_i]) ** 2),
            "taste_dirs_share_removed": 0.0 if Q is None else float((np.linalg.norm(Q.T @ D_ridge.T, axis=0) ** 2).mean()),
            "top": [[wv.index_to_key[i], round(float(sims[i]), 4)] for i in top],
            "calvados_rank": cal_rank,
            "calvados_cos": None if cal is None else round(float(sims[cal]), 4),
            "pred_taste_result": dict(zip(AXES, mdl.predict(unit(v)[None])[0].round(2).tolist())),
            "pred_taste_mirin": dict(zip(AXES, mdl.predict(Wq[mirin_i][None])[0].round(2).tolist())),
        }
    metrics["arithmetic_mirin"] = ari
    mirin_scores = "/".join(final["mirin"][a] for a in AXES)

    def ing_cell(t, s):
        tg = f" [{tags[t][0][:3]}]" if t in tags else ""
        sc = "/".join(final[t][a] for a in AXES) if t in final else "—"
        return f"{t}{tg} ({s:.2f}) {sc}"

    A = ["# Exp-02 mirin − japanese + french（味を残した足し引き）", "",
         "- 式は Exp-01 と同じ: v(mirin) − 重心(japanese) + 重心(french)。重心は各空間で料理ベクトルを作り直して取る。mirin 自身は除外",
         "- 「味の方向を保存」: 重心差 k 本の部分空間から味のリッジ方向 6 本（4 と同じ）の成分を引き、直交化してから除去する。"
         "除去する本数は同じ k 本で、味の方向の成分は空間に残る",
         f"- 各セル: 食材 [偏りの強い cuisine]（cos） 甘/塩/酸/苦/旨/辛 の本人スコア（303 食材外は —）。mirin は {mirin_scores}",
         "- [xxx] は Exp-01b と同じ文化タグ（P(c|食材)/P(c) ≥ 3 の最大の cuisine）", "",
         "| # | " + " | ".join(ari[k]["desc"] for k in spaces) + " |", "|---|" + "---|" * len(spaces)]
    for i in range(ARITH_TOP_K):
        A.append(f"| {i+1} | " + " | ".join(ing_cell(*ari[k]["top"][i]) for k in spaces) + " |")
    A += ["", "| | " + " | ".join(ari[k]["desc"] for k in spaces) + " |", "|---|" + "---|" * len(spaces),
          "| 上位 10 のうち採点済み | " + " | ".join(str(sum(t in final for t, _ in ari[k]["top"])) for k in spaces) + " |",
          "| 上位 10 のうち [jap] タグ | " + " | ".join(str(sum(t in tags and tags[t][0] == "japanese" for t, _ in ari[k]["top"])) for k in spaces) + " |",
          "| calvados の順位（cos） | " + " | ".join(f"{ari[k]['calvados_rank']} ({ari[k]['calvados_cos']:.2f})" for k in spaces) + " |",
          "| mirin から除いた二乗ノルム | " + " | ".join(f"{ari[k]['mirin_norm_share_removed']:.2f}" for k in spaces) + " |",
          "| 味の方向 6 本から除いた割合（平均） | " + " | ".join(f"{ari[k]['taste_dirs_share_removed']:.2f}" for k in spaces) + " |",
          "| 結果ベクトルの予測味（甘/塩/酸/苦/旨/辛） | " + " | ".join("/".join(f"{x:.1f}" for x in ari[k]["pred_taste_result"].values()) for k in spaces) + " |",
          "| mirin の予測味（同じモデル） | " + " | ".join("/".join(f"{x:.1f}" for x in ari[k]["pred_taste_mirin"].values()) for k in spaces) + " |",
          "", f"予測味: その空間の食材ベクトルで全 303 食材に RidgeCV を学習し、結果ベクトル（単位長）に当てた値。参考値。", ""]
    (RESULTS / "arithmetic.md").write_text("\n".join(A))
    L += ["## 5. mirin − japanese + french", "", "全表は `arithmetic.md`。上位 5 件（本人スコア 甘/塩/酸/苦/旨/辛）:", "",
          "| # | " + " | ".join(ari[k]["desc"] for k in spaces) + " |", "|---|" + "---|" * len(spaces)]
    for i in range(5):
        L.append(f"| {i+1} | " + " | ".join(ing_cell(*ari[k]["top"][i]) for k in spaces) + " |")
    L += ["", "| | " + " | ".join(ari[k]["desc"] for k in spaces) + " |", "|---|" + "---|" * len(spaces),
          "| 上位 10 のうち採点済み | " + " | ".join(str(sum(t in final for t, _ in ari[k]["top"])) for k in spaces) + " |",
          "| calvados の順位 | " + " | ".join(str(ari[k]["calvados_rank"]) for k in spaces) + " |",
          "| mirin から除いた二乗ノルム | " + " | ".join(f"{ari[k]['mirin_norm_share_removed']:.2f}" for k in spaces) + " |",
          f"| 語彙数 | {len(wv)} | | | | |", ""]

    # ---------------- 6. 近さの比較 ----------------
    nz = np.where(np.linalg.norm(T, axis=1) > 0)[0]
    zero_ings = [ings[i] for i in range(len(ings)) if i not in set(nz)]
    Tu = unit(T[nz])
    St = Tu @ Tu.T
    Sv = V[nz] @ V[nz].T
    Pu = unit(Pn[nz])
    Sn = Pu @ Pu.T
    iu = np.triu_indices(len(nz), 1)
    st, sv, sn = St[iu], Sv[iu], Sn[iu]
    same_c = canon[nz][iu[0]] == canon[nz][iu[1]]
    rho_all = float(spearmanr(st, sv).statistic)
    rho_diff = float(spearmanr(st[~same_c], sv[~same_c]).statistic)
    rho_nat = float(spearmanr(sn, sv).statistic)
    rho_nat_diff = float(spearmanr(sn[~same_c], sv[~same_c]).statistic)
    rho_t_n = float(spearmanr(st, sn).statistic)
    # コサインは強さを無視する（甘1 の米と甘5 の砂糖が cos 1）。強さも見るユークリッド距離の版
    from scipy.spatial.distance import pdist
    se = -pdist(T[nz])                                 # 符号反転: 大きいほど近い（pdist は上三角と同じ順）
    rho_euc = float(spearmanr(se, sv).statistic)
    rho_euc_diff = float(spearmanr(se[~same_c], sv[~same_c]).statistic)
    # 偏順位相関（国籍プロファイルの近さを制御）
    from scipy.stats import rankdata
    rt_, rv_, rn_ = rankdata(st), rankdata(sv), rankdata(sn)

    def resid(a, b):
        b1 = np.vstack([np.ones_like(b), b]).T
        return a - b1 @ np.linalg.lstsq(b1, a, rcond=None)[0]
    rho_partial = float(np.corrcoef(resid(rt_, rn_), resid(rv_, rn_))[0, 1])
    pt = rt_ / len(rt_)
    pv = rv_ / len(rv_)
    m = ~same_c
    idx_m = np.where(m)[0]

    def pick(score):
        o = idx_m[np.argsort(-score[idx_m], kind="stable")][:SIM_EXAMPLES]
        return [(ings[nz[iu[0][k]]], ings[nz[iu[1][k]]], float(st[k]), float(sv[k]), float(sn[k])) for k in o]
    agree = pick(np.minimum(pt, pv))                  # 両方で近い
    taste_near_space_far = pick(pt - pv)
    pe = rankdata(se) / len(se)
    euc_near_space_far = pick(pe - pv)
    space_near_taste_far = pick(pv - pt)
    metrics["similarity"] = {"n_ingredients": len(nz), "excluded_all_zero": zero_ings, "n_pairs": int(len(st)),
                             "spearman_taste_vs_space": rho_all, "spearman_taste_vs_space_excl_same_canonical": rho_diff,
                             "spearman_nation_vs_space": rho_nat, "spearman_nation_vs_space_excl_same_canonical": rho_nat_diff,
                             "spearman_taste_vs_nation": rho_t_n,
                             "spearman_taste_euclid_vs_space": rho_euc,
                             "spearman_taste_euclid_vs_space_excl_same_canonical": rho_euc_diff,
                             "taste_near_space_far_euclid": euc_near_space_far, "partial_spearman_taste_space_given_nation": rho_partial,
                             "agree": agree, "taste_near_space_far": taste_near_space_far,
                             "space_near_taste_far": space_near_taste_far}

    def pair_rows(lst):
        rows = ["| # | 食材 A | 食材 B | 味 A | 味 B | 味 cos | 空間 cos | 国籍 cos |", "|---|---|---|---|---|---|---|---|"]
        for i, (a, b, s1, s2, s3) in enumerate(lst):
            rows.append(f"| {i+1} | {a}（{ja[a]}） | {b}（{ja[b]}） | {'/'.join(final[a][x] for x in AXES)} | "
                        f"{'/'.join(final[b][x] for x in AXES)} | {s1:.2f} | {s2:.2f} | {s3:.2f} |")
        return rows
    S6 = ["# Exp-02 味覚スコアの近さと空間の近さ", "",
          f"- 対象: 味覚スコアが全軸 0 でない {len(nz)} 食材（全軸 0 で除外: {', '.join(zero_ings)}）、{len(st)} ペア",
          "- 味 cos = 6 次元スコアのコサイン類似。空間 cos = 食材ベクトルのコサイン類似。国籍 cos = P(国籍|食材) のコサイン類似",
          "- 例は同じ canonical のペア（garlic と minced garlic など）を除いて選んだ。"
          "選び方: 一致 = min(味の順位パーセンタイル, 空間の順位パーセンタイル) の大きい順。"
          "ずれ = 2 つのパーセンタイルの差の大きい順（味 cos は整数スコア由来で同順位が多い）",
          "- 味 A/B は 甘/塩/酸/苦/旨/辛", "",
          "## 一致する例（味も空間も近い）", ""] + pair_rows(agree) + [
          "", "## ずれる例: 味は似ているのに空間で遠い", ""] + pair_rows(taste_near_space_far) + [
          "", "## ずれる例: 味は似ているのに空間で遠い（ユークリッド距離版）", "",
          "コサインは味の強さを無視するので、上の表は「甘だけ 1 の食材」と「甘だけ 5 の食材」の組で埋まる。"
          "味の近さを 6 次元スコアのユークリッド距離（小さいほど近い）の順位に替えて選び直したもの", ""] + pair_rows(euc_near_space_far) + [
          "", "## ずれる例: 空間で近いのに味は違う", ""] + pair_rows(space_near_taste_far) + [""]
    (RESULTS / "similarity.md").write_text("\n".join(S6))
    L += ["## 6. 味覚スコアの近さと空間の近さ", "",
          f"{len(nz)} 食材・{len(st)} ペア（全軸 0 の {len(zero_ings)} 食材を除外）。例の表は `similarity.md`。", "",
          "| 比較 | Spearman ρ（全ペア） | 同じ canonical のペアを除く |", "|---|---|---|",
          f"| 味 cos vs 空間 cos | {rho_all:+.3f} | {rho_diff:+.3f} |",
          f"| 国籍 cos vs 空間 cos（参考） | {rho_nat:+.3f} | {rho_nat_diff:+.3f} |",
          f"| 味 cos vs 国籍 cos | {rho_t_n:+.3f} | — |",
          f"| 味 cos vs 空間 cos、国籍 cos を制御した偏順位相関 | {rho_partial:+.3f} | — |",
          f"| 味の近さ（−ユークリッド距離）vs 空間 cos | {rho_euc:+.3f} | {rho_euc_diff:+.3f} |", "",
          "一致例上位 3: " + "; ".join(f"{a}–{b}" for a, b, *_ in agree[:3]),
          "", "味は似ているのに空間で遠い上位 3（cos）: " + "; ".join(f"{a}–{b}" for a, b, *_ in taste_near_space_far[:3]),
          "", "味は似ているのに空間で遠い上位 3（ユークリッド）: " + "; ".join(f"{a}–{b}" for a, b, *_ in euc_near_space_far[:3]),
          "", "空間で近いのに味は違う上位 3: " + "; ".join(f"{a}–{b}" for a, b, *_ in space_near_taste_far[:3]), ""]

    # ---------------- 7. 下書きとの差 ----------------
    Dlt = T - Td
    changed = np.where(np.abs(Dlt).sum(1) > 0)[0]
    flag = np.array([final[t]["changed_from_draft"] == "1" for t in ings])
    dv = {"n_changed_ingredients": int(len(changed)), "flag_consistent": bool((flag == (np.abs(Dlt).sum(1) > 0)).all()),
          "per_axis": {}}
    Dm = ["# Exp-02 下書き（Claude）と本人確認版の差", "",
          f"- 下書き `taste_scores_draft.csv` と本人確認版 `taste_scores.csv` を食材ごとに比べた。"
          f"変更された食材 {len(changed)} 件（`changed_from_draft` 列と一致: {dv['flag_consistent']}）",
          "- 差 = 本人 − 下書き", "",
          "## 軸ごとの集計", "",
          "| 軸 | 変更セル数 | 上げた | 下げた | 差の合計 | |差|の合計 | 下書き平均 → 本人平均 |", "|---|---|---|---|---|---|---|"]
    for j, a in enumerate(AXES):
        d = Dlt[:, j]
        rec = {"n_changed": int((d != 0).sum()), "n_up": int((d > 0).sum()), "n_down": int((d < 0).sum()),
               "sum": int(d.sum()), "abs_sum": int(np.abs(d).sum()),
               "mean_draft": float(Td[:, j].mean()), "mean_final": float(T[:, j].mean())}
        dv["per_axis"][a] = rec
        Dm.append(f"| {AXES_JA[a]} | {rec['n_changed']} | {rec['n_up']} | {rec['n_down']} | {rec['sum']:+d} | "
                  f"{rec['abs_sum']} | {rec['mean_draft']:.2f} → {rec['mean_final']:.2f} |")
    Dm += ["", "要約（差の合計）: " + " / ".join(f"{AXES_JA[a]}{dv['per_axis'][a]['sum']:+d}" for a in AXES), ""]
    conf = collections.Counter(draft[ings[i]]["confidence"] for i in changed)
    conf_all = collections.Counter(draft[t]["confidence"] for t in ings)
    Dm += ["下書きの confidence 別の変更率: " + ", ".join(
        f"{c} {conf[c]}/{conf_all[c]}" for c in ("high", "medium", "low")), ""]
    pdr = pred_draft["group"]
    pfn = pred_res["vec"]["group"]
    Dm += ["## 予測可能性（1 と同じ設定、食材ベクトル、GroupKFold の R²）", "",
           "| スコア | " + " | ".join(AXES_JA[a] for a in AXES) + " | 平均 |", "|---|" + "---|" * (len(AXES) + 1),
           "| 下書き | " + " | ".join(f"{v:.2f}" for v in pdr["r2_mean"]) + f" | {pdr['r2_axis_avg']:.2f} |",
           "| 本人 | " + " | ".join(f"{v:.2f}" for v in pfn["r2_mean"]) + f" | {pfn['r2_axis_avg']:.2f} |", "",
           f"下書きスコアでの 6 軸平均 R² は {pdr['r2_axis_avg']:.2f}、本人スコアでは {pfn['r2_axis_avg']:.2f}"
           f"（差 {pfn['r2_axis_avg'] - pdr['r2_axis_avg']:+.2f}）。", "",
           "## 変更された食材", "", "| 食材 | 和名 | canonical | 下書き confidence | 変更（下書き→本人） |", "|---|---|---|---|---|"]
    for i in sorted(changed, key=lambda i: -int(final[ings[i]]["n_recipes"])):
        t = ings[i]
        ch = ", ".join(f"{AXES_JA[a]} {int(Td[i, j])}→{int(T[i, j])}" for j, a in enumerate(AXES) if Dlt[i, j] != 0)
        Dm.append(f"| {t} | {ja[t]} | {final[t]['canonical']} | {draft[t]['confidence']} | {ch} |")
    Dm += [""]
    (RESULTS / "draft_vs_final.md").write_text("\n".join(Dm))
    metrics["draft_vs_final"] = dv
    L += ["## 7. 下書きと本人確認版", "", f"詳細は `draft_vs_final.md`。変更 {len(changed)} 食材。差の合計（本人 − 下書き）: "
          + " / ".join(f"{AXES_JA[a]}{dv['per_axis'][a]['sum']:+d}" for a in AXES)
          + f"。下書きスコアでの予測 R²（6 軸平均、GroupKFold）{pdr['r2_axis_avg']:.2f}、本人スコアで {pfn['r2_axis_avg']:.2f}。", ""]

    (RESULTS / "summary.md").write_text("\n".join(L))
    (RESULTS / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2, default=float) + "\n")

    log["total_seconds"] = round(time.perf_counter() - t_all, 1)
    run_log = [
        "# Exp-02 実行ログ", "",
        "`uv run python experiments/exp-02/run.py` の最終実行時の記録。", "",
        "## 環境",
        f"- Python {platform.python_version()} / {platform.platform()}",
        f"- gensim {gensim.__version__}, scikit-learn {sklearn.__version__}, scipy {scipy.__version__}, "
        f"numpy {np.__version__}, matplotlib {matplotlib.__version__}",
        "", "## 入力",
        f"- 食材ベクトル: {log['vectors_source']}（sha256 {log['vectors_sha256'][:16]}…）",
        f"- train.json の SHA-256 一致: {log['raw_sha256_matches']}",
        f"- 味覚スコア: {TASTE_PATH.relative_to(ROOT)}（sha256 {hashlib.sha256(TASTE_PATH.read_bytes()).hexdigest()[:16]}…）、"
        f"{log['n_ingredients']} 食材、canonical {log['n_canonical_groups']} 群",
        f"- 下書き: {DRAFT_PATH.relative_to(ROOT)}（sha256 {hashlib.sha256(DRAFT_PATH.read_bytes()).hexdigest()[:16]}…）",
        f"- 料理: {len(recs)} レシピ。採点済み食材 {DISH_MIN_SCORED} 個以上 {log['dish_with_min_scored']} 件。"
        f"語彙内食材のうち採点済みの割合（レシピ平均） {log['dish_scored_coverage_mean']:.1%}",
        "", "## 設定",
        f"- SEED = {SEED}、CV = {CV_FOLDS}-fold × {CV_REPEATS} 回、RidgeCV alphas = logspace(-3, 4, 15)",
        f"- 重心差除去 k = {REMOVE_K}（ランダム除去の対照 {N_RANDOM_SUBSPACES} 回）、足し引きの味保存 k = {ARITH_PRESERVE_K}、PCA 成分 {N_PCA}",
        f"- 判定規則: VERDICT_MIN = {VERDICT_MIN}, VERDICT_RATIO = {VERDICT_RATIO}",
        f"- 平均差方向の件数: " + ", ".join(f"{a} 上位(≥{v['high_threshold']}) {v['n_high']} / 0 {v['n_zero']}" for a, v in diff_n.items()),
        "", "## 所要時間", f"- 全体: {log['total_seconds']} 秒", ""]
    (RESULTS / "run_log.md").write_text("\n".join(run_log))
    print("\n".join(L))


if __name__ == "__main__":
    main()
