"""SMOG (Simple Measure of Gobbledygook) Index."""

from .._types import SMOGResult
from .._utils import tokenize, split_sentences
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

    Example:
        >>> result = compute_smog("The quick brown fox jumps over the lazy dog.")
        >>> print(f"SMOG Index: {result.smog_index:.1f}")
        >>> print(f"Grade Level: {result.grade_level}")
    """
    sentences = split_sentences(text)
    tokens = tokenize(text)

    if len(sentences) < 30:
        # SMOG requires at least 30 sentences for accuracy
        # We'll compute anyway but note in metadata
        pass

    if len(sentences) == 0 or len(tokens) == 0:
        return SMOGResult(
            smog_index=0.0,
            grade_level=0,
            metadata={
                "sentence_count": 0,
                "word_count": 0,
                "polysyllable_count": 0,
                "warning": "Insufficient text"
            }
        )

    # Count polysyllables (words with 3+ syllables)
    polysyllable_count = sum(1 for word in tokens if count_syllables(word) >= 3)

    # TODO: Implement SMOG formula
    smog_index = 0.0  # Placeholder
    grade_level = 0   # Placeholder

    return SMOGResult(
        smog_index=smog_index,
        grade_level=grade_level,
        metadata={
            "sentence_count": len(sentences),
            "word_count": len(tokens),
            "polysyllable_count": polysyllable_count,
            "warning": "Less than 30 sentences" if len(sentences) < 30 else None
        }
    )
