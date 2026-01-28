# Tests

![1022 tests](https://img.shields.io/badge/tests-1022-brightgreen)
![pytest](https://img.shields.io/badge/framework-pytest-blue)

Test suite organized by source module. Run with `make test` or `pytest tests/`.

## Directory Map

| Folder | Tests | Covers |
|--------|-------|--------|
| [`readability/`](readability/) | 56 | ARI, Coleman-Liau, Gunning Fog, Flesch, SMOG, Dale-Chall, Fry, FORCAST, Linsear Write, Powers-Sumner-Kearl |
| [`lexical/`](lexical/) | 52 | TTR, MTLD, Yule, Hapax, MATTR, VocD-D, HD-D, function words, word frequency |
| [`stylistic/`](stylistic/) | 26 | Markers, vocabulary overlap, cohesion/coherence, genre/register |
| [`syntactic/`](syntactic/) | 20 | POS ratios, sentence types, parse tree depth, passive voice, T-units |
| [`dialect/`](dialect/) | 13 | Dialect detection, chunking, spelling/grammar/vocabulary matching |
| [`common/`](common/) | 10 | API surface, normalization, spaCy integration, edge cases |
| [`character/`](character/) | 8 | Character-level metrics, special characters |
| [`ngrams/`](ngrams/) | 6 | Extended n-grams, skipgrams, Shannon entropy |
| [`authorship/`](authorship/) | 4 | NCD compression, MinMax, John's Delta, integration |

## Shared Fixtures

[`conftest.py`](conftest.py) provides `sample_text`, `long_text`, and `multi_sentence_text` fixtures available to all tests.

[`fixtures/`](fixtures/) contains Project Gutenberg texts (Doyle, Dickens) and Kilgarriff test corpora (single-author, spliced, AI-generated).
