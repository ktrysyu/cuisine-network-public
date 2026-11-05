"""JavaScript 版のための書き出し。

    uv run python experiments/exp-14/js/export_data.py

- js/sim_data.json: rules.yaml のうちシミュレータが使う部分（食材の成分・採用値・料理の条件・段階の名前）、
  perception_model.json、レシピ（13品の両版＋順番を変えた7組）。ページ（writeup/cook-lab.html）に埋め込む
- js/expected.json: Python 版の計算結果（JS 版との一致テスト test_parity.js が読む）
- js/expected_maps.json: 最初から用意した地図4枚を粗い刻み（MAP_COARSEN 倍）で Python 版（sim/maps.py）で描いた結果
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
sys.path.insert(0, str(EXP))

import perception as PC  # noqa: E402
from run import NO_MATCH_BELOW  # noqa: E402
from sim import DISH_RECIPES, DISH_RECIPES_TIMED, PAIRS, maps, ops, params as P, verdict  # noqa: E402
from sim import egg_kinetic as EK  # noqa: E402

MAP_COARSEN = 4  # 一致テストの地図は刻みを4倍に粗くする

# 一致を確かめる状態変数（State.summary と同じ並び＋中心・表面の温度・糖濃度の倍率）
KEYS = ["T_core", "T_surface", "T_core_max", "T_surface_max", "T_white", "T_white_max", "T_serve", "water", "fat", "protein", "sugar_conc",
        "sugar_conc_ratio", "salt_conc", "mass_ratio", "egg_form", "egg_dilution", "egg_white_stage", "egg_yolk_stage",
        "egg_gel_stage", "egg_gel_stage_surface", "gel_structure", "porosity", "milk_whey_denatured", "milk_casein",
        "fat_phase", "starch_gel", "starch_retro", "gluten", "gluten_relaxed", "co2", "maillard", "caramel",
        "syrup_stage", "onion_sulfur", "cell_wall", "meat_myosin", "meat_actin", "meat_collagen", "meat_myoglobin",
        "meat_water_loss", "gelatin_state", "gelatin_conc", "foam_stage", "T_whisk", "air", "egg_white_cohesion"]


def recipe_json(r) -> dict:
    return {"name": r.name, "ingredients": r.ingredients, "steps": [[n, kw] for n, kw in r.steps],
            "T0": r.T0, "egg_form": r.egg_form, "form": r.form, "expected": r.expected}


def egg_kinetic_data(ek) -> dict:
    """殻付き卵の熱伝導＋変性（Exp-17、sim/egg_kinetic.py）の値。A は YAML で文字列になるので数にする。"""
    layer = lambda c: {k: float(c[k]) for k in ("k_a", "k_b", "rho_a", "rho_b", "rho_c", "cp", "A", "Ea")}
    return {"yolk": layer(ek["yolk"]), "white": layer(ek["white"]),
            "yolk_volume_fraction": ek["yolk_volume_fraction"]["value"], "nodes": ek["nodes"]["value"],
            "h_air": ek["h_air"]["value"], "sub_s": ek["sub_s"]["value"], "R_gas": EK.R_GAS,
            "stage_map": {k: v["value"] for k, v in ek["stage_map"].items()}}


def data() -> dict:
    R = P.rules()
    sim = R["sim"]
    ht = sim["heat_transfer"]

    def vals(node):
        return {k: v["value"] for k, v in node.items()}

    levels = {k: v.get("levels") for k, v in R["state_variables"].items() if v.get("levels") is not None}
    levels["egg_form"] = sim["added_state_variables"]["egg_form"]["levels"]
    levels["meat_water_loss"] = sim["added_state_variables"]["meat_water_loss"]["levels"]
    levels["egg_white_cohesion"] = sim["added_state_variables"]["egg_white_cohesion"]["levels"]
    return {
        "about": "Exp-14 のシミュレータが使う rules.yaml の一部と、状態→感じ方の変換。export_data.py が生成。",
        "no_match_below": NO_MATCH_BELOW,
        "ingredients": {k: {"ja": v["ja"], "comp": P.composition(k)} for k, v in R["ingredients"].items()},
        "split": sim["composition_split"],
        "run": {k: sim["run"][k]["value"] for k in ("dt_min", "T0_default", "boiling_point_water")},
        "heat_transfer": {
            "tau_min": vals(ht["tau_min"]), "air_tau_factor": ht["air_tau_factor"]["value"],
            "surface_wet_min": vals(ht["surface_wet_min"]), "tau_surface_min": ht["tau_surface_min"]["value"],
            "tau_white_layer_min": ht["tau_white_layer_min"]["value"],
            "pot_cooling_tau_min": ht["pot_cooling_tau_min"]["value"],
            "egg_sphere": vals(ht["egg_sphere"]),
            "evaporation_pct_per_min": vals(ht["evaporation_pct_per_min"]),
        },
        "egg_model": sim["egg_model"]["value"],
        "egg_kinetic": egg_kinetic_data(sim["egg_kinetic"]),
        "adopted": {k: v["value"] for k, v in sim["adopted_values"].items()},
        "levels": levels,
        "var_ja": {**{k: v.get("ja") for k, v in R["state_variables"].items()},
                   **{k: v.get("ja") for k, v in sim["added_state_variables"].items()}},
        "dishes": R["dish_conditions"],
        "perception": json.loads((EXP / "perception_model.json").read_text(encoding="utf-8")),
        "recipes": {
            "until": {k: recipe_json(r) for k, r in DISH_RECIPES.items()},
            "timed": {k: recipe_json(r) for k, r in DISH_RECIPES_TIMED.items()},
            "pairs": [{"title": p.title, "a": recipe_json(p.a), "b": recipe_json(p.b)} for p in PAIRS],
            "extra": {k: recipe_json(r) for k, r in EXTRA.items()},
        },
        "maps": [{**p, "base_recipe": maps.base_recipe(p["base"])} for p in maps.PRESETS],
    }


# 正解のレシピ・組に無い入力で、ポーチ（酢・塩・沸騰・低温）と割った卵の卵白の扱いを確かめる（2026-09-27）
def _extra():
    from sim.recipes import Recipe
    from sim.state import EGG_CRACKED, EGG_SHELL
    e = {"egg_whole": 60}
    return {
        "poach_100_vinegar": Recipe("沸騰した湯＋酢3%に落として3分", e, [("poach", {"T": 100, "time": 3, "vinegar_pct": 3})], egg_form=EGG_CRACKED),
        "poach_100": Recipe("沸騰した湯に落として3分", e, [("poach", {"T": 100, "time": 3})], egg_form=EGG_CRACKED),
        "poach_70_salt": Recipe("70℃の湯＋塩1%に落として10分", e, [("poach", {"T": 70, "time": 10, "salt_pct": 1})], egg_form=EGG_CRACKED),
        "poach_until": Recipe("85℃の湯に落として中心60℃まで", e, [("poach", {"T": 85, "until": {"var": "T_core", "ge": 60}, "max_time": 20})], egg_form=EGG_CRACKED),
        "fried_cracked": Recipe("割った卵をフライパンで3分", e, [("bake", {"T": 170, "time": 3, "form": "thin"})], egg_form=EGG_CRACKED),
        # 余熱（2026-09-28 夜）: 境界条件の切り替え（空気→湯→空気→氷水）と、湯に入れたまま火を止める
        "shell_air_boil_rest_ice": Recipe("冷蔵の卵を室温に20分→沸騰9分→室温3分→氷水10分", e,
                                          [("rest", {"T": 20, "time": 20}), ("simmer", {"T": 100, "time": 9, "form": "shell"}),
                                           ("rest", {"T": 20, "time": 3}), ("plunge", {"T": 0, "time": 10})],
                                          T0=5, egg_form=EGG_SHELL),
        "shell_off_heat": Recipe("沸騰1分→火を止めて5分→冷水", e,
                                 [("simmer", {"T": 100, "time": 1, "form": "shell"}), ("off_heat", {"T": 100, "time": 5}),
                                  ("plunge", {"T": 15, "time": 15})], egg_form=EGG_SHELL),
    }


EXTRA = _extra()


def snapshot(s) -> dict:
    out = {}
    for k in KEYS:
        v = s.get(k)
        out[k] = v
    return out


def expected(models) -> list[dict]:
    cases = [(f"until:{k}", r) for k, r in DISH_RECIPES.items()]
    cases += [(f"timed:{k}", r) for k, r in DISH_RECIPES_TIMED.items()]
    for i, p in enumerate(PAIRS, 1):
        cases += [(f"pair{i}:a", p.a), (f"pair{i}:b", p.b)]
    cases += [(f"extra:{k}", r) for k, r in EXTRA.items()]
    out = []
    for cid, r in cases:
        s = r.initial()
        steps = []
        for name, kw in r.steps:
            s = ops.OPS[name](s, **kw)
            steps.append(snapshot(s))
        v = verdict(s, NO_MATCH_BELOW)
        pv = PC.perceive(models, s)
        out.append({
            "id": cid, "steps": steps, "stops": s.stops,
            "answer": v.answer,
            "candidates": [[c.dish, len(c.met), c.n_total] for c in v.candidates],
            "excluded": [c.dish for c in v.excluded],
            "perception": pv,
            "nearest": PC.nearest(pv, PC.load_labels()),
        })
    return out


def expected_maps() -> list[dict]:
    return [{"id": p["id"], "coarsen": MAP_COARSEN, **maps.preset_grid(p, NO_MATCH_BELOW, MAP_COARSEN)}
            for p in maps.PRESETS]


def main() -> None:
    d = data()
    (HERE / "sim_data.json").write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    models = {k: d["perception"]["items"][k] for k in PC.ITEMS}
    (HERE / "expected.json").write_text(json.dumps(expected(models), ensure_ascii=False) + "\n", encoding="utf-8")
    (HERE / "expected_maps.json").write_text(json.dumps(expected_maps(), ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", HERE / "sim_data.json", HERE / "expected.json", HERE / "expected_maps.json")


if __name__ == "__main__":
    main()
