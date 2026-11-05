"""Exp-15: 世の中のレシピ（機械的な収集が許された出典だけ）から、卵料理の温度・時間を読み取った表を作る。

    uv run python experiments/exp-15-recipes/build.py

- 読み取りは人（Claude）が原文を読んで RECORDS に手で書いた。このスクリプトは
  1) 出典（ダンプ・CSV）から該当ページの版番号・本文を取り出し、
  2) 各行の引用 quote が原文にそのまま在ることを確かめ（無ければ止まる）、
  3) あいまいな表現を extraction_rules.md の換算表（RULES）で温度に直し、
  4) recipes.csv と summary.md を書き出す。
- 生データは data/raw/ にある（git に入れない。取得元とハッシュは data/SOURCES.md）。
- 推定した値は *_est_* の列に入れ、T_is_estimate で区別する。原文の数値は T_stated_c に入れる。
"""
from __future__ import annotations

import bz2
import csv
import json
import re
import statistics
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote as urlquote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / "data" / "raw"
WB = RAW / "wikibooks_cookbook"
EN_DUMP = WB / "enwikibooks-20260901-pages-articles.xml.bz2"
JA_DUMP = WB / "jawikibooks-20260901-pages-articles.xml.bz2"
HF_JSON = WB / "recipes_parsed.mini.json"
FUKUI = RAW / "fukui_opendata"
RETRIEVED = "2026-09-28"

LICENSE = {
    "wb_en": "CC BY-SA 4.0（Wikibooks。ページのフッター表示で確認）",
    "wb_ja": "CC BY-SA 4.0（ウィキブックス。ページのフッター表示で確認）",
    "wb_hf": "CC BY-SA 4.0（Hugging Face gossminn/wikibooks-cookbook のライセンス表示。元は Wikibooks）",
    "fukui": "CC BY 4.0（福井県オープンデータライブラリ利用規約）",
}
SOURCE_NAME = {
    "wb_en": "Wikibooks Cookbook（英語版）公式ダンプ enwikibooks-20260901",
    "wb_ja": "ウィキブックス 料理本（日本語版）公式ダンプ jawikibooks-20260901",
    "wb_hf": "Wikibooks Cookbook（英語版）Hugging Face gossminn/wikibooks-cookbook（2024-07-31 取得のスナップショット、rev 49fb73ea）",
    "fukui": "福井県オープンデータライブラリ",
}
FUKUI_DATASET = {
    "nanetukomekko.csv": ("南越米っ子コンクール応援作品レシピ（丹南農林総合事務所）",
                          "https://www.pref.fukui.lg.jp/doc/dx-suishin/opendata/list_6_d/fil/nanetukomekko.csv"),
    "fukuinobi_recipe.csv": ("「ふくい健幸美食」のレシピ（保健予防課）",
                             "https://www.pref.fukui.lg.jp/doc/dx-suishin/opendata/list_6_d/fil/fukuinobi_recipe.csv"),
    "fukuiasagohan.csv": ("ふくい朝ごはんレシピ（流通販売課）",
                          "https://www.pref.fukui.lg.jp/doc/dx-suishin/opendata/list_6_d/fil/fukuiasagohan.csv"),
}

# ----------------------------------------------------------------------
# 換算表（extraction_rules.md の §2 と同じ。id を md 側にも書き、run 時に突き合わせる）
# (推定の中心, 下限, 上限, 根拠の短い説明)
RULES: dict[str, tuple[float | None, float | None, float | None, str]] = {
    # 湯・蒸気
    "W-BOIL": (100, 95, 100, "沸騰は 95〜100℃（Wikibooks Cookbook:Boiling、標高・気圧で変わる）。海抜0m付近として 100"),
    "W-SIMMER": (90, 85, 95, "simmer は 85〜95℃（Wikibooks Cookbook:Simmering）"),
    "W-GENTLE": (85, 75, 90, "gentle / very gentle simmer・「沸騰させない」。Poaching の定義（71〜82℃）と Simmering（85〜95℃）の間として推定"),
    "W-POACH": (77, 71, 82, "poaching は 160〜180°F（Wikibooks Cookbook:Poaching。ページの℃表記 75〜80 は換算がずれており、°F から直すと 71〜82℃）"),
    "W-BOIL-POACH": (100, 75, 100, "沸騰した湯に落とすと書くが「poach」とも書き、火を弱める指示が無い。書かれたとおり 100 とし、下限は poaching の定義まで広げる"),
    "W-RESID": (None, None, 100, "火を止めた湯・注いだ熱湯の余熱。100℃から下がり続けるので一定温度として書けない（推定しない）"),
    "W-UNSPEC": (100, 95, 100, "「茹でる」「boil」とだけあり湯温の指示が無い。沸騰した湯と読む（推定）"),
    "S-STEAM": (100, 95, 100, "沸騰した湯の上で蓋をして蒸す。蒸気は 100℃（W-BOIL と同じ根拠）"),
    "S-LOW": (88, 80, 95, "蒸し器を弱火で。Exp-14 R-E15（蒸し器内 85〜90℃に保つ、抜粋のみ・確かさ中）を弱火の狙いとみなした推定。実際の庫内温度は書かれていない"),
    "S-BAIN-STOVE": (None, None, 100, "鍋の湯煎（bain-marie）を simmer。容器の外の湯は 85〜95℃だが、中の卵液が受ける温度は書けない（推定しない）"),
    "O-BATH": (None, None, 100, "オーブンの湯煎。オーブン温度は原文の数値（T_stated_c）。卵液が受けるのは湯の温度（100℃以下）で、何℃かは書かれていない"),
    "O-DRY": (None, None, None, "オーブン（湯煎なし）。オーブン温度は原文の数値。卵液の表面・中心の温度は書かれていない"),
    # フライパン（家庭のコンロと鍋で大きく変わる。どれも推定）
    "P-LOW": (130, 100, 150, "弱火。出典なしの推定（中火 P-MED より下）"),
    "P-MEDLOW": (150, 130, 170, "中弱火。Wikibooks Pupusas の low-medium heat（325–350°F＝163〜177℃、鉄板）を上限側の目安にした推定"),
    "P-MED": (175, 150, 190, "中火。Wikibooks 内の用例 medium heat ≈ 175〜180℃（Koesisters の油 180℃、Choripán のグリル 350°F、Nigerian Egg Roll の油 350–375°F）。フライパンの鍋肌の温度としては推定"),
    "P-MEDHIGH": (200, 185, 220, "中強火。Wikibooks Sesame Shrimp Toast の medium-high で油 375°F（190℃）を下限側の目安にした推定"),
    "P-HIGH": (230, 210, 260, "強火。出典なしの推定"),
    "P-HOT": (200, 170, 240, "「熱したフライパン」とだけあり火力の指示が無い。推定"),
    "MW": (None, None, None, "電子レンジ。媒体の温度として書けない"),
    "NONE": (None, None, None, "温度・火力の記述が無い"),
}
EGG_T0_RULES = {
    "E-FRIDGE": (5, 2, 8, "冷蔵庫から出したて。家庭用冷蔵室 2〜8℃の推定"),
    "E-ROOM": (20, 15, 25, "常温に戻す・室温。15〜25℃の推定"),
    "E-NONE": (None, None, None, "記述なし"),
}
VINEGAR_RULE = "V-TBSP-L: 大さじ1（15 ml）/ 水1 L ＝ 1.5%。量の書かれていない a dash / a splash / 少々 は割合を出さない"

SIM_DISH = {  # Exp-14 の料理 id（無いものは新設。地図に重ねるときの突き合わせ用）
    "onsen_tamago": "温泉卵", "soft_boiled_egg": "半熟ゆで卵（Exp-14 に無い）", "hard_boiled_egg": "固ゆで卵",
    "poached_egg": "ポーチドエッグ", "scrambled_eggs": "スクランブルエッグ", "custard_pudding": "プリン",
    "chawanmushi": "茶碗蒸し",
}

