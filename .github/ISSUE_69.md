# Issue #69: Replace Custom Regex Sentence Segmentation with fast-sentence-segment

## Problem

The current `split_sentences()` implementation in `_utils.py` uses a custom regex-based approach with manual abbreviation handling (lines 111-177). This implementation has proven unreliable, causing:

1. **Mid-sentence splits**: Text gets truncated mid-word ("pla", "mu", "dea")
2. **Fragment detection**: Single characters treated as sentences ("I|")
3. **Inconsistent segmentation**: Sentences split at incorrect boundaries
4. **Maintenance burden**: ~70 lines of custom regex that duplicates work done by specialized libraries

**Example of incorrect segmentation:**
```
Row 243: "I|"
Row 244: "began to detect an ally."
```
These should be one sentence: "I began to detect an ally."

## Current Implementation Issues

The custom regex approach in `_utils.py`:
```python
def split_sentences(text: str) -> list[str]:
    """Split text into sentences with improved boundary detection."""
    # Lines 111-177: Custom regex with abbreviation handling
    # - Manually maintains list of 30+ abbreviations
    # - Complex regex patterns prone to edge cases
    # - Not battle-tested like dedicated libraries
```

**Files affected by sentence segmentation:**
- `pystylometry/_utils.py` - Core implementation
- `pystylometry/prosody/sentence_syllable_patterns.py` - Prosody analysis
- `pystylometry/prosody/rhythm_prosody.py` - Rhythm analysis
- `pystylometry/readability/*.py` - Multiple readability formulas
- `pystylometry/cli.py` - CLI interface
- `pystylometry/syntactic/*.py` - Syntactic analysis (uses spaCy `.sents`)

## Proposed Solution

Replace custom regex with **fast-sentence-segment**, a battle-tested sentence segmentation library:

```python
from fast_sentence_segment import segment

def split_sentences(text: str) -> list[str]:
    """Split text into sentences using fast-sentence-segment.

    Uses the fast-sentence-segment library for accurate, reliable
    sentence boundary detection. Handles abbreviations, edge cases,
    and complex punctuation patterns automatically.

    Related GitHub Issue:
        #69 - Replace custom regex with fast-sentence-segment
        https://github.com/craigtrim/pystylometry/issues/69
        #68 - Replace spaCy with built-in utilities
        https://github.com/craigtrim/pystylometry/issues/68

    Args:
        text: Input text to split

    Returns:
        List of sentences

    Example:
        >>> sentences = split_sentences("Dr. Smith arrived. He was happy.")
        >>> print(sentences)
        ['Dr. Smith arrived.', 'He was happy.']
    """
    if not text or not text.strip():
        return []

    return segment(text)
```

## Benefits

### 1. **Accuracy**
- Battle-tested library used in production systems
- Handles edge cases: abbreviations, ellipses, quoted speech, etc.
- Consistent, predictable behavior

### 2. **Simplicity**
- Replace ~70 lines of custom regex with 3 lines
- No manual abbreviation list maintenance
- Single dependency handles all edge cases

### 3. **Maintainability**
- Library updates handled by package maintainer
- Bug fixes benefit from community testing
- Reduces pystylometry maintenance burden

### 4. **Performance**
- Optimized C implementation available
- Faster than regex for large texts
- No regex compilation overhead

### 5. **Consistency with Issue #68**
- Issue #68 removed spaCy to eliminate size/complexity
- This issue completes the transition to lightweight utilities
- Maintains "no heavy dependencies" philosophy

## Implementation Plan

### 1. Add Dependency
```toml
[tool.poetry.dependencies]
python = "^3.9"
rich = "^13.0"
fast-sentence-segment = "^0.1.0"  # Add this
```

