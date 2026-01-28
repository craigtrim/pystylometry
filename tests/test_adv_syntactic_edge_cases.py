"""Tests for advanced syntactic analysis (Issue #17)."""

import math

import pytest

from pystylometry.syntactic.advanced_syntactic import compute_advanced_syntactic

# ===== Fixtures =====


# ===== Basic Functionality Tests =====


@pytest.fixture
def complex_text():
    """Complex sentences with subordination and embedding."""
    return (
        "Although the research methodology that was employed demonstrated "
        "significant theoretical implications, the findings, which were "
        "published in a peer-reviewed journal, suggested that further "
        "investigation would be necessary before definitive conclusions "
        "could be drawn about the phenomena."
    )


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_text(self):
        """Test with empty text."""
        result = compute_advanced_syntactic("")

        # Should return NaN for ratios
        assert math.isnan(result.mean_parse_tree_depth)
        assert result.max_parse_tree_depth == 0
        assert result.t_unit_count == 0
        assert math.isnan(result.mean_t_unit_length)
        assert math.isnan(result.clausal_density)

        # Metadata should indicate warning
        assert "warning" in result.metadata

    def test_single_sentence(self):
        """Test with single sentence."""
        text = "The cat sat on the mat."
        result = compute_advanced_syntactic(text)

        # Should have valid results
        assert result.t_unit_count == 1
        assert result.metadata["sentence_count"] == 1
        assert not math.isnan(result.mean_parse_tree_depth)

    def test_very_short_sentence(self):
        """Test with very short sentence (5 words)."""
        text = "The cat sat there quietly."
        result = compute_advanced_syntactic(text)

        assert result.t_unit_count == 1
        assert result.mean_t_unit_length == pytest.approx(5.0, abs=1)

    def test_very_long_sentence(self, complex_text):
        """Test with very long, complex sentence (40+ words)."""
        result = compute_advanced_syntactic(complex_text)

        # Should handle long sentences
        assert result.metadata["word_count"] > 40
        assert result.mean_parse_tree_depth > 3  # Should be relatively deep

    def test_single_word_sentence(self):
        """Test with single-word sentence."""
        text = "Hello. Goodbye. Yes."
        result = compute_advanced_syntactic(text)

        assert result.t_unit_count == 3
        assert result.metadata["sentence_count"] == 3
