"""13品（＋比較用のゆで卵）それぞれの正解のレシピで、答えがその料理になるか。

- DISH_RECIPES_TIMED: 時間で止める版（最初の版）
- DISH_RECIPES: 状態で止める版（「〜になるまで」。停止条件は結果を見る前に決めた）
答えは verdict（必須条件を満たさない料理は外し、1位が下限 NO_MATCH_BELOW 未満なら「該当なし」）。
"""
import pytest

from run import NO_MATCH_BELOW
from sim import DISH_RECIPES, DISH_RECIPES_TIMED, verdict

ONION_UNTIL = ("モデルの問題（results/summary.md）: 「きつね色（maillard 2）になるまで」で止めると 3.4分で止まる。"
               "玉ねぎの表面が1分で乾いたとみなされ 140℃を超えるため（surface_wet_min は推定）。水分・重さ・硫黄・細胞壁の"
               "4条件が未達で 5/9=0.56 < 0.6、該当なし。停止条件は変えていない")


def _check(recipe, dish):
    v = verdict(recipe.run(), NO_MATCH_BELOW)
    detail = "\n".join(r.line() for r in v.candidates[:3])
    assert v.answer == dish, f"{recipe.describe()}\n{v.line()}\n{detail}"
    assert all(st["reached"] for st in recipe.run().stops), "停止条件に到達しなかった"


# 2026-09-28 夜 Q6 (a) から、沸騰12分の固ゆで卵は中心 77℃・卵黄 2 で該当なしだった（xfail）。
# 同じ夜に余熱（室温に置く後の手順、rules.md §10）を入れて、中心の最高が 80℃を超え固ゆでに戻ったので印を外した


def _mark(k, extra=None):
    if extra and k in extra:
        return pytest.param(k, marks=pytest.mark.xfail(strict=True, reason=extra[k]))
    return k


@pytest.mark.parametrize("dish", [_mark(k) for k in DISH_RECIPES_TIMED])
def test_correct_recipe_timed(dish):
    # 期待する答えはレシピの expected（2026-10-22: 蒸し卵は状態で固ゆで卵と区別できないので expected が hard_boiled_egg）
    _check(DISH_RECIPES_TIMED[dish], DISH_RECIPES_TIMED[dish].expected or dish)


@pytest.mark.parametrize("dish", [_mark(k, {"sauteed_onion": ONION_UNTIL}) for k in DISH_RECIPES])
def test_correct_recipe_until(dish):
    _check(DISH_RECIPES[dish], DISH_RECIPES[dish].expected or dish)
