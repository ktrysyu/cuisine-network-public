# Exp-01b 実行ログ

`uv run python experiments/exp-01b/run.py` の最終実行時の記録。所要時間はマシン依存。

## 環境
- Python 3.12.3 / Linux-7.0.0-34-generic-x86_64-with-glibc2.39
- gensim 4.4.0, umap-learn 0.5.12, scikit-learn 1.9.1, numpy 2.5.3, scipy 1.18.1, matplotlib 3.11.2

## 入力
- `data/raw/train.json` SHA-256 一致: True
- 食材ベクトル: 読み込み: data/processed/exp01_word2vec.kv（vectors の SHA-256 `c958f8aea8a73ed9…`）
- 使用レシピ 39772、語彙 3336
- k=0 の 10-NN 一致率が Exp-01 metrics.json と一致: True
- k=0 の mirin − japanese + french 上位 8 が Exp-01 と一致: True

## 方法
- LDA: sklearn LinearDiscriminantAnalysis({'solver': 'svd'})、入力は k=0 の料理ベクトル（100 次元・単位長）と cuisine ラベル。判別方向 19 本（scalings_ の列、寄与率順）
- scalings_ は互いに直交しないので、先頭 k 列を QR 分解で正規直交化し、その部分空間を除去する（k を増やすと部分空間は入れ子）
- 食材ベクトル: 単位長にしてから部分空間の成分を引き、再び単位長にする。料理ベクトル・cuisine 重心は Exp-01 と同じ式でその k の食材ベクトルから作り直す（料理ベクトルも除去部分空間に成分を持たない。最大残差は metrics.json の `dish_residual_in_removed_subspace`）
- LDA は一度だけ学習し、k ごとに学習し直さない
- 指標: 10-NN 国籍一致率、シルエット（10000 件×5 回）、除去後の空間で LDA を学習し直したときの 5-fold 分類精度（線形に国籍がどれだけ残るか）、製菓っぽいレシピ（['baking powder', 'baking soda', 'vanilla extract', 'powdered sugar', 'confectioners sugar', 'all-purpose flour', 'unsalted butter', 'large eggs', 'granulated sugar', 'heavy cream'] のうち 3 個以上、1998 件）の 10-NN 製菓一致率
- 2D マップは k=5（`map_k5.png`）。k=0 側は Exp-01 の `umap_2d.npy` をそのまま使う。k=5 を選んだ理由: 和食の他 cuisine 最近傍で korean+chinese の割合が最小（0.579、k=0 は 0.684）、分布のエントロピーが最大（2.95 bit）で、10-NN 一致率の低下は 0.031 にとどまるため

## ハイパーパラメータ
- SEED = 42, K_VALUES = [0, 1, 3, 5, 10, 19], MAP_K = 5
- ARITH_TOP_K = 8, MIRIN_NEIGHBORS_K = 10, AXIS_TOP_N = 10, CULTURE_LIFT_MARK = 3.0, CULTURE_MIN_COUNT = 5
- UMAP: {'n_neighbors': 30, 'min_dist': 0.1, 'metric': 'cosine', 'random_state': 42}（Exp-01 と同じ）

## 所要時間
- k ごと: k=0 24.0 秒, k=1 27.4 秒, k=3 26.7 秒, k=5 26.5 秒, k=10 26.3 秒, k=19 25.9 秒
- UMAP: 28.9 秒
- 全体: 187.7 秒
