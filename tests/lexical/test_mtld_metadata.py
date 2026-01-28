"""Comprehensive tests for MTLD (Measure of Textual Lexical Diversity)."""

from pystylometry.lexical import compute_mtld


class TestMTLDMetadata:
    """Test metadata returned with MTLD results."""

    def test_metadata_contains_counts(self):
        """Test that metadata contains total_token_count and threshold."""
        text = "The quick brown fox"
        result = compute_mtld(text)

        assert "total_token_count" in result.metadata
        assert "threshold" in result.metadata

        assert result.metadata["total_token_count"] == 4
        assert result.metadata["threshold"] == 0.72  # default

    def test_metadata_threshold_matches_parameter(self):
        """Test that metadata threshold matches the parameter."""
        text = "The quick brown fox"
        result = compute_mtld(text, threshold=0.6)

        assert result.metadata["threshold"] == 0.6
