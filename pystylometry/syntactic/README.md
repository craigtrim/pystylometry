# syntactic

![4 public functions](https://img.shields.io/badge/functions-4-blue)
![Requires spaCy](https://img.shields.io/badge/requires-spaCy-orange)

Sentence structure, part-of-speech, and parse tree analysis.

## Catalogue

| File | Function | What It Measures |
|------|----------|-----------------|
| `pos_ratios.py` | `compute_pos_ratios` | Noun/verb/adjective/adverb ratios |
| `sentence_stats.py` | `compute_sentence_stats` | Sentence length, word length distributions |
| `sentence_types.py` | `compute_sentence_types` | Declarative, interrogative, imperative, exclamatory classification |
| `advanced_syntactic.py` | `compute_advanced_syntactic` | Parse tree depth, clausal density, passive voice, T-units, dependency distance, subordination/coordination ratios |

## See Also

- [`stylistic/`](../stylistic/) for higher-level style features built on syntactic foundations
- [`ngrams/`](../ngrams/) for POS n-gram sequences via `compute_extended_ngrams(text, pos=True)`
