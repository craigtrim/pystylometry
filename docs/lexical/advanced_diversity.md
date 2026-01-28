# Advanced Lexical Diversity Metrics

## Length-Normalized Measures of Vocabulary Richness

This module provides four sophisticated lexical diversity metrics -- voc-D, MATTR, HD-D, and MSTTR -- that address the fundamental "text length problem" of simple TTR. Each metric normalizes for text length through a different mathematical approach, providing stable and comparable diversity measures across texts of different sizes.

---

## Theoretical Background

### Origins

The development of advanced lexical diversity metrics was driven by a well-known limitation of the Type-Token Ratio: longer texts systematically produce lower TTR values because common words repeat. This makes TTR unsuitable for comparing texts of different lengths, a frequent requirement in stylometry and language assessment.

McCarthy and Jarvis (2010) conducted a comprehensive validation study comparing multiple approaches to this problem, establishing MTLD, voc-D, and HD-D as the most reliable alternatives. Covington and McFall (2010) independently proposed MATTR as a computationally simple sliding-window approach. Malvern et al. (2004) developed the voc-D curve-fitting approach in the context of language development research.

### Mathematical Foundation

#### voc-D (Vocabulary D)

voc-D estimates diversity by fitting a mathematical curve to the relationship between sample size and TTR. The key insight is that the rate at which TTR declines with increasing sample size characterizes vocabulary diversity.

**Algorithm:**

1. Draw random samples of varying sizes from the text (sizes 10, 15, 20, ..., up to 100)
2. For each sample size, compute mean TTR across many random samples (default: 100)
3. Fit the theoretical curve:

```
TTR = D / sqrt(N)
```

Where:
- `D` = the diversity parameter (to be estimated)
- `N` = sample size

4. The D parameter is estimated via least-squares:

```
D = sum(TTR_i / sqrt(N_i)) / sum(1 / N_i)
```

5. Goodness of fit is measured by R-squared.

**Interpretation**: Higher D indicates greater lexical diversity. Typical D values range from 10 (very repetitive) to 100+ (highly diverse).

#### MATTR (Moving-Average Type-Token Ratio)

MATTR computes TTR using a fixed-size sliding window that moves across the text one token at a time, then averages all window TTRs.

**Formula:**

```
MATTR = (1 / (N - W + 1)) * sum(TTR(window_i)) for i = 1 to N - W + 1
```

Where:
- `N` = total tokens
- `W` = window size (default: 50)
- `TTR(window_i)` = types in window i / W

**Interpretation**: MATTR ranges from 0 to 1, like TTR, but is normalized by the fixed window size. Standard deviation across windows indicates whether diversity is uniform or variable throughout the text.

#### HD-D (Hypergeometric Distribution D)

HD-D uses probability theory to estimate diversity. For each word type, it computes the probability that the type would NOT appear in a random sample of fixed size, then sums these probabilities across all types.

**Formula:**

For each word type with frequency `f`:

```
P(not in sample) = ((N - f) / N) ^ S
```

Where:
- `N` = total tokens
- `f` = frequency of the word type
- `S` = sample size (default: 42)

```
HD-D = sum(P(not in sample)) for all types
```

**Interpretation**: Higher HD-D indicates that more word types would be missed in a random sample, which paradoxically indicates greater diversity (more rare types). The implementation uses a simplified approximation of the hypergeometric distribution.

#### MSTTR (Mean Segmental Type-Token Ratio)

MSTTR divides text into non-overlapping segments of equal size, computes TTR for each segment, then averages.

**Formula:**

```
MSTTR = (1 / K) * sum(TTR(segment_i)) for i = 1 to K
```

Where:
- `K` = floor(N / segment_size)
- Remaining tokens that do not form a complete segment are discarded

**Interpretation**: MSTTR ranges from 0 to 1. Unlike MATTR, segments are independent (non-overlapping), making the standard deviation across segments a more interpretable measure of vocabulary consistency.

### Comparison of Methods

