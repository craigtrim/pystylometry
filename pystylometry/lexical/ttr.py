"""Type-Token Ratio (TTR) analysis using stylometry-ttr package.

This module provides a facade wrapper around the stylometry-ttr package,
maintaining consistent API patterns with other pystylometry metrics.
"""

from .._types import TTRResult


def compute_ttr(text: str, text_id: str | None = None) -> TTRResult:
    """
    Compute Type-Token Ratio (TTR) metrics for vocabulary richness.

    This is a facade wrapper around the stylometry-ttr package that provides
    multiple TTR variants for measuring lexical diversity. TTR measures the
    ratio of unique words (types) to total words (tokens).

    Metrics computed:
    - Raw TTR: unique_words / total_words
    - Root TTR (Guiraud's index): unique_words / sqrt(total_words)
    - Log TTR (Herdan's C): log(unique_words) / log(total_words)
    - STTR: Standardized TTR across fixed-size chunks (reduces length bias)
    - Delta Std: Standard deviation of TTR across chunks (vocabulary consistency)

    References:
        Guiraud, P. (1960). Problèmes et méthodes de la statistique linguistique.
        Herdan, G. (1960). Type-token Mathematics: A Textbook of Mathematical
            Linguistics. Mouton.
        Johnson, W. (1944). Studies in language behavior: I. A program of research.
            Psychological Monographs, 56(2), 1-15.

    Args:
        text: Input text to analyze
        text_id: Optional identifier for the text (for tracking purposes)

    Returns:
        TTRResult with all TTR variants and metadata

    Example:
        >>> result = compute_ttr("The quick brown fox jumps over the lazy dog.")
        >>> print(f"Raw TTR: {result.ttr:.3f}")
        Raw TTR: 0.900
        >>> print(f"Root TTR: {result.root_ttr:.3f}")
        Root TTR: 2.846
        >>> print(f"STTR: {result.sttr:.3f}")
        STTR: 1.000

        >>> # With text identifier
        >>> result = compute_ttr("Sample text here.", text_id="sample-001")
        >>> print(result.metadata["text_id"])
        sample-001
    """
    try:
        from stylometry_ttr import compute_ttr as _compute_ttr
    except ImportError as e:
        raise ImportError(
            "TTR metrics require the stylometry-ttr package. "
            "This should have been installed as a core dependency. "
            "Install with: pip install stylometry-ttr"
        ) from e

    # Call the stylometry-ttr compute_ttr function
    # Note: stylometry-ttr requires text_id to be a string, not None
    ttr_result = _compute_ttr(text, text_id=text_id or "")

    # Convert to our TTRResult dataclass
    # The stylometry-ttr result has attributes we can access
    # Some fields (sttr, delta_std) may be None for short texts
    return TTRResult(
        total_words=ttr_result.total_words,
        unique_words=ttr_result.unique_words,
        ttr=ttr_result.ttr,
        root_ttr=ttr_result.root_ttr,
        log_ttr=ttr_result.log_ttr,
        sttr=ttr_result.sttr if ttr_result.sttr is not None else 0.0,
        delta_std=ttr_result.delta_std if ttr_result.delta_std is not None else 0.0,
        metadata={
            "text_id": text_id or "",
            "source": "stylometry-ttr",
            "sttr_available": ttr_result.sttr is not None,
            "delta_std_available": ttr_result.delta_std is not None,
        },
    )
