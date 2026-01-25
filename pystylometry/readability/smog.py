"""SMOG (Simple Measure of Gobbledygook) Index.

This module implements the SMOG readability formula with native chunked
analysis for stylometric fingerprinting.

Related GitHub Issue:
    #27 - Native chunked analysis with Distribution dataclass
    https://github.com/craigtrim/pystylometry/issues/27
"""

import math

from .._normalize import normalize_for_readability
from .._types import Distribution, SMOGResult, chunk_text, make_distribution
from .._utils import split_sentences, tokenize
from .syllables import count_syllables


def _compute_smog_single(text: str) -> tuple[float, float, dict]:
    """Compute SMOG metrics for a single chunk of text.

    Returns:
        Tuple of (smog_index, grade_level, metadata_dict).
        Returns (nan, nan, metadata) for empty/invalid input.
    """
    sentences = split_sentences(text)
    tokens = tokenize(text)
    word_tokens = normalize_for_readability(tokens)

    if len(sentences) == 0 or len(word_tokens) == 0:
        return (
            float("nan"),
            float("nan"),
            {"sentence_count": 0, "word_count": 0, "polysyllable_count": 0},
        )

    # Count polysyllables (words with 3+ syllables)
    polysyllable_count = sum(1 for word in word_tokens if count_syllables(word) >= 3)

    # SMOG formula
    smog_index = 1.043 * math.sqrt(polysyllable_count * 30 / len(sentences)) + 3.1291
    grade_level = max(0, min(20, math.floor(smog_index + 0.5)))

    metadata = {
        "sentence_count": len(sentences),
        "word_count": len(word_tokens),
        "polysyllable_count": polysyllable_count,
    }

    return (smog_index, float(grade_level), metadata)


def compute_smog(text: str, chunk_size: int = 1000) -> SMOGResult:
    """
    Compute SMOG (Simple Measure of Gobbledygook) Index.

    This function uses native chunked analysis to capture variance and patterns
    across the text, which is essential for stylometric fingerprinting.

    Formula:
        SMOG = 1.043 × √(polysyllables × 30/sentences) + 3.1291

    Where polysyllables are words with 3 or more syllables.

    The SMOG index estimates the years of education needed to understand the text.
    It's particularly useful for healthcare materials.

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27

    References:
        McLaughlin, G. H. (1969). SMOG grading: A new readability formula.
        Journal of Reading, 12(8), 639-646.

    Args:
        text: Input text to analyze
        chunk_size: Number of words per chunk (default: 1000).
            The text is divided into chunks of this size, and metrics are
            computed per-chunk.

    Returns:
        SMOGResult with:
            - smog_index: Mean SMOG index across chunks
            - grade_level: Mean grade level across chunks
            - smog_index_dist: Distribution with per-chunk values and stats
            - grade_level_dist: Distribution with per-chunk values and stats
            - chunk_size: The chunk size used
            - chunk_count: Number of chunks analyzed

    Example:
        >>> result = compute_smog("Long text here...", chunk_size=1000)
        >>> result.smog_index  # Mean across chunks
        12.5
        >>> result.smog_index_dist.std  # Variance reveals fingerprint
        1.8
    """
    # Chunk the text
    chunks = chunk_text(text, chunk_size)

    # Compute metrics per chunk
    smog_values = []
    grade_values = []
    total_sentences = 0
    total_words = 0
    total_polysyllables = 0

    for chunk in chunks:
        si, gl, meta = _compute_smog_single(chunk)
        if not math.isnan(si):
            smog_values.append(si)
            grade_values.append(gl)
        total_sentences += meta.get("sentence_count", 0)
        total_words += meta.get("word_count", 0)
        total_polysyllables += meta.get("polysyllable_count", 0)

    # Handle empty or all-invalid chunks
    if not smog_values:
        empty_dist = Distribution(
            values=[],
            mean=float("nan"),
            median=float("nan"),
            std=0.0,
            range=0.0,
            iqr=0.0,
        )
        return SMOGResult(
            smog_index=float("nan"),
            grade_level=float("nan"),
            smog_index_dist=empty_dist,
            grade_level_dist=empty_dist,
            chunk_size=chunk_size,
            chunk_count=len(chunks),
            metadata={
                # Backward-compatible keys
                "sentence_count": 0,
                "word_count": 0,
                "polysyllable_count": 0,
                # New prefixed keys for consistency
                "total_sentence_count": 0,
                "total_word_count": 0,
                "total_polysyllable_count": 0,
                "warning": "Insufficient text",
            },
        )

    # Build distributions
    smog_dist = make_distribution(smog_values)
    grade_dist = make_distribution(grade_values)

    return SMOGResult(
        smog_index=smog_dist.mean,
        grade_level=grade_dist.mean,
        smog_index_dist=smog_dist,
        grade_level_dist=grade_dist,
        chunk_size=chunk_size,
        chunk_count=len(chunks),
        metadata={
            # Backward-compatible keys
            "sentence_count": total_sentences,
            "word_count": total_words,
            "polysyllable_count": total_polysyllables,
            # New prefixed keys for consistency
            "total_sentence_count": total_sentences,
            "total_word_count": total_words,
            "total_polysyllable_count": total_polysyllables,
            "warning": "Less than 30 sentences" if total_sentences < 30 else None,
        },
    )
