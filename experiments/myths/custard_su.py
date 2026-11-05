"""通説6: 茶碗蒸し・プリンは強火だと す が立つ（2026-10-22、CLA-135）。

    uv run python experiments/myths/build.py custard_su

- 計算: Exp-14 のシミュレータで、プリン液・茶碗蒸しの卵液を蒸す温度を変え、固まる（egg_gel_stage 2）までの時間と、
  す が立つ（porosity 1。中心が egg_porosity_T 以上）までの時間を比べる
- 正直に書いておくこと: す の規則（R-E15「中心 90℃ を超えると す」）は温度のしきい値で、す ができる仕組み（卵液の中の水や空気が
  泡になる）を解いていない。計算で言えるのは「蒸す温度ごとに、固まるのと 90℃ を超えるのがどちらが先か」まで。
  器の中の温まり方は一次遅れ（tau_min.cup、推定）
"""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from myths import common as C  # noqa: E402
from myths.common import P, e  # noqa: E402
from sim import DISH_RECIPES_TIMED  # noqa: E402

ID = "custard_su"
OUT = C.WRITEUP / "myth-custard-su.html"

RULE_IDS = ["R-E15", "R-W03", "R-E09"]
SOURCE_IDS = ["chawan_web"]
SOURCE_CHECK = {"chawan_web": ("抜粋のみ", "蒸し器の中を 85〜90℃ に保ち、卵液を沸騰させないと す が最小になる")}
TEMPS = [80, 82.5, 85, 87.5, 90, 92.5, 95, 97.5, 100]
DISHES = [("custard_pudding", "プリン", 0), ("chawanmushi", "茶碗蒸し", 2)]
MAX = 60


def times(dish: str, T: float) -> dict:
    base = DISH_RECIPES_TIMED[dish]
    i = next(k for k, (n, _) in enumerate(base.steps) if n == "steam")

    def until(cond):
        steps = list(base.steps[:i]) + [("steam", {"T": T, "form": "cup", "until": cond, "max_time": MAX})]
        s = replace(base, steps=steps).run()
        st = s.stops[-1]
        return st["minutes"] if st["reached"] else None
    return {"set": until({"var": "egg_gel_stage", "ge": 2}), "su": until({"var": "porosity", "ge": 1})}


def compute() -> dict:
    return {d: {T: times(d, T) for T in TEMPS} for d, *_ in DISHES}


DISH_COLORS = [("x", "x", "#888888", "#888888")]


def fmt(v):
    return "—" if v is None else f"{v:.1f}"


