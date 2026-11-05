"""通説2「卵は常温に戻してからゆでる」（writeup/myth-room-temp-egg.html）。

    uv run python experiments/myths/build.py room_temp_egg

- 計算は Exp-14 のシミュレータのまま（rules.yaml・判定・地図の範囲を変えない）。殻付き卵は 2026-09-30 から既定の
  Exp-17 の計算（2層の球の熱伝導＋変性の反応速度、sim/egg_kinetic.py）。ページの説明もそれに合わせた。地図は sim/maps.py の PRESETS「shell_egg_ice」
  （殻付き卵 × 湯の温度 × 時間、ゆでた後に氷水に 15分取る。2026-09-28 夜の余熱から。ページの実験の手順「すぐ氷水に取る」に合わせた）を、卵の最初の温度（T0）だけ 5℃（冷蔵庫）と 20℃（常温、T0_default）にして2枚描く。
- 「同じ仕上がりまでの時間」は、湯温を固定して 0.1分刻みで時間を延ばし、卵白・卵黄の段階と判定が最初に変わる時間を比べる。
- 殻が割れるかは計算で扱えない（殻の強さ・気室の膨張を状態に持たない）。出典で分かる範囲だけ載せる。
- 通説の説明と結論の文章は本人が書く（2026-09-28 本人方針）。ページには空欄と材料だけを置く。
- レシピでの扱いは Exp-15 の recipes.csv（殻付き卵の行）から数える。
"""
from __future__ import annotations

from collections import Counter

from . import common as C
from .common import NO_MATCH_BELOW, P, maps
from sim import egg_kinetic as EK  # noqa: E402

ID = "room_temp_egg"
OUT = C.WRITEUP / "myth-room-temp-egg.html"
PRESET = next(p for p in maps.PRESETS if p["id"] == "shell_egg_ice")
T_FRIDGE, T_ROOM = 5, 20
e = C.e

DISH_COLORS = [("onsen_tamago", "f-on", "#2a78d6", "#3987e5"), ("soft_boiled_egg", "f-so", "#6b4fb3", "#a08be8"),
               ("hard_boiled_egg", "f-ha", "#eb6834", "#d95926"), ("__none", "f-no", "#b3b8b4", "#4d5651"),
               ("__raw", "f-raw", "#DCE0DC", "#252D29")]
FILL = {k: c for k, c, _, _ in DISH_COLORS}
JA = {"onsen_tamago": "温泉卵", "soft_boiled_egg": "半熟ゆで卵", "hard_boiled_egg": "ゆで卵（固ゆで）",
      maps.NONE: "該当なし", maps.RAW: "生のまま（変化なし）"}
LINE_TEMPS = [100, 90, 80, 68]   # 時間の比較をする湯温（沸騰・沸騰させない湯・卵白が固まる温度・温泉卵の元のレシピ）
LINE_MAX = 40.0                   # 分
EXP_T = 100
EXP_TIMES = [6.5, 11]             # 実験で比べる時間（Exp-15 の 料理本/ゆで卵 の 6〜7分・10〜12分の中央）


# ---------------- 計算 ----------------

def base(T0: float) -> dict:
    b = maps.base_recipe(PRESET["base"])
    b["T0"] = T0
    return b


def at(T0: float, T: float, t: float) -> dict:
    return maps.with_value(maps.with_value(base(T0), PRESET["x"]["axis"], T), PRESET["y"]["axis"], t)


def point(T0: float, T: float, t: float) -> dict:
    r = at(T0, T, t)
    _, s = maps.run_json(r)
    c = maps.cell(r, NO_MATCH_BELOW)
    # 温度の線は湯から出す時点の値（後の手順＝氷水の前）。段階・判定は氷水の後（余熱を含む）
    _, h = maps.run_json({**r, "steps": r["steps"][:1]})
    return {"cls": c["cls"], "top": c["top"], "white": s.egg_white_stage, "yolk": s.egg_yolk_stage,
            "core": h.T_core, "white_T": h.T_white}


def timeline(T0: float, T: float) -> list[dict]:
    out = []
    n = int(round(LINE_MAX * 10))
    for i in range(1, n + 1):
        t = i / 10
        out.append({"t": t, **point(T0, T, t)})
    return out


def first(line: list[dict], pred) -> float | None:
    return next((p["t"] for p in line if pred(p)), None)


