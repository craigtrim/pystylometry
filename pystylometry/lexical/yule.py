"""Yule's K and I statistics for vocabulary richness.

This module implements Yule's K and I metrics with native chunked analysis
for stylometric fingerprinting.

Related GitHub Issue:
    #27 - Native chunked analysis with Distribution dataclass
    https://github.com/craigtrim/pystylometry/issues/27
"""

import math
from collections import Counter

from .._types import Distribution, YuleResult, chunk_text, make_distribution
from .._utils import tokenize


def _compute_yule_single(text: str) -> tuple[float, float, dict]:
    """Compute Yule's K and I for a single chunk of text.

    Returns:
        Tuple of (yule_k, yule_i, metadata_dict).
        Returns (nan, nan, metadata) for empty/invalid input.
    """
    tokens = tokenize(text.lower())
    N = len(tokens)  # noqa: N806

    if N == 0:
        return (
            float("nan"),
            float("nan"),
            {"token_count": 0, "vocabulary_size": 0},
        )

    # Count frequency of each token
    freq_counter = Counter(tokens)
    V = len(freq_counter)  # noqa: N806

    # Count how many words occur with each frequency
    freq_of_freqs = Counter(freq_counter.values())

    # Calculate Σm²×Vm
    sum_m2_vm = sum(m * m * vm for m, vm in freq_of_freqs.items())

    # Yule's K: 10⁴ × (Σm²×Vm - N) / N²
    yule_k = 10_000 * (sum_m2_vm - N) / (N * N)

    # Yule's I: V² / (Σm²×Vm - N)
    denominator = sum_m2_vm - N
    if denominator == 0:
        yule_i = float("nan")
    else:
        yule_i = (V * V) / denominator

    return (
        yule_k,
        yule_i,
        {"token_count": N, "vocabulary_size": V},
    )


def compute_yule(text: str, chunk_size: int = 1000) -> YuleResult:
    """
    Compute Yule's K and I metrics for vocabulary richness.

    This function uses native chunked analysis to capture variance and patterns
    across the text, which is essential for stylometric fingerprinting.

    Yule's K measures vocabulary repetitiveness (higher = more repetitive).
    Yule's I is the inverse measure (higher = more diverse).

    Formula:
        K = 10⁴ × (Σm²×Vm - N) / N²
        I = V² / (Σm²×Vm - N)

    Where:
        - N = total tokens
        - V = vocabulary size (unique types)
        - Vm = number of types occurring m times
        - m = frequency count

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27

    References:
        Yule, G. U. (1944). The Statistical Study of Literary Vocabulary.
        Cambridge University Press.

    Args:
        text: Input text to analyze
        chunk_size: Number of words per chunk (default: 1000)

    Returns:
        YuleResult with yule_k, yule_i, distributions, and metadata

    Example:
        >>> result = compute_yule("Long text here...", chunk_size=1000)
        >>> result.yule_k  # Mean across chunks
        120.5
        >>> result.yule_k_dist.std  # Variance reveals fingerprint
        15.2
    """
    # Chunk the text
    chunks = chunk_text(text, chunk_size)

    # Compute metrics per chunk
    yule_k_values = []
    yule_i_values = []
    total_tokens = 0
    total_vocab = 0

    for chunk in chunks:
        k, i, meta = _compute_yule_single(chunk)
        if not math.isnan(k):
            yule_k_values.append(k)
        if not math.isnan(i):
            yule_i_values.append(i)
        total_tokens += meta.get("token_count", 0)
        total_vocab += meta.get("vocabulary_size", 0)

    # Handle empty or all-invalid chunks
    if not yule_k_values:
        empty_dist = Distribution(
            values=[],
            mean=float("nan"),
            median=float("nan"),
            std=0.0,
            range=0.0,
            iqr=0.0,
        )
        return YuleResult(
            yule_k=float("nan"),
            yule_i=float("nan"),
            yule_k_dist=empty_dist,
            yule_i_dist=empty_dist,
            chunk_size=chunk_size,
            chunk_count=len(chunks),
            metadata={
                # Backward-compatible keys
                "token_count": 0,
                "vocabulary_size": 0,
                # New prefixed keys for consistency
                "total_token_count": 0,
                "total_vocabulary_size": 0,
            },
        )

    # Build distributions
    yule_k_dist = make_distribution(yule_k_values)
    yule_i_dist = (
        make_distribution(yule_i_values)
        if yule_i_values
        else Distribution(
            values=[],
            mean=float("nan"),
            median=float("nan"),
            std=0.0,
            range=0.0,
            iqr=0.0,
        )
    )

    return YuleResult(
        yule_k=yule_k_dist.mean,
        yule_i=yule_i_dist.mean,
        yule_k_dist=yule_k_dist,
        yule_i_dist=yule_i_dist,
        chunk_size=chunk_size,
        chunk_count=len(chunks),
        metadata={
            # Backward-compatible keys
            "token_count": total_tokens,
            "vocabulary_size": total_vocab,
            # New prefixed keys for consistency
            "total_token_count": total_tokens,
            "total_vocabulary_size": total_vocab,
        },
    )
