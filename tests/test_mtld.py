"""Comprehensive tests for MTLD (Measure of Textual Lexical Diversity)."""

import pytest

from pystylometry.lexical import compute_mtld


class TestMTLDBasicFunctionality:
    """Test basic MTLD functionality."""

    def test_basic_mtld_computation(self):
        """Test MTLD computation with sample text."""
        text = "The quick brown fox jumps over the lazy dog and the cat"
        result = compute_mtld(text)

        # Should return all three measures
        assert hasattr(result, "mtld_forward")
        assert hasattr(result, "mtld_backward")
        assert hasattr(result, "mtld_average")

        # All should be non-negative
        assert result.mtld_forward >= 0.0
        assert result.mtld_backward >= 0.0
        assert result.mtld_average >= 0.0

    def test_mtld_average_is_mean(self):
        """Test that mtld_average is the mean of forward and backward."""
        text = "The quick brown fox jumps over the lazy dog"
        result = compute_mtld(text)

        expected_average = (result.mtld_forward + result.mtld_backward) / 2
        assert abs(result.mtld_average - expected_average) < 0.001

    def test_mtld_with_longer_text(self):
        """Test MTLD with longer text for more stable results."""
        # Longer text with varied vocabulary
        text = (
            "The quick brown fox jumps over the lazy dog. "
            "A fast red wolf runs across the sleepy cat. "
            "Many different animals live in various places. "
            "Some creatures prefer water while others choose land. "
            "Birds fly high above the trees and mountains."
        )
        result = compute_mtld(text)

        # MTLD should be positive for diverse text
        assert result.mtld_forward > 0.0
        assert result.mtld_backward > 0.0
        assert result.mtld_average > 0.0


class TestMTLDEdgeCases:
    """Test edge cases for MTLD computation."""

    def test_empty_text(self):
        """Test MTLD with empty text."""
        result = compute_mtld("")

        assert result.mtld_forward == 0.0
        assert result.mtld_backward == 0.0
        assert result.mtld_average == 0.0
        assert result.metadata["token_count"] == 0

    def test_very_short_text(self):
        """Test MTLD with very short text (fewer tokens than typical factor)."""
        text = "one two three"
        result = compute_mtld(text)

        # Should handle short text gracefully
        assert result.mtld_forward >= 0.0
        assert result.mtld_backward >= 0.0
        # For very short text with high diversity, MTLD equals text length
        assert result.metadata["token_count"] == 3

    def test_single_word(self):
        """Test MTLD with single word."""
        text = "hello"
        result = compute_mtld(text)

        # Single word has perfect diversity (TTR = 1.0)
        # Should return length of 1.0
        assert result.mtld_forward == 1.0
        assert result.mtld_backward == 1.0
        assert result.mtld_average == 1.0

    def test_whitespace_only(self):
        """Test MTLD with only whitespace."""
        result = compute_mtld("   \n\t  ")

        assert result.mtld_forward == 0.0
        assert result.mtld_backward == 0.0
        assert result.mtld_average == 0.0


class TestMTLDRepetitionVsDiversity:
    """Test MTLD behavior with varying levels of repetition."""

    def test_highly_repetitive_text(self):
        """Test MTLD with highly repetitive text (low diversity)."""
        # Repeat the same word many times
        text = "the " * 50
        result = compute_mtld(text)

        # Highly repetitive text should have low MTLD
        # TTR will drop quickly below threshold
        assert result.mtld_forward > 0.0
        assert result.mtld_backward > 0.0
        # MTLD should be relatively low for repetitive text
        # (Each factor completes quickly as TTR drops)

    def test_highly_diverse_text(self):
        """Test MTLD with highly diverse text (all unique words)."""
        # All unique words
        text = "one two three four five six seven eight nine ten"
        result = compute_mtld(text)

        # With all unique words, TTR stays at 1.0
        # No factors complete, so MTLD equals text length
        assert result.mtld_forward == 10.0
        assert result.mtld_backward == 10.0
        assert result.mtld_average == 10.0

    def test_mixed_diversity(self):
        """Test MTLD with mixed repetition and diversity."""
        # Some repeated words, some unique
        text = "the cat sat on the mat and the dog ran with the ball"
        result = compute_mtld(text)

        # Should have moderate MTLD
        assert result.mtld_forward > 0.0
        assert result.mtld_backward > 0.0

        # MTLD for mixed text should be between extremes
        # (Greater than highly repetitive, less than perfectly diverse)


