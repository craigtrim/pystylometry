# pystylometry

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

Core package for stylometric analysis and authorship attribution.

## Module Map

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| [`lexical/`](lexical/) | Vocabulary diversity & richness | `compute_mtld`, `compute_yule`, `compute_ttr`, `compute_hapax_ratios` |
| [`readability/`](readability/) | Text readability scoring | `compute_flesch`, `compute_gunning_fog`, `compute_ari`, `compute_smog` |
| [`syntactic/`](syntactic/) | Sentence & parse structure | `compute_pos_ratios`, `compute_sentence_types`, `compute_advanced_syntactic` |
| [`authorship/`](authorship/) | Author attribution & comparison | `compute_burrows_delta`, `compute_kilgarriff`, `compute_compression_distance` |
| [`stylistic/`](stylistic/) | Style markers & vocabulary overlap | `compute_stylistic_markers`, `compute_vocabulary_overlap`, `compute_genre_register` |
| [`character/`](character/) | Character-level features | `compute_character_metrics` |
| [`ngrams/`](ngrams/) | N-gram entropy & sequences | `compute_extended_ngrams`, `compute_ngram_entropy` |
| [`dialect/`](dialect/) | Regional dialect detection | `compute_dialect` |
| [`consistency/`](consistency/) | Intra-document drift detection | `compute_kilgarriff_drift` |
| [`prosody/`](prosody/) | Rhythm & stress patterns | `compute_rhythm_prosody` |
| [`viz/`](viz/) | Visualization (PNG & interactive HTML) | `plot_drift_timeline`, `export_drift_report_jsx` |

## Shared Internals

| File | Purpose |
|------|---------|
| `_types.py` | All dataclass result types (e.g. `FleschResult`, `MTLDResult`, `KilgarriffDriftResult`) |
| `_normalize.py` | Text normalization for readability and stylometry pipelines |
| `_utils.py` | Shared tokenization and helper functions |
| `tokenizer.py` | Configurable tokenizer with sentence/word splitting |
| `cli.py` | Command-line interface (`pystylometry analyze`) |

## Installation Extras

```
pip install pystylometry                  # Core (lexical only)
pip install pystylometry[readability]     # + readability
pip install pystylometry[syntactic]       # + syntactic (requires spaCy)
pip install pystylometry[authorship]      # + authorship attribution
pip install pystylometry[all]             # Everything
```
