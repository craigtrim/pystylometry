"""Tests for Kilgarriff chi-squared drift detection module.

Covers:
    - _create_sliding_windows: non-overlapping, overlapping, gaps, partial
      windows, edge cases (empty, single token), validation errors
    - _compute_trend: linear increase, decrease, flat, single value, two values,
      perfect fit, noisy data
    - _classify_pattern: all 5 patterns (consistent, gradual_drift, sudden_spike,
      suspiciously_uniform, unknown), confidence scaling, marginal data
    - compute_kilgarriff_drift: insufficient data, sequential mode, all_pairs mode,
      fixed_lag mode, validation errors, result structure
"""

import math

import pytest

from pystylometry.consistency.drift import (
    _classify_pattern,
    _compute_trend,
    _create_sliding_windows,
    compute_kilgarriff_drift,
)
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
)


# =========================================================================
# Helpers
# =========================================================================


def _make_long_text(n_words: int, seed: int = 0) -> str:
    """Generate a deterministic pseudo-random text with *n_words* words.

    Uses a small fixed vocabulary and a simple PRNG so that every call with
    the same arguments produces the same output.  The vocabulary is large
    enough to exercise the chi-squared computation meaningfully.
    """
    vocab = [
        "the", "of", "and", "to", "in", "a", "is", "that", "for", "it",
        "was", "on", "are", "be", "with", "as", "at", "this", "from", "or",
        "an", "by", "not", "but", "what", "all", "were", "when", "we", "there",
        "can", "had", "has", "her", "more", "if", "will", "one", "about", "up",
        "out", "do", "so", "some", "time", "very", "just", "know", "people",
        "take", "into", "year", "good", "could", "them", "see", "other", "than",
        "now", "look", "only", "come", "over", "think", "also", "after", "use",
        "work", "first", "well", "way", "even", "new", "want", "because", "any",
        "give", "day", "most", "find", "here", "thing", "many", "still", "long",
        "great", "own", "say", "old", "tell", "world", "should", "big", "high",
        "such", "school", "state", "never",
    ]
    state = seed
    words = []
    for _ in range(n_words):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        words.append(vocab[state % len(vocab)])
    return " ".join(words)


def _make_mixed_text(n_words_a: int, n_words_b: int) -> str:
    """Two distinct pseudo-random blocks stitched together.

    Uses different seeds so the two halves have very different word
    distributions, which should trigger a spike or drift.
    """
    return _make_long_text(n_words_a, seed=0) + " " + _make_long_text(n_words_b, seed=99999)


# =========================================================================
# 1. _create_sliding_windows
# =========================================================================


class TestCreateSlidingWindows:
    """Tests for the sliding-window helper."""

    def test_non_overlapping(self):
        """stride == window_size gives non-overlapping windows."""
        tokens = list("abcdefgh")
        windows = _create_sliding_windows(tokens, window_size=4, stride=4)
        assert windows == [list("abcd"), list("efgh")]

    def test_overlapping(self):
        """stride < window_size gives overlapping windows with shared tokens."""
        tokens = list("abcdefg")  # 7 tokens
        windows = _create_sliding_windows(tokens, window_size=3, stride=2)
        # window 0: start=0 -> abc
        # window 1: start=2 -> cde  (shares 'c' with window 0)
        # window 2: start=4 -> efg  (shares 'e' with window 1)
        assert windows[0] == list("abc")
        assert windows[1] == list("cde")
        assert windows[2] == list("efg")
        assert len(windows) == 3

    def test_gaps(self):
        """stride > window_size skips tokens between windows."""
        tokens = list("abcdefghijkl")  # 12 tokens
        windows = _create_sliding_windows(tokens, window_size=3, stride=5)
        # window 0: start=0 -> abc
        # window 1: start=5 -> fgh
        # window 2: start=10 -> needs 3 tokens but only kl remain -> partial
        assert windows[0] == ["a", "b", "c"]
        assert windows[1] == ["f", "g", "h"]

    def test_partial_window_included(self):
        """Partial final window included if >= 50% of window_size."""
        # 7 tokens, window_size=4, stride=4:
        #   window 0 (start=0): abcd   -- full
        #   window 1 (start=4): efg    -- 3 tokens, 75% >= 50%, included
        tokens = list("abcdefg")
        windows = _create_sliding_windows(tokens, window_size=4, stride=4)
        assert len(windows) == 2
        assert windows[1] == ["e", "f", "g"]

    def test_partial_window_excluded(self):
        """Partial final window excluded if < 50% of window_size."""
        # 5 tokens, window_size=4, stride=4:
        #   window 0 (start=0): abcd  -- full
        #   remaining: e  -- 1 token, 25% < 50%, excluded
        tokens = list("abcde")
        windows = _create_sliding_windows(tokens, window_size=4, stride=4)
        assert len(windows) == 1

    def test_empty_tokens(self):
        """Empty token list returns no windows."""
        windows = _create_sliding_windows([], window_size=4, stride=2)
        assert windows == []

    def test_single_token(self):
        """Single token with window_size > 2 returns no windows (< 50% threshold)."""
        windows = _create_sliding_windows(["a"], window_size=3, stride=1)
        assert windows == []

    def test_tokens_equal_window_size(self):
        """Exactly one full window when len(tokens) == window_size."""
        tokens = list("abcd")
        windows = _create_sliding_windows(tokens, window_size=4, stride=4)
        assert len(windows) == 1
        assert windows[0] == list("abcd")

    def test_stride_validation_zero(self):
        """stride=0 raises ValueError."""
        with pytest.raises(ValueError, match="stride must be positive"):
            _create_sliding_windows(["a", "b"], window_size=1, stride=0)

    def test_stride_validation_negative(self):
        """Negative stride raises ValueError."""
        with pytest.raises(ValueError, match="stride must be positive"):
            _create_sliding_windows(["a", "b"], window_size=1, stride=-1)

    def test_window_size_validation_zero(self):
        """window_size=0 raises ValueError."""
        with pytest.raises(ValueError, match="window_size must be positive"):
            _create_sliding_windows(["a", "b"], window_size=0, stride=1)

    def test_window_size_validation_negative(self):
        """Negative window_size raises ValueError."""
        with pytest.raises(ValueError, match="window_size must be positive"):
            _create_sliding_windows(["a", "b"], window_size=-3, stride=1)


