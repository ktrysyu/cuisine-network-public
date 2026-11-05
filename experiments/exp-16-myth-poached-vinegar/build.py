"""通説の検証ページ「ポーチドエッグは、湯に酢を入れるとまとまる」（writeup/myth-poached-vinegar.html）。

2026-09-28 に通説ページの型（experiments/myths/）へ移した。中身は experiments/myths/poached_vinegar.py。
このファイルは前の呼び方を残すための入口:

    uv run python experiments/exp-16-myth-poached-vinegar/build.py
    （＝ uv run python experiments/myths/build.py poached_vinegar）
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from myths.poached_vinegar import OUT, compute, page  # noqa: E402,F401


def main() -> None:
    OUT.write_text(page(), encoding="utf-8")
    print("wrote", OUT, f"{OUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
