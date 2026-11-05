"""data/labels/fat_content.csv が今の build_fat_content.py・SR Legacy から作ったものと同じか。生データが無ければ飛ばす。

    uv run pytest experiments/exp-11
"""
import csv
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_fat_content as B  # noqa: E402


@pytest.mark.skipif(not (B.FDC / "food.csv").exists(), reason="SR Legacy の生データが無い（data/SOURCES.md の手順で取り直す）")
def test_fat_content_is_fresh():
    rows, _ = B.build()
    with B.OUT.open(encoding="utf-8") as f:
        assert list(csv.DictReader(f)) == rows


def test_blank_rows_have_reasons():
    with B.OUT.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 303
    for r in rows:
        assert (r["fat_g_per_100g"] == "") == (r["match"] == "対応なし"), r["ingredient"]
        if r["match"] in ("対応なし", "代用"):
            assert r["note"], r["ingredient"]
