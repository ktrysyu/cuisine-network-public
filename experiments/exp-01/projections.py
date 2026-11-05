"""Exp-01 補足: 100 次元の料理ベクトルを 2 次元に押しつぶす方法を 4 通り比べる。

実行: リポジトリ直下で `uv run python experiments/exp-01/projections.py`

- 料理ベクトルは run.py と同じ関数・同じ設定（SEED=42, word2vec 100 次元）で作り直す
- run.py の成果物（results/ 直下）には書き込まない。出力は results/projections/ だけ
  （ただし run.py の関数が data/processed/ の前処理 TSV と word2vec モデルを同じ内容で上書きする）
- 手法: PCA(2) / UMAP n_neighbors=10, 30, 100（他の設定は Exp-01 と同じ）
"""

from __future__ import annotations

import importlib.util
import json
import platform
import re
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("exp01_run", HERE / "run.py")
run = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(run)

SEED = run.SEED
OUT = run.RESULTS / "projections"

METHODS = [
    # (key, パネルタイトル, 設定)
    ("pca", "PCA (2 components)", None),
    ("umap_n10", "UMAP n_neighbors=10", 10),
    ("umap_n30", "UMAP n_neighbors=30 (= Exp-01 Fig. 1)", 30),
    ("umap_n100", "UMAP n_neighbors=100", 100),
]
EVAL_SAMPLE = 10000
NEIGHBOR_K = 30       # 近傍保持率・trustworthiness の k
KNN_K = run.KNN_K     # 国籍一致率の k（=10, Exp-01 と同じ）

# 菓子判定: 3 カテゴリのうち 2 つ以上を含むレシピ
SWEETS_MIN_CATEGORIES = 2
SUGAR_EXCLUDE = re.compile(r"pea|pumpkin|snap|free|substitute|cane$")
FLOUR_EXCLUDE = re.compile(
    r"tortilla|rice|corn|chickpea|gram|tapioca|almond|buckwheat|coconut|manioc|potato|cassava|masa|besan"
    r"|oat|soy|millet|sorghum|teff|arrowroot|quinoa|peanut|banana|chestnut|fava|lentil|urad|acorn|hazelnut"
    r"|glutinous|mochiko|sweet rice|bean|plantain|sago|kuzu|water chestnut|arepa|rye|barley|gluten.free")


def sweets_categories(tok: str) -> set[str]:
    """食材トークン → 該当カテゴリ（sugar / flour / vanilla）。
    sugar: 語 "sugar" を含む甘味料（sugar snap peas・sugar pumpkin 等は除く）
    flour: 語 "flour" を含む小麦系の粉（flour tortillas・米粉・コーン粉・豆粉等は除く）
    vanilla: "vanilla" を含むもの全部（vanilla ice cream 等も含む）"""
    cats = set()
    if re.search(r"\bsugars?\b", tok) and not SUGAR_EXCLUDE.search(tok):
        cats.add("sugar")
    if re.search(r"flour", tok) and not FLOUR_EXCLUDE.search(tok):
        cats.add("flour")
    if "vanilla" in tok:
        cats.add("vanilla")
    return cats


# ---------------------------------------------------------------------------
def project_all(X, log):
    import umap
    from sklearn.decomposition import PCA

    Ys, info = {}, {}
    for key, _, nn in METHODS:
        t0 = time.perf_counter()
        if key == "pca":
            p = PCA(n_components=2, random_state=SEED)
            Y = p.fit_transform(X)
            info[key] = {"explained_variance_ratio": [round(float(v), 4) for v in p.explained_variance_ratio_],
                         "explained_variance_ratio_sum": round(float(p.explained_variance_ratio_.sum()), 4)}
        else:
            params = dict(run.UMAP_PARAMS, n_neighbors=nn)
            Y = umap.UMAP(**params).fit_transform(X)
            info[key] = {"params": params}
        Ys[key] = Y.astype(np.float32)
        log[f"{key}_seconds"] = round(time.perf_counter() - t0, 1)
        print(f"[{key}] {log[f'{key}_seconds']} s")
    return Ys, info