MILESTONES = [
    ("white3", "白身がしっかり固まる（卵白 3）", lambda p: p["white"] >= 3),
    ("yolk1", "黄身にとろみ（卵黄 1）", lambda p: p["yolk"] >= 1),
    ("yolk2", "黄身が固まる（卵黄 2）", lambda p: p["yolk"] >= 2),
    ("yolk3", "黄身がほろほろ（卵黄 3）", lambda p: p["yolk"] >= 3),
    ("onsen", "判定が温泉卵になる", lambda p: p["cls"] == "onsen_tamago"),
    ("soft", "判定が半熟ゆで卵になる", lambda p: p["cls"] == "soft_boiled_egg"),
    ("soft_end", "半熟ゆで卵でなくなる（黄身が固まり始める）", None),
    ("hard", "判定が固ゆで卵になる", lambda p: p["cls"] == "hard_boiled_egg"),
]


def milestones(line: list[dict]) -> dict:
    out = {}
    for key, _, pred in MILESTONES:
        if pred is not None:
            out[key] = first(line, pred)
    s = out.get("soft")
    out["soft_end"] = first([p for p in line if s is not None and p["t"] > s], lambda p: p["cls"] != "soft_boiled_egg") if s else None
    return out


def compute() -> dict:
    assert EK.model() == "kinetic", "ページの説明は殻付き卵の計算 kinetic（Exp-17）を前提に書いている"
    grids = {T0: maps.grid(base(T0), PRESET["x"], PRESET["y"], NO_MATCH_BELOW) for T0 in (T_FRIDGE, T_ROOM)}
    count = {T0: Counter(c["cls"] for r in g["cells"] for c in r) for T0, g in grids.items()}
    changed = Counter()
    ex = []
    g5, g20 = grids[T_FRIDGE], grids[T_ROOM]
    for j, (r5, r20) in enumerate(zip(g5["cells"], g20["cells"])):
        for i, (a, b) in enumerate(zip(r5, r20)):
            if a["cls"] != b["cls"]:
                changed[(b["cls"], a["cls"])] += 1
                ex.append((g5["xs"][i], g5["ys"][j], b["cls"], a["cls"]))
    lines = {(T0, T): timeline(T0, T) for T in LINE_TEMPS for T0 in (T_FRIDGE, T_ROOM)}
    ms = {k: milestones(v) for k, v in lines.items()}
    exp = {(T0, t): point(T0, EXP_T, t) for T0 in (T_FRIDGE, T_ROOM) for t in EXP_TIMES}
    return {"grids": grids, "count": count, "changed": changed, "ex": ex, "lines": lines, "ms": ms, "exp": exp,
            "n": len(g5["xs"]) * len(g5["ys"])}


# ---------------- レシピ（Exp-15） ----------------

def recipes() -> dict:
    rows = [r for r in C.recipe_rows() if r["egg_form"] == "shell"]
    t0 = [r for r in rows if r["egg_T0_rule"] != "E-NONE"]
    pages = {r["page_title"] for r in rows}
    t0_pages = {r["page_title"] for r in t0}
    start = Counter(r["start"] for r in rows)
    return {"rows": rows, "t0": t0, "n_pages": len(pages), "t0_pages": sorted(t0_pages), "start": start}


# ---------------- 図 ----------------

def svg_map(g: dict, other: dict, title: str) -> str:
    xs, ys = g["xs"], g["ys"]
    nx, ny = len(xs), len(ys)
    L, T, cw, ch = 40, 8, 17, 9
    W = L + nx * cw + 6
    H = T + ny * ch + 34
    cx = lambda i: L + i * cw  # noqa: E731
    cy = lambda j: T + (ny - 1 - j) * ch  # noqa: E731
    parts = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{e(title)}の地図">',
             '<defs><pattern id="hatch" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
             '<rect width="5" height="5" class="f-raw"/><line x1="0" y1="0" x2="0" y2="5" class="hatch-l"/></pattern></defs>']
    for j, row in enumerate(g["cells"]):
        for i, c in enumerate(row):
            o = other["cells"][j][i]
            a = 1.0 if c["cls"].startswith("__") else 0.3 + 0.7 * min(1, c["margin"] / 0.4)
            fill = ' fill="url(#hatch)"' if c["cls"] == maps.RAW else ""
            top = f"{c['top'][1]}/{c['top'][2]}" if c["top"] else "—"
            tip = f"{xs[i]:g}℃・{ys[j]:g}分: {JA[c['cls']]}（{top}）"
            if c["cls"] != o["cls"]:
                tip += f"／もう一方: {JA[o['cls']]}"
            parts.append(f'<rect x="{cx(i)}" y="{cy(j)}" width="{cw + .3}" height="{ch + .3}" class="{FILL[c["cls"]] if c["cls"] != maps.RAW else ""}"{fill} fill-opacity="{a:.3f}"><title>{e(tip)}</title></rect>')
            if c["cls"] != o["cls"]:
                parts.append(f'<rect x="{cx(i) + 1}" y="{cy(j) + 1}" width="{cw - 2}" height="{ch - 2}" class="dif"/>')
    parts.append(f'<rect x="{L}" y="{T}" width="{nx * cw}" height="{ny * ch}" class="frame"/>')
    for i, x in enumerate(xs):
        if x % 10 == 0:
            parts.append(f'<text class="ax" x="{cx(i) + cw / 2}" y="{T + ny * ch + 12}" text-anchor="middle">{x:g}</text>')
    for j, y in enumerate(ys):
        if (y - 1) % 10 == 0:
            parts.append(f'<text class="ax" x="{L - 4}" y="{cy(j) + ch / 2 + 3.5}" text-anchor="end">{y:g}</text>')
    parts.append(f'<text class="axl" transform="translate(10 {T + ny * ch / 2}) rotate(-90)" text-anchor="middle">湯に入れてからの時間（分）</text>')
    parts.append(f'<text class="axl" x="{L + nx * cw / 2}" y="{H - 4}" text-anchor="middle">湯の温度（℃）</text>')
    parts.append("</svg>")
    return "".join(parts)


