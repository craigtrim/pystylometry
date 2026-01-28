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


class TestMetadataContents:
    """Test metadata contents and completeness."""

    def test_metadata_word_lists(self) -> None:
        """Test that metadata contains word lists."""
        text = "Simple test text for metadata check."
        result = compute_stylistic_markers(text)

        assert "contraction_list" in result.metadata
        assert "intensifier_list" in result.metadata
        assert "hedge_list" in result.metadata
        assert "modal_list" in result.metadata
        assert "negation_list" in result.metadata

    def test_metadata_punctuation_counts(self) -> None:
        """Test that metadata contains punctuation counts."""
        text = "Test! Really? Yes..."
        result = compute_stylistic_markers(text)

        assert "punctuation_counts" in result.metadata
        punct = result.metadata["punctuation_counts"]
        assert "exclamation" in punct
        assert "question" in punct
        assert "ellipsis" in punct

    def test_metadata_detailed_counts(self) -> None:
        """Test that metadata contains detailed marker counts."""
        text = "I can't really believe it's very good!"
        result = compute_stylistic_markers(text)

        assert "all_contraction_counts" in result.metadata
        assert "all_intensifier_counts" in result.metadata
        assert "all_hedge_counts" in result.metadata
        assert "all_negation_counts" in result.metadata
