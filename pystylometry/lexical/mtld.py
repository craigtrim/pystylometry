"""MTLD (Measure of Textual Lexical Diversity) implementation."""

from .._types import MTLDResult
from .._utils import tokenize


def _calculate_mtld_direction(tokens: list[str], threshold: float, forward: bool) -> float:
    """
    Calculate MTLD in one direction (forward or backward).

    Args:
        tokens: List of tokens to analyze
        threshold: TTR threshold to maintain (must be in range (0, 1))
        forward: If True, process forward; if False, process backward

    Returns:
        MTLD score for this direction
    """
    if len(tokens) == 0:
        return 0.0

    # Process tokens in the specified direction
    token_list = tokens if forward else tokens[::-1]

    factors = 0.0
    current_count = 0
    current_types = set()

    for token in token_list:
        current_count += 1
        current_types.add(token)

        # Calculate current TTR
        ttr = len(current_types) / current_count

        # If TTR drops below threshold, we've completed a factor
        if ttr < threshold:
            factors += 1.0
            current_count = 0
            current_types = set()

    # Handle remaining partial factor
    # Add proportion of a complete factor based on how close we are to threshold
    if current_count > 0:
        ttr = len(current_types) / current_count
        # If we're still above threshold, add partial factor credit
        # Formula: (1 - current_ttr) / (1 - threshold)
        # This represents how far we've progressed toward completing a factor
        # In theory, ttr should always be >= threshold here because drops below
        # threshold are handled in the loop above (which resets current_count).
        # Adding defensive check to prevent mathematical errors.
        if ttr >= threshold:
            factors += (1.0 - ttr) / (1.0 - threshold)

    # MTLD is the mean length of factors
    # Total tokens / number of factors
    if factors > 0:
        return len(tokens) / factors
    else:
        # If no factors were completed, return the text length
        # This happens when TTR stays above threshold for the entire text
        return float(len(tokens))


def compute_mtld(
    text: str,
    threshold: float = 0.72,
) -> MTLDResult:
    """
    Compute MTLD (Measure of Textual Lexical Diversity).

    MTLD measures the mean length of sequential word strings that maintain
    a minimum threshold TTR. It's more robust than simple TTR for texts of
    varying lengths.

    Formula:
        MTLD = total_tokens / factor_count
        where factor_count includes:
        - Completed factors (segments where TTR dropped below threshold)
        - Partial factor for any remaining incomplete segment (weighted by proximity to threshold)

    References:
        McCarthy, P. M., & Jarvis, S. (2010). MTLD, vocd-D, and HD-D:
        A validation study of sophisticated approaches to lexical diversity assessment.
        Behavior Research Methods, 42(2), 381-392.

    Args:
        text: Input text to analyze
        threshold: TTR threshold to maintain (default: 0.72, must be in range (0, 1))

    Returns:
        MTLDResult with forward, backward, and average MTLD scores

    Raises:
        ValueError: If threshold is not in range (0, 1)

    Example:
        >>> result = compute_mtld("The quick brown fox jumps over the lazy dog...")
        >>> print(f"MTLD: {result.mtld_average:.2f}")
    """
    # Validate threshold parameter
    if not (0 < threshold < 1):
        raise ValueError(
            f"Threshold must be in range (0, 1), got {threshold}. "
            "Common values: 0.72 (default), 0.5-0.8"
        )

    # Case-insensitive tokenization for consistency with other lexical metrics
    # (compute_yule, compute_hapax_ratios both use text.lower())
    tokens = tokenize(text.lower())

    if len(tokens) == 0:
        return MTLDResult(
            mtld_forward=0.0,
            mtld_backward=0.0,
            mtld_average=0.0,
            metadata={"token_count": 0, "threshold": threshold},
        )

    # Calculate MTLD in forward direction
    mtld_forward = _calculate_mtld_direction(tokens, threshold, forward=True)

    # Calculate MTLD in backward direction
    mtld_backward = _calculate_mtld_direction(tokens, threshold, forward=False)

    # Average of forward and backward
    mtld_average = (mtld_forward + mtld_backward) / 2

    return MTLDResult(
        mtld_forward=mtld_forward,
        mtld_backward=mtld_backward,
        mtld_average=mtld_average,
        metadata={
            "token_count": len(tokens),
            "threshold": threshold,
        },
    )
