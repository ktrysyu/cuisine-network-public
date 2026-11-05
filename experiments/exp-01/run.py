"""Exp-01: 小さな空間を作り、軸を1本引いてみる。

実行: リポジトリ直下で `uv run python experiments/exp-01/run.py`

手順（plan.md）
1. What's Cooking の食材リストで word2vec を学習（cuisine ラベルは学習に使わない）
2. 料理 = 構成食材ベクトルの平均 → UMAP で 2D、cuisine ごとのまとまりを見る（Q1）
3. 「soy sauce ↔ butter」「japanese 重心 ↔ italian 重心」の軸に射影（Q2）
4. japanese の料理ごとに他 cuisine の最近傍（Q3）
5. 食材の足し引き（Q6）
"""

from __future__ import annotations

import collections
import hashlib
import json
import platform
import re
import time
import unicodedata
import zlib
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# 設定（ハイパーパラメータはすべてここ）
# ---------------------------------------------------------------------------
SEED = 42

ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = ROOT / "data" / "raw" / "train.json"
RAW_SHA256 = "f18e7e568d1c606774bfb134ece51ef0a143cd5069e6f9241bb6036b45b7d2b0"
PROCESSED_PATH = ROOT / "data" / "processed" / "whats_cooking_tokens.tsv"
MODEL_PATH = ROOT / "data" / "processed" / "exp01_word2vec.kv"  # gitignore（再生成可）
RESULTS = Path(__file__).resolve().parent / "results"

W2V = dict(
    vector_size=100,
    window=70,        # レシピ最大長(65)以上。食材の並び順に意味は無いので、レシピ全体を文脈にする
    min_count=5,      # 5 レシピ未満の食材は語彙から外す
    sg=1,             # skip-gram
    negative=10,
    sample=1e-3,
    epochs=30,
    workers=1,        # 再現性のため単スレッド
    seed=SEED,
)
SHUFFLE_EACH_EPOCH = True  # 各エポックでレシピ内の食材順をシャッフル（順序の偏りを消す）

UMAP_PARAMS = dict(n_neighbors=30, min_dist=0.1, metric="cosine", random_state=SEED)

SILHOUETTE_SAMPLE = 10000
SILHOUETTE_REPEATS = 5
KNN_K = 10

AXIS_TOP_N = 15
AXIS_MIN_INGREDIENTS = 5   # 軸の両端表の「5 食材以上」版の閾値

CROSS_QUERY_SPECS = [
    # (説明, 含むべき食材) — 条件を満たす japanese レシピのうち最小 id を選ぶ（恣意性を減らすため機械的に）
    ("味噌汁っぽいもの", ["miso", "dashi"]),
    ("照り焼きっぽいもの", ["mirin", "soy sauce", "sake", "chicken thighs"]),
    ("寿司飯っぽいもの", ["sushi rice", "rice vinegar"]),
    ("天ぷら・揚げ物っぽいもの", ["panko breadcrumbs", "eggs", "flour"]),
    ("カレー", ["curry powder", "potatoes", "carrots", "onions"]),
]
CROSS_RANDOM_N = 3
CROSS_TOP_K = 5

# 足し引き: (説明, positive, negative)。"cuisine:xxx" は cuisine 重心、それ以外は食材
ARITHMETIC = [
    ("Kazama 形式: mirin − japanese + french", ["mirin", "cuisine:french"], ["cuisine:japanese"]),
    ("soy sauce − japanese + italian", ["soy sauce", "cuisine:italian"], ["cuisine:japanese"]),
    ("soy sauce − chinese + mexican", ["soy sauce", "cuisine:mexican"], ["cuisine:chinese"]),
    ("miso − japanese + italian", ["miso", "cuisine:italian"], ["cuisine:japanese"]),
    ("sake − japanese + french", ["sake", "cuisine:french"], ["cuisine:japanese"]),
    ("butter − french + indian", ["butter", "cuisine:indian"], ["cuisine:french"]),
    ("flour tortillas − mexican + indian", ["flour tortillas", "cuisine:indian"], ["cuisine:mexican"]),
    ("fish sauce − thai + italian", ["fish sauce", "cuisine:italian"], ["cuisine:thai"]),
    ("parmesan cheese − italian + japanese", ["parmesan cheese", "cuisine:japanese"], ["cuisine:italian"]),
    ("食材だけ: soy sauce − ginger + basil", ["soy sauce", "basil"], ["ginger"]),
    ("食材だけ: sake − rice + grapes", ["sake", "grapes"], ["rice"]),
    ("食材だけ: tofu − soy sauce + cheese", ["tofu", "cheese"], ["soy sauce"]),
]
ARITH_TOP_K = 8


