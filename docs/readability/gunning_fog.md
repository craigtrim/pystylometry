# Gunning Fog Index

## Readability Through Complex Word Analysis

The Gunning Fog Index estimates the years of formal education needed to understand text on a first reading. Unlike other readability formulas that rely on syllable counts or character statistics, Gunning Fog specifically identifies "complex words" using linguistic criteria, making it sensitive to vocabulary sophistication. The pystylometry implementation offers dual-mode detection: an NLP-enhanced mode using spaCy for accurate complex word identification, and a basic heuristic mode as a fallback.

---

## Theoretical Background

### Origins

Robert Gunning developed the Fog Index in 1952 as part of his consulting work helping businesses improve the clarity of their writing. Published in *The Technique of Clear Writing*, the formula was designed to be practical for editors and writers to apply by hand. Gunning observed that two factors made text "foggy" (unclear): long sentences and complex words. His formula combines these two measures with a single coefficient.

The name "Fog" refers to the fog-like obscurity that difficult writing creates for readers. Gunning advocated for clear, simple prose and used his index as a diagnostic tool to identify writing that needed simplification.

### Mathematical Foundation

```
Fog Index = 0.4 * (words_per_sentence + 100 * (complex_words / total_words))
```

Which is equivalent to:
```
Fog Index = 0.4 * (average_sentence_length + complex_word_percentage)
```

Where:
- `words_per_sentence` = total words / total sentences
- `complex_words` = count of words with 3+ syllables, excluding specific categories
- `complex_word_percentage` = (complex_words / total_words) * 100

**Complex Word Definition (Gunning, 1952):**

A word is complex if it has 3 or more syllables AND is NOT:
1. **A proper noun** (names, places, organizations)
2. **A compound word** (hyphenated words)
3. **A common verb form** with endings -es, -ed, or -ing that inflate syllable count

These exclusions prevent inflated complexity scores from proper nouns (which may be long but are not inherently difficult) and from regular inflections of simple verbs (e.g., "created" has 3 syllables but its root "create" is a common word).

### Interpretation

| Fog Index | Reading Level |
|-----------|--------------|
| 6 | 6th grade (easy) |
| 8 | 8th grade (middle school) |
| 10 | 10th grade (high school) |
| 12 | 12th grade (senior year) |
| 14 | College sophomore |
| 16 | College senior |
| 17+ | Graduate level |

Gunning recommended that most business writing target a Fog Index of 12 or below. Major newspapers typically score between 10 and 12. Academic journals often score 16 or higher.

---

## Implementation

### Core Algorithm

The pystylometry implementation uses native chunked analysis with dual-mode complex word detection:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `chunk_size` | 1000 | Number of words per chunk for distribution analysis |
| `spacy_model` | `"en_core_web_sm"` | spaCy model for enhanced mode |

For each chunk:
1. Split text into sentences
2. Tokenize and normalize to word tokens
3. Detect complex words using the best available method (enhanced or basic)
4. Compute average words per sentence and complex word percentage
5. Apply the Fog formula with coefficient 0.4
6. Compute grade level (rounded, clamped to 0-20 range)

### Key Features

**Dual-Mode Complex Word Detection:**

The implementation provides two modes for complex word detection, selected automatically based on available dependencies:

**Enhanced Mode** (when spaCy is available):
- Uses Part-of-Speech (POS) tagging for proper noun detection (`PROPN` tag)
- Uses lemmatization for morphological analysis (e.g., "companies" lemmatizes to "company", still 3 syllables, so still complex; "running" lemmatizes to "run", 1 syllable, so not complex)
- Processes the full text with spaCy to preserve linguistic context
- Handles edge cases: acronyms (NASA), mixed case (iPhone), irregular verbs

**Basic Mode** (fallback when spaCy is unavailable):
- Uses capitalization heuristic for proper noun detection (title case mid-sentence = proper noun, all-caps = acronym)
- Uses suffix stripping for inflection detection (strips -es, -ed, -ing endings)
- Less accurate but requires no external dependencies

The mode used is reported in the result metadata (`mode: "enhanced"` or `mode: "basic"`).

