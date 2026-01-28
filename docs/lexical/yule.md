# Yule's K and I Statistics

## Frequency-Spectrum Measures of Vocabulary Repetitiveness and Diversity

Yule's K and I statistics quantify vocabulary richness by analyzing the frequency distribution of words in a text. Rather than counting unique types directly, these metrics examine how words are distributed across frequency classes, providing a deeper characterization of vocabulary usage patterns.

---

## Theoretical Background

### Origins

George Udny Yule introduced his characteristic constant K in his 1944 monograph *The Statistical Study of Literary Vocabulary*, one of the foundational works in quantitative stylistics. Yule sought a measure of vocabulary richness that would be independent of text length -- a problem that had plagued earlier metrics including simple TTR.

Yule's insight was to base his measure on the frequency spectrum: the distribution of how many words appear once, twice, three times, and so on. By examining this second-order structure, Yule's K captures repetitiveness patterns that are more stable across text lengths than first-order measures like TTR.

The complementary statistic I (Yule's Inverse, or Yule's Index of Diversity) was later derived as the reciprocal formulation, providing a diversity-oriented interpretation where higher values indicate greater lexical variety.

### Mathematical Foundation

Both K and I are derived from the frequency spectrum of a text. Define:

- `N` = total number of tokens
- `V` = vocabulary size (unique types)
- `V_m` = number of types occurring exactly `m` times (frequency spectrum)

The key intermediate quantity is:

```
S = sum(m^2 * V_m) for all m >= 1
```

This sum weights each frequency class by the square of its frequency, emphasizing words that appear many times.

**Yule's K** (vocabulary repetitiveness):

```
K = 10^4 * (S - N) / N^2
```

The factor of 10,000 is a scaling constant for convenient numerical values. Higher K indicates more vocabulary repetition (less diversity).

**Yule's I** (vocabulary diversity):

```
I = V^2 / (S - N)
```

I is inversely related to K. Higher I indicates greater vocabulary diversity.

**Relationship between K and I:**

```
K * I = 10^4 * V^2 / N^2
```

When the denominator `S - N = 0` (which occurs when every word appears exactly once, i.e., `V = N`), Yule's I is undefined (division by zero), indicating maximum diversity.

### Interpretation

| Metric | Low Value | High Value |
|--------|-----------|------------|
| Yule's K | Low repetitiveness, diverse vocabulary | High repetitiveness, limited vocabulary |
| Yule's I | Low diversity, repetitive vocabulary | High diversity, varied vocabulary |

Typical Yule's K ranges for English prose:
- **Literary fiction**: 80-120
- **Academic writing**: 100-150
- **Journalistic prose**: 120-160
- **Technical manuals**: 140-200
- **Conversational speech**: 150-250

---

## Implementation

### Core Algorithm

The implementation computes Yule's K and I with native chunked analysis for stylometric fingerprinting.

```python
def compute_yule(text: str, chunk_size: int = 1000) -> YuleResult
```

**Algorithm steps:**

1. Chunk the input text into segments of `chunk_size` words
2. For each chunk:
   a. Tokenize and lowercase the text
   b. Count frequency of each token using `Counter`
   c. Build frequency-of-frequencies distribution (`V_m`)
   d. Compute `S = sum(m^2 * V_m)`
   e. Compute `K = 10000 * (S - N) / N^2`
   f. Compute `I = V^2 / (S - N)`, handling division by zero
3. Build Distribution objects from per-chunk K and I values

### Key Features

1. **Dual metrics**: Computes both K (repetitiveness) and I (diversity) in a single call
2. **Frequency spectrum analysis**: Uses the full word frequency distribution, not just type counts
3. **Chunked analysis**: Native chunking captures variance across the text
4. **Division-by-zero handling**: When all words are unique (`S = N`), Yule's I returns `NaN` rather than raising an error
5. **Backward-compatible metadata**: Provides both legacy (`token_count`) and prefixed (`total_token_count`) metadata keys

