# Exp-01b 追加: japanese レシピの他 cuisine 最近傍（方法 × k）

- 形式は results/cross_cultural.md と同じ。料理ベクトルはその空間の食材ベクトルから作り直す

## 集計: japanese 全 1423 件の「他 cuisine 最近傍」の割合

### LDA（run.py と同じ）

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

### 重心差 SVD

| cuisine | 候補中の割合 | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|---|
| korean | 0.022 | 0.385 | 0.375 | 0.352 | 0.311 | 0.121 | 0.146 |
| chinese | 0.070 | 0.299 | 0.255 | 0.227 | 0.203 | 0.174 | 0.244 |
| indian | 0.078 | 0.082 | 0.085 | 0.116 | 0.108 | 0.107 | 0.121 |
| thai | 0.040 | 0.056 | 0.048 | 0.056 | 0.048 | 0.105 | 0.053 |
| vietnamese | 0.022 | 0.034 | 0.024 | 0.023 | 0.021 | 0.053 | 0.044 |
| southern_us | 0.113 | 0.028 | 0.041 | 0.036 | 0.043 | 0.051 | 0.056 |
| french | 0.069 | 0.022 | 0.032 | 0.031 | 0.026 | 0.037 | 0.039 |
| filipino | 0.020 | 0.020 | 0.020 | 0.021 | 0.020 | 0.057 | 0.039 |
| italian | 0.204 | 0.017 | 0.038 | 0.037 | 0.038 | 0.079 | 0.070 |
| mexican | 0.168 | 0.012 | 0.013 | 0.027 | 0.110 | 0.106 | 0.073 |
| cajun_creole | 0.040 | 0.012 | 0.015 | 0.013 | 0.012 | 0.015 | 0.022 |
| british | 0.021 | 0.007 | 0.016 | 0.015 | 0.013 | 0.019 | 0.015 |
| russian | 0.013 | 0.006 | 0.010 | 0.006 | 0.008 | 0.012 | 0.009 |
| jamaican | 0.014 | 0.005 | 0.005 | 0.004 | 0.004 | 0.023 | 0.015 |
| moroccan | 0.021 | 0.004 | 0.003 | 0.013 | 0.010 | 0.011 | 0.022 |
| spanish | 0.026 | 0.004 | 0.009 | 0.008 | 0.007 | 0.009 | 0.011 |
| irish | 0.017 | 0.002 | 0.003 | 0.002 | 0.003 | 0.004 | 0.001 |
| brazilian | 0.012 | 0.002 | 0.004 | 0.004 | 0.006 | 0.006 | 0.006 |
| greek | 0.031 | 0.001 | 0.005 | 0.008 | 0.008 | 0.011 | 0.014 |
| korean+chinese | 0.091 | 0.684 | 0.630 | 0.579 | 0.514 | 0.295 | 0.390 |
| 分布のエントロピー (bit) | — | 2.63 | 2.87 | 2.99 | 3.13 | 3.66 | 3.53 |

### INLP（1 反復 1 本）

| cuisine | 候補中の割合 | k=0 | 1反復 (k=1) | 3反復 (k=3) | 5反復 (k=5) | 10反復 (k=10) | 19反復 (k=19) | 30反復 (k=30) |
|---|---|---|---|---|---|---|---|---|
| korean | 0.022 | 0.385 | 0.389 | 0.382 | 0.370 | 0.315 | 0.171 | 0.103 |
| chinese | 0.070 | 0.299 | 0.297 | 0.278 | 0.236 | 0.193 | 0.247 | 0.214 |
| indian | 0.078 | 0.082 | 0.082 | 0.082 | 0.085 | 0.084 | 0.087 | 0.105 |
| thai | 0.040 | 0.056 | 0.055 | 0.054 | 0.056 | 0.064 | 0.068 | 0.056 |
| vietnamese | 0.022 | 0.034 | 0.030 | 0.022 | 0.020 | 0.035 | 0.046 | 0.037 |
| southern_us | 0.113 | 0.028 | 0.027 | 0.046 | 0.053 | 0.059 | 0.076 | 0.110 |
| french | 0.069 | 0.022 | 0.022 | 0.025 | 0.035 | 0.060 | 0.070 | 0.060 |
| filipino | 0.020 | 0.020 | 0.021 | 0.020 | 0.024 | 0.020 | 0.015 | 0.020 |
| italian | 0.204 | 0.017 | 0.019 | 0.020 | 0.032 | 0.051 | 0.086 | 0.103 |
| mexican | 0.168 | 0.012 | 0.012 | 0.014 | 0.015 | 0.018 | 0.022 | 0.061 |
| cajun_creole | 0.040 | 0.012 | 0.011 | 0.011 | 0.014 | 0.020 | 0.025 | 0.030 |
| british | 0.021 | 0.007 | 0.009 | 0.015 | 0.017 | 0.019 | 0.019 | 0.025 |
| russian | 0.013 | 0.006 | 0.006 | 0.008 | 0.008 | 0.009 | 0.013 | 0.015 |
| jamaican | 0.014 | 0.005 | 0.005 | 0.004 | 0.004 | 0.003 | 0.004 | 0.008 |
| moroccan | 0.021 | 0.004 | 0.003 | 0.004 | 0.005 | 0.012 | 0.008 | 0.012 |
| spanish | 0.026 | 0.004 | 0.006 | 0.005 | 0.011 | 0.018 | 0.013 | 0.009 |
| irish | 0.017 | 0.002 | 0.002 | 0.004 | 0.005 | 0.007 | 0.008 | 0.012 |
| brazilian | 0.012 | 0.002 | 0.001 | 0.002 | 0.003 | 0.003 | 0.003 | 0.004 |
| greek | 0.031 | 0.001 | 0.002 | 0.004 | 0.008 | 0.012 | 0.018 | 0.015 |
| korean+chinese | 0.091 | 0.684 | 0.687 | 0.661 | 0.607 | 0.507 | 0.419 | 0.318 |
| 分布のエントロピー (bit) | — | 2.63 | 2.62 | 2.74 | 2.94 | 3.26 | 3.45 | 3.62 |