**Hyphenated Word Handling**: Following Gunning's specification ("Do not count compound words"), all hyphenated words are excluded from the complex word count regardless of component syllable counts.

**Sentence Start Tracking**: In basic mode, the implementation tracks sentence-initial words to avoid falsely excluding capitalized words at the beginning of sentences.

**Result Dataclass**: Returns a `GunningFogResult` with:
- `fog_index`: Mean Fog Index across chunks
- `grade_level`: Mean grade level across chunks
- `fog_index_dist`: Full distribution of per-chunk Fog Index values
- `grade_level_dist`: Full distribution of per-chunk grade levels
- `chunk_size` and `chunk_count`: Analysis parameters
- `metadata`: Complex word counts, percentages, detection mode, and reliability flag

---

## Usage

### API Examples

```python
from pystylometry.readability import compute_gunning_fog

# Basic usage (automatically selects enhanced mode if spaCy available)
result = compute_gunning_fog(
    "The implementation of extraordinary administrative procedures "
    "requires sophisticated understanding of bureaucratic mechanisms."
)
print(f"Fog Index: {result.fog_index:.1f}")
print(f"Grade Level: {result.grade_level:.0f}")
print(f"Detection Mode: {result.metadata['mode']}")

# Chunked analysis for stylometric fingerprinting
result = compute_gunning_fog(long_text, chunk_size=1000)
print(f"Mean Fog: {result.fog_index:.1f}")
print(f"Std Dev: {result.fog_index_dist.std:.2f}")
print(f"Chunks analyzed: {result.chunk_count}")

# Specify a different spaCy model for better accuracy
result = compute_gunning_fog(long_text, spacy_model="en_core_web_lg")

# Access complex word statistics
print(f"Complex words: {result.metadata['complex_word_count']}")
print(f"Complex word %: {result.metadata['complex_word_percentage']:.1f}%")
print(f"Avg sentence length: {result.metadata['average_words_per_sentence']:.1f}")

# Check detection method details
print(f"Proper noun detection: {result.metadata['proper_noun_detection']}")
print(f"Inflection handling: {result.metadata['inflection_handling']}")
```

---

## Limitations

### Complex Word Definition Subjectivity

Gunning's original definition of "complex" was pragmatic rather than linguistic. Words with 3+ syllables are not always difficult (e.g., "beautiful", "together", "important"), and some 2-syllable words can be obscure (e.g., "segue", "niche"). The syllable threshold is a proxy for vocabulary sophistication, not a direct measure.

### Enhanced Mode Dependency

The enhanced mode requires spaCy and a downloaded language model (`en_core_web_sm` at minimum). Without spaCy, the basic mode uses heuristics that can fail on:
- Acronyms treated as proper nouns (e.g., "NASA" excluded when it should not be)
- Sentence-initial words incorrectly classified
- Irregular verb forms not handled by simple suffix stripping

### Hyphenated Word Exclusion

Following Gunning's original specification, all hyphenated words are excluded from the complex word count. This blanket exclusion means that genuinely difficult hyphenated words (e.g., "re-establishment", "self-actualization") are never counted as complex.

### Sentence Length Dominance

The Fog Index weighs sentence length and complex word percentage equally within the formula. For text with very long sentences but simple vocabulary, the Fog Index can produce high scores that overestimate difficulty.

### English-Specific

The formula's complex word detection, syllable counting, and grade-level calibration are all designed for English. The concept of "complex words" based on syllable count does not transfer to languages with different morphological systems.

---

## References

Gunning, R. (1952). *The Technique of Clear Writing*. McGraw-Hill, New York.

Gunning, R. (1968). *The Technique of Clear Writing* (Revised Edition). McGraw-Hill, New York.

DuBay, W. H. (2004). The principles of readability. *Impact Information*, 1-76.

Kincaid, J. P., Fishburne, R. P., Rogers, R. L., & Chissom, B. S. (1975). Derivation of new readability formulas for Navy enlisted personnel. *Naval Technical Training Command Research Branch Report* 8-75.
