# Measure of Textual Lexical Diversity (MTLD)

## Robust Lexical Diversity Through Sequential Factor Analysis

MTLD provides a length-robust measure of lexical diversity by computing the mean length of sequential word strings that maintain a minimum Type-Token Ratio threshold. Unlike simple TTR, MTLD is resistant to text length effects, making it one of the most widely recommended metrics for comparing lexical diversity across texts of different sizes.

---

## Theoretical Background

### Origins

MTLD was developed by Philip McCarthy and Scott Jarvis as part of a comprehensive 2010 validation study comparing sophisticated lexical diversity measures. Their research demonstrated that MTLD, along with voc-D and HD-D, outperformed traditional measures like TTR and its simple variants in terms of stability across text lengths and sensitivity to genuine lexical diversity differences.

The core insight behind MTLD is that lexical diversity can be captured by measuring how many tokens an author can produce before their vocabulary begins to repeat significantly. Authors with larger active vocabularies will produce longer sequences before the Type-Token Ratio drops below a critical threshold.

### Mathematical Foundation

MTLD operates by dividing text into "factors" -- sequential segments where the running TTR drops below a specified threshold (default: 0.72).

**Factor computation:**

For a sequence of tokens `t_1, t_2, ..., t_n`, a running TTR is maintained:

```
TTR(k) = |{t_1, ..., t_k}| / k
```

When `TTR(k) < threshold`, a factor is complete, the counter resets, and a new factor begins. The final partial factor is weighted proportionally:

```
Partial factor = (1 - TTR_final) / (1 - threshold)
```

**MTLD formula:**

```
MTLD = N / F
```

Where:
- `N` = total number of tokens
- `F` = total number of factors (complete + partial)

**Bidirectional MTLD:**

To reduce sensitivity to starting position, MTLD is computed in both directions:

```
MTLD_average = (MTLD_forward + MTLD_backward) / 2
```

Where `MTLD_forward` processes tokens left-to-right and `MTLD_backward` processes tokens right-to-left.

### Interpretation

| MTLD Value | Interpretation |
|------------|----------------|
| < 50 | Low lexical diversity (highly repetitive) |
| 50-80 | Moderate diversity (typical conversational text) |
| 80-120 | Good diversity (standard written prose) |
| 120-170 | High diversity (rich vocabulary) |
| > 170 | Very high diversity (exceptional vocabulary range) |

Key properties:
- **Higher values = more diverse**: An MTLD of 100 means, on average, an author produces 100 tokens before their vocabulary becomes significantly repetitive.
- **Length robust**: Unlike TTR, MTLD remains stable across texts of different lengths.
- **Bidirectional**: The average of forward and backward passes reduces position-dependent bias.

---

## Implementation

### Core Algorithm

The implementation computes MTLD using native chunked analysis with the pystylometry Distribution dataclass.

```python
def compute_mtld(
    text: str,
    threshold: float = 0.72,
    chunk_size: int = 1000,
) -> MTLDResult
```

**Algorithm steps:**

1. Chunk the input text into segments of `chunk_size` words
2. For each chunk, compute forward and backward MTLD:
   a. Initialize running token count and type set
   b. Iterate through tokens, computing running TTR
   c. When TTR drops below threshold, increment factor count and reset
   d. For remaining partial segment, compute weighted partial factor
   e. Return `total_tokens / factor_count`
3. Average forward and backward MTLD for each chunk
4. Build Distribution objects from per-chunk values

### Key Features

1. **Bidirectional computation**: Forward and backward passes reduce position-dependent artifacts
2. **Chunked analysis**: Native chunking captures variance across the text for stylometric fingerprinting
3. **Configurable threshold**: Default 0.72 follows McCarthy & Jarvis (2010); adjustable for specific applications
4. **Partial factor handling**: Incomplete final segments are proportionally weighted rather than discarded
5. **Validation**: Threshold must be in range (0, 1); raises `ValueError` otherwise

### Return Type

`MTLDResult` dataclass with fields:

