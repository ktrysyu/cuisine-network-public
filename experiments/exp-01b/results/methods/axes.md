# Exp-01b 追加: 軸への射影（方法 × k）

- 形式は results/axes.md と同じ。セルは「cuisine (平均射影値)」。上 = 左側の極寄り

## soy sauce ↔ butter

### LDA（run.py と同じ）

| 順 | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | korean (+0.262) | korean (+0.193) | korean (+0.188) | korean (+0.179) | korean (+0.183) | korean (+0.181) |
| 2 | chinese (+0.248) | chinese (+0.169) | chinese (+0.163) | chinese (+0.168) | vietnamese (+0.165) | vietnamese (+0.170) |
| 3 | japanese (+0.201) | japanese (+0.128) | japanese (+0.132) | vietnamese (+0.155) | chinese (+0.163) | thai (+0.163) |
| 4 | vietnamese (+0.196) | vietnamese (+0.106) | vietnamese (+0.108) | thai (+0.151) | thai (+0.161) | chinese (+0.162) |
| 5 | thai (+0.190) | thai (+0.083) | thai (+0.091) | japanese (+0.115) | japanese (+0.131) | japanese (+0.132) |
| 6 | filipino (+0.056) | filipino (+0.031) | filipino (+0.035) | filipino (+0.063) | filipino (+0.058) | filipino (+0.043) |
| 7 | jamaican (-0.032) | mexican (-0.019) | mexican (-0.005) | jamaican (+0.023) | jamaican (+0.019) | mexican (+0.008) |
| 8 | indian (-0.035) | jamaican (-0.021) | jamaican (-0.010) | mexican (+0.010) | mexican (+0.010) | jamaican (+0.003) |
| 9 | mexican (-0.064) | brazilian (-0.052) | indian (-0.023) | indian (+0.007) | indian (+0.003) | indian (-0.008) |
| 10 | brazilian (-0.073) | cajun_creole (-0.070) | moroccan (-0.038) | brazilian (-0.015) | moroccan (-0.007) | brazilian (-0.018) |
| 11 | moroccan (-0.099) | spanish (-0.071) | brazilian (-0.043) | moroccan (-0.019) | brazilian (-0.017) | moroccan (-0.028) |
| 12 | cajun_creole (-0.122) | moroccan (-0.075) | greek (-0.059) | cajun_creole (-0.032) | cajun_creole (-0.042) | cajun_creole (-0.044) |
| 13 | spanish (-0.126) | greek (-0.078) | spanish (-0.060) | spanish (-0.045) | spanish (-0.043) | spanish (-0.047) |
| 14 | greek (-0.136) | indian (-0.081) | cajun_creole (-0.066) | greek (-0.049) | greek (-0.049) | greek (-0.048) |
| 15 | russian (-0.162) | italian (-0.106) | italian (-0.101) | italian (-0.089) | italian (-0.094) | italian (-0.101) |
| 16 | italian (-0.176) | russian (-0.126) | russian (-0.115) | russian (-0.102) | russian (-0.098) | russian (-0.105) |
| 17 | southern_us (-0.188) | french (-0.143) | french (-0.138) | southern_us (-0.113) | southern_us (-0.113) | southern_us (-0.120) |
| 18 | french (-0.196) | southern_us (-0.146) | southern_us (-0.143) | french (-0.122) | french (-0.119) | french (-0.120) |
| 19 | irish (-0.206) | irish (-0.165) | irish (-0.157) | irish (-0.138) | irish (-0.132) | irish (-0.142) |
| 20 | british (-0.213) | british (-0.176) | british (-0.167) | british (-0.149) | british (-0.145) | british (-0.155) |
| η² | 0.676 | 0.522 | 0.507 | 0.497 | 0.501 | 0.496 |
| 射影値の標準偏差 | 0.181 | 0.139 | 0.137 | 0.137 | 0.138 | 0.142 |
| k=0 の並びとの順位相関 | +1.00 | +0.96 | +0.98 | +0.99 | +0.99 | +0.98 |

食材の左の極側（上位 10）

- k=0: soy sauce (+0.67), light soy sauce (+0.53), reduced sodium soy sauce (+0.49), low sodium soy sauce (+0.47), gluten free soy sauce (+0.47), tamari soy sauce (+0.47), mushroom soy sauce (+0.47), brown rice vinegar (+0.45), sesame chili oil (+0.45), sesame oil (+0.44)
- k=1: soy sauce (+0.65), light soy sauce (+0.44), gluten free soy sauce (+0.40), reduced sodium soy sauce (+0.38), tamari soy sauce (+0.37), mushroom soy sauce (+0.37), low sodium soy sauce (+0.36), sesame chili oil (+0.36), brown rice vinegar (+0.34), accent seasoning (+0.34)
- k=3: soy sauce (+0.65), light soy sauce (+0.43), gluten free soy sauce (+0.39), tamari soy sauce (+0.37), reduced sodium soy sauce (+0.37), sesame chili oil (+0.35), mushroom soy sauce (+0.35), low sodium soy sauce (+0.35), red radishes (+0.33), liquid smoke (+0.33)
- k=5: soy sauce (+0.64), light soy sauce (+0.42), gluten free soy sauce (+0.38), accent seasoning (+0.36), tamari soy sauce (+0.35), mushroom soy sauce (+0.35), sesame chili oil (+0.34), reduced sodium soy sauce (+0.34), low sodium soy sauce (+0.33), jerk marinade (+0.33)
- k=10: soy sauce (+0.64), light soy sauce (+0.40), gluten free soy sauce (+0.37), reduced sodium soy sauce (+0.37), mushroom soy sauce (+0.36), tamari soy sauce (+0.36), accent seasoning (+0.35), jerk marinade (+0.35), sesame chili oil (+0.34), red radishes (+0.34)
- k=19: soy sauce (+0.64), light soy sauce (+0.44), reduced sodium soy sauce (+0.43), mushroom soy sauce (+0.41), tamari soy sauce (+0.37), gluten free soy sauce (+0.37), red radishes (+0.36), sesame chili oil (+0.36), brown rice vinegar (+0.35), jerk marinade (+0.35)

食材の右の極側（上位 10）

- k=0: butter (-0.67), unsalted butter (-0.48), margarine (-0.45), light butter (-0.38), emmenthal (-0.36), compote (-0.36), melted butter (-0.35), softened butter (-0.35), buttermilk cornbread (-0.34), condensed cheddar cheese soup (-0.34)
- k=1: butter (-0.65), margarine (-0.47), unsalted butter (-0.44), light butter (-0.38), melted butter (-0.36), salted butter (-0.36), softened butter (-0.33), ghee (-0.32), whole nutmegs (-0.32), saffron (-0.32)
- k=3: butter (-0.65), margarine (-0.48), unsalted butter (-0.45), salted butter (-0.37), light butter (-0.36), melted butter (-0.35), butter-margarine blend (-0.34), softened butter (-0.33), evaporated skim milk (-0.32), light cream cheese (-0.30)
- k=5: butter (-0.64), margarine (-0.46), unsalted butter (-0.45), salted butter (-0.35), light butter (-0.34), melted butter (-0.33), truffle oil (-0.32), softened butter (-0.30), buttermilk biscuits (-0.30), butter-margarine blend (-0.30)
- k=10: butter (-0.64), margarine (-0.48), unsalted butter (-0.45), salted butter (-0.37), melted butter (-0.35), light butter (-0.35), truffle oil (-0.32), buttermilk biscuits (-0.31), butter-margarine blend (-0.30), softened butter (-0.30)
- k=19: butter (-0.64), margarine (-0.53), unsalted butter (-0.44), salted butter (-0.40), light butter (-0.39), melted butter (-0.35), butter-margarine blend (-0.34), buttermilk biscuits (-0.33), saffron (-0.31), cinnamon sugar (-0.31)

### 重心差 SVD