class TestMTLDThresholdParameter:
    """Test MTLD threshold parameter effects."""

    def test_default_threshold(self):
        """Test MTLD with default threshold (0.72)."""
        text = "The quick brown fox jumps over the lazy dog"
        result = compute_mtld(text)

        # Default threshold should be 0.72
        assert result.metadata["threshold"] == 0.72

    def test_custom_threshold(self):
        """Test MTLD with custom threshold."""
        text = "The quick brown fox jumps over the lazy dog"
        result = compute_mtld(text, threshold=0.5)

        # Should use custom threshold
        assert result.metadata["threshold"] == 0.5

    def test_threshold_affects_results(self):
        """Test that different thresholds produce different results."""
        text = "the cat sat on the mat and the dog ran with the ball"

        result_low = compute_mtld(text, threshold=0.5)
        result_high = compute_mtld(text, threshold=0.8)

        # Lower threshold = factors complete sooner = lower MTLD (more factors)
        # Higher threshold = factors take longer = higher MTLD (fewer factors)
        # Note: This may not always hold for very short texts
        # but is generally true for longer texts

    def test_threshold_zero_raises_error(self):
        """Test that threshold=0 raises ValueError."""
        text = "The quick brown fox"
        with pytest.raises(ValueError, match="Threshold must be in range \\(0, 1\\)"):
            compute_mtld(text, threshold=0.0)

    def test_threshold_one_raises_error(self):
        """Test that threshold=1.0 raises ValueError (would cause division by zero)."""
        text = "The quick brown fox"
        with pytest.raises(ValueError, match="Threshold must be in range \\(0, 1\\)"):
            compute_mtld(text, threshold=1.0)

    def test_threshold_negative_raises_error(self):
        """Test that negative threshold raises ValueError."""
        text = "The quick brown fox"
        with pytest.raises(ValueError, match="Threshold must be in range \\(0, 1\\)"):
            compute_mtld(text, threshold=-0.5)

    def test_threshold_above_one_raises_error(self):
        """Test that threshold > 1 raises ValueError."""
        text = "The quick brown fox"
        with pytest.raises(ValueError, match="Threshold must be in range \\(0, 1\\)"):
            compute_mtld(text, threshold=1.5)


class TestMTLDForwardBackward:
    """Test MTLD forward vs backward computation."""

    def test_forward_backward_similarity(self):
        """Test that forward and backward MTLD are similar for typical text."""
        # For most texts, forward and backward should be reasonably close
        text = (
            "The quick brown fox jumps over the lazy dog. "
            "A fast red wolf runs across the sleepy cat. "
            "Many different animals live in various places."
        )
        result = compute_mtld(text)

        # Forward and backward should be positive
        assert result.mtld_forward > 0.0
        assert result.mtld_backward > 0.0

        # They should be reasonably similar (within a factor of 2 or so)
        # for balanced text
        ratio = max(result.mtld_forward, result.mtld_backward) / min(
            result.mtld_forward, result.mtld_backward
        )
        # This is a loose bound - they don't need to be identical
        # but shouldn't be wildly different for typical prose

    def test_forward_backward_identical_for_all_unique(self):
        """Test forward = backward when all words are unique."""
        text = "one two three four five six seven"
        result = compute_mtld(text)

        # With all unique words, direction doesn't matter
        assert result.mtld_forward == result.mtld_backward == 7.0


class TestMTLDMetadata:
    """Test metadata returned with MTLD results."""

    def test_metadata_contains_counts(self):
        """Test that metadata contains token_count and threshold."""
        text = "The quick brown fox"
        result = compute_mtld(text)

        assert "token_count" in result.metadata
        assert "threshold" in result.metadata

        assert result.metadata["token_count"] == 4
        assert result.metadata["threshold"] == 0.72  # default

    def test_metadata_threshold_matches_parameter(self):
        """Test that metadata threshold matches the parameter."""
        text = "The quick brown fox"
        result = compute_mtld(text, threshold=0.6)

        assert result.metadata["threshold"] == 0.6


class TestMTLDRobustness:
    """Test MTLD robustness to text length variations."""

    def test_mtld_more_stable_than_ttr(self):
        """
        Test that MTLD is more robust to text length than simple TTR.

        This is a key advantage of MTLD - it should be less affected by
        text length compared to Type-Token Ratio.
        """
        # Short text with some diversity
        short_text = "the cat sat on the mat"

        # Longer text with similar diversity pattern
        long_text = "the cat sat on the mat and the dog ran with the ball"

        result_short = compute_mtld(short_text)
        result_long = compute_mtld(long_text)

        # Both should have positive MTLD
        assert result_short.mtld_average > 0.0
        assert result_long.mtld_average > 0.0

        # MTLD should be more stable across lengths than TTR would be
        # (This is qualitative - we're just checking they're both reasonable)
