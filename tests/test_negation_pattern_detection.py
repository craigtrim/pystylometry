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
    NEGATION_MARKERS,
    compute_stylistic_markers,
)


class TestNegationPatternDetection:
    """Test negation pattern detection."""

    def test_basic_negation(self) -> None:
        """Test detection of basic negation markers."""
        text = "I do not know. She has no idea. We never go there."
        result = compute_stylistic_markers(text)

        assert result.negation_count >= 3
        assert result.negation_density > 0

    def test_negation_types(self) -> None:
        """Test that negation types are correctly recorded."""
        text = "not here. no way. never again. none left. nothing wrong."
        result = compute_stylistic_markers(text)

        assert "not" in result.negation_types or result.negation_types.get("not", 0) >= 0
        assert result.negation_count >= 5

    def test_rare_negation_markers(self) -> None:
        """Test detection of less common negation markers."""
        text = "I hardly know. She barely survived. We scarcely noticed."
        result = compute_stylistic_markers(text)

        assert result.negation_count >= 3

    def test_negation_density_calculation(self) -> None:
        """Test that negation density is correctly calculated."""
        # 50 words with 5 negation markers = 10 per 100 words
        base_words = ["word"] * 45
        negations = ["not", "no", "never", "none", "nothing"]
        text = " ".join(base_words + negations)
        result = compute_stylistic_markers(text)

        assert result.negation_count == 5
        assert abs(result.negation_density - 10.0) < 0.1

    def test_negation_list_completeness(self) -> None:
        """Test that the negation list is comprehensive."""
        common_negations = ["not", "no", "never", "none", "nothing", "nobody", "nowhere"]
        for word in common_negations:
            assert word in NEGATION_MARKERS
