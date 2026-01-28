# N-gram Entropy and Perplexity

## Information-Theoretic Measures for Stylometric Fingerprinting

---

## Theoretical Background

### Origins

Claude Shannon introduced information entropy in his landmark 1948 paper "A Mathematical Theory of Communication" (Shannon 379-423). Entropy quantifies the uncertainty or unpredictability in a sequence of symbols. When applied to natural language, entropy measures how surprising the next word or character is, given the preceding context. High entropy indicates diverse, unpredictable text; low entropy indicates repetitive, predictable patterns.

In stylometry, n-gram entropy captures an author's vocabulary diversity and phrasing habits at a granular level. Different authors produce characteristic entropy signatures: technical writing tends toward lower word bigram entropy (repetitive terminology), while literary prose often shows higher entropy (varied vocabulary and syntax). Character-level entropy captures orthographic habits, including spelling patterns and character co-occurrence preferences.

### Mathematical Foundation

**Shannon Entropy** measures the average information content per n-gram:

```
H(X) = -SUM p(x) * log2(p(x))
```

Where:
- `X` is the random variable representing n-gram occurrences
- `p(x)` is the probability of n-gram `x` occurring, estimated as `count(x) / total_ngrams`
- The sum is over all distinct n-grams in the text
- The logarithm base 2 yields entropy in bits

**Perplexity** is the exponentiated entropy:

```
Perplexity = 2^H(X)
```

Perplexity can be interpreted as the effective number of equally likely n-grams. A perplexity of 32 means the text behaves as if choosing uniformly among 32 possible n-grams at each position.

### Interpretation

| Entropy Range | Interpretation |
|---------------|----------------|
| Low (< 3.0 bits) | Highly repetitive text; limited vocabulary or formulaic phrasing |
| Medium (3.0-6.0 bits) | Typical prose; balanced between predictability and variety |
| High (> 6.0 bits) | Highly diverse text; rich vocabulary, varied constructions |

Character bigram entropy typically ranges from 3.0 to 5.0 bits for English text, reflecting the constrained letter co-occurrence patterns of the language. Word bigram entropy is typically higher (4.0-8.0 bits), as word sequences are less constrained than character sequences.

The variance of entropy across chunks (captured by the Distribution dataclass) is itself a stylometric signal. Consistent entropy suggests uniform style; high variance may indicate mixed authorship or topic shifts.

---

## Implementation

### Core Algorithm

The pystylometry implementation computes n-gram entropy with native chunked analysis:

1. **Chunking**: Split the input text into chunks of `chunk_size` words using `chunk_text()`
2. **N-gram generation**: For each chunk, generate n-grams using a sliding window over tokens (word or character)
3. **Frequency counting**: Count occurrences of each distinct n-gram using `Counter`
4. **Entropy calculation**: Compute Shannon entropy from the frequency distribution
5. **Perplexity**: Compute `2^H(X)` for each chunk
6. **Aggregation**: Build `Distribution` objects from per-chunk values, capturing mean, median, standard deviation, range, and IQR

| Parameter | Default | Description |
|-----------|---------|-------------|
| `text` | (required) | Input text to analyze |
| `n` | 2 | N-gram size (2 for bigrams, 3 for trigrams, etc.) |
| `ngram_type` | `"word"` | Type of n-gram: `"word"` or `"character"` |
| `chunk_size` | 1000 | Number of words per chunk for distribution analysis |

### Key Features

- **Native chunked analysis**: Following Issue #27, metrics are computed per chunk and aggregated into `Distribution` objects. The standard deviation across chunks reveals whether entropy is stable (single-author) or volatile (mixed-authorship).
- **Word and character n-grams**: Word n-grams capture phrasal patterns; character n-grams capture orthographic and morphological habits.
- **Convenience functions**: `compute_character_bigram_entropy()` and `compute_word_bigram_entropy()` provide direct access to the most common configurations.
- **Graceful handling of short text**: Returns `NaN` for chunks too short to form n-grams, excluding them from distribution calculations.

### Return Value

The function returns an `EntropyResult` dataclass containing:

- `entropy`: Mean entropy across chunks (in bits)
- `perplexity`: Mean perplexity across chunks
- `ngram_type`: String describing the n-gram configuration (e.g., `"word_2gram"`)
- `entropy_dist`: `Distribution` object with per-chunk entropy statistics
- `perplexity_dist`: `Distribution` object with per-chunk perplexity statistics
- `chunk_size`: Words per chunk used
- `chunk_count`: Number of chunks analyzed
- `metadata`: Dictionary with total item count, unique n-grams, and total n-grams

---

## Usage

### API Examples

```python
from pystylometry.ngrams import (
    compute_ngram_entropy,
    compute_character_bigram_entropy,
    compute_word_bigram_entropy,
)

# General n-gram entropy
result = compute_ngram_entropy(text, n=2, ngram_type="word", chunk_size=1000)
print(f"Word bigram entropy: {result.entropy:.2f} bits")
print(f"Perplexity: {result.perplexity:.1f}")
print(f"Entropy std across chunks: {result.entropy_dist.std:.3f}")

# Character bigram entropy (convenience function)
char_result = compute_character_bigram_entropy(text, chunk_size=1000)
print(f"Character bigram entropy: {char_result.entropy:.2f} bits")

# Word bigram entropy (convenience function)
word_result = compute_word_bigram_entropy(text, chunk_size=1000)
print(f"Word bigram entropy: {word_result.entropy:.2f} bits")

# Compare two authors using entropy distributions
result_a = compute_ngram_entropy(author_a_text, n=2)
result_b = compute_ngram_entropy(author_b_text, n=2)
print(f"Author A: {result_a.entropy:.2f} +/- {result_a.entropy_dist.std:.3f}")
print(f"Author B: {result_b.entropy:.2f} +/- {result_b.entropy_dist.std:.3f}")

# Trigram entropy for richer context
tri_result = compute_ngram_entropy(text, n=3, ngram_type="word")
print(f"Word trigram entropy: {tri_result.entropy:.2f} bits")
```

---

## Limitations

### Text Length Requirements

N-gram entropy requires sufficient text for reliable estimation. With very short texts (under 100 words), n-gram frequency estimates are noisy and entropy values may be unstable. The chunked analysis mitigates this by reporting distribution statistics, but individual chunk values should be interpreted cautiously when chunks are small.

### Vocabulary Sensitivity

Word-level entropy is sensitive to tokenization. The implementation uses pystylometry's standard tokenizer, which may handle edge cases (contractions, hyphenated words, abbreviations) differently than other tools. Character-level entropy avoids this issue but captures different information.

### N-gram Order

Higher-order n-grams (n >= 4) suffer from data sparsity: most n-grams appear only once, pushing entropy toward its theoretical maximum. For reliable higher-order entropy, substantially longer texts are required.

### Language Dependence

Entropy values are language-dependent. English character bigram entropy reflects English orthography; applying the metric to other languages will yield different baselines. Cross-language comparisons require normalization.

---

## References

Shannon, C. E. "A Mathematical Theory of Communication." *Bell System Technical Journal*, vol. 27, no. 3, 1948, pp. 379-423.

Manning, C. D., and H. Schutze. *Foundations of Statistical Natural Language Processing*. MIT Press, 1999.

Jurafsky, D., and J. H. Martin. *Speech and Language Processing*. 3rd ed., Prentice Hall, 2023.

Baayen, R. H. "Word Frequency Distributions." *Text, Speech and Language Technology*, vol. 18. Springer, 2001.
