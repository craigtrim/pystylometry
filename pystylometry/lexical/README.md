# lexical

![11 public functions](https://img.shields.io/badge/functions-11-blue)
![No external deps](https://img.shields.io/badge/deps-none-brightgreen)

Vocabulary diversity, richness, and frequency analysis.

## Catalogue

| File | Functions | What It Measures |
|------|-----------|-----------------|
| `ttr.py` | `compute_ttr` | Type-Token Ratio (basic vocabulary diversity) |
| `mtld.py` | `compute_mtld` | Measure of Textual Lexical Diversity |
| `yule.py` | `compute_yule` | Yule's K and I (frequency spectrum measures) |
| `hapax.py` | `compute_hapax_ratios`, `compute_hapax_with_lexicon_analysis` | Hapax legomena, Honore's R, Sichel's S |
| `advanced_diversity.py` | `compute_vocd_d`, `compute_mattr`, `compute_hdd`, `compute_msttr` | VocD-D, MATTR, HD-D, MSTTR |
| `function_words.py` | `compute_function_words` | Function word frequencies by category |
| `word_frequency_sophistication.py` | `compute_word_frequency_sophistication` | Vocabulary sophistication via frequency bands |

## See Also

- [`authorship/`](../authorship/) uses lexical features for attribution
- [`stylistic/vocabulary_overlap.py`](../stylistic/) for Jaccard, Dice, and KL divergence between texts
