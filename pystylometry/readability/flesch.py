"""Flesch Reading Ease and Flesch-Kincaid Grade Level."""

from .._types import FleschResult
from .._utils import tokenize, split_sentences
from .syllables import count_syllables


def compute_flesch(text: str) -> FleschResult:
    """
    Compute Flesch Reading Ease and Flesch-Kincaid Grade Level.

    Flesch Reading Ease:
        Score = 206.835 - 1.015 × (words/sentences) - 84.6 × (syllables/words)
        Higher scores = easier to read (0-100 scale)

    Flesch-Kincaid Grade Level:
        Grade = 0.39 × (words/sentences) + 11.8 × (syllables/words) - 15.59

    Interpretation of Reading Ease:
        90-100: Very Easy (5th grade)
        80-89:  Easy (6th grade)
        70-79:  Fairly Easy (7th grade)
        60-69:  Standard (8th-9th grade)
        50-59:  Fairly Difficult (10th-12th grade)
        30-49:  Difficult (College)
        0-29:   Very Difficult (College graduate)

    References:
        Flesch, R. (1948). A new readability yardstick.
        Journal of Applied Psychology, 32(3), 221.

        Kincaid, J. P., et al. (1975). Derivation of new readability formulas
        for Navy enlisted personnel. Naval Technical Training Command.

    Args:
        text: Input text to analyze

    Returns:
        FleschResult with reading ease, grade level, and difficulty rating

    Example:
        >>> result = compute_flesch("The quick brown fox jumps over the lazy dog.")
        >>> print(f"Reading Ease: {result.reading_ease:.1f}")
        >>> print(f"Grade Level: {result.grade_level:.1f}")
        >>> print(f"Difficulty: {result.difficulty}")
    """
    sentences = split_sentences(text)
    tokens = tokenize(text)

    if len(sentences) == 0 or len(tokens) == 0:
        return FleschResult(
            reading_ease=0.0,
            grade_level=0.0,
            difficulty="Unknown",
            metadata={"sentence_count": 0, "word_count": 0, "syllable_count": 0}
        )

    # Count syllables
    total_syllables = sum(count_syllables(word) for word in tokens)

    # Calculate metrics
    words_per_sentence = len(tokens) / len(sentences)
    syllables_per_word = total_syllables / len(tokens)

    # TODO: Implement Flesch formulas
    reading_ease = 0.0  # Placeholder
    grade_level = 0.0   # Placeholder
    difficulty = "Unknown"  # Placeholder

    return FleschResult(
        reading_ease=reading_ease,
        grade_level=grade_level,
        difficulty=difficulty,
        metadata={
            "sentence_count": len(sentences),
            "word_count": len(tokens),
            "syllable_count": total_syllables,
            "words_per_sentence": words_per_sentence,
            "syllables_per_word": syllables_per_word,
        }
    )
