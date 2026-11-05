# Exp-01b 追加（方法の比較）実行ログ

`uv run python experiments/exp-01b/run_methods.py` の最終実行時の記録。所要時間はマシン依存。

## 環境
- Python 3.12.3 / Linux-7.0.0-34-generic-x86_64-with-glibc2.39
- gensim 4.4.0, scikit-learn 1.9.1, numpy 2.5.3, scipy 1.18.1

## 入力
- `data/raw/train.json` SHA-256 一致: True
- 食材ベクトル: 読み込み: data/processed/exp01_word2vec.kv（vectors の SHA-256 `c958f8aea8a73ed9…`）
- 使用レシピ 39772、語彙 3336
- k=0 の 10-NN 一致率が run.py の metrics.json と一致: True
- lda 列（10-NN 一致率と除去割合）が run.py の metrics.json と一致: {1: True, 3: True, 5: True, 10: True, 19: True}

## 方法
- 共通: 方向はすべて k=0 の料理ベクトル（100 次元・単位長）から求め、run.py と同じ `remove_subspace` で単位長の食材ベクトルから部分空間の成分を引いて単位長に戻し、料理ベクトル・cuisine 重心を作り直す
- lda: run.py と同じ（LinearDiscriminantAnalysis({'solver': 'svd'}) の scalings_ 先頭 k 列を QR）
- centroid: cuisine ごとの料理ベクトルの平均（単位長にしない）20 個から全料理の平均を引いた 20×100 行列を SVD。各 cuisine の行を等しく扱う（件数で重み付けしない）。階数 19。右特異ベクトル上位 k 本
- INLP 共通: 料理ベクトルを層化で学習 80% / dev 20% に分け（random_state=42）、LogisticRegression({'C': 10.0, 'max_iter': 2000}, random_state=42) を学習。係数行列（20×100）から、既に除いた部分空間の成分を落として SVD。除去後は食材ベクトルから料理ベクトルを作り直し、その上で学習し直す
- inlp1: 各反復で第 1 右特異ベクトル 1 本だけ除く。30 反復で打ち切り（19 本ずつ除く標準形だと 100 次元が約 5 反復で尽き、k を 1, 3, 5, 10 と揃えられないため追加した変種）。評価は [1, 3, 5, 10, 19, 30] 反復目
- inlp: 各反復で係数行列の行空間（階数 0.001 比で判定）を丸ごと除く。停止: 学習時の dev 精度 ≤ 最多クラス率（0.197）+ 0.02、100 次元をすべて除いた、または 30 反復
- 評価指標・足し引き・軸・和食最近傍は run.py の関数をそのまま呼ぶ。シルエット・交差検証の乱数も run.py と同じ
- 部分空間の診断: 重心差行列の二乗ノルムのうち部分空間に入る割合、k=0 料理ベクトルの全分散のうち部分空間に入る割合、部分空間どうしの主角 cos² の平均

## ハイパーパラメータ
- SEED = 42, K_VALUES = [1, 3, 5, 10, 19], INLP1_ITERS = 30, INLP1_EVAL = [1, 3, 5, 10, 19, 30], INLP_MAX_ITERS = 30, INLP_STOP_MARGIN = 0.02, INLP_DEV_SIZE = 0.2, LR_PARAMS = {'C': 10.0, 'max_iter': 2000}, RANK_TOL = 0.001
- LR の C=10 は、k=0 の料理ベクトルで C ∈ {1, 10, 100} を dev 精度で比べて選んだ（0.742 / 0.749 / 0.747）

## 所要時間
- INLP 方向探索: inlp1 768.5 秒, inlp 119.7 秒
- 評価: base 26.9 秒, lda_1 27.4 秒, lda_3 27.0 秒, lda_5 26.6 秒, lda_10 26.3 秒, lda_19 27.7 秒, centroid_1 27.6 秒, centroid_3 28.2 秒, centroid_5 27.3 秒, centroid_10 25.7 秒, centroid_19 25.7 秒, inlp1_1 27.3 秒, inlp1_3 26.7 秒, inlp1_5 26.7 秒, inlp1_10 26.1 秒, inlp1_19 24.2 秒, inlp1_30 25.5 秒, inlp_1 25.5 秒, inlp_2 26.6 秒, inlp_3 27.5 秒, inlp_4 24.6 秒, inlp_5 24.6 秒
- 全体: 1472.0 秒
