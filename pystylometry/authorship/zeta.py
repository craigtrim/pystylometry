"""Zeta score for distinctive word usage in authorship attribution."""

from .._types import ZetaResult
from .._utils import tokenize


def compute_zeta(text1: str, text2: str, segments: int = 10, top_n: int = 50) -> ZetaResult:
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

    Example:
        >>> result = compute_zeta(author1_text, author2_text)
        >>> print(f"Zeta score: {result.zeta_score:.3f}")
        >>> print(f"Marker words: {result.marker_words[:10]}")
        >>> print(f"Anti-markers: {result.anti_marker_words[:10]}")
    """
    # Tokenize texts
    tokens1 = [t.lower() for t in tokenize(text1)]
    tokens2 = [t.lower() for t in tokenize(text2)]

    if len(tokens1) < segments or len(tokens2) < segments:
        return ZetaResult(
            zeta_score=0.0,
            marker_words=[],
            anti_marker_words=[],
            metadata={
                "text1_token_count": len(tokens1),
                "text2_token_count": len(tokens2),
                "segments": segments,
                "top_n": top_n,
                "warning": "Text too short for requested number of segments",
            },
        )

    # Divide texts into segments
    def create_segments(tokens: list[str], n_segments: int) -> list[set[str]]:
        segment_size = len(tokens) // n_segments
        return [set(tokens[i * segment_size : (i + 1) * segment_size]) for i in range(n_segments)]

    segments1 = create_segments(tokens1, segments)
    segments2 = create_segments(tokens2, segments)

    # Get all unique words
    all_words = set(tokens1) | set(tokens2)

    # Calculate document proportion (DP) for each word
    word_scores = {}
    for word in all_words:
        # DP1: proportion of segments in text1 containing the word
        dp1 = sum(1 for seg in segments1 if word in seg) / len(segments1)
        # DP2: proportion of segments in text2 containing the word
        dp2 = sum(1 for seg in segments2 if word in seg) / len(segments2)
        # Zeta score for this word
        word_scores[word] = dp1 - dp2

    # Sort words by zeta score
    sorted_words = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)

    # Extract top marker words (positive zeta) and anti-marker words (negative zeta)
    marker_words = [word for word, score in sorted_words[:top_n] if score > 0]
    anti_marker_words = [word for word, score in sorted_words[-top_n:] if score < 0]
    anti_marker_words.reverse()  # Most negative first

    # Overall zeta score (mean of absolute zeta scores)
    zeta_score = (
        sum(abs(score) for score in word_scores.values()) / len(word_scores) if word_scores else 0.0
    )

    return ZetaResult(
        zeta_score=zeta_score,
        marker_words=marker_words,
        anti_marker_words=anti_marker_words,
        metadata={
            "text1_token_count": len(tokens1),
            "text2_token_count": len(tokens2),
            "segments": segments,
            "top_n": top_n,
            "total_unique_words": len(all_words),
            "marker_word_count": len(marker_words),
            "anti_marker_word_count": len(anti_marker_words),
        },
    )
