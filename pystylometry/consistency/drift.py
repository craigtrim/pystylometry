"""Kilgarriff chi-squared drift detection for intra-document stylistic analysis.

This module implements drift detection within a single document by applying
Kilgarriff's chi-squared method to sequential chunks of text. It enables
detection of stylistic inconsistencies, AI-generated content signatures,
multi-author documents, and pasted/edited content.

Related GitHub Issues:
    #36 - Kilgarriff Chi-Squared drift detection for intra-document analysis
    https://github.com/craigtrim/pystylometry/issues/36
    #31 - Classical Stylometric Methods from Programming Historian
    https://github.com/craigtrim/pystylometry/issues/31
    #27 - Native chunked analysis with Distribution dataclass
    https://github.com/craigtrim/pystylometry/issues/27

Core Concept:
    By comparing sequential chunks of a single document, we can measure
    **internal stylistic consistency**. Human writing typically shows natural
    variation in chi-squared scores between chunks. AI-generated text often
    shows either suspicious uniformity or periodic resets.

Pattern Signatures:
    The function classifies detected patterns into named categories:

    - consistent: Low, stable χ² across pairs
        → Natural human writing with normal variation
        → Well-edited, single-author text

    - gradual_drift: Slowly increasing χ² trend
        → Author fatigue (style degrades over time)
        → Topic evolution affecting vocabulary
        → Editing that becomes progressively heavier

    - sudden_spike: One or more pairs have abnormally high χ²
        → Pasted content from different source
        → Different author wrote a section
        → Heavy editing in one region

    - suspiciously_uniform: Near-zero variance in χ² scores
        → Possible AI generation (too consistent)
        → Text generated in single session without revision
        → Copy-pasted repetitive content

    - unknown: Insufficient data for classification
        → Text too short (fewer than MIN_WINDOWS chunks)

Sliding Window Support:
    The function supports overlapping windows via the `stride` parameter:
    - stride == window_size: Non-overlapping chunks (original behavior)
    - stride < window_size: Overlapping windows (smoother drift curve)
    - stride > window_size: Gaps between windows (sparse sampling)

    50% overlap (stride = window_size / 2) is recommended for smooth detection.

Marketing Name: "Style Drift Detector" / "Consistency Fingerprint"

References:
    Kilgarriff, Adam. "Comparing Corpora." International Journal of Corpus
        Linguistics, vol. 6, no. 1, 2001, pp. 97-133.
        doi: 10.1075/ijcl.6.1.05kil

    Eder, Maciej. "Does Size Matter? Authorship Attribution, Small Samples,
        Big Problem." Digital Scholarship in the Humanities, vol. 30, no. 2,
        2015, pp. 167-182.

    Juola, Patrick. "Authorship Attribution." Foundations and Trends in
        Information Retrieval, vol. 1, no. 3, 2006, pp. 233-334.
"""

from __future__ import annotations

import statistics
from typing import Any

from .._types import KilgarriffDriftResult
from .._utils import tokenize
from ..authorship.kilgarriff import _kilgarriff_core
from ._thresholds import (
    CONFIDENCE_MIN_WINDOWS,
    MARGINAL_DATA_MAX_CONFIDENCE,
    MIN_WINDOWS,
    RECOMMENDED_WINDOWS,
    SPIKE_MIN_ABSOLUTE,
    SPIKE_RATIO,
    TREND_R_SQUARED_THRESHOLD,
    TREND_SLOPE_THRESHOLD,
    UNIFORM_CV_THRESHOLD,
    UNIFORM_MEAN_THRESHOLD,
    get_all_thresholds,
)