# ---------------------------------------------------------------------------
# 前処理
# ---------------------------------------------------------------------------
def normalize_ingredient(s: str) -> str:
    """最小限の正規化: Unicode NFKC、小文字化、®/™ 除去、空白の畳み込み。
    表記ゆれ（"soy sauce" / "low sodium soy sauce" 等）の統合はしない。"""
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("®", "").replace("™", "")
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    return s


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_and_preprocess(log: dict) -> list[dict]:
    digest = sha256(RAW_PATH)
    log["raw_sha256"] = digest
    log["raw_sha256_matches_SOURCES"] = digest == RAW_SHA256
    if digest != RAW_SHA256:
        print(f"[warn] train.json の SHA-256 が SOURCES.md と一致しない: {digest}")
    raw = json.loads(RAW_PATH.read_text())
    recipes = []
    n_dup_removed = 0
    for r in raw:
        toks = [normalize_ingredient(x) for x in r["ingredients"]]
        seen, uniq = set(), []
        for t in toks:
            if t and t not in seen:
                seen.add(t)
                uniq.append(t)
        n_dup_removed += len(toks) - len(uniq)
        recipes.append({"id": r["id"], "cuisine": r["cuisine"], "ingredients": uniq})
    log["n_recipes_raw"] = len(raw)
    log["n_cuisines"] = len({r["cuisine"] for r in recipes})
    log["n_duplicate_ingredients_removed"] = n_dup_removed
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    with PROCESSED_PATH.open("w") as f:
        f.write("id\tcuisine\tingredients(|区切り)\n")
        for r in recipes:
            f.write(f"{r['id']}\t{r['cuisine']}\t{'|'.join(r['ingredients'])}\n")
    return recipes


# ---------------------------------------------------------------------------
# word2vec
# ---------------------------------------------------------------------------
def stable_hash(s: str) -> int:
    # gensim の初期ベクトル生成は既定で Python の hash()（PYTHONHASHSEED で揺れる）を使うので固定する
    return zlib.crc32(s.encode("utf-8"))


class ShuffledCorpus:
    """反復のたびにレシピ内の食材順をシャッフルするコーパス（乱数は SEED から決定的）。"""

    def __init__(self, sentences, seed):
        self.sentences = sentences
        self.seed = seed
        self.epoch = 0

    def __iter__(self):
        rng = np.random.default_rng(self.seed + self.epoch)
        self.epoch += 1
        for s in self.sentences:
            s = list(s)
            if SHUFFLE_EACH_EPOCH:
                rng.shuffle(s)
            yield s


def train_word2vec(recipes, log):
    from gensim.models import Word2Vec

    sentences = [r["ingredients"] for r in recipes]  # cuisine は渡さない
    corpus = ShuffledCorpus(sentences, SEED)
    model = Word2Vec(hashfxn=stable_hash, **{k: v for k, v in W2V.items() if k != "epochs"})
    t0 = time.perf_counter()
    model.build_vocab(corpus)
    model.train(corpus, total_examples=len(sentences), epochs=W2V["epochs"])
    log["w2v_train_seconds"] = round(time.perf_counter() - t0, 1)
    all_ings = collections.Counter(t for s in sentences for t in s)
    log["n_unique_ingredients"] = len(all_ings)
    log["vocab_size"] = len(model.wv)
    oov_tokens = sum(c for t, c in all_ings.items() if t not in model.wv.key_to_index)
    log["oov_token_share"] = round(oov_tokens / sum(all_ings.values()), 4)
    model.wv.save(str(MODEL_PATH))
    return model.wv


# ---------------------------------------------------------------------------
# 料理ベクトル
# ---------------------------------------------------------------------------
def unit(x, axis=-1):
    n = np.linalg.norm(x, axis=axis, keepdims=True)
    return x / np.where(n == 0, 1, n)


