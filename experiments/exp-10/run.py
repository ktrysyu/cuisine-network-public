"""Exp-10: 香りの層を加え、共起・味・香りの近さを比べる。Ahn et al. 2011 の ΔNs を What's Cooking で追試する。

実行: リポジトリ直下で `uv run python experiments/exp-10/build_mapping.py && uv run python experiments/exp-10/run.py`

入力
- data/raw/ahn2011_zenodo/ingr_comp/*.tsv（Ahn et al. 2011 の食材×香り化合物表。CC BY 4.0。data/SOURCES.md）
- data/raw/ahn2011/srep00196-s2.csv（論文補足: 食材ペアの共有化合物数。上の表との照合に使う）
- data/raw/ahn2011/srep00196-s3.csv（論文補足: Ahn らのレシピ。ΔNs の実装確認に使う）
- data/labels/aroma_mapping.csv（303 食材 → Ahn の食材名。build_mapping.py が生成）
- data/labels/taste_scores.csv（本人確認済みの味覚スコア 303 食材）
- data/raw/train.json と Exp-01 の word2vec（data/processed/exp01_word2vec.kv。無ければ Exp-01 と同じ設定で再生成）

近さの定義（食材 i, j）
- 香り: C_i = Ahn の表で食材 i が持つ化合物の集合（2 値）
  - 共有化合物数 |C_i ∩ C_j|
  - Jaccard |C_i ∩ C_j| / |C_i ∪ C_j|
  - コサイン（2 値の化合物ベクトル）|C_i ∩ C_j| / sqrt(|C_i| |C_j|)
- 味: 本人スコア 6 軸のコサイン（Exp-02 と同じ。全軸 0 の食材は除く）。参考に −ユークリッド距離も
- 共起（word2vec）: Exp-01 の食材ベクトルのコサイン
- 補い合う（complement）: What's Cooking の同一レシピ内の直接共起の PPMI。
  N = レシピ数、n_i = i を含むレシピ数、n_ij = i と j を両方含むレシピ数として
  PPMI(i, j) = max(0, log( n_ij N / (n_i n_j) ))（n_ij = 0 なら 0）。語彙は Exp-01 の word2vec と同じ（5 レシピ以上）
- 代わりに使える（substitute）: 共起の相手の分布が似ていて、直接の共起が弱いほど高い。
  ctx(i, j) = PPMI 行ベクトル r_i, r_j のコサイン。ただし i 列と j 列を除いて計算する（互いの直接の関係を文脈側に入れない）
  sub(i, j) = ctx(i, j) / (1 + PPMI(i, j))
  （ctx が同じなら直接の PPMI が高いほど下がる。閾値を置かない連続値にした。ctx 単体も参考に並べる）

手順
0. 香り化合物表の射影が論文補足 s2 と一致するかを確認
1. 香りの近さ 3 種
2. 共起（word2vec）・補い合う・代わりに使える・味・香りの近さの順位相関（Spearman）。
   対象は香りに対応でき味が全軸 0 でない食材のペア全体。同じ canonical のペアを除いた版、さらに対応先の香りデータ名が同じペアも除いた版
3. ずれの大きい組み合わせ各 10 件（共起で遠いが香りで近い / 共起で近いが香りで遠い / 味で近いが香りで遠い）と、代わりに使える近さの上位 20 件
4. mirin と calvados（対応できない場合は代替を明記して参考値）
5. Ahn らの ΔNs の追試（国籍別。頻度を保つランダム化の対照）。同じ実装を Ahn らのレシピ（s3）にもかける

成果物は results/。乱数は SEED で固定。
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
N_EXAMPLES = 10
EX_MAX_PER_CANON = 2      # ずれの例で同じ canonical が出てよい回数（olive oil のような化合物の少ない食材で埋まるのを避ける）
N_SUB_TOP = 20
N_NULL = 20                 # ΔNs のランダム化の回数（各回で全レシピを作り直す）
MIRIN_TOP = 15

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = HERE / "results"
AHN_DIR = ROOT / "data" / "raw" / "ahn2011_zenodo" / "ingr_comp"
AHN_ZIP = ROOT / "data" / "raw" / "ahn2011_zenodo" / "flavor_network_data.zip"
S2_PATH = ROOT / "data" / "raw" / "ahn2011" / "srep00196-s2.csv"
S3_PATH = ROOT / "data" / "raw" / "ahn2011" / "srep00196-s3.csv"
MAP_PATH = ROOT / "data" / "labels" / "aroma_mapping.csv"
TASTE_PATH = ROOT / "data" / "labels" / "taste_scores.csv"

EXPECTED_SHA256 = {
    AHN_ZIP: "9c58eae04fc31ba154231786a444f01e21f5e5ffd7c34a24af251f82039a6c54",
    AHN_DIR / "ingr_comp.tsv": "54ac1a13c20534ec91981e9f10d90703f78dd4c95a8eae017aea3a1b91085f24",
    AHN_DIR / "ingr_info.tsv": "5ff493a5cc680a7d5b1dde013f5de69e36f481affaabe4b24bc2acc9ede5f518",
    AHN_DIR / "comp_info.tsv": "17ae9e5034ae0bd8dcb9845af32ddefb88909d0af5bf68d96a7cf399fc1e35cc",
    S2_PATH: "7298f0224e74a1c06d29fe6711cf607fb5f130da9e5b8637303706da1f474d3b",
    S3_PATH: "34dfbe5c55eb1b227a161eb654d71012ce1c4cada7670903bd9f3fe1620ccba1",
}

# What's Cooking の 20 国籍 → Ahn らの地域（zip 内 scirep-cuisines-detail/map.txt の対応に合わせた）
CUISINE_REGION = {
    "brazilian": "LatinAmerican", "british": "WesternEuropean", "cajun_creole": "NorthAmerican",
    "chinese": "EastAsian", "filipino": "SoutheastAsian", "french": "WesternEuropean",
    "greek": "SouthernEuropean", "indian": "SouthAsian", "irish": "WesternEuropean",
    "italian": "SouthernEuropean", "jamaican": "LatinAmerican", "japanese": "EastAsian",
    "korean": "EastAsian", "mexican": "LatinAmerican", "moroccan": "African",
    "russian": "EasternEuropean", "southern_us": "NorthAmerican", "spanish": "SouthernEuropean",
    "thai": "SoutheastAsian", "vietnamese": "SoutheastAsian",
}
WESTERN = {"NorthAmerican", "WesternEuropean", "SouthernEuropean"}

# 砂糖の寄せ方の感度: build_mapping.py で cane_molasses に寄せた精製糖を none にした版
REFINED_SUGARS = {"sugar", "white sugar", "granulated sugar", "powdered sugar", "confectioners sugar"}

# 色（dataviz スキルの参照パレット）
C_POS, C_NEG = "#2a78d6", "#e34948"
C_TEXT, C_TEXT2, C_GRID = "#0b0b0b", "#52514e", "#e4e3df"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


M1B = load_module("exp01b_methods", ROOT / "experiments" / "exp-01b" / "run_methods.py")
B = M1B.B
E1 = M1B.E1
unit = E1.unit
BM = load_module("exp10_build_mapping", HERE / "build_mapping.py")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# 読み込み
# ---------------------------------------------------------------------------
def load_ahn():
    names = {}
    for line in (AHN_DIR / "ingr_info.tsv").open():
        if line.startswith("#"):
            continue
        i, n, _ = line.rstrip("\n").split("\t")
        names[int(i)] = n
    comp = collections.defaultdict(set)
    for line in (AHN_DIR / "ingr_comp.tsv").open():
        if line.startswith("#"):
            continue
        a, b = map(int, line.split())
        comp[names[a]].add(b)
    return names, dict(comp)


def check_s2(comp):
    """射影 |C_i ∩ C_j| が論文補足 s2 と一致するか。"""
    s2 = {}
    for line in S2_PATH.open():
        if line.startswith("#"):
            continue
        a, b, w = line.strip().split(",")
        s2[frozenset((a, b))] = int(w)
    keys = sorted(comp)
    mismatch = 0
    for k, w in s2.items():
        a, b = tuple(k)
        if a in comp and b in comp and len(comp[a] & comp[b]) != w:
            mismatch += 1
    missing = sum(1 for k in s2 if not all(x in comp for x in k))
    extra = 0
    for x in range(len(keys)):
        cx = comp[keys[x]]
        for y in range(x + 1, len(keys)):
            if cx & comp[keys[y]] and frozenset((keys[x], keys[y])) not in s2:
                extra += 1
    return {"s2_pairs": len(s2), "mismatch": mismatch, "missing_in_table": missing, "extra_positive_pairs": extra}


def aroma_matrices(names_list, comp):
    """names_list の順に 共有数・Jaccard・コサイン の行列。"""
    allc = sorted({c for n in names_list for c in comp[n]})
    ci = {c: k for k, c in enumerate(allc)}
    A = np.zeros((len(names_list), len(allc)))
    for r, n in enumerate(names_list):
        A[r, [ci[c] for c in comp[n]]] = 1
    shared = A @ A.T
    sizes = A.sum(1)
    union = sizes[:, None] + sizes[None, :] - shared
    jac = np.where(union > 0, shared / np.where(union > 0, union, 1), 0)
    cos = shared / np.sqrt(sizes[:, None] * sizes[None, :])
    return shared, jac, cos, sizes


def ppmi_matrix(recipes, vocab):
    """レシピ単位の直接共起の PPMI（語彙 vocab、対角 0）。"""
    idx = {t: k for k, t in enumerate(vocab)}
    V = len(vocab)
    from scipy.sparse import csr_matrix
    rows, cols = [], []
    for r_i, r in enumerate(recipes):
        ks = sorted({idx[t] for t in r["ingredients"] if t in idx})
        rows += [r_i] * len(ks)
        cols += ks
    X = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(len(recipes), V))
    C = (X.T @ X).toarray()
    n = np.diag(C).copy()
    N = len(recipes)
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log(C * N / (n[:, None] * n[None, :]))
    P = np.where((C > 0) & np.isfinite(pmi), np.maximum(pmi, 0), 0.0)
    np.fill_diagonal(P, 0.0)
    return P, C, n


def ctx_cos(P, ia, ib):
    """PPMI 行ベクトルのコサイン。i 列と j 列を除く（対角は 0 なので r_i[i] = r_j[j] = 0）。"""
    ra, rb = P[ia], P[ib]
    dot = (ra * rb).sum(1)                         # i 列: r_a[a]=0、j 列: r_b[b]=0 なので内積は変わらない
    na = (ra ** 2).sum(1) - P[ia, ib] ** 2          # r_a から j 列を除く
    nb = (rb ** 2).sum(1) - P[ib, ia] ** 2          # r_b から i 列を除く
    den = np.sqrt(np.maximum(na, 0) * np.maximum(nb, 0))
    return np.where(den > 0, dot / np.where(den > 0, den, 1), 0.0)


# ---------------------------------------------------------------------------
# ΔNs（Ahn et al. 2011）
# ---------------------------------------------------------------------------
def recipe_ns(S, idx):
    """1 レシピの N_s: 食材ペアの共有化合物数の平均。"""
    n = len(idx)
    sub = S[np.ix_(idx, idx)]
    return (sub.sum() - np.trace(sub)) / (n * (n - 1))


def delta_ns(recipes_idx, S, rng, n_null=N_NULL):
    """recipes_idx: 各レシピの食材 index（重複なし、2 個以上）。
    対照: 各レシピと同じ食材数を、そのグループ内の食材頻度に比例した確率で重複なく引く（Ahn らの frequency-conserving null）。
    戻り値: 実データの平均 N_s、対照の平均（回ごと）、ΔN_s、Z = ΔN_s / sd(対照の回ごとの平均)。"""
    real = float(np.mean([recipe_ns(S, r) for r in recipes_idx]))
    freq = collections.Counter(i for r in recipes_idx for i in r)
    ids = np.array(sorted(freq))
    p = np.array([freq[i] for i in ids], dtype=np.float64)
    p /= p.sum()
    sizes = [len(r) for r in recipes_idx]
    nulls = []
    for _ in range(n_null):
        vals = [recipe_ns(S, rng.choice(ids, size=k, replace=False, p=p)) for k in sizes]
        nulls.append(float(np.mean(vals)))
    nulls = np.array(nulls)
    sd = float(nulls.std(ddof=1))
    d = real - float(nulls.mean())
    return {"n_recipes": len(recipes_idx), "n_ingredients": int(len(ids)), "ns_real": real,
            "ns_null_mean": float(nulls.mean()), "ns_null_sd": sd, "delta_ns": d,
            "z": d / sd if sd > 0 else float("nan")}


# ---------------------------------------------------------------------------
# 図
# ---------------------------------------------------------------------------
def style_axes(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(C_TEXT2)
    ax.tick_params(colors=C_TEXT2, labelsize=8)
    ax.xaxis.label.set_color(C_TEXT)
    ax.yaxis.label.set_color(C_TEXT)


def plot_delta(wc_rows, ahn_rows, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(11, 6.8), gridspec_kw={"width_ratios": [1.5, 1]})
    for ax, rows, title in [(axes[0], wc_rows, "What's Cooking (20 cuisines, this study's mapping)"),
                            (axes[1], ahn_rows, "Ahn et al. recipes (s3), same code")]:
        rows = sorted(rows, key=lambda r: r[1])
        labels = [r[0] for r in rows]
        vals = np.array([r[1] for r in rows])
        cols = [C_POS if v >= 0 else C_NEG for v in vals]
        y = np.arange(len(rows))
        ax.barh(y, vals, color=cols, height=0.7, edgecolor="white", linewidth=1)
        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontsize=8, color=C_TEXT)
        ax.axvline(0, color=C_TEXT2, linewidth=0.8)
        ax.grid(axis="x", color=C_GRID, linewidth=0.6)
        ax.set_axisbelow(True)
        span = max(abs(vals).max(), 1e-9)
        for yi, v in zip(y, vals):
            ax.text(v + (0.02 * span if v >= 0 else -0.02 * span), yi, f"{v:+.2f}", va="center",
                    ha="left" if v >= 0 else "right", fontsize=7, color=C_TEXT2)
        ax.set_xlim(-span * 1.35 if vals.min() < 0 else -span * 0.1, span * 1.35 if vals.max() > 0 else span * 0.1)
        ax.set_xlabel("ΔNs (real − random)", fontsize=8)
        ax.set_title(title, fontsize=9, color=C_TEXT, loc="left")
        style_axes(ax)
    fig.text(0.01, 0.01, "ΔNs = mean shared compounds per ingredient pair in real recipes − in frequency-preserving random recipes. "
             "Blue: positive. Red: negative. Parentheses: Ahn et al. region.", fontsize=7.5, color=C_TEXT2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(path, dpi=150, metadata={"Software": None})
    plt.close(fig)


def plot_scatter(sv, st, sa, rhos, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(12.5, 4.2))
    axes = [fig.add_axes((0.05 + k * 0.295, 0.2, 0.24, 0.7)) for k in range(3)]
    cax = fig.add_axes((0.93, 0.2, 0.012, 0.7))
    panels = [(sv, sa, "co-occurrence (word2vec cos)", "aroma (compound cos)", rhos["w2v_aroma"]),
              (st, sa, "taste (6-axis cos)", "aroma (compound cos)", rhos["taste_aroma"]),
              (sv, st, "co-occurrence (word2vec cos)", "taste (6-axis cos)", rhos["w2v_taste"])]
    for ax, (x, y, xl, yl, r) in zip(axes, panels):
        hb = ax.hexbin(x, y, gridsize=40, bins="log", cmap="Blues", mincnt=1, linewidths=0)
        ax.set_xlabel(xl, fontsize=8)
        ax.set_ylabel(yl, fontsize=8)
        ax.set_title(f"Spearman ρ = {r:+.3f}", fontsize=9, color=C_TEXT, loc="left")
        style_axes(ax)
    cb = fig.colorbar(hb, cax=cax)
    cb.set_label("pairs per cell (log)", fontsize=8, color=C_TEXT2)
    cb.ax.tick_params(labelsize=7, colors=C_TEXT2)
    fig.text(0.01, 0.01, f"{len(sa):,} pairs (different canonical and different aroma source). "
             "Aroma cos is 0 for pairs sharing no compound.", fontsize=7.5, color=C_TEXT2)
    fig.savefig(path, dpi=150, metadata={"Software": None})
    plt.close(fig)


# ---------------------------------------------------------------------------
def main():
    import gensim, scipy, sklearn, matplotlib
    from scipy.stats import rankdata, spearmanr

    RESULTS.mkdir(parents=True, exist_ok=True)
    t_all = time.perf_counter()
    log, metrics = {}, {}
    rng = np.random.default_rng(SEED)

    # ---------------- 0. データと照合 ----------------
    log["sha256_ok"] = {str(p.relative_to(ROOT)): sha256(p) == h for p, h in EXPECTED_SHA256.items()}
    assert all(log["sha256_ok"].values()), log["sha256_ok"]
    ahn_names, comp_all = load_ahn()
    t0 = time.perf_counter()
    log["s2_check"] = check_s2(comp_all)
    log["s2_check_seconds"] = round(time.perf_counter() - t0, 1)
    comp = {k: v for k, v in comp_all.items() if k != "farnesol"}   # README の既知の問題
    log["ahn_ingredients_with_compounds"] = len(comp)
    log["ahn_compounds"] = len({c for v in comp.values() for c in v})
    sizes_all = np.array([len(v) for v in comp.values()])
    log["ahn_compounds_per_ingredient"] = {"median": float(np.median(sizes_all)), "mean": float(sizes_all.mean()),
                                           "max": int(sizes_all.max()), "min": int(sizes_all.min())}

    # 対応表は build_mapping.py の出力と一致していること（手で書き換えられていないこと）を確認
    mapping_rows = list(csv.DictReader(MAP_PATH.open()))
    assert mapping_rows == [{k: str(v) for k, v in r.items()} for r in BM.build()], "aroma_mapping.csv が build_mapping.py の出力と違う"
    amap = {r["ingredient"]: r["aroma_source_name"] for r in mapping_rows if r["method"] != "none"}
    meth = collections.Counter(r["method"] for r in mapping_rows)
    metrics["mapping"] = {"n": len(mapping_rows), **dict(meth), "coverage": (len(mapping_rows) - meth["none"]) / len(mapping_rows),
                          "n_aroma_sources": len(set(amap.values())),
                          "none": [r["ingredient"] for r in mapping_rows if r["method"] == "none"]}

    taste = {r["ingredient"]: r for r in csv.DictReader(TASTE_PATH.open())}
    ings303 = list(taste)
    recipes = B.load_recipes(log)
    wv = B.load_vectors(recipes, log)
    W0 = unit(wv.vectors).astype(np.float64)
    assert all(t in wv.key_to_index for t in ings303)

    # PPMI（語彙 = word2vec の語彙）
    t0 = time.perf_counter()
    vocab = list(wv.index_to_key)
    P, Cnt, nocc = ppmi_matrix(recipes, vocab)
    log["ppmi_vocab"] = len(vocab)
    log["ppmi_seconds"] = round(time.perf_counter() - t0, 1)
    vi = {t: k for k, t in enumerate(vocab)}

    # ---------------- 1, 2. 近さの比較 ----------------
    T = {t: np.array([float(taste[t][a]) for a in AXES]) for t in ings303}
    zero_taste = [t for t in ings303 if not T[t].any()]
    items = [t for t in ings303 if t in amap and T[t].any()]
    n = len(items)
    src = [amap[t] for t in items]
    uniq_src = sorted(set(src))
    shared_u, jac_u, cos_u, size_u = aroma_matrices(uniq_src, comp)
    si = np.array([uniq_src.index(s) for s in src])
    iu = np.triu_indices(n, 1)
    a_idx, b_idx = si[iu[0]], si[iu[1]]
    s_shared, s_jac, s_cos = shared_u[a_idx, b_idx], jac_u[a_idx, b_idx], cos_u[a_idx, b_idx]
    Tm = np.array([T[t] for t in items])
    Tu = unit(Tm)
    s_taste = (Tu @ Tu.T)[iu]
    from scipy.spatial.distance import pdist
    s_taste_euc = -pdist(Tm)
    wi = np.array([wv.key_to_index[t] for t in items])
    s_w2v = (W0[wi] @ W0[wi].T)[iu]
    pi = np.array([vi[t] for t in items])
    pa, pb = pi[iu[0]], pi[iu[1]]
    s_ppmi = P[pa, pb]
    s_ctx = ctx_cos(P, pa, pb)
    s_sub = s_ctx / (1 + s_ppmi)
    canon = np.array([taste[t]["canonical"] for t in items])
    same_c = canon[iu[0]] == canon[iu[1]]
    same_s = a_idx == b_idx
    masks = {"all": np.ones(len(s_cos), bool), "excl_same_canonical": ~same_c, "excl_same_canonical_and_source": ~same_c & ~same_s}
    measures = {"w2v": s_w2v, "ppmi": s_ppmi, "sub": s_sub, "ctx": s_ctx, "taste": s_taste, "taste_euc": s_taste_euc,
                "aroma_cos": s_cos, "aroma_jaccard": s_jac, "aroma_shared": s_shared}
    mlabel = {"w2v": "共起（word2vec cos）", "ppmi": "補い合う（直接共起 PPMI）", "sub": "代わりに使える（ctx/(1+PPMI)）",
              "ctx": "（参考）共起相手の分布の近さ ctx", "taste": "味（6 軸 cos）", "taste_euc": "味（−ユークリッド距離）",
              "aroma_cos": "香り（化合物 cos）", "aroma_jaccard": "香り（Jaccard）", "aroma_shared": "香り（共有化合物数）"}
    rho = {m: {} for m in masks}
    for mk, M in masks.items():
        for x in measures:
            for y in measures:
                if x < y:
                    rho[mk][f"{x}|{y}"] = float(spearmanr(measures[x][M], measures[y][M]).statistic)

    def R(mk, x, y):
        return rho[mk][f"{x}|{y}"] if f"{x}|{y}" in rho[mk] else rho[mk][f"{y}|{x}"]

    zero_share = {mk: float((s_shared[M] == 0).mean()) for mk, M in masks.items()}
    metrics["similarity"] = {"n_ingredients": n, "n_pairs": {mk: int(M.sum()) for mk, M in masks.items()},
                             "excluded_zero_taste": [t for t in zero_taste if t in amap],
                             "excluded_unmapped": [t for t in ings303 if t not in amap],
                             "n_aroma_sources": len(uniq_src), "share_pairs_zero_shared_compounds": zero_share,
                             "spearman": rho,
                             "definitions": {"ppmi": "max(0, log(n_ij N / (n_i n_j)))、レシピ単位",
                                             "ctx": "PPMI 行ベクトルのコサイン（i 列・j 列を除く）",
                                             "sub": "ctx / (1 + PPMI)"}}

    # ---------------- 3. ずれの例 ----------------
    MM = masks["excl_same_canonical_and_source"]
    idx_m = np.where(MM)[0]
    pct = {k: rankdata(v) / len(v) for k, v in [("w2v", s_w2v), ("taste", s_taste), ("aroma", s_cos)]}

    def pick(score, k=N_EXAMPLES):
        order = idx_m[np.argsort(-score[idx_m], kind="stable")]
        out, seen, used = [], set(), collections.Counter()
        for q in order:
            ca, cb = canon[iu[0][q]], canon[iu[1][q]]
            key = frozenset((ca, cb))
            if key in seen or used[ca] >= EX_MAX_PER_CANON or used[cb] >= EX_MAX_PER_CANON:
                continue
            seen.add(key)
            used[ca] += 1
            used[cb] += 1
            out.append(int(q))
            if len(out) == k:
                break
        return out

    ex = {"w2v_far_aroma_near": pick(pct["aroma"] - pct["w2v"]),
          "w2v_near_aroma_far": pick(pct["w2v"] - pct["aroma"]),
          "taste_near_aroma_far": pick(pct["taste"] - pct["aroma"])}

    def pair_info(q):
        a, b = items[iu[0][q]], items[iu[1][q]]
        return {"a": a, "b": b, "ja_a": taste[a]["ja"], "ja_b": taste[b]["ja"], "src_a": amap[a], "src_b": amap[b],
                "w2v": float(s_w2v[q]), "ppmi": float(s_ppmi[q]), "sub": float(s_sub[q]), "taste": float(s_taste[q]),
                "aroma_cos": float(s_cos[q]), "shared": int(s_shared[q]),
                "n_comp_a": int(size_u[a_idx[q]]), "n_comp_b": int(size_u[b_idx[q]])}
    metrics["examples"] = {k: [pair_info(q) for q in v] for k, v in ex.items()}

    # 代わりに使える近さの上位（303 食材すべて。香りの対応は問わない。同じ canonical は除く）
    all_i = np.array([vi[t] for t in ings303])
    iu3 = np.triu_indices(len(ings303), 1)
    A3, B3 = all_i[iu3[0]], all_i[iu3[1]]
    pp3 = P[A3, B3]
    ctx3 = ctx_cos(P, A3, B3)
    sub3 = ctx3 / (1 + pp3)
    canon3 = np.array([taste[t]["canonical"] for t in ings303])
    ok3 = canon3[iu3[0]] != canon3[iu3[1]]
    order = np.where(ok3)[0][np.argsort(-sub3[ok3], kind="stable")]
    T3 = unit(np.array([T[t] for t in ings303]))
    top_sub, seen = [], set()
    for q in order:
        a, b = ings303[iu3[0][q]], ings303[iu3[1][q]]
        key = frozenset((canon3[iu3[0][q]], canon3[iu3[1][q]]))
        if key in seen:
            continue
        seen.add(key)
        ac = None
        if a in amap and b in amap:
            ca, cb = comp[amap[a]], comp[amap[b]]
            ac = len(ca & cb) / np.sqrt(len(ca) * len(cb))
        top_sub.append({"a": a, "b": b, "ja_a": taste[a]["ja"], "ja_b": taste[b]["ja"], "sub": float(sub3[q]),
                        "ctx": float(ctx3[q]), "ppmi": float(pp3[q]), "n_ij": int(Cnt[A3[q], B3[q]]),
                        "w2v": float(W0[wv.key_to_index[a]] @ W0[wv.key_to_index[b]]),
                        "taste": float(T3[iu3[0][q]] @ T3[iu3[1][q]]) if T[a].any() and T[b].any() else None,
                        "aroma_cos": ac})
        if len(top_sub) == N_SUB_TOP:
            break
    metrics["substitute_top"] = top_sub

    # ---------------- 4. mirin / calvados ----------------
    mir = {"mirin_mapped": "mirin" in amap, "calvados_in_303": "calvados" in taste,
           "calvados_in_ahn": "calvados" in comp, "calvados_in_w2v_vocab": "calvados" in wv.key_to_index}
    if "calvados" in wv.key_to_index:
        mir["w2v_cos_mirin_calvados"] = float(W0[wv.key_to_index["mirin"]] @ W0[wv.key_to_index["calvados"]])
        mir["w2v_rank_of_calvados_from_mirin"] = int((W0 @ W0[wv.key_to_index["mirin"]] >
                                                      W0[wv.key_to_index["calvados"]] @ W0[wv.key_to_index["mirin"]]).sum())
        if "calvados" in vi:
            mir["ppmi_mirin_calvados"] = float(P[vi["mirin"], vi["calvados"]])
            mir["n_recipes_mirin_calvados"] = int(Cnt[vi["mirin"], vi["calvados"]])
            mir["n_recipes_calvados"] = int(nocc[vi["calvados"]])
    # 代替（参考）: みりん → sake（米の醸造酒）、カルヴァドス → apple_brandy（りんごの蒸留酒）
    proxy = {"mirin": "sake", "calvados": "apple_brandy"}
    all_names = sorted(comp)
    sh_all, jac_all, cos_all, size_all = aroma_matrices(all_names, comp)
    ks = all_names.index(proxy["mirin"])
    kc = all_names.index(proxy["calvados"])
    order_all = [k for k in np.argsort(-cos_all[ks], kind="stable") if k != ks]
    mir["proxy"] = proxy
    mir["sake_n_compounds"] = int(size_all[ks])
    mir["apple_brandy_n_compounds"] = int(size_all[kc])
    mir["sake_apple_brandy"] = {"shared": int(sh_all[ks, kc]), "jaccard": float(jac_all[ks, kc]), "cos": float(cos_all[ks, kc]),
                                "rank_among_all_ahn": order_all.index(kc) + 1, "n_ahn": len(all_names) - 1}
    mir["sake_top_all_ahn"] = [{"name": all_names[k], "cos": float(cos_all[ks, k]), "shared": int(sh_all[ks, k]),
                                "n_compounds": int(size_all[k])} for k in order_all[:MIRIN_TOP]]
    # 303 食材（対応済み）の中で sake に香りで近いもの（sake 自身と同じ対応先は除く）
    near303 = []
    for t in ings303:
        if t in amap and amap[t] != "sake":
            k = all_names.index(amap[t])
            near303.append((float(cos_all[ks, k]), int(sh_all[ks, k]), t))
    near303.sort(key=lambda x: (-x[0], x[2]))
    mir["sake_top_303"] = [{"ingredient": t, "ja": taste[t]["ja"], "source": amap[t], "cos": c, "shared": s,
                            "w2v_cos_with_mirin": float(W0[wv.key_to_index[t]] @ W0[wv.key_to_index["mirin"]])}
                           for c, s, t in near303[:MIRIN_TOP]]
    metrics["mirin"] = mir

    # ---------------- 5. ΔNs ----------------
    t0 = time.perf_counter()
    S_all = sh_all   # 全 Ahn 食材（farnesol 除く）の共有化合物数
    name_idx = {nm: k for k, nm in enumerate(all_names)}

    def wc_delta(mapping, label):
        """What's Cooking のレシピを mapping で Ahn 名に変換し、国籍別・地域別の ΔNs。"""
        res = {"cuisine": {}, "region": {}}
        by_c = collections.defaultdict(list)
        occ_total = collections.Counter()
        occ_mapped = collections.Counter()
        rec_total = collections.Counter()
        for r in recipes:
            c = r["cuisine"]
            rec_total[c] += 1
            occ_total[c] += len(r["ingredients"])
            mapped = {mapping[t] for t in r["ingredients"] if t in mapping}
            occ_mapped[c] += sum(1 for t in r["ingredients"] if t in mapping)
            if len(mapped) >= 2:
                by_c[c].append(np.array(sorted(name_idx[m] for m in mapped)))
        for c in sorted(by_c):
            d = delta_ns(by_c[c], S_all, rng)
            d.update({"region": CUISINE_REGION[c], "n_recipes_total": rec_total[c],
                      "share_recipes_dropped": 1 - d["n_recipes"] / rec_total[c],
                      "share_ingredient_occurrences_unmapped": 1 - occ_mapped[c] / occ_total[c]})
            res["cuisine"][c] = d
        by_r = collections.defaultdict(list)
        for c, lst in by_c.items():
            by_r[CUISINE_REGION[c]] += lst
        for g in sorted(by_r):
            res["region"][g] = delta_ns(by_r[g], S_all, rng)
        tot_occ = sum(occ_total.values())
        res["overall"] = {"share_ingredient_occurrences_unmapped": 1 - sum(occ_mapped.values()) / tot_occ,
                          "share_recipes_dropped": 1 - sum(len(v) for v in by_c.values()) / len(recipes),
                          "n_mapped_ingredient_strings": len(mapping), "label": label}
        return res

    # (a) 主: 303 食材の対応表
    main_res = wc_delta(amap, "303 食材の対応表（aroma_mapping.csv）")
    # (b) 感度: 精製糖を none にした版
    amap_ns = {k: v for k, v in amap.items() if k not in REFINED_SUGARS}
    sugar_res = wc_delta(amap_ns, "精製糖（sugar 等 5 種）を none にした版")
    # (c) 感度: 303 以外の食材にも自動対応（名前の正規化の完全一致のみ・未確認）を足した版
    ahn_set = set(comp)
    ext = dict(amap)
    none303 = {r["ingredient"] for r in mapping_rows if r["method"] == "none"}
    all_strings = sorted({t for r in recipes for t in r["ingredients"]})
    for t in all_strings:
        if t in ext or t in none303:
            continue
        m = BM.auto_match(t, ahn_set)
        if m:
            ext[t] = m
    ext_res = wc_delta(ext, "303 食材の対応表 + それ以外の食材の自動対応（名前の完全一致のみ、未確認）")
    # (d) Ahn らのレシピ（s3）に同じ実装
    s3 = collections.defaultdict(list)
    s3_dropped = 0
    s3_total = 0
    for line in S3_PATH.open():
        if line.startswith("#") or not line.strip():
            continue
        parts = line.strip().split(",")
        s3_total += 1
        ing = sorted({name_idx[x] for x in parts[1:] if x in name_idx})
        if len(ing) >= 2:
            s3[parts[0]].append(np.array(ing))
        else:
            s3_dropped += 1
    ahn_res = {g: delta_ns(v, S_all, rng) for g, v in sorted(s3.items())}
    metrics["delta_ns"] = {"whats_cooking": main_res, "sensitivity_refined_sugar_none": sugar_res,
                           "sensitivity_extended_auto": ext_res,
                           "ahn_s3": {"regions": ahn_res, "n_recipes": s3_total, "n_dropped_lt2": s3_dropped},
                           "n_null": N_NULL}
    log["delta_ns_seconds"] = round(time.perf_counter() - t0, 1)

    # ---------------- 図 ----------------
    plot_delta([(f"{c} ({d['region']})", d["delta_ns"]) for c, d in main_res["cuisine"].items()],
               [(g, d["delta_ns"]) for g, d in ahn_res.items()], RESULTS / "delta_ns_by_cuisine.png")
    rho_fig = {"w2v_aroma": R("excl_same_canonical_and_source", "w2v", "aroma_cos"),
               "taste_aroma": R("excl_same_canonical_and_source", "taste", "aroma_cos"),
               "w2v_taste": R("excl_same_canonical_and_source", "w2v", "taste")}
    plot_scatter(s_w2v[MM], s_taste[MM], s_cos[MM], rho_fig, RESULTS / "similarity_scatter.png")

    # ---------------- summary.md ----------------
    L = ["# Exp-10 香りの層（主要結果）", "",
         "- 香りデータ: Ahn et al. 2011 の食材×香り化合物表（Zenodo 版、CC BY 4.0。化合物の出所は Fenaroli's Handbook 第5版）。"
         f"{log['ahn_ingredients_with_compounds']} 食材 × {log['ahn_compounds']} 化合物（farnesol を食材から除いた）。"
         f"食材あたりの化合物数は中央値 {log['ahn_compounds_per_ingredient']['median']:.0f}・最大 {log['ahn_compounds_per_ingredient']['max']} と偏りが大きい",
         f"- 照合: 表を食材ペアに射影した共有化合物数が論文補足 s2 の {log['s2_check']['s2_pairs']:,} ペアと一致"
         f"（不一致 {log['s2_check']['mismatch']}、s2 に無い正のペア {log['s2_check']['extra_positive_pairs']}）",
         "- 近さの定義は run.py 冒頭。実行設定・所要時間は run_log.md、数値の全体は metrics.json", "",
         "## 0. 対応づけ", "",
         f"303 食材 → auto {meth['auto']}・manual {meth['manual']}・none {meth['none']}。**対応率 {metrics['mapping']['coverage']:.1%}**"
         f"（{len(mapping_rows) - meth['none']}/303、対応先の Ahn 食材 {metrics['mapping']['n_aroma_sources']} 種）。表は `data/labels/aroma_mapping.csv`。",
         "", "none: " + ", ".join(metrics["mapping"]["none"]), "",
         "注意: 対応は 1 対 1 で、加工・発酵・加熱による香りの違いは入らない（例: 醤油の各種 → soy_sauce、tomato paste → tomato）。"
         "唐辛子類 13 種は cayenne、精製糖は cane_molasses に寄せた（Ahn らのレシピでの使われ方から推定した寄せ方。理由は対応表の note）。", "",
         "## 1–2. 近さの順位相関", "",
         f"対象: 香りに対応でき、味が全軸 0 でない {n} 食材（対応先 {len(uniq_src)} 種）。"
         f"ペア数: 全 {masks['all'].sum():,} / 同じ canonical を除く {masks['excl_same_canonical'].sum():,} / "
         f"さらに対応先が同じペアも除く {MM.sum():,}。"
         f"最後の集合で共有化合物 0 のペアが {zero_share['excl_same_canonical_and_source']:.0%}（香りの近さに同順位が多い）。", "",
         "### 共起・味・香り（Spearman ρ）", "",
         "| 比較 | 全ペア | 同じ canonical を除く | さらに対応先が同じペアも除く |", "|---|---|---|---|"]
    for x, y in [("w2v", "taste"), ("w2v", "aroma_cos"), ("w2v", "aroma_jaccard"), ("w2v", "aroma_shared"),
                 ("taste", "aroma_cos"), ("taste", "aroma_jaccard"), ("taste", "aroma_shared"),
                 ("taste_euc", "aroma_cos"), ("aroma_cos", "aroma_jaccard"), ("aroma_cos", "aroma_shared")]:
        L.append(f"| {mlabel[x]} × {mlabel[y]} | " + " | ".join(f"{R(mk, x, y):+.3f}" for mk in masks) + " |")
    L += ["", "### 補い合う関係と代わりに使える関係（Spearman ρ、対応先が同じペアも除いた集合）", "",
          "仮説: 味・香りの近さは、補い合う関係（PPMI）より代わりに使える関係（sub）と一致しやすい。", "",
          "| 共起側の近さ | 味（cos） | 味（−ユークリッド） | 香り（cos） | 香り（Jaccard） | 香り（共有数） |", "|---|---|---|---|---|---|"]
    mk = "excl_same_canonical_and_source"
    for x in ["w2v", "ppmi", "sub", "ctx"]:
        L.append(f"| {mlabel[x]} | " + " | ".join(f"{R(mk, x, y):+.3f}" for y in
                                                  ["taste", "taste_euc", "aroma_cos", "aroma_jaccard", "aroma_shared"]) + " |")
    L += ["", "共起側どうし: " + "、".join(f"{mlabel[x]} × {mlabel[y]} {R(mk, x, y):+.3f}" for x, y in
                                          [("w2v", "ppmi"), ("w2v", "sub"), ("ppmi", "sub"), ("ctx", "sub")]),
          "", "仮説との照合（数値の比較のみ）: " + "、".join(
              f"{mlabel[y]} で sub {R(mk, 'sub', y):+.3f} / PPMI {R(mk, 'ppmi', y):+.3f} / word2vec {R(mk, 'w2v', y):+.3f}"
              for y in ["taste", "aroma_cos"]),
          "", "同じ表の全ペア版・canonical のみ除いた版は metrics.json の `similarity.spearman`。",
          "", "![similarity scatter](similarity_scatter.png)", ""]

    def ex_rows(lst):
        rows = ["| # | 食材 A | 食材 B | 香りデータ名 | 共起 cos | 味 cos | 香り cos | 共有数（化合物数 A/B） |",
                "|---|---|---|---|---|---|---|---|"]
        for i, e in enumerate(lst):
            rows.append(f"| {i+1} | {e['a']}（{e['ja_a']}） | {e['b']}（{e['ja_b']}） | {e['src_a']} / {e['src_b']} | "
                        f"{e['w2v']:.2f} | {e['taste']:.2f} | {e['aroma_cos']:.2f} | {e['shared']}（{e['n_comp_a']}/{e['n_comp_b']}） |")
        return rows
    L += ["## 3. ずれの大きい組み合わせ", "",
          "選び方: 2 つの近さの順位パーセンタイルの差の大きい順。同じ canonical・同じ対応先のペアを除き、canonical の組が重なるものは 1 件に。同じ canonical は各表で 2 回まで。"
          "香りは化合物 cos で見た。化合物数の少ない対応先（scallion 3、wheat 5 など）は cos が 0 になりやすい点に注意", "",
          "### 共起で遠いが香りで近い", ""] + ex_rows(metrics["examples"]["w2v_far_aroma_near"]) + [
          "", "### 共起で近いが香りで遠い", ""] + ex_rows(metrics["examples"]["w2v_near_aroma_far"]) + [
          "", "### 味で近いが香りで遠い", ""] + ex_rows(metrics["examples"]["taste_near_aroma_far"]) + [""]
    L += ["### 代わりに使える近さ（sub）の上位 20", "",
          "303 食材すべてが対象（香りの対応は問わない）。同じ canonical のペアを除き、canonical の組が重なるものは 1 件に。"
          "n_ij = 両方を含むレシピ数", "",
          "| # | 食材 A | 食材 B | sub | ctx | PPMI | n_ij | word2vec cos | 味 cos | 香り cos |", "|---|---|---|---|---|---|---|---|---|---|"]
    for i, e in enumerate(top_sub):
        L.append(f"| {i+1} | {e['a']}（{e['ja_a']}） | {e['b']}（{e['ja_b']}） | {e['sub']:.3f} | {e['ctx']:.3f} | {e['ppmi']:.2f} | "
                 f"{e['n_ij']} | {e['w2v']:.2f} | {'—' if e['taste'] is None else f'{e['taste']:.2f}'} | "
                 f"{'—' if e['aroma_cos'] is None else f'{e['aroma_cos']:.2f}'} |")
    L += ["", "## 4. mirin と calvados", "",
          f"- mirin は Ahn の表に項目が無く対応できなかった（none）。calvados は 303 食材に無く、Ahn の表にもその名前は無い"
          f"（What's Cooking の語彙には{'ある' if mir['calvados_in_w2v_vocab'] else '無い'}）"]
    if "w2v_cos_mirin_calvados" in mir:
        L.append(f"- 共起（word2vec）: mirin–calvados の cos {mir['w2v_cos_mirin_calvados']:+.3f}"
                 f"（mirin から見て calvados より近い語彙が {mir['w2v_rank_of_calvados_from_mirin'] - 1} 件）。"
                 f"直接共起 {mir.get('n_recipes_mirin_calvados', '—')} レシピ（calvados の出現 {mir.get('n_recipes_calvados', '—')} レシピ）")
    L += [f"- **参考（代替）**: みりんの代わりに sake（米の醸造酒、化合物 {mir['sake_n_compounds']}）、"
          f"カルヴァドスの代わりに apple_brandy（りんごの蒸留酒、化合物 {mir['apple_brandy_n_compounds']}）で見た。"
          "みりんは糖と熟成・加熱由来の香りが主で、sake とは別物。以下は「みりんの香り」ではない",
          f"- sake と apple_brandy: 共有 {mir['sake_apple_brandy']['shared']}、Jaccard {mir['sake_apple_brandy']['jaccard']:.3f}、"
          f"cos {mir['sake_apple_brandy']['cos']:.3f}。sake から見た順位 {mir['sake_apple_brandy']['rank_among_all_ahn']} 位"
          f"（Ahn の全 {mir['sake_apple_brandy']['n_ahn']} 食材中）", "",
          "sake に香りで近い食材（303 食材の対応先のうち。word2vec cos は mirin との共起側の近さ）", "",
          "| # | 食材 | 対応先 | 香り cos | 共有数 | mirin との word2vec cos |", "|---|---|---|---|---|---|"]
    for i, e in enumerate(mir["sake_top_303"]):
        L.append(f"| {i+1} | {e['ingredient']}（{e['ja']}） | {e['source']} | {e['cos']:.3f} | {e['shared']} | {e['w2v_cos_with_mirin']:+.2f} |")
    L += ["", "sake に香りで近い食材（Ahn の全食材）: " + "、".join(f"{e['name']} {e['cos']:.2f}" for e in mir["sake_top_all_ahn"][:10]), ""]

    L += ["## 5. Ahn らの ΔNs の追試", "",
          "N_s(R) = レシピ R 内の食材ペアの共有化合物数の平均。ΔN_s = 国籍内の実レシピの平均 N_s − 対照の平均 N_s。"
          f"対照は各レシピと同じ食材数を、その国籍内の食材頻度に比例した確率で重複なく引いたもの（{N_NULL} 回、Z = ΔN_s / 対照の回ごとの平均の標準偏差）。"
          "What's Cooking の食材は 303 食材の対応表で Ahn 名に変換し、対応できない食材はレシピから除いた（同じ Ahn 名に重なる食材は 1 つに）。"
          "対応食材が 2 未満のレシピは除いた", "",
          f"除いた割合（全体）: 食材の出現のうち {main_res['overall']['share_ingredient_occurrences_unmapped']:.1%}、"
          f"レシピのうち {main_res['overall']['share_recipes_dropped']:.1%}", "",
          "![delta Ns](delta_ns_by_cuisine.png)", "",
          "| 国籍 | 地域（Ahn） | ΔN_s | Z | 実 N_s | 対照 N_s | 使ったレシピ | 除いたレシピ | 除いた食材出現 | ΔN_s 精製糖 none | ΔN_s 自動拡張 |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c, d in sorted(main_res["cuisine"].items(), key=lambda kv: -kv[1]["delta_ns"]):
        L.append(f"| {c} | {d['region']} | {d['delta_ns']:+.3f} | {d['z']:+.1f} | {d['ns_real']:.2f} | {d['ns_null_mean']:.2f} | "
                 f"{d['n_recipes']:,} | {d['share_recipes_dropped']:.1%} | {d['share_ingredient_occurrences_unmapped']:.1%} | "
                 f"{sugar_res['cuisine'][c]['delta_ns']:+.3f} | {ext_res['cuisine'][c]['delta_ns']:+.3f} |")
    L += ["", "地域でまとめた版（国籍のレシピを合わせ、地域内の頻度で対照を作る）と、同じ実装を Ahn らのレシピ（s3）にかけた値", "",
          "| 地域 | What's Cooking ΔN_s | Z | 精製糖 none | 自動拡張 | Ahn s3 ΔN_s | Ahn s3 Z | Ahn s3 レシピ数 |", "|---|---|---|---|---|---|---|---|"]
    for g in sorted(set(main_res["region"]) | set(ahn_res)):
        w = main_res["region"].get(g)
        a = ahn_res.get(g)
        L.append(f"| {g} | " + (f"{w['delta_ns']:+.3f} | {w['z']:+.1f} | {sugar_res['region'][g]['delta_ns']:+.3f} | "
                                f"{ext_res['region'][g]['delta_ns']:+.3f}" if w else "— | — | — | —") +
                 " | " + (f"{a['delta_ns']:+.3f} | {a['z']:+.1f} | {a['n_recipes']:,}" if a else "— | — | —") + " |")
    west = [d["delta_ns"] for c, d in main_res["cuisine"].items() if d["region"] in WESTERN]
    east = [d["delta_ns"] for c, d in main_res["cuisine"].items() if d["region"] == "EastAsian"]
    L += ["", f"- 西洋（NorthAmerican・WesternEuropean・SouthernEuropean の国籍 {len(west)}）: 正 {sum(v > 0 for v in west)} / 負 {sum(v < 0 for v in west)}",
          f"- 東アジア（chinese・japanese・korean）: 正 {sum(v > 0 for v in east)} / 負 {sum(v < 0 for v in east)}",
          f"- 自動拡張版の除いた食材出現 {ext_res['overall']['share_ingredient_occurrences_unmapped']:.1%}"
          f"（対応した食材文字列 {ext_res['overall']['n_mapped_ingredient_strings']:,}）。自動拡張分は目視していない",
          f"- Ahn s3: {s3_total:,} レシピ中、Ahn 表の食材が 2 未満で除いたもの {s3_dropped:,}", ""]
    (RESULTS / "summary.md").write_text("\n".join(L))

    # ---------------- metrics / run_log ----------------
    (RESULTS / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=1, default=float))
    log["total_seconds"] = round(time.perf_counter() - t_all, 1)
    RL = ["# Exp-10 run_log", "",
          f"- 実行: `uv run python experiments/exp-10/run.py`（{time.strftime('%Y-%m-%d')}）",
          f"- Python {platform.python_version()}, numpy {np.__version__}, scipy {scipy.__version__}, gensim {gensim.__version__}, "
          f"scikit-learn {sklearn.__version__}, matplotlib {matplotlib.__version__}",
          f"- SEED {SEED}、ΔN_s の対照 {N_NULL} 回",
          f"- 所要時間: 全体 {log['total_seconds']} 秒（s2 照合 {log['s2_check_seconds']} 秒、PPMI {log['ppmi_seconds']} 秒、ΔN_s {log['delta_ns_seconds']} 秒）",
          "", "```json", json.dumps({k: v for k, v in log.items() if not k.endswith("seconds")}, ensure_ascii=False, indent=1), "```", ""]
    (RESULTS / "run_log.md").write_text("\n".join(RL))
    print(f"done {log['total_seconds']}s")


if __name__ == "__main__":
    main()