def _create_sliding_windows(
    tokens: list[str],
    window_size: int,
    stride: int,
) -> list[list[str]]:
    """
    Create sliding windows over a token list.

    This function implements the sliding window mechanism for drift detection.
    Windows can overlap (stride < window_size), be non-overlapping
    (stride == window_size), or have gaps (stride > window_size).

    Related GitHub Issue:
        #36 - Sliding window support for drift detection
        https://github.com/craigtrim/pystylometry/issues/36

    Args:
        tokens: List of tokens to window over
        window_size: Number of tokens per window
        stride: Number of tokens to advance between windows

    Returns:
        List of token lists, each representing one window

    Example:
        >>> tokens = ["a", "b", "c", "d", "e", "f", "g", "h"]
        >>> windows = _create_sliding_windows(tokens, window_size=4, stride=2)
        >>> # windows[0] = ["a", "b", "c", "d"]
        >>> # windows[1] = ["c", "d", "e", "f"]
        >>> # windows[2] = ["e", "f", "g", "h"]
    """
    if stride <= 0:
        raise ValueError(f"stride must be positive, got {stride}")
    if window_size <= 0:
        raise ValueError(f"window_size must be positive, got {window_size}")

    windows = []
    start = 0

    while start + window_size <= len(tokens):
        window = tokens[start : start + window_size]
        windows.append(window)
        start += stride

    # Handle final partial window if text doesn't divide evenly
    # Only include if it has at least 50% of window_size tokens
    if start < len(tokens):
        final_window = tokens[start:]
        if len(final_window) >= window_size * 0.5:
            windows.append(final_window)

    return windows


def _compute_trend(values: list[float]) -> tuple[float, float]:
    """
    Compute linear regression slope and R-squared for trend detection.

    Uses simple linear regression to detect whether chi-squared values
    are increasing or decreasing over the document.

    Related GitHub Issue:
        #36 - Gradual drift pattern detection
        https://github.com/craigtrim/pystylometry/issues/36

    Args:
        values: List of chi-squared values in order

    Returns:
        Tuple of (slope, r_squared)
        - slope: Chi-squared units per comparison (positive = increasing)
        - r_squared: Coefficient of determination (0-1, higher = better fit)

    Example:
        >>> values = [10.0, 15.0, 20.0, 25.0, 30.0]  # Linear increase
        >>> slope, r_sq = _compute_trend(values)
        >>> # slope ≈ 5.0, r_sq ≈ 1.0
    """
    if len(values) < 2:
        return 0.0, 0.0

    n = len(values)
    x = list(range(n))  # 0, 1, 2, ...

    # Means
    mean_x = sum(x) / n
    mean_y = sum(values) / n

    # Covariance and variance
    cov_xy = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, values))
    var_x = sum((xi - mean_x) ** 2 for xi in x)
    var_y = sum((yi - mean_y) ** 2 for yi in values)

    # Slope
    if var_x == 0:
        return 0.0, 0.0
    slope = cov_xy / var_x

    # R-squared
    if var_y == 0:
        r_squared = 1.0 if slope == 0 else 0.0
    else:
        # R² = (explained variance) / (total variance)
        ss_res = sum((yi - (mean_y + slope * (xi - mean_x))) ** 2 for xi, yi in zip(x, values))
        ss_tot = var_y * n
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    return slope, max(0.0, min(1.0, r_squared))


