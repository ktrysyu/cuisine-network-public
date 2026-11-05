"""通説7: 肉は焼く前に常温に戻す（2026-10-22、CLA-135）。

    uv run python experiments/myths/build.py meat_room_temp

- 計算: 通説3（sear_juice）と同じ肉の板（Exp-18 の厚み方向の熱伝導）を、最初の温度だけ 5℃（冷蔵庫）と 20℃（常温）にして、
  同じ手順（中火 175℃・90 秒ごとに返す）で中心 55℃まで焼き、4 分休ませる。焼く時間・外側の層の温度・失う重さ（R-P06）を比べる
- 「中まで均一に火が通る」を、外側の層と中心の最高温度の差で見る
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from myths import common as C  # noqa: E402
from myths import sear_juice as S  # noqa: E402
from myths.common import e  # noqa: E402
from sim import meat_slab as MS  # noqa: E402

ID = "meat_room_temp"
OUT = C.WRITEUP / "myth-meat-room-temp.html"

RULE_IDS = ["R-P06", "R-P02"]
SOURCE_IDS = ["vaskoska2020", "tokyogas_steak", "aussiebeef_steak", "ngadi2007", "ashrae_thermal"]
SOURCE_CHECK = {k: v for k, v in S.SOURCE_CHECK.items() if k in SOURCE_IDS}
SOURCE_CHECK["tokyogas_steak"] = ("本文確認", "厚さ約2cm・250g・「室温に戻す」・中火で中心 55℃まで。通説の手順の例。焼く時間の実測（90秒ごとに返して 6分30秒〜7分）")
T_FRIDGE, T_ROOM = 5.0, 20.0
STEPS = [("pan", S.P_MED, None, True)]


def compute() -> dict:
    MS.set_model("slab")
    try:
        r = {t0: S.run(STEPS, t0) for t0 in (T_FRIDGE, T_ROOM)}
    finally:
        MS.set_model(None)
    for x in r.values():
        n = len(x["tmax"])
        q = n // 4
        x["outer_max"] = sum(x["tmax"][:q] + x["tmax"][-q:]) / (2 * q)
        x["spread"] = x["outer_max"] - x["core_max"]
    return {"r": r}


DISH_COLORS = [("x", "x", "#888888", "#888888")]


def page() -> str:
    R = compute()["r"]
    f, rm = R[T_FRIDGE], R[T_ROOM]
    dt = f["t_cook"] - rm["t_cook"]
    H = C.head("肉を常温に戻す", C.css(DISH_COLORS, C.CSS_FIG))
    A = H.append
    A('<div class="wrap">')
    A(C.header(7, '肉は、焼く前に常温に戻す？',
               '判定と確かさ・決め手の図・言えないこと・自分で試す手順を先に置き、通説の説明・計算の詳しい答え・根拠を後ろに並べたページです。'
               '通説の説明と結論の文章は本人が書きます（いまは空欄と材料）。'))

    A(C.h2("claim", 1, "通説", '<div class="card">'))
    A('<p class="claim">「ステーキは、焼く前に冷蔵庫から出して常温に戻しておく。中まで均一に火が通る」</p>')
    A(C.owner_slot("この通説がどう言われているか・なぜ気になったか", [
        '言われる理由: 冷たいままだと外が焼けすぎて中が生になる／均一に火が通る',
        '東京ガスの実証も「室温に戻す」を条件に入れている（tokyogas_steak）',
        '計算で扱えるのは、最初の温度だけを変えたときの焼く時間・外側と中心の温度の差・失う重さ。常温に置く間に肉の温度がどこまで上がるかは扱っていない（ここでは 20℃ になったとした）',
    ]))
    A('</div></section>')

    A(C.h2("calc", 2, "計算の詳しい答え"))
    A(f'<p>通説3と同じ牛肉（{S.BEEF_G} g・厚さ {S.THICK_MM} mm）を、中火 {S.P_MED}℃ で 90 秒ごとに返して中心 {S.TARGET:g}℃まで焼き、{S.REST_MIN:g} 分休ませました。最初の温度だけを {T_FRIDGE:g}℃ と {T_ROOM:g}℃ にしています。</p>')
    A('<div class="tablewrap"><table><thead><tr><th>最初の温度</th><th>焼く時間（分）</th><th>休ませた後の中心の最高（℃）</th><th>外側（表から 5 mm）の最高の平均（℃）</th><th>外側と中心の差（℃）</th><th>失う重さ（%）</th></tr></thead><tbody>'
      + "".join(f'<tr><td>{lab}（{t0:g}℃）</td><td class="num">{R[t0]["t_cook"]:.1f}</td><td class="num">{R[t0]["core_max"]:.1f}</td><td class="num">{R[t0]["outer_max"]:.1f}</td>'
                f'<td class="num">{R[t0]["spread"]:.1f}</td><td class="num">{R[t0]["loss_pct"]:.1f}</td></tr>' for lab, t0 in (("冷蔵庫から出してすぐ", T_FRIDGE), ("常温に戻した", T_ROOM)))
      + '</tbody></table></div>')
    depth = [(i + 0.5) * S.THICK_MM / len(f["tmax"]) for i in range(len(f["tmax"]))]
    A('<figure class="chart"><figcaption>厚さ方向の各層が届いた最高の温度</figcaption>'
      + C.svg_lines([(f"最初 {T_FRIDGE:g}℃", 0, list(zip(depth, f["tmax"])), False), (f"最初 {T_ROOM:g}℃", 2, list(zip(depth, rm["tmax"])), True)],
                    "肉の中の位置（mm）", "最高温度（℃）", (0, S.THICK_MM), (40, 100), [(60, "60℃"), (70, "70℃")]) + '</figure>')
    A(C.legend_lines([(f"冷蔵（{T_FRIDGE:g}℃）", 0, False), (f"常温（{T_ROOM:g}℃）", 2, True)]))
    A('<ul class="find">')
    A(f'<li><b>冷蔵のままだと、焼く時間が {dt:.1f} 分長くなる</b>（{rm["t_cook"]:.1f} → {f["t_cook"]:.1f} 分）。</li>')
    A(f'<li><b>外側と中心の差は {f["spread"]:.1f}℃ と {rm["spread"]:.1f}℃</b>、失う重さは {f["loss_pct"]:.1f}% と {rm["loss_pct"]:.1f}%。'
      + ('冷蔵のままのほうが外側がやや焼けすぎる向き。' if f["spread"] > rm["spread"] + 0.5 else 'ほとんど同じで、「均一に火が通る」差は計算ではわずか。') + '</li>')
    A('<li class="muted small">注意: 肉の温まり方は Exp-18 の計算（実測より 1〜2 割速い・休ませる間の上昇が大きい）。失う重さは 30 分保った値（R-P06）を当てたもので、多めに出ます。</li>')
    A('</ul></section>')

    A(C.keyfig("最初の温度だけを変えて、同じ中心温度まで焼いたとき（計算）",
               C.svg_bars([(f"焼く時間 冷蔵 {T_FRIDGE:g}℃", f["t_cook"], 0), (f"焼く時間 常温 {T_ROOM:g}℃", rm["t_cook"], 2)], " 分"),
               f'冷蔵のままだと {dt:.1f} 分長く焼くことになる。外側と中心の差は {f["spread"]:.1f}℃ と {rm["spread"]:.1f}℃、失う重さは {f["loss_pct"]:.1f}% と {rm["loss_pct"]:.1f}%。'))

    A(C.h2("basis", 3, "根拠"))
    A(C.basis_links(RULE_IDS, SOURCE_IDS))
    use = {"R-P06": "層ごとの最高温度から失う重さを読む（通説3と同じ）", "R-P02": "参考（60℃で肉汁が急に出る）"}
    H.extend(C.rules_table(RULE_IDS, use))
    H.extend(C.sources_table(SOURCE_IDS, SOURCE_CHECK, col4="この計算で使ったこと"))
    A('</section>')

    A(C.h2("verdict", 4, "判定と確かさ"))
    CAN = ([f'冷蔵のまま焼くと、同じ中心温度まで <b>{dt:.1f} 分長くかかる</b>（計算）。向きは熱の伝わり方から確か、分の値は近似による。{C.conf("中")}',
            f'外側と中心の差（{f["spread"]:.1f}℃ と {rm["spread"]:.1f}℃）・失う重さ（{f["loss_pct"]:.1f}% と {rm["loss_pct"]:.1f}%）の違いは小さい。「均一に火が通る」効果は計算では小さい。{C.conf("低")}'],
           ['常温に置いて肉が実際に何℃になるか。厚い肉は 30 分〜1 時間ではあまり上がらないと言われる（出典は確かめていない）。ここでは 20℃ になったとした。',
            '表面の乾き・焼き色のつきやすさ（冷たい肉の表面が結露で濡れる、など）。計算に無い。',
            '置いておく間の衛生。対象外。',
            '厚さ・重さが違う肉。厚さ 20 mm の1通りだけ。'])
    A(C.can_card(CAN[0]))
    A(C.owner_slot("結論（まとめの文章）", [
        f'焼く時間（計算）: 冷蔵 {f["t_cook"]:.1f} 分・常温 {rm["t_cook"]:.1f} 分',
        f'外側と中心の差: {f["spread"]:.1f}℃・{rm["spread"]:.1f}℃、失う重さ: {f["loss_pct"]:.1f}%・{rm["loss_pct"]:.1f}%',
        '確かさ: 時間の差の向きは 中、均一さの差は 低（計算の差が小さく、近似の確かさを超えない）',
    ], note="下の実験の結果を見てから書くのでもよい"))
    A('</section>')
    A(C.h2("cannot", 5, "言えないこと") + C.cannot_card(CAN[1]) + '</section>')

    A(C.h2("try", 6, "自分で試す"))
    A('<p>同じ肉を2枚、片方は冷蔵庫から出してすぐ、片方は 1 時間置いてから焼きます。肉に刺す温度計と、はかりが要ります。</p>')
    A(C.steps([
        '同じかたまりから厚さ 2 cm のステーキ肉を2枚。1 枚は 1 時間前に冷蔵庫から出す。',
        '焼く直前に、両方の中心の温度を測って書く（常温に置いた肉が何℃になっているか）。',
        '焼く前の重さを量る。',
        f'中火で 90 秒ごとに返し、中心が {S.TARGET:g}℃ になったら下ろす。焼いた時間を書く。',
        f'{S.REST_MIN:g} 分休ませて重さを量り、縦に切って断面の色（外側の灰色の帯の厚さ）を写真に撮る。',
    ]))
    H.extend(C.record_table(["肉", "焼く直前の中心（℃）", "焼いた時間（分）", "焼く前（g）", "休ませた後（g）", "灰色の帯（mm）", "写真", "計算の予言"],
                            [f'<tr><td>{lab}</td><td></td><td></td><td></td><td></td><td></td><td class="photo"></td><td class="pred">焼く時間 {R[t0]["t_cook"]:.1f} 分</td></tr>'
                             for lab, t0 in (("冷蔵からすぐ", T_FRIDGE), ("1時間置いた", T_ROOM))]))
    A('</section>')
    A(C.footer('Cuisine Network。計算: Exp-18 の肉の熱伝導（experiments/exp-14/sim/meat_slab.py）と R-P06。通説3（sear_juice）と同じ計算。'
               'このページは experiments/myths/build.py（通説7 meat_room_temp）が生成します。'))
    A('</div>')
    return C.reorder(C.join(H))
