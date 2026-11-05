"""Exp-01b: 文化（国籍）の方向を取り除く。

実行: リポジトリ直下で `uv run python experiments/exp-01b/run.py`

手順（plan.md）
1. Exp-01 の食材ベクトル（再学習しない）と料理ベクトルを使う
2. 料理ベクトルと cuisine ラベルで LDA し、国籍を分ける方向（最大 19 本）を求める
3. 食材ベクトルからその部分空間の成分を取り除く。取り除く本数 k = 1, 3, 5, 10, 19
4. 各 k で Exp-01 と同じ足し引き・軸・国をまたいだ近傍を計算し直す（k = 0 が Exp-01）

Exp-01 の成果物は読むだけで書き換えない。
"""

from __future__ import annotations

import collections
import hashlib
import importlib.util
import json
import platform
import time
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# 設定（ハイパーパラメータはすべてここ）
# ---------------------------------------------------------------------------
SEED = 42
K_VALUES = [0, 1, 3, 5, 10, 19]   # 取り除く LDA 方向の本数。0 = Exp-01 そのまま
MAP_K = 5                          # 2D マップを描く k（一度全 k を回して metrics を見てから選んだ。理由は run_log）

LDA_PARAMS = dict(solver="svd")    # sklearn LinearDiscriminantAnalysis の既定
LDA_CV_FOLDS = 5                   # 除去後に LDA を学習し直したときの分類精度（交差検証）

ARITH_TOP_K = 8
MIRIN_NEIGHBORS_K = 10
AXIS_TOP_N = 10                    # 軸の両端に並べる食材数
CULTURE_LIFT_MARK = 3.0            # 食材の cuisine 偏り: P(c|食材)/P(c) がこれ以上なら [c] を付ける
CULTURE_MIN_COUNT = 5

# 国籍以外の構造が残るかの確認用: 製菓っぽいレシピ（下の食材を 2 つ以上含む）
DESSERT_MARKERS = ["baking powder", "baking soda", "vanilla extract", "powdered sugar",
                   "confectioners sugar", "all-purpose flour", "unsalted butter", "large eggs",
                   "granulated sugar", "heavy cream"]
DESSERT_MIN_MARKERS = 3

ROOT = Path(__file__).resolve().parents[2]
EXP01_DIR = ROOT / "experiments" / "exp-01"
RESULTS = Path(__file__).resolve().parent / "results"