# ----------------------------------------------------------------------
# 手で読み取った行。1 行 = 1 つの手順（同じページの別の方法・別の硬さは別の行、group で束ねる）
# 共通のキー:
#   src, page, dish, variant, dish_basis, method, egg_form(shell/cracked/beaten/custard_mix), medium,
#   start(hot/cold/preheated/-), T_raw, T_stated_c, T_phrase, rule, time_raw, t_lo, t_hi, time_counts,
#   doneness, egg_T0_raw, egg_T0_rule, vinegar, vinegar_raw, vinegar_pct, salt, salt_raw, tech, quote, group, notes
R = []



# 殻付き卵の後の手順（余熱、Exp-14 rules.md §10 2026-09-28 夜）。techniques（原文から読んだ手順）の言葉で機械的に決める。
# ice: 氷水に取る / cold: 冷水・流水・水に取る / none: 書いていない（Exp-14 では「室温に置く」とみなす）。殻付き卵以外は空
AFTER_WORDS = [("ice", ("氷水",)), ("cold", ("冷水", "流水", "水で粗熱"))]


def after_step(r: dict) -> tuple[str, str]:
    if r["egg_form"] != "shell":
        return "", ""
    tech = r.get("tech", "")
    for kind, words in AFTER_WORDS:
        for wd in words:
            if wd in tech:
                return kind, f"techniques に「{wd}」"
    return "none", "techniques に冷やす手順なし"

def rec(**kw):
    R.append(kw)


# ---------------- 温泉卵 ----------------
rec(src="wb_en", page="Cookbook:Gyudon (Japanese Beef and Rice Bowl)", dish="onsen_tamago",
    variant="余熱（熱湯に浸けて置く）", dish_basis="推定: 原文は料理名を書かず soft inside and not hard の卵を牛丼にのせる。日本の牛丼の温泉卵とみなした",
    method="-", egg_form="shell", medium="water", start="hot",
    T_raw="boiling water（注いだ後の火の有無は書かれていない）", T_phrase="Cover the eggs in boiling water, and let them sit", rule="W-RESID",
    time_raw="20 minutes", t_lo=20, t_hi=20, time_counts="熱湯に浸けてからの放置時間",
    doneness="so they are soft inside and not hard", egg_T0_raw="", egg_T0_rule="E-NONE",
    vinegar="no", salt="no", tech="殻をむいてのせる",
    quote="Cover the eggs in boiling water, and let them sit for 20 minutes so they are soft inside and not hard.",
    group="G-gyudon", notes="火を止めるかどうか・湯量が書かれておらず、温度の履歴は決まらない")

# ---------------- 半熟ゆで卵 ----------------
rec(src="wb_en", page="Cookbook:Soft Boiled Eggs", dish="soft_boiled_egg", variant="runny〜soft yolk",
    dish_basis="ページ名 Soft Boiled Eggs", method="Method 1（沸騰を続ける）", egg_form="shell", medium="water", start="hot",
    T_raw="boil", T_phrase="Bring a saucepan of water to a boil ... boil for 4–6 minutes", rule="W-BOIL",
    time_raw="4–6 minutes (4 minutes for runny yolk, 5 minutes for soft yolk)", t_lo=4, t_hi=6, time_counts="卵を入れてから",
    doneness="4 分で黄身が流れる・5 分で柔らかい", egg_T0_raw="", egg_T0_rule="E-NONE",
    vinegar="no", salt="optional", salt_raw="Salt (optional)（湯に少し。割れたとき白身を早く固める）", tech="",
    quote="Gently add the eggs, and boil for 4–6 minutes (4 minutes for runny yolk, 5 minutes for soft yolk).",
    group="G-softboiled", notes="")
rec(src="wb_en", page="Cookbook:Soft Boiled Eggs", dish="soft_boiled_egg", variant="",
    dish_basis="ページ名 Soft Boiled Eggs", method="Method 2（1分沸騰→火を止めて5分）", egg_form="shell", medium="water", start="hot",
    T_raw="boil 1 minute, then remove from heat", T_phrase="boil for 1 minute. Remove the saucepan from the heat", rule="W-RESID",
    time_raw="1 minute + 5 minutes", t_lo=6, t_hi=6, time_counts="1 分沸騰＋5 分余熱の合計",
    doneness="", egg_T0_raw="", egg_T0_rule="E-NONE", vinegar="no", salt="optional", salt_raw="Salt (optional)", tech="",
    quote="Remove the saucepan from the heat, and allow eggs to stand in the hot water for 5 minutes.",
    group="G-softboiled", notes="前半 1 分は W-BOIL（100℃）、後半は余熱")
rec(src="wb_en", page="Cookbook:Soft Boiled Eggs", dish="soft_boiled_egg", variant="",
    dish_basis="ページ名 Soft Boiled Eggs", method="Method 3（沸騰した湯に入れてすぐ火を止め蓋）", egg_form="shell", medium="water", start="hot",
    T_raw="rolling boil, then immediately remove the pan from heat and cover", T_phrase="immediately remove the pan from heat and cover it", rule="W-RESID",
    time_raw="8 minutes", t_lo=8, t_hi=8, time_counts="卵を入れてから（余熱のみ）",
    doneness="", egg_T0_raw="", egg_T0_rule="E-NONE", vinegar="no", salt="optional", salt_raw="Salt (optional)", tech="蓋",
    quote="Let the eggs sit for 8 minutes, then remove them.", group="G-softboiled", notes="")
rec(src="wb_en", page="Cookbook:Soft Boiled Eggs", dish="soft_boiled_egg", variant="",
    dish_basis="ページ名 Soft Boiled Eggs", method="Method 4（少量の湯で蒸す）", egg_form="shell", medium="steam", start="hot",
    T_raw="about 1 inch (2.5 cm) of water to a rolling boil, cover, boil/steam", T_phrase="Let boil/steam", rule="S-STEAM",
    time_raw="6–6½ minutes", t_lo=6, t_hi=6.5, time_counts="卵を入れて蓋をしてから",
    doneness="depending on how runny you want the yolks", egg_T0_raw="", egg_T0_rule="E-NONE",
    vinegar="no", salt="optional", salt_raw="Salt (optional)", tech="湯は 1 inch（2.5 cm）だけ・蓋",
    quote="Let boil/steam for 6–6½ minutes, depending on how runny you want the yolks.", group="G-softboiled",
    notes="湯に一部つかる。蒸気と湯の混ざった加熱")
rec(src="wb_en", page="Cookbook:Tonkotsu Ramen", dish="soft_boiled_egg", variant="jammy（ラーメンの味付け卵）",
    dish_basis="原文 7 minutes makes a jammier egg", method="Marinated eggs（7 分）", egg_form="shell", medium="water", start="hot",
    T_raw="rolling boil → full boil", T_phrase="Wait for the water to come back to a full boil, then cook", rule="W-BOIL",
    time_raw="7–9 minutes（9 minutes hard, 7 minutes jammier）", t_lo=7, t_hi=7, time_counts="再沸騰してから（入れてから再沸騰までの時間は含まない）",
    doneness="7 minutes makes a jammier egg", egg_T0_raw="", egg_T0_rule="E-NONE", vinegar="no", salt="no",
    tech="殻の底にピンで穴（任意）・氷水で止める",
    quote="9 minutes will give you a fully hard boiled egg, while 7 minutes makes a jammier egg.", group="G-tonkotsu", notes="")
rec(src="wb_ja", page="料理本/ゆで卵", dish="soft_boiled_egg", variant="半熟卵", dish_basis="原文「半熟卵: 6～7分」",
    method="基本のゆで卵（沸騰した湯に入れる）", egg_form="shell", medium="water", start="hot",
    T_raw="水が沸騰したら卵を入れ、再び沸騰するまで加熱", T_phrase="水が沸騰したら、卵をそっと鍋に入れます", rule="W-BOIL",
    time_raw="半熟卵: 6～7分", t_lo=6, t_hi=7, time_counts="再沸騰してから（と読める。「その後は以下の時間で茹でます」）",
    doneness="", egg_T0_raw="冷蔵庫から取り出し、常温に戻します", egg_T0_rule="E-ROOM",
    vinegar="no", salt="optional", salt_raw="塩: 適量（お好みで）", tech="中火で加熱・冷水に移す",
    quote="半熟卵: 6～7分", group="G-ja-yudetamago", notes="")
