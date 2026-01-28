# Additional Readability Formulas

## Dale-Chall, Linsear Write, Fry, FORCAST, and Powers-Sumner-Kearl

Beyond the core readability formulas (Flesch, SMOG, Gunning Fog, Coleman-Liau, ARI), pystylometry implements five additional formulas that offer alternative approaches to measuring text difficulty. Each formula was designed for a specific context or addresses a limitation of earlier formulas, making them valuable for cross-validation and comprehensive readability assessment.

---

## Theoretical Background

### Origins

**Dale-Chall (1948)**: Edgar Dale and Jeanne Chall developed a readability formula based on a list of approximately 3,000 words that 80% of American 4th-graders could understand. Words not on this "familiar words" list are counted as "difficult." This vocabulary-based approach captures semantic difficulty rather than relying on surface features like syllable count.

**Linsear Write (1973)**: Developed by the U.S. Air Force for assessing technical writing, Linsear Write distinguishes between "easy" words (2 or fewer syllables) and "hard" words (3 or more syllables), weighting hard words three times more than easy words. It was designed for use with technical manuals and training materials.

**Fry Readability Graph (1968)**: Edward Fry created a visual graph-based method that plots average sentence length against average syllables per 100 words. The intersection point on the graph indicates the grade level. Unlike formula-based methods, this approach uses a lookup table derived from the graph.

**FORCAST (1973)**: Developed by John Caylor and colleagues at the Human Resources Research Organization for the U.S. Army, FORCAST is unique among readability formulas in that it uses only single-syllable word counts, requiring no sentence segmentation at all. It was designed for evaluating forms, tables, and list-based military documents where traditional sentence structure is absent.

**Powers-Sumner-Kearl (1958)**: R. D. Powers, W. A. Sumner, and B. E. Kearl recalibrated the original Flesch formula using updated comprehension data from primary-grade students. The result is a formula that produces more accurate grade-level estimates for elementary-level text.

### Mathematical Foundation

**Dale-Chall:**
```
Raw Score = 0.1579 * (difficult_words / total_words * 100) + 0.0496 * (total_words / total_sentences)

If difficult_words_percentage > 5%:
    Adjusted Score = Raw Score + 3.6365
Else:
    Adjusted Score = Raw Score
```

Where "difficult words" are words not found in the Dale-Chall familiar words list.

**Linsear Write:**
```
easy_word_count = words with <= 2 syllables
hard_word_count = words with >= 3 syllables
weighted_sum = easy_word_count + (hard_word_count * 3)
raw_score = weighted_sum / sentence_count

If raw_score > 20:
    grade_level = raw_score / 2
Else:
    grade_level = (raw_score - 2) / 2
```

**Fry Readability Graph:**

The Fry method uses two coordinates to locate a point on the readability graph:
```
x = average syllables per 100 words
y = average sentence length (words per sentence)
```

The grade level is determined by the region of the graph where the point falls. The pystylometry implementation uses a lookup table approximation of Fry's original graph.

**FORCAST:**
```
Grade Level = 20 - (N / 10)
```

Where N = number of single-syllable words in a 150-word sample. For samples shorter than 150 words, N is scaled proportionally: `N_scaled = count * (150 / sample_size)`.

**Powers-Sumner-Kearl:**
```
Grade Level = 0.0778 * avg_sentence_length + 0.0455 * avg_syllables_per_word - 2.2029
```

This uses the same two features as Flesch (sentence length and syllable density) but with different regression coefficients calibrated for primary-grade readers.

### Interpretation

**Dale-Chall Score Mapping:**

| Score | Grade Level |
|-------|-------------|
| < 5.0 | 4th grade and below |
| 5.0-5.9 | 5th-6th grade |
| 6.0-6.9 | 7th-8th grade |
| 7.0-7.9 | 9th-10th grade |
| 8.0-8.9 | 11th-12th grade |
| 9.0-9.9 | College |
| 10.0+ | College Graduate |

**Fry Graph Zones:**

The Fry graph defines a "valid" region and several boundary zones:
- `valid`: Point falls within the graph's defined regions
- `above_graph`: Syllable count > 185 or sentence length > 25 (extremely difficult text)
- `below_graph`: Syllable count < 110 (unusually simple text)

---

## Implementation

### Core Algorithm

All five formulas use native chunked analysis for stylometric fingerprinting:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `chunk_size` | 1000 | Number of words per chunk for distribution analysis |

Each formula follows the same pattern: divide text into chunks, compute per-chunk metrics, aggregate into distributions.

### Key Features

**Dale-Chall Familiar Words List**: The implementation includes a representative subset of approximately 1,200 words from the full 3,000-word Dale-Chall list. The subset covers articles, pronouns, conjunctions, prepositions, common verbs (with all conjugated forms), common nouns, adjectives, adverbs, and numbers. Words are matched case-insensitively.

**Dale-Chall Adjustment Threshold**: When more than 5% of words are difficult (not on the familiar list), the raw score is adjusted by adding 3.6365. This non-linear adjustment reflects the finding that texts with many unfamiliar words are disproportionately more difficult.

**Linsear Write Weighting**: Hard words (3+ syllables) receive triple weight compared to easy words (1-2 syllables). The final grade level uses a bifurcated formula based on whether the raw score exceeds 20.

**Fry Sample Size**: The Fry method samples the first 100 words of each chunk (or fewer if the chunk is shorter). This matches Fry's original recommendation of using 100-word passages.

**FORCAST Sample Size**: FORCAST samples the first 150 words of each chunk. For shorter chunks, the single-syllable count is scaled proportionally to a 150-word equivalent.