| 順 | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | korean (+0.262) | korean (+0.052) | moroccan (+0.021) | korean (-0.023) | chinese (-0.034) | chinese (-0.062) |
| 2 | chinese (+0.248) | greek (+0.051) | korean (+0.021) | mexican (-0.024) | greek (-0.043) | japanese (-0.062) |
| 3 | japanese (+0.201) | chinese (+0.036) | chinese (+0.011) | moroccan (-0.025) | jamaican (-0.043) | filipino (-0.064) |
| 4 | vietnamese (+0.196) | italian (+0.033) | jamaican (+0.008) | chinese (-0.025) | brazilian (-0.045) | indian (-0.064) |
| 5 | thai (+0.190) | spanish (+0.027) | japanese (+0.004) | japanese (-0.026) | british (-0.046) | korean (-0.065) |
| 6 | filipino (+0.056) | cajun_creole (+0.021) | greek (+0.001) | jamaican (-0.035) | indian (-0.048) | thai (-0.065) |
| 7 | jamaican (-0.032) | japanese (+0.018) | spanish (-0.011) | greek (-0.039) | southern_us (-0.049) | irish (-0.065) |
| 8 | indian (-0.035) | moroccan (+0.011) | indian (-0.020) | brazilian (-0.039) | vietnamese (-0.050) | vietnamese (-0.065) |
| 9 | mexican (-0.064) | mexican (+0.008) | cajun_creole (-0.020) | british (-0.041) | japanese (-0.052) | brazilian (-0.066) |
| 10 | brazilian (-0.073) | jamaican (-0.008) | filipino (-0.024) | southern_us (-0.051) | korean (-0.053) | russian (-0.066) |
| 11 | moroccan (-0.099) | french (-0.031) | russian (-0.025) | spanish (-0.051) | italian (-0.054) | southern_us (-0.066) |
| 12 | cajun_creole (-0.122) | filipino (-0.032) | british (-0.027) | french (-0.054) | cajun_creole (-0.057) | british (-0.066) |
| 13 | spanish (-0.126) | vietnamese (-0.035) | mexican (-0.032) | russian (-0.055) | filipino (-0.059) | moroccan (-0.066) |
| 14 | greek (-0.136) | russian (-0.050) | french (-0.034) | indian (-0.063) | french (-0.059) | cajun_creole (-0.066) |
| 15 | russian (-0.162) | brazilian (-0.053) | italian (-0.035) | vietnamese (-0.064) | mexican (-0.059) | jamaican (-0.066) |
| 16 | italian (-0.176) | southern_us (-0.057) | southern_us (-0.038) | irish (-0.064) | moroccan (-0.059) | french (-0.067) |
| 17 | southern_us (-0.188) | thai (-0.058) | brazilian (-0.038) | italian (-0.069) | thai (-0.062) | greek (-0.067) |
| 18 | french (-0.196) | irish (-0.073) | irish (-0.040) | filipino (-0.071) | russian (-0.062) | italian (-0.067) |
| 19 | irish (-0.206) | indian (-0.074) | vietnamese (-0.057) | cajun_creole (-0.079) | spanish (-0.063) | mexican (-0.067) |
| 20 | british (-0.213) | british (-0.075) | thai (-0.083) | thai (-0.081) | irish (-0.068) | spanish (-0.068) |
| η² | 0.676 | 0.227 | 0.107 | 0.073 | 0.013 | 0.001 |
| 射影値の標準偏差 | 0.181 | 0.087 | 0.065 | 0.072 | 0.065 | 0.060 |
| k=0 の並びとの順位相関 | +1.00 | +0.34 | +0.36 | +0.27 | +0.25 | +0.57 |

食材の左の極側（上位 10）

- k=0: soy sauce (+0.67), light soy sauce (+0.53), reduced sodium soy sauce (+0.49), low sodium soy sauce (+0.47), gluten free soy sauce (+0.47), tamari soy sauce (+0.47), mushroom soy sauce (+0.47), brown rice vinegar (+0.45), sesame chili oil (+0.45), sesame oil (+0.44)
- k=1: soy sauce (+0.53), giardiniera (+0.42), sausage meat (+0.38), light soy sauce (+0.34), reduced sodium soy sauce (+0.34), sicilian olives (+0.33), pecorino cheese (+0.32), bocconcini (+0.31), capers (+0.30), low sodium soy sauce (+0.30)
- k=3: soy sauce (+0.52), giardiniera (+0.35), sausage meat (+0.32), light soy sauce (+0.32), gluten free soy sauce (+0.31), pita bread (+0.29), reduced sodium soy sauce (+0.28), achiote (+0.28), hog casings (+0.28), couscous (+0.27)
- k=5: soy sauce (+0.52), giardiniera (+0.32), light soy sauce (+0.32), reduced sodium soy sauce (+0.30), pita bread (+0.29), gluten free soy sauce (+0.28), achiote (+0.28), vanilla ice cream (+0.28), tamari soy sauce (+0.27), sausage meat (+0.27)
- k=10: soy sauce (+0.52), sausage meat (+0.34), giardiniera (+0.34), light soy sauce (+0.33), pita bread (+0.32), sicilian olives (+0.31), dijon style mustard (+0.30), pecorino cheese (+0.30), reduced sodium soy sauce (+0.30), hoagie rolls (+0.28)
- k=19: soy sauce (+0.51), sausage meat (+0.34), fresh dill (+0.32), giardiniera (+0.32), dijon style mustard (+0.31), sicilian olives (+0.31), light soy sauce (+0.29), couscous (+0.29), reduced sodium soy sauce (+0.29), mushroom soy sauce (+0.28)

食材の右の極側（上位 10）

- k=0: butter (-0.67), unsalted butter (-0.48), margarine (-0.45), light butter (-0.38), emmenthal (-0.36), compote (-0.36), melted butter (-0.35), softened butter (-0.35), buttermilk cornbread (-0.34), condensed cheddar cheese soup (-0.34)
- k=1: butter (-0.53), margarine (-0.36), ghee (-0.30), green peas (-0.30), straw mushrooms (-0.28), light butter (-0.28), butter oil (-0.27), unsalted butter (-0.27), milk chocolate chips (-0.27), shredded coconut (-0.27)
- k=3: butter (-0.52), margarine (-0.34), straw mushrooms (-0.31), green peas (-0.30), tom yum paste (-0.26), thai chili paste (-0.26), butter-margarine blend (-0.25), light butter (-0.25), unsalted butter (-0.25), butter oil (-0.25)
- k=5: butter (-0.52), margarine (-0.36), green peas (-0.36), straw mushrooms (-0.27), butter oil (-0.27), light butter (-0.26), fresh spinach (-0.26), canola oil (-0.26), soup (-0.26), butter-margarine blend (-0.25)
- k=10: butter (-0.52), margarine (-0.36), green peas (-0.31), canola oil (-0.28), edamame (-0.28), chèvre (-0.28), butter oil (-0.28), unsalted butter (-0.26), chilli paste (-0.26), light butter (-0.26)
- k=19: butter (-0.51), margarine (-0.37), chèvre (-0.33), canola oil (-0.30), light butter (-0.30), unsalted butter (-0.30), ghee (-0.29), butter oil (-0.28), dark leafy greens (-0.27), mazola corn oil (-0.27)

### INLP（1 反復 1 本）

