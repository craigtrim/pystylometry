# Flesch Readability Formulas

## Flesch Reading Ease and Flesch-Kincaid Grade Level

The Flesch formulas are among the most widely used readability metrics in the English language. The Reading Ease score provides a 0-100 scale (higher = easier), while the Kincaid Grade Level maps directly to U.S. school grades. Together, they form the foundation of pystylometry's readability module.

---

## Theoretical Background

### Origins

Rudolf Flesch introduced the Reading Ease formula in 1948 as a practical tool for journalists and educators to assess text difficulty. The formula was derived from regression analysis against comprehension test scores, using two linguistic features: sentence length and word length (measured by syllables). Flesch's insight was that these two surface-level features capture much of what makes text difficult: long sentences strain working memory, and polysyllabic words are typically more abstract or specialized.

In 1975, J. Peter Kincaid and colleagues at the Naval Technical Training Command recalibrated Flesch's formula to output U.S. grade levels directly, producing the Flesch-Kincaid Grade Level formula. This adaptation was developed for the U.S. Navy to assess the readability of technical manuals and training materials.

### Mathematical Foundation

**Flesch Reading Ease:**

```
Reading Ease = 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
```

The formula has two components:
- **Sentence length factor**: `1.015 * (words / sentences)` penalizes long sentences
- **Word length factor**: `84.6 * (syllables / words)` penalizes polysyllabic words

The constant 206.835 sets the baseline so that typical English prose scores between 0 and 100.

**Flesch-Kincaid Grade Level:**

```
Grade Level = 0.39 * (total_words / total_sentences) + 11.8 * (total_syllables / total_words) - 15.59
```

This formula uses the same two linguistic features but with different regression coefficients, calibrated to produce a U.S. grade level (e.g., 8.0 means an 8th-grade reading level).

### Interpretation

**Reading Ease Scale:**

| Score Range | Difficulty | Typical Audience |
|-------------|-----------|------------------|
| 90-100 | Very Easy | 5th grade |
| 80-89 | Easy | 6th grade |
| 70-79 | Fairly Easy | 7th grade |
| 60-69 | Standard | 8th-9th grade |
| 50-59 | Fairly Difficult | 10th-12th grade |
| 30-49 | Difficult | College |
| 0-29 | Very Difficult | College graduate |

Scores can exceed these bounds. Technical and legal writing may produce negative Reading Ease scores. Extremely simple text (e.g., "The cat sat.") may exceed 100.

**Grade Level Interpretation:**

The Kincaid Grade Level indicates the minimum U.S. school grade required to understand the text. A score of 12.0 means the text requires a 12th-grade (senior high school) reading level. Values above 12 correspond to college and graduate-level difficulty.

---

## Implementation

### Core Algorithm

The pystylometry implementation follows the original formulas with native chunked analysis for stylometric fingerprinting:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `chunk_size` | 1000 | Number of words per chunk for distribution analysis |

The text is divided into chunks of `chunk_size` words, and both formulas are computed independently for each chunk. This produces a distribution of scores that captures variance across the document, which is essential for stylometric analysis. The mean across chunks serves as the overall score.

### Key Features

**Chunked Analysis**: Rather than computing a single score for the entire text, pystylometry divides the text into chunks and computes per-chunk scores. The resulting `Distribution` object provides mean, median, standard deviation, range, and IQR. The variance in readability across chunks is itself a stylometric fingerprint: some authors maintain consistent difficulty while others vary significantly.

**Syllable Counting**: Uses the CMU Pronouncing Dictionary via the `pronouncing` library for high-accuracy syllable counts. Falls back to vowel-group counting for words not in the dictionary. See `syllables.md` for details.

**Token Normalization**: Input tokens are normalized for readability analysis, filtering to valid word tokens and excluding punctuation and numbers. This ensures consistent measurement across different text formats.

**Result Dataclass**: Returns a `FleschResult` with:
- `reading_ease`: Mean Reading Ease across chunks
- `grade_level`: Mean Kincaid Grade Level across chunks
- `difficulty`: Human-readable difficulty label (e.g., "Standard", "Difficult")
- `reading_ease_dist`: Full distribution of per-chunk Reading Ease values
- `grade_level_dist`: Full distribution of per-chunk Grade Level values
- `chunk_size` and `chunk_count`: Analysis parameters
- `metadata`: Detailed counts (sentences, words, syllables, ratios)

---

## Usage

### API Examples

```python
from pystylometry.readability import compute_flesch

# Basic usage
result = compute_flesch("The cat sat on the mat. It was a good cat.")
print(f"Reading Ease: {result.reading_ease:.1f}")
print(f"Grade Level: {result.grade_level:.1f}")
print(f"Difficulty: {result.difficulty}")

# Chunked analysis for stylometric fingerprinting
result = compute_flesch(long_text, chunk_size=1000)
print(f"Mean Reading Ease: {result.reading_ease:.1f}")
print(f"Std Dev: {result.reading_ease_dist.std:.2f}")
print(f"Range: {result.reading_ease_dist.range:.1f}")
print(f"Chunks analyzed: {result.chunk_count}")

# Access per-chunk values for visualization
for i, value in enumerate(result.reading_ease_dist.values):
    print(f"Chunk {i}: {value:.1f}")

# Single-chunk mode (no chunking)
result = compute_flesch("Short text here.", chunk_size=1_000_000)
print(f"Chunks: {result.chunk_count}")  # 1

# Access metadata
print(f"Total sentences: {result.metadata['sentence_count']}")
print(f"Total words: {result.metadata['word_count']}")
print(f"Total syllables: {result.metadata['syllable_count']}")
print(f"Words per sentence: {result.metadata['words_per_sentence']:.1f}")
print(f"Syllables per word: {result.metadata['syllables_per_word']:.2f}")
```

---

## Limitations

### Syllable-Dependent Accuracy

Both formulas depend on accurate syllable counting. The CMU Pronouncing Dictionary provides high accuracy for common English words but may miscount rare, technical, or non-English words. The fallback vowel-counting heuristic is less accurate, particularly for words with silent letters or unusual vowel patterns.

### Sentence Boundary Detection

The formulas assume accurate sentence segmentation. Abbreviations (Dr., U.S.A.), ellipses, and other non-terminal periods can cause incorrect sentence counts, which directly affect the words-per-sentence ratio.

### English-Specific Calibration

The Flesch formulas were calibrated on English text. Applying them to other languages produces unreliable results because syllable patterns, word lengths, and sentence structures differ across languages. Language-specific adaptations exist (e.g., the Flesch-Douma formula for Dutch) but are not implemented in pystylometry.

### Content-Blind

The formulas measure surface features only. Text with short words and short sentences scores as "easy" even if the concepts are intellectually demanding. Conversely, text with long medical terms may score as "difficult" even if the ideas are straightforward.

### Score Bounds

Reading Ease scores are not strictly bounded to 0-100. Very simple text can exceed 100, and very complex text can produce negative scores. The difficulty labels are mapped from the standard ranges.

---

## References

Flesch, R. (1948). A new readability yardstick. *Journal of Applied Psychology*, 32(3), 221-233.

Kincaid, J. P., Fishburne, R. P., Rogers, R. L., & Chissom, B. S. (1975). Derivation of new readability formulas (Automated Readability Index, Fog Count and Flesch Reading Ease Formula) for Navy enlisted personnel. *Naval Technical Training Command Research Branch Report* 8-75.

DuBay, W. H. (2004). The principles of readability. *Impact Information*, 1-76.