def svg_core(lines: dict, T: float, tmax: float = 16) -> str:
    """湯温 T での中心と卵白の層の温度（最初の温度 5℃・20℃）。
    段階は温度のしきい値ではなく変性度の分布から出る（Exp-17）ので、しきい値の横線は引かない。"""
    W, H, L, R, Tp, B = 640, 260, 44, 12, 10, 34
    pw, ph = W - L - R, H - Tp - B
    X = lambda t: L + t / tmax * pw  # noqa: E731
    Y = lambda v: Tp + (1 - v / 100) * ph  # noqa: E731
    parts = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="湯温 {T:g}℃ での卵の温度の上がり方">']
    for v in range(0, 101, 20):
        parts.append(f'<line x1="{L}" x2="{W - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" class="grid"/><text class="ax" x="{L - 4}" y="{Y(v) + 3.5:.1f}" text-anchor="end">{v}</text>')
    for t in range(0, int(tmax) + 1, 2):
        parts.append(f'<text class="ax" x="{X(t):.1f}" y="{H - B + 14}" text-anchor="middle">{t}</text>')
    for T0, cls in ((T_FRIDGE, "l5"), (T_ROOM, "l20")):
        pts = [(0.0, T0)] + [(p["t"], p["core"]) for p in lines[(T0, T)] if p["t"] <= tmax]
        wpts = [(0.0, T0)] + [(p["t"], p["white_T"]) for p in lines[(T0, T)] if p["t"] <= tmax]
        parts.append(f'<polyline class="{cls}" points="{" ".join(f"{X(t):.1f},{Y(v):.1f}" for t, v in pts)}"/>')
        parts.append(f'<polyline class="{cls} dash" points="{" ".join(f"{X(t):.1f},{Y(v):.1f}" for t, v in wpts)}"/>')
    parts.append(f'<text class="axl" x="{L + pw / 2}" y="{H - 4}" text-anchor="middle">湯に入れてからの時間（分）</text>')
    parts.append(f'<text class="axl" transform="translate(11 {Tp + ph / 2}) rotate(-90)" text-anchor="middle">温度（℃）</text>')
    parts.append("</svg>")
    return "".join(parts)


EXTRA_CSS = """.grid{stroke:var(--rule);stroke-width:.6}
.th{stroke:var(--saffron);stroke-width:1;stroke-dasharray:3 3}
.l5,.l20{fill:none;stroke-width:2.2}
.l5{stroke:var(--d-onsen_tamago)}.l20{stroke:var(--d-hard_boiled_egg)}
.dash{stroke-dasharray:5 3;stroke-width:1.4}
.ln{display:inline-block;width:22px;height:0;border-top:2.5px solid;vertical-align:middle}
.ln.dash{border-top-style:dashed;border-top-width:1.6px}
td.d{font-weight:700}
.chart{max-width:720px;margin-top:10px}
""" + C.CSS_OWNER


def fmt_t(v: float | None) -> str:
    return "—" if v is None else f"{v:g}"


def delta(a: float | None, b: float | None) -> str:
    if a is None or b is None:
        return "—"
    d = round(a - b, 1)
    return f"{d:+g}"


# ---------------- ページ ----------------