### INLP（1 反復で係数行列の行空間を除去）

| cuisine | 候補中の割合 | k=0 | 1反復 (k=19) | 2反復 (k=38) | 3反復 (k=57) | 4反復 (k=76) | 5反復 (k=95) |
|---|---|---|---|---|---|---|---|
| korean | 0.022 | 0.385 | 0.347 | 0.189 | 0.117 | 0.046 | 0.018 |
| chinese | 0.070 | 0.299 | 0.293 | 0.301 | 0.266 | 0.145 | 0.074 |
| indian | 0.078 | 0.082 | 0.080 | 0.086 | 0.105 | 0.112 | 0.083 |
| thai | 0.040 | 0.056 | 0.056 | 0.075 | 0.067 | 0.061 | 0.043 |
| vietnamese | 0.022 | 0.034 | 0.037 | 0.067 | 0.047 | 0.033 | 0.022 |
| southern_us | 0.113 | 0.028 | 0.036 | 0.043 | 0.061 | 0.098 | 0.124 |
| french | 0.069 | 0.022 | 0.025 | 0.040 | 0.053 | 0.070 | 0.060 |
| filipino | 0.020 | 0.020 | 0.030 | 0.034 | 0.027 | 0.022 | 0.022 |
| italian | 0.204 | 0.017 | 0.025 | 0.046 | 0.073 | 0.141 | 0.213 |
| mexican | 0.168 | 0.012 | 0.013 | 0.034 | 0.060 | 0.100 | 0.153 |
| cajun_creole | 0.040 | 0.012 | 0.010 | 0.015 | 0.027 | 0.032 | 0.040 |
| british | 0.021 | 0.007 | 0.014 | 0.013 | 0.014 | 0.014 | 0.022 |
| russian | 0.013 | 0.006 | 0.006 | 0.007 | 0.007 | 0.009 | 0.007 |
| jamaican | 0.014 | 0.005 | 0.005 | 0.006 | 0.014 | 0.022 | 0.013 |
| moroccan | 0.021 | 0.004 | 0.006 | 0.006 | 0.011 | 0.023 | 0.020 |
| spanish | 0.026 | 0.004 | 0.007 | 0.016 | 0.018 | 0.027 | 0.022 |
| irish | 0.017 | 0.002 | 0.002 | 0.006 | 0.010 | 0.011 | 0.021 |
| brazilian | 0.012 | 0.002 | 0.003 | 0.005 | 0.007 | 0.011 | 0.012 |
| greek | 0.031 | 0.001 | 0.006 | 0.011 | 0.015 | 0.021 | 0.029 |
| korean+chinese | 0.091 | 0.684 | 0.640 | 0.490 | 0.383 | 0.190 | 0.093 |
| 分布のエントロピー (bit) | — | 2.63 | 2.83 | 3.30 | 3.56 | 3.78 | 3.65 |

## クエリごとの上位 5（cuisine と cos）

### 味噌汁っぽいもの: id 20490

食材: dashi, firm tofu, miso, water, scallions

LDA（run.py と同じ）

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | korean (0.89) | korean (0.86) | korean (0.86) | korean (0.86) | chinese (0.87) | korean (0.90) |
| 2 | korean (0.88) | korean (0.85) | korean (0.86) | korean (0.85) | chinese (0.86) | korean (0.89) |
| 3 | korean (0.88) | korean (0.84) | korean (0.84) | korean (0.85) | chinese (0.86) | korean (0.89) |
| 4 | korean (0.87) | korean (0.84) | korean (0.84) | chinese (0.84) | chinese (0.86) | korean (0.88) |
| 5 | korean (0.87) | korean (0.84) | korean (0.84) | thai (0.84) | korean (0.86) | korean (0.88) |

