"""Burrows' Delta and Cosine Delta for authorship attribution."""

from typing import List
from .._types import BurrowsDeltaResult
from .._utils import check_optional_dependency, tokenize


def compute_burrows_delta(
    text1: str,
    text2: str,
    mfw: int = 500,
    distance_type: str = "burrows"
) -> BurrowsDeltaResult:
    """
    Compute Burrows' Delta or Cosine Delta between two texts.

    Burrows' Delta:
        Delta = mean(|z₁(f) - z₂(f)|) for all features f
        where z(f) = (frequency(f) - mean(f)) / std(f)

    Cosine Delta:
        Delta = 1 - cos(z₁, z₂)
        Measures angular distance between z-score vectors

    Both methods:
    1. Extract most frequent words (MFW) across both texts
    2. Calculate word frequencies in each text
    3. Z-score normalize frequencies
    4. Compute distance measure

    Lower scores indicate more similar texts (likely same author).

    References:
        Burrows, J. (2002). 'Delta': A measure of stylistic difference and
        a guide to likely authorship. Literary and Linguistic Computing, 17(3), 267-287.

        Argamon, S. (2008). Interpreting Burrows's Delta: Geometric and
        probabilistic foundations. Literary and Linguistic Computing, 23(2), 131-147.

    Args:
        text1: First text to compare
        text2: Second text to compare
        mfw: Number of most frequent words to use (default: 500)
        distance_type: "burrows", "cosine", or "eder" (default: "burrows")

    Returns:
        BurrowsDeltaResult with delta score and metadata

    Raises:
        ImportError: If scikit-learn or scipy is not installed

    Example:
        >>> result = compute_burrows_delta(text1, text2, mfw=300)
        >>> print(f"Delta score: {result.delta_score:.3f}")
        >>> print(f"Lower is more similar")
    """
    check_optional_dependency("sklearn", "authorship")
    check_optional_dependency("scipy", "authorship")

    # TODO: Implement Burrows' Delta calculation
    # from collections import Counter
    # from scipy import stats
    # from sklearn.metrics.pairwise import cosine_similarity

    delta_score = 0.0  # Placeholder

    return BurrowsDeltaResult(
        delta_score=delta_score,
        distance_type=distance_type,
        mfw_count=mfw,
        metadata={
            "text1_token_count": len(tokenize(text1)),
            "text2_token_count": len(tokenize(text2)),
        }
    )


def compute_cosine_delta(text1: str, text2: str, mfw: int = 500) -> BurrowsDeltaResult:
    """
    Compute Cosine Delta between two texts.

    Convenience function that calls compute_burrows_delta with distance_type="cosine".

    Args:
        text1: First text to compare
        text2: Second text to compare
        mfw: Number of most frequent words to use (default: 500)

    Returns:
        BurrowsDeltaResult with cosine delta score

    Example:
        >>> result = compute_cosine_delta(text1, text2)
        >>> print(f"Cosine Delta: {result.delta_score:.3f}")
    """
    return compute_burrows_delta(text1, text2, mfw=mfw, distance_type="cosine")
