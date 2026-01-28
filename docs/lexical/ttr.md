# Type-Token Ratio (TTR)

## Measuring Vocabulary Richness Through Type-to-Token Proportions

Type-Token Ratio is the foundational metric for lexical diversity in stylometry. It quantifies vocabulary richness by computing the ratio of unique word types to total tokens, providing a straightforward measure of how varied an author's word usage is across a text.

---

## Theoretical Background

### Origins

The Type-Token Ratio was introduced by Wendell Johnson in his landmark 1944 study of language behavior as one of the earliest quantitative measures of vocabulary diversity. Johnson observed that speakers and writers differ systematically in how many unique words they employ relative to their total output, and that this ratio could serve as a diagnostic indicator of language development and style.

TTR quickly became the standard baseline metric in computational stylometry. While its sensitivity to text length is well-documented -- longer texts inherently produce lower TTR values as common words repeat -- it remains widely used as a first-pass measure and as a building block for more sophisticated metrics like STTR and Root TTR.

### Mathematical Foundation

**Raw TTR** measures the proportion of unique types in a text:

```
TTR = V / N
```

Where:
- `V` = vocabulary size (number of unique word types)
- `N` = total number of tokens

**Root TTR (Guiraud's Index)** compensates partially for text length by using the square root:

```
Root TTR = V / sqrt(N)
```

This transformation was proposed by Guiraud (1960) to reduce the systematic decline of TTR with increasing text length.

**Log TTR (Herdan's C)** applies logarithmic scaling for further length normalization:

```
Log TTR = log(V) / log(N)
```

Herdan (1960) demonstrated that this formulation provides more stable values across texts of varying length than raw TTR.

**Standardized TTR (STTR)** computes TTR over fixed-size chunks and averages the results, providing the most robust length normalization:

```
STTR = mean(TTR_chunk_1, TTR_chunk_2, ..., TTR_chunk_k)
```

Where each chunk contains a fixed number of tokens (default: 1000).

**Delta Standard Deviation** captures the variability of TTR across chunks:

```
Delta Std = std(TTR_chunk_1, TTR_chunk_2, ..., TTR_chunk_k)
```

This variance measure is particularly valuable for stylometric fingerprinting, as different authors exhibit characteristic levels of vocabulary consistency.

### Interpretation

| Metric | Low Value | High Value |
|--------|-----------|------------|
| Raw TTR | Repetitive vocabulary (common in long texts) | Diverse vocabulary (common in short texts) |
| Root TTR | Limited vocabulary relative to length | Rich vocabulary relative to length |
| Log TTR | Low diversity (approaches 0) | High diversity (approaches 1) |
| STTR | Consistently repetitive across chunks | Consistently diverse across chunks |
| Delta Std | Uniform vocabulary usage | Variable vocabulary usage |

Typical TTR ranges:
- **Conversational speech**: 0.35-0.50
- **Journalistic prose**: 0.45-0.60
- **Academic writing**: 0.50-0.65
- **Literary fiction**: 0.55-0.70
- **Poetry**: 0.60-0.80

---

## Implementation

### Core Algorithm

The pystylometry implementation wraps the `stylometry-ttr` package, providing a facade that integrates with pystylometry's Distribution dataclass and chunked analysis framework.

```python
def compute_ttr(text: str, text_id: str | None = None, chunk_size: int = 1000) -> TTRResult
```

The function delegates computation to the `stylometry-ttr` package, which handles internal chunking for STTR calculation. Results are wrapped in `Distribution` objects for compatibility with pystylometry's stylometric fingerprinting pipeline.

### Key Features

1. **Multiple TTR variants**: Computes raw TTR, Root TTR (Guiraud), Log TTR (Herdan), STTR, and Delta Std in a single call
2. **Distribution dataclass**: Each metric is wrapped in a `Distribution` object containing mean, median, std, range, and IQR for cross-chunk analysis
3. **Graceful degradation**: Short texts that cannot produce STTR or Delta Std values return `NaN` rather than raising errors
4. **Text identification**: Optional `text_id` parameter for tracking results across corpora
5. **Metadata**: Result includes source attribution, availability flags for STTR and Delta Std

### Return Type

`TTRResult` dataclass with fields:

| Field | Type | Description |
|-------|------|-------------|
| `total_words` | `int` | Total token count |
| `unique_words` | `int` | Unique type count (V) |
| `ttr` | `float` | Raw TTR (V/N) |
| `root_ttr` | `float` | Guiraud's Root TTR |
| `log_ttr` | `float` | Herdan's Log TTR |
| `sttr` | `float` | Standardized TTR across chunks |
| `delta_std` | `float` | Standard deviation of TTR across chunks |
| `ttr_dist` | `Distribution` | Distribution of raw TTR values |
| `root_ttr_dist` | `Distribution` | Distribution of Root TTR values |
| `log_ttr_dist` | `Distribution` | Distribution of Log TTR values |
| `sttr_dist` | `Distribution` | Distribution of STTR values |
| `delta_std_dist` | `Distribution` | Distribution of Delta Std values |
| `chunk_size` | `int` | Words per chunk |
| `chunk_count` | `int` | Number of chunks processed |
| `metadata` | `dict` | Text ID, source info, availability flags |

---

## Usage

### API Examples

**Basic usage:**

```python
from pystylometry.lexical import compute_ttr

result = compute_ttr("The quick brown fox jumps over the lazy dog.")
print(f"Raw TTR: {result.ttr:.3f}")          # 0.900
print(f"Root TTR: {result.root_ttr:.3f}")     # 2.846
print(f"Log TTR: {result.log_ttr:.3f}")       # 0.954
print(f"STTR: {result.sttr:.3f}")             # 1.000
print(f"Total words: {result.total_words}")   # 10
print(f"Unique words: {result.unique_words}") # 9
```

**With text identification:**

```python
result = compute_ttr(
    "A longer text sample for analysis...",
    text_id="sample-001",
    chunk_size=1000
)
print(result.metadata["text_id"])  # "sample-001"
```

**Accessing distribution data for fingerprinting:**

```python
result = compute_ttr(long_text, chunk_size=500)

# Distribution statistics for cross-text comparison
print(f"TTR mean: {result.ttr_dist.mean:.3f}")
print(f"TTR std: {result.ttr_dist.std:.3f}")
print(f"TTR IQR: {result.ttr_dist.iqr:.3f}")
```

**Comparing two texts:**

```python
text_a = open("author_a.txt").read()
text_b = open("author_b.txt").read()

result_a = compute_ttr(text_a, text_id="author-a")
result_b = compute_ttr(text_b, text_id="author-b")

# Compare STTR (length-normalized) rather than raw TTR
print(f"Author A STTR: {result_a.sttr:.3f}")
print(f"Author B STTR: {result_b.sttr:.3f}")

# Compare vocabulary consistency
print(f"Author A Delta Std: {result_a.delta_std:.3f}")
print(f"Author B Delta Std: {result_b.delta_std:.3f}")
```

---

## Limitations

1. **Text length sensitivity**: Raw TTR systematically decreases with text length because common words inevitably repeat. STTR and Root TTR partially mitigate this, but comparisons should ideally use texts of similar length.

2. **Language dependence**: TTR values are not directly comparable across languages. Morphologically rich languages (e.g., Finnish, Turkish) naturally produce higher TTR values due to inflectional variation.

3. **Tokenization effects**: Results depend on tokenization decisions (e.g., whether contractions count as one or two tokens, handling of hyphenated words). The implementation uses whitespace-based tokenization with punctuation stripping.

4. **Genre confounds**: Different genres have inherently different TTR ranges (e.g., technical writing vs. narrative fiction), making cross-genre comparisons unreliable without normalization.

5. **No semantic awareness**: TTR treats all word types equally regardless of semantic similarity. "Big" and "large" count as two types despite being near-synonyms.

6. **Short text instability**: For texts under approximately 100 tokens, TTR values become highly variable and less reliable. STTR requires sufficient text to generate multiple chunks.

---

## References

- Johnson, W. (1944). Studies in language behavior: I. A program of research. *Psychological Monographs*, 56(2), 1-15.
- Guiraud, P. (1960). *Problemes et methodes de la statistique linguistique*. Presses Universitaires de France.
- Herdan, G. (1960). *Type-token Mathematics: A Textbook of Mathematical Linguistics*. Mouton.
- Tweedie, F. J., & Baayen, R. H. (1998). How variable may a constant be? Measures of lexical richness in perspective. *Computers and the Humanities*, 32(5), 323-352.
- McCarthy, P. M., & Jarvis, S. (2010). MTLD, vocd-D, and HD-D: A validation study of sophisticated approaches to lexical diversity assessment. *Behavior Research Methods*, 42(2), 381-392.
