"""Exp-01 補足: UMAP の「島どうしの配置」は本物か、初期配置・乱数の種の産物か。

実行: リポジトリ直下で `uv run python experiments/exp-01/robustness.py`

- 料理ベクトルは run.py と同じ関数・同じ設定（SEED=42, word2vec 100 次元）で作り直す
- projections.py の関数（評価・ラベル配置・軸の体裁）を再利用する。既存成果物は変えない。
  出力は results/robustness/ だけ
  （ただし run.py の関数が data/processed/ の前処理 TSV と word2vec モデルを同じ内容で上書きする）
- 条件（min_dist=0.1, metric=cosine は Exp-01 と同じ）
  1. n_neighbors=30, init=spectral, random_state ∈ {0,1,2,3,42}（42 が Exp-01 図1 = 基準）
  2. n_neighbors=30, init=random,   random_state ∈ {0,1,2,3,42}
  3. 近傍数の系列 n_neighbors ∈ {5, 10, 30, 100, 500, 1000, 5000}, init=spectral, random_state=42
     （5000 だけ 10,000 件サンプル。対照として n_neighbors=30 も同じ 10,000 件サンプルで）
- 島の配置の一致度: 20 国籍の重心（2D 中央値）を基準（図1）の重心と比べる
  - Procrustes 残差（scipy.spatial.procrustes の disparity。平行移動・回転・反転・拡大縮小を許す）
  - 重心間距離行列（上三角 190 対）のスピアマン相関
"""

from __future__ import annotations

import importlib.util
import json
import platform
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("exp01_projections", HERE / "projections.py")
proj = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(proj)
run = proj.run

SEED = run.SEED
OUT = run.RESULTS / "robustness"
EVAL_SAMPLE = proj.EVAL_SAMPLE   # 10000
NEIGHBOR_K = proj.NEIGHBOR_K     # 30
KNN_K = proj.KNN_K               # 10
SEEDS = [0, 1, 2, 3, 42]
N_NULL = 2000                    # 重心の国籍ラベルを入れ替えた帰無分布の回数

# (key, パネルタイトル, n_neighbors, init, random_state, 10k サンプルで当てるか)
CONDITIONS = (
    [(f"spectral_s{s}", f"n=30, spectral, seed={s}" + (" (= Fig. 1, reference)" if s == 42 else ""),
      30, "spectral", s, False) for s in SEEDS]
    + [(f"random_s{s}", f"n=30, init=random, seed={s}", 30, "random", s, False) for s in SEEDS]
    + [(f"n{nn}", f"n={nn}, spectral, seed=42", nn, "spectral", 42, False) for nn in (5, 10, 100, 500, 1000)]
    + [
       ("n5000_sample", "n=5000, spectral, seed=42 [10k sample]", 5000, "spectral", 42, True),
       ("n30_sample", "n=30, spectral, seed=42 [10k sample] (control)", 30, "spectral", 42, True)]
)
REF = "spectral_s42"
# grid.png に並べる条件（乱数の種・初期配置・大きい近傍）
GRID_KEYS = [f"spectral_s{s}" for s in SEEDS] + [f"random_s{s}" for s in SEEDS] + ["n1000", "n5000_sample", "n30_sample"]
# neighbors_series.png に並べる近傍数の系列（n=30 は基準そのもの）
SERIES_KEYS = ["n5", "n10", REF, "n100", "n500", "n1000", "n5000_sample", "n30_sample"]


# ---------------------------------------------------------------------------
def centroids(Y, y, n_cls):
    return np.array([np.median(Y[y == c], axis=0) for c in range(n_cls)])


def upper(D):
    i, j = np.triu_indices(len(D), 1)
    return D[i, j]


def compare_layout(C_ref, C):
    from scipy.spatial import procrustes
    from scipy.spatial.distance import pdist
    from scipy.stats import spearmanr

    _, _, disp = procrustes(C_ref, C)
    rho = spearmanr(pdist(C_ref), pdist(C)).statistic
    return float(disp), float(rho)


def align_to(C_ref, C, Y):
    """C を C_ref に合わせる相似変換（回転・反転・拡大縮小・平行移動）を Y に当てる。表示用。"""
    mr, mc = C_ref.mean(0), C.mean(0)
    A, B = C_ref - mr, C - mc
    U, S, Vt = np.linalg.svd(B.T @ A)
    R = U @ Vt
    s = S.sum() / (B ** 2).sum()
    return (Y - mc) @ R * s + mr


