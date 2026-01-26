"""Coleman-Liau Index.

This module implements the Coleman-Liau readability formula with native chunked
analysis for stylometric fingerprinting.

Related GitHub Issue:
    #27 - Native chunked analysis with Distribution dataclass
    https://github.com/craigtrim/pystylometry/issues/27
"""

import math

from .._types import ColemanLiauResult, Distribution, chunk_text, make_distribution
from .._utils import split_sentences, tokenize

# Regression coefficients from Coleman & Liau (1975)
_LETTER_COEFFICIENT = 0.0588
_SENTENCE_COEFFICIENT = -0.296
_INTERCEPT = -15.8


def _compute_coleman_liau_single(text: str) -> tuple[float, float, dict]:
    """Compute Coleman-Liau metrics for a single chunk of text.

    Returns:
        Tuple of (cli_index, grade_level, metadata_dict).
        Returns (nan, nan, metadata) for empty/invalid input.
    """
    sentences = split_sentences(text)
    all_tokens = tokenize(text)
    tokens = [token for token in all_tokens if any(char.isalpha() for char in token)]
    letter_count = sum(1 for token in tokens for char in token if char.isalpha())

    if len(sentences) == 0 or len(tokens) == 0:
        return (
            float("nan"),
            float("nan"),
            {"sentence_count": 0, "word_count": 0, "letter_count": 0},
        )

    # Calculate per 100 words
    L = (letter_count / len(tokens)) * 100  # noqa: N806
    S = (len(sentences) / len(tokens)) * 100  # noqa: N806

    # Compute Coleman-Liau Index
    cli_index = _LETTER_COEFFICIENT * L + _SENTENCE_COEFFICIENT * S + _INTERCEPT
    grade_level = max(0, math.floor(cli_index + 0.5))

    metadata = {
        "sentence_count": len(sentences),
        "word_count": len(tokens),
        "letter_count": letter_count,
        "letters_per_100_words": L,
        "sentences_per_100_words": S,
    }

    return (cli_index, float(grade_level), metadata)


def compute_coleman_liau(text: str, chunk_size: int = 1000) -> ColemanLiauResult:
    """
    Compute Coleman-Liau Index.

    This function uses native chunked analysis to capture variance and patterns
    across the text, which is essential for stylometric fingerprinting.

    Formula:
        CLI = 0.0588 × L - 0.296 × S - 15.8

    Where:
        L = average number of letters per 100 words
        S = average number of sentences per 100 words

    The Coleman-Liau index relies on characters rather than syllables,
    making it easier to compute and not requiring syllable-counting algorithms.

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27

    References:
        Coleman, M., & Liau, T. L. (1975). A computer readability formula
        designed for machine scoring. Journal of Applied Psychology, 60(2), 283.

    Args:
        text: Input text to analyze
        chunk_size: Number of words per chunk (default: 1000).
            The text is divided into chunks of this size, and metrics are
            computed per-chunk.

    Returns:
        ColemanLiauResult with:
            - cli_index: Mean CLI across chunks
            - grade_level: Mean grade level across chunks
            - cli_index_dist: Distribution with per-chunk values and stats
            - grade_level_dist: Distribution with per-chunk values and stats
            - chunk_size: The chunk size used
            - chunk_count: Number of chunks analyzed

    Example:
        >>> result = compute_coleman_liau("Long text here...", chunk_size=1000)
        >>> result.cli_index  # Mean across chunks
        8.5
        >>> result.cli_index_dist.std  # Variance reveals fingerprint
        1.2
    """
    # Chunk the text
    chunks = chunk_text(text, chunk_size)

    # Compute metrics per chunk
    cli_values = []
    grade_values = []
    total_sentences = 0
    total_words = 0
    total_letters = 0

    for chunk in chunks:
        ci, gl, meta = _compute_coleman_liau_single(chunk)
        if not math.isnan(ci):
            cli_values.append(ci)
            grade_values.append(gl)
        total_sentences += meta.get("sentence_count", 0)
        total_words += meta.get("word_count", 0)
        total_letters += meta.get("letter_count", 0)

    # Handle empty or all-invalid chunks
    if not cli_values:
        empty_dist = Distribution(
            values=[],
            mean=float("nan"),
            median=float("nan"),
            std=0.0,
            range=0.0,
            iqr=0.0,
        )
        return ColemanLiauResult(
            cli_index=float("nan"),
            grade_level=float("nan"),
            cli_index_dist=empty_dist,
            grade_level_dist=empty_dist,
            chunk_size=chunk_size,
            chunk_count=len(chunks),
            metadata={
                # Backward-compatible keys
                "sentence_count": 0,
                "word_count": 0,
                "letter_count": 0,
                "letters_per_100_words": 0.0,
                "sentences_per_100_words": 0.0,
                # New prefixed keys for consistency
                "total_sentence_count": 0,
                "total_word_count": 0,
                "total_letter_count": 0,
                "reliable": False,
            },
        )

    # Build distributions
    cli_dist = make_distribution(cli_values)
    grade_dist = make_distribution(grade_values)

    # Reliability heuristic
    reliable = total_words >= 100

    return ColemanLiauResult(
        cli_index=cli_dist.mean,
        grade_level=grade_dist.mean,
        cli_index_dist=cli_dist,
        grade_level_dist=grade_dist,
        chunk_size=chunk_size,
        chunk_count=len(chunks),
        metadata={
            # Backward-compatible keys
            "sentence_count": total_sentences,
            "word_count": total_words,
            "letter_count": total_letters,
            "letters_per_100_words": (total_letters / total_words * 100) if total_words > 0 else 0,
            "sentences_per_100_words": (total_sentences / total_words * 100)
            if total_words > 0
            else 0,
            # New prefixed keys for consistency
            "total_sentence_count": total_sentences,
            "total_word_count": total_words,
            "total_letter_count": total_letters,
            "reliable": reliable,
        },
    )
