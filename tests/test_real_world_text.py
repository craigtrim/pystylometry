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


class TestRealWorldText:
    """Test with realistic text samples."""

    def test_formal_academic_text(self) -> None:
        """Test analysis of formal academic text."""
        text = """
        The results of this study suggest that the proposed methodology
        may be applicable to a wide range of scenarios. It appears that
        the correlation between variables is statistically significant.
        We must consider, however, that these findings are preliminary.
        """
        result = compute_stylistic_markers(text)

        # Formal text should have low contraction ratio
        assert result.contraction_ratio < 0.5
        # Should have hedges (suggest, may, appears, however)
        assert result.hedging_count > 0
        # Should have modals
        assert result.modal_density > 0

    def test_informal_conversational_text(self) -> None:
        """Test analysis of informal conversational text."""
        text = """
        I can't believe you're really going! That's absolutely amazing!
        You've got to tell me everything when you get back, okay?
        It's gonna be so much fun! Don't forget to take pictures!
        """
        result = compute_stylistic_markers(text)

        # Informal text should have high contraction ratio
        assert result.contraction_ratio > 0.5
        # Should have intensifiers (really, absolutely, so much)
        assert result.intensifier_count > 0
        # Should have exclamations
        assert result.exclamation_density > 0

    def test_dialogue_heavy_text(self) -> None:
        """Test analysis of dialogue-heavy text."""
        text = """
        "What do you mean?" she asked.
        "I can't explain it," he replied. "It's just... complicated."
        "That's not good enough!" she exclaimed.
        "Maybe you're right," he admitted.
        """
        result = compute_stylistic_markers(text)

        # Should have quotation marks
        assert result.quotation_density > 0
        # Should have question marks
        assert result.question_density > 0
        # Should have contractions
        assert result.contraction_count > 0
        # Should have hedges (maybe)
        assert result.hedging_count > 0

    def test_technical_documentation(self) -> None:
        """Test analysis of technical documentation."""
        text = """
        To install the package, you must run the following command:
        pip install pystylometry

        This will install all required dependencies. You should ensure
        that your Python version is 3.9 or higher. If you encounter
        any issues, please check the documentation.
        """
        result = compute_stylistic_markers(text)

        # Technical docs should have modals (must, should)
        assert result.modal_density > 0
        # Should have colons for instructions
        assert result.colon_density > 0
