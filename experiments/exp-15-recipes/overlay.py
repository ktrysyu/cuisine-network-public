"""Exp-15: 世の中のレシピ（recipes.csv の map_ok=yes の行）を Exp-14 の地図に重ねる。

    uv run python experiments/exp-15-recipes/overlay.py

- 各行の (温度, 時間) = (map_T_c, map_time_min) を、卵の形（map_egg_form）に合う Exp-14 の地図（sim/maps.py の PRESETS）に置き、
  **その点ちょうど**で Exp-14 のシミュレータを走らせた判定（maps.cell）を「計算の答え」とする。地図のマスに丸めない。
- 計算・レシピの値は合わせ込まない。判定は Exp-14 のまま（rules.yaml・NO_MATCH_BELOW も変えない）。
- 一致しない点には理由の候補を付ける。候補を確かめるための別計算（推定の幅の端・時間の幅の端・手順を変えた場合）は
  「参考」として別の列に出すだけで、一致・不一致の集計には使わない。
- 書き出し: overlay.json（writeup/cook-lab.html に埋め込む。exp-14/js/build_page.py が読む）、overlay.md、figures/overlay.png
"""
from __future__ import annotations

import copy
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP14 = HERE.parent / "exp-14"
sys.path.insert(0, str(EXP14))

from run import NO_MATCH_BELOW  # noqa: E402
from sim import maps  # noqa: E402
from sim import params as P  # noqa: E402

CSV = HERE / "recipes.csv"
OUT_JSON = HERE / "overlay.json"
OUT_MD = HERE / "overlay.md"
OUT_PNG = HERE / "figures" / "overlay.png"

# 卵の形 → Exp-14 の地図
FORM_TO_MAP = {"shell": "shell_egg", "cracked": "poach", "beaten": "beaten_pan", "custard_mix": "pudding"}
# 料理で地図を選び直すもの（2026-09-28 夜 Q6 (d)）。スクランブルエッグは混ぜながら焼くので、混ぜる元のレシピの地図に置く
DISH_TO_MAP = {"scrambled_eggs": "beaten_stir"}
# 殻付き卵は後の手順（recipes.csv の after_step）で地図を選ぶ（余熱、Exp-14 rules.md §10 2026-09-28 夜）。
# 書いていない（none）は「室温に置く」とみなす。冷水・流水（cold）は氷水の地図に置き、後の手順の水温だけ 15℃にして計算する
AFTER_TO_MAP = {"none": "shell_egg", "ice": "shell_egg_ice", "cold": "shell_egg_ice"}
AFTER_JA = {"none": "書いていない（室温に置く）", "ice": "氷水に取る", "cold": "冷水・流水に取る（15℃）"}
COLD_WATER_T = 15  # 推定（Exp-14 sim/recipes.py AFTER_COLD と同じ）
PRESET = {p["id"]: p for p in maps.PRESETS}

# 料理ごとの点の形（ページ・図で共通）。soft_boiled_egg は Exp-14 に無い料理（exp-15 で置いた id）
SHAPE = {"soft_boiled_egg": "circle", "hard_boiled_egg": "square", "poached_egg": "diamond",
         "scrambled_eggs": "triangle", "custard_pudding": "triangle_down"}
DISH_JA = {"soft_boiled_egg": "半熟ゆで卵", "hard_boiled_egg": "ゆで卵（固ゆで）", "poached_egg": "ポーチドエッグ",
           "scrambled_eggs": "スクランブルエッグ", "custard_pudding": "プリン", "onsen_tamago": "温泉卵",
           "omelet": "オムレツ", maps.NONE: "該当なし", maps.RAW: "生のまま（変化なし）"}

# 理由の候補の種類（overlay.md の表の列の順）
REASONS = {
    "T_EST": "温度の推定",
    "T_COUNT": "時間の数え始め",
    "RULE": "計算の規則",
    "DEF": "料理の定義",
    "BASE": "地図の前提（元のレシピの手順）",
}


def _f(v: str):
    return float(v) if v not in ("", None) else None


def point_cell(preset: dict, T: float, t: float, mod=None) -> dict:
    """地図 preset の元のレシピを (T, t) にしたものの判定。mod(recipe) で手順を変えられる（参考の別計算用）。"""
    b = maps.base_recipe(preset["base"])
    if mod:
        mod(b)
    r = maps.with_value(maps.with_value(b, preset["x"]["axis"], T), preset["y"]["axis"], t)
    return maps.cell(r, NO_MATCH_BELOW)


