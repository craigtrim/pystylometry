"""Comprehensive tests for consistency threshold constants and get_all_thresholds().

Covers:
    - Existence and type of each module-level constant
    - Reasonable value ranges for each constant
    - Relationships between related constants
    - get_all_thresholds() return structure, types, and values
    - Consistency between get_all_thresholds() and module-level constants
    - Semantic constraints (CV < 1.0, SPIKE_RATIO > 1.0, etc.)
    - Immutability: mutating the returned dict does not affect future calls
"""

from pystylometry.consistency._thresholds import (
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


# =========================================================================
# 1. Each constant exists and has the expected type
# =========================================================================


class TestConstantTypes:
    """Every threshold constant must be either int or float."""

    def test_min_windows_is_int(self):
        """MIN_WINDOWS should be an integer (window count)."""
        assert isinstance(MIN_WINDOWS, int)

    def test_recommended_windows_is_int(self):
        """RECOMMENDED_WINDOWS should be an integer (window count)."""
        assert isinstance(RECOMMENDED_WINDOWS, int)

    def test_uniform_cv_threshold_is_float(self):
        """UNIFORM_CV_THRESHOLD should be a float (ratio)."""
        assert isinstance(UNIFORM_CV_THRESHOLD, float)

    def test_uniform_mean_threshold_is_float(self):
        """UNIFORM_MEAN_THRESHOLD should be a float (chi-squared value)."""
        assert isinstance(UNIFORM_MEAN_THRESHOLD, float)

    def test_spike_ratio_is_float(self):
        """SPIKE_RATIO should be a float (multiplicative factor)."""
        assert isinstance(SPIKE_RATIO, float)

    def test_spike_min_absolute_is_float(self):
        """SPIKE_MIN_ABSOLUTE should be a float (chi-squared value)."""
        assert isinstance(SPIKE_MIN_ABSOLUTE, float)

    def test_trend_slope_threshold_is_float(self):
        """TREND_SLOPE_THRESHOLD should be a float (slope units)."""
        assert isinstance(TREND_SLOPE_THRESHOLD, float)

    def test_trend_r_squared_threshold_is_float(self):
        """TREND_R_SQUARED_THRESHOLD should be a float (R-squared)."""
        assert isinstance(TREND_R_SQUARED_THRESHOLD, float)

    def test_confidence_min_windows_is_int(self):
        """CONFIDENCE_MIN_WINDOWS should be an integer (window count)."""
        assert isinstance(CONFIDENCE_MIN_WINDOWS, int)

    def test_marginal_data_max_confidence_is_float(self):
        """MARGINAL_DATA_MAX_CONFIDENCE should be a float (probability)."""
        assert isinstance(MARGINAL_DATA_MAX_CONFIDENCE, float)


# =========================================================================
# 2. Each constant has a reasonable, positive value
# =========================================================================


class TestConstantRanges:
    """Each constant should be strictly positive and within a sensible range."""

    def test_min_windows_positive(self):
        """MIN_WINDOWS must be at least 2 to compute any variance."""
        assert MIN_WINDOWS >= 2

    def test_recommended_windows_at_least_three(self):
        """RECOMMENDED_WINDOWS must be at least 3 for trend detection."""
        assert RECOMMENDED_WINDOWS >= 3

    def test_uniform_cv_threshold_positive(self):
        """UNIFORM_CV_THRESHOLD must be positive."""
        assert UNIFORM_CV_THRESHOLD > 0

    def test_uniform_mean_threshold_positive(self):
        """UNIFORM_MEAN_THRESHOLD must be positive."""
        assert UNIFORM_MEAN_THRESHOLD > 0

    def test_spike_ratio_above_one(self):
        """SPIKE_RATIO must exceed 1.0 to represent an outlier multiplier."""
        assert SPIKE_RATIO > 1.0

    def test_spike_min_absolute_positive(self):
        """SPIKE_MIN_ABSOLUTE must be positive."""
        assert SPIKE_MIN_ABSOLUTE > 0

    def test_trend_slope_threshold_positive(self):
        """TREND_SLOPE_THRESHOLD must be positive."""
        assert TREND_SLOPE_THRESHOLD > 0

    def test_trend_r_squared_between_zero_and_one(self):
        """R-squared thresholds are bounded to [0, 1]."""
        assert 0 < TREND_R_SQUARED_THRESHOLD <= 1.0

    def test_confidence_min_windows_positive(self):
        """CONFIDENCE_MIN_WINDOWS must be a positive integer."""
        assert CONFIDENCE_MIN_WINDOWS > 0

    def test_marginal_data_max_confidence_between_zero_and_one(self):
        """MARGINAL_DATA_MAX_CONFIDENCE is a probability, so 0 < x <= 1."""
        assert 0 < MARGINAL_DATA_MAX_CONFIDENCE <= 1.0


# =========================================================================
# 3. Relationships between constants
# =========================================================================


class TestConstantRelationships:
    """Validate logical ordering and relationships between thresholds."""

    def test_min_windows_less_than_recommended(self):
        """MIN_WINDOWS must be strictly less than RECOMMENDED_WINDOWS."""
        assert MIN_WINDOWS < RECOMMENDED_WINDOWS

    def test_confidence_min_windows_ge_min_windows(self):
        """Full-confidence window count must be at least MIN_WINDOWS."""
        assert CONFIDENCE_MIN_WINDOWS >= MIN_WINDOWS

    def test_marginal_data_max_confidence_below_full(self):
        """Marginal data confidence must be below 1.0 (full confidence)."""
        assert MARGINAL_DATA_MAX_CONFIDENCE < 1.0

    def test_uniform_cv_below_one(self):
        """CV threshold for uniformity must be well below 1.0."""
        assert UNIFORM_CV_THRESHOLD < 1.0

    def test_spike_ratio_reasonable_upper_bound(self):
        """SPIKE_RATIO should not be so high that spikes are never detected."""
        assert SPIKE_RATIO <= 10.0

    def test_trend_slope_reasonable_upper_bound(self):
        """TREND_SLOPE_THRESHOLD should stay reasonable for chi-squared drift."""
        assert TREND_SLOPE_THRESHOLD <= 100.0


# =========================================================================
# 4. get_all_thresholds() return structure
# =========================================================================


class TestGetAllThresholdsStructure:
    """Validate the dict returned by get_all_thresholds()."""

    def test_returns_dict(self):
        """get_all_thresholds() must return a dict."""
        result = get_all_thresholds()
        assert isinstance(result, dict)

    def test_returns_exactly_ten_keys(self):
        """The dict should contain exactly 10 threshold entries."""
        result = get_all_thresholds()
        assert len(result) == 10

    def test_expected_keys_present(self):
        """Every expected key must be present in the returned dict."""
        expected_keys = {
            "min_windows",
            "recommended_windows",
            "uniform_cv_threshold",
            "uniform_mean_threshold",
            "spike_ratio",
            "spike_min_absolute",
            "trend_slope_threshold",
            "trend_r_squared_threshold",
            "confidence_min_windows",
            "marginal_data_max_confidence",
        }
        result = get_all_thresholds()
        assert set(result.keys()) == expected_keys

    def test_all_values_numeric(self):
        """Every value in the dict must be int or float."""
        result = get_all_thresholds()
        for key, value in result.items():
            assert isinstance(value, (int, float)), (
                f"Value for '{key}' is {type(value).__name__}, expected int or float"
            )


# =========================================================================
# 5. get_all_thresholds() matches module-level constants
# =========================================================================


class TestGetAllThresholdsValues:
    """Each dict value must match its corresponding module-level constant."""

    def test_min_windows_matches(self):
        result = get_all_thresholds()
        assert result["min_windows"] == MIN_WINDOWS

    def test_recommended_windows_matches(self):
        result = get_all_thresholds()
        assert result["recommended_windows"] == RECOMMENDED_WINDOWS

    def test_uniform_cv_threshold_matches(self):
        result = get_all_thresholds()
        assert result["uniform_cv_threshold"] == UNIFORM_CV_THRESHOLD

    def test_uniform_mean_threshold_matches(self):
        result = get_all_thresholds()
        assert result["uniform_mean_threshold"] == UNIFORM_MEAN_THRESHOLD

    def test_spike_ratio_matches(self):
        result = get_all_thresholds()
        assert result["spike_ratio"] == SPIKE_RATIO

    def test_spike_min_absolute_matches(self):
        result = get_all_thresholds()
        assert result["spike_min_absolute"] == SPIKE_MIN_ABSOLUTE

    def test_trend_slope_threshold_matches(self):
        result = get_all_thresholds()
        assert result["trend_slope_threshold"] == TREND_SLOPE_THRESHOLD

    def test_trend_r_squared_threshold_matches(self):
        result = get_all_thresholds()
        assert result["trend_r_squared_threshold"] == TREND_R_SQUARED_THRESHOLD

    def test_confidence_min_windows_matches(self):
        result = get_all_thresholds()
        assert result["confidence_min_windows"] == CONFIDENCE_MIN_WINDOWS

    def test_marginal_data_max_confidence_matches(self):
        result = get_all_thresholds()
        assert result["marginal_data_max_confidence"] == MARGINAL_DATA_MAX_CONFIDENCE


# =========================================================================
# 6. Threshold semantics
# =========================================================================


class TestThresholdSemantics:
    """Validate the domain semantics of each threshold value."""

    def test_uniform_cv_threshold_less_than_one(self):
        """CV is std/mean; a threshold below 1.0 catches low-variance signals."""
        assert UNIFORM_CV_THRESHOLD < 1.0

    def test_spike_ratio_greater_than_one(self):
        """A ratio > 1 means max must be a multiple of the mean."""
        assert SPIKE_RATIO > 1.0

    def test_r_squared_not_trivially_zero(self):
        """R-squared of zero would flag any positive slope; must be meaningful."""
        assert TREND_R_SQUARED_THRESHOLD > 0.0

    def test_marginal_data_penalises_small_samples(self):
        """Marginal max confidence must be strictly below 1.0 to penalise."""
        assert MARGINAL_DATA_MAX_CONFIDENCE < 1.0

    def test_spike_min_absolute_nontrivial(self):
        """Spike minimum should be large enough to avoid noise-level triggers."""
        assert SPIKE_MIN_ABSOLUTE >= 10.0


# =========================================================================
# 7. Immutability: mutating the returned dict must not affect future calls
# =========================================================================


class TestImmutability:
    """Mutating the dict from get_all_thresholds() must not leak state."""

    def test_mutation_does_not_persist(self):
        """Deleting a key from one call must not affect the next call."""
        first = get_all_thresholds()
        first.pop("min_windows")

        second = get_all_thresholds()
        assert "min_windows" in second

    def test_overwrite_does_not_persist(self):
        """Overwriting a value in one call must not affect the next call."""
        first = get_all_thresholds()
        first["spike_ratio"] = -999.0

        second = get_all_thresholds()
        assert second["spike_ratio"] == SPIKE_RATIO

    def test_adding_key_does_not_persist(self):
        """Adding a new key to the dict must not appear in subsequent calls."""
        first = get_all_thresholds()
        first["extra_key"] = 42

        second = get_all_thresholds()
        assert "extra_key" not in second

    def test_separate_calls_return_distinct_objects(self):
        """Each call should return a new dict object."""
        first = get_all_thresholds()
        second = get_all_thresholds()
        assert first is not second

    def test_separate_calls_return_equal_dicts(self):
        """Two consecutive calls should return equal (but distinct) dicts."""
        first = get_all_thresholds()
        second = get_all_thresholds()
        assert first == second
