"""Coleman-Liau Index."""

from .._types import ColemanLiauResult
from .._utils import tokenize, split_sentences


def compute_coleman_liau(text: str) -> ColemanLiauResult:
    """
    Compute Coleman-Liau Index.

    Formula:
        CLI = 0.0588 × L - 0.296 × S - 15.8

    Where:
        L = average number of letters per 100 words
        S = average number of sentences per 100 words

    The Coleman-Liau index relies on characters rather than syllables,
    making it easier to compute and potentially more language-agnostic.

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
        >>> print(f"Grade Level: {result.grade_level}")
    """
    sentences = split_sentences(text)
    tokens = tokenize(text)

    if len(sentences) == 0 or len(tokens) == 0:
        return ColemanLiauResult(
            cli_index=0.0,
            grade_level=0,
            metadata={"sentence_count": 0, "word_count": 0, "letter_count": 0}
        )

    # Count letters (excluding spaces and punctuation)
    letter_count = sum(1 for char in text if char.isalpha())

    # Calculate per 100 words
    L = (letter_count / len(tokens)) * 100
    S = (len(sentences) / len(tokens)) * 100

    # TODO: Implement Coleman-Liau formula
    cli_index = 0.0  # Placeholder
    grade_level = 0  # Placeholder

    return ColemanLiauResult(
        cli_index=cli_index,
        grade_level=grade_level,
        metadata={
            "sentence_count": len(sentences),
            "word_count": len(tokens),
            "letter_count": letter_count,
            "letters_per_100_words": L,
            "sentences_per_100_words": S,
        }
    )