rec(src="wb_ja", page="料理本/畜産物", dish="soft_boiled_egg", variant="半熟", dish_basis="原文「半熟：6分」",
    method="調理のコツ（手順なし）", egg_form="shell", medium="water", start="-",
    T_raw="茹でる（湯温・水から/湯からの記述なし）", T_phrase="茹でる時間を調整し", rule="W-UNSPEC",
    time_raw="半熟：6分", t_lo=6, t_hi=6, time_counts="不明（数え始めの記述なし）",
    doneness="", egg_T0_raw="", egg_T0_rule="E-NONE", vinegar="no", salt="no", tech="",
    quote="茹でる時間を調整し、好みの固さに仕上げる（半熟：6分、固ゆで：10分程度）", group="G-ja-yudetamago",
    notes="手順の無い一行の説明。同じ時期（2024-08）に作られた ゆで卵 ページと値が近い")
rec(src="fukui", page="nanetukomekko.csv|もちもち米粉ときな粉麺", dish="soft_boiled_egg", variant="半熟卵（麺の具）",
    dish_basis="原文「（半熟卵）」", method="水から茹で、沸騰したら火を止め蓋", egg_form="shell", medium="water", start="cold",
    T_raw="水の状態から鍋で茹でる→沸騰したら火を止めふた", T_phrase="沸騰したら火を止めふたをする", rule="W-RESID",
    time_raw="3分30秒ほど（沸騰して火を止めてから）", t_lo=3.5, t_hi=3.5, time_counts="火を止めてから。水から沸騰までの時間は含まない（書かれていない）",
    doneness="", egg_T0_raw="", egg_T0_rule="E-NONE", vinegar="no", salt="no", tech="水で粗熱をとる",
    quote="沸騰したら火を止めふたをする。3分30秒ほど経ったら取り出し、水で粗熱をとったら完成。", group="G-fukui-komekko",
    notes="水から始めるので、沸騰までの昇温の間にも卵は加熱される")

# ---------------- 固ゆで卵 ----------------
rec(src="wb_en", page="Cookbook:Hard Cooked Eggs", dish="hard_boiled_egg", variant="", dish_basis="ページ名 Hard Cooked Eggs",
    method="Boiling method（水から）", egg_form="shell", medium="water", start="cold",
    T_raw="Bring to a rolling boil. Reduce heat to a low boil.", T_phrase="Reduce heat to a low boil", rule="W-BOIL",
    time_raw="10–15 minutes, depending on the size and number of eggs", t_lo=10, t_hi=15, time_counts="沸騰してから（水から沸騰までは含まない）",
    doneness="", egg_T0_raw="", egg_T0_rule="E-NONE", vinegar="no", salt="optional",
    salt_raw="adding salt to the water keeps the shells from sticking（注記）", tech="卵の上 25 mm（1 inch）まで水・氷水で冷やす",
    quote="Reduce heat to a low boil. Cook for 10–15 minutes, depending on the size and number of eggs.", group="G-hardcooked",
    notes="low boil も沸騰なので W-BOIL")
rec(src="wb_en", page="Cookbook:Hard Cooked Eggs", dish="hard_boiled_egg", variant="", dish_basis="ページ名 Hard Cooked Eggs",
    method="Steaming method", egg_form="shell", medium="steam", start="hot",
    T_raw="2 cm of water to a fast boil; steam with lid", T_phrase="Steam for about 12–13 minutes—the heat can be lowered slightly, as long as there is steam", rule="S-STEAM",
    time_raw="about 12–13 minutes", t_lo=12, t_hi=13, time_counts="蒸し始めてから",
    doneness="", egg_T0_raw="", egg_T0_rule="E-NONE", vinegar="no", salt="no", tech="蓋・氷水で冷やす",
    quote="Steam for about 12–13 minutes—the heat can be lowered slightly, as long as there is steam.", group="G-hardcooked", notes="")
rec(src="wb_en", page="Cookbook:Hard Cooked Eggs", dish="hard_boiled_egg", variant="", dish_basis="ページ名 Hard Cooked Eggs",
    method="注記の別法（卵を入れたら火を止め蓋）", egg_form="shell", medium="water", start="-",
    T_raw="turn off the heat after adding the eggs", T_phrase="turn off the heat after adding the eggs, cover the pot", rule="W-RESID",
    time_raw="15–18 minutes", t_lo=15, t_hi=18, time_counts="火を止めてから",
    doneness="", egg_T0_raw="", egg_T0_rule="E-NONE", vinegar="no", salt="no", tech="蓋",
    quote="An alternate method for boiling is to turn off the heat after adding the eggs, cover the pot, and let stand 15–18 minutes.",
    group="G-hardcooked", notes="卵を水から入れるのか沸騰した湯に入れるのかは書かれていない")
rec(src="wb_en", page="Cookbook:Tonkotsu Ramen", dish="hard_boiled_egg", variant="", dish_basis="原文 9 minutes will give you a fully hard boiled egg",
    method="Marinated eggs（9 分）", egg_form="shell", medium="water", start="hot",
    T_raw="rolling boil → full boil", T_phrase="Wait for the water to come back to a full boil, then cook", rule="W-BOIL",
    time_raw="9 minutes", t_lo=9, t_hi=9, time_counts="再沸騰してから",
    doneness="fully hard boiled", egg_T0_raw="", egg_T0_rule="E-NONE", vinegar="no", salt="no", tech="氷水で止める",
    quote="Wait for the water to come back to a full boil, then cook for 7–9 minutes.", group="G-tonkotsu", notes="")
rec(src="wb_ja", page="料理本/ゆで卵", dish="hard_boiled_egg", variant="", dish_basis="原文「中身がしっかり固まった卵: 10～12分」",
    method="基本のゆで卵（沸騰した湯に入れる）", egg_form="shell", medium="water", start="hot",
    T_raw="水が沸騰したら卵を入れ、再び沸騰するまで加熱", T_phrase="再び沸騰するまで加熱し", rule="W-BOIL",
    time_raw="10～12分", t_lo=10, t_hi=12, time_counts="再沸騰してから",
    doneness="", egg_T0_raw="冷蔵庫から取り出し、常温に戻します", egg_T0_rule="E-ROOM",
    vinegar="no", salt="optional", salt_raw="塩: 適量（お好みで）", tech="冷水に移す",
    quote="中身がしっかり固まった卵: 10～12分", group="G-ja-yudetamago", notes="")
rec(src="wb_ja", page="料理本/畜産物", dish="hard_boiled_egg", variant="", dish_basis="原文「固ゆで：10分程度」",
    method="調理のコツ（手順なし）", egg_form="shell", medium="water", start="-",
    T_raw="茹でる", T_phrase="茹でる時間を調整し", rule="W-UNSPEC",
    time_raw="10分程度", t_lo=10, t_hi=10, time_counts="不明",
    doneness="", egg_T0_raw="", egg_T0_rule="E-NONE", vinegar="no", salt="no", tech="",
    quote="固ゆで：10分程度", group="G-ja-yudetamago", notes="")
rec(src="wb_en", page="Cookbook:Egg Butter", dish="hard_boiled_egg", variant="", dish_basis="原文 Hard-boil the eggs",
    method="-", egg_form="shell", medium="water", start="-", T_raw="hard-boil", T_phrase="Hard-boil the eggs", rule="W-UNSPEC",
    time_raw="about 10 minutes", t_lo=10, t_hi=10, time_counts="不明",
    doneness="", egg_T0_raw="", egg_T0_rule="E-NONE", vinegar="no", salt="no", tech="",
    quote="Hard-boil the eggs (about 10 minutes).", group="G-eggbutter", notes="Hard Boiled Eggs ページへのリンクつき")
