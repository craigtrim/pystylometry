"""Comprehensive tests for Automated Readability Index (ARI) computation."""

from pystylometry.readability import compute_ari


class TestARIBasic:
    """Test basic ARI functionality."""

    def test_simple_sentence(self):
        """Test single simple sentence."""
        text = "The cat sat on the mat."
        result = compute_ari(text)

        assert isinstance(result.ari_score, float)
        assert isinstance(result.grade_level, (int, float))  # Float for chunked mean
        assert isinstance(result.age_range, str)
        assert result.grade_level >= 0
        assert result.grade_level <= 20
        assert not result.metadata["reliable"]  # < 100 words

    def test_expected_values(self):
        """Test known expected values for calibration."""
        # From docstring example
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_ari(text)

        # Should match docstring example
        assert abs(result.ari_score - 0.1) < 0.2  # Allow tolerance
        assert result.grade_level == 0
        assert "Kindergarten" in result.age_range
        assert not result.metadata["reliable"]

    def test_reliable_text(self):
        """Test text that meets reliability threshold."""
        # Generate text with 100+ words
        words = ["The", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"]
        text = " ".join(words * 12) + "."  # 108 words

        result = compute_ari(text)
        assert result.metadata["reliable"]
        assert result.metadata["word_count"] >= 100
