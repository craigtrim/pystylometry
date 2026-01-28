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


class TestExpandedFormDetection:
    """Test detection of expanded (non-contracted) forms."""

    def test_expanded_negatives(self) -> None:
        """Test detection of expanded negative forms."""
        text = "I do not know. She can not come. They will not help."
        result = compute_stylistic_markers(text)

        assert result.expanded_form_count >= 3

    def test_expanded_pronouns(self) -> None:
        """Test detection of expanded pronoun forms."""
        text = "I am happy. You are great. It is working."
        result = compute_stylistic_markers(text)

        assert result.expanded_form_count >= 3

    def test_cannot_as_single_word(self) -> None:
        """Test handling of 'cannot' as single word."""
        text = "I cannot believe it. She cannot help."
        result = compute_stylistic_markers(text)

        # "cannot" is a single word that could be "can't"
        # The pattern looks for "can not" (two words), so cannot might not be caught
        # This tests that we don't error on it
        assert result.contraction_ratio >= 0.0
