# ngrams

![4 public functions](https://img.shields.io/badge/functions-4-blue)
![No external deps](https://img.shields.io/badge/deps-none-brightgreen)

N-gram generation, entropy computation, and sequence analysis.

## Catalogue

| File | Functions | What It Measures |
|------|-----------|-----------------|
| `entropy.py` | `compute_ngram_entropy`, `compute_character_bigram_entropy`, `compute_word_bigram_entropy` | Shannon entropy at character and word n-gram levels |
| `extended_ngrams.py` | `compute_extended_ngrams` | Word, character, and POS n-gram profiles with frequency distributions |

## See Also

- [`syntactic/`](../syntactic/) provides POS tags consumed by `compute_extended_ngrams(text, pos=True)`
- [`character/`](../character/) for character-level features without n-gram structure
