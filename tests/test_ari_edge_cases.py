"""Comprehensive tests for Automated Readability Index (ARI) computation."""

import math

from pystylometry.readability import compute_ari


class TestARIEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string(self):
        """Test empty string input."""
        result = compute_ari("")

        assert math.isnan(result.ari_score)
        assert math.isnan(result.grade_level)
        assert result.age_range == "Unknown"
        assert result.metadata["sentence_count"] == 0
        assert result.metadata["word_count"] == 0
        assert result.metadata["character_count"] == 0
        assert result.metadata["characters_per_word"] == 0.0
        assert result.metadata["words_per_sentence"] == 0.0
        assert not result.metadata["reliable"]

    def test_whitespace_only(self):
        """Test string with only whitespace."""
        result = compute_ari("   \n\t  ")

        assert math.isnan(result.ari_score)
        assert math.isnan(result.grade_level)
        assert not result.metadata["reliable"]

    def test_very_simple_text(self):
        """Test extremely simple text."""
        text = "Go. Run. Stop. Hi."
        result = compute_ari(text)

        # Should be low grade level
        assert result.grade_level <= 5

    def test_single_word(self):
        """Test single word."""
        result = compute_ari("Hello")

        assert result.metadata["word_count"] == 1
        assert result.metadata["sentence_count"] >= 0
        assert not result.metadata["reliable"]