def fit_umap(X, nn, init, rs):
    import umap
    params = dict(run.UMAP_PARAMS, n_neighbors=nn, init=init, random_state=rs)
    return umap.UMAP(**params).fit_transform(X).astype(np.float32), params


def eval_sample(Xs, Ys, ys, nb_hi):
    """10k サンプル内での近傍保持率 (k=30) と 2D 10-NN 国籍一致率。"""
    from sklearn.neighbors import NearestNeighbors
    _, nb_lo = NearestNeighbors(n_neighbors=NEIGHBOR_K + 1).fit(Ys).kneighbors(Ys)
    nb_lo = nb_lo[:, 1:]
    keep = np.mean([len(set(a) & set(b)) / NEIGHBOR_K for a, b in zip(nb_hi, nb_lo)])
    agree = (ys[nb_lo[:, :KNN_K]] == ys[:, None]).mean()
    return round(float(keep), 4), round(float(agree), 4)


# ---------------------------------------------------------------------------
def plot_grid(Ys_plot, y, cuisines, titles, stats, keys, nrows, ncols, figsize, legend_anchor, legend_ncol,
              fname, headline):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    INK = "#0b0b0b"
    counts = np.bincount(y, minlength=len(cuisines))
    order = sorted(range(len(cuisines)), key=lambda c: -counts[c])  # 図1と同じ件数順の tab20
    cmap = plt.get_cmap("tab20")
    col_of = {c: cmap(i) for i, c in enumerate(order)}

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, dpi=100)
    flat = axes.ravel()
    for ax in flat[len(keys):]:
        ax.axis("off")
    placed = {}
    for ax, key in zip(flat, keys):
        Y, yy = Ys_plot[key]
        perm = np.random.default_rng(SEED).permutation(len(yy))
        colors = np.array([col_of[c] for c in yy])
        ax.scatter(Y[perm, 0], Y[perm, 1], s=0.35, c=colors[perm], linewidths=0, alpha=0.55, rasterized=True)
        d, r = stats[key]
        proj.style_ax(ax, titles[key])
        ax.title.set_fontsize(9.5)
        ax.text(0.01, 0.01, f"Procrustes disparity {d:.3f} / Spearman ρ {r:.3f}", transform=ax.transAxes,
                fontsize=8, color="#52514e", va="bottom")
        ax.set_xlim(ax.get_xlim()); ax.set_ylim(ax.get_ylim())
    handles = [plt.Line2D([], [], marker="o", ls="", color=cmap(i), label=f"{cuisines[c]} ({counts[c]})")
               for i, c in enumerate(order)]
    fig.legend(handles=handles, loc="center", bbox_to_anchor=legend_anchor, ncol=legend_ncol, frameon=False,
               fontsize=9.5, labelcolor=INK, markerscale=1.6)
    fig.suptitle(f"Exp-01 robustness: UMAP (min_dist=0.1, metric=cosine) {headline}, colored by cuisine\n"
                 "each panel rotated/reflected/scaled onto the reference (n=30, spectral, seed=42) by Procrustes on the "
                 "20 cuisine medians — display only; labels at medians, moved apart to avoid overlap",
                 x=0.01, ha="left", color=INK, fontsize=12)
    fig.tight_layout(rect=(0, 0.1 if legend_anchor[1] < 0.1 else 0, 1, 0.95))
    for ax, key in zip(flat, keys):
        Y, yy = Ys_plot[key]
        anchors = [np.median(Y[yy == c], axis=0) for c in order]
        kws = [dict(fontsize=5.5, color=INK,
                    bbox=dict(boxstyle="round,pad=0.1", fc="white", ec=cmap(i), lw=0.8, alpha=0.85))
               for i in range(len(order))]
        placed[key] = proj.place_labels(ax, fig, anchors, [cuisines[c] for c in order], kws)
    fig.savefig(OUT / fname, metadata={"Software": None})
    plt.close(fig)
    return placed