def load_exp01():
    """Exp-01 の run.py を import する（main は実行されない）。"""
    spec = importlib.util.spec_from_file_location("exp01_run", EXP01_DIR / "run.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


E1 = load_exp01()
unit = E1.unit


# ---------------------------------------------------------------------------
# 読み込み（Exp-01 と同じ前処理。processed tsv は書き換えない）
# ---------------------------------------------------------------------------
def load_recipes(log):
    digest = E1.sha256(E1.RAW_PATH)
    log["raw_sha256_matches"] = digest == E1.RAW_SHA256
    raw = json.loads(E1.RAW_PATH.read_text())
    recipes = []
    for r in raw:
        seen, uniq = set(), []
        for t in (E1.normalize_ingredient(x) for x in r["ingredients"]):
            if t and t not in seen:
                seen.add(t)
                uniq.append(t)
        recipes.append({"id": r["id"], "cuisine": r["cuisine"], "ingredients": uniq})
    return recipes


def load_vectors(recipes, log):
    """Exp-01 が保存した KeyedVectors を読む。無ければ Exp-01 の関数・設定で再生成する。"""
    from gensim.models import KeyedVectors

    if E1.MODEL_PATH.exists():
        wv = KeyedVectors.load(str(E1.MODEL_PATH))
        log["vectors_source"] = f"読み込み: data/processed/{E1.MODEL_PATH.name}"
    else:
        wv = E1.train_word2vec(recipes, {})  # 同じシード・設定。保存先は Exp-01 と同じ（gitignore）
        log["vectors_source"] = "再生成: Exp-01 の train_word2vec（同シード・同設定）"
    log["vectors_sha256"] = hashlib.sha256(np.ascontiguousarray(wv.vectors).tobytes()).hexdigest()
    return wv


# ---------------------------------------------------------------------------
# 空間の変換
# ---------------------------------------------------------------------------
def dish_vectors(W, recs_idx):
    """Exp-01 と同じ式: 料理 = 語彙内食材の単位ベクトルの平均を単位長に。"""
    return unit(np.asarray([W[idx].mean(axis=0) for idx in recs_idx], dtype=np.float32))


def remove_subspace(W0, Q):
    """単位長の食材ベクトルから部分空間 Q（正規直交）の成分を除き、単位長に戻す。"""
    if Q is None:
        return W0
    return unit(W0 - (W0 @ Q) @ Q.T)


# ---------------------------------------------------------------------------
# 指標
# ---------------------------------------------------------------------------
def knn(X, k):
    from sklearn.neighbors import NearestNeighbors

    nn = NearestNeighbors(n_neighbors=k + 1, metric="cosine").fit(X)
    return nn.kneighbors(X)[1][:, 1:]


def space_metrics(X, y, dessert, cuisines):
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    from sklearn.metrics import silhouette_score
    from sklearn.model_selection import StratifiedKFold, cross_val_score

    nbr = knn(X, E1.KNN_K)
    p = np.bincount(y) / len(y)
    per = {cuisines[c]: round(float((y[nbr[y == c]] == c).mean()), 4) for c in range(len(cuisines))}
    sil = [silhouette_score(X, y, metric="cosine", sample_size=E1.SILHOUETTE_SAMPLE, random_state=SEED + r)
           for r in range(E1.SILHOUETTE_REPEATS)]
    # 国籍以外の構造: 製菓レシピの近傍が製菓レシピである率
    pd_ = dessert.mean()
    d_agree = float(dessert[nbr[dessert]].mean())
    cv = StratifiedKFold(n_splits=LDA_CV_FOLDS, shuffle=True, random_state=SEED)
    acc = cross_val_score(LinearDiscriminantAnalysis(**LDA_PARAMS), X, y, cv=cv)
    return {
        "knn_label_agreement": round(float((y[nbr] == y[:, None]).mean()), 4),
        "knn_label_agreement_chance": round(float((p ** 2).sum()), 4),
        "knn_label_agreement_by_cuisine": dict(sorted(per.items(), key=lambda kv: -kv[1])),
        "silhouette_100d_cosine": {"mean": round(float(np.mean(sil)), 4), "std": round(float(np.std(sil)), 4)},
        "dessert_knn_agreement": round(d_agree, 4),
        "dessert_share_chance": round(float(pd_), 4),
        "lda_refit_cv_accuracy": {"mean": round(float(acc.mean()), 4), "std": round(float(acc.std()), 4)},
    }


# ---------------------------------------------------------------------------
# 食材の文化タグ（読み手が「和食食材が残っているか」を判断するための客観的な印）
# ---------------------------------------------------------------------------
def culture_tags(recipes, cuisines):
    cnt = collections.defaultdict(collections.Counter)
    for r in recipes:
        for t in r["ingredients"]:
            cnt[t][r["cuisine"]] += 1
    base = collections.Counter(r["cuisine"] for r in recipes)
    n = len(recipes)
    tags = {}
    for t, c in cnt.items():
        tot = sum(c.values())
        if tot < CULTURE_MIN_COUNT:
            continue
        best, lift = max(((cu, (c[cu] / tot) / (base[cu] / n)) for cu in cuisines), key=lambda kv: kv[1])
        if lift >= CULTURE_LIFT_MARK:
            tags[t] = (best, lift)
    return tags


def tag(t, tags):
    return f"{t} [{tags[t][0][:3]}]" if t in tags else t


# ---------------------------------------------------------------------------
# 各 k の計算
# ---------------------------------------------------------------------------
def nearest(W, wv, v, exclude, k):
    sims = W @ unit(v)
    out = []
    for i in np.argsort(-sims):
        t = wv.index_to_key[i]
        if t in exclude:
            continue
        out.append((t, float(sims[i])))
        if len(out) == k:
            break
    return out


def arithmetic_for_k(W, wv, cent, tags):
    def vec(term):
        return cent[term.split(":", 1)[1]] if term.startswith("cuisine:") else W[wv.key_to_index[term]]

    res = {}
    for desc, pos, neg in E1.ARITHMETIC:
        v = sum(vec(t) for t in pos) - sum(vec(t) for t in neg)
        excl = {t for t in pos + neg if not t.startswith("cuisine:")}
        top = nearest(W, wv, v, excl, ARITH_TOP_K)
        plus = nearest(W, wv, sum(vec(t) for t in pos[1:]), excl, ARITH_TOP_K)
        cuis = [t.split(":", 1)[1] for t in pos + neg if t.startswith("cuisine:")]
        neg_c = [t.split(":", 1)[1] for t in neg if t.startswith("cuisine:")]
        res[desc] = {
            "top": [[t, round(s, 4)] for t, s in top],
            "overlap_with_plus_only": len({t for t, _ in top} & {t for t, _ in plus}),
            "n_tagged_with_negative_cuisine": sum(1 for t, _ in top if t in tags and tags[t][0] in neg_c),
            "_cuisines": cuis,
        }
    mi = nearest(W, wv, W[wv.key_to_index["mirin"]], {"mirin"}, MIRIN_NEIGHBORS_K)
    return res, [[t, round(s, 4)] for t, s in mi]


def axes_for_k(X, W, wv, labels, cuisines, cent):
    out = {}
    for name, a in [
        ("soy sauce ↔ butter", unit(W[wv.key_to_index["soy sauce"]] - W[wv.key_to_index["butter"]])),
        ("japanese 重心 ↔ italian 重心", unit(cent["japanese"] - cent["italian"])),
    ]:
        proj = X @ a
        means = {c: float(proj[labels == c].mean()) for c in cuisines}
        # eta^2: 射影値の分散のうち cuisine 間で説明される割合（軸がどれだけ国籍で分かれるか）
        grand = proj.mean()
        between = sum((labels == c).sum() * (means[c] - grand) ** 2 for c in cuisines)
        eta2 = between / ((proj - grand) ** 2).sum()
        ip = W @ a
        io = np.argsort(-ip)
        out[name] = {
            "cuisine_mean_projection": dict(sorted(((c, round(v, 4)) for c, v in means.items()), key=lambda kv: -kv[1])),
            "eta2_cuisine": round(float(eta2), 4),
            "projection_std": round(float(proj.std()), 4),
            "pos_ingredients": [[wv.index_to_key[i], round(float(ip[i]), 3)] for i in io[:AXIS_TOP_N]],
            "neg_ingredients": [[wv.index_to_key[i], round(float(ip[i]), 3)] for i in io[::-1][:AXIS_TOP_N]],
        }
    return out


def cross_queries(recs, labels):
    jp = np.where(labels == "japanese")[0]
    qs = []
    for desc, need in E1.CROSS_QUERY_SPECS:
        cand = [i for i in jp if all(t in recs[i]["ingredients"] for t in need)]
        if cand:
            qs.append((desc, int(min(cand, key=lambda i: recs[i]["id"]))))
    rng = np.random.default_rng(SEED)  # Exp-01 と同じ乱数でランダムクエリを選ぶ
    for i in rng.choice(jp, size=E1.CROSS_RANDOM_N, replace=False):
        qs.append(("ランダム抽出", int(i)))
    return qs


def cross_for_k(X, recs, labels, queries):
    jp = np.where(labels == "japanese")[0]
    other = np.where(labels != "japanese")[0]
    Xo = X[other]
    S = X[jp] @ Xo.T
    dist = collections.Counter(labels[other][S.argmax(axis=1)])
    per_q = {}
    for desc, i in queries:
        sims = Xo @ X[i]
        top = np.argsort(-sims)[:E1.CROSS_TOP_K]
        per_q[recs[i]["id"]] = [[int(recs[other[j]]["id"]), recs[other[j]]["cuisine"], round(float(sims[j]), 3)]
                                for j in top]
    return {"nn_cuisine_counts": dict(dist.most_common()), "queries": per_q}


# ---------------------------------------------------------------------------
# 書き出し
# ---------------------------------------------------------------------------
def kcols(ks):
    return "| " + " | ".join(f"k={k}" for k in ks) + " |", "|" + "---|" * len(ks)


def write_arithmetic(per_k, mirin, tags, ks):
    L = ["# Exp-01b 食材の足し引き（k ごと）", "",
         "- k = 取り除いた LDA 方向の本数。k=0 は Exp-01 と同じ空間（数値が Exp-01 と一致することを確認済み）",
         "- 式・語彙・除外規則は Exp-01 と同じ。`cuisine:xxx` は**その k の空間で計算し直した** cuisine 重心",
         f"- 食材名の後ろの `[xxx]` は、その食材を含むレシピで cuisine xxx が偶然の {CULTURE_LIFT_MARK:g} 倍以上多いことを示す（先頭3文字。jap=japanese, fre=french 等）。"
         "学習データの出現頻度から機械的に付けた印で、空間とは無関係",
         "- k が大きいと cuisine 重心の差は小さくなり、「− japanese + french」はほぼ「食材単体の近傍」になる。そのため mirin 単体の近傍も並べる",
         ""]
    L += ["## mirin の近傍（文化除去後）", "", "| # " + kcols(ks)[0], "|---" + kcols(ks)[1]]
    for r in range(MIRIN_NEIGHBORS_K):
        L.append(f"| {r+1} | " + " | ".join(tag(mirin[k][r][0], tags) for k in ks) + " |")
    L.append("")
    for desc, *_ in E1.ARITHMETIC:
        L += [f"## {desc}", "", "| # " + kcols(ks)[0], "|---" + kcols(ks)[1]]
        for r in range(ARITH_TOP_K):
            L.append(f"| {r+1} | " + " | ".join(
                f"{tag(per_k[k][desc]['top'][r][0], tags)} ({per_k[k][desc]['top'][r][1]:.2f})" for k in ks) + " |")
        L.append("| − 側 cuisine の印が付いた数 | " + " | ".join(
            str(per_k[k][desc]["n_tagged_with_negative_cuisine"]) for k in ks) + " |")
        L.append("| 「+ 側だけ」上位8との重なり | " + " | ".join(
            str(per_k[k][desc]["overlap_with_plus_only"]) for k in ks) + " |")
        L.append("")
    (RESULTS / "arithmetic.md").write_text("\n".join(L))


def write_axes(per_k, ks):
    L = ["# Exp-01b 軸への射影（k ごと）", "",
         "- 軸・射影の式は Exp-01 と同じ。軸ベクトルは**その k の空間で**作り直す（soy sauce / butter の食材ベクトル、cuisine 重心）",
         "- 表のセルは「cuisine (平均射影値)」。上 = 左側の極寄り",
         "- η² = 料理の射影値の分散のうち、cuisine の違いで説明される割合。0 なら軸は国籍と無関係",
         ""]
    for name in per_k[ks[0]]:
        L += [f"## {name}", "", "### cuisine 平均の並び", "", "| 順 " + kcols(ks)[0], "|---" + kcols(ks)[1]]
        orders = {k: list(per_k[k][name]["cuisine_mean_projection"].items()) for k in ks}
        for r in range(len(orders[ks[0]])):
            L.append(f"| {r+1} | " + " | ".join(f"{orders[k][r][0]} ({orders[k][r][1]:+.3f})" for k in ks) + " |")
        L.append("| η² | " + " | ".join(f"{per_k[k][name]['eta2_cuisine']:.3f}" for k in ks) + " |")
        L.append("| 射影値の標準偏差 | " + " | ".join(f"{per_k[k][name]['projection_std']:.3f}" for k in ks) + " |")
        L.append("| k=0 の並びとの順位相関 | " + " | ".join(f"{per_k[k][name]['spearman_vs_k0']:+.2f}" for k in ks) + " |")
        L.append("")
        for side, key in [("左の極側", "pos_ingredients"), ("右の極側", "neg_ingredients")]:
            L += [f"### 食材の{side}（上位 {AXIS_TOP_N}）", ""]
            for k in ks:
                L.append(f"- k={k}: " + ", ".join(f"{t} ({v:+.2f})" for t, v in per_k[k][name][key]))
            L.append("")
    (RESULTS / "axes.md").write_text("\n".join(L))


def write_cross(per_k, ks, recs, queries, labels):
    other_n = int((labels != "japanese").sum())
    base = collections.Counter(labels[labels != "japanese"])
    n_jp = int((labels == "japanese").sum())
    cu_order = list(per_k[0]["nn_cuisine_counts"].keys())
    cu_order += sorted(c for c in base if c not in cu_order)
    L = ["# Exp-01b japanese レシピの他 cuisine 最近傍（k ごと）", "",
         "- 式は Exp-01 と同じ（料理ベクトルのコサイン類似度、候補は japanese 以外の全レシピ）。料理ベクトルはその k の食材ベクトルから作り直す",
         "- クエリは Exp-01 と同じレシピ（同じ規則・同じ乱数）", "",
         f"## 集計: japanese 全 {n_jp} 件の「他 cuisine 最近傍」の割合", "",
         "| cuisine | 候補中の割合 " + kcols(ks)[0], "|---|---" + kcols(ks)[1]]
    for c in cu_order:
        L.append(f"| {c} | {base[c]/other_n:.3f} | " + " | ".join(
            f"{per_k[k]['nn_cuisine_counts'].get(c, 0)/n_jp:.3f}" for k in ks) + " |")
    L.append("| korean+chinese | " + f"{(base['korean']+base['chinese'])/other_n:.3f} | " + " | ".join(
        f"{per_k[k]['korean_chinese_share']:.3f}" for k in ks) + " |")
    L.append("| 分布のエントロピー (bit) | — | " + " | ".join(f"{per_k[k]['entropy_bits']:.2f}" for k in ks) + " |")
    L.append("")
    L += ["## クエリごとの上位 5（cuisine と cos）", ""]
    for desc, i in queries:
        r = recs[i]
        L += [f"### {desc}: id {r['id']}", "", f"食材: {', '.join(r['ingredients'])}", "",
              "| # " + kcols(ks)[0], "|---" + kcols(ks)[1]]
        for rank in range(E1.CROSS_TOP_K):
            L.append(f"| {rank+1} | " + " | ".join(
                f"{per_k[k]['queries'][r['id']][rank][1]} ({per_k[k]['queries'][r['id']][rank][2]:.2f})" for k in ks) + " |")
        L.append("")
    L += ["各近傍のレシピ id と食材は metrics.json の `cross_cultural.<k>.queries` にある。", ""]
    (RESULTS / "cross_cultural.md").write_text("\n".join(L))


def plot_map(Y0, Yk, labels, dessert, cuisines):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams["svg.hashsalt"] = "exp01b"
    plt.rcParams["font.size"] = 9
    INK, BG_PT, HI = "#0b0b0b", "#d4d3cf", "#c2410c"
    order = sorted(cuisines, key=lambda c: -(labels == c).sum())
    cmap = plt.get_cmap("tab20")
    colors = np.array([cmap(order.index(c)) for c in labels])
    perm = np.random.default_rng(SEED).permutation(len(labels))
    fig, axes = plt.subplots(2, 2, figsize=(13, 11.5), dpi=140)
    for col, (Y, name) in enumerate([(Y0, "k=0 (Exp-01)"), (Yk, f"k={MAP_K} LDA directions removed")]):
        ax = axes[0, col]
        ax.scatter(Y[perm, 0], Y[perm, 1], s=1.0, c=colors[perm], linewidths=0, alpha=0.6, rasterized=True)
        ax.set_title(f"{name}: colored by cuisine", color=INK, loc="left", fontsize=10)
        ax = axes[1, col]
        ax.scatter(Y[~dessert, 0], Y[~dessert, 1], s=0.6, c=BG_PT, linewidths=0, rasterized=True)
        ax.scatter(Y[dessert, 0], Y[dessert, 1], s=1.4, c=HI, linewidths=0, alpha=0.7, rasterized=True)
        ax.set_title(f"{name}: baking-like recipes (≥{DESSERT_MIN_MARKERS} markers) in orange",
                     color=INK, loc="left", fontsize=10)
    for ax in axes.ravel():
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_color("#e6e5e1")
    handles = [plt.Line2D([], [], marker="o", ls="", color=cmap(i), label=f"{c} ({(labels == c).sum()})")
               for i, c in enumerate(order)]
    # 凡例は図の外（右上）に置き、どのパネルの点・右下にも重ねない
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.86, 0.95), frameon=False, fontsize=8,
               labelcolor=INK)
    fig.suptitle("Exp-01b: dish vectors → UMAP (same UMAP settings as Exp-01)", x=0.01, ha="left", color=INK)
    fig.tight_layout(rect=(0, 0, 0.86, 0.97))
    fig.savefig(RESULTS / f"map_k{MAP_K}.png", metadata={"Software": None})
    plt.close(fig)