**Powers-Sumner-Kearl Flesch Comparison**: The PSK result metadata includes the equivalent Flesch Reading Ease and Flesch-Kincaid Grade Level computed from the same underlying features (sentence length and syllable density), along with the difference between PSK and Flesch-Kincaid. This enables direct comparison of the two calibrations.

**Result Dataclasses**: Each formula returns a typed result with:
- Primary metric(s) and grade level
- Distribution objects for all per-chunk values
- Chunk parameters
- Formula-specific metadata and reliability flag

---

## Usage

### API Examples

```python
from pystylometry.readability import (
    compute_dale_chall,
    compute_linsear_write,
    compute_fry,
    compute_forcast,
    compute_powers_sumner_kearl,
)

# Dale-Chall
result = compute_dale_chall(long_text, chunk_size=1000)
print(f"Dale-Chall Score: {result.dale_chall_score:.1f}")
print(f"Grade Level: {result.grade_level}")
print(f"Difficult words: {result.difficult_word_count}")
print(f"Difficult word ratio: {result.difficult_word_ratio:.2%}")
print(f"Avg sentence length: {result.avg_sentence_length:.1f}")
print(f"Score adjusted: {result.metadata['adjusted']}")

# Linsear Write
result = compute_linsear_write(long_text, chunk_size=1000)
print(f"Linsear Score: {result.linsear_score:.1f}")
print(f"Grade Level: {result.grade_level:.0f}")
print(f"Easy words: {result.easy_word_count}")
print(f"Hard words: {result.hard_word_count}")

# Fry Readability Graph
result = compute_fry(long_text, chunk_size=1000)
print(f"Avg sentence length: {result.avg_sentence_length:.1f}")
print(f"Avg syllables per 100 words: {result.avg_syllables_per_100:.1f}")
print(f"Grade Level: {result.grade_level}")
print(f"Graph Zone: {result.graph_zone}")

# FORCAST (works without sentence segmentation)
result = compute_forcast(long_text, chunk_size=1000)
print(f"FORCAST Score: {result.forcast_score:.1f}")
print(f"Grade Level: {result.grade_level:.0f}")
print(f"Single-syllable ratio: {result.single_syllable_ratio:.2%}")

# Powers-Sumner-Kearl
result = compute_powers_sumner_kearl(long_text, chunk_size=1000)
print(f"PSK Score: {result.psk_score:.1f}")
print(f"Grade Level: {result.grade_level:.1f}")
print(f"Difference from Flesch-Kincaid: {result.metadata['difference_from_flesch']:.2f}")

# Cross-validation: compare multiple formulas
from pystylometry.readability import compute_flesch, compute_ari
flesch = compute_flesch(long_text)
ari = compute_ari(long_text)
dale_chall = compute_dale_chall(long_text)
fog = compute_forcast(long_text)

print(f"Flesch Grade: {flesch.grade_level:.1f}")
print(f"ARI Grade: {ari.grade_level:.1f}")
print(f"Dale-Chall Grade: {dale_chall.grade_level}")
print(f"FORCAST Grade: {fog.grade_level:.1f}")
```

---

## Limitations

### Dale-Chall Word List Subset

The implementation uses a representative subset (~1,200 words) of the full Dale-Chall list (~3,000 words). Words that are on the full list but not in the subset will be incorrectly classified as "difficult," potentially inflating the Dale-Chall score. The subset covers the most common everyday words and their inflected forms.

### Dale-Chall Case Sensitivity

Words are matched case-insensitively against the familiar words list. This means proper nouns that happen to match common words (e.g., "Will" as a name vs. "will" as a modal verb) are always treated as familiar.

### Linsear Write Bifurcation

The grade level formula changes behavior at a raw score threshold of 20. This creates a discontinuity in the grade level output near this threshold, which can cause unexpected jumps in scores for texts near the boundary.

### Fry Graph Discretization

The Fry method maps continuous coordinate values to discrete grade levels using a lookup table. This discretization means that small changes in sentence length or syllable density can cause grade level jumps, unlike the continuous output of formula-based methods.

### FORCAST Sentence Independence

FORCAST deliberately ignores sentence structure, using only single-syllable word counts. While this makes it applicable to non-prose text (forms, lists, tables), it also means it cannot distinguish between well-structured text with simple vocabulary and poorly structured text with simple vocabulary.

### Powers-Sumner-Kearl Grade Range

PSK was calibrated on primary-grade reading materials (approximately grades 1-6). It may produce less accurate results for text at higher grade levels, where the original Flesch-Kincaid formula may be more appropriate.

### Sample Size Effects

Both Fry (100-word samples) and FORCAST (150-word samples) use fixed sample sizes. For chunks shorter than these sizes, the scores are extrapolated, which introduces uncertainty. The metadata includes sample size information for assessing reliability.

---

## References

Dale, E., & Chall, J. S. (1948). A formula for predicting readability. *Educational Research Bulletin*, 27(1), 11-20, 28.

Chall, J. S., & Dale, E. (1995). *Readability revisited: The new Dale-Chall readability formula*. Brookline Books.

Fry, E. (1968). A readability formula that saves time. *Journal of Reading*, 11(7), 513-516, 575-578.

Caylor, J. S., Sticht, T. G., Fox, L. C., & Ford, J. P. (1973). Methodologies for determining reading requirements of military occupational specialties. *Human Resources Research Organization Technical Report* 73-5.

Powers, R. D., Sumner, W. A., & Kearl, B. E. (1958). A recalculation of four adult readability formulas. *Journal of Educational Psychology*, 49(2), 99-105.

Klare, G. R. (1974-1975). Assessing readability. *Reading Research Quarterly*, 10(1), 62-102.