重心差 SVD

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | korean (0.89) | korean (0.86) | korean (0.86) | korean (0.85) | jamaican (0.89) | cajun_creole (0.92) |
| 2 | korean (0.88) | korean (0.85) | korean (0.85) | korean (0.85) | jamaican (0.88) | thai (0.91) |
| 3 | korean (0.88) | korean (0.85) | korean (0.85) | korean (0.84) | korean (0.88) | thai (0.91) |
| 4 | korean (0.87) | chinese (0.84) | korean (0.84) | chinese (0.83) | chinese (0.88) | indian (0.90) |
| 5 | korean (0.87) | korean (0.84) | thai (0.84) | korean (0.83) | jamaican (0.88) | italian (0.90) |

INLP（1 反復 1 本）

| # | k=0 | 1反復 (k=1) | 3反復 (k=3) | 5反復 (k=5) | 10反復 (k=10) | 19反復 (k=19) | 30反復 (k=30) |
|---|---|---|---|---|---|---|---|
| 1 | korean (0.89) | korean (0.89) | korean (0.86) | korean (0.83) | korean (0.83) | italian (0.81) | korean (0.84) |
| 2 | korean (0.88) | korean (0.88) | korean (0.85) | korean (0.82) | korean (0.81) | chinese (0.81) | italian (0.84) |
| 3 | korean (0.88) | korean (0.87) | korean (0.85) | korean (0.82) | chinese (0.81) | russian (0.80) | italian (0.83) |
| 4 | korean (0.87) | korean (0.87) | korean (0.84) | korean (0.81) | korean (0.81) | irish (0.80) | italian (0.82) |
| 5 | korean (0.87) | korean (0.87) | korean (0.83) | thai (0.81) | thai (0.80) | chinese (0.80) | italian (0.82) |

INLP（1 反復で係数行列の行空間を除去）

| # | k=0 | 1反復 (k=19) | 2反復 (k=38) | 3反復 (k=57) | 4反復 (k=76) | 5反復 (k=95) |
|---|---|---|---|---|---|---|
| 1 | korean (0.89) | korean (0.87) | chinese (0.86) | italian (0.85) | jamaican (0.86) | mexican (1.00) |
| 2 | korean (0.88) | korean (0.86) | korean (0.84) | jamaican (0.84) | moroccan (0.86) | french (1.00) |
| 3 | korean (0.88) | korean (0.85) | mexican (0.84) | spanish (0.84) | italian (0.86) | filipino (0.99) |
| 4 | korean (0.87) | korean (0.85) | korean (0.84) | cajun_creole (0.84) | french (0.86) | italian (0.99) |
| 5 | korean (0.87) | chinese (0.85) | korean (0.83) | italian (0.84) | italian (0.86) | mexican (0.99) |

### 照り焼きっぽいもの: id 17805

食材: mirin, corn flour, sake, ginger, eggs, flour, chicken thighs, soy sauce, garlic

LDA（run.py と同じ）

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | chinese (0.90) | chinese (0.88) | chinese (0.88) | filipino (0.88) | chinese (0.91) | chinese (0.92) |
| 2 | chinese (0.89) | filipino (0.88) | chinese (0.88) | chinese (0.88) | chinese (0.90) | chinese (0.91) |
| 3 | korean (0.89) | chinese (0.88) | filipino (0.88) | chinese (0.88) | filipino (0.90) | chinese (0.91) |
| 4 | chinese (0.89) | chinese (0.87) | chinese (0.87) | chinese (0.88) | chinese (0.90) | korean (0.91) |
| 5 | chinese (0.89) | chinese (0.87) | chinese (0.87) | chinese (0.87) | chinese (0.90) | filipino (0.91) |

重心差 SVD

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | chinese (0.90) | filipino (0.88) | chinese (0.89) | chinese (0.88) | british (0.90) | chinese (0.93) |
| 2 | chinese (0.89) | chinese (0.88) | chinese (0.89) | chinese (0.88) | british (0.90) | mexican (0.93) |
| 3 | korean (0.89) | chinese (0.88) | filipino (0.88) | spanish (0.88) | brazilian (0.90) | chinese (0.93) |
| 4 | chinese (0.89) | chinese (0.87) | indian (0.88) | indian (0.87) | filipino (0.90) | chinese (0.93) |
| 5 | chinese (0.89) | chinese (0.87) | moroccan (0.88) | filipino (0.87) | mexican (0.90) | southern_us (0.92) |

INLP（1 反復 1 本）