| 順 | k=0 | 1反復 (k=1) | 3反復 (k=3) | 5反復 (k=5) | 10反復 (k=10) | 19反復 (k=19) | 30反復 (k=30) |
|---|---|---|---|---|---|---|---|
| 1 | korean (+0.262) | korean (+0.250) | korean (+0.104) | korean (-0.013) | korean (-0.069) | greek (-0.128) | mexican (-0.168) |
| 2 | chinese (+0.248) | chinese (+0.228) | chinese (+0.095) | chinese (-0.040) | moroccan (-0.069) | moroccan (-0.138) | greek (-0.191) |
| 3 | japanese (+0.201) | japanese (+0.190) | japanese (+0.062) | japanese (-0.043) | chinese (-0.075) | mexican (-0.139) | moroccan (-0.191) |
| 4 | vietnamese (+0.196) | vietnamese (+0.165) | vietnamese (+0.013) | greek (-0.078) | greek (-0.081) | thai (-0.141) | cajun_creole (-0.194) |
| 5 | thai (+0.190) | thai (+0.147) | thai (-0.015) | spanish (-0.081) | spanish (-0.089) | vietnamese (-0.141) | thai (-0.199) |
| 6 | filipino (+0.056) | filipino (+0.031) | filipino (-0.039) | mexican (-0.090) | vietnamese (-0.102) | chinese (-0.146) | vietnamese (-0.208) |
| 7 | jamaican (-0.032) | indian (-0.043) | jamaican (-0.054) | moroccan (-0.093) | japanese (-0.102) | korean (-0.146) | spanish (-0.211) |
| 8 | indian (-0.035) | jamaican (-0.056) | cajun_creole (-0.092) | vietnamese (-0.094) | thai (-0.107) | spanish (-0.149) | korean (-0.213) |
| 9 | mexican (-0.064) | moroccan (-0.078) | mexican (-0.092) | cajun_creole (-0.096) | italian (-0.108) | cajun_creole (-0.151) | chinese (-0.215) |
| 10 | brazilian (-0.073) | mexican (-0.083) | moroccan (-0.103) | jamaican (-0.096) | cajun_creole (-0.111) | italian (-0.167) | italian (-0.219) |
| 11 | moroccan (-0.099) | brazilian (-0.097) | greek (-0.104) | filipino (-0.105) | mexican (-0.125) | jamaican (-0.173) | jamaican (-0.220) |
| 12 | cajun_creole (-0.122) | greek (-0.109) | spanish (-0.105) | thai (-0.108) | jamaican (-0.126) | japanese (-0.175) | japanese (-0.231) |
| 13 | spanish (-0.126) | spanish (-0.118) | brazilian (-0.112) | italian (-0.112) | indian (-0.131) | indian (-0.177) | indian (-0.236) |
| 14 | greek (-0.136) | cajun_creole (-0.141) | indian (-0.128) | brazilian (-0.119) | filipino (-0.140) | brazilian (-0.191) | brazilian (-0.244) |
| 15 | russian (-0.162) | russian (-0.149) | russian (-0.145) | indian (-0.139) | brazilian (-0.148) | filipino (-0.191) | filipino (-0.247) |
| 16 | italian (-0.176) | italian (-0.165) | italian (-0.150) | french (-0.155) | french (-0.157) | french (-0.215) | french (-0.264) |
| 17 | southern_us (-0.188) | french (-0.185) | french (-0.157) | russian (-0.178) | russian (-0.196) | southern_us (-0.232) | southern_us (-0.268) |
| 18 | french (-0.196) | southern_us (-0.198) | southern_us (-0.165) | southern_us (-0.186) | southern_us (-0.198) | irish (-0.245) | irish (-0.281) |
| 19 | irish (-0.206) | irish (-0.199) | irish (-0.173) | irish (-0.199) | british (-0.204) | russian (-0.248) | russian (-0.282) |
| 20 | british (-0.213) | british (-0.208) | british (-0.182) | british (-0.201) | irish (-0.207) | british (-0.250) | british (-0.288) |
| η² | 0.676 | 0.654 | 0.442 | 0.214 | 0.163 | 0.133 | 0.123 |
| 射影値の標準偏差 | 0.181 | 0.172 | 0.121 | 0.097 | 0.095 | 0.096 | 0.097 |
| k=0 の並びとの順位相関 | +1.00 | +0.99 | +0.95 | +0.72 | +0.63 | +0.51 | +0.44 |

食材の左の極側（上位 10）

- k=0: soy sauce (+0.67), light soy sauce (+0.53), reduced sodium soy sauce (+0.49), low sodium soy sauce (+0.47), gluten free soy sauce (+0.47), tamari soy sauce (+0.47), mushroom soy sauce (+0.47), brown rice vinegar (+0.45), sesame chili oil (+0.45), sesame oil (+0.44)
- 1反復 (k=1): soy sauce (+0.67), light soy sauce (+0.52), reduced sodium soy sauce (+0.48), tamari soy sauce (+0.46), low sodium soy sauce (+0.46), mushroom soy sauce (+0.45), gluten free soy sauce (+0.45), brown rice vinegar (+0.45), bean sauce (+0.44), sesame chili oil (+0.43)
- 3反復 (k=3): soy sauce (+0.62), light soy sauce (+0.44), kikkoman soy sauce (+0.37), mushroom soy sauce (+0.37), reduced sodium soy sauce (+0.37), tamari soy sauce (+0.37), low sodium soy sauce (+0.36), pork spare ribs (+0.35), gluten free soy sauce (+0.34), accent seasoning (+0.34)
- 5反復 (k=5): soy sauce (+0.58), light soy sauce (+0.34), brown rice vinegar (+0.33), reduced sodium soy sauce (+0.31), achiote (+0.29), gluten free soy sauce (+0.29), low sodium soy sauce (+0.29), habanero chile (+0.29), giardiniera (+0.29), tamari soy sauce (+0.28)
- 10反復 (k=10): soy sauce (+0.57), reduced sodium soy sauce (+0.33), sicilian olives (+0.30), light soy sauce (+0.29), pita bread (+0.28), green olives (+0.28), gluten free soy sauce (+0.28), giardiniera (+0.28), pitted green olives (+0.27), couscous (+0.27)
- 19反復 (k=19): soy sauce (+0.59), reduced sodium soy sauce (+0.34), pita bread (+0.30), small red beans (+0.28), light soy sauce (+0.27), achiote (+0.27), low sodium soy sauce (+0.26), sicilian olives (+0.26), mushroom soy sauce (+0.25), whole milk greek yogurt (+0.24)
- 30反復 (k=30): soy sauce (+0.63), couscous (+0.38), reduced sodium soy sauce (+0.32), harissa (+0.30), preserved lemon (+0.30), pita bread (+0.30), small red beans (+0.27), canned black beans (+0.27), ground rosemary (+0.25), fresh dill (+0.25)

食材の右の極側（上位 10）

- k=0: butter (-0.67), unsalted butter (-0.48), margarine (-0.45), light butter (-0.38), emmenthal (-0.36), compote (-0.36), melted butter (-0.35), softened butter (-0.35), buttermilk cornbread (-0.34), condensed cheddar cheese soup (-0.34)
- 1反復 (k=1): butter (-0.67), unsalted butter (-0.47), margarine (-0.46), light butter (-0.40), melted butter (-0.36), softened butter (-0.36), salted butter (-0.35), emmenthal (-0.34), buttermilk cornbread (-0.34), butter-margarine blend (-0.34)
- 3反復 (k=3): butter (-0.62), margarine (-0.45), unsalted butter (-0.39), ghee (-0.35), light butter (-0.35), green peas (-0.32), salted butter (-0.32), milk chocolate chips (-0.32), softened butter (-0.32), evaporated skim milk (-0.32)
- 5反復 (k=5): butter (-0.58), margarine (-0.43), nilla wafers (-0.35), unsalted butter (-0.35), cream style corn (-0.35), milk chocolate chips (-0.35), light butter (-0.34), green peas (-0.34), butter-margarine blend (-0.33), softened butter (-0.32)
- 10反復 (k=10): butter (-0.57), margarine (-0.39), nilla wafers (-0.37), milk chocolate chips (-0.36), cream style corn (-0.35), unsalted butter (-0.34), light butter (-0.32), ghee (-0.32), canola oil (-0.32), mazola corn oil (-0.32)
- 19反復 (k=19): butter (-0.59), margarine (-0.45), mazola corn oil (-0.39), unsalted butter (-0.39), milk chocolate chips (-0.38), nilla wafers (-0.38), light butter (-0.37), water (-0.36), chèvre (-0.36), ghee (-0.36)
- 30反復 (k=30): butter (-0.63), margarine (-0.44), light butter (-0.43), green peas (-0.43), unsalted butter (-0.41), water (-0.41), chèvre (-0.41), nilla wafers (-0.40), spinach (-0.40), ghee (-0.40)

