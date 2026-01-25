"""Flesch Reading Ease and Flesch-Kincaid Grade Level.

This module implements the Flesch readability formulas with native chunked
analysis for stylometric fingerprinting.

Related GitHub Issue:
    #27 - Native chunked analysis with Distribution dataclass
    https://github.com/craigtrim/pystylometry/issues/27
"""

from .._normalize import normalize_for_readability
from .._types import Distribution, FleschResult, chunk_text, make_distribution
from .._utils import split_sentences, tokenize
from .syllables import count_syllables


def _compute_flesch_single(text: str) -> tuple[float, float, dict]:
    """Compute Flesch metrics for a single chunk of text.

    Returns:
        Tuple of (reading_ease, grade_level, metadata_dict).
        Returns (nan, nan, metadata) for empty/invalid input.
    """
    sentences = split_sentences(text)
    tokens = tokenize(text)

    # Filter tokens to only valid words for syllable counting
    word_tokens = normalize_for_readability(tokens)

    if len(sentences) == 0 or len(word_tokens) == 0:
        return (
            float("nan"),
            float("nan"),
            {"sentence_count": 0, "word_count": 0, "syllable_count": 0},
        )

    # Count syllables
    total_syllables = sum(count_syllables(word) for word in word_tokens)

    # Calculate metrics
    words_per_sentence = len(word_tokens) / len(sentences)
    syllables_per_word = total_syllables / len(word_tokens)

    # Flesch Reading Ease
    reading_ease = 206.835 - (1.015 * words_per_sentence) - (84.6 * syllables_per_word)

    # Flesch-Kincaid Grade Level
    grade_level = (0.39 * words_per_sentence) + (11.8 * syllables_per_word) - 15.59

    metadata = {
        "sentence_count": len(sentences),
        "word_count": len(word_tokens),
        "syllable_count": total_syllables,
        "words_per_sentence": words_per_sentence,
        "syllables_per_word": syllables_per_word,
    }

    return (reading_ease, grade_level, metadata)


def _get_difficulty(reading_ease: float) -> str:
    """Determine difficulty rating based on reading ease score."""
    import math

    if math.isnan(reading_ease):
        return "Unknown"
    if reading_ease >= 90:
        return "Very Easy"
    if reading_ease >= 80:
        return "Easy"
    if reading_ease >= 70:
        return "Fairly Easy"
    if reading_ease >= 60:
        return "Standard"
    if reading_ease >= 50:
        return "Fairly Difficult"
    if reading_ease >= 30:
        return "Difficult"
    return "Very Difficult"


def compute_flesch(text: str, chunk_size: int = 1000) -> FleschResult:
    """
    Compute Flesch Reading Ease and Flesch-Kincaid Grade Level.

    This function uses native chunked analysis to capture variance and patterns
    across the text, which is essential for stylometric fingerprinting.

    Flesch Reading Ease:
        Score = 206.835 - 1.015 × (words/sentences) - 84.6 × (syllables/words)
        Higher scores = easier to read
        Typical range: 0-100, but can exceed bounds

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

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27

    References:
        Flesch, R. (1948). A new readability yardstick.
        Journal of Applied Psychology, 32(3), 221.

        Kincaid, J. P., et al. (1975). Derivation of new readability formulas
        for Navy enlisted personnel. Naval Technical Training Command.

    Args:
        text: Input text to analyze
        chunk_size: Number of words per chunk (default: 1000).
            The text is divided into chunks of this size, and metrics are
            computed per-chunk. Use a large value (e.g., 1_000_000) for
            single-chunk "aggregate" mode.

    Returns:
        FleschResult with:
            - reading_ease: Mean reading ease across chunks
            - grade_level: Mean grade level across chunks
            - difficulty: Difficulty rating based on mean reading_ease
            - reading_ease_dist: Distribution with per-chunk values and stats
            - grade_level_dist: Distribution with per-chunk values and stats
            - chunk_size: The chunk size used
            - chunk_count: Number of chunks analyzed

    Example:
        >>> result = compute_flesch("Long text here...", chunk_size=1000)
        >>> result.reading_ease  # Mean across chunks
        68.54
        >>> result.reading_ease_dist.std  # Variance reveals fingerprint
        4.2
        >>> result.reading_ease_dist.values  # Per-chunk values
        [65.2, 71.1, 68.8, ...]
        >>> result.chunk_count
        59

        >>> # Single-chunk mode (no chunking)
        >>> result = compute_flesch("Short text.", chunk_size=1_000_000)
        >>> result.chunk_count
        1
    """
    import math

    # Chunk the text
    chunks = chunk_text(text, chunk_size)

    # Compute metrics per chunk
    reading_ease_values = []
    grade_level_values = []
    total_sentences = 0
    total_words = 0
    total_syllables = 0

    for chunk in chunks:
        re, gl, meta = _compute_flesch_single(chunk)
        if not math.isnan(re):  # Only include valid results
            reading_ease_values.append(re)
            grade_level_values.append(gl)
        total_sentences += meta.get("sentence_count", 0)
        total_words += meta.get("word_count", 0)
        total_syllables += meta.get("syllable_count", 0)

    # Handle empty or all-invalid chunks
    if not reading_ease_values:
        empty_dist = Distribution(
            values=[],
            mean=float("nan"),
            median=float("nan"),
            std=0.0,
            range=0.0,
            iqr=0.0,
        )
        return FleschResult(
            reading_ease=float("nan"),
            grade_level=float("nan"),
            difficulty="Unknown",
            reading_ease_dist=empty_dist,
            grade_level_dist=empty_dist,
            chunk_size=chunk_size,
            chunk_count=len(chunks),
            metadata={
                # Backward-compatible keys
                "sentence_count": 0,
                "word_count": 0,
                "syllable_count": 0,
                # New prefixed keys for consistency
                "total_sentence_count": 0,
                "total_word_count": 0,
                "total_syllable_count": 0,
            },
        )

    # Build distributions
    reading_ease_dist = make_distribution(reading_ease_values)
    grade_level_dist = make_distribution(grade_level_values)

    # Use mean for convenient access
    mean_reading_ease = reading_ease_dist.mean
    mean_grade_level = grade_level_dist.mean
    difficulty = _get_difficulty(mean_reading_ease)

    return FleschResult(
        reading_ease=mean_reading_ease,
        grade_level=mean_grade_level,
        difficulty=difficulty,
        reading_ease_dist=reading_ease_dist,
        grade_level_dist=grade_level_dist,
        chunk_size=chunk_size,
        chunk_count=len(chunks),
        metadata={
            # Backward-compatible keys
            "sentence_count": total_sentences,
            "word_count": total_words,
            "syllable_count": total_syllables,
            # New prefixed keys for consistency
            "total_sentence_count": total_sentences,
            "total_word_count": total_words,
            "total_syllable_count": total_syllables,
            "words_per_sentence": total_words / total_sentences if total_sentences > 0 else 0,
            "syllables_per_word": total_syllables / total_words if total_words > 0 else 0,
        },
    )