| Field | Type | Description |
|-------|------|-------------|
| `mtld_forward` | `float` | Mean forward MTLD across chunks |
| `mtld_backward` | `float` | Mean backward MTLD across chunks |
| `mtld_average` | `float` | Mean of forward and backward MTLD |
| `mtld_forward_dist` | `Distribution` | Distribution of forward MTLD values |
| `mtld_backward_dist` | `Distribution` | Distribution of backward MTLD values |
| `mtld_average_dist` | `Distribution` | Distribution of average MTLD values |
| `chunk_size` | `int` | Words per chunk |
| `chunk_count` | `int` | Number of chunks processed |
| `metadata` | `dict` | Total token count, threshold value |

---

## Usage

### API Examples

**Basic usage:**

```python
from pystylometry.lexical import compute_mtld

result = compute_mtld("The quick brown fox jumps over the lazy dog and the fox runs.")
print(f"MTLD forward: {result.mtld_forward:.1f}")
print(f"MTLD backward: {result.mtld_backward:.1f}")
print(f"MTLD average: {result.mtld_average:.1f}")
```

**Custom threshold:**

```python
# Lower threshold = more permissive (longer factors)
result_permissive = compute_mtld(text, threshold=0.50)

# Higher threshold = more strict (shorter factors)
result_strict = compute_mtld(text, threshold=0.80)

print(f"Permissive MTLD: {result_permissive.mtld_average:.1f}")
print(f"Strict MTLD: {result_strict.mtld_average:.1f}")
```

**Chunked analysis for fingerprinting:**

```python
result = compute_mtld(long_text, chunk_size=500)

# Cross-chunk variance reveals authorial consistency
print(f"MTLD mean: {result.mtld_average_dist.mean:.1f}")
print(f"MTLD std: {result.mtld_average_dist.std:.1f}")
print(f"MTLD range: {result.mtld_average_dist.range:.1f}")
print(f"Chunks analyzed: {result.chunk_count}")
```

**Comparing authors:**

```python
from pystylometry.lexical import compute_mtld

text_a = open("hemingway.txt").read()
text_b = open("faulkner.txt").read()

result_a = compute_mtld(text_a, chunk_size=1000)
result_b = compute_mtld(text_b, chunk_size=1000)

print(f"Hemingway MTLD: {result_a.mtld_average:.1f}")
print(f"Faulkner MTLD: {result_b.mtld_average:.1f}")

# Faulkner's richer vocabulary should produce higher MTLD
# Hemingway's deliberate simplicity should produce lower MTLD
```

---

## Limitations

1. **Threshold sensitivity**: The choice of threshold (default 0.72) affects absolute MTLD values. While relative comparisons remain valid, different thresholds may be more appropriate for different languages or genres.

2. **Short text instability**: Texts shorter than approximately 100 tokens may not produce enough factors for reliable MTLD estimation. Very short texts where TTR never drops below threshold return the text length as MTLD.

3. **Partial factor estimation**: The weighting of incomplete final factors is an approximation. For texts that naturally end mid-factor, the partial factor calculation introduces some estimation error.

4. **Forward-backward asymmetry**: The forward and backward MTLD values can differ substantially for texts with non-uniform vocabulary distribution (e.g., technical introduction followed by narrative).

5. **No semantic consideration**: Like TTR, MTLD treats all word types equally and does not account for semantic similarity or register variation within the text.

6. **Tokenization dependence**: Results depend on tokenization choices. Case normalization (lowercase) is applied internally, but decisions about handling contractions, hyphenated words, and numbers affect factor boundaries.

---

## References

- McCarthy, P. M., & Jarvis, S. (2010). MTLD, vocd-D, and HD-D: A validation study of sophisticated approaches to lexical diversity assessment. *Behavior Research Methods*, 42(2), 381-392.
- McCarthy, P. M. (2005). *An assessment of the range and usefulness of lexical diversity measures and the potential of the measure of textual, lexical diversity (MTLD)*. Doctoral dissertation, University of Memphis.
- Koizumi, R., & In'nami, Y. (2012). Effects of text length on lexical diversity measures: Using short texts with less than 200 tokens. *System*, 40(4), 554-564.
- Zenker, F., & Kyle, K. (2021). Investigating minimum text lengths for lexical diversity indices. *Assessing Writing*, 47, 100505.