rec(src="wb_en", page="Cookbook:Vinegar-Pickled Eggs and Onions", dish="hard_boiled_egg", variant="酢漬けの下ゆで",
    dish_basis="原文の手順（ゆでて殻をむき酢に漬ける）", method="-", egg_form="shell", medium="water", start="hot",
    T_raw="boiling water, return to a boil", T_phrase="Wait for the water to return to a boil and then boil the eggs", rule="W-BOIL",
    time_raw="a further 12 minutes", t_lo=12, t_hi=12, time_counts="再沸騰してから",
    doneness="", egg_T0_raw="", egg_T0_rule="E-NONE", vinegar="no", salt="no", tech="お玉でそっと入れる・氷水で止める",
    quote="Wait for the water to return to a boil and then boil the eggs for a further 12 minutes.", group="G-pickled",
    notes="原文に「卵を入れると湯温が下がる」とある（The temperature of the water will lower with the addition of the eggs.）")
rec(src="wb_en", page="Cookbook:Potato Salad (Southern Ontario Style)", dish="hard_boiled_egg", variant="",
    dish_basis="原文 until hard-boiled", method="-", egg_form="shell", medium="water", start="-",
    T_raw="boil the eggs in water", T_phrase="boil the eggs in water", rule="W-UNSPEC",
    time_raw="about 30 minutes", t_lo=30, t_hi=30, time_counts="不明（水からか湯からか書かれていない）",
    doneness="until hard-boiled", egg_T0_raw="", egg_T0_rule="E-NONE", vinegar="no", salt="no", tech="流水で冷やす",
    quote="boil the eggs in water for about 30 minutes until hard-boiled.", group="G-potatosalad", notes="他の行より長い（外れ値）")
rec(src="wb_en", page="Cookbook:Tea Eggs", dish="hard_boiled_egg", variant="茶葉蛋（ゆでてから殻を割り煮汁で煮る）",
    dish_basis="原文の手順", method="3 分ゆで→殻を割る→1 時間 simmer", egg_form="shell", medium="water", start="hot",
    T_raw="boil 3 minutes, then simmer 1 hour", T_phrase="boil for 3 minutes ... simmer for 1 hour", rule="W-SIMMER",
    time_raw="3 minutes + 1 hour", t_lo=63, t_hi=63, time_counts="沸騰 3 分＋simmer 60 分の合計",
    doneness="", egg_T0_raw="", egg_T0_rule="E-NONE", vinegar="no", salt="no", tech="煮汁は水＋香辛料・殻にひびを入れて戻す",
    quote="Return the eggs to the pot of liquid, reduce to a simmer, and simmer for 1 hour.", group="G-teaeggs",
    notes="温度は2段（100℃で3分→85〜95℃で60分）。T は長い方の simmer で代表させた")
rec(src="wb_en", page="Cookbook:Quail Egg and Chili Jangjorim", dish="hard_boiled_egg", variant="うずら卵",
    dish_basis="原文の手順（ゆでて殻をむき煮る）", method="-", egg_form="shell", medium="water", start="hot",
    T_raw="Bring a pot of water to a boil. Add the quail eggs", T_phrase="boil for about 10 minutes", rule="W-BOIL",
    time_raw="about 10 minutes", t_lo=10, t_hi=10, time_counts="卵を入れてから",
    doneness="", egg_T0_raw="", egg_T0_rule="E-NONE", vinegar="no", salt="no", tech="冷水で冷ます",
    quote="Add the quail eggs, and boil for about 10 minutes.", group="G-quail",
    notes="うずら卵（鶏卵より小さい）。鶏卵の地図に重ねない")

# ---------------- ポーチドエッグ ----------------
rec(src="wb_en", page="Cookbook:Poached Egg", dish="poached_egg", variant="", dish_basis="ページ名 Poached Egg",
    method="-", egg_form="cracked", medium="water", start="hot",
    T_raw='"shrimp eyes" stage. It should be about 70–80 °C (155–175 °F)', T_stated_c="70–80", T_phrase='Bring the water to a "shrimp eyes" stage',
    rule="", time_raw="The yolks should set in around 2–3 minutes", t_lo=2, t_hi=3, time_counts="湯に入れてから",
    doneness="yolks should set", egg_T0_raw="", egg_T0_rule="E-NONE",
    vinegar="optional", vinegar_raw="Optionally, add 1 tablespoon of vinegar（湯は about 1 cm）", salt="no",
    tech="渦を作る・ざるで水っぽい卵白を切る・10〜15 秒ずつ間をあけて入れる",
    quote="It should be about 70–80 °C (155–175 °F)", group="G-poachedegg",
    notes="湯量が書かれず（1 cm の深さ）酢の割合は出せない。「yolks should set」は卵黄が固まる意味にも読める")
rec(src="wb_en", page="Cookbook:Poaching", dish="poached_egg", variant="soft, runny yolk", dish_basis="節名 Egg poaching",
    method="Whirlpool method（3–4 分）", egg_form="cracked", medium="water", start="hot",
    T_raw="gentle simmer（Avoid boiling the water）", T_phrase="Heat the water over medium-low heat until it reaches a gentle simmer", rule="W-GENTLE",
    time_raw="about 3-4 minutes for a soft, runny yolk", t_lo=3, t_hi=4, time_counts="湯に入れてから",
    doneness="soft, runny yolk", egg_T0_raw="", egg_T0_rule="E-NONE",
    vinegar="optional", vinegar_raw="a splash of white vinegar (about one tablespoon per liter/quart of water)", vinegar_pct=1.5,
    salt="optional", salt_raw="a pinch of salt", tech="新しい卵・渦を作る・小さな器に割ってから滑らせる",
    quote="poach the egg for about 3-4 minutes for a soft, runny yolk or 5-6 minutes for a firmer yolk", group="G-poaching",
    notes="同じページ冒頭に poaching の理想温度 160F–180F（75-80C）とあるが、この節の手順は gentle simmer と書く")
rec(src="wb_en", page="Cookbook:Poaching", dish="poached_egg", variant="firmer yolk", dish_basis="節名 Egg poaching",
    method="Whirlpool method（5–6 分）", egg_form="cracked", medium="water", start="hot",
    T_raw="gentle simmer", T_phrase="Heat the water over medium-low heat until it reaches a gentle simmer", rule="W-GENTLE",
    time_raw="5-6 minutes for a firmer yolk", t_lo=5, t_hi=6, time_counts="湯に入れてから",
    doneness="firmer yolk", egg_T0_raw="", egg_T0_rule="E-NONE",
    vinegar="optional", vinegar_raw="about one tablespoon per liter/quart of water", vinegar_pct=1.5,
    salt="optional", salt_raw="a pinch of salt", tech="渦を作る",
    quote="poach the egg for about 3-4 minutes for a soft, runny yolk or 5-6 minutes for a firmer yolk", group="G-poaching", notes="")
rec(src="wb_en", page="Cookbook:Portable Eggs Benedict", dish="poached_egg", variant="エッグベネディクト風",
    dish_basis="原文 our favorite poached egg dish", method="-", egg_form="cracked", medium="water", start="hot",
    T_raw="boiling water/vinegar mixture", T_phrase="Crack eggs into the boiling water/vinegar mixture", rule="W-BOIL-POACH",
    time_raw="5–7 minutes", t_lo=5, t_hi=7, time_counts="湯に入れてから",
    doneness="", egg_T0_raw="", egg_T0_rule="E-NONE", vinegar="yes", vinegar_raw="1 dash white vinegar", salt="no", tech="深い鍋",
    quote="Crack eggs into the boiling water/vinegar mixture. Leave them alone for 5–7 minutes.", group="G-portable", notes="")
rec(src="wb_en", page="Cookbook:English Breakfast", dish="poached_egg", variant="イングリッシュ・ブレックファストの卵",
    dish_basis="原文 fried or poached eggs の poached の手順", method="沸騰した湯に割り入れ、ごく弱い simmer", egg_form="cracked", medium="water", start="hot",
    T_raw="boiling → very very gently simmer", T_phrase="turn the heat down to a very very gently simmer", rule="W-GENTLE",
    time_raw="about 8–10 minutes", t_lo=8, t_hi=10, time_counts="割り入れてから",
    doneness="egg white should be soft but cooked through and the yolk still runny", egg_T0_raw="", egg_T0_rule="E-NONE",
    vinegar="no", salt="no", tech="湯は深さ約 1 cm・セルクル（任意）・上から湯をかける",
    quote="They should take about 8–10 minutes to cook.", group="G-englishbreakfast",
    notes="湯が浅く卵の上面が湯から出るので、上から湯をかける。他の行より長い")
