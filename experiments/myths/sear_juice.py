"""通説3: 肉は先に焼き目を付けると肉汁を閉じ込める（2026-10-22、CLA-135）。

    uv run python experiments/myths/build.py sear_juice

- 計算: 肉片を厚み方向の熱伝導で解く形（Exp-18 の meat_slab、sim/meat_slab.py）を直接使い、厚さ方向の各層が
  到達した最高温度を記録する。加熱損失（肉汁・水分として失う重さ）は、層ごとの最高温度に R-P06（vaskoska2020: 50・60・70・80℃に
  30分保った牛肉の加熱損失）を当てはめて、体積で平均した（合わせ込みはしない）
- 比べるのは「同じ中心温度（55℃、tokyogas_steak・aussiebeef_steak）まで焼いて休ませる」4通り。焼き目の有無と火加減だけを変える
- 正直に書いておくこと: 加熱損失の値は 30分保った後の値（上限に近い）で、短い加熱での失い方の速さは入れていない。50℃未満は
  0（20℃）から直線で近づけた（推定）。80℃を超える部分（表面の乾いた層）は 80℃ の値のまま（多めには数えない）
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from myths import common as C  # noqa: E402
from myths.common import P, e  # noqa: E402
from sim import meat_slab as MS  # noqa: E402

ID = "sear_juice"
OUT = C.WRITEUP / "myth-sear-juice.html"

RULE_IDS = ["R-P06", "R-P01", "R-P02", "R-P05"]
SOURCE_IDS = ["vaskoska2020", "wiki_searing", "mcgee", "tokyogas_steak", "aussiebeef_steak", "ngadi2007", "ashrae_thermal"]
SOURCE_CHECK = {
    "vaskoska2020": ("本文確認", "牛肉の3つの筋肉を 50・60・70・80℃の湯に 30 分。加熱損失は 7〜11%・17〜21%・29〜32%・34〜40%。温度とともに増える。層ごとの失う割合に使った"),
    "wiki_searing": ("本文確認", "1930年代から試されていて、焼き目を付けた肉は同じかそれ以上の水分を失った。McGee（2004）p.161 を引く"),
    "mcgee": ("未確認（書籍）", "焼き目は肉汁を閉じ込めない、同じ中心温度なら焼き目を付けたほうが多く失う（Wikipedia が引く p.161。書籍本文は開いていない）"),
    "tokyogas_steak": ("本文確認", "厚さ約2cm・250g・室温に戻す・中火で中心 55℃まで。条件をそろえるのに使った"),
    "aussiebeef_steak": ("本文確認", "ミディアムは中心 約55℃、3〜5分休ませる。強火→弱火の手順"),
    "ngadi2007": ("本文確認", "フライパンに触れた面と上の面の熱の伝わりやすさ（h = 300・60 W/(m²·K)）"),
    "ashrae_thermal": ("本文確認", "肉の成分から熱の伝わりやすさ・比熱・密度を出す式（Choi & Okos）"),
}

BEEF_G, THICK_MM, T0, TARGET, REST_MIN = 250, 20, 20.0, 55.0, 4.0
P_HIGH, P_MED, P_LOW, OVEN = 230, 175, 130, 120   # Exp-15 extraction_rules.md P-HIGH（出典なし）・P-MED（弱い根拠）・P-LOW（出典なし）。オーブンは推定
FLIP_MIN = 1.5

# (鍵, 名前, 手順の説明, 色番号, 手順)。手順は [(媒体, 温度, 分 or None=中心が TARGET まで, 返すか)]
SCENARIOS = [
    ("sear_first", "焼き目を付けてから弱火", f"強火 {P_HIGH}℃ で片面 1 分ずつ焼き目を付け、弱火 {P_LOW}℃ で 90 秒ごとに返して中心 {TARGET:g}℃まで", 2,
     [("pan", P_HIGH, 1.0, False), ("pan", P_HIGH, 1.0, True), ("pan", P_LOW, None, True)]),
    ("low_only", "焼き目なし（弱火だけ）", f"弱火 {P_LOW}℃ で 90 秒ごとに返して中心 {TARGET:g}℃まで", 0,
     [("pan", P_LOW, None, True)]),
    ("medium", "中火のまま", f"中火 {P_MED}℃ で 90 秒ごとに返して中心 {TARGET:g}℃まで（東京ガスの手順）", 1,
     [("pan", P_MED, None, True)]),
    ("reverse", "低温のオーブン→最後に焼き目", f"{OVEN}℃ のオーブンで中心 {TARGET - 5:g}℃まで、強火 {P_HIGH}℃ で片面 1 分ずつ", 3,
     [("air", OVEN, "pre", False), ("pan", P_HIGH, 1.0, False), ("pan", P_HIGH, 1.0, True)]),
]


def loss_curve() -> list[tuple[float, float]]:
    """(温度, 加熱損失 %)。R-P06 の採用値（範囲の中央）に、はじめの温度で 0 を足す（推定）。"""
    pts = P.V("cook_loss_pct")
    return [(T0, 0.0)] + sorted((float(k), float(v)) for k, v in pts.items())


def loss_at(T: float, curve) -> float:
    if T <= curve[0][0]:
        return 0.0
    for (a, la), (b, lb) in zip(curve, curve[1:]):
        if T <= b:
            return la + (lb - la) * (T - a) / (b - a)
    return curve[-1][1]   # 80℃を超える部分は 80℃の値のまま


def run(steps, t0: float = T0) -> dict:
    """肉の板を手順どおりに焼き、休ませる。層ごとの最高温度・中心の経過を返す。"""
    fr = MS.mass_fractions({"beef": BEEF_G})
    sl = MS.MeatSlab(THICK_MM / 1000.0, fr, t0)
    tmax = list(sl.T)
    dt = 0.05
    t = 0.0
    trace = [(0.0, sl.T_center, sl.T[0])]
    curve0 = t0
    bp = 100.0   # 水がある間は沸点を超えない（R-W01、Exp-18 と同じ）

    def tick(medium, T_med):
        nonlocal t, tmax
        b = MS.boundary(medium, T_med, T0)
        sl.step(dt, *b, bp)
        t += dt
        tmax = [max(a, x) for a, x in zip(tmax, sl.T)]
        trace.append((round(t, 3), sl.T_center, max(sl.T[0], sl.T[-1])))

    def flip():
        nonlocal tmax
        sl.flip()
        tmax = list(reversed(tmax))

    for medium, T_med, dur, do_flip in steps:
        if do_flip:
            flip()
        if dur == "pre":
            while sl.T_center < TARGET - 5 and t < 120:
                tick(medium, T_med)
        elif dur is None:
            since = 0.0
            while sl.T_center < TARGET and t < 60:
                tick(medium, T_med)
                since += dt
                if since >= FLIP_MIN - 1e-9:
                    flip()
                    since = 0.0
        else:
            for _ in range(int(round(dur / dt))):
                tick(medium, T_med)
    t_cook = t
    core_at_end = sl.T_center
    for _ in range(int(round(REST_MIN / dt))):
        tick("air", T0)
    curve = [(min(curve0, T0), 0.0)] + loss_curve()[1:]
    losses = [loss_at(x, curve) for x in tmax]
    return {"t_cook": t_cook, "core_end": core_at_end, "core_max": max(c for _, c, _ in trace), "tmax": tmax,
            "loss_pct": sum(losses) / len(losses), "trace": trace,
            "outer_5mm": sum(losses[:len(losses) // 4] + losses[-(len(losses) // 4):]) / (2 * (len(losses) // 4))}


def compute() -> dict:
    MS.set_model("slab")
    try:
        res = {k: run(st) for k, *_, st in SCENARIOS}
    finally:
        MS.set_model(None)
    return {"res": res}


DISH_COLORS = [("x", "x", "#888888", "#888888")]


def page() -> str:
    Cm = compute()
    R = Cm["res"]
    nm = {k: n for k, n, *_ in SCENARIOS}
    a, b = R["sear_first"], R["low_only"]
    d_ab = a["loss_pct"] - b["loss_pct"]
    H = C.head("焼き目と肉汁", C.css(DISH_COLORS, C.CSS_FIG))
    A = H.append
    A('<div class="wrap">')
    A(C.header(3, '肉は、先に焼き目を付けると肉汁を閉じ込める？',
               '判定と確かさ・決め手の図・言えないこと・自分で試す手順を先に置き、通説の説明・計算の詳しい答え・根拠を後ろに並べたページです。'
               '通説の説明と結論の文章は本人が書きます（いまは空欄と材料）。'))

    A(C.h2("claim", 1, "通説", '<div class="card">'))
    A('<p class="claim">「ステーキは、最初に強火で表面を焼き固めると、肉汁が閉じ込められる」</p>')
    A(C.owner_slot("この通説がどう言われているか・なぜ気になったか", [
        '言われる理由: 表面のたんぱく質が固まって膜になり、中の汁が出ていかない',
        '反対の記録: 1930年代から試されていて、焼き目を付けた肉は同じかそれ以上の水分を失った（Wikipedia "Searing"、McGee 2004 p.161 を引く）',
        '計算で扱えるのは「同じ中心温度まで焼いたとき、失う重さ（加熱損失）が焼き目でどう変わるか」。表面に膜ができて汁を止めるかどうか（膜の性質）は扱えない',
    ]))
    A('</div></section>')

    # 計算の詳しい答え
    A(C.h2("calc", 2, "計算の詳しい答え"))
    A(f'<p>牛肉（成分表の牛ひき肉の成分、{BEEF_G} g・厚さ {THICK_MM} mm・{T0:g}℃から）を、厚み方向の熱の伝わり方で計算しました（Exp-18 の計算）。'
      f'4 通りとも中心が {TARGET:g}℃ になったら火から下ろし、{REST_MIN:g} 分休ませます。肉の中を {MS.S("nodes")} 層に分け、層ごとに届いた最高の温度から、'
      '牛肉を各温度に保ったときに失う重さの割合（R-P06）を読み、厚さで平均しました。</p>')
    A('<div class="tablewrap"><table><thead><tr><th>焼き方</th><th>手順</th><th>火にかけた時間（分）</th><th>休ませた後の中心の最高（℃）</th>'
      '<th>失う重さ（%）</th><th>うち表から 5 mm の層（%）</th><th>250 g あたり（g）</th></tr></thead><tbody>')
    for k, n, how, *_ in SCENARIOS:
        r = R[k]
        A(f'<tr><td>{e(n)}</td><td class="small">{e(how)}</td><td class="num">{r["t_cook"]:.1f}</td><td class="num">{r["core_max"]:.1f}</td>'
          f'<td class="num">{r["loss_pct"]:.1f}</td><td class="num">{r["outer_5mm"]:.1f}</td><td class="num">{r["loss_pct"] * BEEF_G / 100:.0f}</td></tr>')
    A('</tbody></table></div>')
    depth = [(i + 0.5) * THICK_MM / len(a["tmax"]) for i in range(len(a["tmax"]))]
    A(f'<figure class="chart"><figcaption>厚さ方向の各層が届いた最高の温度（休ませた後まで）</figcaption>'
      + C.svg_lines([(nm[k], c, list(zip(depth, R[k]["tmax"])), k == "reverse") for k, _, _, c, _ in SCENARIOS],
                    "肉の中の位置（mm、0 と 20 が表面）", "最高温度（℃）", (0, THICK_MM), (40, 100),
                    [(50, "50℃"), (60, "60℃"), (70, "70℃"), (80, "80℃")]) + '</figure>')
    A(C.legend_lines([(nm[k], c, k == "reverse") for k, _, _, c, _ in SCENARIOS]))
    A('<ul class="find">')
    A(f'<li><b>{"焼き目の有無で、失う重さはほとんど変わらない" if abs(d_ab) < 1 else ("焼き目を付けたほうが多く失う" if d_ab > 0 else "焼き目を付けたほうが少し少ない")}。</b>'
      f'焼き目を付けてから弱火 {a["loss_pct"]:.1f}%、焼き目なし（弱火だけ）{b["loss_pct"]:.1f}%（差 {d_ab:+.1f} ポイント）。'
      f'表から 5 mm の層でも {a["outer_5mm"]:.1f}% と {b["outer_5mm"]:.1f}%。この計算では、水が残っている間は表面が 100℃ を超えない（R-W01）ので、強火でも弱火でも表面の層は 100℃ 止まりになり、差が出にくい。</li>')
    A(f'<li><b>差を決めているのは、中の層がどこまで上がったか。</b>休ませる間に中心は {a["core_max"]:.0f}〜{max(r["core_max"] for r in R.values()):.0f}℃ まで上がり、'
      f'その上がり方が大きい焼き方（中火 {R["medium"]["loss_pct"]:.1f}%、低温のオーブン→焼き目 {R["reverse"]["loss_pct"]:.1f}%）ほど多く失う。'
      f'低温のオーブンの手順は、焼き目を付ける間に中心が {R["reverse"]["core_end"]:.1f}℃ まで上がっていて、ほかと同じ中心温度にはそろっていない。</li>')
    A('<li class="muted small">注意: 加熱損失の値（R-P06）は肉を各温度に 30 分保った後の値で、短い加熱では実際にはこれより少なく失います。'
      'ここで比べられるのは焼き方どうしの大小の向きで、何 g 失うかの値は確かではありません。表面の乾いた層（クラスト）・蒸発で逃げる熱・肉の縮みは入れていません（Exp-18）。</li>')
    A('</ul></section>')

    A(C.keyfig("同じ中心温度（55℃）まで焼いたときに失う重さ（計算）",
               C.svg_bars([(nm[k], R[k]["loss_pct"], c) for k, _, _, c, _ in SCENARIOS], "%"),
               f'焼き目ありとなしの差は {d_ab:+.1f} ポイント。焼き目を付けても失う重さは減らない（計算）。失う量を左右するのは、休ませる間を含めて中がどこまで上がったか。'))

    A(C.h2("basis", 3, "根拠"))
    A(C.basis_links(RULE_IDS, SOURCE_IDS))
    use = {
        "R-P06": "層ごとの最高温度から失う重さの割合を読む（50・60・70・80℃ の範囲の中央を直線でつなぐ。50℃未満は 20℃で 0 から直線＝推定、80℃超は 80℃ の値）",
        "R-P01": "参考（ミオシン・アクチンの変性温度）。この計算では失う重さに直接は使っていない",
        "R-P02": "参考（60℃で肉汁が急に出る）。R-P06 の 50→60℃ の増え方と向きが合う",
        "R-P05": "参考（牛ステーキの安全上の中心温度 63℃＋3分休ませる）。ここでは中心 55℃（ミディアムの手順）にそろえた",
    }
    H.extend(C.rules_table(RULE_IDS, use))
    H.extend(C.sources_table(SOURCE_IDS, SOURCE_CHECK, col4="この計算で使ったこと"))
    A('</section>')

    A(C.h2("verdict", 4, "判定と確かさ"))
    CAN = ([f'同じ中心温度（{TARGET:g}℃）まで焼くなら、<b>焼き目を先に付けても失う重さは減らない</b>。計算では焼き目ありが {a["loss_pct"]:.1f}%、なしが {b["loss_pct"]:.1f}%（差 {d_ab:+.1f} ポイント）。'
            f'出典（Wikipedia が引く McGee、1930年代からの実験「同じかそれ以上を失った」）と食い違わない。{C.conf("中")}',
            f'失う量を左右するのは焼き目ではなく、休ませる間を含めて中の層がどこまで上がったか（R-P06 は到達温度とともに増える）。{C.conf("中")}',
            '焼き目を付けたほうが「多く」失う、までは計算からは言えない（差が小さく、表面の乾いた層を入れていない）。'],
           ['<b>表面の膜が汁を止める力</b>そのもの。膜の性質（すき間・強さ）は計算に無い。',
            '何 g 失うかの値。R-P06 は 30 分保った後の値で、短い加熱の失い方の速さを入れていない。',
            '焼き目の<b>香ばしさ・おいしさ</b>。焼き目を付ける理由として正しい（メイラード反応、R-M01）が、肉汁の話とは別。',
            '休ませる間に皿に出る汁の量。休ませる間の上昇は計算では大きめに出る（Exp-18）。',
            '肉の種類・厚さ・脂の量による違い。牛ひき肉の成分・厚さ 20 mm の1通りだけ。',
            '強火の表面がどれだけ乾いて重さを失うか。計算では水が残る間は表面が 100℃ 止まり（R-W01）で、焼き目の層の乾きを持たない。'])
    A(C.can_card(CAN[0]))
    A(C.owner_slot("結論（まとめの文章）", [
        f'失う重さ（計算）: ' + "、".join(f'{nm[k]} {R[k]["loss_pct"]:.1f}%' for k, *_ in SCENARIOS),
        f'焼き目ありとなしの差: {d_ab:+.1f} ポイント（ほぼ同じ）。出典は「同じかそれ以上を失った」',
        '確かさ: 「焼き目で減らない」は 中（出典と計算が食い違わない）、値は 低（30分保った値を当てた）',
        '焼き目の役目は香ばしさ（メイラード反応）で、肉汁を閉じ込めることではない、という言い方ができる',
    ], note="下の実験の結果を見てから書くのでもよい"))
    A('</section>')
    A(C.h2("cannot", 5, "言えないこと") + C.cannot_card(CAN[1]) + '</section>')

    A(C.h2("try", 6, "自分で試す"))
    A('<p>同じ肉を2枚に切り、焼き方だけを変えて、焼く前と休ませた後の重さを量ります。中心温度をそろえるために温度計（肉に刺すもの）と、1 g 単位のはかりが要ります。</p>')
    A(C.steps([
        '同じかたまりから、厚さ 2 cm・同じくらいの重さのステーキ肉を2枚切る。30 分ほど室温に置く。',
        '焼く前の重さを量って書く。',
        f'A: 強火で片面 1 分ずつ焼き目を付け、弱火にして 90 秒ごとに返し、中心が {TARGET:g}℃ になったら火から下ろす。',
        f'B: はじめから弱火で 90 秒ごとに返し、中心が {TARGET:g}℃ になったら火から下ろす。',
        f'どちらも網か皿の上で {REST_MIN:g} 分休ませ、出た汁をふかずに肉だけの重さを量る。',
        '失った割合 =（焼く前 − 休ませた後）÷ 焼く前。できれば順番を入れ替えてもう一組。',
    ]))
    pred = {k: f'{R[k]["loss_pct"]:.0f}% 前後（多めに出る見積もり）' for k in R}
    H.extend(C.record_table(["回", "焼き方", "焼く前（g）", "中心温度（℃、下ろした時）", "焼いた時間（分）", "休ませた後（g）", "失った割合（%）", "計算の予言"],
                            [f'<tr><td class="num">{i}</td><td>{e(nm[k])}</td><td></td><td></td><td></td><td></td><td></td><td class="pred">{e(pred[k])}</td></tr>'
                             for i, k in enumerate(["sear_first", "low_only"], 1)]))
    A('<p class="small muted">計算の予言は「A と B はほぼ同じ」。A のほうがはっきり少なければ、通説の側に合う結果です。値は R-P06 が 30 分保った値なので、実際より多めに出ます。</p>')
    A('</section>')

    A(C.footer('Cuisine Network。計算: Exp-18 の肉の熱伝導（experiments/exp-14/sim/meat_slab.py）と R-P06（rules.yaml）。'
               'このページは experiments/myths/build.py（通説3 sear_juice）が生成します。'))
    A('</div>')
    return C.reorder(C.join(H))
