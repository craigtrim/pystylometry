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


class TestSpecialCharacters:
    """Test handling of special characters and unicode."""

    def test_smart_quotes(self) -> None:
        """Test handling of smart/curly quotes."""
        text = '"Hello," she said. "How are you?"'
        result = compute_stylistic_markers(text)

        # Should detect quotation marks
        assert result.quotation_density > 0

    def test_mixed_apostrophe_styles(self) -> None:
        """Test handling of mixed apostrophe styles."""
        text = "I can't and I can't and I can't"  # Mix of straight and curly
        result = compute_stylistic_markers(text)

        # Should normalize and count
        assert result.contraction_count >= 1

    def test_non_ascii_characters(self) -> None:
        """Test handling of non-ASCII characters in text."""
        text = "The café wasn't bad. I couldn't complain about the naïve décor."
        result = compute_stylistic_markers(text)

        # Should still detect contractions
        assert result.contraction_count >= 2