def dish_vectors(recipes, wv, log):
    """料理 = 語彙内食材の単位ベクトルの平均を、さらに単位長にしたもの。"""
    W = unit(wv.vectors)
    vecs, kept = [], []
    for i, r in enumerate(recipes):
        idx = [wv.key_to_index[t] for t in r["ingredients"] if t in wv.key_to_index]
        if not idx:
            continue
        vecs.append(W[idx].mean(axis=0))
        kept.append(i)
    log["n_recipes_dropped_no_vocab"] = len(recipes) - len(kept)
    return unit(np.asarray(vecs, dtype=np.float32)), kept


# ---------------------------------------------------------------------------
# Q1: 2D マップとシルエット
# ---------------------------------------------------------------------------
def q1_map_and_metrics(X, labels, cuisines, log, metrics):
    import umap
    from sklearn.metrics import silhouette_samples, silhouette_score
    from sklearn.neighbors import NearestNeighbors

    t0 = time.perf_counter()
    Y = umap.UMAP(**UMAP_PARAMS).fit_transform(X)
    log["umap_seconds"] = round(time.perf_counter() - t0, 1)
    np.save(RESULTS / "umap_2d.npy", Y.astype(np.float32))

    y = np.array([cuisines.index(c) for c in labels])
    rng = np.random.default_rng(SEED)

    def sil(Z, metric, yy):
        vals = [silhouette_score(Z, yy, metric=metric, sample_size=SILHOUETTE_SAMPLE,
                                 random_state=SEED + k) for k in range(SILHOUETTE_REPEATS)]
        return {"mean": round(float(np.mean(vals)), 4), "std": round(float(np.std(vals)), 4)}

    y_shuf = rng.permutation(y)
    metrics["silhouette"] = {
        "note": f"cuisine ラベルをクラスタとみなしたシルエット係数。{SILHOUETTE_SAMPLE} 件サンプル×{SILHOUETTE_REPEATS} 回の平均。参考値",
        "dish_space_100d_cosine": sil(X, "cosine", y),
        "umap_2d_euclidean": sil(Y, "euclidean", y),
        "baseline_shuffled_labels_100d_cosine": sil(X, "cosine", y_shuf),
        "baseline_shuffled_labels_umap_2d_euclidean": sil(Y, "euclidean", y_shuf),
    }

    # cuisine 別シルエット（100 次元、全件ではなく層別なしのサンプル 1 回）
    idx = rng.choice(len(X), size=SILHOUETTE_SAMPLE, replace=False)
    s = silhouette_samples(X[idx], y[idx], metric="cosine")
    metrics["silhouette_by_cuisine_100d"] = {
        cuisines[c]: round(float(s[y[idx] == c].mean()), 4)
        for c in sorted(set(y[idx]), key=lambda c: -s[y[idx] == c].mean())
    }

    # 補助指標: 10-NN の cuisine 一致率（自分を除く）。偶然一致率 = Σ p_c^2
    nn = NearestNeighbors(n_neighbors=KNN_K + 1, metric="cosine").fit(X)
    _, nbr = nn.kneighbors(X)
    agree = (y[nbr[:, 1:]] == y[:, None]).mean()
    p = np.bincount(y) / len(y)
    per = {cuisines[c]: round(float((y[nbr[y == c, 1:]] == c).mean()), 4) for c in range(len(cuisines))}
    metrics["knn_label_agreement"] = {
        "k": KNN_K,
        "overall": round(float(agree), 4),
        "chance_sum_p_squared": round(float((p ** 2).sum()), 4),
        "by_cuisine": dict(sorted(per.items(), key=lambda kv: -kv[1])),
        "by_cuisine_chance": {cuisines[c]: round(float(p[c]), 4) for c in range(len(cuisines))},
    }
    # 各 cuisine の近傍に最も多く現れる他 cuisine（混同の傾向）
    conf = {}
    for c in range(len(cuisines)):
        nb = y[nbr[y == c, 1:]].ravel()
        nb = nb[nb != c]
        top = collections.Counter(nb).most_common(3)
        conf[cuisines[c]] = [[cuisines[k], round(v / len(nb), 3)] for k, v in top]
    metrics["knn_top_other_cuisines"] = conf
    return Y, nbr


