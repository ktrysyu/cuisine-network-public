# データの出所

生データ（`data/raw/`）は git に入れない。ここに取得元・取得日・SHA-256 を残し、誰でも同じものを取り直せるようにする。

| ファイル | 取得元 | 取得日 | SHA-256 | 使う実験 |
|---|---|---|---|---|
| `raw/train.json` | Kaggle "What's Cooking"（2015）の train.json。**非公式ミラーから取得・Kaggle 公式との照合は未実施**。使用したのは https://raw.githubusercontent.com/Chetana99/kaggle-whats-cooking/96a6ed4ecd09bfd6487f2a7764ee89810c392404/data/train.json （コミット固定） | 2026-09-27 | `f18e7e568d1c606774bfb134ece51ef0a143cd5069e6f9241bb6036b45b7d2b0` | Exp-01 |

### train.json の照合記録（2026-09-27）
- Kaggle API の認証情報が無いため、GitHub 上の非公式ミラーから取得した。**Kaggle 公式配布物とのハッシュ照合は未実施**
- 以下の独立した 7 リポジトリのミラーを取得し、SHA-256 がすべて `f18e7e56…b7d2b0` で一致した（サイズ 12,415,067 bytes）。URL はすべてコミット固定
  - https://raw.githubusercontent.com/Chetana99/kaggle-whats-cooking/96a6ed4ecd09bfd6487f2a7764ee89810c392404/data/train.json （使用）
  - https://raw.githubusercontent.com/T1anyuZhu/WhatsCooking/c9cac8b0828429182397bd435c7ece0258a13a47/input/train.json
  - https://raw.githubusercontent.com/abtpst/Kaggle-Whats-Cooking/cb0ebc84ed5217b81009690d32ad346a0e0919d7/data/train.json
  - https://raw.githubusercontent.com/fazrulrahman/WhatsCooking/aa0a039dcdad641ba9e2bbb9cc74917ada9d6a1b/data/train.json
  - https://raw.githubusercontent.com/ryankrumperman/Whats_Cooking/4c3472eea26a01cc00e0d97701b22cdf6bc75c12/train.json
  - https://raw.githubusercontent.com/rchavezj/Whats_Cooking/8f30631244be08c9a6fa2d5e74d2686485faa25f/train.json
  - https://raw.githubusercontent.com/ChrisYohann/WhatsCooking/f2797a0a93ada14f9c2439dcfc7db8981f671587/train.json
- 中身の確認: レシピ 39,774 件、cuisine 20 種、ユニーク食材（生の文字列）6,714 種。Kaggle 公式の記載値と一致
- 料理名は含まれない（`id`, `cuisine`, `ingredients` のみ）

## ラベル（`data/labels/`）

| ファイル | 作成者 | 作成日 | 状態 | 使う実験 |
|---|---|---|---|---|
| `labels/taste_scores_draft.csv` | Claude（モデル ID claude-opus-5-5）による下書き。本人の確認前 | 2026-09-27 | 下書き。上書きしない。本人が直した版は `labels/taste_scores.csv` として別に作る | Exp-02 |

- 対象は What's Cooking の出現レシピ数上位 303 食材。尺度と選定基準は `experiments/exp-02/scale.md`
- スコアはモデルの知識から付けたもので、官能評価や成分分析の裏付けはない

- `data/labels/taste_scores.csv`: 本人が確認・修正した味覚スコア（303件、2026-09-27）。Claude の下書き `taste_scores_draft.csv` を確認ページ（Artifact の db）で修正したものを書き出した。`changed_from_draft` 列が下書きから変えた行。

## 香り化合物（Exp-10、2026-09-27 確認）

### 使うもの: Ahn et al. 2011 のデータセット（Zenodo 版）