def _classify_pattern(
    mean_chi: float,
    std_chi: float,
    max_chi: float,
    min_chi: float,
    trend_slope: float,
    trend_r_squared: float,
    window_count: int,
) -> tuple[str, float]:
    """
    Classify the detected pattern and compute confidence score.

    This function implements the pattern classification logic described in
    _thresholds.py. It uses a decision tree approach, checking for each
    pattern in order of specificity.

    Related GitHub Issue:
        #36 - Pattern classification for drift detection
        https://github.com/craigtrim/pystylometry/issues/36

    Decision Order:
        1. Suspiciously uniform (near-zero variance)
        2. Sudden spike (outlier max value)
        3. Gradual drift (significant trend)
        4. Consistent (default)

    Args:
        mean_chi: Mean chi-squared across comparisons
        std_chi: Standard deviation of chi-squared values
        max_chi: Maximum chi-squared value
        min_chi: Minimum chi-squared value
        trend_slope: Linear regression slope
        trend_r_squared: R-squared of trend fit
        window_count: Number of windows analyzed

    Returns:
        Tuple of (pattern_name, confidence)
        - pattern_name: One of "consistent", "gradual_drift", "sudden_spike",
                        "suspiciously_uniform", "unknown"
        - confidence: 0.0-1.0 confidence in the classification

    Note:
        Confidence is scaled down for marginal data (few windows).
    """
    # Base confidence scales with window count
    if window_count < MIN_WINDOWS:
        return "unknown", 0.0

    base_confidence = min(1.0, window_count / CONFIDENCE_MIN_WINDOWS)
    if window_count < RECOMMENDED_WINDOWS:
        base_confidence = min(base_confidence, MARGINAL_DATA_MAX_CONFIDENCE)

    # Handle edge case of zero mean
    if mean_chi == 0:
        return "consistent", base_confidence

    # Coefficient of variation
    cv = std_chi / mean_chi if mean_chi > 0 else 0.0

    # 1. Check for suspiciously uniform (AI signature)
    # Very low variance with low mean suggests artificial consistency
    if cv < UNIFORM_CV_THRESHOLD and mean_chi < UNIFORM_MEAN_THRESHOLD:
        # Confidence increases as CV decreases
        uniformity_strength = 1 - (cv / UNIFORM_CV_THRESHOLD)
        confidence = base_confidence * (0.6 + 0.4 * uniformity_strength)
        return "suspiciously_uniform", confidence

    # 2. Check for sudden spike (discontinuity)
    # Max significantly exceeds mean, indicating an outlier
    spike_ratio = max_chi / mean_chi if mean_chi > 0 else 0.0
    if spike_ratio > SPIKE_RATIO and max_chi > SPIKE_MIN_ABSOLUTE:
        # Confidence based on how extreme the spike is
        spike_strength = min(1.0, (spike_ratio - SPIKE_RATIO) / SPIKE_RATIO)
        confidence = base_confidence * (0.7 + 0.3 * spike_strength)
        return "sudden_spike", confidence

    # 3. Check for gradual drift (trend)
    # Significant slope with reasonable R-squared
    if abs(trend_slope) > TREND_SLOPE_THRESHOLD and trend_r_squared > TREND_R_SQUARED_THRESHOLD:
        # Confidence based on R-squared (how well trend explains variance)
        confidence = base_confidence * (0.5 + 0.5 * trend_r_squared)
        return "gradual_drift", confidence

    # 4. Default: consistent (natural human variation)
    # Moderate variance, no extreme patterns
    confidence = base_confidence * 0.8  # Slightly lower confidence for "normal"
    return "consistent", confidence


