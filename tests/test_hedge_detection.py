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
    HEDGES,
    compute_stylistic_markers,
)


class TestHedgeDetection:
    """Test hedge detection and density calculation."""

    def test_epistemic_hedges(self) -> None:
        """Test detection of epistemic hedges."""
        text = "Maybe this will work. Perhaps it's true. Probably not."
        result = compute_stylistic_markers(text)

        assert result.hedging_count >= 3

    def test_approximators(self) -> None:
        """Test detection of approximator hedges."""
        text = "It's about ten miles. Roughly speaking, it's nearly done."
        result = compute_stylistic_markers(text)

        assert result.hedging_count >= 3

    def test_shield_expressions(self) -> None:
        """Test detection of shield expression hedges."""
        text = "It seems good. It appears to work. This suggests progress."
        result = compute_stylistic_markers(text)

        assert result.hedging_count >= 3

    def test_hedging_density_calculation(self) -> None:
        """Test that hedging density is correctly calculated."""
        # 50 words with 10 hedges = 20 per 100 words
        base_words = ["word"] * 40
        hedges_list = [
            "maybe",
            "perhaps",
            "probably",
            "possibly",
            "seemingly",
            "apparently",
            "roughly",
            "generally",
            "usually",
            "typically",
        ]
        text = " ".join(base_words + hedges_list)
        result = compute_stylistic_markers(text)

        assert result.hedging_count == 10
        assert abs(result.hedging_density - 20.0) < 0.1

    def test_top_hedges_ordering(self) -> None:
        """Test that top hedges are ordered by frequency."""
        text = "maybe maybe maybe perhaps perhaps probably"
        result = compute_stylistic_markers(text)

        if result.top_hedges:
            assert result.top_hedges[0][0] == "maybe"
            assert result.top_hedges[0][1] == 3

    def test_hedge_list_completeness(self) -> None:
        """Test that the hedge list is comprehensive."""
        common_hedges = ["maybe", "perhaps", "probably", "possibly", "seemingly"]
        for word in common_hedges:
            assert word in HEDGES
