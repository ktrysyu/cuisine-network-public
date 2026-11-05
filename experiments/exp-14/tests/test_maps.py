"""地図（sim/maps.py）: 軸の値・レシピの書き換え・マスの分類。"""
from run import NO_MATCH_BELOW
from sim import maps


def test_values_include_both_ends():
    assert maps.values(50, 100, 2.5)[0] == 50 and maps.values(50, 100, 2.5)[-1] == 100
    assert len(maps.values(1, 60, 2)) == 30 and maps.values(1, 60, 2)[-1] == 59


def test_with_value_does_not_touch_base():
    base = maps.base_recipe("timed:onsen_tamago")
    r = maps.with_value(base, {"kind": "step", "i": 0, "key": "T"}, 100)
    assert r["steps"][0][1]["T"] == 100 and base["steps"][0][1]["T"] == 68


def test_cell_of_base_recipe_is_its_dish():
    for p in maps.PRESETS:
        base = maps.base_recipe(p["base"])
        c = maps.cell(base, NO_MATCH_BELOW)
        assert c["cls"] == base["expected"], p["id"]


def test_raw_and_none_are_separated():
    base = maps.base_recipe("timed:onsen_tamago")
    cold = maps.with_value(maps.with_value(base, {"kind": "step", "i": 0, "key": "T"}, 50),
                           {"kind": "step", "i": 0, "key": "time"}, 1)
    assert maps.cell(cold, NO_MATCH_BELOW)["cls"] == maps.RAW


def test_presets_axes_exist_in_base():
    for p in maps.PRESETS:
        base = maps.base_recipe(p["base"])
        for ax in (p["x"]["axis"], p["y"]["axis"]):
            assert ax["key"] in base["steps"][ax["i"]][1], (p["id"], ax)
