# Coleman-Liau Index

## Character-Based Grade Level Estimation

The Coleman-Liau Index (CLI) estimates the U.S. grade level needed to comprehend a text using letter and sentence counts per 100 words. Like the Automated Readability Index, it avoids syllable counting entirely, but uses a different normalization approach that measures features per 100 words rather than per word or per sentence.

---

## Theoretical Background

### Origins

Meri Coleman and T. L. Liau developed the Coleman-Liau Index in 1975, specifically designed for machine scoring of readability. Their key innovation was expressing features as rates per 100 words, which simplified both computation and interpretation. The formula was derived through regression analysis against comprehension test scores from the Cloze deletion procedure, where readers fill in missing words from a text.

Coleman and Liau explicitly designed their formula to avoid syllable counting, noting that syllable analysis was error-prone even for human raters (disagreements on syllable counts for words like "fire", "hired", and "real" were common). By using letter counts, which are unambiguous, they eliminated a significant source of measurement error.

### Mathematical Foundation

```
CLI = 0.0588 * L - 0.296 * S - 15.8
```

Where:
- `L` = average number of letters per 100 words
- `S` = average number of sentences per 100 words

To compute L and S:
```
L = (total_letters / total_words) * 100
S = (total_sentences / total_words) * 100
```

The formula has two components:
- **Letter density**: `0.0588 * L` captures word complexity. More letters per 100 words indicates longer, more complex vocabulary.
- **Sentence density**: `-0.296 * S` captures sentence length inversely. More sentences per 100 words means shorter sentences (easier to read), so this factor is negative.

The constant `-15.8` is the regression intercept.

### Interpretation

The Coleman-Liau Index produces a U.S. grade level:

| CLI Score | Approximate Grade Level |
|-----------|------------------------|
| 1-5 | Elementary school |
| 6-8 | Middle school |
| 9-12 | High school |
| 13-16 | College |
| 17+ | Graduate |

A score of 9.0, for example, indicates that the text is understandable by an average 9th-grade student. The implementation clamps grade levels to a non-negative range.

---

## Implementation

### Core Algorithm

The pystylometry implementation uses native chunked analysis:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `chunk_size` | 1000 | Number of words per chunk for distribution analysis |

For each chunk:
1. Split text into sentences
2. Tokenize and filter to words containing at least one alphabetic character
3. Count letters (alphabetic characters only) across all word tokens
4. Compute L (letters per 100 words) and S (sentences per 100 words)
5. Apply the Coleman-Liau formula with coefficients: `0.0588`, `-0.296`, `-15.8`
6. Compute grade level (rounded, non-negative)

### Key Features

**Letter Counting**: Counts only alphabetic characters (`char.isalpha()`) rather than all alphanumeric characters. This differs from ARI and ensures that numbers in the text do not inflate the letter count.

**Word Filtering**: Tokens are filtered to include only those containing at least one alphabetic character. This excludes pure numbers and punctuation from the word count, providing a more accurate measure of textual complexity.

**Per-100-Words Normalization**: The L and S values are computed per 100 words, matching Coleman and Liau's original specification. This normalization makes the intermediate values intuitive: an L of 450 means 450 letters per 100 words, or an average of 4.5 letters per word.

**Reliability Flag**: The metadata includes a `reliable` boolean flag set to `True` when the text contains 100 or more words.

**Result Dataclass**: Returns a `ColemanLiauResult` with:
- `cli_index`: Mean CLI score across chunks
- `grade_level`: Mean grade level across chunks
- `cli_index_dist`: Full distribution of per-chunk CLI scores
- `grade_level_dist`: Full distribution of per-chunk grade levels
- `chunk_size` and `chunk_count`: Analysis parameters
- `metadata`: Letters per 100 words, sentences per 100 words, total counts, reliability flag

---

## Usage

### API Examples

```python
from pystylometry.readability import compute_coleman_liau

# Basic usage
result = compute_coleman_liau("The quick brown fox jumps over the lazy dog. It was a sunny day.")
print(f"CLI Index: {result.cli_index:.1f}")
print(f"Grade Level: {result.grade_level:.0f}")

# Chunked analysis for stylometric fingerprinting
result = compute_coleman_liau(long_text, chunk_size=1000)
print(f"Mean CLI: {result.cli_index:.1f}")
print(f"Std Dev: {result.cli_index_dist.std:.2f}")
print(f"Chunks analyzed: {result.chunk_count}")

# Access per-100-words metrics
print(f"Letters per 100 words: {result.metadata['letters_per_100_words']:.1f}")
print(f"Sentences per 100 words: {result.metadata['sentences_per_100_words']:.2f}")

# Compare with other character-based formulas
from pystylometry.readability import compute_ari
ari_result = compute_ari(long_text)
print(f"CLI grade: {result.grade_level:.1f}")
print(f"ARI grade: {ari_result.grade_level:.1f}")
```

---

## Limitations

### Letter-Only Counting

By counting only alphabetic characters, the Coleman-Liau Index ignores the complexity introduced by numbers, symbols, and mixed alphanumeric tokens. Text with heavy numeric content (e.g., statistical reports) may appear simpler than it actually is.

### Per-100-Words Normalization

The per-100-words approach assumes that the text is long enough for the rates to be meaningful. For very short texts (fewer than 100 words), the S value (sentences per 100 words) can be unstable, as a single additional sentence significantly changes the ratio.

### Sentence Boundary Sensitivity

Like all readability formulas, CLI depends on accurate sentence segmentation. The formula is particularly sensitive because S (sentences per 100 words) directly affects the result through a relatively large coefficient (-0.296).

### English Calibration

The regression coefficients were derived from English text using the Cloze procedure. The relationship between letter density and comprehension difficulty is language-specific. Languages with longer average words (e.g., German, Finnish) would produce systematically higher CLI scores that do not accurately reflect difficulty for native speakers.

### No Vocabulary Assessment

CLI measures only surface features (letter and sentence patterns). It cannot distinguish between familiar long words (e.g., "grandmother") and unfamiliar long words (e.g., "grandiloquent"), treating them identically.

---

## References

Coleman, M., & Liau, T. L. (1975). A computer readability formula designed for machine scoring. *Journal of Applied Psychology*, 60(2), 283-284.

Klare, G. R. (1974-1975). Assessing readability. *Reading Research Quarterly*, 10(1), 62-102.

DuBay, W. H. (2004). The principles of readability. *Impact Information*, 1-76.
