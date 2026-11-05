# Exp-10 run_log

- 実行: `uv run python experiments/exp-10/run.py`（2026-09-27）
- Python 3.12.3, numpy 2.5.3, scipy 1.18.1, gensim 4.4.0, scikit-learn 1.9.1, matplotlib 3.11.2
- SEED 42、ΔN_s の対照 20 回
- 所要時間: 全体 132.2 秒（s2 照合 0.8 秒、PPMI 0.2 秒、ΔN_s 127.5 秒）

```json
{
 "sha256_ok": {
  "data/raw/ahn2011_zenodo/flavor_network_data.zip": true,
  "data/raw/ahn2011_zenodo/ingr_comp/ingr_comp.tsv": true,
  "data/raw/ahn2011_zenodo/ingr_comp/ingr_info.tsv": true,
  "data/raw/ahn2011_zenodo/ingr_comp/comp_info.tsv": true,
  "data/raw/ahn2011/srep00196-s2.csv": true,
  "data/raw/ahn2011/srep00196-s3.csv": true
 },
 "s2_check": {
  "s2_pairs": 221777,
  "mismatch": 0,
  "missing_in_table": 0,
  "extra_positive_pairs": 0
 },
 "ahn_ingredients_with_compounds": 1524,
 "ahn_compounds": 1107,
 "ahn_compounds_per_ingredient": {
  "median": 2.0,
  "mean": 24.133858267716537,
  "max": 239,
  "min": 1
 },
 "raw_sha256_matches": true,
 "vectors_source": "読み込み: data/processed/exp01_word2vec.kv",
 "vectors_sha256": "c958f8aea8a73ed9ce1fb220402b09d697c84d6bb9203d2b86029465064e06f1",
 "ppmi_vocab": 3336
}
```
