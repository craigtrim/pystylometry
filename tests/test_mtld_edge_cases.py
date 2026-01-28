"""Comprehensive tests for MTLD (Measure of Textual Lexical Diversity)."""

from pystylometry.lexical import compute_mtld


class TestMTLDEdgeCases:
    """Test edge cases for MTLD computation."""

    def test_empty_text(self):
        """Test MTLD with empty text."""
        import math

        result = compute_mtld("")

        # Empty text returns NaN for metrics (per Distribution pattern)
        assert math.isnan(result.mtld_forward)
        assert math.isnan(result.mtld_backward)
        assert math.isnan(result.mtld_average)
        assert result.metadata["total_token_count"] == 0

    def test_very_short_text(self):
        """Test MTLD with very short text (fewer tokens than typical factor)."""
        text = "one two three"
        result = compute_mtld(text)

        # Should handle short text gracefully
        assert result.mtld_forward >= 0.0
        assert result.mtld_backward >= 0.0
        # For very short text with high diversity, MTLD equals text length
        assert result.metadata["total_token_count"] == 3

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
        import math

        result = compute_mtld("   \n\t  ")

        # Whitespace-only returns NaN for metrics (per Distribution pattern)
        assert math.isnan(result.mtld_forward)
        assert math.isnan(result.mtld_backward)
        assert math.isnan(result.mtld_average)
