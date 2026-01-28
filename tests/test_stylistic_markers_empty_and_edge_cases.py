"""Comprehensive tests for stylistic markers module.

This module tests the stylistic markers functionality, including contraction
detection, intensifier analysis, hedge detection, modal auxiliary classification,
negation patterns, and punctuation style analysis.

Related GitHub Issues:
    #20 - Stylistic Markers
    https://github.com/craigtrim/pystylometry/issues/20

Test coverage:
    - Basic functionality and return type validation
    - Contraction detection and ratio calculation
    - Intensifier detection and density calculation
    - Hedge detection and density calculation
    - Modal auxiliary analysis (epistemic vs deontic)
    - Negation pattern detection
    - Punctuation style analysis (8 types)
    - Edge cases (empty text, no markers, short text)
    - Density normalization (per 100 words)
"""

from pystylometry.stylistic.markers import (
    compute_stylistic_markers,
)


class TestStylisticMarkersEmptyAndEdgeCases:
    """Test edge cases and empty input handling."""

    def test_empty_text(self) -> None:
        """Test handling of empty text."""
        result = compute_stylistic_markers("")

        assert result.contraction_ratio == 0.0
        assert result.contraction_count == 0
        assert result.intensifier_density == 0.0
        assert result.metadata["word_count"] == 0

    def test_whitespace_only(self) -> None:
        """Test handling of whitespace-only text."""
        result = compute_stylistic_markers("   \n\t  ")

        assert result.contraction_ratio == 0.0
        assert result.contraction_count == 0
        assert result.metadata["word_count"] == 0

    def test_single_word(self) -> None:
        """Test handling of single word input."""
        result = compute_stylistic_markers("hello")

        assert result.metadata["word_count"] == 1
        assert result.contraction_ratio == 0.0

    def test_no_markers_in_text(self) -> None:
        """Test text with no stylistic markers."""
        text = "The sun rose over the mountains. Birds sang in the trees."
        result = compute_stylistic_markers(text)

        # Should have zero counts for many markers
        assert result.contraction_count == 0
        assert result.exclamation_density == 0.0
        assert result.question_density == 0.0

    def test_punctuation_only(self) -> None:
        """Test text with only punctuation."""
        result = compute_stylistic_markers("!!! ??? ...")

        # Should handle gracefully
        assert result.metadata["word_count"] == 0