def compute_kilgarriff_drift(
    text: str,
    window_size: int = 1000,
    stride: int = 500,
    comparison_mode: str = "sequential",
    lag: int = 1,
    n_words: int = 500,
) -> KilgarriffDriftResult:
    """
    Detect stylistic drift within a single document using Kilgarriff's chi-squared.

    This function chunks a single text and computes chi-squared distances between
    sequential (or all) chunk pairs to measure internal stylistic consistency.
    It classifies the detected pattern and returns detailed metrics for analysis.

    Related GitHub Issues:
        #36 - Kilgarriff Chi-Squared drift detection for intra-document analysis
        https://github.com/craigtrim/pystylometry/issues/36
        #31 - Classical Stylometric Methods from Programming Historian
        https://github.com/craigtrim/pystylometry/issues/31

    Marketing Name: "Style Drift Detector" / "Consistency Fingerprint"

    Pattern Signatures:
        - consistent: Low, stable χ² across pairs (natural human writing)
        - gradual_drift: Slowly increasing trend (author fatigue, topic shift)
        - sudden_spike: One pair has high χ² (pasted content, different author)
        - suspiciously_uniform: Near-zero variance (possible AI generation)

    Algorithm:
        1. Tokenize text and create sliding windows
        2. For each window pair (based on comparison_mode):
           a. Compute chi-squared using Kilgarriff's method
           b. Record contributing words
        3. Compute holistic metrics (mean, std, max, trend)
        4. Classify pattern based on thresholds
        5. Return detailed result with all metrics

    References:
        Kilgarriff, Adam. "Comparing Corpora." International Journal of Corpus
            Linguistics, vol. 6, no. 1, 2001, pp. 97-133.

    Args:
        text: Input text to analyze for stylistic drift
        window_size: Number of words per analysis window (default: 1000).
            Larger windows provide more stable chi-squared but fewer comparisons.
        stride: Number of words to advance between windows (default: 500).
            - stride == window_size: Non-overlapping chunks
            - stride < window_size: Overlapping windows (smoother detection)
            - stride > window_size: Gaps between windows (sparse sampling)
        comparison_mode: How to compare windows (default: "sequential")
            - "sequential": Compare adjacent windows only (1-2, 2-3, 3-4)
            - "all_pairs": Compare every window pair (produces distance matrix)
            - "fixed_lag": Compare windows at fixed distance (e.g., 1-3, 2-4)
        lag: Window distance for fixed_lag mode (default: 1, ignored otherwise)
        n_words: Top N most frequent words for chi-squared (default: 500)

    Returns:
        KilgarriffDriftResult containing:
            - status: "success", "marginal_data", or "insufficient_data"
            - pattern: Classified pattern name
            - pattern_confidence: 0.0-1.0 confidence score
            - mean_chi_squared, std_chi_squared, max_chi_squared: Statistics
            - trend: Slope of chi-squared over document
            - pairwise_scores: Detailed per-pair data
            - And more (see KilgarriffDriftResult docstring)

    Raises:
        ValueError: If stride is 0 or negative

    Example:
        >>> # Basic usage
        >>> result = compute_kilgarriff_drift(long_text)
        >>> print(f"Pattern: {result.pattern}")
        >>> print(f"Confidence: {result.pattern_confidence:.2f}")

        >>> # Custom sliding window
        >>> result = compute_kilgarriff_drift(
        ...     text,
        ...     window_size=2000,  # Larger windows
        ...     stride=1000,       # 50% overlap
        ... )

        >>> # Check for AI-generated content
        >>> if result.pattern == "suspiciously_uniform":
        ...     print("Warning: Text may be AI-generated")

        >>> # Handle insufficient data gracefully
        >>> if result.status == "insufficient_data":
        ...     print(result.status_message)
    """
    # Input validation
    if stride <= 0:
        raise ValueError(f"stride must be positive, got {stride}")
    if window_size <= 0:
        raise ValueError(f"window_size must be positive, got {window_size}")
    valid_modes = ("sequential", "all_pairs", "fixed_lag")
    if comparison_mode not in valid_modes:
        raise ValueError(f"comparison_mode must be one of {valid_modes}, got '{comparison_mode}'")

    # Tokenize text
    tokens = [t.lower() for t in tokenize(text) if t.isalpha()]

    # Create sliding windows
    windows = _create_sliding_windows(tokens, window_size, stride)
    window_count = len(windows)

    # Compute overlap ratio for metadata
    overlap_ratio = max(0.0, 1 - (stride / window_size))

    # Get thresholds for transparency
    thresholds = get_all_thresholds()

    # Check for insufficient data
    if window_count < MIN_WINDOWS:
        return KilgarriffDriftResult(
            status="insufficient_data",
            status_message=(
                f"Text produced {window_count} windows; minimum {MIN_WINDOWS} required. "
                f"Need approximately {window_size + (MIN_WINDOWS - 1) * stride} words."
            ),
            pattern="unknown",
            pattern_confidence=0.0,
            mean_chi_squared=float("nan"),
            std_chi_squared=float("nan"),
            max_chi_squared=float("nan"),
            min_chi_squared=float("nan"),
            max_location=-1,
            trend=float("nan"),
            pairwise_scores=[],
            window_size=window_size,
            stride=stride,
            overlap_ratio=overlap_ratio,
            comparison_mode=comparison_mode,
            window_count=window_count,
            distance_matrix=None,
            thresholds=thresholds,
            metadata={
                "total_tokens": len(tokens),
                "tokens_per_window": [len(w) for w in windows],
            },
        )

    # Determine which pairs to compare based on mode
    pairs_to_compare: list[tuple[int, int]] = []

    if comparison_mode == "sequential":
        # Compare adjacent windows: (0,1), (1,2), (2,3), ...
        pairs_to_compare = [(i, i + 1) for i in range(window_count - 1)]

    elif comparison_mode == "all_pairs":
        # Compare all window pairs: (0,1), (0,2), ..., (n-2,n-1)
        pairs_to_compare = [(i, j) for i in range(window_count) for j in range(i + 1, window_count)]

    elif comparison_mode == "fixed_lag":
        # Compare windows at fixed lag distance: (0,lag), (1,lag+1), ...
        pairs_to_compare = [
            (i, i + lag) for i in range(window_count - lag) if i + lag < window_count
        ]

    # Compute chi-squared for each pair
    pairwise_scores: list[dict[str, Any]] = []
    chi_squared_values: list[float] = []

    for i, j in pairs_to_compare:
        chi_sq, df, contributions, details = _kilgarriff_core(
            windows[i], windows[j], n_words=n_words
        )

        pairwise_scores.append(
            {
                "chunk_pair": (i, j),
                "chi_squared": chi_sq,
                "degrees_of_freedom": df,
                "top_words": contributions[:10],  # Top 10 contributing words
                "window_i_size": len(windows[i]),
                "window_j_size": len(windows[j]),
            }
        )
        chi_squared_values.append(chi_sq)

    # Build distance matrix for all_pairs mode
    distance_matrix: list[list[float]] | None = None
    if comparison_mode == "all_pairs":
        distance_matrix = [[0.0] * window_count for _ in range(window_count)]
        for score in pairwise_scores:
            i, j = score["chunk_pair"]
            distance_matrix[i][j] = score["chi_squared"]
            distance_matrix[j][i] = score["chi_squared"]  # Symmetric

    # Compute holistic statistics
    if chi_squared_values:
        mean_chi = statistics.mean(chi_squared_values)
        std_chi = statistics.stdev(chi_squared_values) if len(chi_squared_values) > 1 else 0.0
        max_chi = max(chi_squared_values)
        min_chi = min(chi_squared_values)
        max_location = chi_squared_values.index(max_chi)
    else:
        mean_chi = std_chi = max_chi = min_chi = float("nan")
        max_location = -1

    # Compute trend (only meaningful for sequential comparisons)
    if comparison_mode == "sequential" and len(chi_squared_values) >= 2:
        trend_slope, trend_r_squared = _compute_trend(chi_squared_values)
    else:
        trend_slope = 0.0
        trend_r_squared = 0.0

    # Classify pattern
    pattern, pattern_confidence = _classify_pattern(
        mean_chi=mean_chi,
        std_chi=std_chi,
        max_chi=max_chi,
        min_chi=min_chi,
        trend_slope=trend_slope,
        trend_r_squared=trend_r_squared,
        window_count=window_count,
    )

    # Determine status
    if window_count >= RECOMMENDED_WINDOWS:
        status = "success"
        status_message = f"Analyzed {window_count} windows with {len(pairwise_scores)} comparisons."
    else:
        status = "marginal_data"
        status_message = (
            f"Analyzed {window_count} windows; {RECOMMENDED_WINDOWS}+ recommended "
            f"for reliable pattern classification."
        )

    return KilgarriffDriftResult(
        status=status,
        status_message=status_message,
        pattern=pattern,
        pattern_confidence=pattern_confidence,
        mean_chi_squared=mean_chi,
        std_chi_squared=std_chi,
        max_chi_squared=max_chi,
        min_chi_squared=min_chi,
        max_location=max_location,
        trend=trend_slope,
        pairwise_scores=pairwise_scores,
        window_size=window_size,
        stride=stride,
        overlap_ratio=overlap_ratio,
        comparison_mode=comparison_mode,
        window_count=window_count,
        distance_matrix=distance_matrix,
        thresholds=thresholds,
        metadata={
            "total_tokens": len(tokens),
            "tokens_per_window": [len(w) for w in windows],
            "comparisons_made": len(pairwise_scores),
            "trend_r_squared": trend_r_squared,
            "n_words_used": n_words,
            "method": "kilgarriff_drift_2001",
        },
    )
