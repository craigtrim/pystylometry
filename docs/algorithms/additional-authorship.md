# Additional Authorship Attribution Methods

## Overview

This module extends pystylometry's authorship attribution capabilities with three additional methods from the stylometry literature.

## Methods

### MinMax Distance (`compute_minmax`)

Burrows' original min-max method computes authorship distance by comparing the minimum and maximum relative frequency differences across the most frequent words.

```python
from pystylometry.authorship import compute_minmax

result = compute_minmax(text1, text2, mfw=100)
print(f"MinMax distance: {result.distance:.4f}")
```

**Parameters:**
- `text1`, `text2`: Texts to compare
- `mfw`: Number of most frequent words to consider (default: 100)

### John's Delta Variations (`compute_johns_delta`)

Two Delta variants that use different distance calculations:

- **Quadratic Delta**: Root mean squared z-score difference (Euclidean-inspired)
- **Weighted Delta**: Inverse-rank weighted mean absolute difference (gives more weight to the most frequent words)

```python
from pystylometry.authorship import compute_johns_delta

result = compute_johns_delta(text1, text2, mfw=100, method="quadratic")
print(f"Delta score: {result.delta:.4f}")
```

**Parameters:**
- `text1`, `text2`: Texts to compare
- `mfw`: Number of most frequent words (default: 100)
- `method`: `"quadratic"` or `"weighted"` (default: `"quadratic"`)

### Normalized Compression Distance (`compute_compression_distance`)

A language-independent similarity metric based on Kolmogorov complexity, approximated through real-world compressors. If two texts share statistical regularities, compressing them together yields better compression than compressing separately.

```python
from pystylometry.authorship import compute_compression_distance

result = compute_compression_distance(text1, text2, compressor="gzip")
print(f"NCD: {result.ncd:.3f}")
```

**Interpretation:**
- NCD ~ 0: Texts are maximally similar
- NCD ~ 1: Texts are maximally different
- Typical same-author pairs: 0.3–0.6
- Typical different-author pairs: 0.6–0.9

**Compressor options:** `"gzip"` (default), `"zlib"`, `"bz2"`

## References

- Burrows, J. F. (1992). Not unless you ask nicely. *Literary and Linguistic Computing*.
- Burrows, J. (2005). Who wrote Shamela? *Literary and Linguistic Computing*.
- Argamon, S. (2008). Interpreting Burrows's Delta. *Literary and Linguistic Computing*.
- Cilibrasi, R., & Vitányi, P. M. (2005). Clustering by compression. *IEEE Transactions on Information Theory*, 51(4), 1523–1545.
