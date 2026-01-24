"""Additional authorship attribution methods.

This module provides alternative distance/similarity metrics for authorship
attribution beyond Burrows' Delta and Zeta.

Related GitHub Issue:
    #24 - Additional Authorship Attribution Methods
    https://github.com/craigtrim/pystylometry/issues/24

Methods implemented:
    - Kilgarriff's Chi-squared
    - Min-Max (Burrows' original method)
    - John Burrows' Delta variations

References:
    Kilgarriff, A. (2001). Comparing corpora. International Journal of Corpus Linguistics.
    Burrows, J. F. (1992). Not unless you ask nicely. Literary and Linguistic Computing.
    Burrows, J. (2005). Who wrote Shamela? Literary and Linguistic Computing.
"""

from .._types import JohnsBurrowsResult, KilgarriffResult, MinMaxResult


def compute_kilgarriff(text1: str, text2: str, mfw: int = 100) -> KilgarriffResult:
    """
    Compute Kilgarriff's Chi-squared distance between two texts.

    Related GitHub Issue:
        #24 - Additional Authorship Attribution Methods
        https://github.com/craigtrim/pystylometry/issues/24

    Args:
        text1: First text for comparison
        text2: Second text for comparison
        mfw: Number of most frequent words to analyze

    Returns:
        KilgarriffResult with chi-squared statistic, p-value, and
        most distinctive features.
    """
    # TODO: Implement Kilgarriff's chi-squared
    # GitHub Issue #24: https://github.com/craigtrim/pystylometry/issues/24
    raise NotImplementedError(
        "Kilgarriff's chi-squared not yet implemented. "
        "See GitHub Issue #24: https://github.com/craigtrim/pystylometry/issues/24"
    )


def compute_minmax(text1: str, text2: str, mfw: int = 100) -> MinMaxResult:
    """
    Compute Min-Max distance (Burrows' original method).

    Related GitHub Issue:
        #24 - Additional Authorship Attribution Methods
        https://github.com/craigtrim/pystylometry/issues/24

    Args:
        text1: First text for comparison
        text2: Second text for comparison
        mfw: Number of most frequent words to analyze

    Returns:
        MinMaxResult with min-max distance and distinctive features.
    """
    # TODO: Implement Min-Max distance
    # GitHub Issue #24: https://github.com/craigtrim/pystylometry/issues/24
    raise NotImplementedError(
        "Min-Max distance not yet implemented. "
        "See GitHub Issue #24: https://github.com/craigtrim/pystylometry/issues/24"
    )


def compute_johns_delta(
    text1: str,
    text2: str,
    mfw: int = 100,
    method: str = "quadratic",
) -> JohnsBurrowsResult:
    """
    Compute John Burrows' Delta variations.

    Related GitHub Issue:
        #24 - Additional Authorship Attribution Methods
        https://github.com/craigtrim/pystylometry/issues/24

    Args:
        text1: First text for comparison
        text2: Second text for comparison
        mfw: Number of most frequent words to analyze
        method: Delta variation ("quadratic", "weighted", "rotated")

    Returns:
        JohnsBurrowsResult with delta score and method details.
    """
    # TODO: Implement John's Delta variations
    # GitHub Issue #24: https://github.com/craigtrim/pystylometry/issues/24
    raise NotImplementedError(
        "John's Delta variations not yet implemented. "
        "See GitHub Issue #24: https://github.com/craigtrim/pystylometry/issues/24"
    )
