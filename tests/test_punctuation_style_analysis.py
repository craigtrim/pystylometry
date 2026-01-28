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


class TestPunctuationStyleAnalysis:
    """Test punctuation style analysis."""

    def test_exclamation_marks(self) -> None:
        """Test detection of exclamation marks."""
        text = "Wow! Amazing! Incredible! This is great!"
        result = compute_stylistic_markers(text)

        assert result.exclamation_density > 0
        assert result.metadata["punctuation_counts"]["exclamation"] == 4

    def test_question_marks(self) -> None:
        """Test detection of question marks."""
        text = "What? Why? How? When did this happen?"
        result = compute_stylistic_markers(text)

        assert result.question_density > 0
        assert result.metadata["punctuation_counts"]["question"] == 4

    def test_quotation_marks(self) -> None:
        """Test detection of quotation marks."""
        text = 'He said "hello" and she replied "goodbye".'
        result = compute_stylistic_markers(text)

        assert result.quotation_density > 0
        assert result.metadata["punctuation_counts"]["quotation"] >= 4

    def test_parentheses(self) -> None:
        """Test detection of parenthetical expressions."""
        text = "The result (as expected) was good. We tried (and failed) again."
        result = compute_stylistic_markers(text)

        assert result.parenthetical_density > 0
        assert result.metadata["punctuation_counts"]["parenthetical"] == 4

    def test_ellipses(self) -> None:
        """Test detection of ellipses."""
        text = "I wonder... maybe... perhaps... who knows..."
        result = compute_stylistic_markers(text)

        assert result.ellipsis_density > 0
        assert result.metadata["punctuation_counts"]["ellipsis"] == 4

    def test_unicode_ellipsis(self) -> None:
        """Test detection of unicode ellipsis character."""
        text = "I wonder… maybe… perhaps…"
        result = compute_stylistic_markers(text)

        assert result.metadata["punctuation_counts"]["ellipsis"] == 3

    def test_dashes(self) -> None:
        """Test detection of dashes (em-dash, en-dash)."""
        text = "This—and that—are different. Also this–that–those."
        result = compute_stylistic_markers(text)

        assert result.dash_density > 0
        assert result.metadata["punctuation_counts"]["dash"] >= 4

    def test_double_hyphen_as_dash(self) -> None:
        """Test detection of double hyphen as dash."""
        text = "This--that--those are options."
        result = compute_stylistic_markers(text)

        assert result.metadata["punctuation_counts"]["dash"] == 2

    def test_semicolons(self) -> None:
        """Test detection of semicolons."""
        text = "First point; second point; third point; conclusion."
        result = compute_stylistic_markers(text)

        assert result.semicolon_density > 0
        assert result.metadata["punctuation_counts"]["semicolon"] == 3

    def test_colons(self) -> None:
        """Test detection of colons."""
        text = "Consider this: one option. Also: another option. Finally: the last."
        result = compute_stylistic_markers(text)

        assert result.colon_density > 0
        assert result.metadata["punctuation_counts"]["colon"] == 3

    def test_punctuation_density_normalization(self) -> None:
        """Test that punctuation densities are normalized per 100 words."""
        # 50 words with 5 exclamations = 10 per 100 words
        text = " ".join(["word"] * 50) + " !!!!! "
        result = compute_stylistic_markers(text)

        # Note: exclamations aren't words, so word count stays 50
        expected_density = 5 * (100.0 / 50)  # = 10.0
        assert abs(result.exclamation_density - expected_density) < 0.1
