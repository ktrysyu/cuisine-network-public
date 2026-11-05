# Exp-01b japanese レシピの他 cuisine 最近傍（k ごと）

- 式は Exp-01 と同じ（料理ベクトルのコサイン類似度、候補は japanese 以外の全レシピ）。料理ベクトルはその k の食材ベクトルから作り直す
- クエリは Exp-01 と同じレシピ（同じ規則・同じ乱数）

## 集計: japanese 全 1423 件の「他 cuisine 最近傍」の割合

| cuisine | 候補中の割合 | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|---|
| korean | 0.022 | 0.385 | 0.412 | 0.414 | 0.329 | 0.180 | 0.270 |
| chinese | 0.070 | 0.299 | 0.255 | 0.256 | 0.250 | 0.446 | 0.354 |
| indian | 0.078 | 0.082 | 0.082 | 0.081 | 0.081 | 0.084 | 0.083 |
| thai | 0.040 | 0.056 | 0.048 | 0.049 | 0.100 | 0.058 | 0.058 |
| vietnamese | 0.022 | 0.034 | 0.027 | 0.026 | 0.050 | 0.043 | 0.049 |
| southern_us | 0.113 | 0.028 | 0.036 | 0.034 | 0.040 | 0.040 | 0.039 |
| french | 0.069 | 0.022 | 0.022 | 0.022 | 0.025 | 0.022 | 0.024 |
| filipino | 0.020 | 0.020 | 0.022 | 0.021 | 0.026 | 0.030 | 0.030 |
| italian | 0.204 | 0.017 | 0.024 | 0.025 | 0.030 | 0.027 | 0.025 |
| mexican | 0.168 | 0.012 | 0.015 | 0.018 | 0.018 | 0.022 | 0.019 |
| cajun_creole | 0.040 | 0.012 | 0.012 | 0.011 | 0.011 | 0.011 | 0.011 |
| british | 0.021 | 0.007 | 0.011 | 0.012 | 0.011 | 0.011 | 0.010 |
| russian | 0.013 | 0.006 | 0.011 | 0.009 | 0.009 | 0.007 | 0.006 |
| jamaican | 0.014 | 0.005 | 0.004 | 0.004 | 0.004 | 0.003 | 0.006 |
| moroccan | 0.021 | 0.004 | 0.004 | 0.004 | 0.004 | 0.004 | 0.004 |
| spanish | 0.026 | 0.004 | 0.006 | 0.006 | 0.005 | 0.006 | 0.004 |
| irish | 0.017 | 0.002 | 0.001 | 0.002 | 0.001 | 0.001 | 0.002 |
| brazilian | 0.012 | 0.002 | 0.004 | 0.004 | 0.004 | 0.004 | 0.001 |
| greek | 0.031 | 0.001 | 0.002 | 0.002 | 0.001 | 0.004 | 0.004 |
| korean+chinese | 0.091 | 0.684 | 0.667 | 0.670 | 0.579 | 0.625 | 0.624 |
| 分布のエントロピー (bit) | — | 2.63 | 2.71 | 2.70 | 2.95 | 2.78 | 2.85 |

## クエリごとの上位 5（cuisine と cos）

### 味噌汁っぽいもの: id 20490

食材: dashi, firm tofu, miso, water, scallions

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | korean (0.89) | korean (0.86) | korean (0.86) | korean (0.86) | chinese (0.87) | korean (0.90) |
| 2 | korean (0.88) | korean (0.85) | korean (0.86) | korean (0.85) | chinese (0.86) | korean (0.89) |
| 3 | korean (0.88) | korean (0.84) | korean (0.84) | korean (0.85) | chinese (0.86) | korean (0.89) |
| 4 | korean (0.87) | korean (0.84) | korean (0.84) | chinese (0.84) | chinese (0.86) | korean (0.88) |
| 5 | korean (0.87) | korean (0.84) | korean (0.84) | thai (0.84) | korean (0.86) | korean (0.88) |

### 照り焼きっぽいもの: id 17805

食材: mirin, corn flour, sake, ginger, eggs, flour, chicken thighs, soy sauce, garlic

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | chinese (0.90) | chinese (0.88) | chinese (0.88) | filipino (0.88) | chinese (0.91) | chinese (0.92) |
| 2 | chinese (0.89) | filipino (0.88) | chinese (0.88) | chinese (0.88) | chinese (0.90) | chinese (0.91) |
| 3 | korean (0.89) | chinese (0.88) | filipino (0.88) | chinese (0.88) | filipino (0.90) | chinese (0.91) |
| 4 | chinese (0.89) | chinese (0.87) | chinese (0.87) | chinese (0.88) | chinese (0.90) | korean (0.91) |
| 5 | chinese (0.89) | chinese (0.87) | chinese (0.87) | chinese (0.87) | chinese (0.90) | filipino (0.91) |

### 寿司飯っぽいもの: id 265