RULE_IDS = ["R-E06", "R-E08"]
SOURCE_IDS = ["dilorenzo2025", "soc_sousvide", "tatsu2019", "wiki_boiled", "egg_structure", "egg_thermal"]
SOURCE_CHECK = {
    "dilorenzo2025": ("本文確認", "卵黄・卵白の熱伝導率・密度・比熱（温度の関数）と、変性の速さの式の値（Table 4）。卵の温まり方と固まり方をこの値で計算した"),
    "soc_sousvide": ("本文確認", "黄身がほろほろになるのは 80〜90℃（McGee p.85 を引用）。黄身の段階3に中心 80℃ 以上を要るとした根拠"),
    "tatsu2019": ("抄録確認", "殻付き卵の中心が湯温近くに達するまで 65℃:30分・68℃:28分・70℃:27分。合わせ込みはせず、計算の照合に使った（68℃で 28.4 分）"),
    "wiki_boiled": ("本文確認", "半熟は黄身が一部液体。熱は白身を通って黄身に届くので時間がかかる"),
    "egg_structure": ("本文確認", "卵白 56〜59%・卵黄 30〜33%・殻 0.2〜0.38mm（黄身＝中心の球 34%、白身＝外側の層とした割合）"),
    "egg_thermal": ("抜粋のみ", "卵白・卵黄の熱拡散率（1.3〜1.7×10⁻⁷ m²/s）。Di Lorenzo et al. の表の値（約 1.3×10⁻⁷）と同じ桁であることの確かめに使った"),
}
# 殻が割れる話の出典（rules.yaml には入れていない。計算に使わないため）
CRACK_SOURCES = [
    ("Yahoo!ニュース エキスパート「ぱぷちゃん」（調理師）『「ゆで卵、常温に戻してから茹でる？」実は注意したい“温度差”』",
     "https://news.yahoo.co.jp/expert/articles/f48330bf8443b754988e89424515b33c18132db2", "本文確認（2026-09-28）",
     "冷たい卵をいきなり熱い湯に入れると、急な温度差で殻にヒビが入る。湯からゆでるなら15分ほど前に冷蔵庫から出す。水からゆでるなら冷たいままでよい。割れた数などの数値は無い"),
    ("macaroni「卵は常温に戻すべき？」", "https://macaro-ni.jp/174808", "検索抜粋のみ", "温度差でヒビが入る。夏は30分、冬は1時間ほど室温に置く（検索結果の要約で見ただけ）"),
    ("The Kitchn “How to Keep Eggs from Cracking When Hard-Boiling”", "https://www.thekitchn.com/never-boil-cold-eggs-22957631", "検索抜粋のみ", "冷たい卵を沸騰した湯に入れると割れやすい（題名と要約で見ただけ）"),
    ("J. Kenji López-Alt “The Food Lab: Perfect Boiled Eggs”（Serious Eats、2009）", "https://www.seriouseats.com/the-food-lab-perfect-boiled-eggs", "写し（web.baz.org）の本文確認。元のページは取得できなかった",
     "実験の卵は冷蔵庫から出したまま（約 37°F ≈ 3℃）。最初の温度の違いと割れは本文では比べていない（割れの話はコメント欄のみ）"),
]