### Return Type

`YuleResult` dataclass with fields:

| Field | Type | Description |
|-------|------|-------------|
| `yule_k` | `float` | Mean Yule's K across chunks |
| `yule_i` | `float` | Mean Yule's I across chunks |
| `yule_k_dist` | `Distribution` | Distribution of K values across chunks |
| `yule_i_dist` | `Distribution` | Distribution of I values across chunks |
| `chunk_size` | `int` | Words per chunk |
| `chunk_count` | `int` | Number of chunks processed |
| `metadata` | `dict` | Token count, vocabulary size |

---

## Usage

### API Examples

**Basic usage:**

```python
from pystylometry.lexical import compute_yule

result = compute_yule("The quick brown fox jumps over the lazy dog and the fox runs.")
print(f"Yule's K: {result.yule_k:.1f}")  # Repetitiveness
print(f"Yule's I: {result.yule_i:.1f}")  # Diversity
```

**Chunked analysis for fingerprinting:**

```python
result = compute_yule(long_text, chunk_size=1000)

# Cross-chunk statistics reveal authorial patterns
print(f"K mean: {result.yule_k_dist.mean:.1f}")
print(f"K std: {result.yule_k_dist.std:.1f}")
print(f"K range: {result.yule_k_dist.range:.1f}")
print(f"I mean: {result.yule_i_dist.mean:.1f}")
print(f"Chunks: {result.chunk_count}")
```

**Author comparison:**

```python
from pystylometry.lexical import compute_yule

result_a = compute_yule(text_author_a, chunk_size=1000)
result_b = compute_yule(text_author_b, chunk_size=1000)

# Lower K = more diverse vocabulary
print(f"Author A - K: {result_a.yule_k:.1f}, I: {result_a.yule_i:.1f}")
print(f"Author B - K: {result_b.yule_k:.1f}, I: {result_b.yule_i:.1f}")

# Stability comparison
print(f"Author A K variance: {result_a.yule_k_dist.std:.1f}")
print(f"Author B K variance: {result_b.yule_k_dist.std:.1f}")
```

**Accessing metadata:**

```python
result = compute_yule(text)
print(f"Total tokens: {result.metadata['total_token_count']}")
print(f"Total vocabulary: {result.metadata['total_vocabulary_size']}")
```

---

## Limitations

1. **Text length effects**: While more stable than TTR, Yule's K is not entirely immune to text length effects. Short texts (under 200 tokens) produce unreliable K values because the frequency spectrum is sparse.

2. **Frequency spectrum sparsity**: In short texts, most words appear only once or twice, which makes the frequency spectrum degenerate and K/I less meaningful.

3. **Sensitivity to common words**: Very frequent function words (the, of, and) contribute disproportionately to the `S` statistic due to the `m^2` weighting. This can mask differences in content word diversity.

4. **No semantic awareness**: Two texts using completely different vocabulary but with similar frequency distributions will produce similar K values.

5. **Genre dependence**: Different genres have inherently different K ranges (e.g., technical writing vs. poetry), making cross-genre comparisons unreliable without normalization.

6. **Yule's I undefined case**: When all words in a chunk appear exactly once (maximum diversity), Yule's I is undefined. This is handled by returning `NaN` but complicates statistical aggregation.

---

## References

- Yule, G. U. (1944). *The Statistical Study of Literary Vocabulary*. Cambridge University Press.
- Tweedie, F. J., & Baayen, R. H. (1998). How variable may a constant be? Measures of lexical richness in perspective. *Computers and the Humanities*, 32(5), 323-352.
- Miranda-Garcia, A., & Calle-Martin, J. (2005). Yule's characteristic K revisited. *Language Resources and Evaluation*, 39(4), 287-294.
- Oakes, M. P. (1998). *Statistics for Corpus Linguistics*. Edinburgh University Press.
