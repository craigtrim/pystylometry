# Kilgarriff Chi-Squared Drift Detection

## Intra-Document Stylistic Consistency Analysis

---

## Theoretical Background

### Origins

Adam Kilgarriff introduced the chi-squared method for corpus comparison in his 2001 paper "Comparing Corpora" (Kilgarriff 97-133). The original method compares two separate text corpora by measuring statistical distance between their word frequency distributions. Pystylometry extends this method to intra-document analysis: rather than comparing two separate texts, it compares sequential chunks within a single document to detect stylistic drift, discontinuities, and consistency patterns.

This extension was motivated by practical applications in authorship verification and AI-generated content detection. Eder (2015) demonstrated that stylometric methods are sensitive to text length and sampling strategy. Juola (2006) surveyed authorship attribution methods, noting that intra-document consistency is an underexplored signal. The drift detection approach fills this gap by measuring how a document's style evolves from beginning to end.

### Mathematical Foundation

**Chi-squared statistic** between two text windows A and B:

For the top N most frequent words in the combined window:

```
chi_squared(w) = (O(w,A) - E(w,A))^2 / E(w,A) + (O(w,B) - E(w,B))^2 / E(w,B)
```

Where:
- `O(w,T)` = observed count of word w in text T
- `E(w,T) = count(w, joint) * size(T) / size(joint)` = expected count under the null hypothesis that both windows share the same distribution

Total chi-squared: `chi_sq = SUM chi_squared(w)` for w in top N words.

**Sliding windows**:

```
overlap_ratio = (window_size - stride) / window_size
```

Default: `window_size=1000`, `stride=500` produces 50% overlap.

**Trend detection** via linear regression:

```
slope = cov(x, chi_values) / var(x)
R_squared = 1 - (SS_res / SS_tot)
```

Where x = [0, 1, 2, ...] is the comparison index.

**Pattern classification thresholds**:

| Threshold | Value | Purpose |
|-----------|-------|---------|
| `UNIFORM_CV_THRESHOLD` | 0.15 | CV below this is suspiciously uniform |
| `UNIFORM_MEAN_THRESHOLD` | 50.0 | Mean below this (with low CV) suggests AI |
| `SPIKE_RATIO` | 2.5 | Max/mean ratio above this indicates a spike |
| `SPIKE_MIN_ABSOLUTE` | 100.0 | Minimum absolute spike size |
| `TREND_SLOPE_THRESHOLD` | 5.0 | Minimum slope for drift detection |
| `TREND_R_SQUARED_THRESHOLD` | 0.3 | Minimum R-squared for meaningful trend |
| `MIN_WINDOWS` | 3 | Minimum windows for any analysis |
| `RECOMMENDED_WINDOWS` | 5 | Recommended minimum for reliable classification |

### Interpretation

The function classifies detected patterns into four named signatures:

**Consistent**: Low, stable chi-squared across all window pairs. The coefficient of variation is moderate, and no trends or outliers are detected. This pattern is characteristic of natural human writing with normal stylistic variation from a single author in a single session.

**Gradual Drift**: Chi-squared values show a monotonic trend (increasing or decreasing) with significant slope and R-squared. Possible causes include author fatigue (style degrades over time), topic evolution affecting vocabulary, or editing that becomes progressively heavier.

**Sudden Spike**: One or more window pairs produce chi-squared values significantly exceeding the mean (by a factor of `SPIKE_RATIO` or more). This indicates an abrupt stylistic boundary. Common causes include pasted content from a different source, a section written by a different author, or heavy localized editing.

**Suspiciously Uniform**: Near-zero variance in chi-squared scores (CV below `UNIFORM_CV_THRESHOLD`) combined with low mean (below `UNIFORM_MEAN_THRESHOLD`). This pattern is uncharacteristic of natural human writing and may indicate AI-generated content, text generated in a single session without revision, or copy-pasted repetitive content.

---

## Implementation

### Core Algorithm

1. **Tokenization**: Convert text to lowercase alphabetic tokens
2. **Sliding windows**: Create overlapping windows with configurable size and stride
3. **Pairwise comparison**: Compare window pairs using Kilgarriff's chi-squared method
4. **Statistics**: Compute mean, standard deviation, min, max, and trend across all comparisons
5. **Pattern classification**: Apply threshold-based decision tree to classify the pattern
6. **Confidence scoring**: Scale confidence based on data quantity (number of windows)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `text` | (required) | Input text to analyze |
| `window_size` | 1000 | Tokens per sliding window |
| `stride` | 500 | Tokens to advance between windows |
| `comparison_mode` | `"sequential"` | `"sequential"`, `"all_pairs"`, or `"fixed_lag"` |
| `lag` | 1 | Window distance for `"fixed_lag"` mode |
| `n_words` | 500 | Top N most frequent words for chi-squared |

### Key Features

- **Sliding window support**: Configurable overlap via `stride` parameter. 50% overlap (default) produces smooth drift curves with reduced boundary artifacts.
- **Three comparison modes**: Sequential (adjacent windows), all pairs (full distance matrix), and fixed lag (compare windows at specified distance).
- **Pattern classification**: Automatic classification into named patterns with confidence scores.
- **Top contributing words**: For each pairwise comparison, the top 10 words contributing most to the chi-squared value are recorded, providing interpretability.
- **Distance matrix**: In `"all_pairs"` mode, a symmetric distance matrix is returned for advanced analysis.
- **Threshold transparency**: All classification thresholds are included in the result, enabling reproducibility and customization.
- **Graceful degradation**: Returns `"insufficient_data"` or `"marginal_data"` status with explanatory messages when text is too short.

