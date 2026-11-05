# Exp-01 補足: 100 次元 → 2 次元の押しつぶし方 4 通り

`uv run python experiments/exp-01/projections.py` の最終実行時の記録。料理ベクトルは run.py と同じ関数・設定で作り直した。

## 数値

| 手法 | 近傍保持率 (k=30) | trustworthiness (k=30) | 10-NN 国籍一致率 | 菓子の 10-NN 菓子率 |
|---|---|---|---|---|
| 100 次元（参考） | 1 | 1 | 0.659 | 0.845 |
| PCA (2 components) | 0.047 | 0.824 | 0.302 | 0.595 |
| UMAP n_neighbors=10 | 0.192 | 0.938 | 0.557 | 0.643 |
| UMAP n_neighbors=30 (= Exp-01 Fig. 1) | 0.190 | 0.938 | 0.547 | 0.630 |
| UMAP n_neighbors=100 | 0.184 | 0.936 | 0.538 | 0.619 |

- PCA の説明分散比: 第1成分 0.1563, 第2成分 0.1384（計 0.2947）
- 近傍保持率 = 100 次元（cosine）での近傍 30 件のうち、2 次元（ユークリッド）でも近傍 30 件に入っている割合の平均。10000 件サンプル（seed=42）内で近傍を取った
- trustworthiness = `sklearn.manifold.trustworthiness(n_neighbors=30, metric='cosine')`、同じ 10000 件サンプル
- 10-NN 国籍一致率 = 全 39772 件で、各レシピの近傍 10 件（自分を除く）のうち同じ cuisine の割合。100 次元の値は Exp-01 の metrics.json と同じ計算（偶然一致率 Σp² = 0.100）
- 菓子の 10-NN 菓子率 = 菓子レシピの近傍 10 件のうち菓子レシピの割合（全体に占める菓子の割合 0.105）
- UMAP n_neighbors=30 の座標が Exp-01 の `results/umap_2d.npy` と一致: True（最大絶対差 0.0）

## 菓子レシピの定義

- sugar / flour / vanilla の 3 カテゴリのうち 2 つ以上を含むレシピ: 4184 件（10.5%）
- カテゴリはトークン名で判定（`sweets_categories()`）。sugar は sugar snap peas 等を、flour は flour tortillas・米粉・コーン粉・豆粉等を除く。vanilla は vanilla ice cream 等も含む
- 該当トークン数: sugar 58, flour 39, vanilla 47
  - flour: all purpose unbleached flour, all-purpose flour, bread flour, cake flour, chapati flour, chapatti flour, durum wheat flour, flour, flour for dusting, gluten flour, gold medal all purpose flour, gold medal flour, graham flour, high gluten bread flour, high-gluten flour, kamut flour, maida flour, pastry flour, plain flour, seasoned flour, self raising flour, self rising flour, self-rising cake flour, semolina flour, soft-wheat flour, spelt flour, strong white bread flour, tipo 00 flour, unbleached flour, wheat flour, white bread flour, white flour, white lily flour, whole grain spelt flour, whole wheat bread flour, whole wheat flour, whole wheat pastry flour, wholemeal flour, wondra flour

## 図

- `compare_2x2.png`: 4 通りを cuisine 色分け（配色は Exp-01 図1と同じ tab20・件数順）。重心ラベルは重ならないよう押し離し、動かしたものは細線で元の重心と結ぶ（重なり解消に成功: {'pca': True, 'umap_n10': True, 'umap_n30': True, 'umap_n100': True}）
- `sweets_2x2.png`: 菓子レシピを濃色、その他を薄い灰色
- `*_2d.npy`: 各手法の 2 次元座標（行順は run.py の使用レシピ順）

## 環境・所要時間

- Python 3.12.3 / umap-learn 0.5.12, scikit-learn 1.9.1, numpy 2.5.3, matplotlib 3.11.2
- 前処理 + word2vec 学習 + 料理ベクトル: 58.1 秒
- pca: 0.0 秒
- umap_n10: 20.8 秒
- umap_n30: 17.8 秒
- umap_n100: 40.7 秒
- 評価指標: 34.1 秒 / 描画: 2.7 秒
- 全体: 175.1 秒