def evaluate(X, Ys, y, sweet, metrics):
    from sklearn.manifold import trustworthiness
    from sklearn.neighbors import NearestNeighbors

    rng = np.random.default_rng(SEED)
    idx = np.sort(rng.choice(len(X), size=EVAL_SAMPLE, replace=False))
    Xs = X[idx]
    _, nb_hi = NearestNeighbors(n_neighbors=NEIGHBOR_K + 1, metric="cosine").fit(Xs).kneighbors(Xs)
    nb_hi = nb_hi[:, 1:]

    def knn(Z, metric):
        _, nb = NearestNeighbors(n_neighbors=KNN_K + 1, metric=metric).fit(Z).kneighbors(Z)
        return nb[:, 1:]

    def agree(nb):
        return round(float((y[nb] == y[:, None]).mean()), 4)

    def sweet_purity(nb):
        return round(float(sweet[nb[sweet]].mean()), 4)

    nb100 = knn(X, "cosine")
    metrics["reference_100d"] = {
        "knn_label_agreement_k10": agree(nb100),
        "sweets_knn_purity_k10": sweet_purity(nb100),
        "chance_sum_p_squared": round(float(((np.bincount(y) / len(y)) ** 2).sum()), 4),
        "sweets_share": round(float(sweet.mean()), 4),
    }
    for key, *_ in METHODS:
        Y = Ys[key]
        Ysmp = Y[idx]
        _, nb_lo = NearestNeighbors(n_neighbors=NEIGHBOR_K + 1).fit(Ysmp).kneighbors(Ysmp)
        nb_lo = nb_lo[:, 1:]
        keep = np.mean([len(set(a) & set(b)) / NEIGHBOR_K for a, b in zip(nb_hi, nb_lo)])
        tw = trustworthiness(Xs, Ysmp, n_neighbors=NEIGHBOR_K, metric="cosine")
        nb2 = knn(Y, "euclidean")
        metrics["methods"][key].update({
            "neighbor_preservation_k30_sample": round(float(keep), 4),
            "trustworthiness_k30_sample": round(float(tw), 4),
            "knn_label_agreement_k10_2d": agree(nb2),
            "sweets_knn_purity_k10_2d": sweet_purity(nb2),
        })
        print(f"[{key}] eval done")


# ---------------------------------------------------------------------------
def place_labels(ax, fig, anchors, texts, kw_list, iters=400):
    """重心ラベルを置き、文字枠が重ならないよう表示座標上で少しずつ押し離す。
    動かしたラベルには元の重心への細い引き出し線を付ける。"""
    objs = [ax.text(a[0], a[1], t, ha="center", va="center", zorder=5, **kw)
            for a, t, kw in zip(anchors, texts, kw_list)]
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    to_disp, to_data = ax.transData, ax.transData.inverted()
    pos = to_disp.transform(np.asarray(anchors))
    home = pos.copy()
    wh = np.array([[b.width, b.height] for b in (o.get_window_extent(r) for o in objs)]) + 4
    for _ in range(iters):
        moved = False
        for i in range(len(objs)):
            for j in range(i + 1, len(objs)):
                d = pos[j] - pos[i]
                ox = (wh[i, 0] + wh[j, 0]) / 2 - abs(d[0])
                oy = (wh[i, 1] + wh[j, 1]) / 2 - abs(d[1])
                if ox > 0 and oy > 0:
                    moved = True
                    if oy < ox:  # 縦に離す方が近い
                        s = np.sign(d[1]) or (1 if j % 2 else -1)
                        pos[i, 1] -= s * (oy / 2 + 0.5); pos[j, 1] += s * (oy / 2 + 0.5)
                    else:
                        s = np.sign(d[0]) or (1 if j % 2 else -1)
                        pos[i, 0] -= s * (ox / 2 + 0.5); pos[j, 0] += s * (ox / 2 + 0.5)
        if not moved:
            break
    for o, p, h in zip(objs, pos, home):
        o.set_position(to_data.transform(p))
        if np.hypot(*(p - h)) > 6:
            a, b = to_data.transform(h), to_data.transform(p)
            ax.plot([a[0], b[0]], [a[1], b[1]], color="#52514e", lw=0.6, zorder=4)
    return not moved


