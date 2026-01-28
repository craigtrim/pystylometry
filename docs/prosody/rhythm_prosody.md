# Rhythm and Prosody Metrics

## Capturing the Musical Qualities of Written Language

---

## Theoretical Background

### Origins

Prosody -- the rhythm, stress, and intonation of language -- has been studied formally since classical antiquity, with Greek and Latin metrics providing systematic descriptions of poetic meter. Modern computational prosody extends these ideas to quantitative analysis of both poetry and prose.

Fabb and Halle (2008) developed a formal theory of poetic meter grounded in generative phonology, showing that metrical patterns can be described by rules operating on stress representations. Their framework provides the theoretical basis for the metrical foot estimation in this module: iambic (unstressed-stressed), trochaic (stressed-unstressed), dactylic (stressed-unstressed-unstressed), and anapestic (unstressed-unstressed-stressed) patterns.

Greene, Bodrumlu, and Knight (2010) demonstrated that computational analysis of rhythmic poetry can achieve practical results using the CMU Pronouncing Dictionary as a phonological resource. Their work on automatic scansion informs this module's approach to stress pattern extraction.

Lea, Mulligan, and Walton (2005) showed that sentence rhythm affects text comprehension. Their research establishes that sentence length alternation -- the deliberate variation of long and short sentences -- is a measurable stylistic property with cognitive significance. This module captures sentence rhythm through alternation and composite rhythm scores.

### Mathematical Foundation

**Syllable Statistics**:
- Mean syllables per word: `mu = SUM(syllable_count_i) / N`
- Standard deviation: `sigma = sqrt(SUM((s_i - mu)^2) / N)`
- Polysyllabic ratio: fraction of words with 3+ syllables
- Monosyllabic ratio: fraction of single-syllable words

**Rhythmic Regularity** (inverse coefficient of variation):

```
CV = sigma / mu
Regularity = 1 / CV
```

Higher regularity indicates more uniform syllable lengths, producing a metrically regular text. When CV = 0 (all words have equal syllable count), regularity is set to the word count as a practical upper bound.

**Stress Pattern Entropy** (Shannon entropy of metrical patterns):

```
H = -SUM p(pattern) * log2(p(pattern))
```

Each word's stress pattern is binarized (0 = unstressed, 1 = stressed) and treated as a categorical event. Higher entropy means more varied stress patterns; lower entropy means the text gravitates toward a few dominant metrical feet.

**Phonological Feature Densities** (per 100 words):

- Alliteration density: consecutive word pairs sharing initial consonant sounds
- Assonance density: consecutive word pairs sharing vowel phonemes
- Consonance density: consecutive word pairs sharing consonant phonemes

```
density = (matching_pairs / total_words) * 100
```

**Sentence Rhythm**:
- Length alternation: mean absolute difference between consecutive sentence lengths, normalized by mean sentence length
- Rhythm score: composite of alternation and coefficient of variation of sentence lengths

```
alternation = mean(|len_i - len_{i-1}|) / mean_sentence_length
rhythm_score = (alternation + CV_sentence) / 2
```

**Metrical Foot Estimation**:

Word-level stress patterns are decomposed into overlapping bigrams and trigrams:
- Iamb: (0, 1) -- unstressed-stressed
- Trochee: (1, 0) -- stressed-unstressed
- Dactyl: (1, 0, 0) -- stressed-unstressed-unstressed
- Anapest: (0, 0, 1) -- unstressed-unstressed-stressed

Each foot type ratio is reported as a fraction of total detected patterns.

### Interpretation

| Metric | Low Value | High Value |
|--------|-----------|------------|
| Rhythmic regularity | Varied syllable lengths; natural prose | Uniform syllable lengths; metered text |
| Stress entropy | Few dominant patterns; repetitive rhythm | Many varied patterns; complex rhythm |
| Alliteration density | Minimal sound repetition | Deliberate sound patterning (poetry, rhetoric) |
| Sentence alternation | Monotonous sentence lengths | Dynamic pacing; varied sentence structure |
| Polysyllabic ratio | Simple vocabulary | Complex, academic vocabulary |
| Iambic ratio | Non-iambic rhythm | English prose natural tendency (iambic) |

---

## Implementation

### Core Algorithm

The module uses the CMU Pronouncing Dictionary (via the `pronouncing` package) for phonological analysis:

1. **Word extraction**: Extract alphabetic words from text using regex `[a-zA-Z]+`
2. **Syllable counting**: Look up each word in the CMU dictionary; fall back to vowel-group heuristic for unknown words
3. **Stress extraction**: Extract stress patterns (0=no stress, 1=primary, 2=secondary) from CMU phoneme sequences
4. **Phoneme extraction**: Extract vowel and consonant phonemes for assonance and consonance detection
5. **Initial sound extraction**: Determine initial consonant sound for alliteration detection
6. **Consonant cluster analysis**: Detect initial and final consonant clusters using regex patterns
7. **Sentence segmentation**: Split on sentence-ending punctuation for sentence rhythm analysis
8. **Metrical foot classification**: Decompose stress patterns into bigram and trigram foot patterns

### Key Features

- **CMU Dictionary integration**: Accurate phonological data for English words, with LRU caching (4096 entries) for performance
- **Fallback heuristics**: Words not in the CMU dictionary use a vowel-counting heuristic with silent-e adjustment
- **Comprehensive metrics**: 19 distinct metrics covering syllable patterns, rhythmic regularity, phonological features, syllable complexity, sentence rhythm, and metrical feet
- **CMU coverage reporting**: Metadata includes the fraction of unique words found in the CMU dictionary, allowing users to assess data quality
- **Metadata richness**: Returns syllable distribution histogram, per-word stress patterns, and sentence/word counts