### INLP（1 反復で係数行列の行空間を除去）

| 順 | k=0 | 1反復 (k=19) | 2反復 (k=38) | 3反復 (k=57) | 4反復 (k=76) | 5反復 (k=95) |
|---|---|---|---|---|---|---|
| 1 | korean (+0.262) | korean (+0.150) | thai (-0.011) | thai (-0.073) | thai (-0.113) | british (-0.137) |
| 2 | chinese (+0.248) | chinese (+0.149) | vietnamese (-0.018) | vietnamese (-0.092) | vietnamese (-0.135) | southern_us (-0.152) |
| 3 | japanese (+0.201) | vietnamese (+0.126) | chinese (-0.030) | korean (-0.123) | chinese (-0.143) | irish (-0.173) |
| 4 | vietnamese (+0.196) | thai (+0.125) | korean (-0.033) | moroccan (-0.133) | japanese (-0.144) | brazilian (-0.182) |
| 5 | thai (+0.190) | japanese (+0.100) | japanese (-0.069) | greek (-0.134) | korean (-0.157) | russian (-0.190) |
| 6 | filipino (+0.056) | filipino (+0.014) | greek (-0.109) | chinese (-0.134) | moroccan (-0.166) | chinese (-0.195) |
| 7 | jamaican (-0.032) | indian (-0.009) | moroccan (-0.114) | indian (-0.142) | brazilian (-0.171) | french (-0.196) |
| 8 | indian (-0.035) | moroccan (-0.009) | indian (-0.117) | japanese (-0.145) | spanish (-0.175) | vietnamese (-0.196) |
| 9 | mexican (-0.064) | mexican (-0.020) | mexican (-0.119) | spanish (-0.146) | french (-0.178) | japanese (-0.204) |
| 10 | brazilian (-0.073) | jamaican (-0.021) | spanish (-0.124) | mexican (-0.162) | greek (-0.191) | jamaican (-0.226) |
| 11 | moroccan (-0.099) | greek (-0.035) | brazilian (-0.129) | italian (-0.180) | jamaican (-0.193) | moroccan (-0.232) |
| 12 | cajun_creole (-0.122) | brazilian (-0.047) | filipino (-0.138) | brazilian (-0.181) | italian (-0.209) | indian (-0.234) |
| 13 | spanish (-0.126) | spanish (-0.052) | jamaican (-0.153) | jamaican (-0.197) | indian (-0.210) | thai (-0.236) |
| 14 | greek (-0.136) | cajun_creole (-0.065) | cajun_creole (-0.172) | cajun_creole (-0.203) | cajun_creole (-0.217) | korean (-0.241) |
| 15 | russian (-0.162) | italian (-0.101) | italian (-0.182) | french (-0.208) | filipino (-0.217) | filipino (-0.248) |
| 16 | italian (-0.176) | russian (-0.131) | french (-0.208) | filipino (-0.215) | mexican (-0.223) | spanish (-0.284) |
| 17 | southern_us (-0.188) | french (-0.138) | russian (-0.240) | russian (-0.274) | british (-0.228) | italian (-0.313) |
| 18 | french (-0.196) | southern_us (-0.163) | southern_us (-0.264) | southern_us (-0.283) | russian (-0.236) | greek (-0.317) |
| 19 | irish (-0.206) | irish (-0.180) | irish (-0.275) | irish (-0.285) | southern_us (-0.241) | mexican (-0.322) |
| 20 | british (-0.213) | british (-0.193) | british (-0.293) | british (-0.301) | irish (-0.241) | cajun_creole (-0.333) |
| η² | 0.676 | 0.458 | 0.275 | 0.128 | 0.040 | 0.026 |
| 射影値の標準偏差 | 0.181 | 0.145 | 0.142 | 0.154 | 0.174 | 0.395 |
| k=0 の並びとの順位相関 | +1.00 | +0.96 | +0.84 | +0.70 | +0.69 | -0.27 |

食材の左の極側（上位 10）

- k=0: soy sauce (+0.67), light soy sauce (+0.53), reduced sodium soy sauce (+0.49), low sodium soy sauce (+0.47), gluten free soy sauce (+0.47), tamari soy sauce (+0.47), mushroom soy sauce (+0.47), brown rice vinegar (+0.45), sesame chili oil (+0.45), sesame oil (+0.44)
- 1反復 (k=19): soy sauce (+0.65), light soy sauce (+0.43), tamari soy sauce (+0.42), gluten free soy sauce (+0.41), mushroom soy sauce (+0.40), bean sauce (+0.38), sesame chili oil (+0.36), reduced sodium soy sauce (+0.35), low sodium soy sauce (+0.35), white rice vinegar (+0.34)
- 2反復 (k=38): soy sauce (+0.62), mushroom soy sauce (+0.42), tamari soy sauce (+0.38), habanero chile (+0.37), sesame chili oil (+0.36), achiote (+0.35), light soy sauce (+0.35), shell-on shrimp (+0.34), low sodium soy sauce (+0.34), watermelon (+0.34)
- 3反復 (k=57): soy sauce (+0.62), burrata (+0.50), small red beans (+0.48), goat (+0.48), tamari soy sauce (+0.47), caper berries (+0.47), gaeta olives (+0.45), merguez sausage (+0.44), shell-on shrimp (+0.44), mushroom soy sauce (+0.44)
- 4反復 (k=76): soy sauce (+0.68), chipotle salsa (+0.67), granny smith apples (+0.67), gold potatoes (+0.67), japanese turnips (+0.62), low fat mozzarella (+0.60), peperoncino (+0.59), brioche (+0.59), spam (+0.58), fresh fava bean (+0.57)
- 5反復 (k=95): reduced fat monterey jack cheese (+0.98), granulated sugar (+0.97), center cut pork chops (+0.96), nectarines (+0.95), cutlet (+0.95), guanciale (+0.94), reduced fat mayonnaise (+0.94), bean sauce (+0.93), thai jasmine rice (+0.93), pasilla (+0.93)

食材の右の極側（上位 10）

- k=0: butter (-0.67), unsalted butter (-0.48), margarine (-0.45), light butter (-0.38), emmenthal (-0.36), compote (-0.36), melted butter (-0.35), softened butter (-0.35), buttermilk cornbread (-0.34), condensed cheddar cheese soup (-0.34)
- 1反復 (k=19): butter (-0.65), margarine (-0.49), unsalted butter (-0.45), softened butter (-0.36), light butter (-0.36), deep dish pie crust (-0.35), melted butter (-0.35), ragu (-0.34), butter-margarine blend (-0.34), salted butter (-0.33)
- 2反復 (k=38): butter (-0.62), margarine (-0.52), unbaked pie crusts (-0.47), eggs (-0.47), ragu (-0.45), ground sausage (-0.44), vegetable shortening (-0.44), shortening (-0.44), porridge oats (-0.43), sprinkles (-0.43)
- 3反復 (k=57): butter (-0.62), egg whites (-0.61), water (-0.51), boiling water (-0.50), ragu old world style pasta sauc (-0.49), ragu (-0.47), salt (-0.47), eggs (-0.46), light cream cheese (-0.46), light butter (-0.46)
- 4反復 (k=76): butter (-0.68), chicken fillets (-0.64), marinara sauce (-0.63), chicken breast strips (-0.61), gochujang base (-0.60), light butter (-0.59), tom yum paste (-0.58), bows (-0.58), chunky (-0.58), flora cuisine (-0.58)
- 5反復 (k=95): beef shoulder roast (-0.97), taco shells (-0.97), pumpkin pie spice (-0.95), medium-grain rice (-0.95), jumbo pasta shells (-0.94), garlic powder (-0.94), organic tomato (-0.93), crabmeat (-0.93), agave nectar (-0.92), beef bones (-0.92)

## japanese 重心 ↔ italian 重心

### LDA（run.py と同じ）

