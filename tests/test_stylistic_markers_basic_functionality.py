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


class TestStylisticMarkersBasicFunctionality:
    """Test basic stylistic markers functionality."""

    def test_returns_correct_type(self) -> None:
        """Test that compute_stylistic_markers returns StylisticMarkersResult."""
        from pystylometry._types import StylisticMarkersResult

        text = "This is a simple test sentence."
        result = compute_stylistic_markers(text)

        assert isinstance(result, StylisticMarkersResult)

    def test_basic_text_analysis(self) -> None:
        """Test basic text analysis returns expected fields."""
        text = "I can't believe it's really happening! This is absolutely incredible."
        result = compute_stylistic_markers(text)

        # Check required fields exist
        assert hasattr(result, "contraction_ratio")
        assert hasattr(result, "contraction_count")
        assert hasattr(result, "intensifier_density")
        assert hasattr(result, "hedging_density")
        assert hasattr(result, "modal_density")
        assert hasattr(result, "negation_density")
        assert hasattr(result, "exclamation_density")
        assert hasattr(result, "metadata")

    def test_word_count_in_metadata(self) -> None:
        """Test that word count is correctly recorded in metadata."""
        text = "one two three four five"
        result = compute_stylistic_markers(text)

        assert "word_count" in result.metadata
        assert result.metadata["word_count"] == 5

    def test_density_per_100_words(self) -> None:
        """Test that densities are normalized per 100 words."""
        # Create text with exactly 100 words and 2 intensifiers
        text = " ".join(["word"] * 98 + ["very", "really"])
        result = compute_stylistic_markers(text)

        # With 2 intensifiers in 100 words, density should be 2.0
        assert result.intensifier_count == 2
        assert abs(result.intensifier_density - 2.0) < 0.01
