# Exp-02 下書き（Claude）と本人確認版の差

- 下書き `taste_scores_draft.csv` と本人確認版 `taste_scores.csv` を食材ごとに比べた。変更された食材 48 件（`changed_from_draft` 列と一致: True）
- 差 = 本人 − 下書き

## 軸ごとの集計

| 軸 | 変更セル数 | 上げた | 下げた | 差の合計 | |差|の合計 | 下書き平均 → 本人平均 |
|---|---|---|---|---|---|---|
| 甘 | 13 | 4 | 9 | -5 | 13 | 0.87 → 0.86 |
| 塩 | 2 | 0 | 2 | -2 | 2 | 0.62 → 0.61 |
| 酸 | 9 | 6 | 3 | +4 | 10 | 0.57 → 0.59 |
| 苦 | 10 | 4 | 6 | -4 | 12 | 0.56 → 0.54 |
| 旨 | 10 | 10 | 0 | +11 | 11 | 0.74 → 0.78 |
| 辛 | 10 | 10 | 0 | +13 | 13 | 0.61 → 0.65 |

要約（差の合計）: 甘-5 / 塩-2 / 酸+4 / 苦-4 / 旨+11 / 辛+13

下書きの confidence 別の変更率: high 13/92, medium 22/183, low 13/28

## 予測可能性（1 と同じ設定、食材ベクトル、GroupKFold の R²）

| スコア | 甘 | 塩 | 酸 | 苦 | 旨 | 辛 | 平均 |
|---|---|---|---|---|---|---|---|
| 下書き | 0.09 | 0.05 | 0.32 | 0.24 | 0.13 | 0.22 | 0.18 |
| 本人 | 0.12 | 0.05 | 0.32 | 0.22 | 0.10 | 0.24 | 0.18 |

下書きスコアでの 6 軸平均 R² は 0.18、本人スコアでは 0.18（差 -0.00）。

## 変更された食材

| 食材 | 和名 | canonical | 下書き confidence | 変更（下書き→本人） |
|---|---|---|---|---|
| onions | 玉ねぎ | onions | medium | 甘 2→1, 酸 0→1, 辛 0→2 |
| sugar | 砂糖 | sugar | high | 旨 0→1 |
| garlic cloves | にんにく（片） | garlic | low | 旨 1→2 |
| kosher salt | コーシャーソルト（粗塩） | salt | high | 旨 0→1 |
| green onions | 青ねぎ | green onions | medium | 甘 1→0 |
| unsalted butter | 無塩バター | butter | medium | 旨 1→2 |
| extra-virgin olive oil | エクストラバージンオリーブオイル | olive oil | medium | 苦 2→1 |
| ground cumin | クミンパウダー | cumin | medium | 辛 1→3 |
| milk | 牛乳 | milk | high | 旨 0→1 |
| red bell pepper | 赤パプリカ | bell pepper | high | 苦 0→1 |
| purple onion | 紫玉ねぎ | onions | medium | 酸 0→1 |
| scallions | 青ねぎ（スキャリオン） | green onions | medium | 苦 0→1 |
| baking powder | ベーキングパウダー | baking powder | medium | 酸 1→0 |
| sour cream | サワークリーム | sour cream | high | 旨 0→2 |
| shallots | エシャロット | shallots | medium | 酸 0→1 |
| honey | はちみつ | honey | high | 酸 1→0 |
| vanilla extract | バニラエッセンス | vanilla extract | low | 甘 1→2, 苦 2→0 |
| paprika | パプリカパウダー | paprika | medium | 辛 0→1 |
| chopped onion | 玉ねぎ（みじん切り） | onions | medium | 酸 0→2 |
| heavy cream | 生クリーム（乳脂肪高め） | heavy cream | high | 甘 1→2 |
| bay leaves | ローリエ | bay leaves | low | 苦 2→1 |
| sea salt | 海塩 | salt | high | 旨 0→1 |
| large garlic cloves | にんにく（大きめの片） | garlic | low | 旨 1→2 |
| bay leaf | ローリエ（1枚） | bay leaves | low | 苦 2→1 |
| cucumber | きゅうり | cucumber | high | 甘 1→0 |
| green chilies | 青唐辛子 | chile pepper | low | 辛 3→4 |
| ground ginger | ジンジャーパウダー | ginger | medium | 苦 1→2 |
| whipping cream | ホイップ用生クリーム | heavy cream | high | 甘 1→2 |
| balsamic vinegar | バルサミコ酢 | balsamic vinegar | medium | 甘 3→2 |
| capers | ケッパー | capers | medium | 辛 0→1 |
| large egg whites | 卵白（Lサイズ） | egg whites | medium | 塩 1→0 |
| raisins | レーズン | raisins | high | 酸 2→1 |
| red pepper | 赤唐辛子／赤パプリカ | bell pepper | low | 甘 2→1, 辛 1→2 |
| sauce | ソース | sauce | low | 辛 0→1 |
| beansprouts | もやし | beansprouts | medium | 甘 1→0 |
| egg whites | 卵白 | egg whites | medium | 塩 1→0 |
| cherry tomatoes | ミニトマト | tomatoes | high | 酸 2→3 |
| chopped celery | セロリ（刻み） | celery | medium | 苦 1→2 |
| bell pepper | パプリカ（ピーマン類） | bell pepper | low | 甘 2→1, 辛 0→1 |
| active dry yeast | ドライイースト | yeast | low | 苦 2→0 |
| cajun seasoning | ケイジャンシーズニング | cajun seasoning | medium | 酸 0→1 |
| ground allspice | オールスパイス | allspice | medium | 甘 1→0 |
| vanilla | バニラ | vanilla extract | low | 甘 1→2, 苦 2→1 |
| green chile | 青唐辛子（チレ） | chile pepper | low | 辛 2→4 |
| fine sea salt | 海塩（細粒） | salt | high | 旨 0→1 |
| juice | 果汁 | juice | low | 旨 0→1 |
| taco seasoning | タコスシーズニング | taco seasoning | medium | 辛 2→3 |
| okra | オクラ | okra | medium | 甘 1→0 |