| ファイル | 取得元 | 取得日 | SHA-256 | 使う実験 |
|---|---|---|---|---|
| `raw/ahn2011_zenodo/flavor_network_data.zip` | Zenodo "Dataset for 'Flavor network and the principles of food pairing'" https://zenodo.org/records/11449658 （concept DOI 10.5281/zenodo.11449657、v1.0。著者 Y.-Y. Ahn の論文一覧ページ https://yongyeol.com/pub/ の "Data" リンク先）。Zenodo 表示の md5 `2cbca1517ebe2e3d52f73dfef5f22f3c` と一致 | 2026-09-27 | `9c58eae04fc31ba154231786a444f01e21f5e5ffd7c34a24af251f82039a6c54` | Exp-10 |
| ├ `ingr_comp/ingr_comp.tsv`（食材 id × 化合物 id、36,781 辺） | 上の zip を展開 | 同 | `54ac1a13c20534ec91981e9f10d90703f78dd4c95a8eae017aea3a1b91085f24` | Exp-10 |
| ├ `ingr_comp/ingr_info.tsv`（1,530 食材、名前・カテゴリ） | 同 | 同 | `5ff493a5cc680a7d5b1dde013f5de69e36f481affaabe4b24bc2acc9ede5f518` | Exp-10 |
| ├ `ingr_comp/comp_info.tsv`（1,107 化合物、名前・CAS 番号） | 同 | 同 | `17ae9e5034ae0bd8dcb9845af32ddefb88909d0af5bf68d96a7cf399fc1e35cc` | Exp-10 |
| `raw/ahn2011/srep00196-s2.csv`（食材ペアの共有化合物数。照合用） | 論文の Supplementary Dataset 1（MOESM2_ESM.zip）https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fsrep00196/MediaObjects/41598_2011_BFsrep00196_MOESM2_ESM.zip | 2026-09-27 | csv `7298f0224e74a1c06d29fe6711cf607fb5f130da9e5b8637303706da1f474d3b`（zip `89e56041…3ce2`） | Exp-10（照合のみ） |
| `raw/ahn2011/srep00196-s3.csv`（Ahn らのレシピ 56,498 件。参考） | 同 Supplementary Dataset 2（MOESM3_ESM.zip） | 2026-09-27 | csv `34dfbe5c55eb1b227a161eb654d71012ce1c4cada7670903bd9f3fe1620ccba1`（zip `800a8ff3…f167`） | 未使用 |
| `raw/ahn2011/MOESM1.pdf`（Supplementary Information） | 同 MOESM1_ESM.pdf | 2026-09-27 | `862a3eb5567e73b981b46f68ca6ec8bc6d6e47f28b718a307c8104fddd90d5eb` | 手法の確認 |

利用条件
- **データセット（Zenodo）: CC BY 4.0**。Zenodo のレコードのライセンス欄と、zip 内 `ingr_comp/LICENSE`（"This dataset is shared through CC BY 4.0 license"）の両方で確認。商用・再配布とも可、出典表示が条件
- **論文本体と補足（Scientific Reports）: CC BY-NC-SA 3.0 Unported**（記事ページの Rights and permissions）。補足データ s2/s3 はこちらの条件と見なし、照合にだけ使う。コミットしない
- 化合物の出所は Fenaroli's Handbook of Flavor Ingredients 第5版（書籍）。書籍自体の権利と Zenodo データの CC BY 4.0 の関係は**未確認**（データセットの配布者が CC BY 4.0 を付けている事実だけを記録する）
- 本リポジトリでは研究・非商用で使う。生データはコミットしない（容量の方針どおり）。処理後の対応表 `data/labels/aroma_mapping.csv` は食材名だけでデータの中身を含まない。出典: Ahn, Y.-Y., Ahnert, S. E., Bagrow, J. P., & Barabási, A.-L. (2011). Flavor network and the principles of food pairing. *Scientific Reports*, 1, 196. https://doi.org/10.1038/srep00196

中身の照合
- `ingr_comp.tsv` を食材×食材に射影した共有化合物数が、論文補足 s2 の全 221,777 ペアで一致（不一致 0、s2 にない正のペア 0）。2026-09-27 に確認
- 同じファイルは GitHub の非公式ミラー（lingcheng99/Flavor-Network、donnate/Datasets など）にもあり、SHA-256 が Zenodo 版と一致
- zip 内 README の既知の問題: farnesol が食材（id 339）と化合物（id 951）の両方にある。README の勧めどおり食材としての farnesol を除いて使う
- zip の `__MACOSX/` は macOS のメタデータなので展開後に削除した

### 確認したが使わないもの