def plot_maps(Y, labels, cuisines):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams["svg.hashsalt"] = "exp01"
    plt.rcParams["font.size"] = 9
    INK, MUTED, BG_PT, HI = "#0b0b0b", "#52514e", "#d4d3cf", "#2a78d6"
    labels = np.asarray(labels)
    order = sorted(cuisines, key=lambda c: -(labels == c).sum())

    # (a) 全 cuisine 色分け（20 色は識別の限界を超える。重心に直接ラベルを置いて補う）
    fig, ax = plt.subplots(figsize=(11, 10), dpi=150)
    cmap = plt.get_cmap("tab20")
    rng = np.random.default_rng(SEED)
    perm = rng.permutation(len(Y))  # 描画順で大きい cuisine が上に来る偏りを避ける
    colors = np.array([cmap(order.index(c)) for c in labels])
    ax.scatter(Y[perm, 0], Y[perm, 1], s=1.2, c=colors[perm], linewidths=0, alpha=0.6, rasterized=True)
    for c in order:
        m = np.median(Y[labels == c], axis=0)
        ax.text(m[0], m[1], c, fontsize=8, color=INK, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=cmap(order.index(c)), lw=1.2, alpha=0.85))
    handles = [plt.Line2D([], [], marker="o", ls="", color=cmap(i), label=f"{c} ({(labels == c).sum()})")
               for i, c in enumerate(order)]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.0, 1.0), frameon=False, fontsize=8,
              labelcolor=INK)
    ax.set_title("Exp-01: dishes as mean ingredient vectors (word2vec) → UMAP, colored by cuisine\n"
                 "labels at per-cuisine median; cuisine labels were not used for training", color=INK, loc="left")
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    fig.tight_layout()
    fig.savefig(RESULTS / "map_all.png", metadata={"Software": None})
    fig.savefig(RESULTS / "map_all.svg", metadata={"Date": None})
    plt.close(fig)

    # (b) 小分け: 各パネルで 1 cuisine を強調、他は灰色
    fig, axes = plt.subplots(4, 5, figsize=(15, 12.5), dpi=130, sharex=True, sharey=True)
    for ax, c in zip(axes.ravel(), order):
        m = labels == c
        ax.scatter(Y[~m, 0], Y[~m, 1], s=0.6, c=BG_PT, linewidths=0, rasterized=True)
        ax.scatter(Y[m, 0], Y[m, 1], s=1.6, c=HI, linewidths=0, alpha=0.7, rasterized=True)
        ax.set_title(f"{c}  (n={m.sum()})", color=INK, fontsize=10, loc="left")
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_color("#e6e5e1")
    fig.suptitle("Exp-01: same UMAP map, one cuisine highlighted per panel", x=0.01, ha="left", color=INK)
    fig.tight_layout()
    fig.savefig(RESULTS / "map_facets.png", metadata={"Software": None})
    fig.savefig(RESULTS / "map_facets.svg", metadata={"Date": None})
    plt.close(fig)


# ---------------------------------------------------------------------------
# Q2: 軸
# ---------------------------------------------------------------------------
def fmt_ings(ings, n=10):
    s = ", ".join(ings[:n])
    return s + (f", …(+{len(ings) - n})" if len(ings) > n else "")


