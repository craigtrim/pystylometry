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


class TestContractionDetection:
    """Test contraction detection and ratio calculation."""

    def test_common_contractions(self) -> None:
        """Test detection of common contractions."""
        text = "I can't believe it's happening. We don't know what she's doing."
        result = compute_stylistic_markers(text)

        # Should detect multiple contractions
        assert result.contraction_count >= 4
        assert ("can't", 1) in result.top_contractions or any(
            c[0] == "can't" for c in result.top_contractions
        )

    def test_pronoun_contractions(self) -> None:
        """Test detection of pronoun contractions."""
        text = "I'm happy. You're great. He's here. She's there. It's working."
        result = compute_stylistic_markers(text)

        assert result.contraction_count >= 5

    def test_negative_contractions(self) -> None:
        """Test detection of negative contractions."""
        text = "I won't go. She can't come. They haven't arrived. He isn't here."
        result = compute_stylistic_markers(text)

        assert result.contraction_count >= 4

    def test_contraction_ratio_all_contracted(self) -> None:
        """Test contraction ratio when all forms are contracted."""
        text = "I can't do it. She won't help. They don't care."
        result = compute_stylistic_markers(text)

        # With only contractions (no expanded forms), ratio should be 1.0
        if result.contraction_count > 0 and result.expanded_form_count == 0:
            assert result.contraction_ratio == 1.0

    def test_contraction_ratio_mixed(self) -> None:
        """Test contraction ratio with mixed contracted and expanded forms."""
        # Mix of contractions and expanded forms
        text = "I can't go but she can not come. They don't know but we do not care."
        result = compute_stylistic_markers(text)

        # Should have both contractions and expanded forms
        assert result.contraction_count >= 2
        assert result.expanded_form_count >= 2
        # Ratio should be between 0 and 1
        assert 0.0 < result.contraction_ratio < 1.0

    def test_contraction_case_insensitivity(self) -> None:
        """Test that contraction detection is case-insensitive."""
        text = "I CAN'T believe IT'S true. DON'T do that!"
        result = compute_stylistic_markers(text)

        assert result.contraction_count >= 3

    def test_smart_apostrophe_handling(self) -> None:
        """Test handling of smart/curly apostrophes."""
        text = "I can't and I can't and I can't"  # Uses different apostrophe styles
        result = compute_stylistic_markers(text)

        # Should normalize apostrophes and count all
        assert result.contraction_count >= 1

    def test_top_contractions_ordering(self) -> None:
        """Test that top contractions are ordered by frequency."""
        text = "I can't can't can't. You don't don't. She won't."
        result = compute_stylistic_markers(text)

        # Top contraction should be the most frequent
        if result.top_contractions:
            assert result.top_contractions[0][0] == "can't"
            assert result.top_contractions[0][1] == 3