| 候補 | 取得元 | 利用条件 | 使わない理由 |
|---|---|---|---|
| FlavorDB（Garg et al. 2018, Nucleic Acids Research） | https://cosylab.iiitd.edu.in/flavordb/ （flavordb2 も同じ表示） | サイトのフッターに **CC BY-NC-SA 3.0 Unported**（"Copyright © 2017 All rights reserved. This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License"）。一括ダウンロードの提供と、スクレイピングの可否は**未確認** | 一括取得の手段が無く、ページ単位の取得になる。Ahn の Zenodo 版で目的が足りる |

### 参照のみ・分析には不使用: FlavorGraph（Park et al. 2021）

**参照のみ・分析には不使用。**本人の方針（2026-09-27）「どう学習されたか分かっていて、かつ手元で再生成できるものだけを使う。そうでなければ自作する」により、FlavorGraph の学習済み埋め込みもグラフも分析に使わない。香りの層は Ahn et al. 2011 の食材×化合物表から `experiments/exp-10/run.py` で再生成する。当初は後の手法比較のために取得を依頼されたため、方針変更の前に下記を `data/raw/flavorgraph/` に取得済み（gitignore 対象・コミットなし）。取得の記録として残す。同じ方針で Epicure（Hugging Face の Kaikaku/epicure-corpus-resources）の埋め込みも使わない（取得していない）

| ファイル（`raw/flavorgraph/`） | 取得元 | 取得日 | SHA-256 |
|---|---|---|---|
| `nodes_191120.csv`（8,298 ノード: 食材 6,653・化合物 1,645） | https://github.com/lamypark/FlavorGraph の `input/`（コミット `8d3472d0823f4542b2ce47f83e28046c41d2f06a` 固定の raw URL） | 2026-09-27 | `ea59d1858ae3a41de14aeabda32e6274693ea7897eb6ae1a3b7262bac5526d5a` |
| `edges_191120.csv`（ingr-ingr 111,355・ingr-fcomp 35,440・ingr-dcomp 384） | 同 | 同 | `af2c2324f34fc44493ecf2711787a50f16cc8c61c474dfae64194517a3f51399` |
| `dict_ingr2cate - Top300+FDB400+HyperFoods104=616.csv` | 同 | 同 | `846e942baadc2cc619f9c54deb21e69d408729660cee6d27d43104be48c7604d` |
| `node_classification_hub.csv` | 同 | 同 | `fad01dd2b3e8d12374979380b9af4f1f5c08e1eca2c23bb205224d29fe5da6ba` |
| `LICENSE`（Apache-2.0 本文） | 同リポジトリ直下 | 同 | `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` |
| `FlavorGraph_Node_Embedding.pickle`（学習済み 300 次元ノード埋め込み。dict: ノード id 文字列 → ndarray(300)、8,297 件。ノード表より 1 件少ない） | README の "Pickle file containing the 300D FlavorGraph node embeddings" の Google Drive リンク（file id `1MN2dGr-e8x09XSfj0kG4MahTRFY8GDw4`）。`https://drive.usercontent.google.com/download?id=<id>&export=download&confirm=t` で取得 | 2026-09-27 | `36671d66942931f3af436c35db7cab21ecfc0b913ec0654804f3ff3eb9051bb9` |

利用条件
- **リポジトリ: Apache-2.0**（GitHub のライセンス表示・`LICENSE`・README 末尾 "License: Apache License 2.0"）
- **論文: CC BY 4.0**（Scientific Reports 11, 931 (2021), https://doi.org/10.1038/s41598-020-79422-8）。Data availability 節に "Data and trained food representations are available at https://github.com/lamypark/FlavorGraph" とあり、埋め込みもこのリポジトリの配布物として扱った。ただし埋め込み本体は Google Drive にあり、Apache-2.0 がこのファイルに及ぶと明記した箇所は無い（**未確認**）
- グラフの元データ: 食材どうしの辺は Recipe1M（利用条件は配布ページが登録制で、公開ページに記載が無く**未確認**）、食材と化合物の辺は FlavorDB（サイト表示 CC BY-NC-SA 3.0）と HyperFoods。これらの条件が派生物にどう及ぶかは**未確認**
- 以上から、本リポジトリでは研究・非商用に限って使い、**生データも処理後のデータ（埋め込みから切り出したベクトルなど）もコミットしない**。使うときは再生成スクリプトだけコミットする
- 出典: Park, D., Kim, K., Kim, S., Spranger, M., & Kang, J. (2021). FlavorGraph: a large-scale food-chemical graph for generating food representations and recommending food pairings. *Scientific Reports*, 11, 931.