def point_state(preset: dict, T: float, t: float, mod=None):
    """点の最後の状態（理由の説明に段階の値を出すため）。"""
    b = maps.base_recipe(preset["base"])
    if mod:
        mod(b)
    r = maps.with_value(maps.with_value(b, preset["x"]["axis"], T), preset["y"]["axis"], t)
    return maps.run_json(r)[1]


def _stir(b):  # 溶き卵の地図の元（オムレツ）は混ぜない。スクランブルエッグの手順どおり混ぜた場合
    b["steps"][1][1]["stirring"] = True


def _vinegar(b):  # ポーチの地図の元は酢・塩なし。exp-15 で割合が出せた唯一の値（大さじ1/水1 L＝1.5%）を入れた場合
    b["steps"][0][1]["vinegar_pct"] = 1.5


def base_mod_of(r: dict) -> dict | None:
    """地図の元のレシピから変える欄（JS の一致テストも同じものを当てる）。冷水・流水に取る行は後の手順の水温。"""
    if r.get("after_step") == "cold":
        return {"i": 1, "key": "T", "value": COLD_WATER_T}
    return None


def _apply(bm):
    if bm is None:
        return None

    def f(b):
        b["steps"][bm["i"]][1][bm["key"]] = bm["value"]
    return f


def _to_ice(b):  # 参考: 書いていない行を「すぐ氷水に取った」場合（地図 shell_egg_ice の元のレシピの後の手順）
    b["steps"][1] = ["plunge", {"T": 0, "time": b["steps"][1][1]["time"]}]


def _to_rest(b):  # 参考: 水に取る行を「室温に置いた」場合
    b["steps"][1] = ["rest", {"T": 20, "time": b["steps"][1][1]["time"]}]


def load_rows() -> list[dict]:
    with CSV.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r["map_ok"].startswith("yes")]


def reasons_for(r: dict, c: dict, sens: set, alt: dict | None) -> list[list[str]]:
    """不一致の点の理由の候補 [[種類, 説明], ...]。規則は機械的（行の列と計算結果から）。"""
    out = []
    dish, ans = r["dish"], c["cls"]
    est = r["T_is_estimate"] == "yes"
    if dish not in P.dishes():
        out.append(["DEF", f"Exp-14 に「{DISH_JA[dish]}」が無い。どこに置いても一致しない"])
    if est:
        rng = f"{r['T_est_lo_c']}〜{r['T_est_hi_c']}℃" if r["T_est_lo_c"] else ""
        hit = " 推定の幅・時間の幅の端では一致する答えがある" if dish in sens else ""
        out.append(["T_EST", f"温度は推定（{r['T_rule']}、中心 {r['map_T_c']}℃ {rng}）。{r['T_phrase'] or r['T_raw']}".strip() + ("。" + hit.strip() if hit else "")])
    tc = r["time_counts"]
    if any(k in tc for k in ("再沸騰", "不明", "まで", "段階", "含めない", "合計")):
        out.append(["T_COUNT", f"時間の数え始め: {tc}。地図の時間は湯・鍋に入れてからの時間"])
    if r["map_egg_form"] == "shell" and ans in ("onsen_tamago", maps.NONE, maps.RAW, "soft_boiled_egg", "hard_boiled_egg"):
        s = point_state(PRESET[AFTER_TO_MAP[r["after_step"]]], float(r["map_T_c"]), float(r["map_time_min"]), _apply(base_mod_of(r)))
        if s.egg_kin is not None:
            gw, _ = s.egg_kin.layer_stats("white")
            gy, _ = s.egg_kin.layer_stats("yolk")
            how = (f"殻付き卵は場所ごとの変性度から卵白・卵黄の段階を決める（Exp-17、2026-09-30 から既定）。後の手順は{AFTER_JA[r['after_step']]}で、余熱を含めて"
                   f"固まった割合 卵白 {gw:.2f}・卵黄 {gy:.2f}、中心 最高 {s.T_core_max:.1f}℃")
        else:
            how = (f"殻付き卵は卵白を卵白の層の温度、卵黄を中心の温度で決める（Exp-14 rules.md §10 修正 B）。後の手順は{AFTER_JA[r['after_step']]}で、余熱を含めて"
                   f"卵白の層 最高 {s.T_white_max:.1f}℃・中心 最高 {s.T_core_max:.1f}℃")
        out.append(["RULE", how + f"、卵白 {s.egg_white_stage}・卵黄 {s.egg_yolk_stage}"
                    + ("。卵白が固まり卵黄がやわらかく固まった（卵黄 2）状態で、半熟ゆで卵（卵黄 0〜1）と固ゆで（卵黄 3）の間。必須条件を満たす料理が無い" if (s.egg_white_stage, s.egg_yolk_stage) == (3, 2) else "")])
    if r["map_egg_form"] == "beaten":
        if DISH_TO_MAP.get(dish, FORM_TO_MAP["beaten"]) == "beaten_pan":
            a = alt["cls"] if alt else None
            out.append(["BASE", "溶き卵の地図の元はオムレツ（混ぜない）。スクランブルエッグの必須「固まり方＝小片」は混ぜないと出ない"
                        + (f"。参考: 手順どおり混ぜた場合の答え＝{DISH_JA.get(a, a)}" if a else "")])
        else:
            out.append(["BASE", "地図の元はスクランブルエッグ（牛乳・バター入り、110℃で混ぜながら）。材料の割合・火加減の細部はレシピと違う"])
        out.append(["RULE", "フライパンの鍋肌の温度→卵液の温度は時定数の推定（Exp-14 sim.heat_transfer、出典なし）"])
    return out


