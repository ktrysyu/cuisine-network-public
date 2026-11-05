"""順番・操作を変えると別の料理になるか（非可換性）。"""
import pytest

from run import NO_MATCH_BELOW
from sim import PAIRS, evaluate, rank, verdict
from sim.recipes import Recipe
from sim.state import EGG_SHELL


def top1(recipe: Recipe) -> str:
    return rank(recipe.run(), 1)[0].dish


def result_for(state, dish):
    return next(r for r in evaluate(state) if r.dish == dish)


def unmet_vars(res):
    return {u.text.split(" ")[0] for u in res.unmet}


# ---- 依頼の3組 ----
def test_egg_milk_whisk_pan_is_scrambled():
    r = Recipe("卵+牛乳→撹拌→フライパン短時間", {"egg_whole": 100, "milk": 20},
               [("whisk", {"time": 1}),
                ("bake", {"T": 110, "time": 1.75, "stirring": True, "form": "thin"})])
    assert top1(r) == "scrambled_eggs"


# 90℃は 2026-09-27 まで xfail だった（理由: 中心 86.5℃でプリンの T_core_max 80〜85℃を外れ、溶いて薄めた卵にも
# 卵白・卵黄単体のしきい値を当てているため ゆで卵 が 0.80 で逆転する）。殻付きをゆで卵の必須条件にしたので
# ゆで卵は候補から外れ、プリン 0.78 が1位になった。T_core_max を外れること・薄めた卵の規則不足（C3）は残っている。
@pytest.mark.parametrize("T", [85, 88, 90])
def test_egg_milk_sugar_whisk_steam_is_pudding(T):
    r = Recipe("卵+牛乳+砂糖→撹拌→蒸す", {"egg_whole": 100, "milk": 250, "sugar": 40},
               [("whisk", {"time": 1}), ("steam", {"T": T, "time": 15, "form": "cup"})])
    assert top1(r) == "custard_pudding"


def test_only_water_temperature_changes_onsen_vs_boiled():
    def egg(T):
        return Recipe(f"殻付き卵 {T}℃ 30分", {"egg_whole": 60},
                      [("simmer", {"T": T, "time": 30, "form": "shell"})], egg_form=EGG_SHELL)
    assert top1(egg(68)) == "onsen_tamago"
    assert top1(egg(100)) == "hard_boiled_egg"


# ---- recipes.PAIRS（結果の表にも出す組）----
def _pair(title):
    return next(p for p in PAIRS if p.title.startswith(title))


def test_same_ingredients_pan_vs_steam():
    p = _pair("同じ材料で 撹拌→フライパン")
    assert p.a.ingredients == p.b.ingredients
    assert top1(p.a) == "scrambled_eggs"
    assert top1(p.b) == "custard_pudding"


def test_stirring_only_scrambled_vs_omelet():
    p = _pair("撹拌の有無だけ")
    assert top1(p.a) == "scrambled_eggs"
    assert top1(p.b) == "omelet"


FAIL_100 = ("答えの集合と下限の問題（results/summary.md）: 殻付きの必須化でゆで卵（0.80）が外れ、す立ちのプリン液は"
            "プリンの9条件のうち6つ（食材・糖濃度・連続ゲル・乳清・焼き色なし・提供温度）を満たして 0.67。下限 0.6 を"
            "上回るので該当なしにもならない。答えの集合に「す立ちのプリン」が無い")


@pytest.mark.xfail(strict=True, reason=FAIL_100)
def test_steam_100_makes_porous_not_pudding():
    p = _pair("同じ材料で加熱温度だけ変える（プリン")
    assert top1(p.a) == "custard_pudding"
    s = p.b.run()
    assert s.porosity >= 1
    assert top1(p.b) != "custard_pudding"


def test_heat_then_chill_vs_chill_then_heat_gelatin():
    """冷やす→温める では固まらない。答えの集合に「温かいゼラチン入り牛乳」が無いので1位は牛乳ゼリーのまま（割合が下がる）。"""
    p = _pair("順番を入れ替える（温める")
    a, b = p.a.run(), p.b.run()
    assert a.gelatin_state == "ゲル"
    assert b.gelatin_state == "溶解（ゾル）"
    ra, rb = result_for(a, "milk_jelly"), result_for(b, "milk_jelly")
    assert ra.fraction == 1.0
    assert rb.fraction < ra.fraction
    assert {"gelatin_state", "T_serve"} <= unmet_vars(rb)


def test_chill_then_whisk_vs_whisk_then_chill_cream():
    """室温で泡立てると泡が粗い（R-D03）。後から冷やしても戻らない。"""
    p = _pair("順番を入れ替える（冷やす→泡立てる")
    a, b = p.a.run(), p.b.run()
    assert a.foam_stage >= 2 and b.foam_stage <= 1
    ra, rb = result_for(a, "whipped_cream"), result_for(b, "whipped_cream")
    assert rb.fraction < ra.fraction
    assert {"foam_stage", "fat_phase"} <= unmet_vars(rb)


# ---- 「該当なし」（下限 run.NO_MATCH_BELOW）----
def _verdict(recipe):
    return verdict(recipe.run(), NO_MATCH_BELOW)


@pytest.mark.xfail(strict=True, reason=FAIL_100)
def test_steam_100_is_no_match():
    assert _verdict(_pair("同じ材料で加熱温度だけ変える（プリン").b).no_match


def test_cream_whisked_warm_is_no_match():
    """室温で泡立てた生クリーム → 該当なし。
    2026-09-27: ホイップクリーム 3/6=0.50 < 0.6。2026-09-28 からホイップの網目が必須なので候補から外れ、候補なし。"""
    v = _verdict(_pair("順番を入れ替える（冷やす→泡立てる").b)
    assert v.no_match and v.top is None
    assert "whipped_cream" in {r.dish for r in v.excluded}


def test_gelatin_chill_then_heat_is_no_match():
    """冷やしてから温めたゼラチン入り牛乳 → 該当なし。
    2026-09-27 までは xfail（牛乳ゼリーの6条件のうち4つを満たして 0.67 ≧ 0.6）。2026-09-28 からゲルが必須なので外れる。"""
    v = _verdict(_pair("順番を入れ替える（温める").b)
    assert v.no_match and "milk_jelly" in {r.dish for r in v.excluded}
