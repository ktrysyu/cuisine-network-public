"""通説ページを作る。

    uv run python experiments/myths/build.py            # 全部
    uv run python experiments/myths/build.py room_temp_egg

通説1本 = experiments/myths/<id>.py（データと計算、ID・OUT・page() を持つ）＋ common.py（共通テンプレート）。
新しい通説は MYTHS に足す。候補の一覧は candidates.md。
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

MYTHS = ["poached_vinegar", "room_temp_egg", "sear_juice", "onion_sweet", "salt_boil", "custard_su", "meat_room_temp", "chicken_low"]


def load(mid: str):
    return importlib.import_module(f"myths.{mid}")


def main(argv: list[str]) -> None:
    for mid in argv or MYTHS:
        m = load(mid)
        m.OUT.write_text(m.page(), encoding="utf-8")
        print("wrote", m.OUT, f"{m.OUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main(sys.argv[1:])