# ---------------------------------------------------------------------------
def main():
    import sklearn, umap, scipy, matplotlib
    from scipy.spatial.distance import pdist
    from scipy.stats import spearmanr
    from sklearn.neighbors import NearestNeighbors

    OUT.mkdir(parents=True, exist_ok=True)
    log, metrics = {}, {"conditions": {}}
    t_all = time.perf_counter()

    recipes = run.load_and_preprocess({})
    wv = run.train_word2vec(recipes, {})
    X, kept = run.dish_vectors(recipes, wv, {})
    labels = [recipes[i]["cuisine"] for i in kept]
    cuisines = sorted(set(labels))
    y = np.array([cuisines.index(c) for c in labels])
    n_cls = len(cuisines)
    log["prep_seconds"] = round(time.perf_counter() - t_all, 1)

    # 評価用サンプル（projections.py と同じ引き方）。10k サンプル条件の UMAP もこの集合に当てる
    idx = np.sort(np.random.default_rng(SEED).choice(len(X), size=EVAL_SAMPLE, replace=False))
    Xs, ys = X[idx], y[idx]
    _, nb_hi = NearestNeighbors(n_neighbors=NEIGHBOR_K + 1, metric="cosine").fit(Xs).kneighbors(Xs)
    nb_hi = nb_hi[:, 1:]
    ref100_agree = round(float((ys[nb_hi[:, :KNN_K]] == ys[:, None]).mean()), 4)

    # 100 次元の国籍重心（中央値）どうしのコサイン距離（参考: 2D の重心配置が高次元の関係をどれだけ映すか）
    C100 = centroids(X, y, n_cls)
    d100 = pdist(C100, metric="cosine")

    Ys, C2 = {}, {}
    for key, title, nn, init, rs, sample in CONDITIONS:
        t0 = time.perf_counter()
        Y, params = fit_umap(Xs if sample else X, nn, init, rs)
        sec = round(time.perf_counter() - t0, 1)
        yy = ys if sample else y
        Ys[key] = (Y, yy)
        C2[key] = centroids(Y, yy, n_cls)
        Ysmp = Y if sample else Y[idx]
        keep, agree = eval_sample(Xs, Ysmp, ys, nb_hi)
        metrics["conditions"][key] = {
            "title": title, "params": params, "fit_on": "10k sample" if sample else "all",
            "n_points": int(len(Y)), "seconds": sec,
            "neighbor_preservation_k30_sample": keep, "knn_label_agreement_k10_2d_sample": agree,
        }
        print(f"[{key}] {sec} s  keep={keep} agree={agree}", flush=True)

    # 基準が Exp-01 図1 と一致するか
    ref_npy = np.load(run.RESULTS / "umap_2d.npy")
    Yref = Ys[REF][0]
    metrics["reference_matches_exp01_umap_2d_npy"] = bool(ref_npy.shape == Yref.shape and np.allclose(ref_npy, Yref, atol=1e-4))
    # n=10 / 100 が projections.py の座標と一致するか
    metrics["matches_projections_npy"] = {}
    for nn in (10, 100):
        p = run.RESULTS / "projections" / f"umap_n{nn}_2d.npy"
        if p.exists():
            a, b = np.load(p), Ys[f"n{nn}"][0]
            metrics["matches_projections_npy"][f"n{nn}"] = bool(a.shape == b.shape and np.allclose(a, b, atol=1e-4))

    Cref = C2[REF]
    stats = {}
    for key, *_ in CONDITIONS:
        d, r = compare_layout(Cref, C2[key])
        r100 = float(spearmanr(d100, pdist(C2[key])).statistic)
        stats[key] = (d, r)
        metrics["conditions"][key].update({
            "procrustes_disparity_vs_ref": round(d, 4), "spearman_centroid_dist_vs_ref": round(r, 4),
            "spearman_centroid_dist_vs_100d_cosine": round(r100, 4),
            "centroids_2d": {cuisines[c]: [round(float(v), 3) for v in C2[key][c]] for c in range(n_cls)},
        })

    # 帰無分布: 基準の重心に国籍ラベルをでたらめに付け直したときの値（配置が無関係なら出る値）
    rng = np.random.default_rng(SEED)
    null_d, null_r = [], []
    for _ in range(N_NULL):
        d, r = compare_layout(Cref, Cref[rng.permutation(n_cls)])
        null_d.append(d); null_r.append(r)
    null_d, null_r = np.array(null_d), np.array(null_r)
    metrics["null_label_shuffle"] = {
        "n": N_NULL, "disparity_mean": round(float(null_d.mean()), 4),
        "disparity_p05": round(float(np.percentile(null_d, 5)), 4), "disparity_min": round(float(null_d.min()), 4),
        "spearman_mean": round(float(null_r.mean()), 4), "spearman_p95": round(float(np.percentile(null_r, 95)), 4),
        "spearman_max": round(float(null_r.max()), 4),
    }
    metrics["reference_100d_sample"] = {"knn_label_agreement_k10": ref100_agree}

    # 同じ群の中でのばらつき（種どうし・全ペア）
    def pairwise(keys):
        out = [compare_layout(C2[a], C2[b]) for i, a in enumerate(keys) for b in keys[i + 1:]]
        ds, rs_ = np.array([o[0] for o in out]), np.array([o[1] for o in out])
        return {"pairs": len(out), "disparity_mean": round(float(ds.mean()), 4), "disparity_max": round(float(ds.max()), 4),
                "spearman_mean": round(float(rs_.mean()), 4), "spearman_min": round(float(rs_.min()), 4)}
    metrics["within_group_pairwise"] = {
        "spectral_seeds": pairwise([f"spectral_s{s}" for s in SEEDS]),
        "random_seeds": pairwise([f"random_s{s}" for s in SEEDS]),
    }

    # 表示用に基準へ整列
    t0 = time.perf_counter()
    Ys_plot = {k: (align_to(Cref, C2[k], Y), yy) for k, (Y, yy) in Ys.items()}
    titles = {k: t for k, t, *_ in CONDITIONS}
    log["labels_no_overlap"] = {
        "grid": plot_grid(Ys_plot, y, cuisines, titles, stats, GRID_KEYS, 3, 5, (20, 13.2), (0.8, 0.18), 3,
                          "grid.png", "under different seeds / init / n_neighbors"),
        "neighbors_series": plot_grid(Ys_plot, y, cuisines, titles, stats, SERIES_KEYS, 2, 4, (20, 11.5), (0.5, 0.04), 7,
                                      "neighbors_series.png", "n_neighbors series (init=spectral, seed=42)"),
    }
    log["plot_seconds"] = round(time.perf_counter() - t0, 1)

    metrics["settings"] = {
        "eval_sample": EVAL_SAMPLE, "eval_sample_seed": SEED, "neighbor_k": NEIGHBOR_K, "knn_label_k": KNN_K,
        "centroid": "per-cuisine median of 2-d coordinates", "reference": REF,
        "n_recipes_used": int(len(X)), "labels_no_overlap": log["labels_no_overlap"],
    }
    log["total_seconds"] = round(time.perf_counter() - t_all, 1)
    metrics["seconds"] = {"prep": log["prep_seconds"], "plot": log["plot_seconds"], "total": log["total_seconds"]}
    (OUT / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")

    M, N, W = metrics["conditions"], metrics["null_label_shuffle"], metrics["within_group_pairwise"]
    def table(keys):
      rows = ["| 条件 | 当てた点 | Procrustes 残差（対 図1） | 重心距離の順位相関（対 図1） | 重心距離の順位相関（対 100 次元） "
            "| 近傍保持率 (k=30) | 2D 10-NN 国籍一致率 | 所要時間 |",
            "|---|---|---|---|---|---|---|---|"]
      for key in keys:
        m = M[key]
        rows.append(f"| {m['title']} | {m['n_points']} | {m['procrustes_disparity_vs_ref']:.3f} "
                    f"| {m['spearman_centroid_dist_vs_ref']:.3f} | {m['spearman_centroid_dist_vs_100d_cosine']:.3f} "
                    f"| {m['neighbor_preservation_k30_sample']:.3f} | {m['knn_label_agreement_k10_2d_sample']:.3f} "
                    f"| {m['seconds']} 秒 |")
      return rows
    lines = [
        "# Exp-01 補足: UMAP の島どうしの配置は乱数の種・初期配置・近傍数で変わるか", "",
        "`uv run python experiments/exp-01/robustness.py` の最終実行時の記録。料理ベクトルは run.py と同じ関数・設定で作り直した。"
        "UMAP の共通設定は min_dist=0.1, metric=cosine（Exp-01 と同じ）。", "",
        "## 数値", "",
        "### 乱数の種・初期配置", "",
        *table([f"spectral_s{s}" for s in SEEDS] + [f"random_s{s}" for s in SEEDS]), "",
        "### 近傍数の系列（init=spectral, seed=42）", "",
        *table(SERIES_KEYS), "",
        f"- 基準 = n=30, spectral, seed=42（Exp-01 図1）。Exp-01 の `results/umap_2d.npy` と一致: {metrics['reference_matches_exp01_umap_2d_npy']}。"
        f"n=10 / 100 は計算し直し、projections.py の座標と一致: {metrics['matches_projections_npy']}",
        "- 重心 = 各国籍の 2 次元座標の中央値（20 点）。Procrustes 残差 = `scipy.spatial.procrustes` の disparity"
        "（両方を中心化・大きさ 1 に正規化し、回転・反転・拡大縮小で合わせた後の二乗残差の和。0 が完全一致、最大 1）",
        "- 重心距離の順位相関 = 20 重心の距離行列（上三角 190 対）どうしのスピアマン相関",
        "- 対 100 次元 = 100 次元の国籍重心（各次元の中央値）どうしのコサイン距離とのスピアマン相関（参考）",
        f"- 帰無分布（基準の重心に国籍ラベルをでたらめに付け直す、{N['n']} 回）: 残差 平均 {N['disparity_mean']:.3f}・"
        f"5 パーセント点 {N['disparity_p05']:.3f}・最小 {N['disparity_min']:.3f} / 順位相関 平均 {N['spearman_mean']:.3f}・"
        f"95 パーセント点 {N['spearman_p95']:.3f}・最大 {N['spearman_max']:.3f}",
        f"- 種どうしの総当たり（{W['spectral_seeds']['pairs']} 対）: spectral 残差 平均 {W['spectral_seeds']['disparity_mean']:.3f}・"
        f"最大 {W['spectral_seeds']['disparity_max']:.3f}、順位相関 平均 {W['spectral_seeds']['spearman_mean']:.3f}・"
        f"最小 {W['spectral_seeds']['spearman_min']:.3f} / random 残差 平均 {W['random_seeds']['disparity_mean']:.3f}・"
        f"最大 {W['random_seeds']['disparity_max']:.3f}、順位相関 平均 {W['random_seeds']['spearman_mean']:.3f}・"
        f"最小 {W['random_seeds']['spearman_min']:.3f}",
        f"- 近傍保持率・国籍一致率は {EVAL_SAMPLE} 件サンプル（seed={SEED}、projections.py と同じ引き方）の中で計算した。"
        f"近傍保持率 = 100 次元（cosine）の近傍 {NEIGHBOR_K} 件のうち 2 次元でも近傍 {NEIGHBOR_K} 件に入る割合。"
        f"国籍一致率 = 2 次元の近傍 {KNN_K} 件のうち同じ cuisine の割合（同じサンプル内の 100 次元の値: {ref100_agree:.3f}）。"
        "サンプル内で近傍を取るので projections.py の全件の値とは直接比べられない",
        "- n=5000 は全件（39,772 件）では近傍グラフと最適化が重いため、上の 10,000 件サンプルだけに UMAP を当てた。"
        "サンプルにしたこと自体の影響を分けるため、同じサンプルに n=30, spectral, seed=42 を当てた対照を置いた。"
        "サンプル条件の重心はサンプル内の点だけで取り、全件で取った図1の重心と比べている",
        "", "## 図", "",
        "- `grid.png`: 乱数の種・初期配置の 10 条件と n=1000 / 5000 / 対照の計 13 条件を cuisine 色分け（配色は図1と同じ tab20・件数順）。**表示のためだけに**各パネルを 20 重心の Procrustes"
        "（相似変換）で基準の向きに合わせた。数値は整列前の座標から計算。重心ラベルは重ならないよう押し離し、動かしたものは細線で結ぶ"
        f"（重なり解消に成功: {log['labels_no_overlap']}）",
        "- `neighbors_series.png`: 近傍数の系列 5, 10, 30, 100, 500, 1000, 5000（サンプル）と対照。体裁は grid.png と同じ",
        "- 各条件の 20 重心の座標は `metrics.json` の `centroids_2d`（整列前）",
        "", "## 環境・所要時間", "",
        f"- Python {platform.python_version()} / umap-learn {umap.__version__}, scikit-learn {sklearn.__version__}, "
        f"scipy {scipy.__version__}, numpy {np.__version__}, matplotlib {matplotlib.__version__}",
        f"- 前処理 + word2vec 学習 + 料理ベクトル: {log['prep_seconds']} 秒",
        "- 各条件の UMAP 所要時間は上の表",
        f"- 描画: {log['plot_seconds']} 秒 / 全体: {log['total_seconds']} 秒",
        "",
    ]
    (OUT / "summary.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