| Metric | Normalization Approach | Typical Range | Min Tokens | Key Advantage |
|--------|----------------------|---------------|------------|---------------|
| voc-D | Curve fitting | 10-100+ | 100 | Theoretically grounded |
| MATTR | Sliding window | 0-1 | window_size | Simple, fast |
| HD-D | Probability-based | varies | sample_size | Mathematically rigorous |
| MSTTR | Fixed segments | 0-1 | segment_size | Independent samples |

---

## Implementation

### Core Algorithms

```python
def compute_vocd_d(text, sample_size=35, num_samples=100, min_tokens=100,
                   random_seed=None, chunk_size=1000) -> VocdDResult

def compute_mattr(text, window_size=50, chunk_size=1000) -> MATTRResult

def compute_hdd(text, sample_size=42, chunk_size=1000) -> HDDResult

def compute_msttr(text, segment_size=100, chunk_size=1000) -> MSTTRResult
```

All four functions:
1. Tokenize input (lowercase, strip punctuation)
2. Validate minimum text length (raise `ValueError` if insufficient)
3. Compute the metric
4. Wrap results in Distribution objects
5. Return typed result dataclass with metadata

### Key Features

1. **Consistent API**: All four metrics share a common interface pattern with `chunk_size` parameter
2. **Minimum length validation**: Each metric raises `ValueError` if text is too short, with informative error messages
3. **Distribution objects**: Results include Distribution dataclasses for fingerprinting integration
4. **Reproducibility**: `compute_vocd_d` accepts an optional `random_seed` parameter
5. **Comprehensive metadata**: Token counts, type counts, simple TTR, and metric-specific details

### Return Types

**VocdDResult:**

| Field | Type | Description |
|-------|------|-------------|
| `d_parameter` | `float` | The D diversity parameter |
| `curve_fit_r_squared` | `float` | Goodness of curve fit (0-1) |
| `sample_count` | `int` | Number of sample sizes tested |
| `optimal_sample_size` | `int` | Sample size parameter used |
| `d_parameter_dist` | `Distribution` | Distribution of D values |
| `curve_fit_r_squared_dist` | `Distribution` | Distribution of R-squared |

**MATTRResult:**

| Field | Type | Description |
|-------|------|-------------|
| `mattr_score` | `float` | Average TTR across all windows |
| `window_size` | `int` | Window size used |
| `window_count` | `int` | Number of windows analyzed |
| `ttr_std_dev` | `float` | Std dev of TTR across windows |
| `min_ttr` | `float` | Minimum window TTR |
| `max_ttr` | `float` | Maximum window TTR |

**HDDResult:**

| Field | Type | Description |
|-------|------|-------------|
| `hdd_score` | `float` | HD-D score |
| `sample_size` | `int` | Hypothetical sample size used |
| `type_count` | `int` | Number of unique types |
| `token_count` | `int` | Total token count |

**MSTTRResult:**

| Field | Type | Description |
|-------|------|-------------|
| `msttr_score` | `float` | Mean TTR across segments |
| `segment_size` | `int` | Tokens per segment |
| `segment_count` | `int` | Number of complete segments |
| `ttr_std_dev` | `float` | Std dev of segment TTRs |
| `min_ttr` | `float` | Minimum segment TTR |
| `max_ttr` | `float` | Maximum segment TTR |
| `segment_ttrs` | `list[float]` | TTR for each segment |

---

## Usage

### API Examples

**voc-D (curve fitting):**

```python
from pystylometry.lexical import compute_vocd_d

result = compute_vocd_d(text, sample_size=35, num_samples=100, random_seed=42)
print(f"D parameter: {result.d_parameter:.2f}")
print(f"Curve fit R-squared: {result.curve_fit_r_squared:.3f}")
print(f"Sample sizes tested: {result.sample_count}")
```

**MATTR (sliding window):**

