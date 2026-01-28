# consistency

![1 public function](https://img.shields.io/badge/functions-1-blue)
![No external deps](https://img.shields.io/badge/deps-none-brightgreen)

Intra-document style drift detection using sliding-window chi-squared analysis.

## Catalogue

| File | Function | What It Does |
|------|----------|-------------|
| `drift.py` | `compute_kilgarriff_drift` | Detects stylistic drift, splice points, and AI-generation signatures |
| `_thresholds.py` | _(internal)_ | Classification thresholds for pattern detection |

## Detected Patterns

| Pattern | Meaning |
|---------|---------|
| `consistent` | Natural human variation throughout |
| `gradual_drift` | Style shifts progressively over the document |
| `sudden_spike` | Abrupt discontinuity (possible splice or paste) |
| `suspiciously_uniform` | Unnaturally low variation (possible AI generation) |

## See Also

- [`authorship/kilgarriff.py`](../authorship/) -- the underlying chi-squared method (between-text comparison)
- [`viz/`](../viz/) for timeline and report visualizations of drift results