# =========================================================================
# 2. _compute_trend
# =========================================================================


class TestComputeTrend:
    """Tests for linear-regression trend helper."""

    def test_linear_increase(self):
        """Perfect linear increase produces slope > 0, R-squared ~1."""
        slope, r_sq = _compute_trend([10.0, 15.0, 20.0, 25.0, 30.0])
        assert slope == pytest.approx(5.0)
        assert r_sq == pytest.approx(1.0, abs=1e-9)

    def test_linear_decrease(self):
        """Perfect linear decrease produces negative slope, R-squared ~1."""
        slope, r_sq = _compute_trend([30.0, 25.0, 20.0, 15.0, 10.0])
        assert slope == pytest.approx(-5.0)
        assert r_sq == pytest.approx(1.0, abs=1e-9)

    def test_flat(self):
        """Constant values yield slope=0, R-squared=1 (perfect fit to flat line)."""
        slope, r_sq = _compute_trend([7.0, 7.0, 7.0, 7.0])
        assert slope == pytest.approx(0.0)
        # When all values are equal, var_y=0 and slope=0 -> r_squared=1.0
        assert r_sq == pytest.approx(1.0)

    def test_single_value(self):
        """Single value returns (0.0, 0.0)."""
        slope, r_sq = _compute_trend([42.0])
        assert slope == 0.0
        assert r_sq == 0.0

    def test_two_values(self):
        """Two values still produce a valid regression."""
        slope, r_sq = _compute_trend([10.0, 20.0])
        assert slope == pytest.approx(10.0)
        assert r_sq == pytest.approx(1.0, abs=1e-9)

    def test_noisy_data(self):
        """Oscillating data produces near-zero slope and R-squared below 1."""
        values = [50.0, 10.0, 50.0, 10.0, 50.0]
        slope, r_sq = _compute_trend(values)
        # Oscillating data should have near-zero slope
        assert abs(slope) < 1.0
        # R-squared should be less than a perfect linear fit
        assert r_sq < 1.0

    def test_r_squared_bounded(self):
        """R-squared is always between 0 and 1."""
        for vals in [
            [1.0, 100.0, 2.0, 99.0],
            [0.0, 0.0, 0.0],
            [3.0, 6.0, 9.0, 12.0],
        ]:
            _, r_sq = _compute_trend(vals)
            assert 0.0 <= r_sq <= 1.0

    def test_empty_list(self):
        """Empty list returns (0.0, 0.0)."""
        slope, r_sq = _compute_trend([])
        assert slope == 0.0
        assert r_sq == 0.0


# =========================================================================
# 3. _classify_pattern
# =========================================================================