| 順 | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | japanese (+0.308) | japanese (+0.246) | japanese (+0.242) | japanese (+0.220) | chinese (+0.224) | korean (+0.231) |
| 2 | korean (+0.303) | korean (+0.224) | korean (+0.211) | korean (+0.203) | japanese (+0.220) | chinese (+0.230) |
| 3 | chinese (+0.292) | chinese (+0.189) | chinese (+0.175) | vietnamese (+0.196) | korean (+0.217) | japanese (+0.221) |
| 4 | vietnamese (+0.234) | vietnamese (+0.132) | vietnamese (+0.107) | chinese (+0.184) | vietnamese (+0.207) | vietnamese (+0.209) |
| 5 | thai (+0.228) | thai (+0.102) | thai (+0.072) | thai (+0.183) | thai (+0.189) | thai (+0.199) |
| 6 | filipino (+0.107) | filipino (+0.078) | filipino (+0.062) | filipino (+0.087) | filipino (+0.102) | filipino (+0.097) |
| 7 | indian (+0.038) | brazilian (+0.021) | brazilian (-0.002) | brazilian (+0.025) | indian (+0.039) | brazilian (+0.041) |
| 8 | jamaican (-0.006) | jamaican (+0.009) | indian (-0.006) | indian (+0.021) | brazilian (+0.029) | indian (+0.038) |
| 9 | brazilian (-0.017) | indian (-0.006) | jamaican (-0.011) | jamaican (-0.007) | jamaican (+0.005) | jamaican (+0.006) |
| 10 | russian (-0.083) | russian (-0.029) | russian (-0.032) | russian (-0.041) | russian (-0.035) | british (-0.048) |
| 11 | british (-0.094) | mexican (-0.040) | british (-0.043) | british (-0.054) | british (-0.053) | russian (-0.051) |
| 12 | mexican (-0.097) | british (-0.042) | irish (-0.055) | irish (-0.070) | southern_us (-0.064) | southern_us (-0.066) |
| 13 | southern_us (-0.101) | southern_us (-0.044) | southern_us (-0.057) | southern_us (-0.071) | irish (-0.071) | irish (-0.076) |
| 14 | irish (-0.108) | irish (-0.051) | mexican (-0.112) | mexican (-0.101) | moroccan (-0.085) | moroccan (-0.082) |
| 15 | moroccan (-0.138) | moroccan (-0.114) | french (-0.113) | moroccan (-0.102) | mexican (-0.095) | mexican (-0.104) |
| 16 | cajun_creole (-0.173) | french (-0.117) | moroccan (-0.118) | french (-0.109) | french (-0.109) | french (-0.111) |
| 17 | french (-0.178) | cajun_creole (-0.123) | cajun_creole (-0.139) | spanish (-0.150) | spanish (-0.144) | spanish (-0.139) |
| 18 | spanish (-0.203) | spanish (-0.148) | spanish (-0.157) | cajun_creole (-0.163) | cajun_creole (-0.150) | cajun_creole (-0.157) |
| 19 | greek (-0.246) | greek (-0.195) | greek (-0.190) | greek (-0.181) | greek (-0.167) | greek (-0.169) |
| 20 | italian (-0.307) | italian (-0.250) | italian (-0.245) | italian (-0.221) | italian (-0.219) | italian (-0.220) |
| η² | 0.735 | 0.623 | 0.606 | 0.595 | 0.602 | 0.595 |
| 射影値の標準偏差 | 0.227 | 0.179 | 0.176 | 0.181 | 0.188 | 0.192 |
| k=0 の並びとの順位相関 | +1.00 | +0.99 | +0.98 | +0.98 | +0.98 | +0.98 |

食材の左の極側（上位 10）

- k=0: soy sauce (+0.55), sesame oil (+0.54), mirin (+0.53), bonito (+0.53), toasted sesame seeds (+0.53), togarashi (+0.52), satsuma imo (+0.52), toasted sesame oil (+0.51), sushi grade tuna (+0.51), nori sheets (+0.49)
- k=1: bonito (+0.59), satsuma imo (+0.47), shichimi togarashi (+0.47), kewpie mayonnaise (+0.47), dried bonito flakes (+0.45), mirin (+0.45), sushi grade tuna (+0.45), togarashi (+0.44), toasted sesame seeds (+0.43), nori sheets (+0.42)
- k=3: bonito (+0.56), mirin (+0.47), satsuma imo (+0.47), dried bonito flakes (+0.46), kewpie mayonnaise (+0.46), shichimi togarashi (+0.46), togarashi (+0.45), roasted white sesame seeds (+0.45), sushi grade tuna (+0.44), bonito flakes (+0.42)
- k=5: bonito (+0.48), roasted white sesame seeds (+0.43), shiso (+0.40), mirin (+0.38), yuzu (+0.38), toasted sesame seeds (+0.37), sushi grade tuna (+0.37), shichimi togarashi (+0.37), ginger ale (+0.37), white cabbage (+0.37)
- k=10: bonito (+0.45), roasted white sesame seeds (+0.41), white cabbage (+0.39), sugar cane (+0.39), ginger ale (+0.38), dark soy sauce (+0.38), sushi grade tuna (+0.37), organic sugar (+0.36), pork neck (+0.36), shiso (+0.35)
- k=19: bonito (+0.44), ginger ale (+0.41), roasted white sesame seeds (+0.41), pork fillet (+0.41), sugar cane (+0.41), toasted sesame seeds (+0.40), organic sugar (+0.40), lime (+0.38), pickled radish (+0.38), beef ribs (+0.38)

食材の右の極側（上位 10）

- k=0: uncooked ziti (-0.52), frozen pizza dough (-0.51), cooked meatballs (-0.48), grated parmesan cheese (-0.48), hot cherry pepper (-0.47), uncooked rigatoni (-0.46), parmesan cheese (-0.44), perciatelli (-0.44), penne (-0.44), manicotti (-0.43)
- k=1: uncooked ziti (-0.47), uncooked rigatoni (-0.45), polenta prepar (-0.45), fat-free reduced-sodium chicken broth (-0.44), prosciutto (-0.43), whole wheat penne (-0.43), grated parmesan cheese (-0.42), parmigiano-reggiano cheese (-0.40), italian turkey sausage (-0.40), mild italian sausage (-0.39)
- k=3: polenta prepar (-0.49), uncooked ziti (-0.45), fat-free reduced-sodium chicken broth (-0.44), uncooked rigatoni (-0.43), whole wheat penne (-0.42), prosciutto (-0.41), mild italian sausage (-0.40), grated parmesan cheese (-0.40), cooked meatballs (-0.39), dried oregano (-0.39)
- k=5: polenta prepar (-0.45), dried oregano (-0.40), uncooked ziti (-0.39), diced tomatoes (-0.39), low-fat spaghetti sauce (-0.38), rotini (-0.38), fontina cheese (-0.38), asiago (-0.38), fresh marjoram (-0.38), fat-free reduced-sodium chicken broth (-0.37)
- k=10: polenta prepar (-0.45), uncooked ziti (-0.42), diced tomatoes (-0.41), dried oregano (-0.41), mild italian sausage (-0.40), fontina cheese (-0.39), pimento stuffed green olives (-0.39), beefsteak tomatoes (-0.39), whole wheat penne (-0.39), grated parmesan cheese (-0.38)
- k=19: polenta prepar (-0.43), dried oregano (-0.42), applewood smoked bacon (-0.41), diced tomatoes (-0.41), mild italian sausage (-0.41), uncooked ziti (-0.40), pimento stuffed green olives (-0.40), whole wheat penne (-0.39), prosciutto (-0.39), grated parmesan cheese (-0.39)

### 重心差 SVD

