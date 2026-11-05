"""判定: 必須条件で候補から外す・「該当なし」を返す。"""
import run
from sim import NO_MATCH, State, candidates, ops, rank, verdict
from sim.state import EGG_SHELL


def test_threshold_is_a_constant_in_run():
    assert isinstance(run.NO_MATCH_BELOW, float) and 0 < run.NO_MATCH_BELOW < 1


def test_raw_beaten_egg_is_no_match_but_keeps_breakdown():
    """加熱していない溶き卵 → 該当なし。内訳は返す。
    2026-09-27 は候補の1位が 0.6 に届かなかった。2026-09-28 から形（小片・外側連続…）が必須なので候補が無く、
    内訳は外した料理（excluded）に残る。"""
    s = ops.whisk(State.from_ingredients({"egg_whole": 100}), time=1)
    v = verdict(s, run.NO_MATCH_BELOW)
    assert v.no_match and v.answer is None and v.ja == NO_MATCH
    assert v.top is None or v.top.fraction < run.NO_MATCH_BELOW
    for r in v.candidates + v.excluded:
        assert len(r.met) + len(r.unmet) == r.n_total
    assert {"scrambled_eggs", "omelet"} <= {r.dish for r in v.excluded}


def test_no_match_when_threshold_is_above_top():
    s = ops.whisk(State.from_ingredients({"egg_whole": 100}), time=1)
    s = ops.bake(s, T=110, time=1.75, stirring=True, form="thin")
    top = verdict(s, 0.0).top
    assert verdict(s, top.fraction).answer == top.dish          # 下限ちょうどは該当
    assert verdict(s, top.fraction + 1e-9).no_match             # 下限を上回れば該当なし


def test_required_failing_dishes_are_excluded():
    s = ops.whisk(State.from_ingredients({"egg_whole": 100}), time=1)
    v = verdict(s, run.NO_MATCH_BELOW)
    assert all(r.required_ok for r in candidates(s))
    assert all(r.required_ok for r in rank(s, 20))
    assert "custard_pudding" in {r.dish for r in v.excluded}    # 牛乳・砂糖が無い


def test_shell_is_required_for_onsen_and_boiled_egg():
    """割った卵を 68℃の湯で30分: 温泉卵・ゆで卵は候補に入らない（殻付きが必須）。"""
    cracked = ops.simmer(State.from_ingredients({"egg_whole": 60}), T=68, time=30, form="cup")
    shell = ops.simmer(State.from_ingredients({"egg_whole": 60}, egg_form=EGG_SHELL), T=68, time=30, form="shell")
    excluded = {r.dish for r in verdict(cracked, run.NO_MATCH_BELOW).excluded}
    assert {"onsen_tamago", "hard_boiled_egg"} <= excluded
    assert verdict(shell, run.NO_MATCH_BELOW).answer == "onsen_tamago"
