"""Exp-18: 肉片を厚み方向の熱伝導で解く形（meat_model = slab）と、揚げ物の吸油（oil_uptake）。"""
from sim import meat_slab as MS
from sim import ops, params
from sim.state import State


def test_default_is_tau_and_oil_off():
    assert MS.model() == "tau"
    assert params.H("oil_uptake", "enabled") is False
    s = ops.deep_fry(State.from_ingredients({"potato": 100}), T=170, time=6, form="thin")
    assert "vegetable_oil" not in s.masses


def test_props_within_measured_range():
    """牛肉の k・熱拡散率が ASHRAE の実測（牛赤身 k 0.40〜0.51、熱拡散率 1.2〜1.3×10⁻⁷）の近く。"""
    k, rho, cp = MS.mix_props(MS.mass_fractions({"beef": 100}), 40)
    assert 0.40 <= k <= 0.51
    assert 1.1e-7 <= k / rho / cp <= 1.45e-7


def test_slab_center_stays_below_boiling_and_flips():
    MS.set_model("slab")
    try:
        s = State.from_ingredients({"beef": 250}, thickness_mm=20)
        for _ in range(4):
            s = ops.bake(s, T=175, time=1.5, form="piece")
        assert max(s.meat_slab.T) <= 100.0 + 1e-9
        assert 50 < s.T_core < 75
        assert s.meat_slab.flips == 3
        s2 = ops.bake(s, T=130, time=1, form="piece", flip=False)
        assert s2.meat_slab.flips == 3
    finally:
        MS.set_model(None)


def test_oil_uptake_is_proportional_to_water_lost():
    node = params.rules()["sim"]["oil_uptake"]["enabled"]
    node["value"] = True
    try:
        s = ops.deep_fry(State.from_ingredients({"potato": 100}), T=170, time=6, form="thin")
        assert abs(s.masses["vegetable_oil"] - params.H("oil_uptake", "ratio") * s.water_lost) < 1e-6
    finally:
        node["value"] = False
