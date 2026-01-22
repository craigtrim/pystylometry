"""Gunning Fog Index."""

import math
import re

from .._types import GunningFogResult
from .._utils import split_sentences, tokenize
from .syllables import count_syllables

# Formula coefficient from Gunning (1952)
# Reference: Gunning, R. (1952). The Technique of Clear Writing. McGraw-Hill.
_FOG_COEFFICIENT = 0.4

# Complex word threshold (syllable count)
_COMPLEX_SYLLABLE_THRESHOLD = 3


def _is_complex_word(word: str, is_sentence_start: bool = False) -> bool:
    """
    Determine if a word is complex according to Gunning Fog criteria.

    Complex words have 3+ syllables, but exclude:
    - Proper nouns (capitalized words mid-sentence, though imperfect heuristic)
    - Compound words (hyphenated)
    - Words ending in common inflections (-es, -ed, -ing) that add syllables

    Args:
        word: Word to evaluate
        is_sentence_start: Whether word appears at start of sentence

    Returns:
        True if word is considered complex
    """
    # Skip hyphenated compound words
    if "-" in word:
        return False

    # Skip likely proper nouns (capitalized mid-sentence words)
    # Sentence-initial words are allowed even if capitalized
    # Note: This heuristic is imperfect but follows Gunning's approach
    if word and word[0].isupper() and not is_sentence_start:
        return False

    syllable_count = count_syllables(word)

    # Not complex if below threshold
    if syllable_count < _COMPLEX_SYLLABLE_THRESHOLD:
        return False

    # Check for common inflectional suffixes that might inflate syllable count
    # If word ends in -es, -ed, or -ing, check if base word would still be complex
    if re.search(r"(es|ed|ing)$", word.lower()):
        # Approximately adjust syllable count for suffix
        # This is a simplification of Gunning's original approach
        adjusted_count = syllable_count - 1
        return adjusted_count >= _COMPLEX_SYLLABLE_THRESHOLD

    return True


def compute_gunning_fog(text: str) -> GunningFogResult:
    """
    Compute Gunning Fog Index.

    Formula:
        Fog Index = 0.4 × [(words/sentences) + 100 × (complex words/words)]

    Where complex words are defined as words with 3+ syllables,
    excluding proper nouns (capitalized), hyphenated compounds, and
    common inflectional suffixes (-es, -ed, -ing).

    The index estimates years of formal education needed to understand the text
    on first reading.

    **Implementation Notes:**
    - Grade levels are clamped to [0, 20] range
    - Uses round-half-up rounding for grade level calculation
    - Proper noun detection uses capitalization heuristic (imperfect)
    - Suffix handling (-es, -ed, -ing) is simplified approximation
    - Reliability heuristic: 100+ words and 3+ sentences recommended

    References:
        Gunning, R. (1952). The Technique of Clear Writing. McGraw-Hill.

    Args:
        text: Input text to analyze

    Returns:
        GunningFogResult with fog index and grade level

        Note: For empty input (no sentences or words), fog_index and grade_level
        will be float('nan'). This prevents conflating "no data" with actual scores
        (0.0 is a valid fog index for extremely simple text).

    Example:
        >>> result = compute_gunning_fog("The quick brown fox jumps over the lazy dog.")
        >>> print(f"Fog Index: {result.fog_index:.1f}")
        Fog Index: 4.0
        >>> print(f"Grade Level: {result.grade_level}")
        Grade Level: 4
        >>> result.metadata["reliable"]
        False

        >>> # Empty input returns NaN
        >>> import math
        >>> result_empty = compute_gunning_fog("")
        >>> math.isnan(result_empty.fog_index)
        True
    """
    sentences = split_sentences(text)
    tokens = tokenize(text)

    if len(sentences) == 0 or len(tokens) == 0:
        return GunningFogResult(
            fog_index=float("nan"),
            grade_level=float("nan"),
            metadata={
                "sentence_count": len(sentences),
                "word_count": len(tokens),
                "complex_word_count": 0,
                "complex_word_percentage": 0.0,
                "average_words_per_sentence": 0.0,
                "reliable": False,
            },
        )

    # Identify sentence-initial token positions
    # Build a set of indices that mark the start of each sentence
    sentence_start_indices = set()
    token_position = 0
    for sentence in sentences:
        sentence_tokens = tokenize(sentence)
        if sentence_tokens:
            sentence_start_indices.add(token_position)
            token_position += len(sentence_tokens)

    # Count complex words using Gunning's criteria
    complex_word_count = sum(
        1
        for i, word in enumerate(tokens)
        if _is_complex_word(word, is_sentence_start=(i in sentence_start_indices))
    )

    # Calculate average words per sentence
    avg_words_per_sentence = len(tokens) / len(sentences)

    # Calculate percentage of complex words
    complex_word_percentage = (complex_word_count / len(tokens)) * 100

    # Apply Gunning Fog formula
    fog_index = _FOG_COEFFICIENT * (avg_words_per_sentence + complex_word_percentage)

    # Round to nearest integer and clamp to valid grade range [0, 20]
    # math.floor(x + 0.5) implements round-half-up for positive values
    # Clamping ensures we stay within [0, 20] range regardless
    grade_level = max(0, min(20, math.floor(fog_index + 0.5)))

    # Reliability heuristic: Gunning recommends 100+ words and multiple sentences
    reliable = len(tokens) >= 100 and len(sentences) >= 3

    return GunningFogResult(
        fog_index=fog_index,
        grade_level=grade_level,
        metadata={
            "sentence_count": len(sentences),
            "word_count": len(tokens),
            "complex_word_count": complex_word_count,
            "complex_word_percentage": complex_word_percentage,
            "average_words_per_sentence": avg_words_per_sentence,
            "reliable": reliable,
        },
    )