### Dependencies

Requires the `pronouncing` package for CMU dictionary access:

```bash
pip install pystylometry[readability]
```

### Return Value

The function returns a `RhythmProsodyResult` dataclass with the following fields:

**Syllable patterns**: `mean_syllables_per_word`, `syllable_std_dev`, `polysyllabic_ratio`, `monosyllabic_ratio`

**Rhythmic regularity**: `rhythmic_regularity`, `syllable_cv`, `stress_pattern_entropy`

**Sentence rhythm**: `sentence_length_alternation`, `sentence_rhythm_score`

**Phonological features**: `alliteration_density`, `assonance_density`, `consonance_density`

**Syllable complexity**: `mean_consonant_cluster_length`, `initial_cluster_ratio`, `final_cluster_ratio`

**Metrical feet**: `iambic_ratio`, `trochaic_ratio`, `dactylic_ratio`, `anapestic_ratio`

**Metadata**: `word_count`, `unique_words`, `sentence_count`, `total_syllables`, `cmu_coverage`, `syllable_distribution`, `word_stress_patterns`

---

## Usage

### API Examples

```python
from pystylometry.prosody import compute_rhythm_prosody

# Basic prosody analysis
result = compute_rhythm_prosody(
    "The quick brown fox jumps over the lazy dog."
)
print(f"Syllables/word: {result.mean_syllables_per_word:.2f}")
print(f"Rhythmic regularity: {result.rhythmic_regularity:.3f}")
print(f"Stress entropy: {result.stress_pattern_entropy:.2f} bits")

# Phonological features
print(f"Alliteration density: {result.alliteration_density:.2f} per 100 words")
print(f"Assonance density: {result.assonance_density:.2f} per 100 words")
print(f"Consonance density: {result.consonance_density:.2f} per 100 words")

# Metrical analysis
print(f"Iambic ratio: {result.iambic_ratio:.3f}")
print(f"Trochaic ratio: {result.trochaic_ratio:.3f}")
print(f"Dactylic ratio: {result.dactylic_ratio:.3f}")
print(f"Anapestic ratio: {result.anapestic_ratio:.3f}")

# Sentence rhythm
print(f"Sentence alternation: {result.sentence_length_alternation:.3f}")
print(f"Sentence rhythm score: {result.sentence_rhythm_score:.3f}")

# Syllable complexity
print(f"Mean cluster length: {result.mean_consonant_cluster_length:.2f}")
print(f"Initial cluster ratio: {result.initial_cluster_ratio:.3f}")
print(f"Final cluster ratio: {result.final_cluster_ratio:.3f}")

# Access metadata
print(f"CMU coverage: {result.metadata['cmu_coverage']:.1%}")
print(f"Syllable distribution: {result.metadata['syllable_distribution']}")

# Compare authors
result_a = compute_rhythm_prosody(author_a_text)
result_b = compute_rhythm_prosody(author_b_text)
print(f"Author A iambic: {result_a.iambic_ratio:.3f}")
print(f"Author B iambic: {result_b.iambic_ratio:.3f}")
```

---

## Limitations

### English Only

The CMU Pronouncing Dictionary covers English words only. Non-English text will fall back entirely to the vowel-counting heuristic, which is language-dependent and may produce unreliable syllable counts.

### CMU Dictionary Coverage

The CMU dictionary contains approximately 134,000 entries. Rare words, proper nouns, technical jargon, and neologisms may not be found. The `cmu_coverage` metadata field reports what fraction of unique words were resolved via the dictionary. Low coverage (below 70%) suggests results should be interpreted cautiously.

### Simplified Meter Model

The metrical foot estimation uses a simplified model that classifies individual words into foot patterns. True poetic meter operates across word boundaries (e.g., "to BE or NOT to BE" spans multiple words in an iambic pattern). The word-level approach provides a useful approximation for prose stylometry but should not be treated as formal scansion.

### Text Length

For reliable prosodic statistics, at least 100 words are recommended. Shorter texts will produce valid but potentially unstable metrics, particularly for density measures (alliteration, assonance, consonance) and sentence rhythm.

### Sentence Segmentation

Sentences are split on `.`, `!`, and `?` punctuation. Abbreviations (e.g., "Dr.", "U.S.") may cause false sentence boundaries. This affects sentence rhythm metrics but not word-level metrics.

---

## References

Fabb, Nigel, and Morris Halle. *Meter in Poetry: A New Theory*. Cambridge University Press, 2008.

Greene, Erica, Tugba Bodrumlu, and Kevin Knight. "Automatic Analysis of Rhythmic Poetry with Applications to Generation and Translation." *Proceedings of EMNLP*, 2010, pp. 524-533.

Lea, R. Brooke, Eileen J. Mulligan, and Jeffrey H. Walton. "Sentence Rhythm and Text Comprehension." *Memory & Cognition*, vol. 33, no. 3, 2005, pp. 388-396.

Clements, George N., and Samuel J. Keyser. *CV Phonology: A Generative Theory of the Syllable*. MIT Press, 1983.

Shannon, C. E. "A Mathematical Theory of Communication." *Bell System Technical Journal*, vol. 27, no. 3, 1948, pp. 379-423.
