"""Automated Readability Index (ARI)."""

from .._types import ARIResult
from .._utils import split_sentences, tokenize


def compute_ari(text: str) -> ARIResult:
    """
    Compute Automated Readability Index (ARI).

    Formula:
        ARI = 4.71 × (characters/words) + 0.5 × (words/sentences) - 21.43

    The ARI is designed to gauge the understandability of a text and produces
    an approximate representation of the US grade level needed to comprehend the text.

    Grade Level to Age mapping:
        1-5:   5-11 years
        6-8:   11-14 years
        9-12:  14-18 years
        13-14: 18-22 years
        14+:   22+ years (college level)

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
        >>> print(f"Grade Level: {result.grade_level}")
        >>> print(f"Age Range: {result.age_range}")
    """
    sentences = split_sentences(text)
    tokens = tokenize(text)

    if len(sentences) == 0 or len(tokens) == 0:
        return ARIResult(
            ari_score=0.0,
            grade_level=0,
            age_range="Unknown",
            metadata={"sentence_count": 0, "word_count": 0, "character_count": 0},
        )

    # Count characters (letters, numbers, excluding spaces and punctuation)
    character_count = sum(1 for char in text if char.isalnum())

    # TODO: Implement ARI formula
    ari_score = 0.0  # Placeholder
    grade_level = 0  # Placeholder
    age_range = "Unknown"  # Placeholder

    return ARIResult(
        ari_score=ari_score,
        grade_level=grade_level,
        age_range=age_range,
        metadata={
            "sentence_count": len(sentences),
            "word_count": len(tokens),
            "character_count": character_count,
            "characters_per_word": character_count / len(tokens) if tokens else 0,
            "words_per_sentence": len(tokens) / len(sentences) if sentences else 0,
        },
    )
