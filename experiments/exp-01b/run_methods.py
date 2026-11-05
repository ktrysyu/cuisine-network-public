"""Exp-01b 追加: 国籍方向の求め方を 3 通りで比べる（LDA / 重心差 / INLP）。

実行: リポジトリ直下で `uv run python experiments/exp-01b/run_methods.py`

背景: run.py の LDA 方向（scalings_ を QR で正規直交化）は 19 本除いても食材ベクトルの 22% しか
取れず、除去後の空間で LDA を学習し直すと 61% 国籍を当てられた。LDA の方向は
「クラス内分散で割った判別方向」で、国籍重心が実際に離れているユークリッド方向と一致しない
可能性がある。それを確かめるため、次の方法を同じ評価で並べる。

- lda:      run.py と同じ（k = 1, 3, 5, 10, 19）
- centroid: cuisine ごとの料理ベクトル重心（20 個）から全料理の平均を引いた 20×100 行列を SVD し、
            右特異ベクトル上位 k 本（k = 1, 3, 5, 10, 19。行列の階数は 19）
- inlp1:    INLP。ロジスティック回帰で国籍を学習 → 係数行列の第 1 右特異ベクトル 1 本だけ除去 →
            除去後の空間で学習し直す、を 30 反復（1 反復 1 本）。1, 3, 5, 10, 19, 30 反復目を評価
- inlp:     INLP の標準形（Ravfogel et al. 2020）。1 反復で係数行列の行空間（階数 19）を丸ごと除去。
            dev 精度が最多クラス率 + INLP_STOP_MARGIN 以下になるか、次元が尽きるか、INLP_MAX_ITERS で止める。
            全反復を評価

除去の仕方・料理ベクトルの作り直し・評価指標はすべて run.py と同じ関数を使う。
run.py とその results/ 直下のファイルは読むだけで書き換えない。成果物は results/methods/ に置く。
"""

from __future__ import annotations

import collections
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
K_VALUES = [1, 3, 5, 10, 19]            # lda / centroid の本数（run.py と同じ。0 は共通の基準列）
INLP1_ITERS = 30                        # inlp1 の反復数（1 反復 1 本）
INLP1_EVAL = [1, 3, 5, 10, 19, 30]      # inlp1 で全指標を計算する反復
INLP_MAX_ITERS = 30                     # inlp（1 反復で行空間ごと除去）の上限
INLP_STOP_MARGIN = 0.02                 # dev 精度 <= 最多クラス率 + これ で停止
INLP_DEV_SIZE = 0.2                     # INLP の分類器の学習/評価分割（層化、SEED 固定）
LR_PARAMS = dict(C=10.0, max_iter=2000)  # sklearn LogisticRegression（多クラスは multinomial、lbfgs）
RANK_TOL = 1e-3                         # 係数行列の階数判定（最大特異値に対する比）。多クラス LR の係数はクラス和が 0 で階数 19 のはずだが、最適化の残差で 20 本目が小さく残るため

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "methods"


