"""Comprehensive tests for hapax legomena and vocabulary richness metrics."""

from pystylometry.lexical import compute_hapax_ratios


class TestHapaxMetadata:
    """Test metadata returned with hapax results."""

    def test_metadata_contains_counts(self):
        """Test that metadata contains token_count and vocabulary_size."""
        text = "one two three one two one"
        result = compute_hapax_ratios(text)

        assert "total_token_count" in result.metadata
        assert "total_vocabulary_size" in result.metadata

        assert result.metadata["total_token_count"] == 6
        assert result.metadata["total_vocabulary_size"] == 3

    def test_metadata_consistency(self):
        """Test that metadata counts are consistent with results."""
        text = "the quick brown fox"
        result = compute_hapax_ratios(text)

        # All words unique, so hapax_count should equal vocabulary_size
        assert result.hapax_count == result.metadata["total_vocabulary_size"]

        # hapax_ratio should equal hapax_count / token_count
        expected_ratio = result.hapax_count / result.metadata["total_token_count"]
        assert abs(result.hapax_ratio - expected_ratio) < 0.001
