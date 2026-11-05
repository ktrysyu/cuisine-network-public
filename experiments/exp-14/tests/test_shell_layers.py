"""修正 B（2026-09-28）: 殻付き卵は卵白＝卵白の層の温度、卵黄＝中心の温度。半熟ゆで卵（soft_boiled_egg）。

rules.md §10「2026-09-28 修正 B」。時定数・料理の条件は結果を見る前に決めた。
"""
import pytest

from run import NO_MATCH_BELOW
from sim import DISH_RECIPES, State, ops, params as P, verdict
from sim.state import EGG_BEATEN, EGG_CRACKED, EGG_SHELL


def _shell():
    return State.from_ingredients({"egg_whole": 60}, egg_form=EGG_SHELL)


def test_white_layer_only_for_shell_egg():
    assert _shell().T_white == 20
    assert State.from_ingredients({"egg_whole": 60}, egg_form=EGG_CRACKED).T_white is None
    beaten = ops.whisk(State.from_ingredients({"egg_whole": 60}), time=1)
    assert beaten.egg_form == EGG_BEATEN and beaten.T_white is None


def _sphere_exact(T0, Tm, t, r_lo=0.0):
    """一様な球（表面＝Tm）の解を、刻まずに直接（2000 項）。r_lo=0 なら中心、>0 なら半径 r_lo〜1 の体積平均。"""
    import math
    sp = P.H("heat_transfer")["egg_sphere"]
    tau0 = sp["R2_over_alpha_min"]["value"]
    tot = 0.0
    for n in range(1, 2001):
        k = n * math.pi
        bn = 2.0 * (-1) ** (n + 1)
        if r_lo == 0:
            wn = 1.0
        else:
            F = lambda r: math.sin(k * r) / k ** 2 - r * math.cos(k * r) / k  # noqa: E731
            wn = 3.0 / ((1.0 - r_lo ** 3) * k) * (F(1.0) - F(r_lo))
        tot += bn * wn * math.exp(-k * k * t / tau0)
    return Tm + (T0 - Tm) * tot


def test_white_layer_heats_faster_than_core(stage_model):
    """Q6 (a)（2026-09-28 夜）から殻付き卵は球の熱伝導の解。刻んで計算した値が、直接の解と合う。"""
    s = ops.simmer(_shell(), T=100, time=3, form="shell")
    assert s.T_core < s.T_white < s.T_surface == 100
    a = P.H("heat_transfer")["egg_sphere"]["yolk_volume_fraction"]["value"] ** (1 / 3)
    assert s.T_white == pytest.approx(_sphere_exact(20, 100, 3, a), abs=0.05)
    assert s.T_core == pytest.approx(_sphere_exact(20, 100, 3), abs=0.05)


def test_sphere_matches_tatsu2019():
    """R²/α の根拠（tatsu2019）: 20℃の卵を 68℃の湯に 28分で、中心が 1℃以内。"""
    s = ops.simmer(_shell(), T=68, time=28, form="shell")
    assert 66.9 <= s.T_core <= 67.1


def test_white_stage_follows_white_layer_yolk_follows_core(stage_model):
    """Q6 (a) の後は沸騰 6.5分の中心は 47℃ 前後（前は一次遅れで 67.6℃・卵黄 1）。卵黄は 0。"""
    s = ops.simmer(_shell(), T=100, time=6.5, form="shell")
    assert s.T_white_max >= P.V("egg_white_s3") > s.T_core_max
    assert s.egg_white_stage == 3 and s.egg_yolk_stage == 0


def test_white_layer_hold_is_recorded():
    s = ops.simmer(_shell(), T=68, time=30, form="shell")
    assert s.hold("white", "ge", 65) > s.hold("core", "ge", 65) > 0
    assert State.from_ingredients({"egg_whole": 60}, egg_form=EGG_CRACKED).hold("white", "ge", 0) == 0


def test_onsen_unchanged():
    assert verdict(DISH_RECIPES["onsen_tamago"].run(), NO_MATCH_BELOW).answer == "onsen_tamago"


# 2026-09-28 夜 Q6 (a) で xfail（沸騰12分の中心 77℃・卵黄 2）。余熱（室温に置く）を入れて固ゆでに戻ったので印を外した
def test_hard_boiled_unchanged():
    assert verdict(DISH_RECIPES["hard_boiled_egg"].run(), NO_MATCH_BELOW).answer == "hard_boiled_egg"


def test_soft_boiled_correct_recipe():
    s = DISH_RECIPES["soft_boiled_egg"].run()
    v = verdict(s, NO_MATCH_BELOW)
    assert v.answer == "soft_boiled_egg" and v.top.fraction == 1.0
    assert "onsen_tamago" in {r.dish for r in v.excluded}


@pytest.mark.parametrize("t", [6, 6.5, 7])
def test_boiling_6_to_7_min_is_not_onsen(t):
    """きっかけ（Exp-15 の半熟ゆで卵）: 沸騰した湯で6〜7分は温泉卵ではない。"""
    s = ops.simmer(_shell(), T=100, time=t, form="shell")
    assert verdict(s, NO_MATCH_BELOW).answer == "soft_boiled_egg"