rec(src="wb_en", page="Cookbook:Çılbır (Turkish Eggs with Yogurt)", dish="poached_egg", variant="チュルブル（ヨーグルトがけ）",
    dish_basis="原文 poach the eggs", method="-", egg_form="cracked", medium="water", start="hot",
    T_raw="boiling water ... poach", T_phrase="Add the vinegar and some salt to boiling water, and poach the eggs", rule="W-BOIL-POACH",
    time_raw="（記述なし）", t_lo=None, t_hi=None, time_counts="",
    doneness="", egg_T0_raw="", egg_T0_rule="E-NONE", vinegar="yes", vinegar_raw="1 tbsp vinegar / 1 L water", vinegar_pct=1.5,
    salt="yes", salt_raw="some salt", tech="",
    quote="Add the vinegar and some salt to boiling water, and poach the eggs.", group="G-cilbir", notes="時間の記述なし")
rec(src="wb_hf", page="Stir-fried Veggies and Poached Egg", dish="poached_egg", variant="", dish_basis="ページ名",
    method="-", egg_form="cracked", medium="water", start="hot",
    T_raw="boiling, swirl", T_phrase="Once water is boiling, swirl the water", rule="W-BOIL-POACH",
    time_raw="2 minutes or more", t_lo=2, t_hi=None, time_counts="湯に入れてから",
    doneness="depending on your preference", egg_T0_raw="", egg_T0_rule="E-NONE",
    vinegar="yes", vinegar_raw="a dash of vinegar", salt="no", tech="器に割ってから・渦を約 20 秒作る",
    quote="Once water is boiling, swirl the water anti clockwise for about 20 seconds, then place the egg in the middle of the swirl.",
    group="G-stirfried", notes="2026-09-01 の公式ダンプには無い（2024-07-31 以降に削除）。HF のスナップショットから読んだ")

# ---------------- スクランブルエッグ ----------------
def scr(page, heat_raw, rule, time_raw, t_lo, t_hi, quote, *, variant="", fat="", tech="", notes="", src="wb_en",
        doneness="", counts="卵液を入れてから", medium="pan", phrase=None, group=None):
    rec(src=src, page=page, dish="scrambled_eggs", variant=variant, dish_basis="ページ名・原文の scramble",
        method="-", egg_form="beaten", medium=medium, start="preheated" if medium == "pan" else "-",
        T_raw=heat_raw, T_phrase=phrase or heat_raw, rule=rule, time_raw=time_raw, t_lo=t_lo, t_hi=t_hi,
        time_counts=counts if t_lo is not None else "", doneness=doneness, egg_T0_raw="", egg_T0_rule="E-NONE",
        vinegar="no", salt="", tech=(fat + ("・" if fat and tech else "") + tech), quote=quote,
        group=group or ("G-" + re.sub(r"\W+", "", page.split(":")[-1])[:20].lower()), notes=notes)


scr("Cookbook:Basic Scrambled Eggs", "medium heat", "P-MED", "（記述なし）", None, None,
    "Melt butter in a frying pan on medium heat", fat="バター",
    tech="泡立つまで溶く・速く混ぜると小さいカード", doneness="The eggs are done when the sheen disappears; stop cooking just before this happens.")
scr("Cookbook:Easy Scrambled Eggs", "medium", "P-MED", "30 seconds to 3 or more minutes", 0.5, 3,
    "The time will vary from 30 seconds to 3 or more minutes", fat="バター・油・スプレー", tech="牛乳か水（任意）・へらで絶えずこそげる",
    notes="上限は「3 or more」")
scr("Cookbook:Easy Scrambled Eggs", "microwave on high", "MW", "40 seconds to 2 minutes", 40 / 60, 2,
    "Microwave on high for 40 seconds to 2 minutes.", variant="電子レンジ版", medium="microwave", counts="加熱時間",
    group="G-easyscrambledeggs", notes="電子レンジ。フライパンの地図に重ねない")
scr("Cookbook:Microwaved Scrambled Egg", "microwave on high power", "MW", "30 seconds + 30 seconds", 1, 1,
    "Microwave on high power for 30 seconds.", variant="電子レンジ", medium="microwave", counts="加熱時間の合計（途中で混ぜる）",
    notes="電子レンジ。フライパンの地図に重ねない")
scr("Cookbook:Creamy Cornstarch Scrambled Eggs", "high heat until hot; butter melted and bubbly, but before it browns; then off the heat",
    "P-HIGH", "about 3 seconds + 11–12 seconds off the heat", (3 + 11) / 60, (3 + 12) / 60,
    "Start stirring the eggs, making 1 full circle per second, for about 11–12 seconds.",
    phrase="Heat a non-stick skillet over high heat until hot", fat="バター", tech="牛乳＋コーンスターチ・火から外して混ぜる",
    counts="火の上 3 秒＋火から外して 11〜12 秒", notes="大半は火から外した余熱。T は火の上の段階")
scr("Cookbook:Scrambled Eggs with Herbs", "medium heat", "P-MED", "several minutes", None, None,
    "Stir gently with corner spoon for several minutes until mixture begins to congeal into lumps.",
    phrase="Put pan on stovetop at medium heat", fat="スプレー（任意）", doneness="no longer visibly wet",
    notes="時間は several minutes で数値なし")
scr("Cookbook:Scrambled Eggs with Sausage", "hot frying pan（ソーセージを焼いた後）", "P-HOT", "30–60 seconds", 0.5, 1,
    "Fry for 30–60 seconds.", fat="ソーセージの脂")
scr("Cookbook:Scrambled Eggs with Vegetables", "medium heat", "P-MED", "（記述なし。30 秒ごとに返す）", None, None,
    "Cook eggs and vegetables, turning every 30 seconds until cooked to taste.", phrase="Heat a frying pan over medium heat",
    fat="油", tech="トマト・きゅうり")
scr("Cookbook:Southwestern Scramble", "medium heat → high", "P-MED", "30 seconds to 1 minute（強火に上げる前）", 0.5, 1,
    "allow to cook for 30 seconds to 1 minute, until they just begin to set", fat="バター等", tech="途中で強火に上げてかき混ぜる",
    counts="中火の段階のみ。強火にしてからの時間は書かれていない", doneness="still moist, but mostly cooked")
scr("Cookbook:Machacado con Huevo (Eggs with Shredded Beef)", "medium-high heat", "P-MEDHIGH", "2–3 minutes (+2–3 minutes with beef)", 2, 3,
    "cook, stirring frequently, for 2–3 minutes or until eggs just begin to set", phrase="Heat butter in large skillet over medium-high heat",
    fat="バター", counts="卵が固まり始めるまで。牛肉を入れた後の 2〜3 分は含めない")
scr("Cookbook:Nigerian Egg Stew", "medium heat", "P-MED", "2–3 minutes", 2, 3,
    "Cook for another 2–3 minutes, or until eggs are fully set but still moist.", phrase="Heat palm oil in a frying pan over medium heat",
    fat="パーム油", tech="玉ねぎ・唐辛子と", doneness="fully set but still moist")
scr("Cookbook:Latino Scramble", "medium heat", "P-MED", "（記述なし）", None, None,
    "Let cook to your desired egg texture.", phrase="Melt butter in a medium frying pan over medium heat", fat="バター")
scr("Cookbook:Smoked Salmon Breakfast Burrito", "medium heat", "P-MED", "（記述なし）", None, None,
    "In sauté pan over medium heat, add oil to coat the pan, add egg mixture to scramble.", fat="油", tech="牛乳・レモン汁")
scr("Cookbook:Firfir (Ethiopian Spicy Scrambled Eggs with Injera)", "medium heat", "P-MED", "（記述なし）", None, None,
    "Pour the beaten eggs into the empty space in the pan and scramble them with a wooden spoon or spatula until they are fully cooked.",
    phrase="Heat the olive oil in a large skillet or frying pan over medium heat", fat="オリーブ油", doneness="fully cooked")
