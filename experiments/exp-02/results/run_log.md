# Exp-02 実行ログ

`uv run python experiments/exp-02/run.py` の最終実行時の記録。

## 環境
- Python 3.12.3 / Linux-7.0.0-34-generic-x86_64-with-glibc2.39
- gensim 4.4.0, scikit-learn 1.9.1, scipy 1.18.1, numpy 2.5.3, matplotlib 3.11.2

## 入力
- 食材ベクトル: 読み込み: data/processed/exp01_word2vec.kv（sha256 c958f8aea8a73ed9…）
- train.json の SHA-256 一致: True
- 味覚スコア: data/labels/taste_scores.csv（sha256 2f4f6f5f2f4d5e0c…）、303 食材、canonical 153 群
- 下書き: data/labels/taste_scores_draft.csv（sha256 0aa798075abe0c5d…）
- 料理: 39772 レシピ。採点済み食材 3 個以上 37133 件。語彙内食材のうち採点済みの割合（レシピ平均） 70.9%

## 設定
- SEED = 42、CV = 5-fold × 5 回、RidgeCV alphas = logspace(-3, 4, 15)
- 重心差除去 k = [5, 10, 19]（ランダム除去の対照 10 回）、足し引きの味保存 k = [5, 19]、PCA 成分 10
- 判定規則: VERDICT_MIN = 0.1, VERDICT_RATIO = 2.0
- 平均差方向の件数: sweet 上位(≥3) 25 / 0 161, salty 上位(≥3) 34 / 0 233, sour 上位(≥3) 35 / 0 235, bitter 上位(≥3) 6 / 0 181, umami 上位(≥3) 35 / 0 187, spicy 上位(≥3) 36 / 0 220

## 所要時間
- 全体: 12.5 秒
