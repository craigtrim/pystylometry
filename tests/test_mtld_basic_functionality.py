"""Comprehensive tests for MTLD (Measure of Textual Lexical Diversity)."""

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