def page() -> str:
    Cm = compute()
    Rc = recipes()
    ms, cnt = Cm["ms"], Cm["count"]
    g5, g20 = Cm["grids"][T_FRIDGE], Cm["grids"][T_ROOM]
    n_changed = sum(Cm["changed"].values())
    m100_5, m100_20 = ms[(T_FRIDGE, 100)], ms[(T_ROOM, 100)]

    H = C.head("常温に戻す卵", C.css(DISH_COLORS, EXTRA_CSS))
    A = H.append
    A('<div class="wrap">')
    A(C.header(2, '卵は、常温に戻してからゆでる？',
               '判定と確かさ・決め手の図・言えないこと・自分で試す手順を先に置き、通説の説明・計算の詳しい答え・根拠を後ろに並べたページです。'
               '根拠の詳しい中身は、規則ごと・出典ごとのページに分けました。通説の説明と結論の文章は本人が書きます（いまは空欄と材料）。'))

    # 1. 通説
    A(C.h2("claim", 1, "通説", '<div class="card">'))
    A('<p class="claim">「ゆで卵は、卵を冷蔵庫から出して常温に戻してからゆでる」</p>')
    st = Rc["start"]
    A(C.owner_slot("この通説がどう言われているか・なぜ気になったか", [
        '言われる理由は2つ: <b>(1) 冷たい卵を熱い湯に入れると温度差で殻が割れる</b>、<b>(2) 火の通りがそろう・時間どおりに仕上がる</b>。'
        '(1) は家庭向け記事で多い（Yahoo!ニュース エキスパート・macaroni・The Kitchn。「殻が割れる話」の節）。(2) は時間の話で、この計算で扱える',
        f'世の中のレシピ（Exp-15: Wikibooks 料理本などから読み取った殻付き卵の手順 {len(Rc["rows"])} 件・{Rc["n_pages"]} ページ）で、'
        f'<b>卵の最初の温度を書いているのは {len(Rc["t0"])} 件</b>（どちらも「冷蔵庫から取り出し、常温に戻します」、同じページ {"・".join(e(p) for p in Rc["t0_pages"])}）。'
        f'残り {len(Rc["rows"]) - len(Rc["t0"])} 件は書いていない（冷蔵とも常温とも決めていない）',
        f'同じ {len(Rc["rows"])} 件で、湯が沸いてから入れる（hot）{st.get("hot", 0)} 件・水から（cold）{st.get("cold", 0)} 件・書いていない {st.get("-", 0)} 件。'
        '「水からゆでるなら冷たいままでよい」とする記事がある（Yahoo!ニュース エキスパート）ので、通説は主に「湯が沸いてから入れる」ときの話',
        '家庭の冷蔵庫の卵の温度は 5℃ 前後、常温は季節で 15〜25℃（Exp-15 の抽出規則で常温を 20℃ とした。推定）',
    ]))
    A('</div></section>')

    # 2. 計算の答え
    A(C.h2("calc", 2, "計算の詳しい答え"))
    A(f'<p>殻付き卵（60 g）を湯に入れ、湯の温度（横）と時間（縦）を変えて、マスごとに料理を判定しました。左は卵の最初の温度 {T_FRIDGE}℃（冷蔵庫から出してすぐ）、右は {T_ROOM}℃（常温）。'
      '色の濃さは迷いの少なさ、灰色は該当なし、斜線は生のまま。左右で判定が違うマスを黄色の枠で囲みました。マスにカーソルを当てると値が出ます。</p>')
    A('<div class="maps">')
    A(f'<figure><figcaption>冷蔵庫から出してすぐ（{T_FRIDGE}℃）</figcaption>{svg_map(g5, g20, "卵 5℃")}</figure>')
    A(f'<figure><figcaption>常温に戻した（{T_ROOM}℃）</figcaption>{svg_map(g20, g5, "卵 20℃")}</figure>')
    A('</div>')
    A('<div class="legend">' + "".join(
        f'<span class="it"><span class="sw" style="background:var(--d-{k})"></span>{JA[k]}</span>' for k, *_ in DISH_COLORS)
      + '<span class="it"><span class="sw ring"></span>最初の温度で判定が違う</span></div>')
    ch_txt = "、".join(f"{JA[a]}→{JA[b]} {n}" for (a, b), n in Cm["changed"].most_common())
    A('<div class="tablewrap"><table><thead><tr><th>判定</th>' + f'<th>{T_FRIDGE}℃（マス）</th><th>{T_ROOM}℃（マス）</th></tr></thead><tbody>'
      + "".join(f'<tr><td>{JA[k]}</td><td class="num">{cnt[T_FRIDGE].get(k, 0)}</td><td class="num">{cnt[T_ROOM].get(k, 0)}</td></tr>' for k, *_ in DISH_COLORS)
      + '</tbody></table></div>')
    A(f'<p class="small">全 {Cm["n"]} マスのうち、判定が違うのは <b>{n_changed} マス</b>（常温→冷蔵: {ch_txt}）。違うのは料理の境目の、短い時間の側だけです。</p>')

    A('<h3>同じ仕上がりまでの時間</h3>')
    A(f'<p>湯温を決めて時間を 0.1 分刻みで延ばし、白身・黄身の段階と判定が最初に変わる時間を比べました（{int(LINE_MAX)} 分まで。湯から出した後はすぐ氷水に取る、余熱を含む）。「—」はその時間内に届かないもの。差は「冷蔵 − 常温」（分）。</p>')
    head = "".join(f'<th>{T:g}℃ 冷蔵</th><th>常温</th><th>差</th>' for T in LINE_TEMPS)
    body = []
    for key, lab, _ in MILESTONES:
        tds = "".join(f'<td class="num">{fmt_t(ms[(T_FRIDGE, T)][key])}</td><td class="num">{fmt_t(ms[(T_ROOM, T)][key])}</td>'
                      f'<td class="num d">{delta(ms[(T_FRIDGE, T)][key], ms[(T_ROOM, T)][key])}</td>' for T in LINE_TEMPS)
        body.append(f'<tr><td>{lab}</td>{tds}</tr>')
    A(f'<div class="tablewrap"><table style="min-width:860px"><thead><tr><th>湯に入れてから（分）</th>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>')
    d_soft = delta(m100_5["soft_end"], m100_20["soft_end"])
    d_hard = delta(m100_5["hard"], m100_20["hard"])
    A('<ul class="find">')
    A(f'<li><b>沸騰した湯では、冷蔵の卵は常温の卵より、半熟の終わり（黄身が固まり始める）が {d_soft} 分、固ゆでになるのが {d_hard} 分遅い。</b>'
      f'常温 {fmt_t(m100_20["soft_end"])}・{fmt_t(m100_20["hard"])} 分、冷蔵 {fmt_t(m100_5["soft_end"])}・{fmt_t(m100_5["hard"])} 分。</li>')
    A(f'<li><b>白身が固まる時間はほとんど変わらない</b>（沸騰で 常温 {fmt_t(m100_20["white3"])}・冷蔵 {fmt_t(m100_5["white3"])} 分）。外側は湯に近いので、最初の温度の差がすぐ消える。差が出るのは中心の黄身。</li>')
    A(f'<li>湯温が低いほど差は大きい（表）。{LINE_TEMPS[-1]}℃（温泉卵の元のレシピ）で温泉卵になるのは 常温 {fmt_t(ms[(T_ROOM, LINE_TEMPS[-1])]["onsen"])}・冷蔵 {fmt_t(ms[(T_FRIDGE, LINE_TEMPS[-1])]["onsen"])} 分。</li>')
    A('<li class="muted small">注意: 卵の温まり方は、殻付き卵を黄身（中心の球）と白身（外側の層）の2層の球とみなした熱伝導の計算です（Exp-17）。'
      '卵の形（球でない）・殻は入れていません。白身・黄身の段階は、場所ごとの変性度（固まり具合）から出していて、その決め方は仮の値です。'
      '差の向き（冷蔵のほうが遅い）はこの近似によらず、差の大きさ（何分）は近似の確かさを超えません。</li>')
    A('</ul></section>')

    # 決め手の図（2026-10-22。前は計算の答えの節の中にあった温度のグラフ）
    A(C.keyfig("沸騰した湯（100℃）での卵の温度", svg_core(Cm["lines"], 100),
               '<span class="legend">'
               f'<span class="it"><span class="ln" style="color:var(--d-onsen_tamago)"></span>中心（最初 {T_FRIDGE}℃）</span> '
               f'<span class="it"><span class="ln" style="color:var(--d-hard_boiled_egg)"></span>中心（最初 {T_ROOM}℃）</span> '
               '<span class="it"><span class="ln dash" style="color:var(--muted)"></span>卵白の層（体積の平均）</span></span><br>'
               f'冷蔵の卵は、中心の温度の線が常温の卵より右（遅い側）にずれる。白身の層の線はすぐ重なる。この差が、黄身の固まり方が {d_soft}〜{d_hard} 分遅れる理由です。'))

    # 3. 根拠
    A(C.h2("basis", 3, "根拠"))
    A(C.basis_links(RULE_IDS, SOURCE_IDS))
    use = {
        "R-E06": f"卵黄 3 には、変性度の条件に加えて中心の最高温度 {P.V('egg_yolk_s3'):g}℃ 以上が要る（変性度の式からは出ない性質のため）",
        "R-E08": "卵の温まり方の照合（20℃の卵が 68℃の湯で 28分で 1℃以内）。計算は合わせ込まずに 28.4 分。卵の最初の温度が違っても同じ式を使う",
    }
    H.extend(C.rules_table(RULE_IDS, use))
    ek = P.H("egg_kinetic")
    sm = {k: v["value"] for k, v in ek["stage_map"].items()}
    A('<h3>卵の温まり方と固まり方（採用値）</h3>')
    A(f'<p class="small">殻付き卵を、黄身（中心の球、体積の {ek["yolk_volume_fraction"]["value"] * 100:g}%）と白身（外側の層）の2層の球とみなし、半径方向に {ek["nodes"]["value"]} に分けて熱の伝わり方を計算しています（Exp-17）。'
      '熱伝導率・密度・比熱と、変性（たんぱく質が固まる反応）の速さの式の値は Di Lorenzo et al. 2025 の表の値です。表面は湯温とし、空気中では表面から周りへの熱の流れが温度差に比例するとしました。'
      '場所ごとに変性度（0〜1）を積分し、層の体積のうち変性度 ' + f'{sm["gel_X"]:g} 以上の割合が {sm["stage2_g"]:g} 以上で段階2、{sm["stage3_g"]:g} 以上で段階3、層の平均の変性度が {sm["stage1_mean"]:g} 以上で段階1としました（結果を見る前に決めた仮の値）。'
      '中心＝中心の温度、卵白の層＝白身の層の体積の平均の温度（グラフの線）。最初の温度は、湯に入れた瞬間の卵全体の温度として入るだけで、式は同じです。'
      '白身・黄身の段階と判定は、湯から出した後に<b>氷水（0℃）に 15 分取った</b>ところまで計算しています（実験の手順どおり）。'
      '取り出した後も外側の熱が中へ移り、中心の温度はしばらく上がります（余熱）。温度のグラフは湯から出す時点の値です。</p>')
    H.extend(C.sources_table(SOURCE_IDS, SOURCE_CHECK, col4="この計算で使ったこと"))
    # 食い違い C1（卵白が固まり始める温度）は殻付き卵の計算では使わなくなった（Exp-17）ので載せない
    A('</section>')

    # 4. 殻が割れる話
    A(C.h2("crack", 4, "殻が割れる話（計算では扱えない）"))
    A('<p>このシミュレータは殻の強さ・殻の中の空気（気室）の膨らみ・温度差による力を持っていないので、<b>殻が割れるかどうかは計算できません</b>。'
      '出典で分かる範囲だけ並べます。今夜探した範囲では、割れた数を数えた実験は見つかりませんでした。</p>')
    A('<div class="tablewrap"><table><thead><tr><th>出典</th><th>確かめ方</th><th>言っていること</th></tr></thead><tbody>'
      + "".join(f'<tr><td>{e(c)} <a href="{e(u)}" target="_blank" rel="noopener">リンク</a></td><td class="nw">{e(h)}</td><td class="small">{e(w)}</td></tr>' for c, u, h, w in CRACK_SOURCES)
      + '</tbody></table></div>')
    A('<p class="small muted">仕組みとして挙げられるのは「外側だけ急に温まる（熱衝撃）」「気室の空気が膨らむ」の2つ。どちらも家庭向けの説明で、測った値は見ていません（確かさ 低）。</p>')
    A('</section>')

    # 5. 結論
    A(C.h2("verdict", 5, "判定と確かさ"))
    CAN = (
        [f'冷蔵（{T_FRIDGE}℃）の卵は常温（{T_ROOM}℃）より黄身が固まるのが遅い。沸騰の湯で半熟の終わりが {d_soft} 分、固ゆでが {d_hard} 分。向きは熱の伝わり方から確か、分の値は近似による。{C.conf("中")}',
         f'白身が固まる時間はほぼ同じ（沸騰で差 {delta(m100_5["white3"], m100_20["white3"])} 分）。差は黄身に出る。{C.conf("中")}',
         f'地図で判定が変わるのは境目の {n_changed} マス（全 {Cm["n"]}）だけ。料理の範囲はほとんど同じで、境目が少し長い時間の側にずれる。{C.conf("中")}',
         f'レシピで卵の温度を書いているのは {len(Rc["t0"])} 件/{len(Rc["rows"])} 件（1ページ）。多くのレシピは時間だけを書いている。{C.conf("高")}'],
        ['<b>殻が割れるか</b>。計算に殻が無く、割れた数を数えた出典も見つからない（「殻が割れる話」の節）。',
         '「火の通りがそろう（外と中の差が小さくなる）」か。外と中の差は湯に入れてすぐ大きく開き、最初の 15℃ の差より湯との差（80℃ 前後）が支配する。計算は球の中の温度と変性度の分布を持っているが、それを「そろっている」かどうかに変える方法を持っていない。',
         '卵の大きさ（M・L）・殻の厚さ・湯量（卵を入れて湯温が下がる）の効果。どれも計算に入っていない。',
         '常温に置いておく間の衛生（結露・菌）。対象外。'],
    )
    A(C.can_card(CAN[0]))
    A(C.owner_slot("結論（まとめの文章）", [
        f'沸騰の湯での時間の差（冷蔵−常温）: 白身 {delta(m100_5["white3"], m100_20["white3"])} 分、半熟の終わり {d_soft} 分、固ゆで {d_hard} 分',
        '確かさ: 時間の差の向きは 中〜高、何分かは 中（2層の球の熱伝導と変性の速さの近似。段階の決め方は仮の値）。割れは計算外で 低（家庭向けの説明のみ）',
        f'レシピの多く（{len(Rc["rows"]) - len(Rc["t0"])}/{len(Rc["rows"])} 件）は卵の温度を書かずに時間だけ → 冷蔵のまま同じ時間なら黄身が少しやわらかめに仕上がる、という予言になる',
        '「水からゆでるなら冷たいままでよい」という意見がある（割れの理由は湯から入れるときだけ）',
    ], note="下の実験の結果を見てから書くのでもよい"))
    A('</section>')
    A(C.h2("cannot", 5, "言えないこと") + C.cannot_card(CAN[1]) + '</section>')

    # 6. 実験
    A(C.h2("try", 6, "自分で試す"))
    e5 = {t: Cm["exp"][(T_FRIDGE, t)] for t in EXP_TIMES}
    e20 = {t: Cm["exp"][(T_ROOM, t)] for t in EXP_TIMES}
    A('<p>鍋1つ・コンロ1口で、冷蔵の卵と常温の卵を<b>交互に</b>ゆでて比べます。沸騰した湯を使えば湯温は 100℃ 前後にそろうので、<b>温度計は無くてもできます</b>'
      '（あれば、常温に置いた卵の温度の代わりに部屋の温度を測って書く）。結果はこの表に書き込み、切った断面の写真を添えてください。</p>')
    A(C.steps([
        '同じパックの卵を4個。2個は前の晩から冷蔵庫、2個は<b>ゆでる1時間前</b>に冷蔵庫から出して室温に置く（部屋の温度を書く）。',
        '鍋にたっぷりの水（卵が 2cm 以上かぶる量）を沸騰させる。塩・酢は入れない。',
        f'1回目: 冷蔵の卵1個をおたまで静かに入れ、{EXP_TIMES[0]:g} 分ゆでる（火は沸騰が続く強さのまま）。すぐ氷水に取る。入れた直後に殻にひびが入ったかを見て書く。',
        '湯が再び沸騰するまで待つ（湯量が減ったら同じ量まで足す）。',
        f'2回目: 常温の卵1個を同じように {EXP_TIMES[0]:g} 分。',
        f'3回目・4回目: 順番を入れ替えて（常温→冷蔵）{EXP_TIMES[1]:g} 分。先にゆでたほうが湯が安定している、という順番の影響を打ち消すため。',
        '冷めたら殻をむき、縦半分に切って、同じ明るさで断面を撮る。黄身の中心が流れるか・とろっとしているか・固まっているかを書く。',
    ]))
    rows = []
    for k, (t, T0, lab) in enumerate([(EXP_TIMES[0], T_FRIDGE, "冷蔵"), (EXP_TIMES[0], T_ROOM, "常温"),
                                      (EXP_TIMES[1], T_ROOM, "常温"), (EXP_TIMES[1], T_FRIDGE, "冷蔵")], 1):
        p = (e5 if T0 == T_FRIDGE else e20)[t]
        pred = f'{JA[p["cls"]]}（黄身 {p["yolk"]}・白身 {p["white"]}、中心 {p["core"]:.0f}℃）'
        rows.append(f'<tr><td class="num">{k}</td><td>{lab}</td><td class="muted small">冷蔵: 約5（推定）<br>常温: 部屋の温度</td><td class="muted small">目標 {t:g}</td>'
                    f'<td></td><td class="photo"></td><td></td><td></td><td class="pred">{e(pred)}</td></tr>')
    H.extend(C.record_table(["回", "卵", "卵の温度（℃）", "時間（分）", "ひび（なし／あり）", "断面の写真", "黄身（流れる／とろっと／固まる）", "白身（やわらかい／固い）", "計算の予言"], rows))
    A('<p class="small muted">予言は Exp-14 の規則をそのまま計算したもの（黄身・白身の段階は 0 生〜3）。4個では割れやすさの違いは分かりません（割れはまれなので、確かめるには数十個が要る）。'
      'この実験で確かめられるのは、同じ時間での黄身の違い（時間の差）です。</p>')
    A('</section>')

    A(C.footer('Cuisine Network。計算: Exp-14 のシミュレータ（experiments/exp-14/sim、rules.yaml の規則と採用値）、地図 sim/maps.py の「殻付き卵 × 湯の温度 × 時間」を卵の最初の温度だけ変えて描いた。'
               'レシピ: Exp-15（experiments/exp-15-recipes/recipes.csv）。このページは experiments/myths/build.py（通説2 room_temp_egg）が生成します。'))
    A('</div>')
    return C.reorder(C.join(H))
