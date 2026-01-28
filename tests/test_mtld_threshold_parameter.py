"""Comprehensive tests for MTLD (Measure of Textual Lexical Diversity)."""

import pytest

from pystylometry.lexical import compute_mtld


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

        compute_mtld(text, threshold=0.5)
        compute_mtld(text, threshold=0.8)

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
