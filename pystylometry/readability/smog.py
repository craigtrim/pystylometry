"""SMOG (Simple Measure of Gobbledygook) Index."""

import math

from .._types import SMOGResult
from .._utils import split_sentences, tokenize
from .syllables import count_syllables


def compute_smog(text: str) -> SMOGResult:
    """
    Compute SMOG (Simple Measure of Gobbledygook) Index.

    Formula:
        SMOG = 1.043 × √(polysyllables × 30/sentences) + 3.1291

    Where polysyllables are words with 3 or more syllables.

    The SMOG index estimates the years of education needed to understand the text.
    It's particularly useful for healthcare materials.

    References:
        McLaughlin, G. H. (1969). SMOG grading: A new readability formula.
        Journal of Reading, 12(8), 639-646.

    Args:
        text: Input text to analyze

    Returns:
        SMOGResult with SMOG index and grade level

        Note: For empty input (no sentences or words), smog_index and grade_level
        will be float('nan'). This prevents conflating "no data" with actual scores.

        SMOG is designed for texts with 30+ sentences. For shorter texts, the formula
        still computes but a warning is included in metadata. Results may be less reliable.

    Example:
        >>> result = compute_smog("Caffeinated programmers enthusiastically debugged incomprehensible spaghetti code.")
        >>> print(f"SMOG Index: {result.smog_index:.1f}")
        >>> print(f"Grade Level: {result.grade_level}")
    """
    sentences = split_sentences(text)
    tokens = tokenize(text)

    if len(sentences) == 0 or len(tokens) == 0:
        return SMOGResult(
            smog_index=float("nan"),
            grade_level=float("nan"),
            metadata={
                "sentence_count": 0,
                "word_count": 0,
                "polysyllable_count": 0,
                "warning": "Insufficient text",
            },
        )

    # Count polysyllables (words with 3+ syllables)
    polysyllable_count = sum(1 for word in tokens if count_syllables(word) >= 3)

    # SMOG formula: 1.043 × √(polysyllables × 30/sentences) + 3.1291
    smog_index = 1.043 * math.sqrt(polysyllable_count * 30 / len(sentences)) + 3.1291

    # Use round-half-up rounding (not banker's rounding) and clamp to valid grade range [0, 20]
    # Round half up: 4.5 → 5 (not Python's default round-half-to-even)
    # math.floor(x + 0.5) implements round-half-up for both positive and negative values
    # Lower bound: Prevent negative grades (though mathematically unlikely with SMOG's +3.1291 constant)
    # Upper bound: Cap at grade 20 (post-graduate) for extreme complexity
    grade_level = max(0, min(20, math.floor(smog_index + 0.5)))

    return SMOGResult(
        smog_index=smog_index,
        grade_level=grade_level,
        metadata={
            "sentence_count": len(sentences),
            "word_count": len(tokens),
            "polysyllable_count": polysyllable_count,
            "warning": "Less than 30 sentences" if len(sentences) < 30 else None,
        },
    )
