# Syllable Counting

## High-Accuracy Syllable Analysis Using CMU Pronouncing Dictionary

Syllable counting is a foundational operation for readability analysis. Multiple readability formulas (Flesch, SMOG, Gunning Fog, Linsear Write, Fry, Powers-Sumner-Kearl) depend on accurate syllable counts. The pystylometry implementation uses the CMU Pronouncing Dictionary for phonetic-based counting, with a vowel-group fallback for unknown words.

---

## Theoretical Background

### Origins

The CMU Pronouncing Dictionary is a machine-readable pronunciation dictionary maintained by the Speech Group at Carnegie Mellon University. It contains over 134,000 English words with their phonetic transcriptions using the ARPAbet phoneme set. Each vowel phoneme in the ARPAbet transcription carries a stress marker (0, 1, or 2), and the number of stress markers directly equals the number of syllables.

Syllable counting is deceptively difficult in English. Unlike languages with regular syllable patterns (e.g., Japanese), English has numerous exceptions, silent letters, and borrowed words that defeat simple rule-based counters. The CMU dictionary approach sidesteps these difficulties by looking up pre-determined phonetic transcriptions rather than applying rules.

### Mathematical Foundation

**CMU Dictionary Method:**

For a word found in the CMU dictionary:
```
syllables(word) = count of stress markers (0, 1, 2) in phonetic transcription
```

Example: "beautiful" transcribes to `B Y UW1 T AH0 F AH0 L`, which contains three stress markers (1, 0, 0), so `syllables("beautiful") = 3`.

**Fallback Vowel-Group Method:**

For words not in the CMU dictionary:
```
1. Count vowel groups (consecutive sequences of a, e, i, o, u, y)
2. If word ends in 'e' and count > 1, subtract 1 (silent-e adjustment)
3. Return max(1, count)
```

This heuristic handles most regular English words but fails on irregular patterns.

### Interpretation

Syllable counts are used as a proxy for word complexity in readability formulas. The underlying assumption is that words with more syllables tend to be:
- More abstract or specialized
- Less frequently used in everyday speech
- Acquired later in language development
- More cognitively demanding to process

While this correlation is imperfect, it holds well enough for statistical readability models.

---

## Implementation

### Core Algorithm

The `count_syllables` function follows this decision tree:

1. **Normalize**: Convert to lowercase, strip whitespace and punctuation
2. **Handle contractions**: Remove apostrophes (e.g., "can't" becomes "cant")
3. **Handle hyphens**: Split on hyphens and sum syllable counts of components recursively
4. **CMU lookup**: Query the pronouncing library for phonetic transcription
5. **Count stress markers**: If found, count stress markers in the first (most common) pronunciation
6. **Fallback**: If not found, use vowel-group counting with silent-e adjustment

The function uses `@lru_cache(maxsize=4096)` for performance, caching the 4096 most recently counted words.

### Key Features

**CMU Dictionary Accuracy**: The CMU dictionary provides correct syllable counts for over 134,000 English words, including irregular cases that rule-based systems fail on:
- "fire" = 2 syllables (not 1, despite ending in silent-e)
- "cruel" = 1 syllable (not 2, despite having two vowel groups)
- "choir" = 1 syllable (unusual vowel pattern)

**Contraction Handling**: Apostrophes are removed before lookup, so "can't" is looked up as "cant" and "I'll" as "ill". The CMU dictionary contains entries for contracted forms.

**Hyphenated Compound Handling**: Hyphenated words are split and each component is counted independently. This means "well-known" = count("well") + count("known") = 1 + 1 = 2. Recursive splitting handles multi-hyphen compounds like "mother-in-law".

**LRU Cache**: The `@lru_cache(maxsize=4096)` decorator memoizes syllable counts for recently queried words. This significantly improves performance when the same words appear repeatedly in a text, which is common in natural language.

**Additional Functions**:
- `count_syllables_text(text)`: Returns a list of `(word, syllable_count)` tuples for all words
- `total_syllables(text)`: Returns the total syllable count for the entire text
- `validate_accuracy(test_pairs)`: Tests accuracy against known word-syllable pairs

---

## Usage

### API Examples

```python
from pystylometry.readability.syllables import (
    count_syllables,
    count_syllables_text,
    total_syllables,
    validate_accuracy,
)

# Single word
print(count_syllables("beautiful"))   # 3
print(count_syllables("fire"))        # 2 (CMU: F AY1 ER0)
print(count_syllables("cruel"))       # 1 (CMU: K R UW1 L)
print(count_syllables("antidisestablishmentarianism"))  # 12

# Contractions
print(count_syllables("can't"))       # 1
print(count_syllables("I'm"))         # 1

# Hyphenated compounds
print(count_syllables("well-known"))  # 2 (1 + 1)
print(count_syllables("mother-in-law"))  # 4 (2 + 1 + 1)

# Full text analysis
pairs = count_syllables_text("The quick brown fox jumps over the lazy dog")
for word, count in pairs:
    print(f"{word}: {count}")

# Total syllables in text
total = total_syllables("The quick brown fox jumps over the lazy dog")
print(f"Total syllables: {total}")

# Validate accuracy against known pairs
test_pairs = [("hello", 2), ("world", 1), ("beautiful", 3), ("fire", 2)]
accuracy, failures = validate_accuracy(test_pairs)
print(f"Accuracy: {accuracy:.1f}%")
for word, expected, got in failures:
    print(f"  {word}: expected {expected}, got {got}")
```

### Installation

The `pronouncing` library is required for syllable counting. It is included in the readability extras:

```bash
pip install pystylometry[readability]
```

Or install directly:

```bash
pip install pronouncing
```

---

## Limitations

### Dictionary Coverage

The CMU Pronouncing Dictionary covers approximately 134,000 English words. Words not in the dictionary fall back to the less accurate vowel-group heuristic. Missing categories include:
- Rare or archaic words
- Technical jargon and neologisms
- Non-English words and loanwords
- Brand names and product names

### Fallback Accuracy

The vowel-group fallback heuristic makes systematic errors:
- Silent-e words beyond final position (e.g., "give" is 1 syllable but "live" as a verb is also 1)
- Consecutive vowel letters that form a single sound (e.g., "naivete" has vowel groups that do not correspond to syllable boundaries)
- Words ending in "-le" after a consonant (e.g., "table" = 2 syllables, but vowel counting may give 1)

### Multiple Pronunciations

Some English words have multiple valid pronunciations with different syllable counts (e.g., "caramel" can be 2 or 3 syllables). The implementation always uses the first pronunciation in the CMU dictionary, which is typically the most common but may not match regional pronunciation.

### Case and Punctuation Sensitivity

The implementation normalizes input by converting to lowercase and stripping common punctuation. However, unusual formatting or embedded punctuation may cause lookup failures, triggering the fallback heuristic.

### Cache Size

The LRU cache holds 4096 entries. For extremely large corpora with diverse vocabulary, cache eviction may reduce the performance benefit. In practice, 4096 entries cover the vast majority of repeated words in typical English text.

---

## References

CMU Pronouncing Dictionary. Speech Group, Carnegie Mellon University. http://www.speech.cs.cmu.edu/cgi-bin/cmudict

Bartlett, S., Kondrak, G., & Cherry, C. (2009). On the syllabification of phonemes. *Proceedings of Human Language Technologies: The 2009 Annual Conference of the North American Chapter of the Association for Computational Linguistics*, 308-316.

Marchand, Y., & Damper, R. I. (2000). A multistrategy approach to improving pronunciation by analogy. *Computational Linguistics*, 26(2), 195-219.
