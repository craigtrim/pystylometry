# readability

![10 public functions](https://img.shields.io/badge/functions-10-blue)
![No external deps](https://img.shields.io/badge/deps-none-brightgreen)

Text readability scoring using established formulas from educational and linguistic research.

## Catalogue

| File | Functions | Formula |
|------|-----------|---------|
| `flesch.py` | `compute_flesch` | Flesch Reading Ease & Flesch-Kincaid Grade Level |
| `gunning_fog.py` | `compute_gunning_fog` | Gunning Fog Index (complex word ratio) |
| `coleman_liau.py` | `compute_coleman_liau` | Coleman-Liau Index (character-based) |
| `ari.py` | `compute_ari` | Automated Readability Index |
| `smog.py` | `compute_smog` | SMOG Grade (polysyllabic word count) |
| `additional_formulas.py` | `compute_dale_chall`, `compute_fry`, `compute_forcast`, `compute_linsear_write`, `compute_powers_sumner_kearl` | Dale-Chall, Fry Graph, FORCAST, Linsear Write, Powers-Sumner-Kearl |
| `syllables.py` | _(internal)_ | Syllable counting engine |
| `complex_words.py` | _(internal)_ | Complex word detection heuristics |

## See Also

- [`_normalize.py`](../_normalize.py) for text normalization applied before readability scoring
