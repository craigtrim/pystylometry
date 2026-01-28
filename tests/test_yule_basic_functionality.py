"""Comprehensive tests for Yule's K and I vocabulary richness metrics."""

from pystylometry.lexical import compute_yule


class TestYuleBasicFunctionality:
    """Test basic Yule's K and I functionality."""

    def test_basic_yule_computation(self):
        """Test Yule's K and I computation with sample text."""
        text = "The quick brown fox jumps over the lazy dog"
        result = compute_yule(text)

        # Should return both metrics
        assert hasattr(result, "yule_k")
        assert hasattr(result, "yule_i")
        assert hasattr(result, "metadata")

        # Both should be non-negative
        assert result.yule_k >= 0.0
        assert result.yule_i >= 0.0

    def test_yule_with_longer_text(self):
        """Test Yule with longer text for more reliable metrics."""
        text = (
            "The quick brown fox jumps over the lazy dog. "
            "A fast red wolf runs across the sleepy cat. "
            "Many different animals live in various places."
        )
        result = compute_yule(text)

        # Should have positive values
        assert result.yule_k > 0.0
        assert result.yule_i > 0.0
