"""Automated Readability Index (ARI)."""

import math

from .._types import ARIResult
from .._utils import split_sentences, tokenize

# Formula coefficients from Senter & Smith (1967)
# Reference: Senter, R. J., & Smith, E. A. (1967). Automated readability index.
#            AMRL-TR-6620. Aerospace Medical Research Laboratories.

# Coefficient for characters per word
_CHARACTER_COEFFICIENT = 4.71

# Coefficient for words per sentence
_WORD_COEFFICIENT = 0.5

# Intercept to calibrate scale to U.S. grade levels
_INTERCEPT = -21.43


def _get_age_range(grade_level: int) -> str:
    """
    Map grade level to age range.

    Args:
        grade_level: U.S. grade level (0-20+)

    Returns:
        Age range string
    """
    if grade_level <= 0:
        return "5-6 years (Kindergarten)"
    elif grade_level <= 5:
        return "6-11 years (Elementary)"
    elif grade_level <= 8:
        return "11-14 years (Middle School)"
    elif grade_level <= 12:
        return "14-18 years (High School)"
    elif grade_level <= 14:
        return "18-22 years (College)"
    else:
        return "22+ years (Graduate)"


def compute_ari(text: str) -> ARIResult:
    """
    Compute Automated Readability Index (ARI).

    Formula:
        ARI = 4.71 × (characters/words) + 0.5 × (words/sentences) - 21.43

    The ARI uses character counts and word counts (similar to Coleman-Liau)
    but adds sentence length as a factor. It produces an approximate
    representation of the US grade level needed to comprehend the text.

    **Implementation Notes:**
    - Grade levels are clamped to [0, 20] range
    - Uses round-half-up rounding for grade level calculation
    - Character count includes alphanumeric characters only (letters and digits)
    - Reliability heuristic: 100+ words recommended

    Grade Level to Age mapping:
        1-5:   6-11 years (Elementary)
        6-8:   11-14 years (Middle School)
        9-12:  14-18 years (High School)
        13-14: 18-22 years (College)
        15+:   22+ years (Graduate)

    References:
        Senter, R. J., & Smith, E. A. (1967). Automated readability index.
        AMRL-TR-6620. Aerospace Medical Research Laboratories.

    Args:
        text: Input text to analyze

    Returns:
        ARIResult with ARI score, grade level, and age range

    Example:
        >>> result = compute_ari("The quick brown fox jumps over the lazy dog.")
        >>> print(f"ARI Score: {result.ari_score:.1f}")
        ARI Score: 0.1
        >>> print(f"Grade Level: {result.grade_level}")
        Grade Level: 0
        >>> print(f"Age Range: {result.age_range}")
        Age Range: 5-6 years (Kindergarten)
        >>> result.metadata["reliable"]
        False
    """
    sentences = split_sentences(text)
    tokens = tokenize(text)

    # Count characters (alphanumeric: letters and digits, excluding spaces/punctuation)
    # Computed before early return to ensure metadata consistency
    character_count = sum(1 for char in text if char.isalnum())

    if len(sentences) == 0 or len(tokens) == 0:
        return ARIResult(
            ari_score=0.0,
            grade_level=0,
            age_range="5-6 years (Kindergarten)",
            metadata={
                "sentence_count": len(sentences),
                "word_count": len(tokens),
                "character_count": character_count,
                "characters_per_word": 0.0,
                "words_per_sentence": 0.0,
                "reliable": False,
            },
        )

    # Calculate ratios
    chars_per_word = character_count / len(tokens)
    words_per_sentence = len(tokens) / len(sentences)

    # Apply ARI formula
    ari_score = (
        _CHARACTER_COEFFICIENT * chars_per_word
        + _WORD_COEFFICIENT * words_per_sentence
        + _INTERCEPT
    )

    # Use round-half-up rounding and clamp to valid grade range [0, 20]
    # math.floor(x + 0.5) implements round-half-up for both positive and negative values
    grade_level = max(0, min(20, math.floor(ari_score + 0.5)))

    # Get age range from grade level
    age_range = _get_age_range(grade_level)

    # Reliability heuristic: like other readability metrics, 100+ words recommended
    reliable = len(tokens) >= 100

    return ARIResult(
        ari_score=ari_score,
        grade_level=grade_level,
        age_range=age_range,
        metadata={
            "sentence_count": len(sentences),
            "word_count": len(tokens),
            "character_count": character_count,
            "characters_per_word": chars_per_word,
            "words_per_sentence": words_per_sentence,
            "reliable": reliable,
        },
    )
