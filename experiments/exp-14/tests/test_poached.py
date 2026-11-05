"""ポーチドエッグ（14品目、2026-09-27）: 正解のレシピで1位になるか・卵白のまとまりの規則・既存の結果が変わらないか。"""
import json
from pathlib import Path

import pytest

from run import NO_MATCH_BELOW
from sim import DISH_RECIPES, DISH_RECIPES_TIMED, PAIRS, State, ops, verdict
from sim.state import COH_COHESIVE, COH_FILM, COH_SCATTER, EGG_CRACKED, EGG_SHELL

BEFORE = Path(__file__).resolve().parent / "data" / "before_poached.json"


def _egg(form=EGG_CRACKED):
    return State.from_ingredients({"egg_whole": 60}, egg_form=form)


def test_correct_recipe_is_poached_egg_with_all_conditions():
    v = verdict(DISH_RECIPES["poached_egg"].run(), NO_MATCH_BELOW)
    assert v.answer == "poached_egg"
    assert v.top.fraction == 1.0


def test_white_set_yolk_runny():
    s = DISH_RECIPES["poached_egg"].run()
    assert s.egg_white_stage == 3 and s.egg_yolk_stage == 0 and s.T_core_max < 65


@pytest.mark.parametrize("T,vin,salt,want", [
    (85, 0, 0, COH_COHESIVE), (100, 0, 0, COH_SCATTER), (100, 3, 0, COH_FILM), (85, 0, 1, COH_FILM),
    (70, 0, 0, COH_SCATTER), (70, 3, 0, COH_SCATTER), (120, 0, 0, COH_SCATTER)])
def test_cohesion_rule(T, vin, salt, want):
    assert ops.poach(_egg(), T=T, time=3, vinegar_pct=vin, salt_pct=salt).egg_white_cohesion == want


def test_cohesion_only_for_cracked_egg():
    assert ops.poach(_egg(EGG_SHELL), T=85, time=3).egg_white_cohesion is None
    beaten = ops.whisk(_egg(), time=1)
    assert ops.poach(beaten, T=85, time=3).egg_white_cohesion is None


def test_poach_is_simmer_with_drop_form():
    """poach は形 drop の煮る と温度が同じ（まとまり以外）。"""
    a = ops.poach(_egg(), T=85, time=4)
    b = ops.simmer(_egg(), T=85, time=4, form="drop")
    assert (a.T_core, a.T_surface, a.egg_white_stage, a.egg_yolk_stage) == (b.T_core, b.T_surface, b.egg_white_stage, b.egg_yolk_stage)


def test_shell_egg_white_still_uses_core(stage_model):
    """温泉卵 68℃30分で卵白 2。2026-09-28 の修正 B から殻付き卵の卵白は卵白の層の温度で決める
    （関数名は変更前のまま残した。卵白の層でも 68℃の湯では 2 のまま。tests/test_shell_layers.py）。"""
    s = DISH_RECIPES["onsen_tamago"].run()
    assert s.egg_white_stage == 2


def _cases():
    cases = [(f"until:{k}", r) for k, r in DISH_RECIPES.items()]
    cases += [(f"timed:{k}", r) for k, r in DISH_RECIPES_TIMED.items()]
    for i, p in enumerate(PAIRS, 1):
        cases += [(f"pair{i}:a", p.a), (f"pair{i}:b", p.b)]
    return dict(cases)


# 2026-09-28 の定義上の必須条件で答えが変わった入力（変更前 → 今）。これ以外は変わらない
CHANGED_BY_DEFINITION = {"pair6:b": ("milk_jelly", None)}
# 2026-09-28 夜 Q6 (a): 殻付き卵の温度を球の熱伝導の解に置き換えた（rules.md §10）。殻付き卵の入力は状態（中心・卵白の層の
# 温度と段階）が変わるので、状態・候補の比較から外し、答えだけ見る。答えが変わったのは固ゆで卵の正解のレシピ（沸騰12分で
# 中心 77℃・卵黄 2、固ゆでの必須「卵黄 3」に届かない）
# 同じ夜に余熱（殻付き卵に後の手順「室温に置く」など、rules.md §10）を入れて、固ゆで卵は変更前と同じ答えに戻った
CHANGED_BY_Q6: dict = {}


def test_existing_results_unchanged():
    """変更前（cc45069 の直前）の42入力と比べる。
    - 各操作の後の状態・停止条件はすべて同じ（ポーチドエッグ・必須条件の見直しは状態の計算を変えない）
    - 答えは CHANGED_BY_DEFINITION の入力を除いて同じ
    - 候補は、変更前の候補から「今の必須条件を満たさない料理」を除いたものと同じ（順・満たした数も同じ）"""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "js"))
    from export_data import snapshot
    before = json.loads(BEFORE.read_text(encoding="utf-8"))
    cases = _cases()
    assert len(before) == 42
    for b in before:
        r = cases[b["id"]]
        shell = r.egg_form == EGG_SHELL
        s = r.initial()
        for i, (name, kw) in enumerate(r.steps):
            s = ops.OPS[name](s, **kw)
            now = snapshot(s)
            if not shell:
                assert {k: now[k] for k in b["steps"][i]} == b["steps"][i], (b["id"], i)
            assert now.get("egg_white_cohesion") is None, b["id"]
        v = verdict(s, NO_MATCH_BELOW)
        assert s.stops == b["stops"], b["id"]
        changed = {**CHANGED_BY_DEFINITION, **CHANGED_BY_Q6}
        want = changed[b["id"]] if b["id"] in changed else (b["answer"], b["answer"])
        assert (b["answer"], v.answer) == want, b["id"]
        if shell:
            continue
        now = [[c.dish, len(c.met), c.n_total] for c in v.candidates if c.dish != "poached_egg"]
        keep = {c[0] for c in now}
        assert now == [c for c in b["candidates"] if c[0] in keep], b["id"]
        assert set(b["excluded"]) <= {c.dish for c in v.excluded}, b["id"]
