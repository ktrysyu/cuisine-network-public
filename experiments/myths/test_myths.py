"""通説ページが今の計算・データから作ったものと同じか。

    uv run pytest experiments/myths
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from myths.build import MYTHS, load  # noqa: E402


@pytest.mark.parametrize("mid", MYTHS)
def test_page_is_fresh(mid):
    m = load(mid)
    assert m.OUT.read_text(encoding="utf-8") == m.page()


def test_vinegar_changes_only_cohesion():
    """計算で酢が変えるのは卵白のまとまりだけ（判定の1位は変わらない）。通説1の所見の前提。"""
    d = load("poached_vinegar").compute()["diff"]
    assert d["cls"] == 0
    assert set(d["state"]) == {"egg_white_cohesion"}


def test_basis_pages_are_fresh():
    """規則・出典のページ（writeup/basis/）が今の rules.yaml・通説から作ったものと同じ。"""
    from myths import basis
    files = basis.built()
    assert files, "ページが無い"
    for p, text in files.items():
        assert p.read_text(encoding="utf-8") == text, p


def test_myth_order():
    """通説ページは 判定と確かさ → 決め手の図 → 言えないこと → 自分で試す の順で始まる（motivation.md §14）。"""
    import re
    for mid in MYTHS:
        ids = re.findall(r'<section id="([a-z-]+)">', load(mid).OUT.read_text(encoding="utf-8"))
        assert ids[:4] == ["verdict", "keyfig", "cannot", "try"], (mid, ids)
        assert ids[-1] == "basis"