def page() -> str:
    Cm = compute()
    pT = P.V("egg_porosity_T")
    pu = Cm["custard_pudding"]
    H = C.head("蒸し物の す", C.css(DISH_COLORS, C.CSS_FIG))
    A = H.append
    A('<div class="wrap">')
    A(C.header(6, '茶碗蒸し・プリンは、強火で蒸すと す が立つ？',
               '判定と確かさ・決め手の図・言えないこと・自分で試す手順を先に置き、通説の説明・計算の詳しい答え・根拠を後ろに並べたページです。'
               '通説の説明と結論の文章は本人が書きます（いまは空欄と材料）。'))

    A(C.h2("claim", 1, "通説", '<div class="card">'))
    A('<p class="claim">「茶碗蒸しやプリンは、強火で蒸すと す（小さな穴）が立つ。弱火でゆっくり蒸す」</p>')
    A(C.owner_slot("この通説がどう言われているか・なぜ気になったか", [
        '言われる理由: 卵液が沸騰すると、中の水が泡になって穴が残る（家庭向けの説明で一致。論文では確かめていない、R-E15）',
        '対策としてよく言われること: 蓋をずらす・火を弱めて、蒸し器の中を 85〜90℃ に保つ（R-W03）',
        '計算で扱えるのは、蒸す温度ごとの「固まるまでの時間」と「中心が 90℃ を超えるまでの時間」。す ができる仕組みそのものは扱えない',
    ]))
    A('</div></section>')

    A(C.h2("calc", 2, "計算の詳しい答え"))
    A(f'<p>Exp-14 の正解のレシピ（プリン液・茶碗蒸しの卵液、器に入れて蒸す）の蒸す温度だけを変え、固まる（卵液の段階 2）までと、中心が {pT:g}℃ を超えて す が立つまでの時間を計算しました。{MAX} 分までに届かないものは「—」。</p>')
    head = "".join(f"<th>{n} 固まる</th><th>{n} す</th>" for _, n, _ in DISHES)
    A('<div class="tablewrap"><table><thead><tr><th>蒸す温度（℃）</th>' + head + '</tr></thead><tbody>'
      + "".join(f'<tr><td class="num">{T:g}</td>' + "".join(f'<td class="num">{fmt(Cm[d][T]["set"])}</td><td class="num">{fmt(Cm[d][T]["su"])}</td>' for d, *_ in DISHES) + '</tr>'
                for T in TEMPS) + '</tbody></table></div>')
    win = [(T, pu[T]["su"] - pu[T]["set"]) for T in TEMPS if pu[T]["su"] is not None and pu[T]["set"] is not None]
    A('<ul class="find">')
    A(f'<li><b>蒸す温度が {pT:g}℃ 以下なら、どれだけ蒸しても す は立たない</b>（中心が {pT:g}℃ を超えないため）。これは規則（R-E15）をそのまま言い直したもの。</li>')
    if win:
        A('<li><b>強火（蒸す温度 ' + "・".join(f"{T:g}" for T, _ in win) + '℃）でも、固まってから す が立つまでに '
          + "・".join(f"{w:.1f}" for _, w in win) + ' 分の間がある</b>（プリン）。固まったところで火から下ろせば、計算の上では す は立たない。強火は、ちょうどよく止める時間の幅を狭くする。</li>')
    same = all(Cm["custard_pudding"][T] == Cm["chawanmushi"][T] for T in TEMPS)
    if same:
        A('<li>プリンと茶碗蒸しは同じ時間になった。器の温まり方が同じ一次遅れ（器の大きさ・中身を区別しない）で、固まる・す の規則も同じ温度で決まるため。中身の違い（牛乳・砂糖とだし）は、この計算では時間に効いていない。</li>')
    A('<li class="muted small">注意: 器の中の温まり方は一次遅れ（推定）、す の規則は温度のしきい値（中心 90℃、出典は家庭向けの記事の抜粋）です。何分かの値は確かではありません。</li>')
    A('</ul></section>')

    xs = [T for T in TEMPS]
    A(C.keyfig("プリン: 蒸す温度ごとの、固まるまでと す が立つまでの時間（計算）",
               C.svg_lines([("固まる", 0, [(T, pu[T]["set"]) for T in xs if pu[T]["set"] is not None], False),
                            ("す が立つ", 2, [(T, pu[T]["su"]) for T in xs if pu[T]["su"] is not None], False)],
                           "蒸す温度（℃）", "時間（分）", (80, 100), (0, MAX)),
               f'緑（下）が固まるまで、赤が す が立つまで。{pT:g}℃ 以下では赤い線が無い（す は立たない）。強火ほど、二つの線の間（ちょうどよく止められる時間）が狭くなる。'
               + C.legend_lines([("固まるまで", 0, False), ("す が立つまで", 2, False)])))

    A(C.h2("basis", 3, "根拠"))
    A(C.basis_links(RULE_IDS, SOURCE_IDS))
    use = {"R-E15": f"中心が {pT:g}℃ 以上で す（porosity 1）、{P.V('egg_porosity_hold2_min'):g} 分保つと porosity 2（推定）",
           "R-W03": "蓋をずらす・火を弱めると蒸し器の中を 85〜90℃ に下げられる（ここでは蒸す温度を直接変えた）",
           "R-E09": "プリン液・茶碗蒸しの卵液が固まる温度（卵液の段階）"}
    H.extend(C.rules_table(RULE_IDS, use))
    H.extend(C.sources_table(SOURCE_IDS, SOURCE_CHECK, col4="この計算で使ったこと"))
    A('</section>')

    A(C.h2("verdict", 4, "判定と確かさ"))
    CAN = ([f'蒸す温度を {pT:g}℃ 以下に保てば す は立たない、は規則（R-E15）そのもの。出典は家庭向けの記事の抜粋で、論文では確かめていない。{C.conf("中")}',
            '強火（100℃ 近く）でも、固まったところで止めれば す の前に止められる。ただし止める時間の幅が狭い（計算）。' + C.conf("低"),
            '「強火だと す が立ちやすい」は、止める時間の幅が狭くなる、という意味で計算と合う。' + C.conf("中")],
           ['<b>す ができる仕組み</b>（水が泡になる・溶けていた空気が出る）。計算は温度のしきい値で、泡を解いていない。',
            '器の大きさ・卵液の量・器の材質の違い。器の中の温まり方は一次遅れ1つ（推定）。',
            '「強火」が蒸し器の中で何℃か。家庭のコンロと蒸し器で大きく違う（ここでは蒸す温度で直接比べた）。',
            '卵と水分（牛乳・だし）の割合で す の立ちやすさが変わるか。'])
    A(C.can_card(CAN[0]))
    A(C.owner_slot("結論（まとめの文章）", [
        f'プリン（計算）: 100℃ で固まるまで {fmt(pu[100]["set"])} 分、す が立つまで {fmt(pu[100]["su"])} 分／88℃（正解のレシピ）は す が立たない',
        '確かさ: す の規則は家庭向けの記事の抜粋（中）、止める時間の幅は計算（低）',
    ], note="下の実験の結果を見てから書くのでもよい"))
    A('</section>')
    A(C.h2("cannot", 5, "言えないこと") + C.cannot_card(CAN[1]) + '</section>')

    A(C.h2("try", 6, "自分で試す"))
    A('<p>同じ卵液を2つの器に分け、蒸し方だけを変えます。蒸し器の中の温度を測れる温度計があると、計算と比べられます。</p>')
    A(C.steps([
        'プリン液（卵 2 個・牛乳 250 mL・砂糖 40 g）を作り、こして同じ器 4 つに分ける。',
        'A: 蓋をずらして弱めの火（蒸し器の中 85〜90℃）で、竹串を刺して澄んだ汁が出るまで蒸す。時間を書く。',
        'B: 蓋をしっかり閉めて強火（沸騰）で、同じく澄んだ汁が出たらすぐ止める。時間を書く。',
        'C: B と同じ強火で、B の止めた時間からさらに 5 分蒸す。',
        '冷やしてから横に切り、断面の穴（す）を写真に撮る。',
    ]))
    rows = [("A 弱め（88℃）", 88), ("B 強火・すぐ止める", 100), ("C 強火・5分長く", 100)]
    pu = {**pu, 88: times("custard_pudding", 88)}
    H.extend(C.record_table(["器", "蒸し器の中の温度（℃）", "蒸した時間（分）", "断面の写真", "す（なし／少し／多い）", "計算の予言"],
                            [f'<tr><td>{e(n)}</td><td></td><td></td><td class="photo"></td><td></td><td class="pred">'
                             + (f'す なし（固まるまで {fmt(pu[T]["set"])} 分）' if i < 2 else f'す あり（{fmt(pu[T]["su"])} 分で す）') + '</td></tr>'
                             for i, (n, T) in enumerate(rows)]))
    A('</section>')

    A(C.footer('Cuisine Network。計算: Exp-14 のシミュレータ（experiments/exp-14/sim、rules.yaml の規則と採用値）。'
               'このページは experiments/myths/build.py（通説6 custard_su）が生成します。'))
    A('</div>')
    return C.reorder(C.join(H))
