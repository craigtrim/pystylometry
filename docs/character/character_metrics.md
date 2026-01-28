# Character Metrics

## Character-Level Features for Stylometric Analysis

The `character_metrics` module computes character-level features that capture low-level patterns in writing style. Character-level metrics are fundamental for authorship attribution because they reveal subconscious habits in punctuation usage, word construction, capitalization, and formatting preferences. These features operate below the lexical level, making them language-independent and resistant to deliberate style manipulation.

---

## Theoretical Background

### Origins

Character-level analysis for authorship attribution has roots in early quantitative stylistics, but gained prominence through two key research threads:

- **Grieve (2007)** conducted a comprehensive evaluation of authorship attribution techniques and demonstrated that character-level features, including character n-grams and punctuation frequencies, provide discriminative power comparable to or exceeding word-level features in many settings. His work established character metrics as a standard component of stylometric toolkits.

- **Sapkota et al. (2015)** investigated character n-grams in depth and showed that not all character n-grams contribute equally to authorship attribution. They identified specific categories of character n-grams -- including prefix, suffix, space-prefix, and punctuation n-grams -- that carry distinct stylistic signals. Their findings reinforced the value of decomposing character-level analysis into meaningful subcategories rather than treating all character features uniformly.

- **Stamatatos (2009)** provided a broad survey of modern authorship attribution methods, highlighting that character-level features are particularly effective because they implicitly capture morphological, lexical, and even syntactic information without requiring explicit linguistic processing.

### Mathematical Foundation

The module computes several categories of metrics, each grounded in straightforward statistical measures:

**Character type ratios** express the proportion of each character class relative to total characters or total letters:

```
uppercase_ratio = uppercase_count / total_letters
whitespace_ratio = whitespace_count / total_characters
digit_ratio = digit_count / total_characters
```

**Punctuation density** is normalized per 100 words for interpretability:

```
punctuation_density = (punctuation_count / total_words) * 100
```

**Vowel-to-consonant ratio** captures phonological tendencies at the character level:

```
vowel_consonant_ratio = vowel_count / consonant_count
```

**Letter frequency distribution** computes the relative frequency of each letter a-z (case-insensitive):

```
letter_frequency[c] = count(c) / total_letters
```

All metrics are computed per chunk and then aggregated using the `Distribution` dataclass, which provides mean, median, standard deviation, range, and interquartile range across chunks. The variance across chunks is itself a stylometric signal -- consistent authors show low standard deviation in their character-level features.

### Interpretation

- **Uppercase ratio** reflects capitalization habits. Higher values may indicate frequent use of acronyms, emphasis through capitalization, or genre conventions (e.g., legal documents).
- **Punctuation density and variety** capture an author's punctuation style. Dense punctuation with high variety indicates complex syntactic structure or an expressive writing style. Low variety with moderate density suggests a simpler, more uniform style.
- **Vowel-to-consonant ratio** varies by language and can also reflect vocabulary choices within a language. English text typically has a ratio around 0.6-0.7.
- **Letter frequency** profiles are remarkably stable for a given author writing in a given language, and deviations can signal topic shifts, code-switching, or different authorship.
- **Average word length** is one of the oldest stylometric features, correlating with vocabulary sophistication and formality.

---

## Implementation

### Core Algorithm