### Return Value

The function returns a `KilgarriffDriftResult` dataclass containing:

- `status`: `"success"`, `"marginal_data"`, or `"insufficient_data"`
- `status_message`: Human-readable explanation of status
- `pattern`: Classified pattern name (`"consistent"`, `"gradual_drift"`, `"sudden_spike"`, `"suspiciously_uniform"`, `"unknown"`)
- `pattern_confidence`: Confidence score (0.0-1.0)
- `mean_chi_squared` / `std_chi_squared` / `max_chi_squared` / `min_chi_squared`: Statistics
- `max_location`: Index of the maximum chi-squared comparison
- `trend`: Linear regression slope of chi-squared over document
- `pairwise_scores`: List of per-comparison dictionaries with chi-squared, degrees of freedom, top contributing words, and window sizes
- `window_size` / `stride` / `overlap_ratio` / `comparison_mode` / `window_count`: Configuration
- `distance_matrix`: Full distance matrix (only in `"all_pairs"` mode)
- `thresholds`: Dictionary of all classification thresholds used
- `metadata`: Total tokens, tokens per window, trend R-squared, method identifier

---

## Usage

### API Examples

```python
from pystylometry.consistency import compute_kilgarriff_drift

# Basic drift detection
result = compute_kilgarriff_drift(text)
print(f"Pattern: {result.pattern}")
print(f"Confidence: {result.pattern_confidence:.2f}")
print(f"Mean chi-squared: {result.mean_chi_squared:.1f}")
print(f"Std chi-squared: {result.std_chi_squared:.1f}")

# Custom sliding window
result = compute_kilgarriff_drift(
    text,
    window_size=2000,
    stride=1000,
    n_words=500,
)
print(f"Windows: {result.window_count}")
print(f"Overlap: {result.overlap_ratio:.0%}")

# Check for AI-generated content
result = compute_kilgarriff_drift(text)
if result.pattern == "suspiciously_uniform":
    print("Warning: Text shows unusually uniform style")
    print(f"CV: {result.std_chi_squared / result.mean_chi_squared:.4f}")

# Find splice location
if result.pattern == "sudden_spike":
    print(f"Style change detected at window {result.max_location}")
    spike = result.pairwise_scores[result.max_location]
    print(f"Chi-squared at spike: {spike['chi_squared']:.1f}")
    print(f"Top contributing words: {spike['top_words'][:5]}")

# Detect gradual drift
if result.pattern == "gradual_drift":
    print(f"Trend slope: {result.trend:.4f} chi-sq per comparison")

# Handle insufficient data
if result.status == "insufficient_data":
    print(result.status_message)

# All-pairs mode for full distance matrix
result = compute_kilgarriff_drift(
    text,
    comparison_mode="all_pairs",
)
if result.distance_matrix:
    print(f"Matrix size: {len(result.distance_matrix)}x{len(result.distance_matrix)}")

# Inspect thresholds
print(f"Thresholds used: {result.thresholds}")
```

---

## Limitations

### Window Size Sensitivity

Small windows (under 500 tokens) produce noisy chi-squared values due to sparse word counts. Large windows (over 2000 tokens) smooth over genuine stylistic boundaries. The default of 1000 tokens balances statistical reliability against detection granularity, but optimal window size depends on the expected scale of stylistic variation.

### Minimum Text Length

The method requires at least 3 windows (approximately `window_size + 2 * stride` tokens) for any analysis, and recommends at least 5 windows for reliable pattern classification. Texts shorter than approximately 2500 words (with default parameters) will receive `"insufficient_data"` or `"marginal_data"` status.

### Independence Assumption

The chi-squared test assumes independent observations. Words in natural language are not independent due to syntactic and semantic constraints. The chi-squared value should be interpreted as a relative distance metric rather than a formal test statistic with p-value interpretation.

### Threshold Calibration

The pattern classification thresholds are initial estimates calibrated against a limited set of test corpora. They may require adjustment for specific domains or genres. All thresholds are exposed in the result object for transparency.

### Genre Effects

Chi-squared baselines vary by genre. Academic papers, novels, and technical documentation have different natural variation levels. The pattern classifications are most reliable when comparing within a single genre.

### Stride and Overlap

Overlapping windows share tokens, creating correlation between adjacent chi-squared values. This correlation is beneficial for smooth curve visualization but means adjacent chi-squared values are not statistically independent. The trend detection (linear regression) is robust to this correlation, but the standard deviation may be slightly underestimated.

---

## References

Kilgarriff, Adam. "Comparing Corpora." *International Journal of Corpus Linguistics*, vol. 6, no. 1, 2001, pp. 97-133. doi:10.1075/ijcl.6.1.05kil

Eder, Maciej. "Does Size Matter? Authorship Attribution, Small Samples, Big Problem." *Digital Scholarship in the Humanities*, vol. 30, no. 2, 2015, pp. 167-182.

Juola, Patrick. "Authorship Attribution." *Foundations and Trends in Information Retrieval*, vol. 1, no. 3, 2006, pp. 233-334.

Eder, Maciej, et al. "Stylometry with R: A Package for Computational Text Analysis." *The R Journal*, vol. 8, no. 1, 2016, pp. 107-121.

Stamatatos, Efstathios. "A Survey of Modern Authorship Attribution Methods." *Journal of the American Society for Information Science and Technology*, vol. 60, no. 3, 2009, pp. 538-556.
