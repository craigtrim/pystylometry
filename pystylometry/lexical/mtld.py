"""MTLD (Measure of Textual Lexical Diversity) implementation.

This module implements MTLD with native chunked analysis for stylometric
fingerprinting.

Related GitHub Issue:
    #27 - Native chunked analysis with Distribution dataclass
    https://github.com/craigtrim/pystylometry/issues/27
"""

import math

from .._types import Distribution, MTLDResult, chunk_text, make_distribution
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


def _compute_mtld_single(text: str, threshold: float) -> tuple[float, float, float, dict]:
    """Compute MTLD for a single chunk of text.

    Returns:
        Tuple of (mtld_forward, mtld_backward, mtld_average, metadata_dict).
        Returns (nan, nan, nan, metadata) for empty input.
    """
    tokens = tokenize(text.lower())

    if len(tokens) == 0:
        return (
            float("nan"),
            float("nan"),
            float("nan"),
            {"token_count": 0},
        )

    mtld_forward = _calculate_mtld_direction(tokens, threshold, forward=True)
    mtld_backward = _calculate_mtld_direction(tokens, threshold, forward=False)
    mtld_average = (mtld_forward + mtld_backward) / 2

    return (
        mtld_forward,
        mtld_backward,
        mtld_average,
        {"token_count": len(tokens)},
    )


def compute_mtld(
    text: str,
    threshold: float = 0.72,
    chunk_size: int = 1000,
) -> MTLDResult:
    """
    Compute MTLD (Measure of Textual Lexical Diversity).

    This function uses native chunked analysis to capture variance and patterns
    across the text, which is essential for stylometric fingerprinting.

    MTLD measures the mean length of sequential word strings that maintain
    a minimum threshold TTR. It's more robust than simple TTR for texts of
    varying lengths.

    Formula:
        MTLD = total_tokens / factor_count
        where factor_count includes:
        - Completed factors (segments where TTR dropped below threshold)
        - Partial factor for any remaining incomplete segment (weighted by proximity to threshold)

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27

    References:
        McCarthy, P. M., & Jarvis, S. (2010). MTLD, vocd-D, and HD-D:
        A validation study of sophisticated approaches to lexical diversity assessment.
        Behavior Research Methods, 42(2), 381-392.

    Args:
        text: Input text to analyze
        threshold: TTR threshold to maintain (default: 0.72, must be in range (0, 1))
        chunk_size: Number of words per chunk (default: 1000)

    Returns:
        MTLDResult with forward, backward, average MTLD scores and distributions

    Raises:
        ValueError: If threshold is not in range (0, 1)

    Example:
        >>> result = compute_mtld("Long text here...", chunk_size=1000)
        >>> result.mtld_average  # Mean across chunks
        72.5
        >>> result.mtld_average_dist.std  # Variance reveals fingerprint
        8.3
    """
    # Validate threshold parameter
    if not (0 < threshold < 1):
        raise ValueError(
            f"Threshold must be in range (0, 1), got {threshold}. "
            "Common values: 0.72 (default), 0.5-0.8"
        )

    # Chunk the text
    chunks = chunk_text(text, chunk_size)

    # Compute metrics per chunk
    forward_values = []
    backward_values = []
    average_values = []
    total_tokens = 0

    for chunk in chunks:
        fwd, bwd, avg, meta = _compute_mtld_single(chunk, threshold)
        if not math.isnan(fwd):
            forward_values.append(fwd)
            backward_values.append(bwd)
            average_values.append(avg)
        total_tokens += meta.get("token_count", 0)

    # Handle empty or all-invalid chunks
    if not forward_values:
        empty_dist = Distribution(
            values=[],
            mean=float("nan"),
            median=float("nan"),
            std=0.0,
            range=0.0,
            iqr=0.0,
        )
        return MTLDResult(
            mtld_forward=float("nan"),
            mtld_backward=float("nan"),
            mtld_average=float("nan"),
            mtld_forward_dist=empty_dist,
            mtld_backward_dist=empty_dist,
            mtld_average_dist=empty_dist,
            chunk_size=chunk_size,
            chunk_count=len(chunks),
            metadata={
                "total_token_count": 0,
                "threshold": threshold,
            },
        )

    # Build distributions
    forward_dist = make_distribution(forward_values)
    backward_dist = make_distribution(backward_values)
    average_dist = make_distribution(average_values)

    return MTLDResult(
        mtld_forward=forward_dist.mean,
        mtld_backward=backward_dist.mean,
        mtld_average=average_dist.mean,
        mtld_forward_dist=forward_dist,
        mtld_backward_dist=backward_dist,
        mtld_average_dist=average_dist,
        chunk_size=chunk_size,
        chunk_count=len(chunks),
        metadata={
            "total_token_count": total_tokens,
            "threshold": threshold,
        },
    )