class TestClassifyPattern:
    """Tests for pattern classification logic."""

    def test_unknown_below_min_windows(self):
        """Fewer than MIN_WINDOWS returns 'unknown' with confidence 0."""
        pattern, conf = _classify_pattern(
            mean_chi=20.0, std_chi=5.0, max_chi=30.0, min_chi=10.0,
            trend_slope=0.0, trend_r_squared=0.0,
            window_count=MIN_WINDOWS - 1,
        )
        assert pattern == "unknown"
        assert conf == 0.0

    def test_consistent_zero_mean(self):
        """Zero mean_chi is classified as 'consistent'."""
        pattern, conf = _classify_pattern(
            mean_chi=0.0, std_chi=0.0, max_chi=0.0, min_chi=0.0,
            trend_slope=0.0, trend_r_squared=0.0,
            window_count=RECOMMENDED_WINDOWS,
        )
        assert pattern == "consistent"
        assert conf > 0.0

    def test_suspiciously_uniform(self):
        """Low CV and low mean triggers 'suspiciously_uniform'."""
        mean_chi = UNIFORM_MEAN_THRESHOLD * 0.5  # well below threshold
        std_chi = mean_chi * (UNIFORM_CV_THRESHOLD * 0.5)  # CV well below threshold
        pattern, conf = _classify_pattern(
            mean_chi=mean_chi, std_chi=std_chi, max_chi=mean_chi + std_chi,
            min_chi=mean_chi - std_chi,
            trend_slope=0.0, trend_r_squared=0.0,
            window_count=RECOMMENDED_WINDOWS,
        )
        assert pattern == "suspiciously_uniform"
        assert 0.0 < conf <= 1.0

    def test_sudden_spike(self):
        """Max far exceeding mean triggers 'sudden_spike'."""
        mean_chi = 100.0
        max_chi = mean_chi * (SPIKE_RATIO + 1.0)  # well above spike_ratio
        # Make sure max_chi > SPIKE_MIN_ABSOLUTE
        assert max_chi > SPIKE_MIN_ABSOLUTE
        pattern, conf = _classify_pattern(
            mean_chi=mean_chi, std_chi=50.0, max_chi=max_chi, min_chi=50.0,
            trend_slope=0.0, trend_r_squared=0.0,
            window_count=RECOMMENDED_WINDOWS,
        )
        assert pattern == "sudden_spike"
        assert 0.0 < conf <= 1.0

    def test_gradual_drift(self):
        """Significant slope with good R-squared triggers 'gradual_drift'."""
        slope = TREND_SLOPE_THRESHOLD + 5.0
        r_sq = TREND_R_SQUARED_THRESHOLD + 0.3
        # Use mean/std that do NOT trigger uniform or spike
        mean_chi = 200.0  # above UNIFORM_MEAN_THRESHOLD
        std_chi = 60.0
        max_chi = 300.0  # ratio = 1.5 < SPIKE_RATIO
        pattern, conf = _classify_pattern(
            mean_chi=mean_chi, std_chi=std_chi, max_chi=max_chi, min_chi=100.0,
            trend_slope=slope, trend_r_squared=r_sq,
            window_count=RECOMMENDED_WINDOWS,
        )
        assert pattern == "gradual_drift"
        assert 0.0 < conf <= 1.0

    def test_consistent_default(self):
        """Normal variation without special patterns yields 'consistent'."""
        # mean above UNIFORM_MEAN_THRESHOLD, no spike, no strong trend
        mean_chi = 100.0
        std_chi = 30.0  # CV = 0.3 > UNIFORM_CV_THRESHOLD
        max_chi = 150.0  # ratio = 1.5 < SPIKE_RATIO
        pattern, conf = _classify_pattern(
            mean_chi=mean_chi, std_chi=std_chi, max_chi=max_chi, min_chi=60.0,
            trend_slope=1.0, trend_r_squared=0.1,  # below thresholds
            window_count=RECOMMENDED_WINDOWS,
        )
        assert pattern == "consistent"
        assert 0.0 < conf <= 1.0

    def test_confidence_scaling_marginal_data(self):
        """Confidence is capped at MARGINAL_DATA_MAX_CONFIDENCE for marginal data."""
        # Use window_count between MIN_WINDOWS and RECOMMENDED_WINDOWS
        window_count = MIN_WINDOWS  # exactly at minimum
        assert window_count < RECOMMENDED_WINDOWS
        pattern, conf = _classify_pattern(
            mean_chi=100.0, std_chi=30.0, max_chi=150.0, min_chi=60.0,
            trend_slope=0.0, trend_r_squared=0.0,
            window_count=window_count,
        )
        assert conf <= MARGINAL_DATA_MAX_CONFIDENCE

    def test_confidence_full_data(self):
        """With enough windows, confidence can exceed MARGINAL_DATA_MAX_CONFIDENCE."""
        pattern, conf = _classify_pattern(
            mean_chi=100.0, std_chi=30.0, max_chi=150.0, min_chi=60.0,
            trend_slope=0.0, trend_r_squared=0.0,
            window_count=CONFIDENCE_MIN_WINDOWS + 5,
        )
        # base_confidence = min(1.0, 10/5) = 1.0
        # not marginal -> no cap
        # "consistent" confidence = base * 0.8 = 0.8
        assert conf == pytest.approx(0.8)

    def test_spike_needs_absolute_minimum(self):
        """Spike is not triggered when max_chi is below SPIKE_MIN_ABSOLUTE."""
        mean_chi = 10.0
        max_chi = mean_chi * (SPIKE_RATIO + 1.0)  # high ratio but low absolute
        assert max_chi < SPIKE_MIN_ABSOLUTE  # below absolute threshold
        pattern, _ = _classify_pattern(
            mean_chi=mean_chi, std_chi=5.0, max_chi=max_chi, min_chi=5.0,
            trend_slope=0.0, trend_r_squared=0.0,
            window_count=RECOMMENDED_WINDOWS,
        )
        # Should NOT be sudden_spike because max_chi < SPIKE_MIN_ABSOLUTE
        assert pattern != "sudden_spike"