The implementation uses a chunked analysis approach (Issue #27) that divides text into segments of a configurable word count (default 1000 words). Each chunk is processed independently, and results are aggregated into `Distribution` objects that capture both central tendency and variance.

The single-chunk computation performs a single pass through the text to count:

1. **Letter counts** (a-z, case-insensitive) for frequency distribution
2. **Vowel and consonant counts** for the vowel-to-consonant ratio
3. **Uppercase and lowercase counts** for capitalization analysis
4. **Digit counts** for numeric character usage
5. **Whitespace counts** for formatting analysis
6. **Punctuation counts and types** from a comprehensive set of 30+ punctuation characters including basic punctuation, quotes (straight and curly), brackets, slashes, and special symbols

Word-level and sentence-level metrics (average word length, average sentence length in characters) are computed from whitespace-delimited tokens and sentence-boundary detection using `.`, `!`, and `?` delimiters.

### Key Features

- **Native chunked analysis**: Text is split into word-count-based chunks via `chunk_text()`. Each chunk produces independent metrics, and the aggregation step produces `Distribution` objects with mean, median, std, range, and IQR. This approach captures within-text variance, which is critical for stylometric fingerprinting.

- **Comprehensive punctuation set**: The module recognizes 30+ punctuation characters including curly quotes, em dashes, en dashes, ellipsis characters, and common special symbols. Both punctuation density (frequency) and punctuation variety (unique types) are tracked.

- **Single-pass efficiency**: Character classification is performed in a single iteration over the text, minimizing computational overhead.

- **NaN-safe aggregation**: Empty text and degenerate cases (e.g., no consonants, no words) return `float("nan")` rather than raising exceptions. Distribution aggregation filters out NaN values to produce valid statistics from the remaining chunks.

- **Rich metadata**: The result includes total counts for all character classes, enabling downstream analysis beyond the computed ratios.

---

## Usage

### API Examples

**Basic usage:**

```python
from pystylometry.character import compute_character_metrics

text = """The quick brown fox jumps over the lazy dog.
This sentence contains every letter of the alphabet!"""

result = compute_character_metrics(text)

# Aggregate metrics (mean across chunks)
print(f"Average word length: {result.avg_word_length:.2f}")
print(f"Punctuation density: {result.punctuation_density:.2f} per 100 words")
print(f"Uppercase ratio: {result.uppercase_ratio:.4f}")
print(f"Whitespace ratio: {result.whitespace_ratio:.4f}")
print(f"Vowel-to-consonant ratio: {result.vowel_consonant_ratio:.4f}")
```

**Accessing distributions for variance analysis:**

```python
result = compute_character_metrics(long_text, chunk_size=500)

# Distribution statistics reveal consistency of features
print(f"Avg word length mean: {result.avg_word_length_dist.mean:.2f}")
print(f"Avg word length std:  {result.avg_word_length_dist.std:.3f}")
print(f"Avg word length IQR:  {result.avg_word_length_dist.iqr:.3f}")

# Low std indicates a consistent authorial habit
# High std may indicate mixed content or multiple authors
```

**Letter frequency analysis:**

```python
result = compute_character_metrics(text)

# Letter frequency distribution (a-z)
for letter, freq in sorted(result.letter_frequency.items(), key=lambda x: -x[1])[:5]:
    print(f"  {letter}: {freq:.4f}")
# Shows the top 5 most frequent letters
```

**Accessing metadata for detailed counts:**

```python
result = compute_character_metrics(text)

meta = result.metadata
print(f"Total characters: {meta['total_characters']}")
print(f"Total letters: {meta['total_letters']}")
print(f"Total words: {meta['total_words']}")
print(f"Total sentences: {meta['total_sentences']}")
print(f"Punctuation types used: {meta['punctuation_types']}")
print(f"Vowels: {meta['vowel_count']}, Consonants: {meta['consonant_count']}")
```

**Comparing two texts:**

```python
from pystylometry.character import compute_character_metrics

formal = "The committee shall convene at the designated hour."
informal = "Can't believe they're meeting again... SO annoying!"

formal_result = compute_character_metrics(formal)
informal_result = compute_character_metrics(informal)

# Formal text: lower punctuation density, near-zero uppercase ratio
# Informal text: higher punctuation density, higher uppercase ratio
print(f"Formal uppercase ratio:   {formal_result.uppercase_ratio:.4f}")
print(f"Informal uppercase ratio: {informal_result.uppercase_ratio:.4f}")
print(f"Formal punctuation density:   {formal_result.punctuation_density:.2f}")
print(f"Informal punctuation density: {informal_result.punctuation_density:.2f}")
```

**Adjusting chunk size:**

```python
# Smaller chunks capture more local variation
result_small = compute_character_metrics(text, chunk_size=200)
print(f"Chunks: {result_small.chunk_count}, Std of word length: {result_small.avg_word_length_dist.std:.3f}")

# Larger chunks produce more stable per-chunk estimates
result_large = compute_character_metrics(text, chunk_size=2000)
print(f"Chunks: {result_large.chunk_count}, Std of word length: {result_large.avg_word_length_dist.std:.3f}")
```

---

## Limitations

- **Sentence detection is heuristic**: Sentences are split on `.`, `!`, and `?` characters. This approach does not handle abbreviations (e.g., "Dr.", "U.S.A."), decimal numbers (e.g., "3.14"), or other non-terminal periods correctly.

- **No character bigram or n-gram analysis**: While the module computes unigram letter frequencies, it does not compute character bigrams or higher-order n-grams. For character n-gram analysis, see the `ngrams` module and Sapkota et al. (2015) for guidance on which n-gram categories are most informative.

- **No character entropy computation**: Shannon entropy over character distributions is not directly computed in this module. The letter frequency distribution can be used to compute entropy externally if needed.

- **Whitespace-based tokenization**: Words are identified by splitting on whitespace, which may not handle hyphenated words, contractions, or languages without whitespace delimiters correctly.

- **English-centric letter set**: The vowel and consonant classification uses the standard English vowels (a, e, i, o, u) and the 26-letter Latin alphabet. Characters outside this set (accented characters, non-Latin scripts) are counted as letters by `isalpha()` but do not contribute to letter frequency, vowel, or consonant counts.

- **Chunk boundary effects**: Splitting text into word-count-based chunks may split sentences or paragraphs at arbitrary points, which can affect per-chunk sentence length calculations.

---

## References

Grieve, J. (2007). Quantitative authorship attribution: An evaluation of techniques. *Literary and Linguistic Computing*, 22(3), 251-270.

Sapkota, U., Bethard, S., Montes-y-Gomez, M., & Solorio, T. (2015). Not all character n-grams are created equal: A study in authorship attribution. *Proceedings of NAACL-HLT*, 93-102.

Stamatatos, E. (2009). A survey of modern authorship attribution methods. *Journal of the American Society for Information Science and Technology*, 60(3), 538-556.
