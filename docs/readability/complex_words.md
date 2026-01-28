# Complex Word Detection

## NLP-Enhanced Detection for Gunning Fog Index

Complex word detection is the critical component of the Gunning Fog Index that distinguishes it from other readability formulas. The pystylometry implementation provides a dual-mode detection system: an enhanced mode using spaCy for linguistically accurate analysis, and a basic heuristic mode as a fallback. This module is used internally by the Gunning Fog computation.

---

## Theoretical Background

### Origins

Robert Gunning defined "complex words" in his 1952 book *The Technique of Clear Writing* as words with three or more syllables, with specific exclusions for proper nouns, compound words, and common verb forms. This definition was designed to be practical for manual application by editors and writers.

The challenge of implementing Gunning's definition computationally was identified in pystylometry GitHub PR #4, which documented three specific issues with heuristic-based detection:

1. **Proper noun detection via capitalization is unreliable**: Fails on acronyms (NASA), mixed case (iPhone), all-caps text, and sentence-initial words.
2. **Suffix stripping for inflection handling is incomplete**: Only handles -es, -ed, -ing; misses irregular forms and other suffixes.
3. **Blanket exclusion of hyphenated words ignores complexity**: The original specification excludes all compound words, which is straightforward but may miss genuinely difficult hyphenated terms.

### Mathematical Foundation

The complex word classification is a binary decision function:

```
is_complex(word) = True if ALL of:
    1. syllables(word) >= 3
    2. word is NOT a proper noun
    3. word is NOT a hyphenated compound
    4. base_form(word) has >= 3 syllables (i.e., complexity is not due to inflection)
```

In enhanced mode, conditions 2 and 4 use linguistic analysis:
```
is_proper_noun = (POS_tag == "PROPN")
base_form = lemma(word)
```

In basic mode, conditions 2 and 4 use heuristics:
```
is_proper_noun = (word[0].isupper() AND NOT is_sentence_start) OR word.isupper()
base_form = strip_suffix(word, suffixes=["-ing", "-ed", "-es"])
```

### Interpretation

The complex word count feeds directly into the Gunning Fog formula. A higher complex word percentage increases the Fog Index, indicating more difficult text. The accuracy of complex word detection directly affects the reliability of the Fog Index.

---

## Implementation

### Core Algorithm

The module provides three main components:

**`is_complex_word(word, syllable_count, ...)`**: Determines if a single word is complex according to Gunning's criteria. Accepts optional spaCy annotations (POS tag, lemma) for enhanced mode.

**`process_text_for_complex_words(text, tokens, model)`**: Processes an entire text to count complex words, automatically selecting the best available detection mode.

**`_is_hyphenated_complex(word)`**: Handles the special case of hyphenated words. Per Gunning's specification ("Do not count compound words"), this always returns `False`, excluding all hyphenated words from the complex word count.

### Key Features

**Enhanced Mode (spaCy)**:

When spaCy is available and the specified model is installed, the module uses full NLP pipeline analysis:

1. Process the entire text with spaCy to preserve linguistic context
2. Build sentence start tracking from spaCy's sentence segmentation
3. Identify hyphenated words from the pre-tokenized word list
4. For each spaCy token:
   - Skip non-alphabetic tokens (punctuation, numbers)
   - Skip tokens that are components of hyphenated words
   - Check if `POS_ == "PROPN"` to exclude proper nouns
   - Check if `lemma_` has fewer than 3 syllables to exclude inflected forms
   - Count as complex if all criteria are met

The enhanced mode correctly handles cases that defeat heuristics:
- "NASA" (all-caps): spaCy identifies as PROPN, excluded
- "iPhone" (mixed case): spaCy identifies as PROPN, excluded
- "companies" (3 syllables): lemma "company" has 3 syllables, still complex
- "running" (2 syllables): already below threshold, not complex
- "created" (3 syllables): lemma "create" has 2 syllables, not complex

**Basic Mode (Heuristics)**:

When spaCy is unavailable, the module falls back to heuristics:

1. Build sentence-start word set from sentence segmentation
2. For each token:
   - Skip non-alphabetic tokens (except hyphenated words)
   - Check capitalization for proper noun heuristic (all-caps = acronym, title-case mid-sentence = proper noun)
   - Strip common inflections (-ing, -ed, -es) and check if stripped form has fewer than 3 syllables
   - Count as complex if all criteria are met