# =========================================================================
# 4. compute_kilgarriff_drift (integration)
# =========================================================================


class TestComputeKilgarriffDrift:
    """Integration tests for the main entry point."""

    def test_insufficient_data_empty_text(self):
        """Empty text returns insufficient_data status."""
        result = compute_kilgarriff_drift("")
        assert result.status == "insufficient_data"
        assert result.pattern == "unknown"
        assert result.pattern_confidence == 0.0
        assert math.isnan(result.mean_chi_squared)

    def test_insufficient_data_short_text(self):
        """Text too short to produce MIN_WINDOWS returns insufficient_data."""
        result = compute_kilgarriff_drift("Hello world", window_size=1000)
        assert result.status == "insufficient_data"
        assert result.window_count < MIN_WINDOWS

    def test_stride_validation_error(self):
        """stride <= 0 raises ValueError."""
        with pytest.raises(ValueError, match="stride must be positive"):
            compute_kilgarriff_drift("some text", stride=0)

    def test_window_size_validation_error(self):
        """window_size <= 0 raises ValueError."""
        with pytest.raises(ValueError, match="window_size must be positive"):
            compute_kilgarriff_drift("some text", window_size=0)

    def test_invalid_comparison_mode(self):
        """Invalid comparison_mode raises ValueError."""
        with pytest.raises(ValueError, match="comparison_mode must be one of"):
            compute_kilgarriff_drift("some text", comparison_mode="bogus")

    def test_sequential_mode_result_structure(self):
        """Sequential mode returns well-formed result with expected fields."""
        text = _make_long_text(6000, seed=42)
        result = compute_kilgarriff_drift(
            text, window_size=500, stride=500, comparison_mode="sequential",
        )
        # Should have enough windows
        assert result.window_count >= MIN_WINDOWS
        assert result.status in ("success", "marginal_data")
        assert result.comparison_mode == "sequential"
        assert result.distance_matrix is None  # only for all_pairs
        assert result.pattern in (
            "consistent", "gradual_drift", "sudden_spike",
            "suspiciously_uniform", "unknown",
        )
        assert 0.0 <= result.pattern_confidence <= 1.0
        assert not math.isnan(result.mean_chi_squared)
        assert not math.isnan(result.std_chi_squared)
        assert result.max_location >= 0
        # Pairwise scores should equal window_count - 1
        assert len(result.pairwise_scores) == result.window_count - 1

    def test_all_pairs_mode(self):
        """all_pairs mode builds a distance matrix."""
        text = _make_long_text(4000, seed=7)
        result = compute_kilgarriff_drift(
            text, window_size=500, stride=500, comparison_mode="all_pairs",
        )
        assert result.comparison_mode == "all_pairs"
        assert result.distance_matrix is not None
        n = result.window_count
        assert len(result.distance_matrix) == n
        assert len(result.distance_matrix[0]) == n
        # Diagonal should be zero
        for i in range(n):
            assert result.distance_matrix[i][i] == 0.0
        # Matrix should be symmetric
        for i in range(n):
            for j in range(n):
                assert result.distance_matrix[i][j] == result.distance_matrix[j][i]
        # Number of pairs: n*(n-1)/2
        expected_pairs = n * (n - 1) // 2
        assert len(result.pairwise_scores) == expected_pairs

    def test_fixed_lag_mode(self):
        """fixed_lag mode compares windows at specified lag distance."""
        text = _make_long_text(5000, seed=13)
        lag = 2
        result = compute_kilgarriff_drift(
            text, window_size=500, stride=500,
            comparison_mode="fixed_lag", lag=lag,
        )
        assert result.comparison_mode == "fixed_lag"
        assert result.distance_matrix is None
        # Each pair should have distance == lag
        for score in result.pairwise_scores:
            i, j = score["chunk_pair"]
            assert j - i == lag

    def test_overlap_ratio_computed(self):
        """overlap_ratio reflects the stride/window_size relationship."""
        text = _make_long_text(5000, seed=21)
        result = compute_kilgarriff_drift(
            text, window_size=1000, stride=500,
        )
        assert result.overlap_ratio == pytest.approx(0.5)

    def test_overlap_ratio_non_overlapping(self):
        """Non-overlapping windows have overlap_ratio 0."""
        text = _make_long_text(5000, seed=21)
        result = compute_kilgarriff_drift(
            text, window_size=500, stride=500,
        )
        assert result.overlap_ratio == pytest.approx(0.0)

    def test_thresholds_in_result(self):
        """Result includes threshold values for transparency."""
        text = _make_long_text(5000, seed=33)
        result = compute_kilgarriff_drift(text, window_size=500, stride=500)
        assert "min_windows" in result.thresholds
        assert "spike_ratio" in result.thresholds
        assert result.thresholds["min_windows"] == MIN_WINDOWS

    def test_metadata_present(self):
        """Result metadata contains expected keys."""
        text = _make_long_text(5000, seed=44)
        result = compute_kilgarriff_drift(text, window_size=500, stride=500)
        assert "total_tokens" in result.metadata
        assert "tokens_per_window" in result.metadata
        assert "comparisons_made" in result.metadata
        assert "method" in result.metadata
        assert result.metadata["method"] == "kilgarriff_drift_2001"

    def test_pairwise_score_structure(self):
        """Each pairwise score dict has the expected keys."""
        text = _make_long_text(4000, seed=55)
        result = compute_kilgarriff_drift(text, window_size=500, stride=500)
        assert len(result.pairwise_scores) > 0
        score = result.pairwise_scores[0]
        assert "chunk_pair" in score
        assert "chi_squared" in score
        assert "degrees_of_freedom" in score
        assert "top_words" in score
        assert "window_i_size" in score
        assert "window_j_size" in score
        assert isinstance(score["chunk_pair"], tuple)
        assert score["chi_squared"] >= 0.0

    def test_marginal_data_status(self):
        """Between MIN_WINDOWS and RECOMMENDED_WINDOWS gives marginal_data status."""
        # We need exactly MIN_WINDOWS windows: 3 windows from 3*ws tokens
        # with non-overlapping windows.  Use small window_size.
        text = _make_long_text(300, seed=66)
        result = compute_kilgarriff_drift(
            text, window_size=50, stride=50,
        )
        if MIN_WINDOWS <= result.window_count < RECOMMENDED_WINDOWS:
            assert result.status == "marginal_data"

    def test_success_status_enough_windows(self):
        """Enough windows gives 'success' status."""
        text = _make_long_text(8000, seed=77)
        result = compute_kilgarriff_drift(
            text, window_size=500, stride=500,
        )
        assert result.window_count >= RECOMMENDED_WINDOWS
        assert result.status == "success"

    def test_trend_only_computed_for_sequential(self):
        """Trend is zero for non-sequential modes."""
        text = _make_long_text(5000, seed=88)
        result = compute_kilgarriff_drift(
            text, window_size=500, stride=500, comparison_mode="all_pairs",
        )
        assert result.trend == 0.0

    def test_max_location_valid_index(self):
        """max_location is a valid index into pairwise_scores."""
        text = _make_long_text(5000, seed=99)
        result = compute_kilgarriff_drift(text, window_size=500, stride=500)
        if result.status != "insufficient_data":
            assert 0 <= result.max_location < len(result.pairwise_scores)