- `data/labels/aroma_mapping.csv`: 味覚スコアの 303 食材 → Ahn et al. 2011 の食材名の対応表（2026-09-27、Claude 作成・本人未確認）。`experiments/exp-10/build_mapping.py` が生成する（自動 = 名前の正規化で完全一致、手動 = スクリプト内の辞書、none = 理由つき）。auto 189・manual 81・none 33、対応率 89.1%（270/303）
- `data/labels/dish_perception.csv`: 本人が Exp-14 の目標13品に付けた感じ方（硬さ・とろみ・なめらかさ・甘さ・香ばしさ・温かさ、0〜5）。2026-09-27、採点ページ（Artifact の db）から書き出し。

## レシピの温度・時間（Exp-15、2026-09-28 確認）

本人の方針（2026-09-28）: 機械的な収集が許されている出典だけを使う。クックパッド・楽天（NII のデータセットは大学・公的研究機関限定）、RecipeNLG（非商用限定）、YouTube、利用規約で機械的収集を禁じるサイトは使わない。読み取った表は `experiments/exp-15-recipes/recipes.csv`（`build.py` が生成）。

### 使うもの

| ファイル（`raw/` 以下） | 取得元 | 取得日 | SHA-256 | 使う実験 |
|---|---|---|---|---|
| `wikibooks_cookbook/enwikibooks-20260901-pages-articles.xml.bz2`（203,255,444 bytes） | Wikimedia 公式ダンプ https://dumps.wikimedia.org/enwikibooks/20260901/ 。同じ場所の `enwikibooks-20260901-sha1sums.txt` の SHA-1 `68c95a78346e36ff9ee0b7c687a9af4873390d1b` と一致 | 2026-09-28 | `e3ef78fe67cf66bbfd65be49f8427e6b494913a390f5064960d4bd26a075b181` | Exp-15 |
| `wikibooks_cookbook/jawikibooks-20260901-pages-articles.xml.bz2`（29,919,367 bytes） | https://dumps.wikimedia.org/jawikibooks/20260901/ 。SHA-1 `444627f7bbcd126514fdda5e3e1cba57c746fa79` が sha1sums と一致 | 2026-09-28 | `d790dd030f30fc65a28d368b52e5c976b75fbeb97049cd5548e609edfd124ce9` | Exp-15 |
| `wikibooks_cookbook/recipes_parsed.mini.json`（3,895 レシピ） | Hugging Face gossminn/wikibooks-cookbook、コミット `49fb73ea07d2a1380c15197db5589934937457ed` 固定の `resolve/` URL。2024-07-31 に Wikibooks Cookbook をスクレイプしたもの | 2026-09-28 | `67fd704a6d9280742d2f217ad9f9e4f50921b84fcdefdff9bac749a518c4d46b` | Exp-15（ダンプから消えた1ページだけ） |
| `wikibooks_cookbook/README.md`（上のデータセットカード） | 同 | 2026-09-28 | `8d6f77a31b6755f4a312f518b629289073ebda9155e600b5a73d2f586d81ddf4` | 条件の確認 |
| `fukui_opendata/nanetukomekko.csv`（南越米っ子コンクール応援作品レシピ、丹南農林総合事務所） | 福井県オープンデータライブラリ「6. 観光・グルメ」https://www.pref.fukui.lg.jp/doc/dx-suishin/opendata/list_6.html の CSV（`list_6_d/fil/nanetukomekko.csv`）。cp932 | 2026-09-28 | `763acdbce43a48424de24f6f2dca18e3a996398700ee15b1215d2d774f41fa7e` | Exp-15 |
| `fukui_opendata/fukuinobi_recipe.csv`（「ふくい健幸美食」のレシピ、保健予防課） | 同 `list_6_d/fil/fukuinobi_recipe.csv` | 2026-09-28 | `4afb366088fa0d2e329fd63d47f2f4385ae1e0ce107e274500725f03fb9e9cf0` | Exp-15 |
| `fukui_opendata/` のほか 7 ファイル（ふくい朝ごはん・福井ふるさとの味・ふく囲鍋・ジビエ奥越・米粉・米料理・里芋のレシピ） | 同じ一覧ページの CSV | 2026-09-28 | fukuiasagohan `c306087a…afcfb`、fukuifurusatonoaji `c3994e98…79531`、fukuinabe_recipe `36e40425…b639`、jibieokueturesipi `1c41a26f…ba36`、komeko `a467b260…c6fd`、komeryouri `60abb469…69648`、satoimoresipi `012b4ace…e3c` | 探索のみ（対象の料理が温度・時間つきで無かった） |