def style_ax(ax, title):
    ax.set_title(title, loc="left", color="#0b0b0b", fontsize=12)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_color("#e6e5e1")


def plot_compare(Ys, labels, cuisines, info, log):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    INK = "#0b0b0b"
    labels = np.asarray(labels)
    order = sorted(cuisines, key=lambda c: -(labels == c).sum())  # run.py の図1と同じ配色順
    cmap = plt.get_cmap("tab20")
    colors = np.array([cmap(order.index(c)) for c in labels])
    perm = np.random.default_rng(SEED).permutation(len(labels))

    fig, axes = plt.subplots(2, 2, figsize=(15.5, 13), dpi=130)  # 2015 x 1690 px
    for ax, (key, title, _) in zip(axes.ravel(), METHODS):
        Y = Ys[key]
        if key == "pca":
            ev = info[key]["explained_variance_ratio"]
            title += f" — explained variance {ev[0]:.1%} + {ev[1]:.1%}"
        ax.scatter(Y[perm, 0], Y[perm, 1], s=0.8, c=colors[perm], linewidths=0, alpha=0.6, rasterized=True)
        style_ax(ax, title)
        ax.set_xlim(ax.get_xlim()); ax.set_ylim(ax.get_ylim())
    handles = [plt.Line2D([], [], marker="o", ls="", color=cmap(i), label=f"{c} ({(labels == c).sum()})")
               for i, c in enumerate(order)]
    fig.legend(handles=handles, loc="center left", bbox_to_anchor=(0.86, 0.5), frameon=False, fontsize=9,
               labelcolor=INK, markerscale=1.2)
    fig.suptitle("Exp-01 supplement: the same 100-d dish vectors squashed to 2-d in four ways, colored by cuisine\n"
                 "labels at per-cuisine median (moved apart to avoid overlap; thin line = moved); "
                 "UMAP: min_dist=0.1, metric=cosine, random_state=42",
                 x=0.01, ha="left", color=INK, fontsize=12)
    fig.tight_layout(rect=(0, 0, 0.86, 0.96))
    no_overlap = {}
    for ax, (key, *_) in zip(axes.ravel(), METHODS):
        Y = Ys[key]
        anchors = [np.median(Y[labels == c], axis=0) for c in order]
        kws = [dict(fontsize=7.5, color=INK,
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=cmap(i), lw=1.1, alpha=0.88))
               for i in range(len(order))]
        no_overlap[key] = place_labels(ax, fig, anchors, order, kws)
    fig.savefig(OUT / "compare_2x2.png", metadata={"Software": None})
    plt.close(fig)
    log["labels_no_overlap"] = no_overlap


