"""Yule's K and I statistics for vocabulary richness."""

from collections import Counter

from .._types import YuleResult
from .._utils import tokenize


def compute_yule(text: str) -> YuleResult:
    """
    Compute Yule's K and I metrics for vocabulary richness.

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

    References:
        Yule, G. U. (1944). The Statistical Study of Literary Vocabulary.
        Cambridge University Press.

    Args:
        text: Input text to analyze

    Returns:
        YuleResult with .yule_k, .yule_i, and metadata

        Note: For empty input or when Σm²×Vm = N (perfectly uniform vocabulary),
        metrics will be float('nan') to indicate undefined values.

    Example:
        >>> result = compute_yule("The quick brown fox jumps over the lazy dog.")
        >>> print(f"Yule's K: {result.yule_k:.2f}")
        >>> print(f"Yule's I: {result.yule_i:.2f}")

        >>> # Empty input returns NaN
        >>> import math
        >>> result_empty = compute_yule("")
        >>> math.isnan(result_empty.yule_k)
        True
    """
    tokens = tokenize(text.lower())
    N = len(tokens)  # noqa: N806

    if N == 0:
        return YuleResult(
            yule_k=float("nan"),
            yule_i=float("nan"),
            metadata={"token_count": 0, "vocabulary_size": 0},
        )

    # Count frequency of each token
    freq_counter = Counter(tokens)
    V = len(freq_counter)  # noqa: N806

    # Count how many words occur with each frequency
    # Vm[m] = number of words that occur exactly m times
    freq_of_freqs = Counter(freq_counter.values())

    # Calculate Σm²×Vm (sum of m-squared times Vm for all m)
    # This is the sum across all frequency levels of:
    # (frequency)² × (count of words at that frequency)
    sum_m2_vm = sum(m * m * vm for m, vm in freq_of_freqs.items())

    # Yule's K: 10⁴ × (Σm²×Vm - N) / N²
    # K measures vocabulary repetitiveness (higher K = more repetitive)
    yule_k = 10_000 * (sum_m2_vm - N) / (N * N)

    # Yule's I: V² / (Σm²×Vm - N)
    # I is the inverse measure (higher I = more diverse)
    # If Σm²×Vm = N (perfectly uniform vocabulary), denominator is 0, return NaN
    denominator = sum_m2_vm - N
    if denominator == 0:
        yule_i = float("nan")
    else:
        yule_i = (V * V) / denominator

    return YuleResult(
        yule_k=yule_k,
        yule_i=yule_i,
        metadata={
            "token_count": N,
            "vocabulary_size": V,
        },
    )
