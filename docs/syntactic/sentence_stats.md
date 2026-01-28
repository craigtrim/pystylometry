# Sentence-Level Statistics

## Measuring Syntactic Rhythm Through Sentence Length Distributions

Sentence-level statistics capture the quantitative properties of sentence length in a text. By computing the mean, standard deviation, range, minimum, and maximum of word counts per sentence, these metrics reveal the syntactic rhythm and structural variability that characterize different authors, genres, and registers.

---

## Theoretical Background

### Origins

Sentence length has been one of the most studied features in stylometry since the earliest quantitative investigations of literary style. Augustus de Morgan first suggested in 1851 that average sentence length might distinguish authors. Thomas Mendenhall (1887) extended this idea with his "characteristic curves" plotting word-length distributions.

Kellogg Hunt's (1965) seminal work on *Grammatical Structures Written at Three Grade Levels* established sentence length as a developmental marker for writing maturity. Hunt demonstrated that mean sentence length increases systematically with grade level and writing proficiency, reflecting the growing ability to embed and subordinate clauses.

Modern computational stylometry continues to treat sentence length statistics as a core feature set because:

- **Unconscious production**: Writers rarely monitor their sentence lengths consciously, making these statistics resistant to deliberate manipulation.
- **Genre sensitivity**: Academic writing favors longer, more complex sentences; journalism and conversational text favor shorter ones.
- **Variability as signal**: The standard deviation of sentence length captures an author's rhythmic range. Some writers maintain uniform sentence lengths; others alternate dramatically between short and long constructions.

### Mathematical Foundation

Given a text segmented into *n* sentences, where sentence *i* has word count *w_i*:

**Mean sentence length:**

```
mean = (1/n) * sum(w_i for i in 1..n)
```

**Standard deviation** (sample, Bessel-corrected):

```
std = sqrt( (1/(n-1)) * sum((w_i - mean)^2 for i in 1..n) )
```

For a single sentence (n = 1), the standard deviation is defined as 0.0.

**Range:**

```
range = max(w_i) - min(w_i)
```

**Minimum and maximum** are the smallest and largest sentence word counts, respectively.

### Interpretation

| Metric | Low Values | High Values |
|--------|-----------|-------------|
| Mean sentence length | Simple, direct prose; journalism; children's writing | Complex, academic prose; legal text; Victorian fiction |
| Standard deviation | Uniform sentence rhythm; monotonous pacing | Varied rhythm; literary variety; mixed sentence types |
| Range | Consistent sentence lengths | Dramatic variation between shortest and longest sentences |
| Sentence count | Short text sample | Long text with many sentences |

Typical ranges observed in English:

- **Academic prose**: Mean 20-30 words, std 10-15
- **Fiction**: Mean 12-20 words, std 8-14
- **Journalism**: Mean 15-22 words, std 6-12
- **Children's writing (grade 4)**: Mean 8-12 words, std 3-6
- **Professional writing (adult)**: Mean 17-24 words, std 8-14

Hunt (1965) reported these developmental norms for sentence length:
- Grade 4: Mean ~8.6 words per sentence
- Grade 8: Mean ~11.5 words per sentence
- Grade 12: Mean ~14.4 words per sentence
- Skilled adult: Mean ~20.3 words per sentence

---

## Implementation

### Core Algorithm

The implementation uses spaCy's sentence segmentation pipeline to identify sentence boundaries, then counts alphabetic tokens per sentence:

1. Loads the specified spaCy model and processes the input text.
2. Iterates over `doc.sents` to extract sentence spans.
3. For each sentence, counts only alphabetic tokens (`token.is_alpha`), excluding punctuation, digits, and symbols.
4. Filters out empty sentences (those with zero alphabetic tokens after filtering).
5. Computes mean, standard deviation (Bessel-corrected for n > 1), range, minimum, and maximum from the resulting sentence length list.
6. Returns a `SentenceStatsResult` dataclass with scalar values, distribution objects, and metadata including the raw list of sentence lengths.

### Key Features

- **Alphabetic-only word counting**: Punctuation and numeric tokens are excluded from word counts, ensuring sentence length reflects genuine lexical content rather than punctuation style.
- **Empty sentence filtering**: Sentences that contain no alphabetic tokens (e.g., standalone punctuation sequences) are excluded from all calculations.
- **Bessel correction**: Standard deviation uses the sample formula (dividing by n-1) rather than the population formula, providing an unbiased estimate appropriate for stylometric sampling.
- **Single-sentence handling**: When the text contains exactly one sentence, standard deviation is returned as 0.0 rather than raising an error.
- **Empty text handling**: Empty text or text with no valid sentences returns `NaN` for mean and standard deviation, and 0.0 for range, minimum, and maximum.
- **Raw sentence lengths in metadata**: The `metadata` dictionary includes the full `sentence_lengths` list, enabling custom downstream analysis (histograms, percentile calculations, etc.).

