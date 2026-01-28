# SMOG Index

## Simple Measure of Gobbledygook

The SMOG Index estimates the years of education needed to understand a piece of writing. Developed specifically for healthcare and public communication materials, SMOG focuses exclusively on polysyllabic words as the primary indicator of text difficulty. It is considered one of the most accurate readability formulas for estimating comprehension difficulty.

---

## Theoretical Background

### Origins

G. Harry McLaughlin introduced the SMOG grading formula in 1969 as a simpler, more reliable alternative to existing readability formulas. McLaughlin observed that the number of polysyllabic words (words with three or more syllables) was the single strongest predictor of reading difficulty. By focusing on this one variable, SMOG achieved comparable or better predictive validity than multi-variable formulas like Flesch Reading Ease.

The acronym SMOG stands for "Simple Measure of Gobbledygook," a deliberate play on the Gunning Fog Index (another readability formula that also uses polysyllabic word counts). McLaughlin designed SMOG to be calculated by hand, requiring only a count of polysyllabic words and sentences.

### Mathematical Foundation

```
SMOG = 1.043 * sqrt(polysyllable_count * (30 / sentence_count)) + 3.1291
```

Where:
- `polysyllable_count` = number of words with 3 or more syllables
- `sentence_count` = number of sentences in the text
- The factor `30 / sentence_count` normalizes to a 30-sentence sample

The formula can be understood in two steps:
1. **Normalize**: Scale the polysyllable count to a standard 30-sentence sample
2. **Transform**: Apply square root transformation and linear regression coefficients

The square root transformation is critical because it stabilizes variance and produces a more linear relationship with comprehension difficulty.

**Simplified hand-calculation version** (McLaughlin's original):
```
SMOG = 3 + sqrt(polysyllable_count_in_30_sentences)
```

The pystylometry implementation uses the full regression formula for higher precision.

### Interpretation

The SMOG index directly estimates the number of years of education needed to comprehend the text:

| SMOG Score | Education Level |
|------------|----------------|
| 5-6 | 5th-6th grade |
| 7-8 | 7th-8th grade (middle school) |
| 9-10 | 9th-10th grade (high school) |
| 11-12 | 11th-12th grade (senior high school) |
| 13-16 | College level |
| 17+ | Graduate level |

Healthcare literacy guidelines typically recommend a SMOG score of 6 or below for patient-facing materials, as this corresponds to the reading level of the average American adult.

---

## Implementation

### Core Algorithm

The pystylometry implementation uses native chunked analysis:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `chunk_size` | 1000 | Number of words per chunk for distribution analysis |

For each chunk:
1. Split text into sentences
2. Tokenize and normalize to word tokens
3. Count polysyllabic words (3+ syllables using CMU dictionary)
4. Apply the SMOG formula
5. Compute grade level (rounded, clamped to 0-20 range)

### Key Features

**Polysyllable Detection**: Uses the CMU Pronouncing Dictionary for accurate syllable counting. A word is polysyllabic if `count_syllables(word) >= 3`. This avoids the inaccuracies of simple vowel-group counting for common polysyllabic words.

**Short Text Warning**: The SMOG formula was calibrated on 30-sentence samples. When the total text contains fewer than 30 sentences, the metadata includes a `"warning": "Less than 30 sentences"` flag. Results on short texts may be less reliable.

**Result Dataclass**: Returns a `SMOGResult` with:
- `smog_index`: Mean SMOG index across chunks
- `grade_level`: Mean grade level across chunks (rounded)
- `smog_index_dist`: Full distribution of per-chunk SMOG values
- `grade_level_dist`: Full distribution of per-chunk grade levels
- `chunk_size` and `chunk_count`: Analysis parameters
- `metadata`: Counts (sentences, words, polysyllables) and warnings

---

## Usage

### API Examples

```python
from pystylometry.readability import compute_smog

# Basic usage
result = compute_smog("The implementation of extraordinary administrative procedures requires sophisticated understanding.")
print(f"SMOG Index: {result.smog_index:.1f}")
print(f"Grade Level: {result.grade_level:.0f}")

# Chunked analysis for stylometric fingerprinting
result = compute_smog(long_text, chunk_size=1000)
print(f"Mean SMOG: {result.smog_index:.1f}")
print(f"Std Dev: {result.smog_index_dist.std:.2f}")
print(f"Chunks analyzed: {result.chunk_count}")

# Check for short-text warning
if result.metadata.get("warning"):
    print(f"Warning: {result.metadata['warning']}")

# Access polysyllable counts
print(f"Total polysyllables: {result.metadata['polysyllable_count']}")
print(f"Total sentences: {result.metadata['sentence_count']}")
print(f"Total words: {result.metadata['word_count']}")
```

---

## Limitations

### Sample Size Sensitivity

SMOG was calibrated on 30-sentence samples. For texts shorter than 30 sentences, the normalization factor `30 / sentence_count` amplifies the polysyllable count, which can inflate scores. The implementation warns about this but does not refuse to compute.

### Polysyllable Definition

The strict definition of polysyllabic (3+ syllables) means that common words like "beautiful" (3 syllables) and "important" (3 syllables) are counted equally with truly difficult words like "antidisestablishmentarianism." This can overestimate difficulty for text that uses common polysyllabic words.

### English-Specific

Like all readability formulas based on syllable counting, SMOG is calibrated for English. Languages with different morphological patterns (e.g., agglutinative languages where words are inherently long) would produce invalid results.

### Single Variable

SMOG deliberately uses only one predictor variable (polysyllable density). While this simplicity is a strength for reliability, it means SMOG is blind to sentence complexity. Two texts with identical polysyllable densities but very different sentence structures will receive the same SMOG score.

### Healthcare Context

SMOG was developed and validated primarily in the context of healthcare materials. While it generalizes well to other domains, its calibration may be most accurate for expository prose rather than fiction, poetry, or technical documentation.

---

## References

McLaughlin, G. H. (1969). SMOG grading: A new readability formula. *Journal of Reading*, 12(8), 639-646.

McLaughlin, G. H. (1974). Temptations of the Flesch. *Instructional Science*, 2(4), 367-384.

Wang, L. W., Miller, M. J., Schmitt, M. R., & Wen, F. K. (2013). Assessing readability formula differences with written health information materials: Application, results, and recommendations. *Research in Social and Administrative Pharmacy*, 9(5), 503-516.
