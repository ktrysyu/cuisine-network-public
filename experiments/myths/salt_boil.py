"""通説5: パスタの湯に塩を入れると沸点が上がる（早くゆだる）（2026-10-22、CLA-135）。

    uv run python experiments/myths/build.py salt_boil

- 計算: 沸点上昇の式 ΔTb = Kb × m × i（R-W04、libretexts_bpe）。食塩の分子量 58.44 g/mol（物理定数）
- シミュレータの沸点にはまだ入れていない（このページの計算だけで使う）
- 「早くゆだる」は、湯の温度が何℃上がるかまで。麺の火の通りはシミュレータに無い（パスタの規則が無い）
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from myths import common as C  # noqa: E402
from myths.common import P, e  # noqa: E402

ID = "salt_boil"
OUT = C.WRITEUP / "myth-salt-boil.html"

RULE_IDS = ["R-W04", "R-W01"]
SOURCE_IDS = ["libretexts_bpe"]
SOURCE_CHECK = {
    "libretexts_bpe": ("本文確認", "沸点上昇の式と水の Kb = 0.512 ℃/m。パスタの湯で沸点を数℃上げるには 1 L に 100 g を超える食塩が要る"),
}
M_NACL = 58.44   # g/mol（物理定数）
PCTS = [0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0]


def dT(salt_g_per_kg_water: float) -> float:
    m = salt_g_per_kg_water / M_NACL
    return P.V("bpe_Kb_water") * m * P.V("bpe_i_nacl")


def compute() -> dict:
    rows = [{"pct": p, "g": 10 * p, "dT": dT(10 * p)} for p in PCTS]
    need_1C = 1 / (P.V("bpe_Kb_water") * P.V("bpe_i_nacl")) * M_NACL
    return {"rows": rows, "need_1C": need_1C, "d100": dT(100)}


DISH_COLORS = [("x", "x", "#888888", "#888888")]


def page() -> str:
    Cm = compute()
    rows = Cm["rows"]
    r1 = next(r for r in rows if r["pct"] == 1.0)
    H = C.head("塩と沸点", C.css(DISH_COLORS, C.CSS_FIG))
    A = H.append
    A('<div class="wrap">')
    A(C.header(5, 'パスタの湯に塩を入れると、沸点が上がって早くゆだる？',
               '判定と確かさ・決め手の図・言えないこと・自分で試す手順を先に置き、通説の説明・計算の詳しい答え・根拠を後ろに並べたページです。'
               '通説の説明と結論の文章は本人が書きます（いまは空欄と材料）。'))

    A(C.h2("claim", 1, "通説", '<div class="card">'))
    A('<p class="claim">「パスタをゆでる湯に塩を入れるのは、沸点が上がって早くゆだるから」</p>')
    A(C.owner_slot("この通説がどう言われているか・なぜ気になったか", [
        '言われる理由: 塩を入れると湯の温度が上がる',
        '塩を入れる理由としては、ほかに「麺に塩味を付ける」も言われる（味の話。計算の対象外）',
        '計算で扱えるのは、沸点が何℃上がるか（沸点上昇の式）。麺の火の通りの速さは扱えない',
    ]))
    A('</div></section>')

    A(C.h2("calc", 2, "計算の詳しい答え"))
    A('<p>水 1 kg（1 L）に溶かした食塩の量ごとに、沸点が何℃上がるかを、沸点上昇の式 ΔTb = Kb × m × i で計算しました（R-W04）。'
      f'Kb = {P.V("bpe_Kb_water"):g} ℃·kg/mol、食塩の分子量 {M_NACL:g} g/mol、i = {P.V("bpe_i_nacl"):g}（食塩が完全に分かれたときの理想の値、推定。実際は少し小さいので、上がり幅はこれより少し小さい）。</p>')
    A('<div class="tablewrap"><table><thead><tr><th>塩の濃さ（水に対して %）</th><th>水 1 L あたり（g）</th><th>大さじ（約 18 g、推定）</th><th>沸点の上がり幅（℃）</th></tr></thead><tbody>'
      + "".join(f'<tr><td class="num">{r["pct"]:g}</td><td class="num">{r["g"]:g}</td><td class="num">{r["g"] / 18:.1f}</td><td class="num">{r["dT"]:.2f}</td></tr>' for r in rows)
      + '</tbody></table></div>')
    A('<ul class="find">')
    A(f'<li><b>よく使う 1% の塩（1 L に 10 g）で、沸点は {r1["dT"]:.2f}℃ 上がるだけ。</b>1℃ 上げるには 1 L に約 {Cm["need_1C"]:.0f} g（約 {Cm["need_1C"] / 10:.1f}%）が要る。'
      f'100 g 入れると {Cm["d100"]:.1f}℃（出典の「100 g を超えて数℃」と合う）。</li>')
    A('<li class="muted small">注意: 麺がゆだる速さは計算していません（パスタの規則が無い）。湯の温度が 0.2℃ 違うことが、ゆで時間にどれだけ効くかは分かりません。</li>')
    A('</ul></section>')

    A(C.keyfig("塩の濃さと、沸点の上がり幅（計算）",
               C.svg_bars([(f'{r["pct"]:g}%（1 L に {r["g"]:g} g）', r["dT"], 2 if r["pct"] == 1.0 else 0) for r in rows], "℃", fmt="{:.2f}"),
               f'料理で使う 1% 前後では {r1["dT"]:.2f}℃。沸点を目に見えて上げるには、食べられないほどの塩が要る。'))

    A(C.h2("basis", 3, "根拠"))
    A(C.basis_links(RULE_IDS, SOURCE_IDS))
    use = {"R-W04": "沸点の上がり幅を計算した（Kb・i は採用値）。シミュレータの沸点にはまだ入れていない",
           "R-W01": "水の沸点 100℃（1気圧）。上がり幅の基準"}
    H.extend(C.rules_table(RULE_IDS, use))
    H.extend(C.sources_table(SOURCE_IDS, SOURCE_CHECK, col4="この計算で使ったこと"))
    A('</section>')

    A(C.h2("verdict", 4, "判定と確かさ"))
    CAN = ([f'塩を入れると沸点は<b>上がるが、料理の量ではごくわずか</b>。1% の塩で {r1["dT"]:.2f}℃（i = 2 の理想の値で、実際はこれ以下）。{C.conf("高")}',
            f'沸点を 1℃ 上げるには 1 L に約 {Cm["need_1C"]:.0f} g の塩が要る。教科書（LibreTexts）の「100 g を超えて数℃」と合う。{C.conf("高")}',
            '「早くゆだる」理由としては、沸点の上がり幅が小さすぎて説明にならない（湯の温度の差が 0.2℃ 前後）。' + C.conf("中")],
           ['麺が実際に何秒早くゆだるか。パスタの規則が無く、計算していない。',
            '塩を入れたときに一瞬泡立つこと（溶ける塩の粒が泡のきっかけになる、と言われる）。計算の対象外。',
            '塩味・麺の食感への効果。塩を入れる本当の理由かもしれないが、味の話で計算の対象外。',
            'i（食塩が分かれる割合）の実際の値。今回は理想の値 2 を使った（推定）。'])
    A(C.can_card(CAN[0]))
    A(C.owner_slot("結論（まとめの文章）", [
        f'1% の塩（1 L に 10 g）で沸点は {r1["dT"]:.2f}℃ 上がる（計算）',
        f'1℃ 上げるには 1 L に約 {Cm["need_1C"]:.0f} g（大さじ 3 杯強）',
        '確かさ: 上がり幅は 高（教科書の式）。「だから早くゆだる」は 低〜中（麺は計算していない）',
    ], note="下の実験の結果を見てから書くのでもよい"))
    A('</section>')
    A(C.h2("cannot", 5, "言えないこと") + C.cannot_card(CAN[1]) + '</section>')

    A(C.h2("try", 6, "自分で試す"))
    A('<p>0.1℃ 単位で測れる温度計があれば、沸点の違いを測れます（ふつうの料理用温度計では差が見えません）。</p>')
    A(C.steps([
        '同じ鍋に水 1 L を沸騰させ、温度計の先を鍋底につけずに湯の中ほどに入れて、温度を書く（塩なし）。',
        '火を止めずに、塩 10 g を入れ、再び沸騰したら温度を書く。',
        'さらに塩 20 g（合計 30 g）、さらに 70 g（合計 100 g）と足して、そのつど書く。',
        '気圧（天気予報の hPa）も書いておく。沸点は気圧でも変わる。',
    ]))
    pred = {g: dT(g) for g in (0, 10, 30, 100)}
    H.extend(C.record_table(["塩の合計（g）", "測った温度（℃）", "塩なしとの差（℃）", "計算の予言（差）"],
                            [f'<tr><td class="num">{g}</td><td></td><td></td><td class="pred">+{pred[g]:.2f}℃</td></tr>' for g in (0, 10, 30, 100)]))
    A('<p class="small muted">予言は i = 2 の理想の値なので、実際の差は少し小さく出るはずです。</p>')
    A('</section>')

    A(C.footer('Cuisine Network。計算: 沸点上昇の式（rules.yaml R-W04・採用値 bpe_Kb_water・bpe_i_nacl）。'
               'このページは experiments/myths/build.py（通説5 salt_boil）が生成します。'))
    A('</div>')
    return C.reorder(C.join(H))