| # | k=0 | 1反復 (k=1) | 3反復 (k=3) | 5反復 (k=5) | 10反復 (k=10) | 19反復 (k=19) | 30反復 (k=30) |
|---|---|---|---|---|---|---|---|
| 1 | chinese (0.90) | chinese (0.89) | filipino (0.88) | filipino (0.87) | filipino (0.87) | southern_us (0.87) | southern_us (0.88) |
| 2 | chinese (0.89) | chinese (0.89) | chinese (0.87) | chinese (0.86) | southern_us (0.86) | chinese (0.86) | chinese (0.88) |
| 3 | korean (0.89) | korean (0.89) | chinese (0.87) | chinese (0.85) | filipino (0.86) | filipino (0.85) | southern_us (0.87) |
| 4 | chinese (0.89) | chinese (0.89) | chinese (0.87) | chinese (0.85) | chinese (0.85) | irish (0.85) | irish (0.87) |
| 5 | chinese (0.89) | chinese (0.88) | chinese (0.86) | chinese (0.84) | chinese (0.85) | indian (0.85) | southern_us (0.87) |

INLP（1 反復で係数行列の行空間を除去）

| # | k=0 | 1反復 (k=19) | 2反復 (k=38) | 3反復 (k=57) | 4反復 (k=76) | 5反復 (k=95) |
|---|---|---|---|---|---|---|
| 1 | chinese (0.90) | filipino (0.89) | chinese (0.92) | indian (0.91) | indian (0.92) | italian (1.00) |
| 2 | chinese (0.89) | chinese (0.89) | filipino (0.91) | mexican (0.91) | mexican (0.91) | french (0.99) |
| 3 | korean (0.89) | chinese (0.88) | chinese (0.90) | korean (0.91) | italian (0.91) | italian (0.99) |
| 4 | chinese (0.89) | chinese (0.88) | chinese (0.90) | chinese (0.91) | korean (0.91) | mexican (0.99) |
| 5 | chinese (0.89) | chinese (0.88) | chinese (0.90) | indian (0.91) | mexican (0.91) | mexican (0.99) |

### 寿司飯っぽいもの: id 265

食材: water, nori, avocado, rice vinegar, salt, sushi rice, cucumber

LDA（run.py と同じ）

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | korean (0.87) | korean (0.86) | korean (0.86) | korean (0.86) | chinese (0.86) | thai (0.87) |
| 2 | korean (0.87) | korean (0.85) | korean (0.85) | vietnamese (0.86) | korean (0.86) | chinese (0.87) |
| 3 | korean (0.87) | korean (0.85) | korean (0.85) | vietnamese (0.85) | mexican (0.86) | thai (0.87) |
| 4 | chinese (0.87) | korean (0.85) | korean (0.85) | korean (0.85) | vietnamese (0.86) | korean (0.86) |
| 5 | korean (0.86) | korean (0.85) | korean (0.85) | vietnamese (0.85) | chinese (0.86) | chinese (0.86) |

重心差 SVD

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | korean (0.87) | korean (0.86) | korean (0.87) | korean (0.87) | vietnamese (0.92) | thai (0.92) |
| 2 | korean (0.87) | korean (0.86) | korean (0.86) | korean (0.86) | korean (0.91) | korean (0.91) |
| 3 | korean (0.87) | korean (0.86) | korean (0.86) | mexican (0.86) | korean (0.91) | vietnamese (0.91) |
| 4 | chinese (0.87) | korean (0.85) | korean (0.86) | korean (0.86) | thai (0.90) | moroccan (0.91) |
| 5 | korean (0.86) | chinese (0.85) | korean (0.86) | korean (0.86) | moroccan (0.90) | korean (0.91) |

INLP（1 反復 1 本）

| # | k=0 | 1反復 (k=1) | 3反復 (k=3) | 5反復 (k=5) | 10反復 (k=10) | 19反復 (k=19) | 30反復 (k=30) |
|---|---|---|---|---|---|---|---|
| 1 | korean (0.87) | korean (0.87) | korean (0.85) | korean (0.84) | korean (0.83) | vietnamese (0.83) | mexican (0.81) |
| 2 | korean (0.87) | korean (0.87) | korean (0.85) | korean (0.84) | greek (0.83) | mexican (0.83) | vietnamese (0.80) |
| 3 | korean (0.87) | korean (0.87) | korean (0.84) | korean (0.84) | thai (0.83) | greek (0.82) | mexican (0.79) |
| 4 | chinese (0.87) | chinese (0.86) | chinese (0.84) | korean (0.84) | korean (0.83) | greek (0.81) | french (0.79) |
| 5 | korean (0.86) | korean (0.86) | korean (0.84) | korean (0.83) | vietnamese (0.83) | vietnamese (0.81) | greek (0.79) |

INLP（1 反復で係数行列の行空間を除去）