食材: water, nori, avocado, rice vinegar, salt, sushi rice, cucumber

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | korean (0.87) | korean (0.86) | korean (0.86) | korean (0.86) | chinese (0.86) | thai (0.87) |
| 2 | korean (0.87) | korean (0.85) | korean (0.85) | vietnamese (0.86) | korean (0.86) | chinese (0.87) |
| 3 | korean (0.87) | korean (0.85) | korean (0.85) | vietnamese (0.85) | mexican (0.86) | thai (0.87) |
| 4 | chinese (0.87) | korean (0.85) | korean (0.85) | korean (0.85) | vietnamese (0.86) | korean (0.86) |
| 5 | korean (0.86) | korean (0.85) | korean (0.85) | vietnamese (0.85) | chinese (0.86) | chinese (0.86) |

### 天ぷら・揚げ物っぽいもの: id 3931

食材: flour, eggs, oil, tonkatsu sauce, pork chops, panko breadcrumbs

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | southern_us (0.87) | southern_us (0.87) | southern_us (0.87) | southern_us (0.87) | southern_us (0.88) | southern_us (0.88) |
| 2 | filipino (0.85) | korean (0.84) | korean (0.84) | korean (0.84) | korean (0.85) | korean (0.86) |
| 3 | korean (0.84) | filipino (0.84) | filipino (0.84) | filipino (0.84) | filipino (0.85) | filipino (0.86) |
| 4 | southern_us (0.84) | southern_us (0.84) | southern_us (0.84) | southern_us (0.83) | southern_us (0.84) | french (0.85) |
| 5 | french (0.82) | southern_us (0.82) | southern_us (0.82) | southern_us (0.83) | southern_us (0.83) | southern_us (0.85) |

### カレー: id 12109

食材: crushed tomatoes, potatoes, apples, carrots, pepper, stewing beef, butter, salt, onions, white flour, fresh ginger, beef stock, garlic, bay leaf, curry powder, garam masala, star anise, oil, frozen peas

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | indian (0.93) | indian (0.93) | indian (0.93) | indian (0.93) | indian (0.93) | indian (0.94) |
| 2 | indian (0.92) | indian (0.92) | british (0.93) | british (0.93) | irish (0.93) | moroccan (0.93) |
| 3 | indian (0.92) | indian (0.92) | french (0.92) | indian (0.92) | british (0.93) | jamaican (0.93) |
| 4 | jamaican (0.92) | jamaican (0.92) | irish (0.92) | french (0.92) | indian (0.93) | indian (0.93) |
| 5 | indian (0.91) | british (0.92) | indian (0.92) | irish (0.92) | irish (0.93) | irish (0.93) |

### ランダム抽出: id 46555

食材: sea salt, salmon fillets, sake, lemon wedge

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | french (0.75) | french (0.74) | french (0.74) | italian (0.76) | chinese (0.78) | chinese (0.81) |
| 2 | chinese (0.73) | italian (0.72) | italian (0.73) | italian (0.75) | french (0.78) | italian (0.81) |
| 3 | french (0.72) | italian (0.72) | italian (0.73) | french (0.74) | italian (0.78) | italian (0.80) |
| 4 | chinese (0.72) | russian (0.72) | russian (0.72) | italian (0.74) | italian (0.78) | french (0.80) |
| 5 | french (0.71) | french (0.72) | french (0.72) | russian (0.74) | irish (0.78) | thai (0.80) |

### ランダム抽出: id 27844

食材: potatoes, salt, frozen peas, cauliflower, diced tomatoes, ground coriander, cumin, tumeric, cilantro, cumin seed, vegetable oil, cayenne pepper, boiling water

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | indian (0.95) | indian (0.95) | indian (0.95) | indian (0.95) | indian (0.95) | indian (0.95) |
| 2 | indian (0.95) | indian (0.95) | indian (0.94) | indian (0.94) | indian (0.95) | indian (0.95) |
| 3 | indian (0.95) | indian (0.95) | indian (0.94) | indian (0.94) | indian (0.95) | indian (0.95) |
| 4 | indian (0.95) | indian (0.95) | indian (0.94) | indian (0.94) | indian (0.95) | indian (0.95) |
| 5 | indian (0.94) | indian (0.94) | indian (0.94) | indian (0.94) | indian (0.95) | indian (0.95) |

### ランダム抽出: id 39080

食材: asparagus, soy sauce, sugar, dried bonito flakes, dashi

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | korean (0.85) | korean (0.83) | korean (0.82) | korean (0.82) | chinese (0.84) | chinese (0.86) |
| 2 | korean (0.84) | korean (0.82) | korean (0.82) | korean (0.81) | chinese (0.83) | chinese (0.84) |
| 3 | korean (0.84) | korean (0.82) | korean (0.82) | thai (0.81) | chinese (0.83) | korean (0.84) |
| 4 | korean (0.83) | korean (0.81) | korean (0.81) | chinese (0.81) | chinese (0.83) | chinese (0.84) |
| 5 | korean (0.83) | korean (0.80) | korean (0.81) | korean (0.81) | thai (0.83) | chinese (0.84) |

各近傍のレシピ id と食材は metrics.json の `cross_cultural.<k>.queries` にある。
