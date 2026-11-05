# Exp-12 油分の層（CLA-130）実行結果（fat_layer.py が生成）

Claude の記録。計画は plan.md「2026-10-22 夜: 油分の層」（計算の前にコミット）。比べ方は Exp-10 と同じ。

対象: 脂質量・味（全軸 0 でない）・香りの対応・word2vec の語彙がそろう 249 食材、ペア数 全ペア 30876・同じ canonical を除く 30581・さらに香りの対応先が同じペアも除く 30440

## 順位相関（Spearman ρ）

| 比較 | 全ペア | 同じ canonical を除く | さらに香りの対応先が同じペアも除く |
|---|---|---|---|
| 油分（−|差|） × 共起（word2vec cos） | +0.091 | +0.071 | +0.067 |
| 油分（−|差|） × 補い合う（PPMI） | +0.067 | +0.076 | +0.076 |
| 油分（−|差|） × 代わりに使える（sub） | +0.159 | +0.143 | +0.141 |
| 油分（−|差|） × 味（6 軸 cos） | +0.011 | -0.011 | -0.015 |
| 油分（−|差|） × 香り（化合物 cos） | -0.052 | -0.077 | -0.082 |
| 油分（−|log の差|） × 共起（word2vec cos） | +0.101 | +0.080 | +0.076 |
| 油分（−|log の差|） × 補い合う（PPMI） | +0.060 | +0.069 | +0.069 |
| 油分（−|log の差|） × 代わりに使える（sub） | +0.130 | +0.113 | +0.111 |
| 油分（−|log の差|） × 味（6 軸 cos） | +0.023 | +0.001 | -0.003 |
| 油分（−|log の差|） × 香り（化合物 cos） | -0.010 | -0.035 | -0.040 |
| 味 × 香り（参考、Exp-10 と同じ） | +0.252 | +0.231 | +0.221 |
| 共起 × 味（参考） | +0.103 | +0.080 | +0.073 |

## 油分は近いが共起では遠い組み合わせ（参考、上位 10）

| 食材 | 食材 | 脂質量 | 脂質量 | 共起 cos |
|---|---|---|---|---|
| lemon | low sodium soy sauce | 0.3 | 0.3 | -0.03 |
| white sugar | white wine vinegar | 0 | 0 | -0.02 |
| powdered sugar | cider vinegar | 0 | 0 | -0.01 |
| granulated sugar | dry red wine | 0 | 0 | -0.01 |
| light soy sauce | arborio rice | 0.57 | 0.58 | -0.03 |
| ground turmeric | whole milk | 3.25 | 3.25 | -0.01 |
| granulated sugar | red wine vinegar | 0 | 0 | -0.00 |
| basil | long grain white rice | 0.64 | 0.66 | -0.01 |
| red wine vinegar | powdered sugar | 0 | 0 | 0.02 |
| powdered sugar | white wine vinegar | 0 | 0 | 0.01 |
