"""操作と規則の単体テスト。"""
import pytest

from sim import State, ops, params
from sim.judge import evaluate


def test_ops_are_pure():
    s0 = State.from_ingredients({"egg_whole": 100, "milk": 20})
    before = s0.summary(), dict(s0.masses), len(s0.history)
    s1 = ops.bake(ops.whisk(s0, time=1), T=110, time=2, stirring=True, form="thin")
    assert (s0.summary(), dict(s0.masses), len(s0.history)) == before
    assert s1 is not s0 and s1.T_core_max > s0.T_core_max


def test_wet_heat_caps_at_boiling_and_no_browning():
    """R-W01・R-W02・R-M02: 蒸す・煮るでは 100℃を超えず、焼き色が付かない。"""
    s = State.from_ingredients({"chicken": 200})
    s = ops.simmer(s, T=100, time=60, form="piece")
    assert s.T_core_max <= 100 and s.T_surface_max <= 100
    assert s.maillard == 0


def test_pan_dries_surface_and_browns():
    s = ops.bake(State.from_ingredients({"chicken": 200}), T=180, time=10, form="piece")
    assert s.T_surface_max > 140 and s.maillard >= 2
    assert s.T_core_max <= 100  # R-F01 と同じく中心は沸点を超えない


def test_rice_needs_holding_time():
    """R-S04: 98℃以上で20分に満たないと完全には糊化しない（到達温度だけでは決まらない）。"""
    base = ops.soak(State.from_ingredients({"rice": 150, "water": 210}), T=25, time=30)
    short = ops.simmer(base, T=100, time=15, lid=True, form="pot")
    long = ops.simmer(base, T=100, time=35, lid=True, form="pot")
    assert short.T_core_max >= 98 and long.T_core_max >= 98
    assert short.starch_gel < 0.9 <= long.starch_gel


def test_dilution_raises_egg_set_temperature():
    """R-E07 と R-E09: 同じ 76℃ でも、薄めない卵は固まり、牛乳で薄めた卵液は固まらない。"""
    def cook(ing):
        s = ops.whisk(State.from_ingredients(ing), time=1)
        return ops.heat(s, "water", 76, 60, form="cup")
    assert cook({"egg_whole": 100}).egg_gel_stage >= 2
    assert cook({"egg_whole": 100, "milk": 250}).egg_gel_stage == 0


def test_adopted_values_have_alternatives_recorded():
    av = params.rules()["sim"]["adopted_values"]
    for k in ("egg_white_s1", "egg_undiluted_s2", "sucrose_caramel_T", "rice_gel_onset", "egg_diluted_s2"):
        assert av[k].get("alternatives"), k


def test_judge_returns_met_and_unmet():
    s = ops.whisk(State.from_ingredients({"egg_whole": 100}), time=1)
    res = evaluate(s)
    for r in res:
        assert len(r.met) + len(r.unmet) == len(params.dishes()[r.dish]["conditions"])
    # 必須条件（食材）を満たさない料理は、満たす料理より下
    flags = [r.required_ok for r in res]
    assert flags == sorted(flags, reverse=True)


# ---- 「〜になるまで」加熱（until）----
def _beaten():
    return ops.whisk(State.from_ingredients({"egg_whole": 100}), time=1)


def test_until_stops_when_condition_is_reached():
    s = ops.bake(_beaten(), T=110, stirring=True, form="thin",
                 until={"var": "egg_gel_stage", "ge": 2}, max_time=10)
    st = s.stops[-1]
    assert st["reached"] and 0 < st["minutes"] < 10
    assert s.egg_gel_stage >= 2
    # 止めた刻みの1つ前までは満たしていない（最初に満たした刻みで止まる）
    dt = params.H("run", "dt_min")
    before = ops.bake(_beaten(), T=110, time=round(st["minutes"] - dt, 6), stirring=True, form="thin")
    assert (before.egg_gel_stage or 0) < 2


def test_until_reports_when_not_reached():
    """60℃の湯では溶き卵は段階2（73℃）に届かない → 上限で止め、未到達を返す。"""
    s = ops.heat(_beaten(), "water", 60, until={"var": "egg_gel_stage", "ge": 2}, max_time=5, form="cup")
    st = s.stops[-1]
    assert not st["reached"] and st["minutes"] == pytest.approx(5)
    assert "未到達" in s.ops[-1] and any("到達しなかった" in t for t in s.trace)


def test_until_already_met_takes_no_time():
    s = ops.bake(_beaten(), T=110, stirring=True, form="thin", until={"var": "egg_gel_stage", "ge": 2}, max_time=10)
    s2 = ops.bake(s, T=110, form="thin", until={"var": "egg_gel_stage", "ge": 2}, max_time=10)
    assert s2.stops[-1]["reached"] and s2.stops[-1]["minutes"] == 0
    assert len(s2.history) == len(s.history)


def test_until_with_category_and_temperature():
    s = ops.heat(State.from_ingredients({"chicken": 200}), "pan", 180,
                 until={"var": "T_core", "ge": 74}, max_time=20, form="piece")
    assert s.stops[-1]["reached"] and s.T_core >= 74


def test_until_argument_errors():
    b = _beaten()
    with pytest.raises(ValueError):
        ops.bake(b, T=110)                                                   # time も until も無い
    with pytest.raises(ValueError):
        ops.bake(b, T=110, until={"var": "egg_gel_stage", "ge": 2})           # 上限が無い
    with pytest.raises(ValueError):
        ops.bake(b, T=110, time=1, until={"var": "egg_gel_stage", "ge": 2}, max_time=5)
    with pytest.raises(ValueError):
        ops.bake(b, T=110, time=1, max_time=5)


def test_timed_heat_is_unchanged():
    s = ops.bake(_beaten(), T=110, time=1.75, stirring=True, form="thin")
    assert s.stops == [] and "until" not in s.ops[-1]