| # | k=0 | 1反復 (k=19) | 2反復 (k=38) | 3反復 (k=57) | 4反復 (k=76) | 5反復 (k=95) |
|---|---|---|---|---|---|---|
| 1 | korean (0.87) | korean (0.86) | southern_us (0.86) | southern_us (0.85) | italian (0.85) | mexican (1.00) |
| 2 | korean (0.87) | thai (0.85) | mexican (0.85) | thai (0.84) | italian (0.82) | russian (1.00) |
| 3 | korean (0.87) | thai (0.85) | french (0.85) | thai (0.83) | italian (0.81) | korean (0.99) |
| 4 | chinese (0.87) | chinese (0.85) | vietnamese (0.84) | russian (0.81) | spanish (0.80) | russian (0.99) |
| 5 | korean (0.86) | korean (0.85) | vietnamese (0.84) | italian (0.81) | russian (0.80) | southern_us (0.99) |

### 天ぷら・揚げ物っぽいもの: id 3931

食材: flour, eggs, oil, tonkatsu sauce, pork chops, panko breadcrumbs

LDA（run.py と同じ）

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | southern_us (0.87) | southern_us (0.87) | southern_us (0.87) | southern_us (0.87) | southern_us (0.88) | southern_us (0.88) |
| 2 | filipino (0.85) | korean (0.84) | korean (0.84) | korean (0.84) | korean (0.85) | korean (0.86) |
| 3 | korean (0.84) | filipino (0.84) | filipino (0.84) | filipino (0.84) | filipino (0.85) | filipino (0.86) |
| 4 | southern_us (0.84) | southern_us (0.84) | southern_us (0.84) | southern_us (0.83) | southern_us (0.84) | french (0.85) |
| 5 | french (0.82) | southern_us (0.82) | southern_us (0.82) | southern_us (0.83) | southern_us (0.83) | southern_us (0.85) |

重心差 SVD

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | southern_us (0.87) | southern_us (0.88) | southern_us (0.88) | southern_us (0.86) | southern_us (0.88) | southern_us (0.88) |
| 2 | filipino (0.85) | korean (0.85) | korean (0.86) | filipino (0.85) | filipino (0.86) | filipino (0.87) |
| 3 | korean (0.84) | southern_us (0.85) | filipino (0.85) | korean (0.84) | korean (0.84) | korean (0.86) |
| 4 | southern_us (0.84) | southern_us (0.85) | southern_us (0.85) | southern_us (0.83) | cajun_creole (0.84) | mexican (0.86) |
| 5 | french (0.82) | southern_us (0.85) | southern_us (0.84) | italian (0.83) | southern_us (0.84) | southern_us (0.86) |

INLP（1 反復 1 本）

| # | k=0 | 1反復 (k=1) | 3反復 (k=3) | 5反復 (k=5) | 10反復 (k=10) | 19反復 (k=19) | 30反復 (k=30) |
|---|---|---|---|---|---|---|---|
| 1 | southern_us (0.87) | southern_us (0.86) | southern_us (0.87) | southern_us (0.87) | southern_us (0.88) | southern_us (0.88) | southern_us (0.88) |
| 2 | filipino (0.85) | southern_us (0.84) | southern_us (0.84) | korean (0.84) | korean (0.85) | filipino (0.87) | filipino (0.86) |
| 3 | korean (0.84) | filipino (0.84) | korean (0.84) | southern_us (0.84) | filipino (0.85) | korean (0.86) | southern_us (0.86) |
| 4 | southern_us (0.84) | korean (0.84) | filipino (0.84) | filipino (0.83) | southern_us (0.84) | southern_us (0.85) | korean (0.85) |
| 5 | french (0.82) | french (0.82) | southern_us (0.83) | southern_us (0.83) | southern_us (0.84) | southern_us (0.84) | southern_us (0.84) |

INLP（1 反復で係数行列の行空間を除去）

| # | k=0 | 1反復 (k=19) | 2反復 (k=38) | 3反復 (k=57) | 4反復 (k=76) | 5反復 (k=95) |
|---|---|---|---|---|---|---|
| 1 | southern_us (0.87) | southern_us (0.86) | southern_us (0.87) | southern_us (0.89) | southern_us (0.90) | indian (0.99) |
| 2 | filipino (0.85) | korean (0.84) | korean (0.87) | filipino (0.88) | southern_us (0.90) | jamaican (0.99) |
| 3 | korean (0.84) | filipino (0.84) | filipino (0.86) | korean (0.87) | italian (0.90) | mexican (0.99) |
| 4 | southern_us (0.84) | southern_us (0.83) | southern_us (0.85) | italian (0.85) | filipino (0.90) | chinese (0.99) |
| 5 | french (0.82) | french (0.83) | southern_us (0.84) | southern_us (0.85) | mexican (0.89) | italian (0.99) |

### カレー: id 12109

