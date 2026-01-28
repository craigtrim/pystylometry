"""Comprehensive tests for Yule's K and I vocabulary richness metrics."""

from pystylometry.lexical import compute_yule


class TestYuleMetadata:
    """Test metadata returned with Yule results."""

    def test_metadata_contains_counts(self):
        """Test that metadata contains token_count and vocabulary_size."""
        text = "one two three one two one"
        result = compute_yule(text)

        assert "token_count" in result.metadata
        assert "vocabulary_size" in result.metadata

        assert result.metadata["token_count"] == 6
        assert result.metadata["vocabulary_size"] == 3

    def test_metadata_consistency(self):
        """Test that metadata is consistent with input text."""
        text = "the quick brown fox"
        result = compute_yule(text)

        # All words unique
        assert result.metadata["vocabulary_size"] == 4
        assert result.metadata["token_count"] == 4