**Size impact:** ~50 KB (tiny compared to spaCy's 500 MB)

### 2. Replace split_sentences() Implementation

File: `pystylometry/_utils.py` (lines 111-177)

**Before (70+ lines):**
```python
def split_sentences(text: str) -> list[str]:
    # Complex regex with abbreviation handling
    # Manual pattern matching
    # Edge case logic
    # Fallback handling
```

**After (10 lines):**
```python
from fast_sentence_segment import segment

def split_sentences(text: str) -> list[str]:
    """Split text into sentences using fast-sentence-segment."""
    if not text or not text.strip():
        return []
    return segment(text)
```

### 3. Verify All Usages

**Core modules using `split_sentences()`:**
- ✅ `pystylometry/_utils.py` - Source implementation
- ✅ `pystylometry/prosody/sentence_syllable_patterns.py` - Prosody analysis
- ✅ `pystylometry/prosody/rhythm_prosody.py` - Rhythm metrics
- ✅ `pystylometry/readability/additional_formulas.py` - Readability
- ✅ `pystylometry/readability/coleman_liau.py` - Coleman-Liau
- ✅ `pystylometry/readability/gunning_fog.py` - Gunning Fog
- ✅ `pystylometry/readability/ari.py` - ARI
- ✅ `pystylometry/readability/smog.py` - SMOG
- ✅ `pystylometry/readability/flesch.py` - Flesch
- ✅ `pystylometry/readability/complex_words.py` - Complex words
- ✅ `pystylometry/cli.py` - CLI interface

**Syntactic module (optional - uses spaCy `.sents`):**
- `pystylometry/syntactic/advanced_syntactic.py`
- `pystylometry/syntactic/sentence_types.py`
- `pystylometry/syntactic/sentence_stats.py`

Note: Syntactic module requires spaCy, so it can continue using spaCy's `.sents` for now.

### 4. Test Coverage

**Existing tests to verify:**
- `tests/common/test_utils.py` - Core split_sentences() tests
- `tests/readability/test_smog.py` - SMOG formula
- `tests/readability/test_flesch.py` - Flesch formula
- `tests/prosody/test_sentence_syllable_patterns.py` - 31 tests
- `tests/test_mega_syllable_patterns_integration.py` - 3 integration tests

**New tests to add:**
- Edge cases: abbreviations, ellipses, quoted speech
- Long texts (verify no truncation)
- Special characters and punctuation patterns
- Comparison with old implementation on sample texts

## Verification Checklist

- [ ] Add `fast-sentence-segment` to `pyproject.toml`
- [ ] Run `poetry lock` to update lock file
- [ ] Replace `split_sentences()` in `_utils.py`
- [ ] Remove old abbreviation list and regex logic
- [ ] Update docstring with issue link and library reference
- [ ] Run full test suite: `pytest tests/`
- [ ] Verify prosody CLI works on large texts (e.g., full book)
- [ ] Check output quality: compare old vs new sentence splits
- [ ] Update DEPENDENCIES.md to mention fast-sentence-segment
- [ ] Update Issue #68 reference to note completion with Issue #69

## Related Issues

- **#68** - Replace spaCy with built-in utilities (this completes the transition)
- **#66** - Sentence-level syllable analysis (depends on sentence segmentation)
- **#67** - Syllable pattern repetition analysis (depends on #66)

## Academic Validity

**This change maintains academic rigor:**

Sentence segmentation is an **implementation detail**, not a theoretical requirement for stylometric analysis. As long as sentences are split consistently and accurately, the metrics remain valid.

The choice of segmentation library (regex vs fast-sentence-segment vs spaCy) does not affect:
- Syllable counting accuracy
- Prosody pattern detection
- Readability formula calculations
- Statistical analysis validity

Research on prosodic features and readability metrics focuses on the **patterns within sentences**, not the specific tokenization method used to identify sentence boundaries.

## Breaking Changes

**None.** This is a drop-in replacement:
- Same function signature: `split_sentences(text: str) -> list[str]`
- Same behavior: returns list of sentence strings
- Better accuracy: fewer edge case failures
- No API changes required

## Timeline

1. **Immediate:** Add dependency and replace implementation
2. **Testing:** Run full test suite (should pass with better accuracy)
3. **Validation:** Manual testing on large texts from prosody CLI
4. **Documentation:** Update DEPENDENCIES.md and issue references

---

**Related GitHub Issue:**
- [Issue #68](https://github.com/craigtrim/pystylometry/issues/68) - Replace spaCy with built-in utilities
- [Issue #66](https://github.com/craigtrim/pystylometry/issues/66) - Sentence-level syllable analysis
- [Issue #67](https://github.com/craigtrim/pystylometry/issues/67) - Syllable pattern repetition analysis