```python
from pystylometry.lexical import compute_mattr

result = compute_mattr(text, window_size=50)
print(f"MATTR score: {result.mattr_score:.3f}")
print(f"TTR std dev: {result.ttr_std_dev:.3f}")
print(f"TTR range: {result.min_ttr:.3f} to {result.max_ttr:.3f}")
print(f"Windows analyzed: {result.window_count}")
```

**HD-D (hypergeometric):**

```python
from pystylometry.lexical import compute_hdd

result = compute_hdd(text, sample_size=42)
print(f"HD-D score: {result.hdd_score:.3f}")
print(f"Types: {result.type_count}, Tokens: {result.token_count}")
```

**MSTTR (fixed segments):**

```python
from pystylometry.lexical import compute_msttr

result = compute_msttr(text, segment_size=100)
print(f"MSTTR score: {result.msttr_score:.3f}")
print(f"Segments: {result.segment_count}")
print(f"Segment TTRs: {[f'{t:.3f}' for t in result.segment_ttrs]}")
print(f"Tokens discarded: {result.metadata['tokens_discarded']}")
```

**Comprehensive comparison:**

```python
from pystylometry.lexical import (
    compute_vocd_d, compute_mattr, compute_hdd, compute_msttr
)

vocd = compute_vocd_d(text, random_seed=42)
mattr = compute_mattr(text, window_size=50)
hdd = compute_hdd(text, sample_size=42)
msttr = compute_msttr(text, segment_size=100)

print(f"voc-D:  {vocd.d_parameter:.2f} (R^2={vocd.curve_fit_r_squared:.3f})")
print(f"MATTR:  {mattr.mattr_score:.3f} (std={mattr.ttr_std_dev:.3f})")
print(f"HD-D:   {hdd.hdd_score:.3f}")
print(f"MSTTR:  {msttr.msttr_score:.3f} (std={msttr.ttr_std_dev:.3f})")
```

---

## Limitations

1. **Minimum text length requirements**: Each metric requires a minimum number of tokens (voc-D: 100, MATTR: window_size, HD-D: sample_size, MSTTR: segment_size). Texts below these thresholds raise `ValueError`.

2. **Parameter sensitivity**: All four metrics have tunable parameters (window size, sample size, segment size) that affect results. There is no universally optimal parameter choice; standard defaults follow published recommendations.

3. **voc-D randomness**: Because voc-D uses random sampling, results vary between runs unless a random seed is specified. The simplified curve model `TTR = D/sqrt(N)` may not fit all text types equally well.

4. **MATTR window overlap**: Adjacent MATTR windows share `W-1` tokens, making them non-independent. This means the standard deviation across windows underestimates true variability.

5. **MSTTR information loss**: MSTTR discards tokens that do not form a complete final segment. For a 250-word text with segment size 100, 50 tokens are discarded.

6. **HD-D approximation**: The implementation uses a simplified approximation `((N-f)/N)^S` rather than the exact hypergeometric distribution, which may introduce small errors for very small texts.

7. **No cross-metric calibration**: The four metrics use different scales and are not directly comparable in absolute terms. They should be compared across texts using the same metric and parameters.

---

## References

- McCarthy, P. M., & Jarvis, S. (2010). MTLD, vocd-D, and HD-D: A validation study of sophisticated approaches to lexical diversity assessment. *Behavior Research Methods*, 42(2), 381-392.
- Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The moving-average type-token ratio (MATTR). *Journal of Quantitative Linguistics*, 17(2), 94-100.
- Malvern, D., Richards, B., Chipere, N., & Duran, P. (2004). *Lexical Diversity and Language Development: Quantification and Assessment*. Palgrave Macmillan.
- Johnson, W. (1944). Studies in language behavior: I. A program of research. *Psychological Monographs*, 56(2), 1-15.
- Koizumi, R., & In'nami, Y. (2012). Effects of text length on lexical diversity measures: Using short texts with less than 200 tokens. *System*, 40(4), 554-564.
- Zenker, F., & Kyle, K. (2021). Investigating minimum text lengths for lexical diversity indices. *Assessing Writing*, 47, 100505.
