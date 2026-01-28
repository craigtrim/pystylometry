# Repetitive Word and N-gram Detection

## Verbal Tics and AI Slop Analysis

Generative language models exhibit "verbal tics" -- abnormally repetitive use of certain words and phrases throughout generated text. Words like "shimmered", "obsidian", and "tapestry", or phrases like "a testament to" and "an uncomfortable truth", appear far more frequently than expected in natural writing. This module detects such patterns by comparing observed frequencies against corpus baselines and internal text statistics.

Related GitHub Issue:
- [#28 - Verbal tics detection for slop analysis](https://github.com/craigtrim/pystylometry/issues/28)

---

## Theoretical Background

### The Slop Problem

AI-generated text often exhibits a distinctive repetition pattern where certain content words appear with suspicious regularity. Unlike human writers -- who repeat words when contextually relevant (describing a specific scene, returning to a theme) -- models distribute their favored words evenly across the text. This creates a measurable signal.

The detection approach uses two complementary methods:

1. **Corpus-based unigram detection**: Compares observed word frequencies against the British National Corpus (BNC, ~100 million tokens). Words appearing far more than their BNC relative frequency predicts are flagged.

2. **Internal n-gram detection**: Content n-grams (bigrams, trigrams, etc.) should rarely repeat verbatim in natural writing. No external corpus is needed -- any content phrase repeating beyond a length-scaled threshold is suspicious.

### BNC Baseline Strategy

For unigrams, the expected count of a word in a text of length `L` is computed from the BNC:

```
relative_frequency(word) = raw_count_in_BNC / 100,106,029
expected_count(word, L) = relative_frequency(word) * L
repetition_score = observed_count / expected_count
```

Where `100,106,029` is the total token count of the BNC corpus (4,124 documents). Words not found in the BNC receive an expected count of 0, meaning any repeated occurrence yields an infinite score.

The `bnc-lookup` package (>= 1.3.0) provides the `expected_count()` and `relative_frequency()` functions, built from the raw BNC frequency data (`all.num`) with per-word POS-aggregated counts.

### Distribution Analysis

Both functions support chunked analysis to reveal *how* repetition is distributed across the text:

- **Low entropy** (even distribution): The word appears uniformly across chunks. This is suspicious for rare content words -- it suggests a model's consistent tic rather than contextual usage.
- **High entropy** (clustered distribution): The word is concentrated in specific sections. This is more natural -- a human describing an obsidian tower in one scene.

Shannon entropy of the chunk distribution:

```
H = -sum(p_i * log2(p_i)) for each chunk i where p_i > 0
p_i = count_in_chunk_i / total_count
```

### Aggregate Scoring

For unigrams, the slop score provides a single aggregate metric:

```
slop_score = flagged_words_per_10k * mean_repetition_score
```

Where:
- `flagged_words_per_10k` = number of flagged words normalized per 10,000 content words
- `mean_repetition_score` = average repetition score across flagged words (excluding infinite scores)

Higher slop scores indicate more likely AI-generated verbal tics.

---

## Implementation

### Functions

Two functions are provided:

```python
def compute_repetitive_unigrams(
    text: str,
    threshold: float = 3.0,
    chunk_size: int = 1000,
    min_count: int = 3,
) -> RepetitiveUnigramsResult

def compute_repetitive_ngrams(
    text: str,
    n: int | tuple[int, ...] = (2, 3),
    chunk_size: int = 1000,
    min_count: int = 3,
) -> RepetitiveNgramsResult
```

### Unigram Detection Algorithm

1. Chunk the input text into segments of `chunk_size` words
2. Tokenize each chunk: lowercase, alphabetic only, function words removed
3. Build global and per-chunk word frequency counts
4. For each content word appearing >= `min_count` times:
   a. Query BNC for `expected_count(word, total_content_words)`
   b. Compute `repetition_score = observed / expected`
   c. If score >= `threshold`, flag the word
   d. Compute per-chunk distribution entropy and variance
5. Sort flagged words by repetition score (descending)
6. Compute aggregate metrics: `flagged_words_per_10k`, `mean_repetition_score`, `slop_score`

### N-gram Detection Algorithm

1. Validate `n` parameter (must be in range 2-5)
2. Chunk the input text into segments of `chunk_size` words
3. Tokenize each chunk: lowercase, alphabetic only (function words kept for phrase context)
4. Generate n-grams for each requested order
5. Filter out n-grams composed entirely of function words (e.g., "of the", "in a")
6. Compute length-scaled threshold: `max(min_count, total_ngrams // 10_000)`
7. Flag content n-grams exceeding the threshold
8. Compute per-chunk distribution entropy and variance
9. Sort flagged n-grams by count (descending)

### Function Word Filtering

Content word identification reuses the existing function word sets from `pystylometry.lexical.function_words`:

- Determiners (the, a, an, this, ...)
- Prepositions (in, on, at, by, ...)
- Conjunctions (and, but, or, ...)
- Pronouns (he, she, it, they, ...)
- Auxiliaries (is, are, was, have, ...)
- Particles (up, out, off, ...)

For unigrams, function words are excluded entirely. For n-grams, only n-grams where *all* words are function words are excluded -- mixed n-grams like "the obsidian" are kept because the content word makes the phrase meaningful.

### N-gram Validation

The `n` parameter accepts:
- A single integer: `n=2` for bigrams
- A tuple of integers: `n=(2, 3)` for bigrams and trigrams simultaneously
- Valid range: 2 to 5

Values below 2 are rejected with a message directing users to `compute_repetitive_unigrams()`. Values above 5 are rejected because n-grams of order 6+ are too sparse to produce meaningful repetition signals.

### Return Types

**RepetitiveWord** dataclass:

| Field | Type | Description |
|-------|------|-------------|
| `word` | `str` | The flagged word (lowercased) |
| `count` | `int` | Observed count in the text |
| `expected_count` | `float` | Expected count from BNC baseline |
| `repetition_score` | `float` | `count / expected_count` (inf if expected is 0) |
| `bnc_bucket` | `int \| None` | BNC frequency bucket (1-100, 1=most frequent) |
| `chunk_counts` | `list[int]` | Per-chunk occurrence counts |
| `distribution_entropy` | `float` | Shannon entropy of chunk distribution |
| `distribution_variance` | `float` | Variance of per-chunk counts |

**RepetitiveUnigramsResult** dataclass:

| Field | Type | Description |
|-------|------|-------------|
| `repetitive_words` | `list[RepetitiveWord]` | Flagged words sorted by score descending |
| `total_content_words` | `int` | Total content words in the text |
| `flagged_count` | `int` | Number of flagged words |
| `flagged_words_per_10k` | `float` | Flagged words per 10,000 content words |
| `mean_repetition_score` | `float` | Mean score across flagged words |
| `slop_score` | `float` | Aggregate: `flagged_words_per_10k * mean_repetition_score` |
| `total_content_words_dist` | `Distribution` | Distribution of content words per chunk |
| `chunk_size` | `int` | Words per chunk |
| `chunk_count` | `int` | Number of chunks processed |
| `metadata` | `dict` | Threshold, min_count, unique word count |

**RepetitiveNgram** dataclass:

| Field | Type | Description |
|-------|------|-------------|
| `ngram` | `tuple[str, ...]` | The flagged n-gram |
| `count` | `int` | Observed count in the text |
| `frequency_per_10k` | `float` | Occurrences per 10,000 n-grams |
| `chunk_counts` | `list[int]` | Per-chunk occurrence counts |
| `distribution_entropy` | `float` | Shannon entropy of chunk distribution |
| `distribution_variance` | `float` | Variance of per-chunk counts |

**RepetitiveNgramsResult** dataclass:

| Field | Type | Description |
|-------|------|-------------|
| `repetitive_ngrams` | `list[RepetitiveNgram]` | Flagged n-grams sorted by count descending |
| `n` | `int \| tuple[int, ...]` | N-gram order(s) analyzed |
| `total_ngrams` | `int` | Total content n-grams in the text |
| `flagged_count` | `int` | Number of flagged n-grams |
| `flagged_per_10k` | `float` | Flagged n-grams per 10,000 n-grams |
| `total_ngrams_dist` | `Distribution` | Distribution of n-grams per chunk |
| `chunk_size` | `int` | Words per chunk |
| `chunk_count` | `int` | Number of chunks processed |
| `metadata` | `dict` | Min count, effective threshold, n values |

---

## Usage

### API Examples

**Detecting repetitive words (BNC-based):**

```python
from pystylometry.lexical import compute_repetitive_unigrams

result = compute_repetitive_unigrams(text)

print(f"Slop score: {result.slop_score:.1f}")
print(f"Flagged words: {result.flagged_count}")
print(f"Flagged per 10k: {result.flagged_words_per_10k:.1f}")

for w in result.repetitive_words[:5]:
    print(f"  {w.word}: {w.count}x (expected {w.expected_count:.1f}, "
          f"score {w.repetition_score:.1f})")
```

**Detecting repetitive phrases:**

```python
from pystylometry.lexical import compute_repetitive_ngrams

# Bigrams and trigrams (default)
result = compute_repetitive_ngrams(text)

for ng in result.repetitive_ngrams[:5]:
    phrase = " ".join(ng.ngram)
    print(f"  {phrase}: {ng.count}x ({ng.frequency_per_10k:.1f} per 10k)")

# Analyze bigrams through 4-grams
result = compute_repetitive_ngrams(text, n=(2, 3, 4))
print(f"Flagged: {result.flagged_count} n-grams")
```

**Distribution analysis:**

```python
result = compute_repetitive_unigrams(text, chunk_size=500)

for w in result.repetitive_words:
    if w.distribution_entropy < 1.0:
        print(f"  {w.word}: suspiciously even distribution "
              f"(entropy={w.distribution_entropy:.2f})")
```

**Comparing AI vs. human text:**

```python
ai_result = compute_repetitive_unigrams(ai_text)
human_result = compute_repetitive_unigrams(human_text)

print(f"AI slop score: {ai_result.slop_score:.1f}")
print(f"Human slop score: {human_result.slop_score:.1f}")
```

**Custom thresholds:**

```python
# More sensitive detection
result = compute_repetitive_unigrams(text, threshold=2.0, min_count=2)

# Less sensitive detection
result = compute_repetitive_unigrams(text, threshold=5.0, min_count=5)
```

---

## Limitations

1. **BNC corpus vintage**: The BNC was compiled in the early 1990s and reflects British English of that era. Words that have become common since (e.g., internet-related terminology) may have artificially low expected counts, leading to false positives.

2. **Language dependence**: The BNC baseline is English-only. The n-gram detector works across languages but the function word filtering is English-specific.

3. **Short text sensitivity**: Very short texts (< 100 words) may not produce enough repetition to trigger detection, or may produce noisy results due to small sample sizes.

4. **No semantic awareness**: The detector flags surface-level repetition only. Paraphrased repetition (using synonyms) is not detected.

5. **Genre effects**: Technical writing, legal documents, and other specialized genres may legitimately repeat domain terminology. The threshold and min_count parameters can be adjusted for these cases.

6. **Function word boundaries**: The function word sets are comprehensive but not exhaustive. Some borderline words (e.g., "much", "very") may or may not be filtered depending on their classification.

---

## Dependencies

- **bnc-lookup >= 1.3.0** (optional, in lexical dependency group): Provides `expected_count()` and `bucket()` for BNC baseline comparison in unigram detection.

Install with:
```bash
pip install pystylometry[lexical]
# or
poetry install --with lexical
```

---

## References

- British National Corpus Consortium. (2007). *The British National Corpus, version 3 (BNC XML Edition)*. http://www.natcorp.ox.ac.uk/
- Kilgarriff, A. (2001). BNC database and word frequency lists. https://www.kilgarriff.co.uk/bnc-readme.html
- Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical Journal*, 27(3), 379-423.