---

## Usage

### API Examples

```python
from pystylometry.syntactic import compute_sentence_stats

# Basic usage
result = compute_sentence_stats(
    "The quick brown fox jumped. It landed gracefully on the other side of the fence."
)
print(f"Mean sentence length: {result.mean_sentence_length:.1f} words")
print(f"Standard deviation: {result.sentence_length_std:.1f}")
print(f"Range: {result.sentence_length_range:.0f}")
print(f"Min length: {result.min_sentence_length:.0f}")
print(f"Max length: {result.max_sentence_length:.0f}")
print(f"Sentence count: {result.sentence_count}")
```

```python
# Accessing raw sentence lengths for custom analysis
result = compute_sentence_stats(long_text)
lengths = result.metadata["sentence_lengths"]

# Compute percentiles
import statistics
median = statistics.median(lengths)
print(f"Median sentence length: {median}")

# Find distribution shape
short = sum(1 for l in lengths if l < 10)
medium = sum(1 for l in lengths if 10 <= l <= 25)
long_sent = sum(1 for l in lengths if l > 25)
print(f"Short (<10): {short}, Medium (10-25): {medium}, Long (>25): {long_sent}")
```

```python
# Comparing authors
hemingway = compute_sentence_stats(hemingway_text)
faulkner = compute_sentence_stats(faulkner_text)

print(f"Hemingway mean: {hemingway.mean_sentence_length:.1f}")
print(f"Faulkner mean: {faulkner.mean_sentence_length:.1f}")
print(f"Hemingway std: {hemingway.sentence_length_std:.1f}")
print(f"Faulkner std: {faulkner.sentence_length_std:.1f}")
# Hemingway typically shows shorter, more uniform sentences
# Faulkner typically shows longer, more variable sentences
```

```python
# Using a larger spaCy model for better sentence segmentation
result = compute_sentence_stats(text, model="en_core_web_lg")
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | `str` | (required) | Input text to analyze |
| `model` | `str` | `"en_core_web_sm"` | spaCy model name. Larger models may produce more accurate sentence segmentation. |
| `chunk_size` | `int` | `1000` | Number of words per chunk. Included for API consistency; sentence analysis runs in a single pass. |

### Return Type

`SentenceStatsResult` dataclass with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `mean_sentence_length` | `float` | Average words per sentence |
| `sentence_length_std` | `float` | Standard deviation of sentence lengths |
| `sentence_length_range` | `float` | Max length minus min length |
| `min_sentence_length` | `float` | Shortest sentence word count |
| `max_sentence_length` | `float` | Longest sentence word count |
| `sentence_count` | `int` | Total number of valid sentences |
| `metadata` | `dict` | Model name, raw `sentence_lengths` list |

---

## Limitations

- **Sentence segmentation accuracy**: All metrics depend on the quality of spaCy's sentence segmentation. Texts with non-standard punctuation, dialogue formatting, or missing terminal punctuation may be segmented incorrectly. Larger spaCy models generally produce more accurate segmentation.
- **Alphabetic token assumption**: Word count excludes numeric tokens and punctuation. In technical or mathematical texts, this may underrepresent sentence complexity.
- **Single-pass processing**: The `chunk_size` parameter is accepted for API consistency but does not trigger chunked analysis. The entire text is processed in a single spaCy pass.
- **No sentence type distinction**: All valid sentences are counted equally regardless of type (declarative, interrogative, etc.). For type-aware statistics, combine with `compute_sentence_types`.
- **Abbreviations and titles**: Periods in abbreviations (e.g., "U.S.", "Dr.") may cause false sentence boundaries depending on the spaCy model's handling of these cases.
- **Sample size sensitivity**: Standard deviation and range are unstable with very few sentences. Texts with fewer than 10 sentences should be interpreted cautiously.

---

## References

- Hunt, K. W. (1965). *Grammatical structures written at three grade levels*. NCTE Research Report No. 3. National Council of Teachers of English.
- Mendenhall, T. C. (1887). The characteristic curves of composition. *Science*, 9(214), 237-249.
- Biber, D. (1988). *Variation across speech and writing*. Cambridge University Press.
- Stamatatos, E. (2009). A survey of modern authorship attribution methods. *Journal of the American Society for Information Science and Technology*, 60(3), 538-556.
- Grieve, J. (2007). Quantitative authorship attribution: An evaluation of techniques. *Literary and Linguistic Computing*, 22(3), 251-270.