def load_base():
    spec = importlib.util.spec_from_file_location("exp01b_run", HERE / "run.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


B = load_base()   # run.py（main は実行されない）
E1 = B.E1         # Exp-01 の run.py
unit = B.unit


# ---------------------------------------------------------------------------
# 方向の求め方
# ---------------------------------------------------------------------------
def orth_append(Q, V, tol=1e-6):
    """既存の正規直交基底 Q（d×m か None）に V（d×r）の列を足し、正規直交化して返す。"""
    if Q is not None:
        V = V - Q @ (Q.T @ V)
    U, s, _ = np.linalg.svd(V, full_matrices=False)
    U = U[:, s > tol * max(s.max(), 1e-12)] if s.size else U[:, :0]
    return U if Q is None else np.hstack([Q, U])


def lda_basis(X0, y, n):
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

    lda = LinearDiscriminantAnalysis(**B.LDA_PARAMS).fit(X0, y)
    Q, _ = np.linalg.qr(lda.scalings_[:, :n])
    return Q


def centroid_basis(X0, y, n_classes):
    C = np.stack([X0[y == c].mean(axis=0) for c in range(n_classes)])
    M = C - X0.mean(axis=0)
    _, s, Vt = np.linalg.svd(M, full_matrices=False)
    rank = int((s > RANK_TOL * s[0]).sum())
    return Vt[:rank].T, s, M


def lr_fit(X, y, tr, dv):
    from sklearn.linear_model import LogisticRegression

    clf = LogisticRegression(random_state=SEED, **LR_PARAMS).fit(X[tr], y[tr])
    return clf, float(clf.score(X[dv], y[dv]))


def coef_rowspace(clf, Q):
    """係数行列の行空間（既に除いた部分空間 Q の成分は落とす）。特異値の降順。"""
    Wc = clf.coef_.T.astype(np.float64)          # d × classes
    if Q is not None:
        Wc = Wc - Q @ (Q.T @ Wc)
    U, s, _ = np.linalg.svd(Wc, full_matrices=False)
    rank = int((s > RANK_TOL * s[0]).sum())
    return U[:, :rank], s[:rank]


def knn_agreement(X, y):
    nbr = B.knn(X, E1.KNN_K)
    return float((y[nbr] == y[:, None]).mean())


# ---------------------------------------------------------------------------
# 1 つの部分空間を評価（run.py の k ループの中身と同じ）
# ---------------------------------------------------------------------------
def evaluate(Q, W0, wv, recs_idx, recs, labels, y, dessert, cuisines, tags, queries):
    W = B.remove_subspace(W0, Q)
    X = B.dish_vectors(W, recs_idx)
    cent = {c: unit(X[labels == c].mean(axis=0)) for c in cuisines}
    sm = B.space_metrics(X, y, dessert, cuisines)
    if Q is not None:
        sm["n_directions_removed"] = int(Q.shape[1])
        sm["ingredient_norm_share_removed"] = round(float(((W0 @ Q) ** 2).sum(axis=1).mean()), 4)
        sm["dish_residual_in_removed_subspace"] = float(np.abs(X @ Q).max())
    ar, mi = B.arithmetic_for_k(W, wv, cent, tags)
    ax = B.axes_for_k(X, W, wv, labels, cuisines, cent)
    cr = B.cross_for_k(X, recs, labels, queries)
    n_jp = int((labels == "japanese").sum())
    cnts = np.array(list(cr["nn_cuisine_counts"].values())) / n_jp
    cr["korean_chinese_share"] = round((cr["nn_cuisine_counts"].get("korean", 0)
                                        + cr["nn_cuisine_counts"].get("chinese", 0)) / n_jp, 4)
    cr["entropy_bits"] = round(float(-(cnts * np.log2(cnts)).sum()), 3)
    return {"space": sm, "arith": ar, "mirin": mi, "axes": ax, "cross": cr}


def subspace_diag(Q, M, Sigma):
    """部分空間 Q が (a) 重心差行列 M の二乗ノルム、(b) 料理ベクトルの全分散 のうち何割を含むか。"""
    return {
        "centroid_scatter_share": round(float(np.linalg.norm(M @ Q) ** 2 / np.linalg.norm(M) ** 2), 4),
        "dish_variance_share": round(float(np.trace(Q.T @ Sigma @ Q) / np.trace(Sigma)), 4),
    }


def overlap(A, Bq):
    """2 つの部分空間の重なり: 主角の cos² の平均（= ||AᵀB||_F² / min(dim)）。1 で一方が他方に含まれる。"""
    return round(float(np.linalg.norm(A.T @ Bq) ** 2 / min(A.shape[1], Bq.shape[1])), 4)


# ---------------------------------------------------------------------------
# 書き出し
# ---------------------------------------------------------------------------
METHOD_NAMES = {
    "lda": "LDA（run.py と同じ）",
    "centroid": "重心差 SVD",
    "inlp1": "INLP（1 反復 1 本）",
    "inlp": "INLP（1 反復で係数行列の行空間を除去）",
}


def cols_for(method, configs):
    """その方法の列（基準列 k=0 を先頭に）。"""
    return [("base", "k=0")] + [(cid, c["col"]) for cid, c in configs.items() if c["method"] == method]


def table_head(cols, first="#"):
    return [f"| {first} | " + " | ".join(lab for _, lab in cols) + " |", "|---" + "|---" * len(cols) + "|"]


def write_summary(res, configs, diag, traces, lda_ref):
    L = ["# Exp-01b 追加: 方向の求め方の比較（主要指標）", "",
         "- 方法の定義は run_methods.py の docstring と run_log.md。k = 取り除いた本数。k=0 は Exp-01 そのままの空間",
         "- 指標は run.py と同じ関数で計算（10-NN 国籍一致率、シルエット、除去後に LDA を学習し直した 5-fold 精度、"
         "製菓レシピの 10-NN 製菓一致率、食材ベクトルから取り除いた二乗ノルムの割合）",
         "- 「重心差の割合」= cuisine 重心 − 全体平均 の 20×100 行列の二乗ノルムのうち、除去した部分空間に入る割合。"
         "「料理分散の割合」= k=0 の料理ベクトルの全分散のうち、除去した部分空間に入る割合",
         "- 和食最近傍 K+C = japanese レシピの「他 cuisine 最近傍」が korean か chinese である割合",
         "- 醤油↔バター ρ = soy sauce↔butter 軸の cuisine 平均の並びの k=0 との順位相関。η² = その軸の射影値の分散のうち cuisine で説明される割合",
         "", "## 表", "",
         "| 方法 | k | 10-NN 一致率 | シルエット | LDA 再学習精度 | 製菓 10-NN | 食材から除いた割合 | 重心差の割合 | 料理分散の割合 | 和食最近傍 K+C | 醤油↔バター ρ | 醤油↔バター η² |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    order = [("base", None)] + [(cid, c) for cid, c in configs.items()]
    for cid, c in order:
        s = res[cid]["space"]
        ax = res[cid]["axes"]["soy sauce ↔ butter"]
        d = diag.get(cid, {"centroid_scatter_share": 0.0, "dish_variance_share": 0.0})
        name = "—" if c is None else METHOD_NAMES[c["method"]]
        k = "0" if c is None else c["col"]
        L.append(f"| {name} | {k} | {s['knn_label_agreement']:.3f} | {s['silhouette_100d_cosine']['mean']:+.3f} | "
                 f"{s['lda_refit_cv_accuracy']['mean']:.3f} | {s['dessert_knn_agreement']:.3f} | "
                 f"{s.get('ingredient_norm_share_removed', 0.0):.3f} | {d['centroid_scatter_share']:.3f} | "
                 f"{d['dish_variance_share']:.3f} | {res[cid]['cross']['korean_chinese_share']:.3f} | "
                 f"{ax['spearman_vs_k0']:+.2f} | {ax['eta2_cuisine']:.3f} |")
    base = res["base"]["space"]
    L += ["", f"偶然の 10-NN 一致率（ラベル比の二乗和）: {base['knn_label_agreement_chance']:.3f}。"
          f"製菓の偶然値（製菓レシピの割合）: {base['dessert_share_chance']:.3f}。",
          "", "run.py の結果との一致（lda 列を run.py の metrics.json と照合）: " +
          ", ".join(f"k={k} {'一致' if ok else '不一致'}" for k, ok in lda_ref.items()), ""]

    L += ["## 部分空間どうしの重なり", "",
          "主角の cos² の平均（1 = 小さい方が大きい方に含まれる、0 = 直交）。", "",
          "| | " + " | ".join(diag["_overlap_cols"]) + " |", "|---" + "|---" * len(diag["_overlap_cols"]) + "|"]
    for r, row in zip(diag["_overlap_cols"], diag["_overlap"]):
        L.append(f"| {r} | " + " | ".join(f"{v:.3f}" for v in row) + " |")
    L.append("")

    L += ["## 重心差 SVD の特異値", "",
          "20×100 行列（cuisine 重心 − 全体平均）の特異値の二乗の累積割合（上位 k 本で重心差の何割か）。", "",
          "| k | " + " | ".join(str(k) for k in K_VALUES) + " |", "|---" + "|---" * len(K_VALUES) + "|",
          "| 累積割合 | " + " | ".join(f"{diag['_centroid_cum'][k-1]:.3f}" for k in K_VALUES) + " |", ""]

    for m in ("inlp1", "inlp"):
        tr = traces[m]
        L += [f"## {METHOD_NAMES[m]} の反復ごとの記録", "",
              "dev 精度 = その反復で方向を求めたロジスティック回帰の dev 精度（除去**前**の空間）。"
              "10-NN 一致率は除去**後**の空間。"
              f"最多クラス率 {tr['majority_rate']:.3f}、停止条件 {tr['stop_rule']}", "",
              "| 反復 | この反復で除いた本数 | 累計本数 | dev 精度（除去前） | 10-NN 一致率（除去後） | 食材から除いた割合（累計） |",
              "|---|---|---|---|---|---|"]
        for it in tr["iters"]:
            L.append(f"| {it['iter']} | {it['n_removed']} | {it['total_removed']} | {it['dev_acc_before']:.3f} | "
                     f"{it['knn_after']:.3f} | {it['ingredient_norm_share_removed']:.3f} |")
        L += ["", f"停止理由: {tr['stopped_because']}", ""]
    (OUT / "summary.md").write_text("\n".join(L))


def write_arithmetic(res, configs, tags):
    L = ["# Exp-01b 追加: 食材の足し引き（方法 × k）", "",
         "- 形式は results/arithmetic.md と同じ。`[xxx]` はその食材を含むレシピで cuisine xxx が偶然の 3 倍以上多いことを示す印",
         "- `cuisine:xxx` はその空間で計算し直した cuisine 重心", ""]
    methods = list(METHOD_NAMES)
    L += ["## mirin の近傍（除去後）", ""]
    for m in methods:
        cols = cols_for(m, configs)
        L += [f"### {METHOD_NAMES[m]}", ""] + table_head(cols)
        for r in range(B.MIRIN_NEIGHBORS_K):
            L.append(f"| {r+1} | " + " | ".join(B.tag(res[cid]["mirin"][r][0], tags) for cid, _ in cols) + " |")
        L.append("")
    for desc, *_ in E1.ARITHMETIC:
        L += [f"## {desc}", ""]
        for m in methods:
            cols = cols_for(m, configs)
            L += [f"### {METHOD_NAMES[m]}", ""] + table_head(cols)
            for r in range(B.ARITH_TOP_K):
                L.append(f"| {r+1} | " + " | ".join(
                    f"{B.tag(res[cid]['arith'][desc]['top'][r][0], tags)} ({res[cid]['arith'][desc]['top'][r][1]:.2f})"
                    for cid, _ in cols) + " |")
            L.append("| − 側 cuisine の印が付いた数 | " + " | ".join(
                str(res[cid]["arith"][desc]["n_tagged_with_negative_cuisine"]) for cid, _ in cols) + " |")
            L.append("| 「+ 側だけ」上位8との重なり | " + " | ".join(
                str(res[cid]["arith"][desc]["overlap_with_plus_only"]) for cid, _ in cols) + " |")
            L.append("")
    (OUT / "arithmetic.md").write_text("\n".join(L))


def write_axes(res, configs):
    L = ["# Exp-01b 追加: 軸への射影（方法 × k）", "",
         "- 形式は results/axes.md と同じ。セルは「cuisine (平均射影値)」。上 = 左側の極寄り", ""]
    for name in res["base"]["axes"]:
        L += [f"## {name}", ""]
        for m in METHOD_NAMES:
            cols = cols_for(m, configs)
            L += [f"### {METHOD_NAMES[m]}", ""] + table_head(cols, "順")
            orders = {cid: list(res[cid]["axes"][name]["cuisine_mean_projection"].items()) for cid, _ in cols}
            for r in range(len(orders["base"])):
                L.append(f"| {r+1} | " + " | ".join(
                    f"{orders[cid][r][0]} ({orders[cid][r][1]:+.3f})" for cid, _ in cols) + " |")
            for lab, key, fmt in [("η²", "eta2_cuisine", "{:.3f}"), ("射影値の標準偏差", "projection_std", "{:.3f}"),
                                  ("k=0 の並びとの順位相関", "spearman_vs_k0", "{:+.2f}")]:
                L.append(f"| {lab} | " + " | ".join(fmt.format(res[cid]["axes"][name][key]) for cid, _ in cols) + " |")
            L.append("")
            for side, key in [("左の極側", "pos_ingredients"), ("右の極側", "neg_ingredients")]:
                L += [f"食材の{side}（上位 {B.AXIS_TOP_N}）", ""]
                for cid, lab in cols:
                    L.append(f"- {lab}: " + ", ".join(f"{t} ({v:+.2f})" for t, v in res[cid]["axes"][name][key]))
                L.append("")
    (OUT / "axes.md").write_text("\n".join(L))


def write_cross(res, configs, recs, queries, labels):
    other_n = int((labels != "japanese").sum())
    base = collections.Counter(labels[labels != "japanese"])
    n_jp = int((labels == "japanese").sum())
    cu_order = list(res["base"]["cross"]["nn_cuisine_counts"].keys())
    cu_order += sorted(c for c in base if c not in cu_order)
    L = ["# Exp-01b 追加: japanese レシピの他 cuisine 最近傍（方法 × k）", "",
         "- 形式は results/cross_cultural.md と同じ。料理ベクトルはその空間の食材ベクトルから作り直す", "",
         f"## 集計: japanese 全 {n_jp} 件の「他 cuisine 最近傍」の割合", ""]
    for m in METHOD_NAMES:
        cols = cols_for(m, configs)
        L += [f"### {METHOD_NAMES[m]}", "",
              "| cuisine | 候補中の割合 | " + " | ".join(lab for _, lab in cols) + " |",
              "|---|---" + "|---" * len(cols) + "|"]
        for c in cu_order:
            L.append(f"| {c} | {base[c]/other_n:.3f} | " + " | ".join(
                f"{res[cid]['cross']['nn_cuisine_counts'].get(c, 0)/n_jp:.3f}" for cid, _ in cols) + " |")
        L.append("| korean+chinese | " + f"{(base['korean']+base['chinese'])/other_n:.3f} | " + " | ".join(
            f"{res[cid]['cross']['korean_chinese_share']:.3f}" for cid, _ in cols) + " |")
        L.append("| 分布のエントロピー (bit) | — | " + " | ".join(
            f"{res[cid]['cross']['entropy_bits']:.2f}" for cid, _ in cols) + " |")
        L.append("")
    L += ["## クエリごとの上位 5（cuisine と cos）", ""]
    for desc, i in queries:
        r = recs[i]
        L += [f"### {desc}: id {r['id']}", "", f"食材: {', '.join(r['ingredients'])}", ""]
        for m in METHOD_NAMES:
            cols = cols_for(m, configs)
            L += [f"{METHOD_NAMES[m]}", ""] + table_head(cols)
            for rank in range(E1.CROSS_TOP_K):
                L.append(f"| {rank+1} | " + " | ".join(
                    f"{res[cid]['cross']['queries'][r['id']][rank][1]} ({res[cid]['cross']['queries'][r['id']][rank][2]:.2f})"
                    for cid, _ in cols) + " |")
            L.append("")
    (OUT / "cross_cultural.md").write_text("\n".join(L))


# ---------------------------------------------------------------------------
def main():
    import gensim, sklearn, scipy
    from scipy.stats import spearmanr
    from sklearn.model_selection import train_test_split

    OUT.mkdir(parents=True, exist_ok=True)
    np.random.seed(SEED)
    log = {}
    t_all = time.perf_counter()

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
    dessert = np.array([sum(m in set(r["ingredients"]) for m in B.DESSERT_MARKERS) >= B.DESSERT_MIN_MARKERS
                        for r in recs])
    tags = B.culture_tags(recipes, cuisines)
    queries = B.cross_queries(recs, labels)
    W0 = unit(wv.vectors)
    X0 = B.dish_vectors(W0, recs_idx)
    Sigma = np.cov(X0.astype(np.float64), rowvar=False)
    ctx = (W0, wv, recs_idx, recs, labels, y, dessert, cuisines, tags, queries)

    configs = {}   # id -> {"method", "col", "Q"}
    bases = {}

    # --- LDA / 重心差 ---
    Q_lda = lda_basis(X0, y, len(cuisines) - 1)
    Q_cen, s_cen, M = centroid_basis(X0, y, len(cuisines))
    log["centroid_rank"] = int(Q_cen.shape[1])
    bases["LDA 19"] = Q_lda
    bases["重心差 19"] = Q_cen
    for k in K_VALUES:
        configs[f"lda_{k}"] = {"method": "lda", "col": f"k={k}", "Q": Q_lda[:, :k]}
    for k in K_VALUES:
        configs[f"centroid_{k}"] = {"method": "centroid", "col": f"k={k}", "Q": Q_cen[:, :k]}

    # --- INLP ---
    tr, dv = train_test_split(np.arange(len(y)), test_size=INLP_DEV_SIZE, random_state=SEED, stratify=y)
    majority = float(np.bincount(y[dv]).max() / len(dv))
    stop_acc = majority + INLP_STOP_MARGIN
    traces = {}

    # inlp1: 1 反復 1 本
    t0 = time.perf_counter()
    Q, it_log = None, []
    X = X0
    for it in range(1, INLP1_ITERS + 1):
        clf, acc = lr_fit(X, y, tr, dv)
        U, _ = coef_rowspace(clf, Q)
        Q = orth_append(Q, U[:, :1])
        X = B.dish_vectors(B.remove_subspace(W0, Q), recs_idx)
        it_log.append({"iter": it, "n_removed": 1, "total_removed": int(Q.shape[1]), "dev_acc_before": round(acc, 4),
                       "knn_after": round(knn_agreement(X, y), 4),
                       "ingredient_norm_share_removed": round(float(((W0 @ Q) ** 2).sum(axis=1).mean()), 4)})
        print(f"inlp1 it={it} acc_before={acc:.3f} knn_after={it_log[-1]['knn_after']:.3f}", flush=True)
        if it in INLP1_EVAL:
            configs[f"inlp1_{it}"] = {"method": "inlp1", "col": f"{it}反復 (k={Q.shape[1]})", "Q": Q.copy()}
        if it == 1:
            bases["INLP 1反復目の行空間 19"] = coef_rowspace(clf, None)[0]
    _, acc_end = lr_fit(X, y, tr, dv)
    traces["inlp1"] = {"iters": it_log, "majority_rate": majority, "stop_rule": f"{INLP1_ITERS} 反復で打ち切り（固定）",
                       "dev_acc_after_last": round(acc_end, 4),
                       "stopped_because": f"{INLP1_ITERS} 反復に達した。最後の除去後の dev 精度 {acc_end:.3f}"}
    bases["INLP1 30"] = Q
    log["inlp1_seconds"] = round(time.perf_counter() - t0, 1)

    # inlp: 1 反復で行空間ごと
    t0 = time.perf_counter()
    Q, it_log, X = None, [], X0
    stopped = None
    for it in range(1, INLP_MAX_ITERS + 1):
        clf, acc = lr_fit(X, y, tr, dv)
        if acc <= stop_acc:
            stopped = f"{it} 反復目の学習で dev 精度 {acc:.3f} ≤ {stop_acc:.3f}（最多クラス率 + {INLP_STOP_MARGIN}）。この反復では除去しない"
            break
        U, _ = coef_rowspace(clf, Q)
        if Q is not None and Q.shape[1] + U.shape[1] > X0.shape[1]:
            U = U[:, : X0.shape[1] - Q.shape[1]]
        if U.shape[1] == 0:
            stopped = f"{it} 反復目: 除ける次元が残っていない"
            break
        Q = orth_append(Q, U)
        X = B.dish_vectors(B.remove_subspace(W0, Q), recs_idx)
        it_log.append({"iter": it, "n_removed": int(U.shape[1]), "total_removed": int(Q.shape[1]),
                       "dev_acc_before": round(acc, 4), "knn_after": round(knn_agreement(X, y), 4),
                       "ingredient_norm_share_removed": round(float(((W0 @ Q) ** 2).sum(axis=1).mean()), 4)})
        print(f"inlp it={it} removed={U.shape[1]} total={Q.shape[1]} acc_before={acc:.3f} "
              f"knn_after={it_log[-1]['knn_after']:.3f}", flush=True)
        configs[f"inlp_{it}"] = {"method": "inlp", "col": f"{it}反復 (k={Q.shape[1]})", "Q": Q.copy()}
        if Q.shape[1] >= X0.shape[1]:
            stopped = f"{it} 反復目で {X0.shape[1]} 次元すべてを除いた"
            break
    if stopped is None:
        stopped = f"上限 {INLP_MAX_ITERS} 反復に達した"
    traces["inlp"] = {"iters": it_log, "majority_rate": majority,
                      "stop_rule": f"dev 精度 ≤ 最多クラス率 + {INLP_STOP_MARGIN}、全次元除去、または {INLP_MAX_ITERS} 反復",
                      "stopped_because": stopped}
    log["inlp_seconds"] = round(time.perf_counter() - t0, 1)

    # --- 部分空間の診断 ---
    diag = {cid: subspace_diag(c["Q"], M, Sigma) for cid, c in configs.items()}
    names = list(bases)
    diag["_overlap_cols"] = names
    diag["_overlap"] = [[overlap(bases[a], bases[b]) for b in names] for a in names]
    diag["_centroid_cum"] = [float(v) for v in np.cumsum(s_cen ** 2) / (s_cen ** 2).sum()]

    # --- 評価 ---
    res = {}
    t0 = time.perf_counter()
    res["base"] = evaluate(None, *ctx)
    log["base_seconds"] = round(time.perf_counter() - t0, 1)
    for cid, c in configs.items():
        t0 = time.perf_counter()
        res[cid] = evaluate(c["Q"], *ctx)
        log[f"{cid}_seconds"] = round(time.perf_counter() - t0, 1)
        s = res[cid]["space"]
        print(f"{cid}: knn={s['knn_label_agreement']} lda_cv={s['lda_refit_cv_accuracy']['mean']} "
              f"removed={s['ingredient_norm_share_removed']} ({log[f'{cid}_seconds']}s)", flush=True)

    for name in res["base"]["axes"]:
        base_m = res["base"]["axes"][name]["cuisine_mean_projection"]
        order = list(base_m)
        for cid in res:
            m = res[cid]["axes"][name]["cuisine_mean_projection"]
            res[cid]["axes"][name]["spearman_vs_k0"] = round(float(spearmanr(
                [m[c] for c in order], [base_m[c] for c in order]).statistic), 3)

    # run.py の LDA 結果と一致するか
    ref = json.loads((HERE / "results" / "metrics.json").read_text())
    lda_ref = {k: res[f"lda_{k}"]["space"]["knn_label_agreement"] == ref["by_k"][str(k)]["knn_label_agreement"]
               and res[f"lda_{k}"]["space"]["ingredient_norm_share_removed"]
               == ref["by_k"][str(k)]["ingredient_norm_share_removed"] for k in K_VALUES}
    log["base_matches_runpy_k0"] = res["base"]["space"]["knn_label_agreement"] == ref["by_k"]["0"]["knn_label_agreement"]

    write_summary(res, configs, diag, traces, lda_ref)
    write_arithmetic(res, configs, tags)
    write_axes(res, configs)
    write_cross(res, configs, recs, queries, labels)

    metrics = {
        "configs": {cid: {"method": c["method"], "label": c["col"], "n_directions": int(c["Q"].shape[1])}
                    for cid, c in configs.items()},
        "space": {cid: r["space"] for cid, r in res.items()},
        "subspace_diagnostics": {cid: v for cid, v in diag.items() if not cid.startswith("_")},
        "subspace_overlap": {"names": names, "matrix": diag["_overlap"]},
        "centroid_singular_values": [round(float(v), 6) for v in s_cen],
        "centroid_cumulative_share": [round(v, 4) for v in diag["_centroid_cum"]],
        "inlp_traces": traces,
        "lda_matches_runpy": {str(k): v for k, v in lda_ref.items()},
        "axes": {cid: r["axes"] for cid, r in res.items()},
        "cross_cultural": {cid: r["cross"] for cid, r in res.items()},
        "arithmetic": {cid: {d: {kk: vv for kk, vv in v.items() if not kk.startswith("_")}
                             for d, v in r["arith"].items()} for cid, r in res.items()},
        "mirin_neighbors": {cid: r["mirin"] for cid, r in res.items()},
    }
    (OUT / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")
    log["total_seconds"] = round(time.perf_counter() - t_all, 1)

    run_log = [
        "# Exp-01b 追加（方法の比較）実行ログ", "",
        "`uv run python experiments/exp-01b/run_methods.py` の最終実行時の記録。所要時間はマシン依存。", "",
        "## 環境",
        f"- Python {platform.python_version()} / {platform.platform()}",
        f"- gensim {gensim.__version__}, scikit-learn {sklearn.__version__}, numpy {np.__version__}, scipy {scipy.__version__}",
        "", "## 入力",
        f"- `data/raw/train.json` SHA-256 一致: {log['raw_sha256_matches']}",
        f"- 食材ベクトル: {log['vectors_source']}（vectors の SHA-256 `{log['vectors_sha256'][:16]}…`）",
        f"- 使用レシピ {len(recs)}、語彙 {len(wv)}",
        f"- k=0 の 10-NN 一致率が run.py の metrics.json と一致: {log['base_matches_runpy_k0']}",
        f"- lda 列（10-NN 一致率と除去割合）が run.py の metrics.json と一致: {lda_ref}",
        "", "## 方法",
        "- 共通: 方向はすべて k=0 の料理ベクトル（100 次元・単位長）から求め、run.py と同じ `remove_subspace` で"
        "単位長の食材ベクトルから部分空間の成分を引いて単位長に戻し、料理ベクトル・cuisine 重心を作り直す",
        f"- lda: run.py と同じ（LinearDiscriminantAnalysis({B.LDA_PARAMS}) の scalings_ 先頭 k 列を QR）",
        f"- centroid: cuisine ごとの料理ベクトルの平均（単位長にしない）20 個から全料理の平均を引いた 20×100 行列を SVD。"
        f"各 cuisine の行を等しく扱う（件数で重み付けしない）。階数 {log['centroid_rank']}。右特異ベクトル上位 k 本",
        f"- INLP 共通: 料理ベクトルを層化で学習 {1-INLP_DEV_SIZE:.0%} / dev {INLP_DEV_SIZE:.0%} に分け（random_state={SEED}）、"
        f"LogisticRegression({LR_PARAMS}, random_state={SEED}) を学習。係数行列（20×100）から、既に除いた部分空間の成分を落として SVD。"
        "除去後は食材ベクトルから料理ベクトルを作り直し、その上で学習し直す",
        f"- inlp1: 各反復で第 1 右特異ベクトル 1 本だけ除く。{INLP1_ITERS} 反復で打ち切り（19 本ずつ除く標準形だと 100 次元が約 5 反復で尽き、"
        f"k を 1, 3, 5, 10 と揃えられないため追加した変種）。評価は {INLP1_EVAL} 反復目",
        f"- inlp: 各反復で係数行列の行空間（階数 {RANK_TOL:g} 比で判定）を丸ごと除く。停止: 学習時の dev 精度 ≤ 最多クラス率"
        f"（{majority:.3f}）+ {INLP_STOP_MARGIN}、100 次元をすべて除いた、または {INLP_MAX_ITERS} 反復",
        "- 評価指標・足し引き・軸・和食最近傍は run.py の関数をそのまま呼ぶ。シルエット・交差検証の乱数も run.py と同じ",
        "- 部分空間の診断: 重心差行列の二乗ノルムのうち部分空間に入る割合、k=0 料理ベクトルの全分散のうち部分空間に入る割合、"
        "部分空間どうしの主角 cos² の平均",
        "", "## ハイパーパラメータ",
        f"- SEED = {SEED}, K_VALUES = {K_VALUES}, INLP1_ITERS = {INLP1_ITERS}, INLP1_EVAL = {INLP1_EVAL}, "
        f"INLP_MAX_ITERS = {INLP_MAX_ITERS}, INLP_STOP_MARGIN = {INLP_STOP_MARGIN}, INLP_DEV_SIZE = {INLP_DEV_SIZE}, "
        f"LR_PARAMS = {LR_PARAMS}, RANK_TOL = {RANK_TOL}",
        "- LR の C=10 は、k=0 の料理ベクトルで C ∈ {1, 10, 100} を dev 精度で比べて選んだ（0.742 / 0.749 / 0.747）",
        "", "## 所要時間",
        f"- INLP 方向探索: inlp1 {log['inlp1_seconds']} 秒, inlp {log['inlp_seconds']} 秒",
        "- 評価: " + ", ".join(f"{k.removesuffix('_seconds')} {v} 秒" for k, v in log.items()
                              if k.endswith("_seconds") and k not in ("inlp1_seconds", "inlp_seconds", "total_seconds")),
        f"- 全体: {log['total_seconds']} 秒", "",
    ]
    (OUT / "run_log.md").write_text("\n".join(run_log))
    print("\n".join(run_log))


if __name__ == "__main__":
    main()