食材: crushed tomatoes, potatoes, apples, carrots, pepper, stewing beef, butter, salt, onions, white flour, fresh ginger, beef stock, garlic, bay leaf, curry powder, garam masala, star anise, oil, frozen peas

LDA（run.py と同じ）

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | indian (0.93) | indian (0.93) | indian (0.93) | indian (0.93) | indian (0.93) | indian (0.94) |
| 2 | indian (0.92) | indian (0.92) | british (0.93) | british (0.93) | irish (0.93) | moroccan (0.93) |
| 3 | indian (0.92) | indian (0.92) | french (0.92) | indian (0.92) | british (0.93) | jamaican (0.93) |
| 4 | jamaican (0.92) | jamaican (0.92) | irish (0.92) | french (0.92) | indian (0.93) | indian (0.93) |
| 5 | indian (0.91) | british (0.92) | indian (0.92) | irish (0.92) | irish (0.93) | irish (0.93) |

重心差 SVD

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | indian (0.93) | indian (0.93) | irish (0.94) | indian (0.94) | indian (0.94) | indian (0.95) |
| 2 | indian (0.92) | indian (0.93) | french (0.94) | british (0.93) | french (0.93) | indian (0.95) |
| 3 | indian (0.92) | indian (0.92) | indian (0.94) | irish (0.93) | irish (0.93) | cajun_creole (0.94) |
| 4 | jamaican (0.92) | moroccan (0.92) | british (0.93) | british (0.93) | british (0.93) | indian (0.94) |
| 5 | indian (0.91) | irish (0.92) | british (0.93) | french (0.93) | italian (0.93) | filipino (0.94) |

INLP（1 反復 1 本）

| # | k=0 | 1反復 (k=1) | 3反復 (k=3) | 5反復 (k=5) | 10反復 (k=10) | 19反復 (k=19) | 30反復 (k=30) |
|---|---|---|---|---|---|---|---|
| 1 | indian (0.93) | indian (0.93) | indian (0.93) | indian (0.93) | french (0.93) | french (0.93) | french (0.92) |
| 2 | indian (0.92) | indian (0.92) | irish (0.92) | moroccan (0.93) | french (0.93) | french (0.92) | french (0.91) |
| 3 | indian (0.92) | indian (0.92) | indian (0.92) | jamaican (0.92) | indian (0.92) | irish (0.92) | spanish (0.91) |
| 4 | jamaican (0.92) | jamaican (0.92) | jamaican (0.92) | moroccan (0.92) | moroccan (0.92) | italian (0.92) | italian (0.91) |
| 5 | indian (0.91) | filipino (0.92) | indian (0.92) | irish (0.92) | irish (0.92) | spanish (0.92) | cajun_creole (0.91) |

INLP（1 反復で係数行列の行空間を除去）

| # | k=0 | 1反復 (k=19) | 2反復 (k=38) | 3反復 (k=57) | 4反復 (k=76) | 5反復 (k=95) |
|---|---|---|---|---|---|---|
| 1 | indian (0.93) | irish (0.92) | french (0.94) | cajun_creole (0.93) | mexican (0.94) | italian (1.00) |
| 2 | indian (0.92) | irish (0.92) | irish (0.93) | indian (0.92) | mexican (0.92) | southern_us (1.00) |
| 3 | indian (0.92) | indian (0.92) | irish (0.93) | greek (0.92) | mexican (0.92) | italian (1.00) |
| 4 | jamaican (0.92) | french (0.92) | french (0.93) | french (0.92) | mexican (0.92) | mexican (1.00) |
| 5 | indian (0.91) | jamaican (0.91) | french (0.93) | spanish (0.92) | mexican (0.92) | mexican (1.00) |

### ランダム抽出: id 46555

食材: sea salt, salmon fillets, sake, lemon wedge

LDA（run.py と同じ）

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | french (0.75) | french (0.74) | french (0.74) | italian (0.76) | chinese (0.78) | chinese (0.81) |
| 2 | chinese (0.73) | italian (0.72) | italian (0.73) | italian (0.75) | french (0.78) | italian (0.81) |
| 3 | french (0.72) | italian (0.72) | italian (0.73) | french (0.74) | italian (0.78) | italian (0.80) |
| 4 | chinese (0.72) | russian (0.72) | russian (0.72) | italian (0.74) | italian (0.78) | french (0.80) |
| 5 | french (0.71) | french (0.72) | french (0.72) | russian (0.74) | irish (0.78) | thai (0.80) |

重心差 SVD

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | french (0.75) | russian (0.76) | russian (0.77) | russian (0.75) | british (0.83) | british (0.85) |
| 2 | chinese (0.73) | french (0.76) | italian (0.76) | british (0.75) | italian (0.80) | southern_us (0.84) |
| 3 | french (0.72) | irish (0.75) | french (0.76) | french (0.74) | italian (0.80) | cajun_creole (0.84) |
| 4 | chinese (0.72) | french (0.75) | irish (0.76) | french (0.73) | british (0.80) | italian (0.83) |
| 5 | french (0.71) | italian (0.74) | italian (0.75) | mexican (0.73) | thai (0.80) | british (0.82) |

