import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


import pytest  # noqa: E402


@pytest.fixture
def stage_model():
    """殻付き卵を Exp-14 の形（stage: 一様な球の固有関数の解＋温度のしきい値）で計算する。
    2026-09-30 に既定を kinetic（Exp-17）に切り替えたので、stage の計算そのものを確かめるテストはこれで固定する。"""
    from sim import egg_kinetic as EK
    EK.set_model("stage")
    yield
    EK.set_model(None)
