"""Zeta score for distinctive word usage in authorship attribution."""

from typing import List
from .._types import ZetaResult
from .._utils import check_optional_dependency, tokenize


def compute_zeta(
    text1: str,
    text2: str,
    segments: int = 10,
    top_n: int = 50
) -> ZetaResult:
    """
    Compute Zeta score for distinctive word usage between two texts or text groups.

    Zeta identifies words that are consistently used in one text/author but not another.

    Algorithm:
    1. Divide each text into segments
    2. Calculate document proportion (DP) for each word:
       - DP₁ = proportion of segments in text1 containing the word
       - DP₂ = proportion of segments in text2 containing the word
    3. Zeta score = DP₁ - DP₂
    4. Positive Zeta = marker words (distinctive of text1)
    5. Negative Zeta = anti-marker words (distinctive of text2)

    References:
        Burrows, J. (2007). All the way through: Testing for authorship in
        different frequency strata. Literary and Linguistic Computing, 22(1), 27-47.

        Craig, H., & Kinney, A. F. (2009). Shakespeare, Computers, and the
        Mystery of Authorship. Cambridge University Press.

    Args:
        text1: First text (candidate author)
        text2: Second text (comparison author/corpus)
        segments: Number of segments to divide each text into (default: 10)
        top_n: Number of top marker/anti-marker words to return (default: 50)

    Returns:
        ZetaResult with zeta score, marker words, and anti-marker words

    Raises:
        ImportError: If scipy is not installed

    Example:
        >>> result = compute_zeta(author1_text, author2_text)
        >>> print(f"Zeta score: {result.zeta_score:.3f}")
        >>> print(f"Marker words: {result.marker_words[:10]}")
        >>> print(f"Anti-markers: {result.anti_marker_words[:10]}")
    """
    check_optional_dependency("scipy", "authorship")

    # TODO: Implement Zeta calculation
    zeta_score = 0.0  # Placeholder
    marker_words: List[str] = []  # Placeholder
    anti_marker_words: List[str] = []  # Placeholder

    return ZetaResult(
        zeta_score=zeta_score,
        marker_words=marker_words,
        anti_marker_words=anti_marker_words,
        metadata={
            "text1_token_count": len(tokenize(text1)),
            "text2_token_count": len(tokenize(text2)),
            "segments": segments,
            "top_n": top_n,
        }
    )
