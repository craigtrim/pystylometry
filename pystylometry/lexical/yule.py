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

        **Empty Input Handling (API Consistency):**
        For empty input (no tokens), yule_k and yule_i will be float('nan').
        This maintains API consistency with readability metrics (Flesch PR #3,
        Coleman-Liau PR #2, Gunning Fog PR #4) and prevents conflating "no data"
        with "low vocabulary diversity".

        A text with perfect repetition (e.g., "the the the") legitimately has
        high Yule's K. Empty string semantically means "cannot measure", not
        "zero diversity".

        Consumers should check for NaN:
            import math
            if not math.isnan(result.yule_k):
                # Process valid result

        This follows the IEEE 754 standard for representing undefined/missing values.

    Example:
        >>> result = compute_yule("The quick brown fox jumps over the lazy dog.")
        >>> print(f"Yule's K: {result.yule_k:.2f}")
        >>> print(f"Yule's I: {result.yule_i:.2f}")

        >>> # Empty input returns NaN (not 0.0)
        >>> import math
        >>> result_empty = compute_yule("")
        >>> math.isnan(result_empty.yule_k)
        True
        >>> math.isnan(result_empty.yule_i)
        True
    """
    tokens = tokenize(text.lower())
    N = len(tokens)  # noqa: N806

    # Empty Input Handling: Return NaN for Undefined Measurements
    # ============================================================
    # Design Decision (aligned with Flesch PR #3, Coleman-Liau PR #2, Gunning Fog PR #4):
    #
    # Previous implementation returned yule_k=0.0 and yule_i=0.0 for empty input.
    # This was semantically incorrect because:
    #
    # 1. A text with perfect repetition (e.g., "the the the the") legitimately has
    #    high Yule's K (low diversity), not zero
    # 2. Empty string means "cannot measure", not "zero diversity"
    # 3. Returning 0.0 allowed empty strings to silently contaminate aggregates
    #
    # Correct behavior: Return float('nan') to represent undefined measurement
    # - NaN propagates through arithmetic, signaling missing data
    # - Consumers must explicitly filter: [x for x in scores if not math.isnan(x)]
    # - Follows IEEE 754 standard for undefined/missing numerical values
    # - Consistent with readability metrics: Flesch, Coleman-Liau, Gunning Fog, etc.
    #
    # Academic rationale: Yule (1944) defined K and I for analyzing "vocabulary richness"
    # in literary texts. The formulas (K = 10⁴ × (Σm²×Vm - N) / N² and I = V²/Σm²×Vm - 1/N)
    # involve division by N and N², making them mathematically undefined for N=0.
    #
    # Reference: Yule, G. U. (1944). The Statistical Study of Literary Vocabulary.
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
