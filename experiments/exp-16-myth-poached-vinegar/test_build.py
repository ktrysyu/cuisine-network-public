"""writeup/myth-poached-vinegar.html が今の build.py・シミュレータ・recipes.csv から作ったものと同じか。

    uv run pytest experiments/exp-16-myth-poached-vinegar
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build as B  # noqa: E402


def test_page_is_fresh():
    assert B.OUT.read_text(encoding="utf-8") == B.page()


def test_vinegar_changes_only_cohesion():
    """計算で酢が変えるのは卵白のまとまりだけ（判定の1位は変わらない）。ページの所見の前提。"""
    d = B.compute()["diff"]
    assert d["cls"] == 0
    assert set(d["state"]) == {"egg_white_cohesion"}