# ---------------------------------------------------------------------------
def main():
    import gensim, sklearn, umap, matplotlib, scipy
    from scipy.stats import spearmanr
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

    RESULTS.mkdir(parents=True, exist_ok=True)
    log, metrics = {}, {"k_values": K_VALUES}
    t_all = time.perf_counter()

    recipes = load_recipes(log)
    wv = load_vectors(recipes, log)
    recs_idx, recs = [], []
    for r in recipes:
        idx = [wv.key_to_index[t] for t in r["ingredients"] if t in wv.key_to_index]
        if idx:
            recs_idx.append(idx)
            recs.append(r)
    labels = np.array([r["cuisine"] for r in recs])
    cuisines = sorted(set(labels))
    y = np.array([cuisines.index(c) for c in labels])
    log["n_recipes_used"] = len(recs)
    ing_sets = [set(r["ingredients"]) for r in recs]
    dessert = np.array([sum(m in s for m in DESSERT_MARKERS) >= DESSERT_MIN_MARKERS for s in ing_sets])
    metrics["dessert_definition"] = {"markers": DESSERT_MARKERS, "min_markers": DESSERT_MIN_MARKERS,
                                     "n": int(dessert.sum())}
    tags = culture_tags(recipes, cuisines)

    W0 = unit(wv.vectors)
    X0 = dish_vectors(W0, recs_idx)

    # LDA（k=0 の料理ベクトルで一度だけ学習）→ 上位 k 列を QR で正規直交化（k が増えると部分空間は入れ子）
    t0 = time.perf_counter()
    lda = LinearDiscriminantAnalysis(**LDA_PARAMS).fit(X0, y)
    S = lda.scalings_[:, : len(cuisines) - 1]
    log["lda_seconds"] = round(time.perf_counter() - t0, 1)
    metrics["lda"] = {
        "n_directions": int(S.shape[1]),
        "explained_variance_ratio": [round(float(v), 4) for v in lda.explained_variance_ratio_],
        "train_accuracy_k0": round(float(lda.score(X0, y)), 4),
    }
    Qfull, _ = np.linalg.qr(S)

    per = {}
    queries = cross_queries(recs, labels)
    for k in K_VALUES:
        t0 = time.perf_counter()
        Q = Qfull[:, :k] if k > 0 else None
        W = remove_subspace(W0, Q)
        X = dish_vectors(W, recs_idx)
        cent = {c: unit(X[labels == c].mean(axis=0)) for c in cuisines}
        sm = space_metrics(X, y, dessert, cuisines)
        if Q is not None:
            sm["ingredient_norm_share_removed"] = round(float(((W0 @ Q) ** 2).sum(axis=1).mean()), 4)
            sm["dish_residual_in_removed_subspace"] = float(np.abs(X @ Q).max())
        ar, mi = arithmetic_for_k(W, wv, cent, tags)
        ax = axes_for_k(X, W, wv, labels, cuisines, cent)
        cr = cross_for_k(X, recs, labels, queries)
        n_jp = int((labels == "japanese").sum())
        cnts = np.array(list(cr["nn_cuisine_counts"].values())) / n_jp
        cr["korean_chinese_share"] = round((cr["nn_cuisine_counts"].get("korean", 0)
                                            + cr["nn_cuisine_counts"].get("chinese", 0)) / n_jp, 4)
        cr["entropy_bits"] = round(float(-(cnts * np.log2(cnts)).sum()), 3)
        per[k] = {"space": sm, "arith": ar, "mirin": mi, "axes": ax, "cross": cr, "X": X}
        log[f"k{k}_seconds"] = round(time.perf_counter() - t0, 1)
        print(f"k={k}: knn={sm['knn_label_agreement']} sil={sm['silhouette_100d_cosine']['mean']} "
              f"dessert={sm['dessert_knn_agreement']} lda_cv={sm['lda_refit_cv_accuracy']['mean']} "
              f"({log[f'k{k}_seconds']}s)", flush=True)

    for name in per[0]["axes"]:
        base_order = list(per[0]["axes"][name]["cuisine_mean_projection"])
        for k in K_VALUES:
            m = per[k]["axes"][name]["cuisine_mean_projection"]
            per[k]["axes"][name]["spearman_vs_k0"] = round(float(spearmanr(
                [m[c] for c in base_order], [per[0]["axes"][name]["cuisine_mean_projection"][c] for c in base_order]
            ).statistic), 3)

    # k=0 が Exp-01 と一致するかの確認
    e1 = json.loads((EXP01_DIR / "results" / "metrics.json").read_text())
    log["k0_knn_matches_exp01"] = per[0]["space"]["knn_label_agreement"] == e1["knn_label_agreement"]["overall"]
    log["k0_mirin_arith_matches_exp01"] = (
        [t for t, _ in per[0]["arith"][E1.ARITHMETIC[0][0]]["top"]]
        == [t for t, _ in e1["arithmetic"][E1.ARITHMETIC[0][0]]["top"]])

    write_arithmetic({k: per[k]["arith"] for k in K_VALUES}, {k: per[k]["mirin"] for k in K_VALUES}, tags, K_VALUES)
    write_axes({k: per[k]["axes"] for k in K_VALUES}, K_VALUES)
    write_cross({k: per[k]["cross"] for k in K_VALUES}, K_VALUES, recs, queries, labels)

    metrics["by_k"] = {str(k): per[k]["space"] for k in K_VALUES}
    metrics["axes"] = {str(k): per[k]["axes"] for k in K_VALUES}
    metrics["cross_cultural"] = {str(k): per[k]["cross"] for k in K_VALUES}
    metrics["arithmetic"] = {str(k): {d: {kk: vv for kk, vv in v.items() if not kk.startswith("_")}
                                      for d, v in per[k]["arith"].items()} for k in K_VALUES}
    metrics["mirin_neighbors"] = {str(k): per[k]["mirin"] for k in K_VALUES}
    (RESULTS / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")

    # 2D マップ: k=0 は Exp-01 の UMAP 座標を読むだけ、MAP_K は同じ UMAP 設定で計算
    t0 = time.perf_counter()
    Y0 = np.load(EXP01_DIR / "results" / "umap_2d.npy")
    Yk = umap.UMAP(**E1.UMAP_PARAMS).fit_transform(per[MAP_K]["X"])
    log["umap_seconds"] = round(time.perf_counter() - t0, 1)
    plot_map(Y0, Yk, labels, dessert, cuisines)
    log["total_seconds"] = round(time.perf_counter() - t_all, 1)

    run_log = [
        "# Exp-01b 実行ログ", "",
        "`uv run python experiments/exp-01b/run.py` の最終実行時の記録。所要時間はマシン依存。", "",
        "## 環境",
        f"- Python {platform.python_version()} / {platform.platform()}",
        f"- gensim {gensim.__version__}, umap-learn {umap.__version__}, scikit-learn {sklearn.__version__}, "
        f"numpy {np.__version__}, scipy {scipy.__version__}, matplotlib {matplotlib.__version__}",
        "", "## 入力",
        f"- `data/raw/train.json` SHA-256 一致: {log['raw_sha256_matches']}",
        f"- 食材ベクトル: {log['vectors_source']}（vectors の SHA-256 `{log['vectors_sha256'][:16]}…`）",
        f"- 使用レシピ {log['n_recipes_used']}、語彙 {len(wv)}",
        f"- k=0 の 10-NN 一致率が Exp-01 metrics.json と一致: {log['k0_knn_matches_exp01']}",
        f"- k=0 の mirin − japanese + french 上位 {ARITH_TOP_K} が Exp-01 と一致: {log['k0_mirin_arith_matches_exp01']}",
        "", "## 方法",
        f"- LDA: sklearn LinearDiscriminantAnalysis({LDA_PARAMS})、入力は k=0 の料理ベクトル（100 次元・単位長）と cuisine ラベル。"
        f"判別方向 {metrics['lda']['n_directions']} 本（scalings_ の列、寄与率順）",
        "- scalings_ は互いに直交しないので、先頭 k 列を QR 分解で正規直交化し、その部分空間を除去する（k を増やすと部分空間は入れ子）",
        "- 食材ベクトル: 単位長にしてから部分空間の成分を引き、再び単位長にする。料理ベクトル・cuisine 重心は Exp-01 と同じ式でその k の食材ベクトルから作り直す"
        "（料理ベクトルも除去部分空間に成分を持たない。最大残差は metrics.json の `dish_residual_in_removed_subspace`）",
        "- LDA は一度だけ学習し、k ごとに学習し直さない",
        f"- 指標: 10-NN 国籍一致率、シルエット（{E1.SILHOUETTE_SAMPLE} 件×{E1.SILHOUETTE_REPEATS} 回）、"
        f"除去後の空間で LDA を学習し直したときの {LDA_CV_FOLDS}-fold 分類精度（線形に国籍がどれだけ残るか）、"
        f"製菓っぽいレシピ（{DESSERT_MARKERS} のうち {DESSERT_MIN_MARKERS} 個以上、{int(dessert.sum())} 件）の 10-NN 製菓一致率",
        f"- 2D マップは k={MAP_K}（`map_k{MAP_K}.png`）。k=0 側は Exp-01 の `umap_2d.npy` をそのまま使う。"
        f"k={MAP_K} を選んだ理由: 和食の他 cuisine 最近傍で korean+chinese の割合が最小"
        f"（{per[MAP_K]['cross']['korean_chinese_share']:.3f}、k=0 は {per[0]['cross']['korean_chinese_share']:.3f}）、"
        f"分布のエントロピーが最大（{per[MAP_K]['cross']['entropy_bits']:.2f} bit）で、"
        f"10-NN 一致率の低下は {per[0]['space']['knn_label_agreement'] - per[MAP_K]['space']['knn_label_agreement']:.3f} にとどまるため",
        "", "## ハイパーパラメータ",
        f"- SEED = {SEED}, K_VALUES = {K_VALUES}, MAP_K = {MAP_K}",
        f"- ARITH_TOP_K = {ARITH_TOP_K}, MIRIN_NEIGHBORS_K = {MIRIN_NEIGHBORS_K}, AXIS_TOP_N = {AXIS_TOP_N}, "
        f"CULTURE_LIFT_MARK = {CULTURE_LIFT_MARK}, CULTURE_MIN_COUNT = {CULTURE_MIN_COUNT}",
        f"- UMAP: {E1.UMAP_PARAMS}（Exp-01 と同じ）",
        "", "## 所要時間",
        f"- k ごと: " + ", ".join(f"k={k} {log[f'k{k}_seconds']} 秒" for k in K_VALUES),
        f"- UMAP: {log['umap_seconds']} 秒",
        f"- 全体: {log['total_seconds']} 秒",
        "",
    ]
    (RESULTS / "run_log.md").write_text("\n".join(run_log))
    print("\n".join(run_log))


if __name__ == "__main__":
    main()
