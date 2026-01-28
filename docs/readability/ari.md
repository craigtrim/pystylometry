# Automated Readability Index

## Character-Based Readability Assessment

The Automated Readability Index (ARI) estimates readability using character counts and word counts rather than syllable counts. Developed in 1967 for automated text processing, ARI was one of the first readability formulas designed for machine computation, making it particularly efficient for large-scale text analysis.

---

## Theoretical Background

### Origins

R. J. Senter and E. A. Smith developed the Automated Readability Index in 1967 at the Aerospace Medical Research Laboratories for the U.S. Air Force. The primary motivation was to create a readability formula that could be computed by early electronic text processing systems, which could count characters and words but could not perform syllable analysis. By replacing syllable counts with character counts, ARI eliminated the most computationally expensive component of traditional readability formulas.

The formula was validated against standardized reading comprehension tests and showed comparable predictive validity to syllable-based formulas like the Flesch Reading Ease, despite using a simpler input feature.

### Mathematical Foundation

```
ARI = 4.71 * (characters / words) + 0.5 * (words / sentences) - 21.43
```

Where:
- `characters` = total number of alphanumeric characters in the text
- `words` = total number of word tokens
- `sentences` = total number of sentences

The formula has two components:
- **Character density**: `4.71 * (characters / words)` measures average word length in characters. Longer words tend to be more abstract, specialized, or morphologically complex.
- **Sentence length**: `0.5 * (words / sentences)` measures average sentence length. Longer sentences place greater demands on working memory.

The constant `-21.43` is the regression intercept, calibrated so that the output approximates U.S. grade level.

### Interpretation

ARI produces a score that maps to U.S. grade levels and corresponding age ranges:

| ARI Score | Grade Level | Age Range |
|-----------|-------------|-----------|
| 1 | Kindergarten | 5-6 years |
| 2-5 | Elementary | 6-11 years |
| 6-8 | Middle School | 11-14 years |
| 9-12 | High School | 14-18 years |
| 13-14 | College | 18-22 years |
| 15+ | Graduate | 22+ years |

The implementation clamps grade levels to the 0-20 range and rounds to the nearest integer for the `grade_level` field. The raw `ari_score` is provided without clamping for precise analysis.

---

## Implementation

### Core Algorithm

The pystylometry implementation uses native chunked analysis:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `chunk_size` | 1000 | Number of words per chunk for distribution analysis |

For each chunk:
1. Split text into sentences
2. Tokenize the text
3. Count alphanumeric characters across the full text
4. Compute characters-per-word and words-per-sentence ratios
5. Apply the ARI formula with coefficients: `4.71`, `0.5`, `-21.43`
6. Map to grade level and age range

### Key Features

**No Syllable Counting Required**: Unlike Flesch, SMOG, and Gunning Fog, ARI uses only character counts. This makes it faster to compute and eliminates dependency on syllable-counting accuracy. It does not require the `pronouncing` library.

**Character Counting**: Counts all alphanumeric characters (`char.isalnum()`), which includes both letters and digits. This means numbers in the text contribute to the character count but not to the word length in the same way as alphabetic characters.

**Age Range Mapping**: Provides human-readable age range labels (e.g., "11-14 years (Middle School)") in addition to numeric grade levels, making results accessible to non-technical users.

**Reliability Flag**: The metadata includes a `reliable` boolean flag set to `True` when the text contains 100 or more words. Shorter texts may produce unreliable scores due to small sample effects.

**Result Dataclass**: Returns an `ARIResult` with:
- `ari_score`: Mean ARI score across chunks
- `grade_level`: Mean grade level across chunks
- `age_range`: Human-readable age range for the mean grade level
- `ari_score_dist`: Full distribution of per-chunk ARI scores
- `grade_level_dist`: Full distribution of per-chunk grade levels
- `chunk_size` and `chunk_count`: Analysis parameters
- `metadata`: Detailed counts and ratios (characters, words, sentences, characters per word, words per sentence, reliability flag)

---

## Usage

### API Examples

```python
from pystylometry.readability import compute_ari

# Basic usage
result = compute_ari("The quick brown fox jumps over the lazy dog. It was a sunny day.")
print(f"ARI Score: {result.ari_score:.1f}")
print(f"Grade Level: {result.grade_level:.0f}")
print(f"Age Range: {result.age_range}")

# Chunked analysis for stylometric fingerprinting
result = compute_ari(long_text, chunk_size=1000)
print(f"Mean ARI: {result.ari_score:.1f}")
print(f"Std Dev: {result.ari_score_dist.std:.2f}")
print(f"Range: {result.ari_score_dist.range:.1f}")
print(f"Chunks analyzed: {result.chunk_count}")

# Check reliability
if result.metadata.get("reliable"):
    print("Result is reliable (100+ words)")
else:
    print("Warning: short text, result may be unreliable")

# Access detailed metrics
print(f"Characters per word: {result.metadata['characters_per_word']:.2f}")
print(f"Words per sentence: {result.metadata['words_per_sentence']:.1f}")
```

---

## Limitations

### Character-Based Approximation

Using character counts as a proxy for word complexity is a simplification. Short words can be difficult (e.g., "qi", "pH") and long words can be common (e.g., "everything", "understand"). However, the statistical correlation between word length and difficulty holds well in aggregate.

### Sensitivity to Numbers and Abbreviations

ARI counts all alphanumeric characters. Text with many numbers (e.g., financial reports, scientific data) may produce skewed character-per-word ratios. Similarly, abbreviations and acronyms (e.g., "NASA", "HTML") can affect the metric.

### Sentence Boundary Issues

Like all readability formulas that use sentence counts, ARI is sensitive to sentence segmentation accuracy. Abbreviations with periods, list items, and non-standard punctuation can cause incorrect sentence counts.

### English Calibration

The regression coefficients were derived from English text. Languages with different morphological patterns, such as German (which frequently compounds words) or Chinese (which uses single characters per concept), would produce meaningless results.

### Linear Model

ARI assumes a linear relationship between its features and reading difficulty. In practice, the relationship may be non-linear at the extremes: very short average word lengths do not necessarily mean very easy text, and very long average word lengths may overestimate difficulty.

---

## References

Senter, R. J., & Smith, E. A. (1967). Automated readability index. *AMRL-TR-6620*. Aerospace Medical Research Laboratories, Wright-Patterson Air Force Base, Ohio.

Kincaid, J. P., Fishburne, R. P., Rogers, R. L., & Chissom, B. S. (1975). Derivation of new readability formulas for Navy enlisted personnel. *Naval Technical Training Command Research Branch Report* 8-75.

DuBay, W. H. (2004). The principles of readability. *Impact Information*, 1-76.
