"""Threshold constants for consistency pattern classification.

This module contains calibration constants used for classifying stylistic
patterns in the consistency module. These thresholds determine how the
`compute_kilgarriff_drift()` function classifies detected patterns.

Related GitHub Issues:
    #36 - Kilgarriff Chi-Squared drift detection for intra-document analysis
    https://github.com/craigtrim/pystylometry/issues/36

Calibration Notes:
    These thresholds are initial estimates based on theoretical considerations
    and limited empirical testing. They should be refined through systematic
    evaluation on diverse corpora including:
    - Human-written texts of various lengths and genres
    - AI-generated texts from different models
    - Mixed human/AI texts
    - Multi-author documents

    The thresholds are exposed as module-level constants to allow:
    1. Transparency: Users can inspect what values are used
    2. Customization: Advanced users can override via metadata or subclassing
    3. Research: Easy adjustment for empirical calibration studies

Pattern Classification Logic:
    The pattern classification uses a decision tree approach:

    1. First check for insufficient variance (suspiciously uniform)
       - AI-generated text often shows near-identical statistics across chunks
       - This is detected by very low std_chi_squared

    2. Then check for sudden discontinuities (sudden spike)
       - Pasted content or different authors cause outlier chi-squared values
       - Detected by max_chi_squared significantly exceeding mean

    3. Then check for trends (gradual drift)
       - Author fatigue or topic evolution shows increasing chi-squared
       - Detected by significant slope in chi-squared over time

    4. Otherwise classify as consistent (natural variation)
       - Human writing typically shows moderate, stable variance

References:
    The thresholds are informed by stylometric literature but require
    empirical validation:

    Eder, Maciej, et al. "Stylometry with R: A Package for Computational Text
        Analysis." The R Journal, vol. 8, no. 1, 2016, pp. 107-121.

    Juola, Patrick. "Authorship Attribution." Foundations and Trends in
        Information Retrieval, vol. 1, no. 3, 2006, pp. 233-334.
"""

from __future__ import annotations

# =============================================================================
# Window Count Thresholds
# =============================================================================
# These determine the minimum data requirements for meaningful analysis.

# Absolute minimum: Need at least 2 comparisons for any variance calculation
# With 3 windows, we get pairs: (1,2), (2,3) = 2 comparisons
MIN_WINDOWS = 3

# Recommended minimum: Need enough data points for reliable pattern classification
# With 5 windows, we get pairs: (1,2), (2,3), (3,4), (4,5) = 4 comparisons
# This allows computation of mean, std, and basic trend detection
RECOMMENDED_WINDOWS = 5


# =============================================================================
# Pattern Classification Thresholds
# =============================================================================
# These control how chi-squared patterns are classified into named patterns.

# --- Suspiciously Uniform Detection ---
# AI-generated text often shows near-zero variance in stylistic metrics.
# Human writing naturally fluctuates; AI maintains eerie consistency.

# Coefficient of variation threshold (std / mean)
# Below this, variance is suspiciously low
UNIFORM_CV_THRESHOLD = 0.15

# Also require low absolute mean for "uniform" classification
# (High mean with low variance is just "consistent" with high baseline)
UNIFORM_MEAN_THRESHOLD = 50.0


# --- Sudden Spike Detection ---
# Pasted content, different authors, or major edits cause discontinuities.

# Ratio of max to mean that indicates a spike
# If max > SPIKE_RATIO × mean, we have an outlier
SPIKE_RATIO = 2.5

# Absolute minimum spike size (to avoid false positives on low-baseline texts)
SPIKE_MIN_ABSOLUTE = 100.0


# --- Gradual Drift Detection ---
# Increasing chi-squared over time suggests evolving style or author fatigue.

# Minimum slope (chi-squared units per chunk pair) to detect trend
# Positive = increasing difference over time
# Negative = converging style (less common)
TREND_SLOPE_THRESHOLD = 5.0

# R-squared threshold: Trend must explain this much variance to be meaningful
TREND_R_SQUARED_THRESHOLD = 0.3


# --- Consistent Pattern ---
# If none of the above patterns are detected, text is classified as "consistent"
# This represents natural human writing with normal variation.


# =============================================================================
# Confidence Calculation Weights
# =============================================================================
# These control how pattern confidence scores are computed.

# Minimum window count for full confidence
# Below this, confidence is scaled down proportionally
CONFIDENCE_MIN_WINDOWS = 5

# Maximum confidence achievable with marginal data
MARGINAL_DATA_MAX_CONFIDENCE = 0.6


# =============================================================================
# Export all thresholds as a dict for easy inspection
# =============================================================================


def get_all_thresholds() -> dict[str, float]:
    """
    Return all threshold values as a dictionary.

    This is useful for:
    - Logging/debugging: Record what thresholds were used
    - Transparency: Include in result metadata
    - Research: Compare different threshold settings

    Returns:
        Dict mapping threshold names to their values

    Example:
        >>> thresholds = get_all_thresholds()
        >>> print(f"Spike ratio: {thresholds['spike_ratio']}")
    """
    return {
        "min_windows": MIN_WINDOWS,
        "recommended_windows": RECOMMENDED_WINDOWS,
        "uniform_cv_threshold": UNIFORM_CV_THRESHOLD,
        "uniform_mean_threshold": UNIFORM_MEAN_THRESHOLD,
        "spike_ratio": SPIKE_RATIO,
        "spike_min_absolute": SPIKE_MIN_ABSOLUTE,
        "trend_slope_threshold": TREND_SLOPE_THRESHOLD,
        "trend_r_squared_threshold": TREND_R_SQUARED_THRESHOLD,
        "confidence_min_windows": CONFIDENCE_MIN_WINDOWS,
        "marginal_data_max_confidence": MARGINAL_DATA_MAX_CONFIDENCE,
    }
