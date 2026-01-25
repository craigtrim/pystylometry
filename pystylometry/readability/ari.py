"""Automated Readability Index (ARI).

This module implements the ARI readability formula with native chunked
analysis for stylometric fingerprinting.

Related GitHub Issue:
    #27 - Native chunked analysis with Distribution dataclass
    https://github.com/craigtrim/pystylometry/issues/27
"""

import math

from .._types import ARIResult, Distribution, chunk_text, make_distribution
from .._utils import split_sentences, tokenize

# Formula coefficients from Senter & Smith (1967)
_CHARACTER_COEFFICIENT = 4.71
_WORD_COEFFICIENT = 0.5
_INTERCEPT = -21.43


def _get_age_range(grade_level: float) -> str:
    """Map grade level to age range."""
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


def _compute_ari_single(text: str) -> tuple[float, float, dict]:
    """Compute ARI metrics for a single chunk of text.

    Returns:
        Tuple of (ari_score, grade_level, metadata_dict).
        Returns (nan, nan, metadata) for empty/invalid input.
    """
    sentences = split_sentences(text)
    tokens = tokenize(text)
    character_count = sum(1 for char in text if char.isalnum())

    if len(sentences) == 0 or len(tokens) == 0:
        return (
            float("nan"),
            float("nan"),
            {"sentence_count": 0, "word_count": 0, "character_count": 0},
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

    grade_level = max(0, min(20, math.floor(ari_score + 0.5)))

    metadata = {
        "sentence_count": len(sentences),
        "word_count": len(tokens),
        "character_count": character_count,
        "characters_per_word": chars_per_word,
        "words_per_sentence": words_per_sentence,
    }

    return (ari_score, float(grade_level), metadata)


def compute_ari(text: str, chunk_size: int = 1000) -> ARIResult:
    """
    Compute Automated Readability Index (ARI).

    This function uses native chunked analysis to capture variance and patterns
    across the text, which is essential for stylometric fingerprinting.

    Formula:
        ARI = 4.71 × (characters/words) + 0.5 × (words/sentences) - 21.43

    The ARI uses character counts and word counts (similar to Coleman-Liau)
    but adds sentence length as a factor. It produces an approximate
    representation of the US grade level needed to comprehend the text.

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27

    References:
        Senter, R. J., & Smith, E. A. (1967). Automated readability index.
        AMRL-TR-6620. Aerospace Medical Research Laboratories.

    Args:
        text: Input text to analyze
        chunk_size: Number of words per chunk (default: 1000).
            The text is divided into chunks of this size, and metrics are
            computed per-chunk.

    Returns:
        ARIResult with:
            - ari_score: Mean ARI score across chunks
            - grade_level: Mean grade level across chunks
            - age_range: Age range based on mean grade level
            - ari_score_dist: Distribution with per-chunk values and stats
            - grade_level_dist: Distribution with per-chunk values and stats
            - chunk_size: The chunk size used
            - chunk_count: Number of chunks analyzed

    Example:
        >>> result = compute_ari("Long text here...", chunk_size=1000)
        >>> result.ari_score  # Mean across chunks
        9.5
        >>> result.ari_score_dist.std  # Variance reveals fingerprint
        1.5
    """
    # Chunk the text
    chunks = chunk_text(text, chunk_size)

    # Compute metrics per chunk
    ari_values = []
    grade_values = []
    total_sentences = 0
    total_words = 0
    total_chars = 0

    for chunk in chunks:
        ai, gl, meta = _compute_ari_single(chunk)
        if not math.isnan(ai):
            ari_values.append(ai)
            grade_values.append(gl)
        total_sentences += meta.get("sentence_count", 0)
        total_words += meta.get("word_count", 0)
        total_chars += meta.get("character_count", 0)

    # Handle empty or all-invalid chunks
    if not ari_values:
        empty_dist = Distribution(
            values=[],
            mean=float("nan"),
            median=float("nan"),
            std=0.0,
            range=0.0,
            iqr=0.0,
        )
        return ARIResult(
            ari_score=float("nan"),
            grade_level=float("nan"),
            age_range="Unknown",
            ari_score_dist=empty_dist,
            grade_level_dist=empty_dist,
            chunk_size=chunk_size,
            chunk_count=len(chunks),
            metadata={
                # Backward-compatible keys
                "sentence_count": 0,
                "word_count": 0,
                "character_count": 0,
                "characters_per_word": 0.0,
                "words_per_sentence": 0.0,
                # New prefixed keys for consistency
                "total_sentence_count": 0,
                "total_word_count": 0,
                "total_character_count": 0,
                "reliable": False,
            },
        )

    # Build distributions
    ari_dist = make_distribution(ari_values)
    grade_dist = make_distribution(grade_values)

    # Get age range from mean grade level
    age_range = _get_age_range(grade_dist.mean)

    # Reliability heuristic
    reliable = total_words >= 100

    return ARIResult(
        ari_score=ari_dist.mean,
        grade_level=grade_dist.mean,
        age_range=age_range,
        ari_score_dist=ari_dist,
        grade_level_dist=grade_dist,
        chunk_size=chunk_size,
        chunk_count=len(chunks),
        metadata={
            # Backward-compatible keys
            "sentence_count": total_sentences,
            "word_count": total_words,
            "character_count": total_chars,
            "characters_per_word": total_chars / total_words if total_words > 0 else 0,
            "words_per_sentence": total_words / total_sentences if total_sentences > 0 else 0,
            # New prefixed keys for consistency
            "total_sentence_count": total_sentences,
            "total_word_count": total_words,
            "total_character_count": total_chars,
            "reliable": reliable,
        },
    )
