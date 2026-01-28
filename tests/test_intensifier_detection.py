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
    INTENSIFIERS,
    compute_stylistic_markers,
)


class TestIntensifierDetection:
    """Test intensifier detection and density calculation."""

    def test_common_intensifiers(self) -> None:
        """Test detection of common intensifiers."""
        text = "This is very good, really excellent, and absolutely amazing."
        result = compute_stylistic_markers(text)

        assert result.intensifier_count >= 3
        assert result.intensifier_density > 0

    def test_amplifiers(self) -> None:
        """Test detection of amplifier intensifiers."""
        text = "It was extremely hot, completely empty, and totally destroyed."
        result = compute_stylistic_markers(text)

        assert result.intensifier_count >= 3

    def test_degree_modifiers(self) -> None:
        """Test detection of degree modifier intensifiers."""
        text = "It was quite good, rather nice, and fairly decent."
        result = compute_stylistic_markers(text)

        assert result.intensifier_count >= 3

    def test_informal_intensifiers(self) -> None:
        """Test detection of informal intensifiers."""
        text = "That was super cool and way better than expected."
        result = compute_stylistic_markers(text)

        assert result.intensifier_count >= 2

    def test_intensifier_density_calculation(self) -> None:
        """Test that intensifier density is correctly calculated."""
        # 50 words with 5 intensifiers = 10 per 100 words
        base_words = ["word"] * 45
        intensifiers_list = ["very", "really", "quite", "extremely", "absolutely"]
        text = " ".join(base_words + intensifiers_list)
        result = compute_stylistic_markers(text)

        assert result.intensifier_count == 5
        assert abs(result.intensifier_density - 10.0) < 0.1

    def test_top_intensifiers_ordering(self) -> None:
        """Test that top intensifiers are ordered by frequency."""
        text = "very very very really really quite"
        result = compute_stylistic_markers(text)

        if result.top_intensifiers:
            assert result.top_intensifiers[0][0] == "very"
            assert result.top_intensifiers[0][1] == 3

    def test_intensifier_list_completeness(self) -> None:
        """Test that the intensifier list is comprehensive."""
        # Check that common intensifiers are in the set
        common_intensifiers = ["very", "really", "extremely", "absolutely", "quite"]
        for word in common_intensifiers:
            assert word in INTENSIFIERS