def cautions_for(r: dict, c: dict, alt: dict | None) -> list[str]:
    """一致した点でも、答えの中身に既知の問題があるもの（maps.md の「おかしな領域」に当たる）。"""
    out = []
    T = float(r["map_T_c"])
    if r["dish"] == "custard_pudding" and T >= 100:
        out.append("100℃で蒸すと す が立つ（porosity）が、す は必須条件ではないのでプリンと答える（maps.md §6）")
    if r["dish"] == "poached_egg":
        coh_T_min = P.V("poach_cohesion_T_min")
        if T < coh_T_min:
            out.append(f"湯温 {T:g}℃ は {coh_T_min}℃ 未満で、卵白は「ばらける」（R-E21）。まとまりは必須ではないのでポーチドエッグと答える")
        elif T >= 100 and r["vinegar"] != "yes":
            out.append("沸騰した湯で酢・塩なしは「ばらける」（R-E21）")
        if T >= 100 and r["vinegar"] == "yes":
            out.append("沸騰した湯。地図の元は酢なしで「ばらける」。レシピどおり酢を入れると「まとまる（表面に膜・ちぎれ）」（R-E22）")
    return out


def build() -> dict:
    rows = load_rows()
    pts = []
    for r in rows:
        mid = DISH_TO_MAP.get(r["dish"], FORM_TO_MAP[r["map_egg_form"]])
        if r["map_egg_form"] == "shell":
            mid = AFTER_TO_MAP[r["after_step"]]
        pre = PRESET[mid]
        bm = base_mod_of(r)
        T, t = float(r["map_T_c"]), float(r["map_time_min"])
        c = point_cell(pre, T, t, _apply(bm))
        Tlo, Thi = _f(r["T_est_lo_c"]) or T, _f(r["T_est_hi_c"]) or T
        tlo, thi = _f(r["time_min_lo"]) or t, _f(r["time_min_hi"]) or t
        sens = sorted({point_cell(pre, a, b, _apply(bm))["cls"] for a in (Tlo, T, Thi) for b in (tlo, t, thi)})
        alt = None
        if mid == "shell_egg":
            alt = {"what": "すぐ氷水に取った場合", **point_cell(pre, T, t, _to_ice)}
        elif mid == "shell_egg_ice":
            alt = {"what": "室温に置いた場合", **point_cell(pre, T, t, _to_rest)}
        elif mid == "beaten_pan":
            alt = {"what": "手順どおり混ぜた場合（stirring=true）", **point_cell(pre, T, t, _stir)}
        elif mid == "poach" and r["vinegar"] in ("yes", "optional"):
            alt = {"what": "湯に酢 1.5% を入れた場合", **point_cell(pre, T, t, _vinegar)}
        match = c["cls"] == r["dish"]
        pts.append({
            "row_id": r["row_id"], "map": mid, "after_step": r["after_step"], "base_mod": bm, "dish": r["dish"], "dish_ja": DISH_JA[r["dish"]], "shape": SHAPE[r["dish"]],
            "x": T, "y": t, "estimate": r["T_is_estimate"] == "yes",
            "T_rule": r["T_rule"], "T_range": [Tlo, Thi], "time_range": [tlo, thi],
            "T_raw": r["T_raw"], "time_raw": r["time_raw"], "time_counts": r["time_counts"],
            "T_basis": r["T_est_basis"] if r["T_is_estimate"] == "yes" else f"原文の数値（{r['T_stated_c']}℃）",
            "source": r["source"], "page_title": r["page_title"], "method": r["method"], "permalink": r["permalink"],
            "quote": r["quote"], "vinegar": r["vinegar"], "independence_group": r["independence_group"],
            "answer": c["cls"], "answer_ja": DISH_JA.get(c["cls"], c["cls"]), "top": c["top"], "second": c["second"],
            "margin": round(c["margin"], 6), "match": match,
            "sensitivity": sens,
            "alt": ({"what": alt["what"], "answer": alt["cls"], "answer_ja": DISH_JA.get(alt["cls"], alt["cls"]), "top": alt["top"]} if alt else None),
            "reasons": [] if match else reasons_for(r, c, set(sens), alt),
            "cautions": cautions_for(r, c, alt) if match else [],
        })
    return {
        "about": "Exp-15 のレシピ（map_ok=yes）を Exp-14 の地図に重ねた点。experiments/exp-15-recipes/overlay.py が生成。手で直さない。",
        "no_match_below": NO_MATCH_BELOW,
        "reason_kinds": REASONS,
        "points": pts,
    }


