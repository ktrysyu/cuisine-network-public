# Cuisine Network

食材の組み合わせから料理の空間を学習し、その上で料理の「足し引き」や「調理の計算」ができるかを試している研究ノートと実験コードです。Arukashi（料理の通説を計算で確かめる試み）の元になっています。

進行中の研究なので、結果は途中のものです。

## 何があるか

- `writeup/` 研究ページ（HTML）。`writeup/index.html` から読めます。問い、実験計画、Exp-01〜20 の結果、通説を確かめるページ 8 本が入っています。
- `experiments/` 各実験のコードと結果。実験ごとに `plan.md` があります。
- `data/labels/` 味覚・香り・食感などのラベル。本人が確認・修正したものです。
- `data/SOURCES.md` データの出典と利用条件。

## 動かし方

```
uv sync
uv run python experiments/exp-01/run.py
```

実験 1 は `data/raw/train.json`（Kaggle "What's Cooking" の train.json）が必要です。再配布の条件が確認できていないため、このリポジトリには含めていません。取得元と SHA-256 は `data/SOURCES.md` にあります。`run.py` が `data/processed/whats_cooking_tokens.tsv` を作り、実験 2 以降はこれを使います。

## ライセンス

コードは MIT です（`LICENSE`）。外部データは、それぞれの出典の条件に従います（`data/SOURCES.md`）。
