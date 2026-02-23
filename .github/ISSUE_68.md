# Issue #68: Replace spaCy with Built-in Utilities for Sentence Syllable Analysis

## Problem

The sentence syllable pattern analysis (Issue #66, #67) currently depends on spaCy for sentence segmentation, which imposes a **1M character hard limit** on text size. This prevents analysis of longer texts and creates unnecessary complexity:

```
Text too large for spaCy (2,167,027 chars > 1,000,000 limit)
```

## Current spaCy Usage Analysis

### What spaCy Actually Does

In `sentence_syllable_patterns.py`, spaCy is used for exactly two operations:

1. **Sentence Segmentation** (lines 221-223):
```python
doc = nlp(text)
sentences = list(doc.sents)
```

2. **Tokenization** (line 244):
```python
words = [token.text for token in sent if token.is_alpha]
```

### Dependencies Created

- Requires spaCy installation
- Requires downloading en_core_web_sm model (~12 MB)
- Requires auto-download logic (Issue #67)
- Imposes 1M character limit on input text
- Slower processing (model loading overhead)

## Proposed Solution

### Replace with Built-in Utilities

pystylometry already has fast, reliable utilities in `_utils.py` that handle both operations:

#### 1. Sentence Segmentation → `split_sentences()`

```python
def split_sentences(text: str) -> list[str]:
    """Split text into sentences with improved boundary detection.

    Handles common abbreviations and edge cases better than simple
    splitting on sentence-ending punctuation. Uses a two-pass approach:
    1. Protect known abbreviations from splitting
    2. Split on sentence boundaries
    3. Restore abbreviations
    """
```

**Features:**
- Handles abbreviations (Dr., Mr., U.S.A., etc.)
- No size limit
- Fast (pure regex, no model loading)
- Already tested and used throughout codebase

#### 2. Tokenization → `tokenize()`

```python
def tokenize(text: str) -> list[str]:
    """Tokenize text into words using pyphen-based tokenizer."""
```

**Features:**
- Fast word extraction
- No dependencies beyond what we already use
- Consistent with rest of toolkit

### Implementation Plan

Replace lines 193-244 in `sentence_syllable_patterns.py`:

**Before (spaCy):**
```python
# Load spaCy model (auto-download if missing)
try:
    nlp = spacy.load(model)
except OSError:
    # Auto-download logic...

# Segment text into sentences
doc = nlp(text)
sentences = list(doc.sents)

# Extract words
for idx, sent in enumerate(sentences):
    words = [token.text for token in sent if token.is_alpha]
```

**After (built-in utilities):**
```python
from .._utils import split_sentences, tokenize

# Segment text into sentences
sentences = split_sentences(text)

# Extract words
for idx, sent_text in enumerate(sentences):
    words = [w for w in tokenize(sent_text) if w.isalpha()]
```

## Benefits

### 1. **No Size Limit**
- Works on texts of any length
- No 1M character restriction
- No chunking or workarounds needed

### 2. **Simpler Dependencies**
- Remove spaCy requirement for this analysis
- No model download needed
- Faster installation

### 3. **Better Performance**
- No model loading overhead
- Pure regex/string operations
- Faster processing for large texts

### 4. **Consistency**
- Uses same utilities as rest of toolkit
- Sentence splitting matches other modules
- Predictable behavior

### 5. **Maintainability**
- Remove auto-download logic
- Simpler error handling
- Fewer moving parts

## Verification Needed

**Before implementing, verify:**

1. ✅ **Sentence segmentation**: Does `split_sentences()` produce equivalent results to spaCy's sentence boundary detection?
   - Test on edge cases: abbreviations, ellipses, quoted speech
   - Compare output quality on sample texts

2. ✅ **Tokenization**: Does `tokenize()` + `.isalpha()` filter match spaCy's `token.is_alpha`?
   - Test on punctuation, contractions, hyphenated words
   - Verify syllable counting still works correctly

3. ✅ **Test suite**: Do all existing tests pass with the replacement?
   - Run `tests/prosody/test_sentence_syllable_patterns.py` (31 tests)
   - Run `tests/test_mega_syllable_patterns_integration.py` (3 tests)

4. ✅ **Accuracy**: Does pattern repetition analysis produce similar results?
   - Compare metrics on sample texts (old vs new)
   - Verify academic validity is maintained

## Related Issues

- #66 - Sentence-level syllable analysis (original implementation)
- #67 - Syllable pattern repetition analysis (depends on #66)
- Addresses user feedback: "Text too large for spaCy" error on 2.1M char texts

## Implementation Checklist

- [ ] Replace spaCy imports with `split_sentences` and `tokenize`
- [ ] Update sentence segmentation logic
- [ ] Update tokenization logic
- [ ] Remove spaCy auto-download code
- [ ] Remove `model` parameter from function signature
- [ ] Update docstrings to reflect no spaCy dependency
- [ ] Run full test suite
- [ ] Verify accuracy on sample texts
- [ ] Update mega.py to remove spaCy size limit check
- [ ] Update integration tests to remove spaCy skipif logic

## Academic Validity

**This change maintains academic rigor:**

The core analysis (syllable pattern repetition) depends on:
1. Identifying sentence boundaries
2. Counting syllables per word
3. Detecting repeated n-gram patterns

The sentence segmentation method (spaCy vs regex) is an **implementation detail**, not a theoretical requirement. As long as sentences are split consistently and accurately, the stylometric analysis remains valid.

Research on syllable pattern repetition (Gibbon, 2017; Lagutina & Lagutina, 2019; Breen & Clifton, 2012) focuses on the patterns themselves, not the specific sentence tokenization method.

## Next Steps

1. Carefully verify spaCy isn't used for anything else in `sentence_syllable_patterns.py`
2. Create test branch and implement replacement
3. Run comprehensive tests
4. Compare output quality on diverse text samples
5. If validation passes, merge and remove spaCy dependency from this module

---

**Related GitHub Issue:**
- [Issue #66](https://github.com/craigtrim/pystylometry/issues/66) - Sentence-level syllable analysis
- [Issue #67](https://github.com/craigtrim/pystylometry/issues/67) - Syllable pattern repetition analysis