| 順 | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | japanese (+0.308) | british (+0.182) | japanese (+0.123) | japanese (+0.124) | japanese (+0.035) | japanese (+0.007) |
| 2 | korean (+0.303) | japanese (+0.157) | mexican (+0.094) | mexican (+0.039) | french (+0.020) | thai (+0.006) |
| 3 | chinese (+0.292) | irish (+0.146) | korean (+0.017) | moroccan (+0.001) | spanish (+0.019) | chinese (+0.005) |
| 4 | vietnamese (+0.234) | southern_us (+0.141) | southern_us (+0.006) | korean (-0.002) | filipino (+0.018) | korean (+0.005) |
| 5 | thai (+0.228) | russian (+0.128) | cajun_creole (+0.002) | greek (-0.002) | mexican (+0.010) | vietnamese (+0.004) |
| 6 | filipino (+0.107) | french (+0.052) | russian (-0.009) | southern_us (-0.027) | jamaican (+0.009) | indian (+0.001) |
| 7 | indian (+0.038) | brazilian (+0.042) | moroccan (-0.013) | russian (-0.027) | russian (+0.005) | filipino (-0.000) |
| 8 | jamaican (-0.006) | korean (+0.040) | greek (-0.014) | indian (-0.028) | vietnamese (-0.003) | moroccan (-0.002) |
| 9 | brazilian (-0.017) | jamaican (+0.033) | indian (-0.021) | spanish (-0.039) | thai (-0.008) | jamaican (-0.002) |
| 10 | russian (-0.083) | indian (+0.026) | irish (-0.022) | british (-0.044) | chinese (-0.013) | mexican (-0.003) |
| 11 | british (-0.094) | chinese (+0.016) | british (-0.030) | french (-0.045) | irish (-0.015) | cajun_creole (-0.003) |
| 12 | mexican (-0.097) | filipino (+0.000) | brazilian (-0.032) | irish (-0.045) | greek (-0.020) | brazilian (-0.003) |
| 13 | southern_us (-0.101) | moroccan (-0.030) | chinese (-0.033) | chinese (-0.053) | british (-0.023) | russian (-0.003) |
| 14 | irish (-0.108) | cajun_creole (-0.035) | spanish (-0.036) | cajun_creole (-0.056) | indian (-0.023) | british (-0.004) |
| 15 | moroccan (-0.138) | mexican (-0.037) | jamaican (-0.037) | brazilian (-0.057) | cajun_creole (-0.028) | irish (-0.005) |
| 16 | cajun_creole (-0.173) | spanish (-0.073) | french (-0.052) | jamaican (-0.079) | moroccan (-0.033) | southern_us (-0.005) |
| 17 | french (-0.178) | vietnamese (-0.074) | vietnamese (-0.091) | vietnamese (-0.099) | italian (-0.035) | french (-0.006) |
| 18 | spanish (-0.203) | greek (-0.096) | filipino (-0.096) | thai (-0.109) | southern_us (-0.038) | greek (-0.006) |
| 19 | greek (-0.246) | thai (-0.110) | thai (-0.103) | italian (-0.124) | brazilian (-0.065) | spanish (-0.007) |
| 20 | italian (-0.307) | italian (-0.156) | italian (-0.122) | filipino (-0.140) | korean (-0.079) | italian (-0.007) |
| η² | 0.735 | 0.352 | 0.478 | 0.354 | 0.109 | 0.005 |
| 射影値の標準偏差 | 0.227 | 0.173 | 0.108 | 0.106 | 0.075 | 0.063 |
| k=0 の並びとの順位相関 | +1.00 | +0.26 | +0.09 | -0.03 | +0.12 | +0.90 |

食材の左の極側（上位 10）

- k=0: soy sauce (+0.55), sesame oil (+0.54), mirin (+0.53), bonito (+0.53), toasted sesame seeds (+0.53), togarashi (+0.52), satsuma imo (+0.52), toasted sesame oil (+0.51), sushi grade tuna (+0.51), nori sheets (+0.49)
- k=1: kewpie mayonnaise (+0.56), satsuma imo (+0.49), bonito (+0.46), toasted nori (+0.46), nori sheets (+0.44), fine granulated sugar (+0.44), bonito flakes (+0.43), caviar (+0.43), wasabi paste (+0.43), shichimi togarashi (+0.43)
- k=3: nori sheets (+0.59), kewpie mayonnaise (+0.55), wasabi paste (+0.55), nori (+0.53), relish (+0.51), toasted nori (+0.50), mirin (+0.49), togarashi (+0.48), gari (+0.47), dried bonito flakes (+0.46)
- k=5: nori sheets (+0.62), wasabi paste (+0.57), nori (+0.56), toasted nori (+0.54), kewpie mayonnaise (+0.53), mirin (+0.53), togarashi (+0.51), relish (+0.51), satsuma imo (+0.48), gari (+0.48)
- k=10: tarragon vinegar (+0.39), dried tarragon leaves (+0.34), grapefruit juice (+0.34), fresca (+0.32), tostada shells (+0.32), sake (+0.32), konbu (+0.31), emmenthal (+0.31), chardonnay (+0.30), white wine vinegar (+0.30)
- k=19: green olives (+0.37), soy sauce (+0.35), butter beans (+0.34), nuoc cham (+0.33), mirin (+0.33), california bay leaves (+0.32), lime leaves (+0.32), diced tomatoes (+0.32), rice vermicelli (+0.31), preserved lemon (+0.30)

食材の右の極側（上位 10）

- k=0: uncooked ziti (-0.52), frozen pizza dough (-0.51), cooked meatballs (-0.48), grated parmesan cheese (-0.48), hot cherry pepper (-0.47), uncooked rigatoni (-0.46), parmesan cheese (-0.44), perciatelli (-0.44), penne (-0.44), manicotti (-0.43)
- k=1: italian style stewed tomatoes (-0.43), cooked meatballs (-0.42), polenta prepar (-0.40), prepared lasagne (-0.40), basil leaves (-0.40), pasta shell small (-0.39), fresh basil (-0.39), uncooked rigatoni (-0.39), tom yum paste (-0.38), italian herbs (-0.37)
- k=3: prepared lasagne (-0.40), basil leaves (-0.36), long pepper (-0.34), kaffir lime (-0.34), frozen green beans (-0.33), pork meat (-0.33), dried thai chili (-0.33), pork leg (-0.32), pappardelle (-0.32), venison (-0.32)
- k=5: prepared lasagne (-0.40), pork meat (-0.39), venison (-0.38), pork leg (-0.37), long pepper (-0.36), frozen mixed thawed vegetables, (-0.36), frozen green beans (-0.35), ragu (-0.35), spaghetti, cook and drain (-0.33), basil leaves (-0.33)
- k=10: tandoori seasoning (-0.41), gluten free all purpose flour (-0.40), gluten-free tamari (-0.38), minute rice (-0.38), pasta water (-0.37), sweet rice flour (-0.35), frozen banana (-0.35), gochujang base (-0.35), sesame chili oil (-0.34), rice syrup (-0.34)
- k=19: canola oil (-0.46), vegetable oil (-0.44), sunflower oil (-0.43), peanut oil (-0.33), extra-virgin olive oil (-0.31), fillets (-0.31), tilapia fillets (-0.31), salmon (-0.31), neutral oil (-0.29), safflower oil (-0.29)

### INLP（1 反復 1 本）