def plot_sweets(Ys, sweet):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    HI, BG = "#b3261e", "#d4d3cf"
    fig, axes = plt.subplots(2, 2, figsize=(15.5, 13), dpi=130)
    for ax, (key, title, _) in zip(axes.ravel(), METHODS):
        Y = Ys[key]
        ax.scatter(Y[~sweet, 0], Y[~sweet, 1], s=0.6, c=BG, linewidths=0, rasterized=True)
        ax.scatter(Y[sweet, 0], Y[sweet, 1], s=1.4, c=HI, linewidths=0, alpha=0.7, rasterized=True)
        style_ax(ax, title)
    fig.suptitle(f"Exp-01 supplement: recipes with ≥{SWEETS_MIN_CATEGORIES} of {{sugar, wheat flour, vanilla}} "
                 f"highlighted (n={sweet.sum()} / {len(sweet)}); others light gray",
                 x=0.01, ha="left", color="#0b0b0b", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(OUT / "sweets_2x2.png", metadata={"Software": None})
    plt.close(fig)


# ---------------------------------------------------------------------------
def main():
    import sklearn, umap, matplotlib

    OUT.mkdir(parents=True, exist_ok=True)
    log, metrics = {}, {"methods": {}}
    t_all = time.perf_counter()

    recipes = run.load_and_preprocess({})
    wv = run.train_word2vec(recipes, {})
    X, kept = run.dish_vectors(recipes, wv, {})
    recs = [recipes[i] for i in kept]
    labels = [r["cuisine"] for r in recs]
    cuisines = sorted(set(labels))
    y = np.array([cuisines.index(c) for c in labels])
    log["prep_seconds"] = round(time.perf_counter() - t_all, 1)

    cat_hits = [set().union(*[sweets_categories(t) for t in r["ingredients"]]) for r in recs]
    sweet = np.array([len(h) >= SWEETS_MIN_CATEGORIES for h in cat_hits])
    tok_matched = {c: sorted({t for r in recs for t in r["ingredients"] if c in sweets_categories(t)})
                   for c in ("sugar", "flour", "vanilla")}

    Ys, info = project_all(X, log)
    for key, title, _ in METHODS:
        metrics["methods"][key] = {"title": title, **info[key]}

    # n_neighbors=30 が Exp-01 の umap_2d.npy と一致するか
    ref = np.load(run.RESULTS / "umap_2d.npy")
    same = ref.shape == Ys["umap_n30"].shape and np.allclose(ref, Ys["umap_n30"], atol=1e-4)
    metrics["umap_n30_matches_exp01_umap_2d_npy"] = bool(same)
    metrics["umap_n30_max_abs_diff_vs_exp01"] = float(np.abs(ref - Ys["umap_n30"]).max()) if ref.shape == Ys["umap_n30"].shape else None

    t0 = time.perf_counter()
    evaluate(X, Ys, y, sweet, metrics)
    log["eval_seconds"] = round(time.perf_counter() - t0, 1)

    t0 = time.perf_counter()
    plot_compare(Ys, labels, cuisines, info, log)
    plot_sweets(Ys, sweet)
    log["plot_seconds"] = round(time.perf_counter() - t0, 1)
    for key, Y in Ys.items():
        np.save(OUT / f"{key}_2d.npy", Y)

    metrics["settings"] = {
        "eval_sample": EVAL_SAMPLE, "eval_sample_seed": SEED, "neighbor_k": NEIGHBOR_K, "knn_label_k": KNN_K,
        "sweets_rule": f">= {SWEETS_MIN_CATEGORIES} of sugar / flour / vanilla categories",
        "n_sweets": int(sweet.sum()), "n_recipes_used": len(recs),
        "labels_no_overlap": log["labels_no_overlap"],
    }
    (OUT / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")
    log["total_seconds"] = round(time.perf_counter() - t_all, 1)

    M, R = metrics["methods"], metrics["reference_100d"]
    rows = ["| 手法 | 近傍保持率 (k=30) | trustworthiness (k=30) | 10-NN 国籍一致率 | 菓子の 10-NN 菓子率 |",
            "|---|---|---|---|---|",
            f"| 100 次元（参考） | 1 | 1 | {R['knn_label_agreement_k10']:.3f} | {R['sweets_knn_purity_k10']:.3f} |"]
    for key, *_ in METHODS:
        m = M[key]
        rows.append(f"| {m['title']} | {m['neighbor_preservation_k30_sample']:.3f} | {m['trustworthiness_k30_sample']:.3f} "
                    f"| {m['knn_label_agreement_k10_2d']:.3f} | {m['sweets_knn_purity_k10_2d']:.3f} |")
    ev = M["pca"]["explained_variance_ratio"]
    lines = [
        "# Exp-01 補足: 100 次元 → 2 次元の押しつぶし方 4 通り", "",
        "`uv run python experiments/exp-01/projections.py` の最終実行時の記録。料理ベクトルは run.py と同じ関数・設定で作り直した。", "",
        "## 数値", "",
        *rows, "",
        f"- PCA の説明分散比: 第1成分 {ev[0]:.4f}, 第2成分 {ev[1]:.4f}（計 {sum(ev):.4f}）",
        f"- 近傍保持率 = 100 次元（cosine）での近傍 {NEIGHBOR_K} 件のうち、2 次元（ユークリッド）でも近傍 {NEIGHBOR_K} 件に入っている割合の平均。"
        f"{EVAL_SAMPLE} 件サンプル（seed={SEED}）内で近傍を取った",
        f"- trustworthiness = `sklearn.manifold.trustworthiness(n_neighbors={NEIGHBOR_K}, metric='cosine')`、同じ {EVAL_SAMPLE} 件サンプル",
        f"- 10-NN 国籍一致率 = 全 {len(recs)} 件で、各レシピの近傍 {KNN_K} 件（自分を除く）のうち同じ cuisine の割合。"
        f"100 次元の値は Exp-01 の metrics.json と同じ計算（偶然一致率 Σp² = {R['chance_sum_p_squared']:.3f}）",
        f"- 菓子の 10-NN 菓子率 = 菓子レシピの近傍 {KNN_K} 件のうち菓子レシピの割合（全体に占める菓子の割合 {R['sweets_share']:.3f}）",
        f"- UMAP n_neighbors=30 の座標が Exp-01 の `results/umap_2d.npy` と一致: {metrics['umap_n30_matches_exp01_umap_2d_npy']}"
        f"（最大絶対差 {metrics['umap_n30_max_abs_diff_vs_exp01']}）",
        "", "## 菓子レシピの定義", "",
        f"- sugar / flour / vanilla の 3 カテゴリのうち {SWEETS_MIN_CATEGORIES} つ以上を含むレシピ: {int(sweet.sum())} 件（{sweet.mean():.1%}）",
        "- カテゴリはトークン名で判定（`sweets_categories()`）。sugar は sugar snap peas 等を、flour は flour tortillas・米粉・コーン粉・豆粉等を除く。vanilla は vanilla ice cream 等も含む",
        f"- 該当トークン数: sugar {len(tok_matched['sugar'])}, flour {len(tok_matched['flour'])}, vanilla {len(tok_matched['vanilla'])}",
        f"  - flour: {', '.join(tok_matched['flour'])}",
        "", "## 図", "",
        "- `compare_2x2.png`: 4 通りを cuisine 色分け（配色は Exp-01 図1と同じ tab20・件数順）。重心ラベルは重ならないよう押し離し、動かしたものは細線で元の重心と結ぶ"
        f"（重なり解消に成功: {log['labels_no_overlap']}）",
        "- `sweets_2x2.png`: 菓子レシピを濃色、その他を薄い灰色",
        "- `*_2d.npy`: 各手法の 2 次元座標（行順は run.py の使用レシピ順）",
        "", "## 環境・所要時間", "",
        f"- Python {platform.python_version()} / umap-learn {umap.__version__}, scikit-learn {sklearn.__version__}, numpy {np.__version__}, matplotlib {matplotlib.__version__}",
        f"- 前処理 + word2vec 学習 + 料理ベクトル: {log['prep_seconds']} 秒",
        *[f"- {k}: {log[f'{k}_seconds']} 秒" for k, *_ in METHODS],
        f"- 評価指標: {log['eval_seconds']} 秒 / 描画: {log['plot_seconds']} 秒",
        f"- 全体: {log['total_seconds']} 秒",
        "",
    ]
    (OUT / "summary.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