# ---------------- 集計・文書 ----------------

def tally(pts: list[dict]):
    t = defaultdict(lambda: Counter())
    for p in pts:
        k = (p["dish"], "推定" if p["estimate"] else "数値")
        t[k]["n"] += 1
        t[k]["match"] += p["match"]
    return t


def pct(a, b):
    return f"{a}/{b}（{100 * a / b:.0f}%）" if b else "—"


def write_md(d: dict) -> str:
    pts = d["points"]
    n, m = len(pts), sum(p["match"] for p in pts)
    in14 = [p for p in pts if p["dish"] in P.dishes()]
    m14 = sum(p["match"] for p in in14)
    groups = {}
    for p in pts:
        groups.setdefault(p["independence_group"], []).append(p)
    gm = sum(all(p["match"] for p in g) for g in groups.values())
    t = tally(pts)
    L = []
    A = L.append
    A("# Exp-15 世の中のレシピを Exp-14 の地図に重ねる")
    A("")
    A("`overlay.py` が生成（手で直さない）。2026-09-28。`recipes.csv` の `map_ok=yes` の 28 行を、卵の形に合う Exp-14 の地図"
      "（`experiments/exp-14/sim/maps.py` の PRESETS）に点として置き、**その点ちょうど**の計算の答え（判定の1位）とレシピの料理を比べた。")
    A("")
    A("- 計算・レシピの値は合わせ込んでいない。判定は Exp-14 のまま（必須条件＋下限 0.6）。点の温度は `map_T_c`（原文の数値の中央、無ければ換算表の推定の中心）、時間は `map_time_min`")
    A("- 「参考」の列（推定・時間の幅の端での答え、手順を変えた場合の答え）は理由の候補を確かめるためだけに出した。一致・不一致の集計には使っていない")
    A("- 殻付き卵は後の手順（`recipes.csv` の `after_step`、`techniques` から機械的に読んだ）で地図を選ぶ: 氷水・冷水・流水に取る行は「氷水に取る」の地図（冷水・流水は後の手順の水温を 15℃にして計算）、書いていない行は「室温に置く」の地図（Exp-14 rules.md §10 2026-09-28 夜「余熱」）。参考の列に、逆の後の手順（すぐ氷水／室温に置く）での答えを出した")
    A("- 図: `figures/overlay.png`（地図6枚。塗りは Exp-14 の地図と同じ、点の形・色は料理、中抜きは温度が推定、塗りつぶしは原文に数値）。ページ: `writeup/cook-lab.html` の地図で「世の中のレシピを重ねる」")
    A("")
    A("## 1. 一致率")
    A("")
    A(f"- 全体: **{pct(m, n)}**")
    if len(in14) != n:
        A(f"- Exp-14 にある料理だけ: **{pct(m14, len(in14))}**")
    A(f"- 独立の目安（`independence_group` ごと、束の全行が一致なら一致）: {pct(gm, len(groups))}")
    A(f"- 温度が原文の数値の点は 1 行（R021）だけで、推定と数値を比べられるほどの数はない")
    A("")
    A("| 料理 | 地図 | 温度が推定 | 温度が原文の数値 | 計 |")
    A("|---|---|---|---|---|")
    order = ["soft_boiled_egg", "hard_boiled_egg", "poached_egg", "scrambled_eggs", "custard_pudding"]
    mapja = {p["id"]: p["title"] for p in maps.PRESETS}
    for dish in order:
        e, s = t[(dish, "推定")], t[(dish, "数値")]
        mids = sorted({p["map"] for p in pts if p["dish"] == dish}, key=[q["id"] for q in maps.PRESETS].index)
        A(f"| {DISH_JA[dish]} | {'／'.join(mapja[mm] for mm in mids)} | {pct(e['match'], e['n'])} | {pct(s['match'], s['n'])} | {pct(e['match'] + s['match'], e['n'] + s['n'])} |")
    A("")
    A("## 2. 点ごとの答え")
    A("")
    A("| 行 | レシピの料理 | 出典 | 温度（℃） | 時間（分） | 後の手順 | 計算の答え（満たした割合） | 一致 | 参考: 幅の端での答え | 参考: 手順を変えた場合 |")
    A("|---|---|---|---|---|---|---|---|---|---|")
    for p in pts:
        top = f"{p['top'][1]}/{p['top'][2]}" if p["top"] else "—"
        T = f"{p['x']:g}" + ("（推定 " + f"{p['T_range'][0]:g}〜{p['T_range'][1]:g}、{p['T_rule']}）" if p["estimate"] else "（原文）")
        tm = f"{p['y']:g}" + (f"（{p['time_range'][0]:g}〜{p['time_range'][1]:g}）" if p["time_range"][0] != p["time_range"][1] else "")
        sens = "・".join(DISH_JA.get(s, s) for s in p["sensitivity"])
        alt = f"{p['alt']['what']}: {p['alt']['answer_ja']}" if p["alt"] else ""
        src = p["page_title"].replace("Cookbook:", "") + (f"（{p['method']}）" if p["method"] not in ("", "-") else "")
        aft = AFTER_JA[p["after_step"]] if p["after_step"] else "—"
        A(f"| {p['row_id']} | {p['dish_ja']} | {src} | {T} | {tm} | {aft} | {p['answer_ja']}（{top}） | {'○' if p['match'] else '×'} | {sens} | {alt} |")
    A("")
    A("## 3. 一致しない点と理由の候補")
    A("")
    A("候補は行の列（推定か・数え始め）と計算の中身から機械的に付けた。どれが本当の理由かは確かめていない。")
    A("")
    A("| 行 | レシピ → 計算 | " + " | ".join(REASONS.values()) + " |")
    A("|---|---|" + "---|" * len(REASONS))
    for p in pts:
        if p["match"]:
            continue
        cols = []
        for k in REASONS:
            txt = "；".join(x for kk, x in p["reasons"] if kk == k)
            cols.append(txt.replace("|", "／") or "")
        A(f"| {p['row_id']} | {p['dish_ja']} → {p['answer_ja']} | " + " | ".join(cols) + " |")
    A("")
    A("## 4. 一致したが中身に注意がある点")
    A("")
    for p in pts:
        if p["match"] and p["cautions"]:
            A(f"- {p['row_id']}（{p['dish_ja']}、{p['x']:g}℃・{p['y']:g}分）: " + "；".join(p["cautions"]))
    A("")
    A("## 5. 所見")
    A("")
    for line in FINDINGS:
        A(f"- {line}")
    A("")
    return "\n".join(L)