scr("Cookbook:Riz Gras (West African Fried Rice)", "medium heat", "P-MED", "（記述なし）", None, None,
    "Pour the lightly beaten eggs into the pan, and scramble them until cooked through.",
    phrase="Heat a small amount of vegetable oil in the skillet or wok over medium heat", fat="植物油", doneness="cooked through")
scr("Cookbook:Khao Pad Gai (Thai Chicken Fried Rice)", "high heat（中華鍋）", "P-HIGH", "（記述なし）", None, None,
    "When almost fully scrambled, mix in the chicken and stir around for 30 seconds more.",
    phrase="turn the flame to high heat", fat="ピーナッツ油", tech="中華鍋・鶏肉と一緒")

# ---------------- プリン類 ----------------
def cus(page, variant, medium, T_raw, T_stated_c, rule, time_raw, t_lo, t_hi, quote, *, src="wb_en", tech="", doneness="",
        notes="", phrase=None, basis="ページ名・原文", dish="custard_pudding", group=None, egg_T0_raw="", egg_T0_rule="E-NONE"):
    rec(src=src, page=page, dish=dish, variant=variant, dish_basis=basis, method="-", egg_form="custard_mix", medium=medium,
        start="preheated", T_raw=T_raw, T_stated_c=T_stated_c, T_phrase=phrase or T_raw, rule=rule, time_raw=time_raw,
        t_lo=t_lo, t_hi=t_hi, time_counts="加熱を始めてから" if t_lo is not None else "", doneness=doneness,
        egg_T0_raw=egg_T0_raw, egg_T0_rule=egg_T0_rule, vinegar="no", salt="", tech=tech, quote=quote,
        group=group or ("G-" + re.sub(r"\W+", "", page.split(":")[-1].split("/")[-1])[:20].lower()), notes=notes)


cus("料理本/プリン", "蒸しプリン（卵・牛乳・砂糖）", "steam", "蒸し器に水を沸かし、弱火", "", "S-LOW", "15分ほど", 15, 15,
    "蒸し器に水を沸かし、弱火で15分ほど蒸す。", src="wb_ja", tech="アルミホイルで蓋", basis="ページ名 プリン")
cus("Cookbook:Baked Custard", "焼きカスタード（卵・牛乳・砂糖）", "oven_water_bath", "slow oven (300–325°F / 150–160°C)", "150–160", "O-BATH",
    "between 30 and 40 minutes", 30, 40,
    "Place the baking dish or the molds in a pan of water in a slow oven (300–325°F / 150–160°C) and bake for between 30 and 40 minutes.",
    doneness="knife will come out clean")
cus("Cookbook:Crème Brûlée I", "クレームブリュレ（生クリーム・卵黄）", "oven_water_bath", "300°F (150°C)、熱湯を型の 2/3 まで", "150", "O-BATH",
    "start checking at 30 minutes ... up to an hour", 30, 60,
    "Bake until an instant-read thermometer registers 170–175°F (77–79°C)",
    doneness="中心温度 170–175°F（77–79℃）または縁が固まり中央が少し揺れる", tech="天板にタオル・熱湯を注ぐ",
    notes="止める条件が中心温度で書かれている唯一の行")
cus("Cookbook:Crème Brûlée II", "クレームブリュレ", "oven_water_bath", "350°F (180°C)、湯 2–2.5 cm", "180", "O-BATH",
    "from 25 to 50 minutes", 25, 50, "Usually, the time ranges from 25 to 50 minutes.", doneness="until set (like Jell-O)")
cus("Cookbook:Crème Brûlée III", "クレームブリュレ", "oven_water_bath", "325°F (160°C)、型を少しの湯に", "160", "O-BATH",
    "around 40 minutes", 40, 40, "bake for around 40 minutes or until the custard is set", doneness="until the custard is set")
cus("Cookbook:Flan de Queso (Cream Cheese Flan)", "フラン（クリームチーズ・練乳・無糖練乳）", "oven_water_bath", "350°F (175°C)、湯 1.5 inch",
    "175", "O-BATH", "45–50 minutes", 45, 50, "Bake flan for 45–50 minutes in the preheated oven.", doneness="toothpick comes out clean")
cus("Cookbook:Spanish Flan", "フラン（練乳・無糖練乳）", "oven_water_bath", "375°F、湯 1 inch", "191", "O-BATH",
    "1 hour", 60, 60, "Cook for 1 hour or until center is firm.", doneness="center is firm", notes="375°F＝190.6℃を 191 に丸めた")
cus("Cookbook:Dominican Flan", "フラン（練乳・無糖練乳・卵 8 個）", "stove_bain_marie", "鍋の湯煎を中火で simmer（蓋）", "",
    "S-BAIN-STOVE", "（記述なし）", None, None,
    "Cover the larger pot with a lid, and simmer over medium heat until the custard is fully cooked.",
    doneness="butter knife に何も付かない")
cus("Cookbook:Khanom Mo Keang (Thai Custard)", "タイの焼きカスタード（ココナッツクリーム）", "oven_dry", "180°C", "180", "O-DRY",
    "35–45 minutes", 35, 45, "Bake at 180°C for 35–45 minutes or until the center is slightly firm and the top is golden brown.",
    doneness="中心が少し固く表面が焼き色", notes="湯煎なし")
cus("Cookbook:Coconut Pudding II", "蒸しココナッツプリン", "steam", "蒸籠を沸騰した湯の上", "", "S-STEAM", "30–40 minutes", 30, 40,
    "Steam the pudding for 30–40 minutes, or until no longer fluid. If the pudding is cooked too fast, it becomes rubbery.",
    doneness="no longer fluid", notes="「速く火を通すとゴムのようになる」とある")
cus("Cookbook:Watalappam (Sri Lankan Coconut Custard)", "ワタラッパン（ココナッツミルク・ジャガリー）", "steam", "steam（湯温の記述なし）", "", "S-STEAM",
    "20 minutes（小分けなら 5–10 minutes）", 20, 20, "Transfer the mixture to a pot and steam for 20 minutes.",
    notes="小さなアルミ容器に分けると 5〜10 分とも書く")
cus("Cookbook:Kuih Seri Muka (Malaysian Sticky Rice with Pandan Custard)", "もち米の上のパンダンカスタード層", "steam",
    "蒸し器の湯を沸騰", "", "S-STEAM", "15–20 minutes", 15, 20,
    "Steam for 15–20 minutes, or until the custard is firm and a skewer inserted into it comes out clean.",
    doneness="skewer comes out clean", tech="蓋を布で包み水滴を防ぐ", notes="単独のプリンではなく層")

# ---------------- 茶碗蒸し ----------------
cus("fukuinobi_recipe.csv|豆乳茶碗蒸し・おろしそば", "豆乳茶碗蒸し", "steam", "蒸す（温度・火力の記述なし）", "", "NONE",
    "（記述なし）", None, None, "器にささみとかまぼこを入れ、豆乳などを混ぜ合わせたものを流し入れ蒸す。しばらく置いて固まったら、上にエビをのせる。",
    src="fukui", dish="chawanmushi", basis="献立名 豆乳茶碗蒸し", doneness="しばらく置いて固まったら", tech="ザルでこす",
    group="G-fukui-kenkobishoku", notes="茶碗蒸しで見つかったのはこの1件のみ。温度・時間は書かれていない")

# ----------------------------------------------------------------------


