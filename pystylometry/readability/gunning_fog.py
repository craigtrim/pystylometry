"""Gunning Fog Index."""

from .._types import GunningFogResult
from .._utils import tokenize, split_sentences
from .syllables import count_syllables


def compute_gunning_fog(text: str) -> GunningFogResult:
    """
    Compute Gunning Fog Index.

    Formula:
        Fog Index = 0.4 × [(words/sentences) + 100 × (complex words/words)]

    Where complex words are defined as words with 3+ syllables,
    excluding proper nouns, compound words, and common suffixes.

    The index estimates years of formal education needed to understand the text
    on first reading.

    References:
        Gunning, R. (1952). The Technique of Clear Writing.
        McGraw-Hill.

    Args:
        text: Input text to analyze

    Returns:
        GunningFogResult with fog index and grade level

    Example:
        >>> result = compute_gunning_fog("The quick brown fox jumps over the lazy dog.")
        >>> print(f"Fog Index: {result.fog_index:.1f}")
        >>> print(f"Grade Level: {result.grade_level}")
    """
    sentences = split_sentences(text)
    tokens = tokenize(text)

    if len(sentences) == 0 or len(tokens) == 0:
        return GunningFogResult(
            fog_index=0.0,
            grade_level=0,
            metadata={"sentence_count": 0, "word_count": 0, "complex_word_count": 0}
        )

    # Count complex words (3+ syllables)
    # TODO: Exclude proper nouns, compound words, and -es/-ed/-ing endings
    complex_word_count = sum(1 for word in tokens if count_syllables(word) >= 3)

    # TODO: Implement Gunning Fog formula
    fog_index = 0.0  # Placeholder
    grade_level = 0  # Placeholder

    return GunningFogResult(
        fog_index=fog_index,
        grade_level=grade_level,
        metadata={
            "sentence_count": len(sentences),
            "word_count": len(tokens),
            "complex_word_count": complex_word_count,
            "complex_word_percentage": (complex_word_count / len(tokens) * 100) if tokens else 0
        }
    )