# 所見（計算結果を見た後に書いた。数字は上の表から）
FINDINGS = [
    "**殻付き卵の計算を熱伝導＋変性の反応速度（Exp-17）に切り替えた後（2026-09-30、本人決定で既定に）**: 全体 22/28 → **21/28**、独立の目安 17/22 のまま。"
    "変わったのは半熟ゆで卵 R006（Tonkotsu Ramen、沸騰 7 分→氷水）が 半熟ゆで卵 → 該当なし の 1 行だけ（沸騰 7 分で黄身の半分以上が固まり卵黄 2）。"
    "以下の所見は切り替える前に書いたもの",
    "**余熱（2026-09-28 夜、Exp-14 rules.md §10「余熱」）の前後**: 全体 20/28 → **22/28**、独立の目安 15/22 → 17/22。殻付き卵を取り出した後の温度（室温に置く／水に取る）を計算に入れ、後の手順を `after_step` で読んだ。固ゆで卵は 1/7 → **6/7**（R011・R014・R015・R016・R017 が固ゆでに戻った。残る R013 は再沸騰から 9分＋氷水で卵黄 2、時間の数え始めの候補は前のまま）。**半熟ゆで卵は 5/5 → 2/5**: 氷水・冷水に取る R006・R007 は半熟のまま、後の手順を書いていない R002・R005・R008 は「室温に置く」とみなした余熱で中心が 70℃を超え卵黄 2（該当なし）。3 行とも「すぐ氷水に取った場合」は半熟ゆで卵。書いていない＝置く、は変更前に決めた扱い（rules.md §10）で、結果を見て変えていない。なお R002・R005 の出典ページ（Cookbook:Soft Boiled Eggs）は、方法ごとの手順の外の「Tips」に「Running the cooked eggs under cold water will help stop the cooking process」と任意の助言として書いている（`techniques` は方法ごとの手順から読んだので none のまま）。割った卵・溶き卵・プリン液の 16 行は変わらない",
    "**Q6（2026-09-28 夜、Exp-14 rules.md §10、余熱の前）の前後**: 全体 21/28 → **20/28**。殻付き卵の温度を球の熱伝導の解にして固ゆで卵が 6/7 → **1/7**（沸騰 9〜12.5分の中心が 80℃に届かず卵黄 2。R011・R014・R017 は該当なし、R015・R016 は半熟ゆで卵、R013 は該当なし→半熟ゆで卵）。スクランブルエッグは混ぜながら焼く地図（beaten_stir）に置き直して 0/6 → **4/6**（R029・R034・R037・R038。R032 230℃0.24分は生のまま、R036 175℃0.75分は該当なし）。半熟ゆで卵 5/5・ポーチドエッグ 6/6・プリン 4/4 は同じ。以下の項目のうち修正 B までの記述は Q6 の前の数",
    "**修正 B（2026-09-28、Exp-14 rules.md §10）の前後**: 全体 16/28（57%）→ **21/28（75%）**、独立の目安 13/22 → 15/22。変わったのは殻付き卵の 6 行だけ（半熟ゆで卵 R002 該当なし・R005〜R008 温泉卵 → 5 行とも半熟ゆで卵、固ゆで R013 温泉卵 → 該当なし）。割った卵・溶き卵・プリン液の 16 行は答えも満たした数も同じ",
    "**半熟ゆで卵の 5/5 には自己参照が入っている**。修正 B（殻付き卵の卵白を卵白の層の温度で決める）だけでは 5 行とも「該当なし」（温泉卵とゆで卵の間）で、料理 `soft_boiled_egg` を足して一致した。定義の必須条件（卵白 3・卵黄 0〜1・殻付き）は一般の出典（R-E03・R-E05・wiki_boiled）から、表面 95〜100℃ はこの 5 行が沸騰の湯か蒸しであることから、正解のレシピ（沸騰 6.5分）は R007 から採った。「世の中のレシピが計算と合う」証拠としては、修正 B の後に温泉卵と答えなくなった（卵白が固まる）ことまでが独立な部分",
    "**固ゆで卵とポーチドエッグは、レシピの条件の上で計算もその料理と答える**（固ゆで 6/7、ポーチドエッグ 6/6）。どちらも温度は推定が主（固ゆでは全行が沸騰の換算、ポーチドエッグは 6 行中 5 行）",
    "**固ゆで卵の外れ 1 件（R013 Tonkotsu Ramen、再沸騰から 9 分）は、修正 B で温泉卵から該当なしに変わった**。卵白 3・卵黄 2（中心 70〜80℃）で、半熟ゆで卵（卵黄 0〜1）と固ゆで（卵黄 3）の間。時間の数え始めの候補は前と同じく強い（地図では 100℃ の殻付き卵は 10 分から固ゆで。再沸騰までの時間を数えていない）",
    "**スクランブルエッグ 6 行はどれも一致しない**（修正 B の影響なし）。溶き卵の地図の元はオムレツ（混ぜない）で、スクランブルエッグの必須（小片）は出ない。参考に手順どおり混ぜると 2 行（R029 175℃1.75分・R034 200℃0.75分）がスクランブルエッグになり、残りは該当なし・生のまま。フライパンの温度はすべて推定（根拠が一番弱い換算）",
    "**プリン 4 行はすべて一致するが、100℃で蒸す 3 行は計算上 す が立っている**（す は必須ではない）。レシピ（Coconut Pudding II・Watalappam・Kuih Seri Muka）は沸騰した湯の蒸し器と読んだ推定（S-STEAM）で、実際の蒸し器の中が 100℃ かは分からない",
    "**ポーチドエッグの R021（原文 70–80°C、唯一の数値）は、計算では卵白が「ばらける」**（80℃未満、R-E21）。まとまりは必須ではないのでポーチドエッグと答える。Wikibooks の 70–80°C と R-E21 の出典（terumimorita「70℃では固まりきらない」）の食い違いは C13 のとおり",
    "一致率はレシピの料理と判定の1位が同じかだけを見ている。点の温度の大半が推定なので、「世の中のレシピが計算と合っている」証拠としては弱い。原文に数値がある点は 28 行中 1 行",
]


