# Exp-02 mirin − japanese + french（味を残した足し引き）

- 式は Exp-01 と同じ: v(mirin) − 重心(japanese) + 重心(french)。重心は各空間で料理ベクトルを作り直して取る。mirin 自身は除外
- 「味の方向を保存」: 重心差 k 本の部分空間から味のリッジ方向 6 本（4 と同じ）の成分を引き、直交化してから除去する。除去する本数は同じ k 本で、味の方向の成分は空間に残る
- 各セル: 食材 [偏りの強い cuisine]（cos） 甘/塩/酸/苦/旨/辛 の本人スコア（303 食材外は —）。mirin は 4/0/0/0/1/0
- [xxx] は Exp-01b と同じ文化タグ（P(c|食材)/P(c) ≥ 3 の最大の cuisine）

| # | 通常（Exp-01） | 重心差 5 本を除去（Exp-01b） | 重心差 5 本を除去・味の方向 6 本を保存 | 重心差 19 本を除去（Exp-01b） | 重心差 19 本を除去・味の方向 6 本を保存 |
|---|---|---|---|---|---|
| 1 | white asparagus [fre] (0.56) — | sake [jap] (0.62) 1/0/1/1/2/0 | sake [jap] (0.62) 1/0/1/1/2/0 | brewed espresso [ita] (0.66) — | brewed espresso [ita] (0.67) — |
| 2 | chopped fresh thyme [fre] (0.56) 0/0/0/2/0/1 | bonito flakes [jap] (0.60) — | bonito flakes [jap] (0.59) — | mini chocolate chips [gre] (0.66) — | mini chocolate chips [gre] (0.63) — |
| 3 | fresh thyme leaves [jam] (0.55) — | dried bonito flakes [jap] (0.59) — | dried bonito flakes [jap] (0.58) — | oreo cookies [iri] (0.65) — | milk chocolate chips [bra] (0.62) — |
| 4 | parsley sprigs [fre] (0.54) — | dashi [jap] (0.57) — | dashi [jap] (0.57) — | milk chocolate chips [bra] (0.64) — | oreo cookies [iri] (0.62) — |
| 5 | candied lemon peel [bri] (0.52) — | white miso [jap] (0.56) — | white miso [jap] (0.56) — | espresso beans [iri] (0.64) — | frangelico [ita] (0.62) — |
| 6 | unsalted butter [bri] (0.52) 1/0/0/0/2/0 | red miso [jap] (0.56) — | red miso [jap] (0.55) — | vanilla pudding [bri] (0.64) — | baileys irish cream liqueur [iri] (0.61) — |
| 7 | dried bonito flakes [jap] (0.51) — | shichimi togarashi [jap] (0.56) — | togarashi [jap] (0.55) — | lemon curd [iri] (0.63) — | espresso beans [iri] (0.61) — |
| 8 | lemon curd [iri] (0.51) — | togarashi [jap] (0.55) — | shichimi togarashi [jap] (0.55) — | frangelico [ita] (0.63) — | lemon curd [iri] (0.61) — |
| 9 | gala apples [fre] (0.51) — | buckwheat soba noodles [jap] (0.55) — | buckwheat soba noodles [jap] (0.54) — | baileys irish cream liqueur [iri] (0.63) — | vanilla pudding [bri] (0.61) — |
| 10 | amaretti [bri] (0.51) — | dashi powder [jap] (0.54) — | kewpie mayonnaise [jap] (0.53) — | miniature semisweet chocolate chips [ita] (0.62) — | angel food cake [ita] (0.61) — |

| | 通常（Exp-01） | 重心差 5 本を除去（Exp-01b） | 重心差 5 本を除去・味の方向 6 本を保存 | 重心差 19 本を除去（Exp-01b） | 重心差 19 本を除去・味の方向 6 本を保存 |
|---|---|---|---|---|---|
| 上位 10 のうち採点済み | 2 | 1 | 1 | 0 | 0 |
| 上位 10 のうち [jap] タグ | 1 | 10 | 10 | 0 | 0 |
| calvados の順位（cos） | 42 (0.47) | 291 (0.38) | 299 (0.38) | 871 (0.39) | 701 (0.39) |
| mirin から除いた二乗ノルム | 0.00 | 0.31 | 0.31 | 0.53 | 0.53 |
| 味の方向 6 本から除いた割合（平均） | 0.00 | 0.07 | 0.00 | 0.20 | 0.00 |
| 結果ベクトルの予測味（甘/塩/酸/苦/旨/辛） | 1.5/0.9/0.8/0.9/1.1/-0.1 | 1.2/0.6/0.7/1.3/0.8/0.7 | 1.7/0.9/0.8/0.9/1.2/-0.2 | 1.0/1.1/0.3/0.9/1.1/0.6 | 1.7/1.0/0.7/0.9/1.2/-0.2 |
| mirin の予測味（同じモデル） | 1.6/0.9/0.5/0.6/1.4/0.1 | 1.3/0.6/0.9/1.1/0.7/0.5 | 1.8/0.9/0.5/0.6/1.5/-0.0 | 1.0/1.1/0.3/0.9/1.1/0.6 | 1.9/1.0/0.5/0.6/1.7/-0.1 |

予測味: その空間の食材ベクトルで全 303 食材に RidgeCV を学習し、結果ベクトル（単位長）に当てた値。参考値。