| 順 | k=0 | 1反復 (k=1) | 3反復 (k=3) | 5反復 (k=5) | 10反復 (k=10) | 19反復 (k=19) | 30反復 (k=30) |
|---|---|---|---|---|---|---|---|
| 1 | japanese (+0.308) | japanese (+0.298) | japanese (+0.243) | japanese (+0.182) | japanese (+0.146) | british (+0.146) | british (+0.258) |
| 2 | korean (+0.303) | korean (+0.289) | korean (+0.193) | korean (+0.078) | british (+0.136) | japanese (+0.116) | southern_us (+0.169) |
| 3 | chinese (+0.292) | chinese (+0.267) | chinese (+0.180) | brazilian (+0.068) | southern_us (+0.101) | brazilian (+0.079) | irish (+0.141) |
| 4 | vietnamese (+0.234) | vietnamese (+0.198) | vietnamese (+0.085) | british (+0.061) | irish (+0.098) | french (+0.075) | brazilian (+0.125) |
| 5 | thai (+0.228) | thai (+0.178) | filipino (+0.059) | indian (+0.060) | brazilian (+0.098) | southern_us (+0.069) | french (+0.125) |
| 6 | filipino (+0.107) | filipino (+0.078) | thai (+0.047) | southern_us (+0.039) | russian (+0.085) | irish (+0.064) | russian (+0.106) |
| 7 | indian (+0.038) | indian (+0.031) | jamaican (+0.031) | russian (+0.035) | korean (+0.066) | russian (+0.037) | japanese (+0.095) |
| 8 | jamaican (-0.006) | jamaican (-0.035) | british (+0.016) | chinese (+0.035) | vietnamese (+0.061) | chinese (+0.014) | chinese (+0.030) |
| 9 | brazilian (-0.017) | brazilian (-0.045) | russian (+0.012) | irish (+0.033) | french (+0.053) | vietnamese (+0.009) | jamaican (-0.002) |
| 10 | russian (-0.083) | russian (-0.066) | irish (+0.005) | jamaican (+0.032) | indian (+0.050) | thai (-0.001) | vietnamese (-0.012) |
| 11 | british (-0.094) | british (-0.089) | brazilian (+0.005) | filipino (+0.017) | chinese (+0.035) | korean (-0.008) | korean (-0.016) |
| 12 | mexican (-0.097) | irish (-0.098) | southern_us (+0.002) | vietnamese (-0.012) | jamaican (+0.034) | jamaican (-0.015) | filipino (-0.032) |
| 13 | southern_us (-0.101) | moroccan (-0.112) | indian (-0.012) | moroccan (-0.015) | filipino (+0.031) | indian (-0.016) | thai (-0.033) |
| 14 | irish (-0.108) | southern_us (-0.113) | french (-0.069) | french (-0.016) | moroccan (+0.031) | filipino (-0.031) | indian (-0.033) |
| 15 | moroccan (-0.138) | mexican (-0.121) | mexican (-0.079) | mexican (-0.024) | thai (+0.027) | moroccan (-0.037) | moroccan (-0.062) |
| 16 | cajun_creole (-0.173) | french (-0.166) | cajun_creole (-0.082) | thai (-0.033) | cajun_creole (-0.029) | spanish (-0.068) | spanish (-0.088) |
| 17 | french (-0.178) | spanish (-0.196) | moroccan (-0.092) | cajun_creole (-0.050) | spanish (-0.037) | greek (-0.079) | italian (-0.102) |
| 18 | spanish (-0.203) | cajun_creole (-0.200) | spanish (-0.131) | spanish (-0.058) | mexican (-0.065) | italian (-0.123) | mexican (-0.119) |
| 19 | greek (-0.246) | greek (-0.216) | greek (-0.174) | greek (-0.109) | greek (-0.080) | cajun_creole (-0.136) | greek (-0.122) |
| 20 | italian (-0.307) | italian (-0.299) | italian (-0.248) | italian (-0.188) | italian (-0.153) | mexican (-0.154) | cajun_creole (-0.129) |
| η² | 0.735 | 0.721 | 0.604 | 0.423 | 0.337 | 0.218 | 0.182 |
| 射影値の標準偏差 | 0.227 | 0.215 | 0.173 | 0.145 | 0.162 | 0.197 | 0.259 |
| k=0 の並びとの順位相関 | +1.00 | +0.98 | +0.93 | +0.67 | +0.48 | +0.40 | +0.31 |

食材の左の極側（上位 10）

- k=0: soy sauce (+0.55), sesame oil (+0.54), mirin (+0.53), bonito (+0.53), toasted sesame seeds (+0.53), togarashi (+0.52), satsuma imo (+0.52), toasted sesame oil (+0.51), sushi grade tuna (+0.51), nori sheets (+0.49)
- 1反復 (k=1): mirin (+0.54), togarashi (+0.54), toasted sesame seeds (+0.54), bonito (+0.53), soy sauce (+0.52), sesame oil (+0.52), satsuma imo (+0.51), nori sheets (+0.51), toasted sesame oil (+0.51), sushi grade tuna (+0.49)
- 3反復 (k=3): kewpie mayonnaise (+0.57), bonito (+0.55), shichimi togarashi (+0.53), satsuma imo (+0.49), nori sheets (+0.49), togarashi (+0.49), mirin (+0.48), dried bonito flakes (+0.48), bonito flakes (+0.47), sushi grade tuna (+0.44)
- 5反復 (k=5): bonito (+0.54), kewpie mayonnaise (+0.53), nori sheets (+0.52), satsuma imo (+0.52), wasabi paste (+0.49), bonito flakes (+0.48), nori (+0.48), mirin (+0.47), sushi rice (+0.47), toasted nori (+0.46)
- 10反復 (k=10): kewpie mayonnaise (+0.49), lemon-lime soda (+0.49), sorghum syrup (+0.49), bonito (+0.48), angostura bitters (+0.47), cranberry juice (+0.45), kumquats (+0.42), whole cranberry sauce (+0.42), satsuma imo (+0.41), silver (+0.41)
- 19反復 (k=19): coconut rum (+0.54), rye whiskey (+0.52), sweet sherry (+0.52), sauterne (+0.52), lemon-lime soda (+0.51), flavored syrup (+0.51), whole cranberry sauce (+0.51), angostura bitters (+0.51), peach schnapps (+0.51), shortbread cookies (+0.49)
- 30反復 (k=30): shortbread cookies (+0.69), marzipan (+0.67), pink grapefruit juice (+0.66), sauterne (+0.65), color food green (+0.65), cake mix (+0.64), cointreau liqueur (+0.63), flavored syrup (+0.63), sanding sugar (+0.63), icing (+0.63)

食材の右の極側（上位 10）

- k=0: uncooked ziti (-0.52), frozen pizza dough (-0.51), cooked meatballs (-0.48), grated parmesan cheese (-0.48), hot cherry pepper (-0.47), uncooked rigatoni (-0.46), parmesan cheese (-0.44), perciatelli (-0.44), penne (-0.44), manicotti (-0.43)
- 1反復 (k=1): frozen pizza dough (-0.48), uncooked ziti (-0.48), cooked meatballs (-0.47), grated parmesan cheese (-0.47), uncooked rigatoni (-0.46), hot cherry pepper (-0.45), prepar pesto (-0.45), fat-free reduced-sodium chicken broth (-0.45), parmesan cheese (-0.44), italian style stewed tomatoes (-0.44)
- 3反復 (k=3): polenta prepar (-0.50), cooked rigatoni (-0.49), uncooked rigatoni (-0.49), whole wheat penne (-0.47), uncooked ziti (-0.47), cooked meatballs (-0.44), grated parmesan cheese (-0.44), low moisture mozzarella (-0.44), shredded mozzarella cheese (-0.43), frozen pizza dough (-0.43)
- 5反復 (k=5): prepared lasagne (-0.47), polenta prepar (-0.46), cooked meatballs (-0.41), uncooked rigatoni (-0.40), basil dried leaves (-0.40), lasagna noodles, cooked and drained (-0.40), prepar pesto (-0.40), pasta sauce (-0.40), marinara sauce (-0.39), sliced mushrooms (-0.39)
- 10反復 (k=10): cooked meatballs (-0.49), whole wheat penne (-0.45), part-skim mozzarella cheese (-0.45), rigatoni (-0.45), polenta prepar (-0.44), pasta sauce (-0.42), italian style stewed tomatoes (-0.41), marinara sauce (-0.41), uncooked rigatoni (-0.41), 2% low-fat cottage cheese (-0.40)
- 19反復 (k=19): cooked meatballs (-0.53), pasta shell small (-0.50), whole wheat penne (-0.46), extra-lean ground beef (-0.46), red bell pepper (-0.45), spaghetti squash (-0.45), promise buttery spread (-0.44), small pasta (-0.43), zucchini (-0.43), lean ground turkey (-0.42)
- 30反復 (k=30): pasta shell small (-0.53), chicken noodle soup (-0.50), italian herbs (-0.49), red bell pepper (-0.47), cooked meatballs (-0.46), promise buttery spread (-0.45), cannellini beans (-0.45), red gold diced tomatoes (-0.45), small pasta (-0.45), chickpeas (-0.42)