# ---------------- 図 ----------------

COLORS = {  # page_template.html の --d-* と同じ（ライト）。soft_boiled_egg は地図に無い料理なので新しく置いた色
    "onsen_tamago": "#2a78d6", "hard_boiled_egg": "#eb6834", "poached_egg": "#1baf7a", "scrambled_eggs": "#eda100",
    "omelet": "#e87ba4", "custard_pudding": "#008300", "chawanmushi": "#4a3aa7", "pancake": "#e34948",
    maps.NONE: "#b3b8b4", maps.RAW: "#DCE0DC", "soft_boiled_egg": "#6b4fb3",
}
MARKER = {"circle": "o", "square": "s", "diamond": "D", "triangle": "^", "triangle_down": "v"}


def draw_png(d: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager as fm
    from matplotlib.colors import to_rgba
    from matplotlib.lines import Line2D

    for name in ("Noto Sans CJK JP", "IPAGothic"):
        if any(f.name == name for f in fm.fontManager.ttflist):
            plt.rcParams["font.family"] = name
            break
    fig, axes = plt.subplots(2, 3, figsize=(20, 10.5), dpi=110)
    for ax in list(axes.flat)[len(maps.PRESETS):]:
        ax.axis("off")
    for ax, pre in zip(axes.flat, maps.PRESETS):
        g = maps.preset_grid(pre, NO_MATCH_BELOW)
        xs, ys = g["xs"], g["ys"]
        dx, dy = pre["x"]["step"], pre["y"]["step"]
        for j, row in enumerate(g["cells"]):
            for i, c in enumerate(row):
                a = 1.0 if c["cls"].startswith("__") else 0.3 + 0.7 * min(1, c["margin"] / 0.4)
                rgba = to_rgba(COLORS.get(c["cls"], "#999999"), a)
                ax.add_patch(plt.Rectangle((xs[i] - dx / 2, ys[j] - dy / 2), dx, dy, facecolor=rgba, edgecolor="none",
                                           hatch="///" if c["cls"] == maps.RAW else None))
        ax.set_xlim(xs[0] - dx / 2, xs[-1] + dx / 2)
        ax.set_ylim(ys[0] - dy / 2, ys[-1] + dy / 2)
        pts = [p for p in d["points"] if p["map"] == pre["id"]]
        # 点: 外側に濃い輪（同じ色の塗りの上でも見えるように）、内側に料理の色。中抜き＝温度が推定
        for p in pts:
            col = COLORS[p["dish"]]
            ax.scatter([p["x"]], [p["y"]], marker=MARKER[p["shape"]], s=120, linewidths=3.6, facecolors="none", edgecolors="#1A1F1C", zorder=3)
            ax.scatter([p["x"]], [p["y"]], marker=MARKER[p["shape"]], s=120, linewidths=1.8,
                       facecolors="white" if p["estimate"] else col, edgecolors=col, zorder=4)
        # ラベル: 同じ温度に重なる点は、左に縦に並べて線で結ぶ（点の位置は動かさない）
        span = ys[-1] - ys[0]
        byx = defaultdict(list)
        for p in pts:
            byx[p["x"]].append(p)
        for x0, grp in byx.items():
            grp.sort(key=lambda p: p["y"])
            gap = span * 0.045
            ly = []
            for p in grp:
                ly.append(max(p["y"], ly[-1] + gap) if ly else p["y"])
            crowded = len(grp) > 1 and min(b["y"] - a["y"] for a, b in zip(grp, grp[1:])) < gap
            for p, yy in zip(grp, ly):
                mark = "○" if p["match"] else "×"
                txt = f"{p['row_id']} {mark}"
                if crowded:
                    ax.annotate(txt, (p["x"], p["y"]), xytext=(x0 - (xs[-1] - xs[0]) * 0.12, yy), textcoords="data", fontsize=7.5, zorder=5,
                                va="center", ha="right", arrowprops=dict(arrowstyle="-", lw=0.6, color="#1A1F1C"),
                                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
                else:
                    ax.annotate(txt, (p["x"], p["y"]), xytext=(-8, 0), textcoords="offset points", fontsize=7.5, zorder=5, va="center", ha="right",
                                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
        m = sum(p["match"] for p in pts)
        ax.set_title(f"{pre['title']}　一致 {m}/{len(pts)}", fontsize=11)
        xl = "フライパンの温度（℃）" if pre["id"] in ("beaten_pan", "beaten_stir") else ("蒸す温度（℃）" if pre["id"] == "pudding" else "湯の温度（℃）")
        ax.set_xlabel(xl)
        ax.set_ylabel("時間（分）")
    cls_seen = ["onsen_tamago", "soft_boiled_egg", "hard_boiled_egg", "poached_egg", "omelet", "custard_pudding", maps.NONE, maps.RAW]
    h1 = [plt.Rectangle((0, 0), 1, 1, fc=COLORS[k], hatch="///" if k == maps.RAW else None) for k in cls_seen]
    l1 = ["塗り: " + DISH_JA.get(k, k) for k in cls_seen]
    dishes = ["soft_boiled_egg", "hard_boiled_egg", "poached_egg", "scrambled_eggs", "custard_pudding"]
    h2 = [Line2D([], [], marker=MARKER[SHAPE[k]], color=COLORS[k], ls="none", markersize=9, markerfacecolor=COLORS[k], markeredgecolor="#1A1F1C") for k in dishes]
    l2 = ["点: " + DISH_JA[k] for k in dishes]
    h3 = [Line2D([], [], marker="o", color="#555", ls="none", markersize=9, markerfacecolor="#555"),
          Line2D([], [], marker="o", color="#555", ls="none", markersize=9, markerfacecolor="white")]
    l3 = ["塗りつぶし: 温度が原文の数値", "中抜き: 温度が推定（○一致 ×不一致）"]
    fig.legend(h1 + h2 + h3, l1 + l2 + l3, loc="lower center", ncol=7, fontsize=9, frameon=False)
    fig.suptitle("世の中のレシピ（Exp-15、28 行）を Exp-14 の地図に重ねる。塗り＝計算の答え（濃いほど迷いが少ない）、点＝レシピ", fontsize=12)
    fig.tight_layout(rect=(0, 0.07, 1, 0.96))
    OUT_PNG.parent.mkdir(exist_ok=True)
    fig.savefig(OUT_PNG)
    plt.close(fig)


def main() -> None:
    d = build()
    OUT_JSON.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    OUT_MD.write_text(write_md(d), encoding="utf-8")
    if "--no-png" not in sys.argv:
        draw_png(d)
    n, m = len(d["points"]), sum(p["match"] for p in d["points"])
    print(f"wrote {OUT_JSON.name} {OUT_MD.name} {OUT_PNG.relative_to(HERE)}  一致 {m}/{n}")


if __name__ == "__main__":
    main()