**Automatic Mode Selection**: The `process_text_for_complex_words` function automatically detects whether spaCy is installed and whether the requested model is downloaded. If spaCy import fails or model loading raises `OSError`, it falls back to basic mode with a warning log message.

**Metadata Reporting**: Both modes return metadata describing the detection method used:
- `mode`: "enhanced" or "basic"
- `proper_noun_detection`: "POS-based" or "Capitalization-based"
- `inflection_handling`: "Lemmatization-based" or "Suffix-stripping"
- `spacy_model`: Model name (enhanced mode only)

---

## Usage

### API Examples

The complex word module is used internally by `compute_gunning_fog`. Direct usage is possible but typically not necessary:

```python
from pystylometry.readability.complex_words import (
    is_complex_word,
    process_text_for_complex_words,
)
from pystylometry.readability.syllables import count_syllables

# Direct complex word check (basic mode)
word = "beautiful"
syllables = count_syllables(word)
result = is_complex_word(word, syllables, use_spacy=False)
print(f"'{word}' ({syllables} syllables): complex = {result}")
# "beautiful" (3 syllables): complex = True

# Direct complex word check (enhanced mode with spaCy annotations)
result = is_complex_word(
    "California", 4, use_spacy=True, pos="PROPN", lemma="California"
)
print(f"California: complex = {result}")  # False (proper noun)

result = is_complex_word(
    "companies", 3, use_spacy=True, pos="NOUN", lemma="company"
)
print(f"companies: complex = {result}")  # True (lemma still 3 syllables)

# Process full text
text = "The beautiful California sunset was absolutely extraordinary."
tokens = ["The", "beautiful", "California", "sunset", "was", "absolutely", "extraordinary"]
count, metadata = process_text_for_complex_words(text, tokens)
print(f"Complex words: {count}")
print(f"Mode: {metadata['mode']}")
print(f"Detection: {metadata['proper_noun_detection']}")
```

### spaCy Model Installation

For enhanced mode, install spaCy and download a model:

```bash
pip install spacy
python -m spacy download en_core_web_sm   # Small model (default)
python -m spacy download en_core_web_md   # Medium model (better accuracy)
python -m spacy download en_core_web_lg   # Large model (best accuracy)
```

The model is specified via the `spacy_model` parameter in `compute_gunning_fog` or `process_text_for_complex_words`.

---

## Limitations

### Enhanced Mode Requirements

The enhanced mode requires spaCy and a downloaded language model, which adds significant dependency size (the small model is approximately 12 MB, the large model is approximately 560 MB). Without these, the basic mode is used automatically.

### spaCy Tokenization Mismatch

spaCy's tokenizer splits hyphenated words differently than pystylometry's tokenizer. For example, spaCy splits "well-known" into ["well", "-", "known"] while pystylometry keeps it as a single token. The implementation handles this by building a set of hyphenated words and skipping their components during spaCy token analysis.

### Basic Mode Heuristic Failures

The capitalization heuristic for proper nouns fails on:
- Words at the start of a sentence (may be falsely excluded)
- Intentionally capitalized words for emphasis
- All-caps words that are not acronyms
- Mixed-case words that are not proper nouns

The suffix stripping heuristic fails on:
- Irregular verb forms ("spoke" from "speak")
- Words where the suffix is part of the root ("bed" is not "b" + "-ed")
- Non-standard inflections

### Lemmatization Scope

spaCy's lemmatizer handles inflectional morphology (grammatical variations) but not derivational morphology (word formation). The suffix -ly is derivational, so "beautifully" lemmatizes to "beautifully" (not "beautiful"), preserving its 5-syllable count. This matches Gunning's original specification, which mentioned only -ed, -es, and -ing.

### Hyphenated Word Blanket Exclusion

Following Gunning's specification exactly, all hyphenated words are excluded from the complex word count. This means words like "re-establishment" (5 syllables) and "self-actualization" (7 syllables) are never counted as complex, even though they may contribute to text difficulty.

---

## References

Gunning, R. (1952). *The Technique of Clear Writing*. McGraw-Hill, New York. Pages 38-39.

Honnibal, M., & Montani, I. (2017). spaCy 2: Natural language understanding with Bloom embeddings, convolutional neural networks and incremental parsing. *To appear*.

pystylometry GitHub PR #4: NLP-enhanced complex word detection. https://github.com/craigtrim/pystylometry/pull/4
