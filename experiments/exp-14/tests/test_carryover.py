"""余熱（2026-09-28 夜、rules.md §10「余熱」）: 殻付き卵を取り出した後も球の熱伝導の解を続ける。

- 空気: 表面から周りへの熱の流れが温度差に比例する条件（Bi_air）。水・蒸気: 表面＝媒体温度（今までどおり）
- 後の操作: rest（置く）・plunge（水に取る）・off_heat（湯に入れたまま火を止める）
"""
import math

import pytest

from sim import State, ops, params as P
from sim.physics import _robin_roots, _sphere_consts
from sim.recipes import AFTER_MIN
from sim.state import EGG_SHELL


def _shell(T0=20):
    return State.from_ingredients({"egg_whole": 60}, T0=T0, egg_form=EGG_SHELL)


def _bi():
    return P.H("heat_transfer")["egg_sphere"]["Bi_air"]["value"]


def test_robin_roots_solve_the_equation():
    for bi in (0.25, 0.5, 1.25, 5.0):
        for n, k in enumerate(_robin_roots(bi, 60), start=1):
            assert (n - 1) * math.pi < k < n * math.pi
            assert abs(k * math.cos(k) - (1 - bi) * math.sin(k)) < 1e-9


def test_robin_uniform_expansion_is_one():
    """一様な分布 1 の展開係数 b_n を足すと、中心で 1 に近い（有限項の打ち切り）。"""
    b, w, lam, ks = _sphere_consts(_bi())
    assert sum(b) == pytest.approx(1.0, abs=0.05)
    assert sum(bi * wi for bi, wi in zip(b, w)) == pytest.approx(1.0, abs=1e-3)


def _robin_exact_center(T0, Tm, t, bi, M=2000):
    tau0 = P.H("heat_transfer")["egg_sphere"]["R2_over_alpha_min"]["value"]
    tot = 0.0
    for k in _robin_roots(bi, M):
        bn = k * (math.sin(k) / k ** 2 - math.cos(k) / k) / (0.5 - math.sin(2 * k) / (4 * k))
        tot += bn * math.exp(-k * k * t / tau0)
    return Tm + (T0 - Tm) * tot


def test_air_matches_direct_robin_solution(stage_model):
    """冷蔵庫の卵（5℃）を室温 20℃に置く: 刻んで計算した中心が、直接の解（2000 項）と合う。"""
    s = ops.rest(_shell(5), T=20, time=30)
    assert s.T_core == pytest.approx(_robin_exact_center(5, 20, 30, _bi(), M=400), abs=0.05)


def test_switch_matches_finite_difference(stage_model):
    """湯→空気・湯→氷水で境界条件が変わるときの射影し直しが正しいか。独立に解いた差分法（半径 400 分割の陽解法、
    2026-09-28 夜に scratch で計算）の値と比べる: 沸騰 12分→室温に 15分で中心の最高 88.393℃・終わり 79.269℃、
    沸騰 12分→氷水に 15分で 83.702℃・15.344℃。"""
    s = ops.simmer(_shell(), T=100, time=12, form="shell")
    air = ops.rest(s, T=20, time=15)
    assert air.T_core_max == pytest.approx(88.393, abs=0.02) and air.T_core == pytest.approx(79.269, abs=0.02)
    ice = ops.plunge(s, T=0, time=15)
    assert ice.T_core_max == pytest.approx(83.702, abs=0.02) and ice.T_core == pytest.approx(15.344, abs=0.02)


@pytest.mark.parametrize("after", [("rest", {"T": 20}), ("plunge", {"T": 0}), ("plunge", {"T": 15})])
def test_core_keeps_rising_after_removal_and_peaks_within_after_min(after):
    """沸騰 12分で取り出すと、中心はその後も上がる（余熱）。最高は後の操作の長さ（15分）の中に入る。"""
    s = ops.simmer(_shell(), T=100, time=12, form="shell")
    name, kw = after
    t = ops.OPS[name](s, time=AFTER_MIN, **kw)
    assert t.T_core_max > s.T_core_max + 1
    assert t.T_core < t.T_core_max  # 最後は下がっている＝最高は過ぎた
    longer = ops.OPS[name](s, time=AFTER_MIN * 2, **kw)
    assert longer.T_core_max == pytest.approx(t.T_core_max, abs=1e-9)


def test_ice_stops_carryover_more_than_air():
    s = ops.simmer(_shell(), T=100, time=12, form="shell")
    air = ops.rest(s, T=20, time=AFTER_MIN)
    ice = ops.plunge(s, T=0, time=AFTER_MIN)
    assert ice.T_core_max < air.T_core_max
    assert ice.T_core < air.T_core


def test_water_heating_unchanged_by_carryover_change(stage_model):
    """湯の中の計算（表面＝媒体温度）は余熱の前と同じ（Q6 (a) の値: 沸騰 12分で中心 77.47℃）。"""
    s = ops.simmer(_shell(), T=100, time=12, form="shell")
    assert s.T_core == pytest.approx(77.47, abs=0.01)


def test_off_heat_water_cools():
    """湯に入れたまま火を止めると、火を止めない場合より中心が上がらない。"""
    on = ops.simmer(_shell(), T=100, time=10, form="shell")
    off = ops.off_heat(_shell(), T=100, time=10)
    assert off.T_core_max < on.T_core_max
    assert off.ops[-1].startswith("off_heat(")
