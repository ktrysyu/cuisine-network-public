"""殻付き卵の既定の計算（2026-09-30 から kinetic、Exp-17）。

値は experiments/exp-17-egg-kinetics/results/output.md（切り替える前に kinetic を並べて出した結果）と同じ。
stage（Exp-14 の形）の計算そのものを確かめるテストは、conftest.py の stage_model で固定している。
"""
import pytest

from run import NO_MATCH_BELOW
from sim import DISH_RECIPES, egg_kinetic as EK, verdict
from sim.recipes import AFTER_ICE, Recipe
from sim.state import EGG_SHELL


def _boil_then_ice(t):
    r = Recipe("t", {"egg_whole": 60}, [("simmer", {"T": 100, "time": t, "form": "shell"}), AFTER_ICE], egg_form=EGG_SHELL)
    return r.run()


def test_default_is_kinetic():
    assert EK.model() == "kinetic"
    assert DISH_RECIPES["soft_boiled_egg"].run().egg_kin is not None


def test_tatsu2019_without_fitting():
    """20℃の卵を 68℃の湯に入れて中心が 67℃に達するのは 28.4分（tatsu2019 約28分）。合わせ込みなし。"""
    g = EK.EggGrid(60.0, 20.0)
    t = 0.0
    while g.T_center < 67.0:
        g.step(68.0, 0.1)
        t += 0.1
    assert t == pytest.approx(28.4, abs=0.15)


@pytest.mark.parametrize("t,answer", [(5, None), (6, "soft_boiled_egg"), (6.5, "soft_boiled_egg"), (8, None), (11, "hard_boiled_egg")])
def test_boil_then_ice(t, answer):
    """沸騰した湯 → 氷水: 半熟ゆで卵は 6〜6.5分、11分から固ゆで（Exp-17 の結果）。"""
    assert verdict(_boil_then_ice(t), NO_MATCH_BELOW).answer == answer


def test_white_sets_from_outside():
    """白身は外側から固まる: 固まった割合が時間とともに増える。"""
    gs = [_boil_then_ice(t).egg_kin.layer_stats("white")[0] for t in (1, 3, 5)]
    assert gs[0] < gs[1] < gs[2] < 1.0
