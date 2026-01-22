"""Coleman-Liau Index."""

import math

from .._types import ColemanLiauResult
from .._utils import split_sentences, tokenize

# Regression coefficients from Coleman & Liau (1975)
# Derived from empirical analysis of Cloze test results on graded texts
# Reference: Coleman, M., & Liau, T. L. (1975). A computer readability formula
#            designed for machine scoring. Journal of Applied Psychology, 60(2), 283.

# Coefficient for letters per 100 words
# Represents impact of word length on reading difficulty
_LETTER_COEFFICIENT = 0.0588

# Coefficient for sentences per 100 words (negative: more sentences = easier)
# Represents impact of sentence length on reading difficulty
_SENTENCE_COEFFICIENT = -0.296

# Intercept to calibrate scale to U.S. grade levels (1-16)
_INTERCEPT = -15.8


def compute_coleman_liau(text: str) -> ColemanLiauResult:
    """
    Compute Coleman-Liau Index.

    Formula:
        CLI = 0.0588 × L - 0.296 × S - 15.8

    Where:
        L = average number of letters per 100 words
        S = average number of sentences per 100 words

    The Coleman-Liau index relies on characters rather than syllables,
    making it easier to compute and not requiring syllable-counting algorithms.

    **Implementation Notes:**
    - Grade levels are clamped to [0, 20] range (upper bound is design choice,
      not empirically derived from Coleman & Liau 1975)
    - Uses round-half-up rounding (not banker's rounding) for grade level calculation
    - Letter counts (Unicode alphabetic characters only) from raw text while word
      counts from tokenized text may diverge in edge cases (e.g., special tokens,
      URLs, email addresses)
    - Reliability heuristic based on validation study passage lengths (~100 words);
      shorter texts flagged in metadata
    - English-centric sentence splitting and Unicode assumptions limit true
      cross-language applicability

    References:
        Coleman, M., & Liau, T. L. (1975). A computer readability formula
        designed for machine scoring. Journal of Applied Psychology, 60(2), 283.

    Args:
        text: Input text to analyze

    Returns:
        ColemanLiauResult with CLI index and grade level

    Example:
        >>> result = compute_coleman_liau("The quick brown fox jumps over the lazy dog.")
        >>> print(f"CLI Index: {result.cli_index:.1f}")
        CLI Index: 1.8
        >>> print(f"Grade Level: {result.grade_level}")
        Grade Level: 2
        >>> result.metadata["reliable"]
        False
    """
    sentences = split_sentences(text)
    tokens = tokenize(text)

    # Count Unicode alphabetic characters only (excludes digits, spaces, punctuation, symbols)
    # Computed before early return to ensure metadata consistency
    letter_count = sum(1 for char in text if char.isalpha())

    if len(sentences) == 0 or len(tokens) == 0:
        return ColemanLiauResult(
            cli_index=0.0,
            grade_level=0,
            metadata={
                "sentence_count": len(sentences),
                "word_count": len(tokens),
                "letter_count": letter_count,
                "letters_per_100_words": 0.0,
                "sentences_per_100_words": 0.0,
                "reliable": False,
            },
        )

    # Calculate per 100 words
    L = (letter_count / len(tokens)) * 100  # noqa: N806
    S = (len(sentences) / len(tokens)) * 100  # noqa: N806

    # Compute Coleman-Liau Index using empirically-derived coefficients
    cli_index = _LETTER_COEFFICIENT * L + _SENTENCE_COEFFICIENT * S + _INTERCEPT

    # Use round-half-up rounding (not banker's rounding) and clamp to valid grade range [0, 20]
    # Round half up: 4.5 → 5 (not Python's default round-half-to-even)
    # math.floor(x + 0.5) implements round-half-up for both positive and negative values
    # Lower bound: Prevent negative grades for very simple texts
    # Upper bound: Cap at grade 20 (post-graduate) for extreme complexity
    grade_level = max(0, min(20, math.floor(cli_index + 0.5)))

    # Reliability heuristic: validation study used ~100-word passages
    # Not a hard minimum, but shorter texts may deviate from expected behavior
    reliable = len(tokens) >= 100

    return ColemanLiauResult(
        cli_index=cli_index,
        grade_level=grade_level,
        metadata={
            "sentence_count": len(sentences),
            "word_count": len(tokens),
            "letter_count": letter_count,
            "letters_per_100_words": L,
            "sentences_per_100_words": S,
            "reliable": reliable,
        },
    )
