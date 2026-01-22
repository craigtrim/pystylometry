"""Flesch Reading Ease and Flesch-Kincaid Grade Level."""

from .._types import FleschResult
from .._utils import split_sentences, tokenize
from .syllables import count_syllables


def compute_flesch(text: str) -> FleschResult:
    """
    Compute Flesch Reading Ease and Flesch-Kincaid Grade Level.

    Flesch Reading Ease:
        Score = 206.835 - 1.015 × (words/sentences) - 84.6 × (syllables/words)
        Higher scores = easier to read
        Typical range: 0-100, but can exceed bounds for extremely simple (>100) or complex (<0) text

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

        Note: The difficulty label ("Very Easy", "Easy", etc.) is determined solely
        from the reading_ease score and does NOT consider the grade_level score.
        This means text with high reading_ease (e.g., 85 = "Easy") but high
        grade_level (e.g., 12 = college) will still be labeled "Easy". The two
        metrics measure different aspects of readability and may not always align.

        Note: For empty input (no sentences or words), reading_ease and grade_level
        will be float('nan'). This prevents conflating "no data" with "extremely
        difficult text" (score of 0). Consumers should check for NaN before
        performing arithmetic operations (e.g., using math.isnan() or filtering
        before aggregation) to avoid silent propagation of NaN in statistics.

    Example:
        >>> result = compute_flesch("The quick brown fox jumps over the lazy dog.")
        >>> print(f"Reading Ease: {result.reading_ease:.1f}")
        >>> print(f"Grade Level: {result.grade_level:.1f}")
        >>> print(f"Difficulty: {result.difficulty}")

        >>> # Empty input returns NaN
        >>> import math
        >>> result_empty = compute_flesch("")
        >>> math.isnan(result_empty.reading_ease)
        True
        >>> result_empty.difficulty
        'Unknown'
    """
    sentences = split_sentences(text)
    tokens = tokenize(text)

    if len(sentences) == 0 or len(tokens) == 0:
        return FleschResult(
            reading_ease=float("nan"),
            grade_level=float("nan"),
            difficulty="Unknown",
            metadata={"sentence_count": 0, "word_count": 0, "syllable_count": 0},
        )

    # Count syllables
    total_syllables = sum(count_syllables(word) for word in tokens)

    # Calculate metrics
    words_per_sentence = len(tokens) / len(sentences)
    syllables_per_word = total_syllables / len(tokens)

    # Flesch Reading Ease: 206.835 - 1.015 × (words/sentences) - 84.6 × (syllables/words)
    reading_ease = 206.835 - (1.015 * words_per_sentence) - (84.6 * syllables_per_word)

    # Flesch-Kincaid Grade Level: 0.39 × (words/sentences) + 11.8 × (syllables/words) - 15.59
    grade_level = (0.39 * words_per_sentence) + (11.8 * syllables_per_word) - 15.59

    # Determine difficulty rating based ONLY on reading ease score (not grade level)
    # This is a conscious design choice: difficulty labels follow the Reading Ease
    # thresholds exclusively, even though grade_level may suggest a different difficulty
    if reading_ease >= 90:
        difficulty = "Very Easy"
    elif reading_ease >= 80:
        difficulty = "Easy"
    elif reading_ease >= 70:
        difficulty = "Fairly Easy"
    elif reading_ease >= 60:
        difficulty = "Standard"
    elif reading_ease >= 50:
        difficulty = "Fairly Difficult"
    elif reading_ease >= 30:
        difficulty = "Difficult"
    else:
        difficulty = "Very Difficult"

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
        },
    )
