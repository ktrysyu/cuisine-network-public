"""通説8（候補の11）: 鶏むね肉は低温でゆっくり加熱するとしっとりする（2026-10-22、CLA-135）。

    uv run python experiments/myths/build.py chicken_low

- 計算: 鶏むね肉（成分表の若どり むね 皮なし）を厚さ 20 mm の板として、厚み方向の熱伝導（Exp-18 の meat_slab）で解く
- 安全: 中心の温度の経過から、サルモネラを 7 桁減らすのに要る時間（R-P07、FSIS の表）に対する割合を足し合わせ、1 に届いたら安全とする
- しっとり: 層ごとの最高温度のうち、むね肉が乾く 70℃（R-P04）を超えた層の割合と、失う重さ（R-P06。牛肉の値を鶏に代用＝推定）
- 冷蔵庫（5℃）から出してすぐ湯に入れる（安全側）
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from myths import common as C  # noqa: E402
from myths import sear_juice as S  # noqa: E402
from myths.common import P, e  # noqa: E402
from sim import meat_slab as MS  # noqa: E402

ID = "chicken_low"
OUT = C.WRITEUP / "myth-chicken-low.html"

RULE_IDS = ["R-P07", "R-P05", "R-P04", "R-P06"]
SOURCE_IDS = ["fsis_poultry_tables", "fsis", "soc_temps", "vaskoska2020", "ashrae_thermal"]
SOURCE_CHECK = {
    "fsis_poultry_tables": ("本文確認（写し）", "鶏・脂肪 2% でサルモネラを 7 桁減らす時間（60℃ 25.7 分・62.8℃ 8.6 分・65.6℃ 2.7 分・73.9℃ 10 秒未満）。中心の安全の判定に使った"),
    "fsis": ("抜粋のみ", "鶏肉の安全な中心温度 165°F（74℃）。フライパンで焼く手順の止め方に使った"),
    "soc_temps": ("本文確認", "むね肉は 70℃（158°F）で乾く（R-P04）"),
    "vaskoska2020": ("本文確認", "牛肉の加熱損失と温度（R-P06）。鶏に代用した（推定）"),
    "ashrae_thermal": ("本文確認", "肉の成分から熱の伝わりやすさ・比熱・密度を出す式"),
}
MASS, THICK_MM, T0, T_ROOM = 200, 20, 5.0, 20.0
BATHS = [60, 62.5, 65, 70]
PAN, PAN_TARGET, REST = 180, 74.0, 4.0
DT = 0.05


def t_req(T: float) -> float | None:
    """その温度で 7 桁減らすのに要る時間（分）。表より低い温度は None（数えない）。"""
    tab = [((f - 32) / 1.8, m) for f, m in P.V("poultry_7log_min_fat2")]
    if T < tab[0][0]:
        return None
    if T >= tab[-1][0]:
        return tab[-1][1]
    for (a, ma), (b, mb) in zip(tab, tab[1:]):
        if T <= b:
            return math.exp(math.log(ma) + (math.log(mb) - math.log(ma)) * (T - a) / (b - a))
    return tab[-1][1]


def simulate(kind: str, T_med: float) -> dict:
    sl = MS.MeatSlab(THICK_MM / 1000.0, MS.mass_fractions({"chicken": MASS}), T0)
    tmax = list(sl.T)
    leth, t = 0.0, 0.0
    t_safe = None

    def tick(medium, T):
        nonlocal tmax, leth, t, t_safe
        sl.step(DT, *MS.boundary(medium, T, T_ROOM), 100.0)
        t += DT
        tmax = [max(a, b) for a, b in zip(tmax, sl.T)]
        r = t_req(min(sl.T))   # 一番冷たい層（中心付近）で数える
        if r:
            leth += DT / r
        if t_safe is None and leth >= 1:
            t_safe = t

    if kind == "bath":
        while leth < 1 and t < 300:
            tick("water", T_med)
        t_heat = t
    else:
        since = 0.0
        while sl.T_center < PAN_TARGET and t < 60:
            tick("pan", T_med)
            since += DT
            if since >= 1.5 - 1e-9:
                sl.flip()
                tmax = list(reversed(tmax))
                since = 0.0
        t_heat = t
        for _ in range(int(REST / DT)):
            tick("air", T_ROOM)
    curve = [(T0, 0.0)] + S.loss_curve()[1:]
    loss = sum(S.loss_at(x, curve) for x in tmax) / len(tmax)
    dry = sum(x > 70 for x in tmax) / len(tmax)
    return {"t_heat": t_heat, "t_safe": t_safe, "leth": leth, "core_max": max(tmax[len(tmax) // 2 - 1:len(tmax) // 2 + 1]),
            "tmax": tmax, "loss": loss, "dry": dry}


def compute() -> dict:
    MS.set_model("slab")
    try:
        res = {f"bath{T:g}": simulate("bath", T) for T in BATHS}
        res["pan"] = simulate("pan", PAN)
    finally:
        MS.set_model(None)
    return {"res": res}


NAMES = {**{f"bath{T:g}": f"{T:g}℃ の湯" for T in BATHS}, "pan": f"フライパン {PAN}℃・中心 {PAN_TARGET:g}℃まで"}
COLORS = {"bath60": 0, "bath62.5": 0, "bath65": 1, "bath70": 1, "pan": 2}
DISH_COLORS = [("x", "x", "#888888", "#888888")]


def page() -> str:
    R = compute()["res"]
    pan = R["pan"]
    b60, b65 = R["bath60"], R["bath65"]
    H = C.head("鶏むね肉を低温で", C.css(DISH_COLORS, C.CSS_FIG))
    A = H.append
    A('<div class="wrap">')
    A(C.header(8, '鶏むね肉は、低温でゆっくり加熱するとしっとりする？',
               '判定と確かさ・決め手の図・言えないこと・自分で試す手順を先に置き、通説の説明・計算の詳しい答え・根拠を後ろに並べたページです。'
               '通説の説明と結論の文章は本人が書きます（いまは空欄と材料）。'))

    A(C.h2("claim", 1, "通説", '<div class="card">'))
    A('<p class="claim">「鶏むね肉は、低い温度（60℃台）でゆっくり火を通すと、パサつかずしっとりする」</p>')
    A(C.owner_slot("この通説がどう言われているか・なぜ気になったか", [
        '言われる理由: 高い温度だと水分が出て硬くなる。むね肉は 70℃ で乾く（R-P04）',
        '気になる点: 安全な中心温度は 74℃（R-P05）と言われ、乾く 70℃ と近い（C10）。低温で安全にできるのか',
        '計算で扱えるのは、中心の温度の経過からサルモネラを減らす時間が足りるか（R-P07）と、何℃まで上がった層がどれだけあるか',
    ]))
    A('</div></section>')

    A(C.h2("calc", 2, "計算の詳しい答え"))
    A(f'<p>鶏むね肉（{MASS} g・厚さ {THICK_MM} mm、冷蔵庫の {T0:g}℃ から）を、湯（低温調理）とフライパンで加熱しました。湯は、中心でサルモネラを 7 桁減らす時間が足りたところで止めます（R-P07）。'
      f'フライパンは中心 {PAN_TARGET:g}℃（R-P05）まで焼いて {REST:g} 分休ませます。</p>')
    A('<div class="tablewrap"><table><thead><tr><th>加熱</th><th>加熱した時間（分）</th><th>中心の最高（℃）</th><th>70℃ を超えた層の割合</th><th>失う重さ（%、推定）</th><th>中心の安全</th></tr></thead><tbody>'
      + "".join(f'<tr><td>{e(NAMES[k])}</td><td class="num">{r["t_heat"]:.1f}</td><td class="num">{r["core_max"]:.1f}</td><td class="num">{r["dry"] * 100:.0f}%</td>'
                f'<td class="num">{r["loss"]:.1f}</td><td>{"足りた" if r["leth"] >= 1 else f"足りない（{r["leth"]:.2f}）"}</td></tr>' for k, r in R.items())
      + '</tbody></table></div>')
    A('<ul class="find">')
    A(f'<li><b>60℃ の湯でも、時間をかければ中心の安全は足りる</b>（{b60["t_heat"]:.0f} 分）。65℃ なら {b65["t_heat"]:.0f} 分。どの層も 70℃ を超えない。</li>')
    A(f'<li><b>フライパンで中心 {PAN_TARGET:g}℃ まで焼くと、層の {pan["dry"] * 100:.0f}% が 70℃ を超える</b>（外側ほど高い）。失う重さは {pan["loss"]:.1f}%、60℃ の湯では {b60["loss"]:.1f}%。</li>')
    A('<li class="muted small">注意: 失う重さは牛肉の値（R-P06、30 分保った値）を鶏に代用した推定で、値は確かではありません。比べられるのは大小の向きです。'
      '安全の判定は、一番冷たい層の温度で表（R-P07）の時間に対する割合を足し合わせたもの（表の間は対数で補間、推定）。湯の温度のぶれ・肉の厚さのばらつきは入れていません。</li>')
    A('</ul></section>')

    A(C.keyfig("加熱のしかたと、70℃ を超えた層の割合・失う重さ（計算）",
               C.svg_bars([(NAMES[k], r["loss"], COLORS[k]) for k, r in R.items()], "%"),
               '低温の湯ほど失う重さが少なく、どの層も乾く 70℃ を超えない。安全は「温度 × 時間」で足りる（60℃ なら長く保つ）。'))

    A(C.h2("basis", 3, "根拠"))
    A(C.basis_links(RULE_IDS, SOURCE_IDS))
    use = {"R-P07": "中心（一番冷たい層）の温度の経過から、7 桁減らす時間に対する割合を足し合わせ、1 で安全とした（表の間は対数で補間・57.8℃未満は数えない）",
           "R-P05": f"フライパンの手順を中心 {PAN_TARGET:g}℃ で止めた",
           "R-P04": "70℃ を超えた層を「乾く」層として数えた",
           "R-P06": "失う重さ（牛肉の値を鶏に代用、推定）"}
    H.extend(C.rules_table(RULE_IDS, use))
    H.extend(C.sources_table(SOURCE_IDS, SOURCE_CHECK, col4="この計算で使ったこと"))
    A('</section>')

    A(C.h2("verdict", 4, "判定と確かさ"))
    CAN = ([f'鶏肉は 74℃ でなくても、<b>温度に応じた時間を保てば安全</b>（FSIS の表: 60℃ で 25.7 分など）。{C.conf("高")}',
            f'低温の湯（60〜65℃）では、どの層も乾く 70℃ を超えずに中心の安全が足りる（計算: 60℃ で {b60["t_heat"]:.0f} 分）。フライパンで 74℃ まで焼くと外側の多くが 70℃ を超える。{C.conf("中")}',
            f'失う重さはフライパン {pan["loss"]:.1f}%・60℃ の湯 {b60["loss"]:.1f}%（牛肉の値を代用した推定）。低温のほうが少ない向き。{C.conf("低")}'],
           ['「しっとり」と感じるか。感じ方は計算に無い（乾く 70℃ の規則と、失う重さまで）。',
            '鶏肉の加熱損失の値。牛肉の値を代用した。',
            '家庭の湯の温度のぶれ・肉の厚さのばらつき。安全の時間はこれで大きく変わるので、実際には余裕を持つ必要がある。',
            'サルモネラ以外の菌・芽胞。表は 7 桁のサルモネラだけ。'])
    A(C.can_card(CAN[0]))
    A(C.owner_slot("結論（まとめの文章）", [
        f'中心の安全までの時間（計算、厚さ 20 mm・5℃から）: ' + "、".join(f'{NAMES[f"bath{T:g}"]} {R[f"bath{T:g}"]["t_heat"]:.0f} 分' for T in BATHS),
        f'70℃ を超えた層: フライパン {pan["dry"] * 100:.0f}%・低温の湯 0%',
        '確かさ: 安全の表は 高（公的機関の表）、計算の時間は 中（熱伝導の近似・厚さの推定）、しっとり感は計算外',
        '安全のため、本人が試すときは温度計と時間に余裕を（計算は家庭の条件のぶれを入れていない）',
    ], note="下の実験の結果を見てから書くのでもよい"))
    A('</section>')
    A(C.h2("cannot", 5, "言えないこと") + C.cannot_card(CAN[1]) + '</section>')

    A(C.h2("try", 6, "自分で試す"))
    A('<p><b>安全のため、湯の温度を測れる温度計と、肉の中心を測れる温度計が必須です。</b>計算の時間より長めに保ってください（計算は湯の温度のぶれ・肉の厚さを入れていません）。</p>')
    A(C.steps([
        '同じ鶏むね肉を厚さ 2 cm にそろえて 2 枚。重さを量る。',
        'A: 65℃ の湯（温度計で確かめ、ぶれたら火加減で戻す）に袋に入れて沈め、中心が 65℃ になってから 10 分以上保つ（表では 65.6℃ で 2.7 分。余裕を持つ）。',
        f'B: フライパン（中火）で返しながら、中心が {PAN_TARGET:g}℃ になるまで焼き、{REST:g} 分休ませる。',
        '両方の重さを量り、失った割合を出す。切って食べ比べ、しっとり感を書く。',
    ]))
    H.extend(C.record_table(["肉", "加熱", "中心の最高（℃）", "保った時間（分）", "前（g）", "後（g）", "失った割合（%）", "しっとり（1〜5）", "計算の予言"],
                            [f'<tr><td>A</td><td>65℃ の湯</td><td></td><td></td><td></td><td></td><td></td><td></td><td class="pred">失う重さ {b65["loss"]:.0f}%（推定）・70℃超の層 0%</td></tr>',
                             f'<tr><td>B</td><td>フライパン</td><td></td><td></td><td></td><td></td><td></td><td></td><td class="pred">失う重さ {pan["loss"]:.0f}%（推定）・70℃超の層 {pan["dry"] * 100:.0f}%</td></tr>']))
    A('</section>')
    A(C.footer('Cuisine Network。計算: Exp-18 の肉の熱伝導（meat_slab）、R-P07（FSIS の表）・R-P04・R-P06。'
               'このページは experiments/myths/build.py（通説8 chicken_low）が生成します。'))
    A('</div>')
    return C.reorder(C.join(H))
