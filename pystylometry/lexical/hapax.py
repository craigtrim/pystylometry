"""Hapax legomena and related vocabulary richness metrics."""

from collections import Counter

from .._types import HapaxResult
from .._utils import tokenize


def compute_hapax_ratios(text: str) -> HapaxResult:
    """
    Compute hapax legomena, hapax dislegomena, and related richness metrics.

    Hapax legomena = words appearing exactly once
    Hapax dislegomena = words appearing exactly twice

    Also computes:
    - Sichel's S: V₂ / V (ratio of dislegomena to total vocabulary)
    - Honoré's R: 100 × log(N) / (1 - V₁/V)

    References:
        Sichel, H. S. (1975). On a distribution law for word frequencies.
        Journal of the American Statistical Association, 70(351a), 542-547.

        Honoré, A. (1979). Some simple measures of richness of vocabulary.
        Association for Literary and Linguistic Computing Bulletin, 7, 172-177.

    Args:
        text: Input text to analyze

    Returns:
        HapaxResult with counts, ratios, Sichel's S, Honoré's R, and metadata

    Example:
        >>> result = compute_hapax_ratios("The quick brown fox jumps over the lazy dog.")
        >>> print(f"Hapax ratio: {result.hapax_ratio:.3f}")
        >>> print(f"Sichel's S: {result.sichel_s:.3f}")
    """
    tokens = tokenize(text.lower())
    N = len(tokens)  # noqa: N806

    if N == 0:
        return HapaxResult(
            hapax_count=0,
            hapax_ratio=0.0,
            dis_hapax_count=0,
            dis_hapax_ratio=0.0,
            sichel_s=0.0,
            honore_r=0.0,
            metadata={"token_count": 0, "vocabulary_size": 0},
        )

    # Count frequency of each token
    freq_counter = Counter(tokens)
    V = len(freq_counter)  # noqa: N806

    # Count hapax legomena (V₁) and dislegomena (V₂)
    V1 = sum(1 for count in freq_counter.values() if count == 1)  # noqa: N806
    V2 = sum(1 for count in freq_counter.values() if count == 2)  # noqa: N806

    # TODO: Implement Sichel's S and Honoré's R
    sichel_s = 0.0  # Placeholder
    honore_r = 0.0  # Placeholder

    return HapaxResult(
        hapax_count=V1,
        hapax_ratio=V1 / N if N > 0 else 0.0,
        dis_hapax_count=V2,
        dis_hapax_ratio=V2 / N if N > 0 else 0.0,
        sichel_s=sichel_s,
        honore_r=honore_r,
        metadata={
            "token_count": N,
            "vocabulary_size": V,
        },
    )
