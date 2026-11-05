"""通説4: 玉ねぎは炒めると甘くなる（2026-10-22、CLA-135）。

    uv run python experiments/myths/build.py onion_sweet

- 計算: Exp-14 のシミュレータの炒め玉ねぎ（玉ねぎ 200 g・油 10 g をフライパンで炒める。form thin）を、火加減と時間を変えて走らせる。
  重さ（水が飛んだ割合）・重さあたりの糖・刺激臭の段階・焼き色を記録する
- 糖の総量は変えない（R-O02「新たな遊離糖の生成はない」）。実際には長く炒めると総量は減る（R-O01）ので、重さあたりの糖は計算より低い
- 甘く感じるかは感じ方の層の話で、計算では出さない（R-O01: 糖の量と官能評価の甘さは対応しなかった）
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from myths import common as C  # noqa: E402
from myths.common import P, e  # noqa: E402
from sim import ops  # noqa: E402
from sim.state import State  # noqa: E402

ID = "onion_sweet"
OUT = C.WRITEUP / "myth-onion-sweet.html"

RULE_IDS = ["R-O01", "R-O02", "R-O03"]
SOURCE_IDS = ["tamaki2003", "tokitomo1993", "fooddb"]
SOURCE_CHECK = {
    "tamaki2003": ("抄録確認", "長時間炒めると水分が飛び、色・味・香りが変わり刺激臭が消える。ブドウ糖・果糖・遊離糖の総量は減る。糖の量と甘さの感じ方は対応しなかった"),
    "tokitomo1993": ("抄録確認", "生の玉ねぎの遊離糖（約6%）は加熱で増えず、変わらないか減る。甘い香りの成分ができる。甘く感じるのは濃縮と組織の軟化と考えられる（著者の考察）"),
    "fooddb": ("本文確認", "玉ねぎの成分（水分 90.1・炭水化物 8.4 g/100g）"),
}
ONION, OIL = 200, 10
HEATS = [("弱火", 130, 0), ("中火", 170, 1), ("強火", 210, 2)]   # Exp-15 P-LOW（出典なし）・炒め玉ねぎの正解のレシピの 170℃・強火は推定
TIMES = [0, 2, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]


def point(T: float, t: float) -> dict:
    s = State.from_ingredients({"onion": ONION, "vegetable_oil": OIL})
    s0_sugar = s.sugar_g()
    if t > 0:
        s = ops.apply(s, [("bake", {"T": T, "time": t, "form": "thin"})])
    onion_mass = s.mass - s.masses.get("vegetable_oil", 0)
    return {"t": t, "mass_ratio": s.mass_ratio, "sugar_total": s.sugar_g() / s0_sugar,
            "sugar_per100_onion": 100 * s.sugar_g() / onion_mass if onion_mass > 0 else 0,
            "sulfur": s.onion_sulfur, "maillard": s.maillard, "caramel": s.caramel, "water": s.water}


def compute() -> dict:
    lines = {T: [point(T, t) for t in TIMES] for _, T, _ in HEATS}
    first = {}
    for _, T, _ in HEATS:
        L = lines[T]
        first[T] = {
            "half": next((p["t"] for p in L if p["mass_ratio"] <= 0.5), None),
            "s0": next((p["t"] for p in L if p["sulfur"] == 0), None),
            "m2": next((p["t"] for p in L if (p["maillard"] or 0) >= 2), None),
        }
    return {"lines": lines, "first": first, "raw": point(170, 0)}


DISH_COLORS = [("x", "x", "#888888", "#888888")]


def fmt(v):
    return "—" if v is None else f"{v:g}"


def page() -> str:
    Cm = compute()
    L, F, raw = Cm["lines"], Cm["first"], Cm["raw"]
    mid = L[170]
    end = mid[-1]
    p40 = next(p for p in mid if p["t"] == 40)
    H = C.head("炒め玉ねぎの甘さ", C.css(DISH_COLORS, C.CSS_FIG))
    A = H.append
    A('<div class="wrap">')
    A(C.header(4, '玉ねぎは、炒めると甘くなる？',
               '判定と確かさ・決め手の図・言えないこと・自分で試す手順を先に置き、通説の説明・計算の詳しい答え・根拠を後ろに並べたページです。'
               '通説の説明と結論の文章は本人が書きます（いまは空欄と材料）。'))

    A(C.h2("claim", 1, "通説", '<div class="card">'))
    A('<p class="claim">「玉ねぎは、じっくり炒めると甘くなる（糖が増える・カラメルになる）」</p>')
    A(C.owner_slot("この通説がどう言われているか・なぜ気になったか", [
        '言われる理由: 炒めると糖ができる・増える／糖がカラメルになる',
        '論文（抄録）: 加熱で遊離糖は増えない（tokitomo1993）。長く炒めると総量はむしろ減る（tamaki2003）',
        '計算で扱えるのは、重さ（水が飛ぶ）と重さあたりの糖、刺激臭の段階、焼き色。甘く感じるかどうかは扱えない',
    ]))
    A('</div></section>')

    A(C.h2("calc", 2, "計算の詳しい答え"))
    A(f'<p>玉ねぎ {ONION} g と油 {OIL} g をフライパンで炒める計算を、火加減 3 通り × 時間で走らせました（Exp-14 のシミュレータ、ときどき混ぜる＝混ぜ続けない）。'
      '糖の総量は変えず（R-O02）、水が飛んだ分だけ重さあたりの糖が上がります。</p>')
    head = "".join(f"<th>{n}（{T}℃）</th>" for n, T, _ in HEATS)
    rows = [("重さが半分になる（分）", "half"), ("刺激臭が消える（分）", "s0"), ("きつね色（焼き色 2）になる（分）", "m2")]
    A('<div class="tablewrap"><table><thead><tr><th></th>' + head + '</tr></thead><tbody>'
      + "".join(f'<tr><td>{lab}</td>' + "".join(f'<td class="num">{fmt(F[T][k])}</td>' for _, T, _ in HEATS) + '</tr>' for lab, k in rows)
      + '</tbody></table></div>')
    A(f'<p class="small">「—」は 60 分までに届かないもの。中火 40 分（正解のレシピ）で、重さは生の {p40["mass_ratio"] * 100:.0f}%、'
      f'玉ねぎ 100 g あたりの糖は {raw["sugar_per100_onion"]:.1f} g → {p40["sugar_per100_onion"]:.1f} g。</p>')
    A('<figure class="chart"><figcaption>中火（170℃）で炒めた時間と、重さ・糖（生を 1 とした比）</figcaption>'
      + C.svg_lines([("重さ", 0, [(p["t"], p["mass_ratio"]) for p in mid], False),
                     ("糖の総量", 3, [(p["t"], p["sugar_total"]) for p in mid], True),
                     ("重さあたりの糖", 2, [(p["t"], p["sugar_per100_onion"] / raw["sugar_per100_onion"]) for p in mid], False)],
                    "炒めた時間（分）", "生を 1 とした比", (0, 60), (0, max(3.0, end["sugar_per100_onion"] / raw["sugar_per100_onion"] + 0.2)))
      + '</figure>')
    A(C.legend_lines([("重さ", 0, False), ("糖の総量（計算では変えない）", 3, True), ("重さあたりの糖", 2, False)]))
    A('<ul class="find">')
    A('<li><b>糖は増えない。重さあたりの糖が上がるのは、水が飛んで濃くなるから。</b>計算は糖の総量を変えていない（R-O02）。実際には長く炒めると総量は減る（R-O01）ので、重さあたりの糖は計算より低い。</li>')
    A(f'<li><b>刺激臭（辛み）は、重さが生の 40% になるまでに消える</b>（R-O01 の採用値。中火で {fmt(F[170]["s0"])} 分）。甘く感じる理由の一つは、辛みが消えて甘さが目立つことと考えられる（tokitomo1993 の考察、確かめていない）。</li>')
    A('<li class="muted small">注意: 水の飛び方は、沸点に達した後は火加減によらず毎分 4%（推定）としているので、弱火・中火・強火で重さの減り方が同じになります（表）。'
      '焼き色は中火 5 分で きつね色になり、実際より早すぎます（Exp-14 で分かっている問題。表面の温度の近似が粗い）。'
      '刺激臭が消える重さ（40%）も含めて、何分で何% になるかは鍋・量・混ぜ方で大きく変わります。</li>')
    A('</ul></section>')

    A(C.keyfig("中火で炒めると、重さは減り、糖の総量は変わらない（計算）",
               C.svg_lines([("重さ", 0, [(p["t"], p["mass_ratio"]) for p in mid], False),
                            ("糖の総量", 3, [(p["t"], p["sugar_total"]) for p in mid], True)],
                           "炒めた時間（分）", "生を 1 とした比", (0, 60), (0, 1.2)),
               '実線が重さ、破線が糖の総量。重さあたりの糖が上がるのは、糖が増えるからではなく、水が飛んで濃くなるから。実際には長く炒めると糖の総量はむしろ減る（tamaki2003）。'))

    A(C.h2("basis", 3, "根拠"))
    A(C.basis_links(RULE_IDS, SOURCE_IDS))
    use = {
        "R-O01": f"重さが生の {P.V('onion_sulfur_zero_mass_ratio') * 100:g}% まで減ると刺激臭が消える（採用値）。糖の総量が減ることは計算に入れていない",
        "R-O02": "糖の総量は加熱で変えない（新たな糖はできない）。重さあたりの糖は水が飛んだ分だけ上がる",
        "R-O03": "焼き色（メイラード）の段階。カラメル化との割合は分からない（出典が飲食店のブログのみ、確かさ 低）",
    }
    H.extend(C.rules_table(RULE_IDS, use))
    H.extend(C.sources_table(SOURCE_IDS, SOURCE_CHECK, col4="この計算で使ったこと"))
    A('</section>')

    A(C.h2("verdict", 4, "判定と確かさ"))
    CAN = (['<b>炒めても糖は増えない</b>。生の玉ねぎの遊離糖（約6%）は加熱で変わらないか減る（tokitomo1993）、長く炒めると総量は減る（tamaki2003）。どちらも抄録で確かめた。' + C.conf("高"),
            f'<b>重さあたりの糖は上がる</b>。水が飛ぶから（中火 40 分で重さ {p40["mass_ratio"] * 100:.0f}%、計算）。「甘くなる」が「同じ重さを食べると糖が多い」の意味なら正しい。{C.conf("中")}',
            f'<b>刺激臭は消える</b>（R-O01）。辛みが消えることも甘く感じる理由と考えられている（著者の考察）。{C.conf("中")}'],
           ['<b>甘く感じる</b>かどうか。tamaki2003 は糖の量と甘さの感じ方が対応しなかったと書いている。感じ方は計算に無い。',
            '「カラメルになるから甘い」か。焼き色がメイラード反応かカラメル化かの割合は分からない（R-O03、確かさ 低、C7）。カラメル化は甘さより苦み・香ばしさを足す。',
            '何分で重さが何% になるか。水の飛び方は推定（毎分 4%）で、火加減の違いも入っていない。鍋の広さ・量・混ぜ方で大きく変わる。',
            '糖の総量が減る速さ。計算には入っていない（減ることだけが分かっている）。'])
    A(C.can_card(CAN[0]))
    A(C.owner_slot("結論（まとめの文章）", [
        f'玉ねぎ 100 g あたりの糖（計算）: 生 {raw["sugar_per100_onion"]:.1f} g → 中火 40 分 {p40["sugar_per100_onion"]:.1f} g（総量は同じとした）',
        '確かさ: 「糖は増えない」は 高（論文2本の抄録）、「重さあたりは上がる」は 中、「甘く感じる」は計算外',
        '言い方の候補: 甘くなったように感じるのは、糖が増えたからではなく、水が飛んで濃くなり、辛みが消えたから',
    ], note="下の実験の結果を見てから書くのでもよい"))
    A('</section>')
    A(C.h2("cannot", 5, "言えないこと") + C.cannot_card(CAN[1]) + '</section>')

    A(C.h2("try", 6, "自分で試す"))
    A('<p>はかりがあれば、温度計は要りません。炒める前と後の重さから、水が飛んだ割合を出します。甘さは、同じ重さどうしと、同じ玉ねぎの量どうしで食べ比べます。</p>')
    A(C.steps([
        '玉ねぎ1個を薄切りにし、半分を生のまま取っておく。残りの重さを量る。',
        'フライパンに油小さじ2、中火で、ときどき混ぜながら 20 分・40 分炒める。それぞれの時点で全体の重さを量る（油の重さを引く）。',
        '重さの比 = 炒めた後 ÷ 炒める前。計算の予言と比べる。',
        '食べ比べ1: 生・20 分・40 分を、それぞれ同じ重さ（例 5 g）ずつ食べて甘さを比べる。',
        '食べ比べ2: 生 10 g と、生 10 g ぶんを炒めたもの（重さの比をかけた量）を比べる。糖の量は同じはず。',
        '辛み（つんとする香り）が無くなったかも書く。',
    ]))
    pred = {t: next(p for p in mid if p["t"] == t) for t in (20, 40)}
    H.extend(C.record_table(["時間（分）", "炒める前（g）", "炒めた後（g）", "重さの比", "甘さ（同じ重さ）", "甘さ（同じ玉ねぎの量）", "辛み", "計算の予言"],
                            [f'<tr><td class="num">{t}</td><td></td><td></td><td></td><td></td><td></td><td></td>'
                             f'<td class="pred">重さの比 {pred[t]["mass_ratio"]:.2f}・刺激臭 {pred[t]["sulfur"]}（0 で消える）</td></tr>' for t in (20, 40)]))
    A('<p class="small muted">予言は Exp-14 の規則をそのまま計算したもの。重さの比は水の飛び方（推定）しだいで、鍋・量によって大きくずれます。'
      '食べ比べ2 で炒めたほうが甘く感じれば、糖の量以外（辛みが消える・香り・やわらかさ）が効いていることになります。</p>')
    A('</section>')

    A(C.footer('Cuisine Network。計算: Exp-14 のシミュレータ（experiments/exp-14/sim、rules.yaml の規則と採用値）。'
               'このページは experiments/myths/build.py（通説4 onion_sweet）が生成します。'))
    A('</div>')
    return C.reorder(C.join(H))