INLP（1 反復 1 本）

| # | k=0 | 1反復 (k=1) | 3反復 (k=3) | 5反復 (k=5) | 10反復 (k=10) | 19反復 (k=19) | 30反復 (k=30) |
|---|---|---|---|---|---|---|---|
| 1 | french (0.75) | french (0.75) | french (0.75) | french (0.75) | cajun_creole (0.76) | cajun_creole (0.75) | mexican (0.74) |
| 2 | chinese (0.73) | chinese (0.74) | french (0.73) | russian (0.74) | russian (0.76) | russian (0.75) | southern_us (0.74) |
| 3 | french (0.72) | french (0.74) | chinese (0.73) | italian (0.74) | italian (0.76) | irish (0.75) | italian (0.73) |
| 4 | chinese (0.72) | french (0.72) | cajun_creole (0.73) | italian (0.74) | french (0.75) | italian (0.75) | cajun_creole (0.73) |
| 5 | french (0.71) | chinese (0.72) | russian (0.73) | french (0.74) | italian (0.75) | french (0.75) | british (0.73) |

INLP（1 反復で係数行列の行空間を除去）

| # | k=0 | 1反復 (k=19) | 2反復 (k=38) | 3反復 (k=57) | 4反復 (k=76) | 5反復 (k=95) |
|---|---|---|---|---|---|---|
| 1 | french (0.75) | russian (0.76) | thai (0.81) | southern_us (0.85) | mexican (0.89) | italian (0.99) |
| 2 | chinese (0.73) | chinese (0.75) | chinese (0.80) | jamaican (0.85) | british (0.87) | italian (0.99) |
| 3 | french (0.72) | italian (0.75) | irish (0.80) | southern_us (0.85) | italian (0.86) | french (0.99) |
| 4 | chinese (0.72) | french (0.74) | moroccan (0.79) | british (0.84) | vietnamese (0.86) | french (0.99) |
| 5 | french (0.71) | italian (0.74) | cajun_creole (0.79) | korean (0.83) | southern_us (0.86) | italian (0.99) |

### ランダム抽出: id 27844

食材: potatoes, salt, frozen peas, cauliflower, diced tomatoes, ground coriander, cumin, tumeric, cilantro, cumin seed, vegetable oil, cayenne pepper, boiling water

LDA（run.py と同じ）

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | indian (0.95) | indian (0.95) | indian (0.95) | indian (0.95) | indian (0.95) | indian (0.95) |
| 2 | indian (0.95) | indian (0.95) | indian (0.94) | indian (0.94) | indian (0.95) | indian (0.95) |
| 3 | indian (0.95) | indian (0.95) | indian (0.94) | indian (0.94) | indian (0.95) | indian (0.95) |
| 4 | indian (0.95) | indian (0.95) | indian (0.94) | indian (0.94) | indian (0.95) | indian (0.95) |
| 5 | indian (0.94) | indian (0.94) | indian (0.94) | indian (0.94) | indian (0.95) | indian (0.95) |

重心差 SVD

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | indian (0.95) | indian (0.95) | indian (0.94) | indian (0.93) | indian (0.94) | indian (0.95) |
| 2 | indian (0.95) | indian (0.95) | indian (0.94) | indian (0.93) | indian (0.94) | indian (0.94) |
| 3 | indian (0.95) | indian (0.95) | indian (0.94) | indian (0.93) | indian (0.94) | indian (0.94) |
| 4 | indian (0.95) | indian (0.95) | indian (0.94) | indian (0.93) | indian (0.94) | indian (0.94) |
| 5 | indian (0.94) | indian (0.95) | indian (0.94) | indian (0.93) | indian (0.93) | indian (0.94) |

INLP（1 反復 1 本）

| # | k=0 | 1反復 (k=1) | 3反復 (k=3) | 5反復 (k=5) | 10反復 (k=10) | 19反復 (k=19) | 30反復 (k=30) |
|---|---|---|---|---|---|---|---|
| 1 | indian (0.95) | indian (0.95) | indian (0.95) | indian (0.95) | indian (0.93) | indian (0.92) | indian (0.92) |
| 2 | indian (0.95) | indian (0.95) | indian (0.95) | indian (0.94) | indian (0.93) | indian (0.92) | indian (0.92) |
| 3 | indian (0.95) | indian (0.95) | indian (0.95) | indian (0.94) | indian (0.93) | indian (0.92) | indian (0.92) |
| 4 | indian (0.95) | indian (0.95) | indian (0.95) | indian (0.94) | indian (0.93) | indian (0.91) | indian (0.92) |
| 5 | indian (0.94) | indian (0.94) | indian (0.95) | indian (0.94) | indian (0.93) | indian (0.91) | moroccan (0.92) |

