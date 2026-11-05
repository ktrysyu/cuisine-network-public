"""レシピ（材料・操作・温度・時間）。13品の「正解のレシピ」と、順番・操作を変えるテストの組。

- DISH_RECIPES_TIMED: 時間で止める版（2026-09-27 の最初の版）。時間・温度は家庭の一般的な作り方の
  範囲で書いた。モデルの時定数に合わせて時間を決めた箇所は note に書いた（results/summary.md にも記録）。
- DISH_RECIPES: 正解のレシピ。状態で止めるのが自然な品は、加熱を「〜になるまで」（until）で書き直した。
  停止条件は結果を見る前に UNTIL_REWRITE に決めて固定した（変えたら UNTIL_REWRITE_CHANGES に理由を書く）。
  残りの品は時間の版と同じ。
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from . import ops
from .state import EGG_CRACKED, EGG_SHELL, State


@dataclass
class Recipe:
    name: str
    ingredients: dict[str, float]
    steps: list[tuple[str, dict]]
    T0: float | None = None
    egg_form: str | None = None
    form: str = "pot"
    note: str = ""
    expected: str | None = None
    thickness_mm: float | None = None  # Exp-18: 肉片の厚さ（meat_model = slab のときだけ使う）

    def initial(self) -> State:
        return State.from_ingredients(self.ingredients, T0=self.T0, egg_form=self.egg_form, form=self.form,
                                      thickness_mm=self.thickness_mm)

    def run(self) -> State:
        return ops.apply(self.initial(), self.steps)

    def describe(self) -> str:
        ing = " + ".join(f"{k} {v:g}g" for k, v in self.ingredients.items())
        st = " → ".join(f"{n}({', '.join(f'{k}={v}' for k, v in kw.items())})" for n, kw in self.steps)
        extra = []
        if self.T0 is not None:
            extra.append(f"初期 {self.T0}℃")
        if self.egg_form:
            extra.append(f"卵は{self.egg_form}")
        return f"[{ing}]{' (' + ', '.join(extra) + ')' if extra else ''} → {st}"


# ----------------------------------------------------------------------
# 殻付き卵の後の手順（余熱、rules.md §10 2026-09-28 夜）。判定は後の手順の終わり（食べる時点）で行う。
# 書いていない＝室温 20℃の空気に置く。長さはどれも 15分（thermoworks_egg・wiki_boiled の氷水 15分。中心の最高はその中に入る）
AFTER_MIN = 15
AFTER_REST = ("rest", {"T": 20, "time": AFTER_MIN})      # 置く（書いていないときも）
AFTER_ICE = ("plunge", {"T": 0, "time": AFTER_MIN})      # 氷水に取る
AFTER_COLD = ("plunge", {"T": 15, "time": AFTER_MIN})    # 冷水・流水に取る（水道水 15℃、推定）


# ----------------------------------------------------------------------
# 13品（＋比較用のゆで卵）の正解のレシピ（時間で止める版）
DISH_RECIPES_TIMED: dict[str, Recipe] = {
    "scrambled_eggs": Recipe(
        "スクランブルエッグ",
        {"egg_whole": 100, "milk": 20, "butter": 10, "salt": 1},
        [("whisk", {"time": 1}),
         ("bake", {"T": 110, "time": 1.75, "stirring": True, "form": "thin"})],
        expected="scrambled_eggs",
        note="弱火（110℃）で混ぜながら約1.75分。全条件を満たす窓は 1.7〜1.8分"),
    "omelet": Recipe(
        "オムレツ",
        {"egg_whole": 150, "butter": 10, "salt": 1},
        [("whisk", {"time": 1}),
         ("bake", {"T": 180, "time": 0.78, "form": "thin"})],
        expected="omelet",
        note="高温のフライパンで約47秒、混ぜずに外側を固める。1位になる時間の窓は 0.75〜0.80分"),
    "custard_pudding": Recipe(
        "プリン",
        {"egg_whole": 100, "milk": 250, "sugar": 40},
        [("whisk", {"time": 1}),
         ("steam", {"T": 88, "time": 15, "form": "cup"}),
         ("chill", {"T": 5, "time": 180})],
        expected="custard_pudding",
        note="蒸し器 85〜90℃（R-E15）で15分、冷蔵庫で3時間"),
    "chawanmushi": Recipe(
        "茶碗蒸し",
        {"egg_whole": 50, "dashi": 150, "salt": 1.2},
        [("mix", {"strength": "中", "time": 1}),
         ("steam", {"T": 88, "time": 15, "form": "cup"}),
         ("rest", {"T": 25, "time": 10})],
        expected="chawanmushi",
        note="卵:だし=1:3（R-E16）、85〜90℃で15分、器ごと10分おいて食べる"),
    "white_sauce": Recipe(
        "ホワイトソース",
        {"butter": 20, "flour": 20},
        [("bake", {"T": 120, "time": 3, "stirring": True, "form": "thin"}),
         ("mix", {"add": {"milk": 250, "salt": 1}, "strength": "弱", "time": 1}),
         ("simmer", {"T": 100, "time": 10, "stirring": True, "form": "pot"})],
        expected="white_sauce",
        note="ルーを色づけずに炒め（130℃未満、R-S09）、牛乳でのばして沸騰後10分"),
    "caramel_sauce": Recipe(
        "カラメル",
        {"sugar": 100, "water": 30},
        [("bake", {"T": 190, "time": 10, "stirring": True, "form": "thin"}),
         ("mix", {"add": {"water": 20}, "time": 0.5})],
        expected="caramel_sauce",
        note="鍋をゆすりながら煮詰め、褐色になったら湯を加えて止める。1位で全条件を満たす窓は 9.5〜10.5分（蒸発の推定値に依存）"),
    "sauteed_onion": Recipe(
        "炒め玉ねぎ",
        {"onion": 200, "vegetable_oil": 10},
        [("bake", {"T": 170, "time": 40, "form": "thin"})],
        expected="sauteed_onion",
        note="中火で40分（ときどき混ぜる＝撹拌し続けない）"),
    "steamed_rice": Recipe(
        "ご飯",
        {"rice": 150, "water": 210},
        [("soak", {"T": 25, "time": 30}),
         ("simmer", {"T": 100, "time": 35, "lid": True, "form": "pot"}),
         ("rest", {"T": 90, "time": 10})],
        expected="steamed_rice",
        note="加水 1.4倍（R-S05）、浸漬30分（R-S06）、炊飯35分（温度上昇10＋沸騰5＋蒸し煮15＋余裕、R-S04）、蒸らし10分"),
    "pancake": Recipe(
        "パンケーキ",
        {"flour": 100, "egg_whole": 50, "milk": 100, "sugar": 20, "baking_powder": 4, "butter": 10},
        [("mix", {"strength": "弱", "time": 1}),
         ("rest", {"T": 20, "time": 10}),
         ("bake", {"T": 190, "time": 3, "form": "thin"}),
         ("bake", {"T": 190, "time": 3, "form": "thin"})],
        expected="pancake",
        note="さっくり混ぜ、10分寝かせ、鉄板 190℃（R-L03）で片面3分ずつ"),
    "milk_jelly": Recipe(
        "牛乳ゼリー",
        {"gelatin": 5, "water": 25},
        [("soak", {"T": 15, "time": 30}),
         ("mix", {"add": {"milk": 200, "sugar": 20}, "time": 1}),
         ("heat", {"medium": "water", "T": 60, "time": 10, "stirring": True, "form": "pot"}),
         ("chill", {"T": 5, "time": 180})],
        expected="milk_jelly",
        note="ゼラチンを膨潤（R-J01）、牛乳を湯煎で 60℃まで温めて溶かし（R-J02）、冷蔵3時間"),
    "whipped_cream": Recipe(
        "ホイップクリーム",
        {"heavy_cream": 200, "sugar": 15},
        [("whisk", {"time": 3, "T": 10})],
        T0=8,
        expected="whipped_cream",
        note="生クリームを品温 7.5〜12.5℃（R-D03 の推奨）に保って3分泡立てる"),
    "onsen_tamago": Recipe(
        "温泉卵",
        {"egg_whole": 60},
        [("simmer", {"T": 68, "time": 30, "form": "shell"}), AFTER_REST],
        egg_form=EGG_SHELL,
        expected="onsen_tamago",
        note="68℃の湯に殻ごと30分（R-E08）。後の手順は書かれていないので室温に15分置く（余熱、rules.md §10）"),
    "sauteed_chicken": Recipe(
        "鶏むね肉のソテー",
        {"chicken": 200, "vegetable_oil": 10, "salt": 2},
        [("bake", {"T": 180, "time": 5, "form": "piece"}),
         ("bake", {"T": 180, "time": 5, "form": "piece"})],
        expected="sauteed_chicken",
        note="フライパン 180℃で片面5分ずつ"),
    "hard_boiled_egg": Recipe(
        "ゆで卵",
        {"egg_whole": 60},
        [("simmer", {"T": 100, "time": 12, "form": "shell"}), AFTER_REST],
        egg_form=EGG_SHELL,
        expected="hard_boiled_egg",
        note="沸騰した湯で12分（比較用に追加した品）。後の手順は書かれていないので室温に15分置く（余熱、rules.md §10）"),
    # 2026-09-28 追加（修正 B の後。rules.md §10）。出典の手順をそのまま使った（Exp-15 R007 料理本「沸騰した湯に入れ 6〜7分」の中央。
    # wiki_boiled は 3分・5〜6分）
    "soft_boiled_egg": Recipe(
        "半熟ゆで卵",
        {"egg_whole": 60},
        [("simmer", {"T": 100, "time": 6.5, "form": "shell"}), AFTER_COLD],
        egg_form=EGG_SHELL,
        expected="soft_boiled_egg",
        note="沸騰した湯に殻ごと6.5分（Exp-15 R007 の 6〜7分の中央）。R007 の「冷水に移す」で冷水 15℃に15分（余熱、rules.md §10）"),
    # 2026-09-27 追加（14品目）。計算する前に書いた。出典の手順をそのまま使った（soc_poach「The egg is cooked at
    # 80C for 4 minutes」）。酢・塩は入れない（出典で分かれる、C14）
    "poached_egg": Recipe(
        "ポーチドエッグ",
        {"egg_whole": 60},
        [("poach", {"T": 80, "time": 4})],
        egg_form=EGG_CRACKED,
        expected="poached_egg",
        note="割った卵を 80℃の湯に落として4分（soc_poach）。酢・塩なし"),
    # 2026-10-22 追加（Exp-20、計算する前に書いた。experiments/exp-20-more-dishes-sim/plan.md）
    "steamed_egg": Recipe(
        "蒸し卵",
        {"egg_whole": 60},
        [("steam", {"T": 100, "time": 12.5, "form": "shell"}), AFTER_ICE],
        egg_form=EGG_SHELL,
        expected="hard_boiled_egg",
        note="wikibooks_hard_eggs の蒸す方法（蓋をして 12〜13 分の中央、氷水で冷やす）。状態は固ゆで卵と区別できないので、答えは ゆで卵（固ゆで）"),
    "dashimaki": Recipe(
        "だし巻き卵",
        {"egg_whole": 200, "dashi": 150, "salt": 2, "sugar": 9, "vegetable_oil": 4},
        [("whisk", {"time": 1}),
         ("bake", {"T": 175, "time": 1.5, "form": "thin"})],
        expected="dashimaki",
        note="maff_dashimaki（卵 4 個・だし 150 mL、薄口醤油→食塩 2 g、砂糖とみりん風調味料→砂糖 9 g、推定）。中火 175℃（P-MED、弱い根拠）。時間の版の 1.5 分は推定（出典に時間が無い）"),
    "custard_cream": Recipe(
        "カスタードクリーム",
        {"egg_yolk": 90, "sugar": 200},
        [("whisk", {"time": 2}),
         ("mix", {"add": {"flour": 80}, "strength": "弱", "time": 0.5}),
         ("mix", {"add": {"milk": 495}, "T_add": 100, "strength": "中", "time": 0.5}),
         ("simmer", {"T": 100, "time": 6, "stirring": True, "form": "pot"}),
         ("mix", {"add": {"butter": 14}, "strength": "弱", "time": 0.5})],
        expected="custard_cream",
        note="wikibooks_creme_pat（分量の換算は推定: 砂糖 200 g・薄力粉 80 g・牛乳 495 g・卵黄 18 g×5）。時間の版の 6 分（沸騰まで＋2.5 分）は推定"),
}


# ----------------------------------------------------------------------
# 状態で止める版（2026-09-27）。停止条件は結果を見る前に決めた。時間の探索はしていない。
# 上限時間（max_time）は時間の版のおおよそ3倍以上に置いた（上限で止まったら未到達として記録される）。
UNTIL_REWRITE: dict[str, tuple[list[tuple[str, dict]], str]] = {
    # 2026-10-22（Exp-20、計算する前に決めた）
    "dashimaki": (
        [("whisk", {"time": 1}),
         ("bake", {"T": 175, "form": "thin", "until": {"var": "egg_gel_stage", "ge": 2}, "max_time": 10})],
        "中火 175℃で混ぜずに、卵液が固まる（egg_gel_stage 2。周りが固まってきたら巻く）まで（maff_dashimaki）"),
    "custard_cream": (
        [("whisk", {"time": 2}),
         ("mix", {"add": {"flour": 80}, "strength": "弱", "time": 0.5}),
         ("mix", {"add": {"milk": 495}, "T_add": 100, "strength": "中", "time": 0.5}),
         ("simmer", {"T": 100, "stirring": True, "form": "pot", "until": {"var": "T_core", "ge": 99.5}, "max_time": 20}),
         ("simmer", {"T": 100, "time": 2.5, "stirring": True, "form": "pot"}),
         ("mix", {"add": {"butter": 14}, "strength": "弱", "time": 0.5})],
        "混ぜながら沸騰（中心 99.5℃）するまで煮て、さらに 2.5 分（wikibooks_creme_pat の 2〜3 分の中央）。バターを混ぜる"),
    "scrambled_eggs": (
        [("whisk", {"time": 1}),
         ("bake", {"T": 110, "stirring": True, "form": "thin",
                   "until": {"var": "egg_gel_stage", "ge": 2}, "max_time": 10})],
        "弱火で混ぜながら、卵液がやわらかく固まる（egg_gel_stage 2）まで。「固まりかけたら火から下ろす」"),
    "omelet": (
        [("whisk", {"time": 1}),
         ("bake", {"T": 180, "form": "thin",
                   "until": {"var": "egg_gel_stage", "ge": 1}, "max_time": 5})],
        "高温で混ぜずに、内側にとろみが出る（egg_gel_stage 1）まで。「中が半熟のうちに火から下ろす」"),
    "caramel_sauce": (
        [("bake", {"T": 190, "stirring": True, "form": "thin",
                   "until": {"var": "caramel", "ge": 2}, "max_time": 30}),
         ("mix", {"add": {"water": 20}, "time": 0.5})],
        "鍋をゆすりながら、褐色（caramel 2）になるまで煮詰め、湯を加えて止める"),
    "custard_pudding": (
        [("whisk", {"time": 1}),
         ("steam", {"T": 88, "form": "cup",
                    "until": {"var": "egg_gel_stage", "ge": 2}, "max_time": 40}),
         ("chill", {"T": 5, "time": 180})],
        "蒸し器 88℃で、卵液が固まる（egg_gel_stage 2。竹串で澄んだ汁が出る）まで。冷蔵庫で3時間"),
    "chawanmushi": (
        [("mix", {"strength": "中", "time": 1}),
         ("steam", {"T": 88, "form": "cup",
                    "until": {"var": "egg_gel_stage", "ge": 2}, "max_time": 40}),
         ("rest", {"T": 25, "time": 10})],
        "88℃で、卵液が固まる（egg_gel_stage 2。竹串で澄んだ汁が出る）まで。器ごと10分おく"),
    "sauteed_onion": (
        [("bake", {"T": 170, "form": "thin",
                   "until": {"var": "maillard", "ge": 2}, "max_time": 120})],
        "中火で、色づく（maillard 2＝きつね色。料理の条件は 2〜3）まで"),
    "sauteed_chicken": (
        [("bake", {"T": 180, "form": "piece",
                   "until": {"var": "maillard", "ge": 2}, "max_time": 15}),
         ("bake", {"T": 180, "form": "piece",
                   "until": {"var": "T_core", "ge": 74}, "max_time": 20})],
        "片面を焼き色（maillard 2）がつくまで、返して中心温度が 74℃（R-P05）に達するまで"),
    "milk_jelly": (
        [("soak", {"T": 15, "time": 30}),
         ("mix", {"add": {"milk": 200, "sugar": 20}, "time": 1}),
         ("heat", {"medium": "water", "T": 60, "stirring": True, "form": "pot",
                   "until": {"var": "gelatin_state", "in": ["溶解（ゾル）"]}, "max_time": 30}),
         ("chill", {"T": 5, "time": 180})],
        "膨潤させたゼラチンと牛乳を湯煎で、ゼラチンが溶ける（gelatin_state ゾル）まで温め、冷蔵3時間"),
}

# 時間のまま残した品と理由（結果を見る前に決めた）
UNTIL_KEPT_TIMED: dict[str, str] = {
    "white_sauce": "牛乳でのばしたあと「沸騰してから数分煮る」は時間で書く手順。とろみ（starch_gel）は沸騰の前に付くので止める合図にならない",
    "steamed_rice": "炊飯は加水・浸漬・加熱・蒸らしの時間で決める手順（R-S04 も時間で書かれている）",
    "pancake": "「焼き色がつくまで」は片面ごとの状態だが、State は表面を1つしか持たない（返した後の面を区別できない）",
    "whipped_cream": "泡立ては加熱の操作ではない（今回の until は加熱だけ）",
    "onsen_tamago": "湯温と時間で定義される料理（R-E08）。殻の中の状態は見えない",
    "hard_boiled_egg": "同上（沸騰した湯で何分）",
    "soft_boiled_egg": "同上（沸騰した湯で何分）。2026-09-28 追加",
    "poached_egg": "湯温と時間で書かれる手順（R-E21: 80℃で4分）。卵黄の状態は外から見えない",
    "steamed_egg": "蒸す時間で書かれる手順（12〜13分）。2026-10-22",
}

# 停止条件を後から変えた記録（変えていなければ空）
UNTIL_REWRITE_CHANGES: dict[str, str] = {}

DISH_RECIPES: dict[str, Recipe] = {
    k: (replace(r, steps=UNTIL_REWRITE[k][0], note=UNTIL_REWRITE[k][1]) if k in UNTIL_REWRITE else r)
    for k, r in DISH_RECIPES_TIMED.items()
}

# 13品（本人が感じ方を採点した品）。ゆで卵（比較用）・ポーチドエッグ（14品目、2026-09-27）・半熟ゆで卵（2026-09-28）は含めない
# 地図の元のレシピのうち、正解のレシピに無いもの（sim/maps.py の base "map:<key>"）
MAP_BASE_RECIPES: dict[str, Recipe] = {
    "shell_egg_ice": Recipe(
        "殻付き卵を湯に入れ、氷水に取る", {"egg_whole": 60},
        [("simmer", {"T": 68, "time": 30, "form": "shell"}), AFTER_ICE],
        egg_form=EGG_SHELL, expected="onsen_tamago", note="温泉卵の元のレシピの後の手順を氷水 0℃に15分にしたもの（余熱、2026-09-28 夜）"),
}

EXTRA = ("hard_boiled_egg", "poached_egg", "soft_boiled_egg", "steamed_egg", "dashimaki", "custard_cream")
THIRTEEN = [k for k in DISH_RECIPES if k not in EXTRA]


# ----------------------------------------------------------------------
# Exp-18（2026-10-22）: 本人が採点した追加3品の正解のレシピ。計算する前に書いた。
# DISH_RECIPES には入れない（既存のテスト・試せるページの対象を変えないため）。
# 肉片は meat_model = slab、揚げ物は oil_uptake = on で計算する前提（Exp-18 の run_eval.py が切り替える）。
STEAK_REST = ("rest", {"T": 20, "time": 4})   # aussiebeef_steak「3〜5分休ませる」の中央
POTATO_DRY = ("bake", {"T": 130, "time": 2, "stirring": True, "form": "piece"})  # wikibooks_boiled_potato「ごく弱火で水気を飛ばす」。弱火 130℃（Exp-15 P-LOW、出典なし）・2分は推定

EXP18_RECIPES_TIMED: dict[str, Recipe] = {
    "beef_steak": Recipe(
        "ビーフステーキ（ミディアム）",
        {"beef": 250, "vegetable_oil": 5},
        [("bake", {"T": 175, "time": 1.5, "form": "piece"}),
         ("bake", {"T": 175, "time": 1.5, "form": "piece"}),
         ("bake", {"T": 175, "time": 1.5, "form": "piece"}),
         ("bake", {"T": 175, "time": 1.5, "form": "piece"}),
         ("bake", {"T": 175, "time": 0.75, "form": "piece"}),
         STEAK_REST],
        T0=20, thickness_mm=20,
        expected="beef_steak",
        note="tokyogas_steak: 厚さ約2cm・250g・室温に戻す・中火で 90秒ごとに返して 6分30秒〜7分（中央 6.75分）。中火 175℃（Exp-15 P-MED、弱い根拠）。3〜5分休ませる（aussiebeef_steak）の中央 4分"),
    "french_fries": Recipe(
        "フライドポテト",
        {"potato": 100},
        [("simmer", {"T": 100, "time": 15, "form": "thin"}),
         ("deep_fry", {"T": 175, "time": 4.5, "form": "thin"})],
        expected="french_fries",
        note="wikibooks_fries: 水で約15分下ゆで（沸騰 100℃とした、推定）→175℃の油で 4〜5分（中央 4.5分）。細い棒状なので form thin"),
    "boiled_potato": Recipe(
        "ゆでじゃがいも（粉ふきいも）",
        {"potato": 150},
        [("simmer", {"T": 100, "time": 17.5, "form": "piece"}), POTATO_DRY],
        expected="boiled_potato",
        note="wikibooks_boiled_potato: 中くらいのいもで 15〜20分（中央 17.5分）→湯を捨てて弱火で水気を飛ばす"),
}

EXP18_UNTIL: dict[str, tuple[list[tuple[str, dict]], str]] = {
    "beef_steak": (
        [("bake", {"T": 175, "form": "piece", "until": {"var": "maillard", "ge": 2}, "max_time": 15}),
         ("bake", {"T": 175, "form": "piece", "until": {"var": "T_core", "ge": 55}, "max_time": 20}),
         STEAK_REST],
        "中火で片面を焼き色（maillard 2）がつくまで、返して中心が 55℃（tokyogas_steak・aussiebeef_steak）に達するまで。4分休ませる"),
    "boiled_potato": (
        [("simmer", {"T": 100, "form": "piece", "until": {"var": "cell_wall", "in": ["軟化"]}, "max_time": 60}),
         POTATO_DRY],
        "串がすっと通る（cell_wall 軟化）まで煮て、弱火で水気を飛ばす"),
}
EXP18_KEPT_TIMED = {"french_fries": "「4〜5分 until light golden」の light golden は焼き色の段階1と2の間で、1つの段階に置けない。時間で書く"}

EXP18_RECIPES: dict[str, Recipe] = {
    k: (replace(r, steps=EXP18_UNTIL[k][0], note=EXP18_UNTIL[k][1]) if k in EXP18_UNTIL else r)
    for k, r in EXP18_RECIPES_TIMED.items()
}


# ----------------------------------------------------------------------
# 順番・操作を変えると別の料理になる組
@dataclass
class Pair:
    title: str
    a: Recipe
    b: Recipe
    what_changed: str = ""


PAIRS: list[Pair] = [
    Pair("撹拌→フライパン vs 撹拌→蒸す（依頼の2例）",
         Recipe("(卵+牛乳)→撹拌→加熱(フライパン,短時間)",
                {"egg_whole": 100, "milk": 20},
                [("whisk", {"time": 1}),
                 ("bake", {"T": 110, "time": 1.75, "stirring": True, "form": "thin"})],
                expected="scrambled_eggs"),
         Recipe("(卵+牛乳+砂糖)→撹拌→蒸す(88℃)",
                {"egg_whole": 100, "milk": 250, "sugar": 40},
                [("whisk", {"time": 1}),
                 ("steam", {"T": 88, "time": 15, "form": "cup"})],
                expected="custard_pudding"),
         "加熱の媒体と撹拌（材料は砂糖と牛乳の量が違う。依頼どおり）"),
    Pair("同じ材料で 撹拌→フライパン vs 撹拌→蒸す",
         Recipe("(卵+牛乳+砂糖)→撹拌→フライパンで混ぜながら",
                {"egg_whole": 100, "milk": 20, "sugar": 10},
                [("whisk", {"time": 1}),
                 ("bake", {"T": 110, "time": 1.75, "stirring": True, "form": "thin"})],
                expected="scrambled_eggs"),
         Recipe("(卵+牛乳+砂糖)→撹拌→蒸す(88℃)→冷やす",
                {"egg_whole": 100, "milk": 20, "sugar": 10},
                [("whisk", {"time": 1}),
                 ("steam", {"T": 88, "time": 15, "form": "cup"}),
                 ("chill", {"T": 5, "time": 180})],
                expected="custard_pudding"),
         "材料は同じ。操作だけ変える"),
    Pair("同じ材料で加熱温度だけ変える（温泉卵 vs ゆで卵）",
         Recipe("殻付き卵を68℃の湯で30分",
                {"egg_whole": 60}, [("simmer", {"T": 68, "time": 30, "form": "shell"}), AFTER_REST],
                egg_form=EGG_SHELL, expected="onsen_tamago"),
         Recipe("殻付き卵を100℃の湯で30分",
                {"egg_whole": 60}, [("simmer", {"T": 100, "time": 30, "form": "shell"}), AFTER_REST],
                egg_form=EGG_SHELL, expected="hard_boiled_egg"),
         "湯の温度だけ"),
    Pair("同じ材料で加熱温度だけ変える（プリン vs す立ち）",
         Recipe("プリン液を88℃で蒸す",
                {"egg_whole": 100, "milk": 250, "sugar": 40},
                [("whisk", {"time": 1}), ("steam", {"T": 88, "time": 15, "form": "cup"}),
                 ("chill", {"T": 5, "time": 180})],
                expected="custard_pudding"),
         Recipe("プリン液を100℃で蒸す",
                {"egg_whole": 100, "milk": 250, "sugar": 40},
                [("whisk", {"time": 1}), ("steam", {"T": 100, "time": 15, "form": "cup"}),
                 ("chill", {"T": 5, "time": 180})],
                expected=None),
         "蒸し器の温度だけ。100℃では す が立つ（R-E15）"),
    Pair("撹拌の有無だけ変える（スクランブルエッグ vs オムレツ）",
         Recipe("溶き卵をフライパンで混ぜながら",
                {"egg_whole": 150, "butter": 10, "salt": 1},
                [("whisk", {"time": 1}), ("bake", {"T": 110, "time": 1.75, "stirring": True, "form": "thin"})],
                expected="scrambled_eggs"),
         Recipe("溶き卵をフライパンで混ぜずに",
                {"egg_whole": 150, "butter": 10, "salt": 1},
                [("whisk", {"time": 1}), ("bake", {"T": 110, "time": 1.75, "form": "thin"})],
                expected="omelet"),
         "加熱中の撹拌だけ（R-E20）"),
    Pair("順番を入れ替える（温める→冷やす vs 冷やす→温める）",
         Recipe("ゼラチン膨潤→牛乳→温める→冷やす",
                {"gelatin": 5, "water": 25},
                [("soak", {"T": 15, "time": 30}), ("mix", {"add": {"milk": 200, "sugar": 20}, "time": 1}),
                 ("heat", {"medium": "water", "T": 60, "time": 10, "stirring": True, "form": "pot"}),
                 ("chill", {"T": 5, "time": 180})],
                expected="milk_jelly"),
         Recipe("ゼラチン膨潤→牛乳→冷やす→温める",
                {"gelatin": 5, "water": 25},
                [("soak", {"T": 15, "time": 30}), ("mix", {"add": {"milk": 200, "sugar": 20}, "time": 1}),
                 ("chill", {"T": 5, "time": 180}),
                 ("heat", {"medium": "water", "T": 60, "time": 10, "stirring": True, "form": "pot"})],
                expected=None),
         "冷やす と 温める の順番だけ"),
    Pair("順番を入れ替える（冷やす→泡立てる vs 泡立てる→冷やす）",
         Recipe("生クリームを冷やしてから泡立てる",
                {"heavy_cream": 200, "sugar": 15},
                [("chill", {"T": 5, "time": 60}), ("whisk", {"time": 3, "T": 10})],
                T0=20, expected="whipped_cream"),
         Recipe("生クリームを室温で泡立ててから冷やす",
                {"heavy_cream": 200, "sugar": 15},
                [("whisk", {"time": 3, "T": 20}), ("chill", {"T": 5, "time": 60})],
                T0=20, expected=None),
         "冷やす と 泡立てる の順番だけ（R-D03）"),
]