利用条件
- **Wikibooks（英語版・日本語版）: CC BY-SA 4.0**。2026-09-28 に en.wikibooks.org/wiki/Cookbook:Poached_Egg と ja.wikibooks.org/wiki/料理本/ゆで卵 のフッターのライセンスリンク（`licenses/by-sa/4.0`）で確認。ダンプは Wikimedia が一括取得用に配布しているもの。再配布・改変可、表示と継承が条件。`recipes.csv` には各行の短い引用・ページ名・版番号・固定リンク（`?oldid=`）を残した。`recipes.csv` は引用を含むので CC BY-SA 4.0 の継承対象として扱う
- **Hugging Face gossminn/wikibooks-cookbook: CC BY-SA 4.0**（データセットカードの `license: cc-by-sa-4.0` と Hub のライセンス表示）。中身は Wikibooks の転載なので、元の条件（CC BY-SA 4.0）と同じ
- **福井県オープンデータライブラリ: CC BY 4.0**。https://www.pref.fukui.lg.jp/doc/dx-suishin/opendata/index.html の利用規約「当サイトにおいて公開するデータは、注のあるものを除いて、クリエイティブ・コモンズ表示4.0国際ライセンスの下に提供」。使った CSV に注は無かった
- 生データはコミットしない（容量の方針どおり）。出典表示: Wikibooks contributors, "Cookbook"（en.wikibooks.org）／ウィキブックス「料理本」（ja.wikibooks.org）／福井県オープンデータライブラリ

### 確認したが使わないもの

| 候補 | 取得元・場所 | 利用条件 | 使わない理由 |
|---|---|---|---|
| 高槻市 学校給食レシピ | BODIK https://data.bodik.jp/dataset/272078_gakkokyusyoku 、CSV を `raw/takatsuki_opendata/gakkokyusyokurecipi.csv` に取得（SHA-256 `169194fa309d8a315a7a4febd7fcd1cec509559451ac69c9c37437fb93c97836`、59 レシピ、令和8年8月1日現在） | CC BY 4.0（BODIK のライセンス欄） | 卵を使うのはスープの溶き卵 2 件だけで、対象の料理が無い |
| 鯖江市 さばえ地場産野菜の料理レシピ | ckan.odp.jig.jp の 202003003 → http://linkdata.org/api/1/rdf1s8262i/resipi.csv を `raw/sabae_opendata/resipi.csv` に取得（SHA-256 `613f929e…f859`） | CKAN 表示は CC BY-SA 4.0、linkdata の datapackage.json は CC BY 3.0 で**食い違う（未解決）** | 材料だけで手順が無い（詳細は PDF のリンク） |
| 東京都保健医療局「一人でもできる簡単レシピ」ほか 4 データセット | 東京都オープンデータカタログ（t000055d0000000467〜470）の CSV 44 個を `raw/tokyo_opendata/csv/` に取得 | CC BY | CSV は栄養価だけ（手順は PDF 側でカタログに無い）。1 つは 404 |
| e-Gov データポータル・BODIK・東京都カタログの「レシピ」「献立」検索 | CKAN API の package_search | — | 献立表（料理名の一覧）が大半で手順が無い |
| 福井県「ほっとするね ふるさとの味」の旧ページ | http://www.pref.fukui.lg.jp/doc/kenkou/furusatonoaji.html | — | 404。同じデータはオープンデータライブラリの「福井ふるさとの味」CSV として残っていた（上の表） |
| 農林水産省「うちの郷土料理」 | https://www.maff.go.jp/j/keikaku/syokubunka/k_ryouri/ | 未確認（政府標準利用規約の可能性） | 国の機関で、本人の方針の「自治体」に当たらない。今回は見送り |
| ROIS-DS 人文学オープンデータ共同利用センター「江戸料理レシピデータセット」（卵百珍） | https://codh.rois.ac.jp/edo-cooking/ | CC BY-SA 4.0（検索結果の記述、未確認） | 自治体でも Wikibooks でもない。江戸時代の本で温度の記述が無い見込み。見送り |