def q2_axes(X, recs, wv, cuisines, metrics):
    labels = np.array([r["cuisine"] for r in recs])
    W = unit(wv.vectors)
    cent = {c: unit(X[labels == c].mean(axis=0)) for c in cuisines}
    axes_def = [
        ("soy sauce ↔ butter", "soy sauce", "butter", unit(W[wv.key_to_index["soy sauce"]] - W[wv.key_to_index["butter"]])),
        ("japanese 重心 ↔ italian 重心", "japanese 重心", "italian 重心", unit(cent["japanese"] - cent["italian"])),
    ]
    n_ing = np.array([len(r["ingredients"]) for r in recs])
    out = ["# Exp-01 軸への射影（Q2）", "",
           "- 料理ベクトル（単位長）と軸ベクトル（単位長）の内積を射影値とする。正 = 左側の極（soy sauce / japanese）寄り",
           "- 軸「soy sauce ↔ butter」= v(soy sauce) − v(butter)。食材ベクトルは単位長にしてから引く",
           "- 軸「japanese 重心 ↔ italian 重心」= 各 cuisine の料理ベクトル平均の差。**cuisine ラベルを使って軸を定義している**（学習には使っていない）",
           "- データに料理名は無い。レシピ ID・cuisine・食材（先頭10件、データ上の順）を載せる",
           f"- 各軸について「全レシピ」版と「食材 {AXIS_MIN_INGREDIENTS} 個以上」版を載せる。前者は食材 1〜3 個のレシピが端を占めやすいため",
           ""]
    metrics["axes"] = {}
    for name, pos, neg, a in axes_def:
        proj = X @ a
        ing_proj = W @ a
        m = {}
        out += [f"## {name}", ""]
        # cuisine ごとの平均位置（並び順）
        cm = sorted(((c, float(proj[labels == c].mean())) for c in cuisines), key=lambda kv: -kv[1])
        m["cuisine_mean_projection"] = {c: round(v, 4) for c, v in cm}
        out += ["### cuisine ごとの平均射影値（上 = " + pos + " 寄り）", "",
                "| 順 | cuisine | 平均 |", "|---|---|---|"]
        out += [f"| {i+1} | {c} | {v:+.3f} |" for i, (c, v) in enumerate(cm)]
        out += [""]
        # 食材の両端
        io = np.argsort(-ing_proj)
        out += [f"### 食材の両端（語彙 {len(wv)} 語）", "",
                f"- {pos} 側: " + ", ".join(f"{wv.index_to_key[i]} ({ing_proj[i]:+.2f})" for i in io[:AXIS_TOP_N]),
                f"- {neg} 側: " + ", ".join(f"{wv.index_to_key[i]} ({ing_proj[i]:+.2f})" for i in io[::-1][:AXIS_TOP_N]),
                ""]
        for variant, mask in [("全レシピ", np.ones(len(recs), bool)),
                              (f"食材 {AXIS_MIN_INGREDIENTS} 個以上", n_ing >= AXIS_MIN_INGREDIENTS)]:
            ids = np.where(mask)[0]
            o = ids[np.argsort(-proj[ids])]
            for side, sel in [(pos, o[:AXIS_TOP_N]), (neg, o[::-1][:AXIS_TOP_N])]:
                out += [f"### {variant}: {side} 側の上位 {AXIS_TOP_N}", "",
                        "| # | id | cuisine | 射影 | 食材数 | 食材 |", "|---|---|---|---|---|---|"]
                for k, i in enumerate(sel):
                    r = recs[i]
                    out.append(f"| {k+1} | {r['id']} | {r['cuisine']} | {proj[i]:+.3f} | {len(r['ingredients'])} | {fmt_ings(r['ingredients'])} |")
                cnt = collections.Counter(recs[i]["cuisine"] for i in sel)
                out += ["", "cuisine 内訳: " + ", ".join(f"{c} {n}" for c, n in cnt.most_common()), ""]
            # 上位 100 の内訳も（15 件だけだと偶然が大きい）
            for side, sel in [(pos, o[:100]), (neg, o[::-1][:100])]:
                cnt = collections.Counter(recs[i]["cuisine"] for i in sel)
                m[f"{variant}_{side}_top100_cuisines"] = dict(cnt.most_common())
        out += [f"### 上位 100 件の cuisine 内訳", ""]
        for k, v in m.items():
            if k.endswith("top100_cuisines"):
                out.append(f"- {k.replace('_top100_cuisines', '')}: " + ", ".join(f"{c} {n}" for c, n in v.items()))
        out += [""]
        metrics["axes"][name] = m
    (RESULTS / "axes.md").write_text("\n".join(out))
    return cent