INLP（1 反復で係数行列の行空間を除去）

| # | k=0 | 1反復 (k=19) | 2反復 (k=38) | 3反復 (k=57) | 4反復 (k=76) | 5反復 (k=95) |
|---|---|---|---|---|---|---|
| 1 | indian (0.95) | indian (0.94) | indian (0.93) | indian (0.93) | cajun_creole (0.93) | filipino (1.00) |
| 2 | indian (0.95) | indian (0.94) | indian (0.92) | indian (0.93) | indian (0.93) | italian (1.00) |
| 3 | indian (0.95) | indian (0.94) | indian (0.92) | indian (0.92) | cajun_creole (0.92) | italian (1.00) |
| 4 | indian (0.95) | indian (0.94) | indian (0.92) | indian (0.92) | indian (0.92) | thai (1.00) |
| 5 | indian (0.94) | indian (0.94) | indian (0.92) | french (0.92) | southern_us (0.92) | mexican (0.99) |

### ランダム抽出: id 39080

食材: asparagus, soy sauce, sugar, dried bonito flakes, dashi

LDA（run.py と同じ）

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | korean (0.85) | korean (0.83) | korean (0.82) | korean (0.82) | chinese (0.84) | chinese (0.86) |
| 2 | korean (0.84) | korean (0.82) | korean (0.82) | korean (0.81) | chinese (0.83) | chinese (0.84) |
| 3 | korean (0.84) | korean (0.82) | korean (0.82) | thai (0.81) | chinese (0.83) | korean (0.84) |
| 4 | korean (0.83) | korean (0.81) | korean (0.81) | chinese (0.81) | chinese (0.83) | chinese (0.84) |
| 5 | korean (0.83) | korean (0.80) | korean (0.81) | korean (0.81) | thai (0.83) | chinese (0.84) |

重心差 SVD

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | korean (0.85) | korean (0.82) | korean (0.84) | korean (0.83) | thai (0.88) | moroccan (0.90) |
| 2 | korean (0.84) | korean (0.82) | thai (0.83) | korean (0.83) | mexican (0.88) | mexican (0.89) |
| 3 | korean (0.84) | korean (0.82) | korean (0.83) | thai (0.82) | thai (0.88) | chinese (0.89) |
| 4 | korean (0.83) | korean (0.81) | thai (0.82) | mexican (0.82) | mexican (0.88) | moroccan (0.89) |
| 5 | korean (0.83) | korean (0.80) | korean (0.82) | thai (0.82) | moroccan (0.88) | korean (0.89) |

INLP（1 反復 1 本）

| # | k=0 | 1反復 (k=1) | 3反復 (k=3) | 5反復 (k=5) | 10反復 (k=10) | 19反復 (k=19) | 30反復 (k=30) |
|---|---|---|---|---|---|---|---|
| 1 | korean (0.85) | korean (0.85) | korean (0.82) | korean (0.80) | korean (0.80) | italian (0.79) | french (0.81) |
| 2 | korean (0.84) | korean (0.84) | korean (0.81) | korean (0.78) | korean (0.78) | french (0.78) | italian (0.78) |
| 3 | korean (0.84) | korean (0.84) | korean (0.81) | korean (0.77) | korean (0.78) | italian (0.78) | italian (0.78) |
| 4 | korean (0.83) | korean (0.83) | korean (0.80) | korean (0.77) | korean (0.78) | italian (0.78) | mexican (0.77) |
| 5 | korean (0.83) | korean (0.83) | korean (0.79) | korean (0.77) | korean (0.78) | french (0.77) | southern_us (0.76) |

INLP（1 反復で係数行列の行空間を除去）

| # | k=0 | 1反復 (k=19) | 2反復 (k=38) | 3反復 (k=57) | 4反復 (k=76) | 5反復 (k=95) |
|---|---|---|---|---|---|---|
| 1 | korean (0.85) | korean (0.82) | chinese (0.81) | chinese (0.80) | thai (0.79) | brazilian (1.00) |
| 2 | korean (0.84) | chinese (0.81) | chinese (0.81) | chinese (0.80) | filipino (0.78) | southern_us (1.00) |
| 3 | korean (0.84) | korean (0.81) | chinese (0.81) | chinese (0.79) | chinese (0.77) | mexican (1.00) |
| 4 | korean (0.83) | korean (0.81) | chinese (0.81) | french (0.79) | italian (0.77) | southern_us (1.00) |
| 5 | korean (0.83) | korean (0.81) | chinese (0.81) | thai (0.79) | mexican (0.76) | korean (1.00) |