### INLP（1 反復で係数行列の行空間を除去）

| 順 | k=0 | 1反復 (k=19) | 2反復 (k=38) | 3反復 (k=57) | 4反復 (k=76) | 5反復 (k=95) |
|---|---|---|---|---|---|---|
| 1 | japanese (+0.308) | japanese (+0.229) | japanese (+0.159) | japanese (+0.110) | british (+0.172) | british (+0.204) |
| 2 | korean (+0.303) | chinese (+0.211) | chinese (+0.148) | chinese (+0.094) | southern_us (+0.132) | southern_us (+0.191) |
| 3 | chinese (+0.292) | korean (+0.210) | korean (+0.137) | vietnamese (+0.083) | french (+0.115) | irish (+0.147) |
| 4 | vietnamese (+0.234) | thai (+0.185) | vietnamese (+0.134) | brazilian (+0.083) | brazilian (+0.104) | russian (+0.125) |
| 5 | thai (+0.228) | vietnamese (+0.181) | thai (+0.117) | british (+0.065) | irish (+0.103) | brazilian (+0.115) |
| 6 | filipino (+0.107) | filipino (+0.077) | brazilian (+0.074) | korean (+0.064) | russian (+0.085) | french (+0.096) |
| 7 | indian (+0.038) | brazilian (+0.030) | filipino (+0.051) | thai (+0.060) | japanese (+0.084) | japanese (+0.053) |
| 8 | jamaican (-0.006) | indian (+0.022) | indian (+0.021) | french (+0.037) | chinese (+0.051) | chinese (+0.043) |
| 9 | brazilian (-0.017) | jamaican (-0.002) | british (+0.006) | southern_us (+0.031) | vietnamese (+0.029) | vietnamese (+0.042) |
| 10 | russian (-0.083) | russian (-0.056) | jamaican (-0.002) | irish (+0.021) | jamaican (+0.013) | jamaican (+0.022) |
| 11 | british (-0.094) | british (-0.058) | russian (-0.017) | russian (+0.012) | thai (+0.007) | korean (+0.020) |
| 12 | mexican (-0.097) | moroccan (-0.076) | french (-0.024) | indian (+0.001) | korean (+0.003) | thai (+0.004) |
| 13 | southern_us (-0.101) | southern_us (-0.080) | irish (-0.033) | jamaican (-0.002) | moroccan (-0.018) | filipino (-0.010) |
| 14 | irish (-0.108) | irish (-0.080) | moroccan (-0.038) | filipino (-0.014) | spanish (-0.040) | spanish (-0.048) |
| 15 | moroccan (-0.138) | french (-0.106) | southern_us (-0.038) | moroccan (-0.016) | filipino (-0.044) | italian (-0.061) |
| 16 | cajun_creole (-0.173) | mexican (-0.112) | spanish (-0.084) | spanish (-0.055) | indian (-0.051) | moroccan (-0.064) |
| 17 | french (-0.178) | spanish (-0.145) | greek (-0.097) | greek (-0.087) | greek (-0.080) | mexican (-0.071) |
| 18 | spanish (-0.203) | cajun_creole (-0.162) | mexican (-0.140) | italian (-0.115) | italian (-0.092) | greek (-0.074) |
| 19 | greek (-0.246) | greek (-0.168) | italian (-0.163) | cajun_creole (-0.150) | cajun_creole (-0.138) | cajun_creole (-0.088) |
| 20 | italian (-0.307) | italian (-0.232) | cajun_creole (-0.169) | mexican (-0.154) | mexican (-0.159) | indian (-0.100) |
| η² | 0.735 | 0.593 | 0.354 | 0.192 | 0.126 | 0.049 |
| 射影値の標準偏差 | 0.227 | 0.190 | 0.185 | 0.208 | 0.292 | 0.437 |
| k=0 の並びとの順位相関 | +1.00 | +0.97 | +0.91 | +0.70 | +0.23 | +0.23 |

食材の左の極側（上位 10）

- k=0: soy sauce (+0.55), sesame oil (+0.54), mirin (+0.53), bonito (+0.53), toasted sesame seeds (+0.53), togarashi (+0.52), satsuma imo (+0.52), toasted sesame oil (+0.51), sushi grade tuna (+0.51), nori sheets (+0.49)
- 1反復 (k=19): bonito (+0.48), ginger ale (+0.47), toasted sesame seeds (+0.47), potato flour (+0.45), mirin (+0.44), organic sugar (+0.43), roasted white sesame seeds (+0.42), togarashi (+0.41), konbu (+0.41), sushi grade tuna (+0.41)
- 2反復 (k=38): ginger ale (+0.68), coconut rum (+0.64), grenadine (+0.55), cranberry juice (+0.55), organic sugar (+0.55), pink grapefruit juice (+0.54), sour cherries (+0.52), margarita mix (+0.52), campari (+0.51), orange juice (+0.51)
- 3反復 (k=57): pink grapefruit juice (+0.72), campari (+0.70), black tea (+0.68), ginger ale (+0.67), orange slices (+0.64), grenadine (+0.64), coconut rum (+0.64), liqueur (+0.64), silver tequila (+0.63), vin santo (+0.63)
- 4反復 (k=76): pink grapefruit juice (+0.86), satsumas (+0.81), self-rising cake flour (+0.81), vin santo (+0.81), campari (+0.78), grape juice (+0.77), lemon-lime soda (+0.77), organic sugar (+0.72), chinese rock sugar (+0.72), mission figs (+0.71)
- 5反復 (k=95): rome apples (+0.97), sauterne (+0.97), light rum (+0.96), vanilla essence (+0.96), wheat bran (+0.96), seedless green grape (+0.95), dill (+0.94), meringue (+0.94), liqueur (+0.94), mahimahi (+0.94)

食材の右の極側（上位 10）

- k=0: uncooked ziti (-0.52), frozen pizza dough (-0.51), cooked meatballs (-0.48), grated parmesan cheese (-0.48), hot cherry pepper (-0.47), uncooked rigatoni (-0.46), parmesan cheese (-0.44), perciatelli (-0.44), penne (-0.44), manicotti (-0.43)
- 1反復 (k=19): prosciutto (-0.44), grated parmesan cheese (-0.44), polenta prepar (-0.42), parmigiano-reggiano cheese (-0.42), low moisture mozzarella (-0.41), asiago (-0.40), hot italian sausages (-0.40), bread, cut into italian loaf (-0.39), parmesan cheese (-0.39), dried oregano (-0.39)
- 2反復 (k=38): bisquick baking mix (-0.49), mirlitons (-0.47), corn mix muffin (-0.47), pillsburytm refrigerated crescent dinner rolls (-0.47), frozen corn kernels (-0.46), large flour tortillas (-0.46), sharp cheddar cheese (-0.44), fontina (-0.44), whole wheat penne (-0.44), fontina cheese (-0.44)
- 3反復 (k=57): taco sauce (-0.52), elbow pasta (-0.51), cream of celery soup (-0.51), fat-free refried beans (-0.51), campbell's condensed cheddar cheese soup (-0.49), low sodium vegetable stock (-0.48), bread mix (-0.47), old el pasotm chopped green chiles (-0.47), mexican style 4 cheese blend (-0.46), italian herbs (-0.46)
- 4反復 (k=76): fresh peas (-0.72), risotto (-0.64), oregano leaves (-0.63), minute rice (-0.62), artichoke hearts (-0.61), grilled chicken breasts (-0.61), garbanzo beans (-0.60), cutlet (-0.59), water chestnuts (-0.56), shao hsing wine (-0.56)
- 5反復 (k=95): miso (-0.98), brisket (-0.98), spanish chorizo (-0.98), gala apples (-0.97), sausages (-0.96), veggies (-0.96), ham (-0.96), lime (-0.95), thick-cut bacon (-0.95), pistachios (-0.95)