# ---------------------------------------------------------------------------
# Q3: cross-cultural 最近傍
# ---------------------------------------------------------------------------
def q3_cross(X, recs, cuisines, nbr_same, metrics):
    labels = np.array([r["cuisine"] for r in recs])
    jp = np.where(labels == "japanese")[0]
    other = np.where(labels != "japanese")[0]
    out = ["# Exp-01 japanese レシピの他 cuisine 最近傍（Q3）", "",
           "- 類似度 = 料理ベクトル同士のコサイン類似度。候補は japanese 以外の全レシピ",
           "- クエリの選び方: 下表の食材を**すべて含む** japanese レシピのうち id 最小のもの（機械的に選んだ。代表例である保証は無い）＋ 乱数で 3 件",
           "- データに料理名が無いので「味噌汁」等は食材からの推測ラベル", ""]
    queries = []
    for desc, need in CROSS_QUERY_SPECS:
        cand = [i for i in jp if all(t in recs[i]["ingredients"] for t in need)]
        if not cand:
            out.append(f"- （{desc}: 条件 {need} を満たす japanese レシピ無し。スキップ）")
            continue
        i = min(cand, key=lambda i: recs[i]["id"])
        queries.append((f"{desc}（条件: {', '.join(need)} / 該当 {len(cand)} 件）", i))
    rng = np.random.default_rng(SEED)
    for i in rng.choice(jp, size=CROSS_RANDOM_N, replace=False):
        queries.append(("ランダム抽出", int(i)))
    out.append("")
    Xo = X[other]
    for desc, i in queries:
        r = recs[i]
        sims = Xo @ X[i]
        top = np.argsort(-sims)[:CROSS_TOP_K]
        out += [f"## {desc}: id {r['id']}", "", f"食材: {', '.join(r['ingredients'])}", "",
                "| # | id | cuisine | cos | 食材 |", "|---|---|---|---|---|"]
        for k, j in enumerate(top):
            rr = recs[other[j]]
            out.append(f"| {k+1} | {rr['id']} | {rr['cuisine']} | {sims[j]:.3f} | {fmt_ings(rr['ingredients'], 12)} |")
        out.append("")
    # 全 japanese レシピについて、他 cuisine 最近傍の cuisine 分布
    S = X[jp] @ Xo.T
    nn_c = labels[other][S.argmax(axis=1)]
    dist = collections.Counter(nn_c).most_common()
    base = collections.Counter(labels[other])
    tot = len(other)
    out += ["## 集計: japanese 全 {} 件の「他 cuisine 最近傍」の cuisine 分布".format(len(jp)), "",
            "候補集合での各 cuisine の割合（偶然ならこの比率になる）と並べる。", "",
            "| cuisine | 最近傍になった件数 | 割合 | 候補集合中の割合 |", "|---|---|---|---|"]
    out += [f"| {c} | {n} | {n/len(jp):.3f} | {base[c]/tot:.3f} |" for c, n in dist]
    metrics["cross_cultural_japanese_nn_cuisine"] = {c: n for c, n in dist}
    (RESULTS / "cross_cultural.md").write_text("\n".join(out) + "\n")


# ---------------------------------------------------------------------------
# Q6: 足し引き
# ---------------------------------------------------------------------------
def q6_arithmetic(wv, cent, cuisines, metrics):
    W = unit(wv.vectors)

    def vec(term):
        if term.startswith("cuisine:"):
            return cent[term.split(":", 1)[1]]
        return W[wv.key_to_index[term]]

    def nearest(v, exclude, k):
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

    lines = ["# Exp-01 食材の足し引き（Q6）", "",
             "- 食材ベクトルは単位長。`cuisine:xxx` はその cuisine の料理ベクトル平均（単位長）。料理ベクトルは食材ベクトルの平均なので同じ空間にある",
             "- 結果 = Σpositive − Σnegative を単位長にし、語彙全体からコサイン類似度上位を出す。式に入っている食材は除外",
             "- 比較のため「+ 側の cuisine / 食材だけの最近傍」も並べる。結果がそれとほぼ同じなら、演算ではなく + 側に引っ張られているだけ",
             ""]
    metrics["arithmetic"] = {}
    for desc, pos, neg in ARITHMETIC:
        missing = [t for t in pos + neg if not t.startswith("cuisine:") and t not in wv.key_to_index]
        lines.append(f"## {desc}")
        if missing:
            lines += ["", f"語彙に無い食材があるためスキップ: {missing}", ""]
            metrics["arithmetic"][desc] = {"skipped_missing": missing}
            continue
        v = sum(vec(t) for t in pos) - sum(vec(t) for t in neg)
        excl = {t for t in pos + neg if not t.startswith("cuisine:")}
        res = nearest(v, excl, ARITH_TOP_K)
        added = [t for t in pos if t != pos[0]]
        base = nearest(sum(vec(t) for t in added), excl, ARITH_TOP_K)
        src = nearest(vec(pos[0]), excl, ARITH_TOP_K)
        overlap = len({t for t, _ in res} & {t for t, _ in base})
        lines += ["", "| # | 結果 | cos | 比較: +側 (" + ", ".join(added) + ") だけ | 比較: " + pos[0] + " だけ |",
                  "|---|---|---|---|---|"]
        for k in range(ARITH_TOP_K):
            lines.append(f"| {k+1} | {res[k][0]} | {res[k][1]:.3f} | {base[k][0]} | {src[k][0]} |")
        lines += ["", f"結果上位 {ARITH_TOP_K} と「+側だけ」上位 {ARITH_TOP_K} の重なり: {overlap} 件", ""]
        metrics["arithmetic"][desc] = {"top": [[t, round(s, 4)] for t, s in res], "overlap_with_plus_only": overlap}
    (RESULTS / "arithmetic.md").write_text("\n".join(lines))