def plain(text: str) -> str:
    """wikitext を引用の照合用に平文へ（ref・リンク・強調・空白を落とす）。"""
    t = re.sub(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>", "", text, flags=re.S)
    t = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", t)
    t = t.replace("'''", "").replace("''", "")
    t = re.sub(r"\s+", " ", t)
    return t


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def load_dump(path: Path, titles: set[str]) -> dict[str, dict]:
    out = {}
    ns = None
    for _, el in ET.iterparse(bz2.open(path), events=("end",)):
        if el.tag.endswith("}page"):
            ns = ns or el.tag[:-4]
            title = el.find(ns + "title").text
            if title in titles:
                rev = el.find(ns + "revision")
                out[title] = {"revid": rev.find(ns + "id").text, "ts": rev.find(ns + "timestamp").text,
                              "text": rev.find(ns + "text").text or ""}
            el.clear()
    return out


def load_sources() -> dict[tuple[str, str], dict]:
    need = defaultdict(set)
    for r in R:
        need[r["src"]].add(r["page"])
    got: dict[tuple[str, str], dict] = {}
    for key, path, host in (("wb_en", EN_DUMP, "en"), ("wb_ja", JA_DUMP, "ja")):
        pages = load_dump(path, need[key])
        for t in need[key]:
            if t not in pages:
                sys.exit(f"ダンプに無いページ: {t}")
            p = pages[t]
            slug = urlquote(t.replace(" ", "_"), safe=":/()")
            got[(key, t)] = {"text": plain(p["text"]), "revid": p["revid"], "ts": p["ts"],
                             "url": f"https://{host}.wikibooks.org/wiki/{slug}",
                             "permalink": f"https://{host}.wikibooks.org/w/index.php?oldid={p['revid']}"}
    hf = {r["recipe_data"]["title"]: r["recipe_data"] for r in json.loads(HF_JSON.read_text())}
    for t in need["wb_hf"]:
        d = hf[t]
        got[("wb_hf", t)] = {"text": norm(" ".join(x["text"] for x in d["text_lines"])), "revid": "", "ts": "2024-07-31（スクレイプ日）",
                             "url": d["url"], "permalink": "https://huggingface.co/datasets/gossminn/wikibooks-cookbook/blob/49fb73ea07d2a1380c15197db5589934937457ed/recipes_parsed.mini.json"}
    for t in need["fukui"]:
        fn, name = t.split("|")
        rows = list(csv.reader((FUKUI / fn).open(encoding="cp932")))
        hits = [r for r in rows[1:] if name in r[:2]]
        text = norm(" ".join(" ".join(r) for r in hits))
        got[("fukui", t)] = {"text": text, "revid": "", "ts": "", "url": FUKUI_DATASET[fn][1],
                             "permalink": "https://www.pref.fukui.lg.jp/doc/dx-suishin/opendata/list_6.html"}
    return got


def fnum(x):
    if x is None or x == "":
        return ""
    return f"{x:.2f}".rstrip("0").rstrip(".")


def build():
    md_rules = (HERE / "extraction_rules.md").read_text()
    for rid in list(RULES) + list(EGG_T0_RULES) + ["V-TBSP-L"]:
        if f"`{rid}`" not in md_rules:
            sys.exit(f"extraction_rules.md に規則 {rid} が無い")
    src = load_sources()
    rows = []
    for i, r in enumerate(R, 1):
        s = src[(r["src"], r["page"])]
        for q in [r["quote"]]:
            if norm(q) not in s["text"]:
                sys.exit(f"引用が原文に無い: {r['page']}: {q}")
        rule = r.get("rule", "")
        stated = r.get("T_stated_c", "")
        if stated:
            est = (None, None, None, "")
            is_est = "no"
        else:
            est = RULES[rule]
            is_est = "yes" if est[0] is not None else ""
        t0 = EGG_T0_RULES[r["egg_T0_rule"]]
        lo, hi = r["t_lo"], r["t_hi"]
        mid = (lo + hi) / 2 if (lo is not None and hi is not None) else (lo if lo is not None else None)
        # 地図に重ねる代表値
        if stated:
            nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", stated)]
            map_T = sum(nums) / len(nums)
        else:
            map_T = est[0]
        medium = r["medium"]
        reasons = []
        if r["src"] and "うずら" in r.get("variant", ""):
            reasons.append("うずら卵")
        if medium in ("oven_water_bath", "oven_dry", "stove_bain_marie", "microwave"):
            reasons.append(f"媒体が {medium}（Exp-14 の地図の軸と違う）")
        if rule == "W-RESID":
            reasons.append("余熱（一定温度でない）")
        if r["start"] == "cold":
            reasons.append("水から（昇温中の加熱を含む）")
        if map_T is None:
            reasons.append("温度が決まらない")
        if mid is None:
            reasons.append("時間の記述なし")
        if r["dish"] == "hard_boiled_egg" and "茶葉" in r.get("variant", ""):
            reasons.append("2段の加熱")
        map_ok = "yes" if not reasons else "no"
        after, after_basis = after_step(r)
        if map_ok == "yes" and (is_est == "yes"):
            map_ok = "yes（温度は推定）"
        rows.append({
            "row_id": f"R{i:03d}",
            "dish": r["dish"], "dish_ja": SIM_DISH[r["dish"]], "variant": r.get("variant", ""), "dish_basis": r["dish_basis"],
            "source": SOURCE_NAME[r["src"]], "page_title": r["page"].split("|")[-1] if r["src"] == "fukui" else r["page"],
            "dataset": FUKUI_DATASET[r["page"].split("|")[0]][0] if r["src"] == "fukui" else "",
            "url": s["url"], "permalink": s["permalink"], "revision_id": s["revid"], "revision_time": s["ts"],
            "license": LICENSE[r["src"]], "retrieved": RETRIEVED,
            "method": r.get("method", ""), "egg_form": r["egg_form"], "medium": medium, "start": r["start"],
            "T_raw": r["T_raw"], "T_stated_c": stated, "T_phrase": r.get("T_phrase", ""),
            "T_rule": "" if stated else rule, "T_est_c": fnum(est[0]), "T_est_lo_c": fnum(est[1]), "T_est_hi_c": fnum(est[2]),
            "T_is_estimate": is_est, "T_est_basis": est[3],
            "time_raw": r["time_raw"], "time_min_lo": fnum(lo), "time_min_hi": fnum(hi), "time_counts": r.get("time_counts", ""),
            "doneness_raw": r.get("doneness", ""),
            "egg_T0_raw": r.get("egg_T0_raw", ""), "egg_T0_rule": r["egg_T0_rule"], "egg_T0_est_c": fnum(t0[0]),
            "vinegar": r.get("vinegar", ""), "vinegar_raw": r.get("vinegar_raw", ""),
            "vinegar_pct_est": fnum(r.get("vinegar_pct")), "salt": r.get("salt", ""), "salt_raw": r.get("salt_raw", ""),
            "techniques": r.get("tech", ""), "quote": r["quote"], "independence_group": r["group"],
            "map_T_c": fnum(map_T), "map_time_min": fnum(mid), "map_egg_form": r["egg_form"], "map_ok": map_ok,
            "map_note": "・".join(reasons), "notes": r.get("notes", ""),
            "after_step": after, "after_basis": after_basis,
        })
    with (HERE / "recipes.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    write_summary(rows)
    print(f"recipes.csv: {len(rows)} 行")


def stats(vals):
    v = sorted(x for x in vals if x is not None)
    if not v:
        return "—", "—", "—", 0
    return fnum(v[0]), fnum(statistics.median(v)), fnum(v[-1]), len(v)


def write_summary(rows):
    order = ["onsen_tamago", "soft_boiled_egg", "hard_boiled_egg", "poached_egg", "scrambled_eggs", "custard_pudding", "chawanmushi"]
    by = defaultdict(list)
    for r in rows:
        by[r["dish"]].append(r)
    f = lambda s: float(s) if s not in ("", None) else None  # noqa: E731
    L = ["# Exp-15 集計（build.py が生成。手で直さない）", "",
         f"`recipes.csv` {len(rows)} 行。1 行 = 1 つの手順（同じページの別の方法・別の硬さは別の行）。",
         "温度は「原文に数値がある」ものと「あいまいな表現を換算した推定」を分けて数える。推定の換算は `extraction_rules.md`。", "",
         "## 1. 料理ごとの件数", "",
         "| 料理 | 行 | ページ（独立の目安） | 温度が原文の数値 | 温度が推定 | 温度が決まらない | 時間あり | 地図に重ねられる |",
         "|---|---|---|---|---|---|---|---|"]
    for d in order:
        rs = by[d]
        groups = len({r["independence_group"] for r in rs})
        n_stated = sum(1 for r in rs if r["T_stated_c"])
        n_est = sum(1 for r in rs if r["T_is_estimate"] == "yes")
        n_none = len(rs) - n_stated - n_est
        n_time = sum(1 for r in rs if r["time_min_lo"] != "")
        n_map = sum(1 for r in rs if r["map_ok"].startswith("yes"))
        L.append(f"| {SIM_DISH[d]} (`{d}`) | {len(rs)} | {groups} | {n_stated} | {n_est} | {n_none} | {n_time} | {n_map} |")
    L += ["", "目安は 1 料理 10〜30 件。温泉卵・茶碗蒸しは足りないまま記録した（§5）。", "",
          "## 2. 温度・時間の分布", "",
          "- 温度は湯・蒸気・フライパンなど**媒体**の温度。オーブンの行はオーブンの設定温度で、卵液が受ける温度ではない（別に分けた）。",
          "- 「すべて」は推定を含む代表値（`map_T_c`：原文に幅があれば中央、推定は換算表の中心）。「原文の数値のみ」は推定を除いた値。",
          "- 時間は `time_min_lo`〜`time_min_hi` の中央（`map_time_min`）。数え始めは行ごとに違う（`time_counts`）。", "",
          "| 料理 | 媒体 | 温度 すべて（最小/中央/最大, n） | 温度 原文の数値のみ | 時間 分（最小/中央/最大, n） |",
          "|---|---|---|---|---|"]
    for d in order:
        med_groups = defaultdict(list)
        for r in by[d]:
            med_groups[r["medium"]].append(r)
        for m, rs in sorted(med_groups.items()):
            a = stats([f(r["map_T_c"]) for r in rs])
            st = []
            for r in rs:
                if r["T_stated_c"]:
                    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", r["T_stated_c"])]
                    st.append(sum(nums) / len(nums))
            b = stats(st)
            t = stats([f(r["map_time_min"]) for r in rs])
            L.append(f"| {SIM_DISH[d]} | {m} | {a[0]} / {a[1]} / {a[2]} (n={a[3]}) | "
                     f"{b[0]} / {b[1]} / {b[2]} (n={b[3]}) | {t[0]} / {t[1]} / {t[2]} (n={t[3]}) |")
    # 酢
    pe = by["poached_egg"]
    vy = sum(1 for r in pe if r["vinegar"] == "yes")
    vo = sum(1 for r in pe if r["vinegar"] == "optional")
    vn = sum(1 for r in pe if r["vinegar"] == "no")
    sy = sum(1 for r in pe if r["salt"] in ("yes", "optional"))
    L += ["", "## 3. 酢・塩（ポーチドエッグ）", "",
          f"- ポーチドエッグ {len(pe)} 行のうち、酢を入れる {vy}・任意 {vo}・入れない {vn}。"
          f"入れる＋任意の割合 {(vy + vo) / len(pe):.0%}、必ず入れる割合 {vy / len(pe):.0%}。",
          f"- 独立ページ単位（同じページは1つ）では: " + ", ".join(
              f"{g}={'/'.join(sorted({r['vinegar'] for r in pe if r['independence_group'] == g}))}"
              for g in sorted({r['independence_group'] for r in pe})),
          f"- 酢の量が割合で出せたのは {sum(1 for r in pe if r['vinegar_pct_est'])} 行（どれも 大さじ1/水1 L＝1.5%）。他は a dash・1 tbsp（湯量不明）。",
          f"- 塩を入れる・任意 {sy} 行。",
          "- 他の料理で酢を入れる手順は無かった。ゆで卵の湯の塩は「割れたとき白身が漏れにくい」「殻がむきやすい」の注記として出る（半熟 Soft Boiled Eggs、固ゆで Hard Cooked Eggs）。"]
    # 出典
    L += ["", "## 4. 出典の内訳", "", "| 出典 | 行 | ページ |", "|---|---|---|"]
    c = Counter(r["source"] for r in rows)
    for s_, n in c.most_common():
        L.append(f"| {s_} | {n} | {len({r['page_title'] for r in rows if r['source'] == s_})} |")
    L += ["", "利用条件の記録は `data/SOURCES.md`（Exp-15 の節）。", "",
          "## 5. 独立でないもの・偏り", "",
          "- **同じページの複数行**: Soft Boiled Eggs（4 方法）、Hard Cooked Eggs（3 方法）、Poaching（2 つの硬さ）、Tonkotsu Ramen（7 分と 9 分）、"
          "ゆで卵（ja、半熟と固ゆで）、畜産物（ja、半熟と固ゆで）、Easy Scrambled Eggs（フライパンと電子レンジ）。1 人の書き手の1つの考えなので、"
          "件数を「世の中の多数派」として数えるときは `independence_group` で束ねる。",
          "- **ウィキブックス日本語版の料理本**: 料理本/ゆで卵・料理本/プリン・料理本/畜産物・料理本/鶏卵 は、ダンプの最終版の編集者がすべて同じ利用者（Ef3）で、"
          "最終版の日時も 2024-08-02〜16 に集まる（プリン 07:25、ゆで卵 07:26）。文体も同じ。最初の作成者は確認していない。"
          "半熟 6〜7 分／6 分、固ゆで 10〜12 分／10 分 は独立な2件と見なさず、同じ `independence_group`（G-ja-yudetamago）に入れた。",
          "- **Wikibooks 英語版の内部リンク**: Egg Butter は Hard Boiled Eggs ページへリンクして時間（about 10 minutes）だけ書く。値の出どころが Hard Cooked Eggs と同じ可能性がある（確認はしていない）。",
          "- **Hugging Face のスナップショット**は Wikibooks の転載（2024-07-31 時点）。公式ダンプ（2026-09-01）と重なるページはダンプを使い、ダンプから消えた "
          "Stir-fried Veggies and Poached Egg の1件だけスナップショットから読んだ。二重に数えていない。",
          "- **温泉卵**: 英語版・日本語版とも温泉卵のレシピは無い。見つかったのは牛丼（Gyudon）の「熱湯に浸けて 20 分置く」卵 1 件で、料理名は推定。",
          "  日本語版の 料理本/鶏卵 に「温泉卵は、卵を低温で長時間温めて作る」とあるが温度・時間が無く、行にしていない。",
          "- **茶碗蒸し**: 福井県「ふくい健幸美食」の豆乳茶碗蒸し 1 件のみで、温度・時間の記述が無い。英語版には茶碗蒸しのレシピが無い（Custard ページの写真の説明だけ）。",
          "- **自治体のオープンデータ**は手順付きのレシピが少なく、対象の料理はほぼ無かった（確認した自治体は SOURCES.md）。結果として英語圏の家庭料理の書き方に偏る。",
          "",
          "## 6. 推定を多く含む項目", ""]
    n = len(rows)
    est_T = sum(1 for r in rows if r["T_is_estimate"] == "yes")
    stated = sum(1 for r in rows if r["T_stated_c"])
    no_T = n - est_T - stated
    t0_known = sum(1 for r in rows if r["egg_T0_rule"] != "E-NONE")
    L += [f"- 温度: 原文に数値 {stated} 行（うち湯・蒸気の数値は Poached Egg の 70–80 °C の 1 行だけ。残りはオーブン）、推定 {est_T} 行、決まらない {no_T} 行。",
          "  フライパンの温度（弱火・中火・強火→℃）はすべて推定で、根拠が一番弱い。",
          f"- 卵を入れるときの卵の温度: 書かれていたのは {t0_known} 行（どれも「常温に戻す」）。冷蔵のまま、と書いたレシピは無い。",
          "- 時間の数え始め: 「再沸騰してから」「卵を入れてから」「火を止めてから」が混ざる。水から始める行は昇温の時間が書かれていない。",
          "- 料理の分類: 温泉卵の 1 行（牛丼の卵）は推定。Tonkotsu Ramen の 7 分（jammier）を半熟に入れたのも原文の語からの判断。",
          ""]
    (HERE / "summary.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    build()
