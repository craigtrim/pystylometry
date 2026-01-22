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
        I = (V² / Σm²×Vm) - (1/N)

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

    Example:
        >>> result = compute_yule("The quick brown fox jumps over the lazy dog.")
        >>> print(f"Yule's K: {result.yule_k:.2f}")
        >>> print(f"Yule's I: {result.yule_i:.2f}")
    """
    tokens = tokenize(text.lower())
    N = len(tokens)  # noqa: N806

    if N == 0:
        return YuleResult(yule_k=0.0, yule_i=0.0, metadata={"token_count": 0, "vocabulary_size": 0})

    # Count frequency of each token
    freq_counter = Counter(tokens)
    V = len(freq_counter)  # noqa: N806

    # Count how many words occur with each frequency
    # Vm[m] = number of words that occur exactly m times
    # freq_of_freqs = Counter(freq_counter.values())  # TODO: Will be needed for Yule's K

    # TODO: Implement Yule's K and I calculations
    yule_k = 0.0  # Placeholder
    yule_i = 0.0  # Placeholder

    return YuleResult(
        yule_k=yule_k,
        yule_i=yule_i,
        metadata={
            "token_count": N,
            "vocabulary_size": V,
        },
    )
