# authorship

![7 public functions](https://img.shields.io/badge/functions-7-blue)
![No external deps](https://img.shields.io/badge/deps-none-brightgreen)

Authorship attribution methods for comparing texts and determining likely authorship.

## Catalogue

| File | Functions | Method |
|------|-----------|--------|
| `burrows_delta.py` | `compute_burrows_delta`, `compute_cosine_delta` | Classic Delta and angular distance variant |
| `zeta.py` | `compute_zeta` | Zeta method for marker word detection |
| `kilgarriff.py` | `compute_kilgarriff` | Chi-squared corpus comparison |
| `additional_methods.py` | `compute_minmax`, `compute_johns_delta` | MinMax distance, Quadratic/Weighted Delta |
| `compression.py` | `compute_compression_distance` | Normalized Compression Distance (NCD) |

## See Also

- [`consistency/`](../consistency/) applies `compute_kilgarriff` in sliding windows for intra-document drift detection
- [`lexical/`](../lexical/) provides the vocabulary features many attribution methods rely on
