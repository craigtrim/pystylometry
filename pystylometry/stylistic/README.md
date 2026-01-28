# stylistic

![4 public functions](https://img.shields.io/badge/functions-4-blue)
![No external deps](https://img.shields.io/badge/deps-none-brightgreen)

Style markers, vocabulary overlap, cohesion/coherence, and genre/register classification.

## Catalogue

| File | Function | What It Measures |
|------|----------|-----------------|
| `markers.py` | `compute_stylistic_markers` | Contractions, intensifiers, hedges, modals, negation, punctuation style |
| `vocabulary_overlap.py` | `compute_vocabulary_overlap` | Jaccard, Dice, Cosine similarity, KL divergence, overlap coefficient |
| `cohesion_coherence.py` | `compute_cohesion_coherence` | Referential cohesion, connectives, coherence measures |
| `genre_register.py` | `compute_genre_register` | Formality scoring, register classification, genre prediction |

## See Also

- [`lexical/function_words.py`](../lexical/) for function word distributions (complements marker analysis)
- [`dialect/`](../dialect/) for regional variant detection (British vs. American)