# ---------------------------------------------------------------------------
def main():
    import gensim, sklearn, umap, matplotlib

    RESULTS.mkdir(parents=True, exist_ok=True)
    log, metrics = {}, {}
    t_all = time.perf_counter()

    recipes = load_and_preprocess(log)
    wv = train_word2vec(recipes, log)
    X, kept = dish_vectors(recipes, wv, log)
    recs = [recipes[i] for i in kept]
    labels = [r["cuisine"] for r in recs]
    cuisines = sorted(set(labels))
    log["n_recipes_used"] = len(recs)
    metrics["n_recipes_used"] = len(recs)
    metrics["vocab_size"] = len(wv)

    Y, nbr = q1_map_and_metrics(X, labels, cuisines, log, metrics)
    plot_maps(Y, labels, cuisines)
    cent = q2_axes(X, recs, wv, cuisines, metrics)
    q3_cross(X, recs, cuisines, nbr, metrics)
    q6_arithmetic(wv, cent, cuisines, metrics)

    (RESULTS / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")
    log["total_seconds"] = round(time.perf_counter() - t_all, 1)

    lens = [len(r["ingredients"]) for r in recipes]
    run_log = [
        "# Exp-01 実行ログ", "",
        "`uv run python experiments/exp-01/run.py` の最終実行時の記録。所要時間はマシン依存（再実行で変わるのはこのファイルの時間の行だけのはず）。", "",
        "## 環境",
        f"- Python {platform.python_version()} / {platform.platform()}",
        f"- gensim {gensim.__version__}, umap-learn {umap.__version__}, scikit-learn {sklearn.__version__}, numpy {np.__version__}, matplotlib {matplotlib.__version__}",
        "", "## データ",
        f"- `data/raw/train.json` SHA-256: `{log['raw_sha256']}`（SOURCES.md と一致: {log['raw_sha256_matches_SOURCES']}）",
        f"- レシピ数 {log['n_recipes_raw']} / cuisine 数 {log['n_cuisines']}",
        f"- 食材数/レシピ: 最小 {min(lens)}, 中央値 {int(np.median(lens))}, 最大 {max(lens)}",
        f"- 同一レシピ内の重複食材（正規化後）を除去: {log['n_duplicate_ingredients_removed']} 件",
        f"- 正規化後のユニーク食材 {log['n_unique_ingredients']} → word2vec 語彙 {log['vocab_size']}（min_count={W2V['min_count']}）。語彙外トークンの割合 {log['oov_token_share']:.2%}",
        f"- 語彙内食材が 1 つも無く除外したレシピ: {log['n_recipes_dropped_no_vocab']} → 使用 {log['n_recipes_used']}",
        f"- 前処理済み: `data/processed/{PROCESSED_PATH.name}`",
        "", "## ハイパーパラメータ",
        f"- SEED = {SEED}",
        f"- word2vec: {W2V}, 各エポックでレシピ内の食材順をシャッフル: {SHUFFLE_EACH_EPOCH}, hashfxn = crc32",
        f"- UMAP: {UMAP_PARAMS}",
        f"- silhouette: sample_size={SILHOUETTE_SAMPLE} × {SILHOUETTE_REPEATS} 回, kNN k={KNN_K}",
        "", "## 所要時間",
        f"- word2vec 学習: {log['w2v_train_seconds']} 秒",
        f"- UMAP: {log['umap_seconds']} 秒",
        f"- 全体: {log['total_seconds']} 秒",
        "",
    ]
    (RESULTS / "run_log.md").write_text("\n".join(run_log))
    print("\n".join(run_log))


if __name__ == "__main__":
    main()
