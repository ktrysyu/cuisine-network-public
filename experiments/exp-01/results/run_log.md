# Exp-01 実行ログ

`uv run python experiments/exp-01/run.py` の最終実行時の記録。所要時間はマシン依存（再実行で変わるのはこのファイルの時間の行だけのはず）。

## 環境
- Python 3.12.3 / Linux-7.0.0-34-generic-x86_64-with-glibc2.39
- gensim 4.4.0, umap-learn 0.5.12, scikit-learn 1.9.1, numpy 2.5.3, matplotlib 3.11.2

## データ
- `data/raw/train.json` SHA-256: `f18e7e568d1c606774bfb134ece51ef0a143cd5069e6f9241bb6036b45b7d2b0`（SOURCES.md と一致: True）
- レシピ数 39774 / cuisine 数 20
- 食材数/レシピ: 最小 1, 中央値 10, 最大 65
- 同一レシピ内の重複食材（正規化後）を除去: 26 件
- 正規化後のユニーク食材 6703 → word2vec 語彙 3336（min_count=5）。語彙外トークンの割合 1.43%
- 語彙内食材が 1 つも無く除外したレシピ: 2 → 使用 39772
- 前処理済み: `data/processed/whats_cooking_tokens.tsv`

## ハイパーパラメータ
- SEED = 42
- word2vec: {'vector_size': 100, 'window': 70, 'min_count': 5, 'sg': 1, 'negative': 10, 'sample': 0.001, 'epochs': 30, 'workers': 1, 'seed': 42}, 各エポックでレシピ内の食材順をシャッフル: True, hashfxn = crc32
- UMAP: {'n_neighbors': 30, 'min_dist': 0.1, 'metric': 'cosine', 'random_state': 42}
- silhouette: sample_size=10000 × 5 回, kNN k=10

## 所要時間
- word2vec 学習: 57.8 秒
- UMAP: 28.1 秒
- 全体: 121.9 秒