## 脂質量（Exp-11 油分の客観値、2026-09-28 夜 確認）

| ファイル | 取得元 | 取得日 | SHA-256 | 使う実験 |
|---|---|---|---|---|
| `raw/usda_fdc/sr_legacy.zip`（展開先 `raw/usda_fdc/FoodData_Central_sr_legacy_food_csv_2018-04/`） | USDA FoodData Central、SR Legacy（2018年4月版）の CSV 一式 https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_csv_2018-04.zip | 2026-09-28 | `b80817294b8850530aaedf2e515c02593b1824f763a0ff356e5c2081643e6fd0` | Exp-11 |

- **利用条件（本文確認、https://fdc.nal.usda.gov/api-guide/ 2026-09-28）**: "USDA FoodData Central data are in the public domain and they are not copyrighted." "They are published under CC0 1.0 Universal (CC0 1.0)"。許可は不要。出典として FoodData Central を挙げるよう求めている。推奨の引用: "U.S. Department of Agriculture, Agricultural Research Service. FoodData Central, 2019. fdc.nal.usda.gov."
- ダウンロードページ・FAQ には利用条件の記載が無く、API ガイドのページにある（上の引用）
- 使った値: nutrient_id 1004「Total lipid (fat)」（g/100g）。`experiments/exp-11/build_fat_content.py` が `labels/fat_content.csv` を作る
- 日本食品標準成分表（八訂）は今回使っていない。What's Cooking の食材名は英語で米国の商品形態（ひき肉の赤身割合・缶詰・タコスシーズニングなど）に合わせやすいため。八訂の利用条件は今回確認していない（Exp-14 の rules.yaml `fooddb` で数値を引いているが、公開サイトに載せる場合は別に確かめる）

| ファイル | 作成者 | 作成日 | 状態 | 使う実験 |
|---|---|---|---|---|
| `labels/fat_content.csv` | Claude（claude-opus-5-5）が食材ごとに SR Legacy の品名を選んだ（対応は build_fat_content.py の MAP、確かさは `match` 列: 一致 200・近い 86・代用 5・対応なし 12） | 2026-09-28 | 本人未確認。値は SR Legacy のまま、対応の選び方だけが Claude の判断 | Exp-11 |

## 食感の物性値（Exp-11 食感の層の作り直し、2026-09-29）

- ファイルは取得していない（`data/raw/` に追加なし）。論文・公的機関の数値だけを使い、値・出典・「出典／計算／仮」の別は `experiments/exp-11/texture_rules.yaml` に持つ
- 使ったのは数値（事実）の引用だけで、図表・本文は転載していない。本文を開けず検索結果の抜粋で確かめた値は、yaml の sources にそう書いた
- 本人の採点 `labels/dish_perception.csv`（Exp-14 で作成）を正解に使う

## 殻付き卵の熱物性と変性の速さ（Exp-17、2026-09-30）

- ファイルは取得していない。Di Lorenzo et al. (2025) Periodic cooking of eggs, Communications Engineering 4:5（CC BY-NC-ND 4.0）の Table 4 の数値（熱伝導率・密度・比熱・反応の A と Ea。熱物性の元は Abbasnezhad et al. 2016 Food Sci Nutr 4:42）を `experiments/exp-14/rules.yaml` の `sim.egg_kinetic` に引用した。数値（事実）の引用だけで、図表・本文は転載していない

## 料理の感じ方の追加採点（Exp-18、2026-09-30）

- `labels/dish_perception_v2_input.csv`: 本人が採点するための記入用ファイル。既存13品は `dish_perception.csv` の値、追加3品（ビーフステーキ・フライドポテト・ゆでじゃがいも）は空欄。説明の列（how）は Claude が書いた

