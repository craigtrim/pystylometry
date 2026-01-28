"""Tests for sentence type classification (Issue #18)."""

from pystylometry.syntactic.sentence_types import compute_sentence_types

# ===== Fixtures =====


# ===== Basic Functionality Tests =====


class TestGenreSpecific:
    """Test genre-specific patterns."""

    def test_academic_text(self):
        """Academic text should have high complex ratio."""
        text = (
            "The research examined the relationship between variables. "
            "Although the data were limited, the findings suggested significant trends. "
            "When analyzed further, the results indicated stronger correlations."
        )
        result = compute_sentence_types(text)

        # Academic: high complex
        assert result.complex_ratio >= 0.3

    def test_fiction_text(self):
        """Fiction should have mixed types."""
        text = (
            "She walked down the street. "
            "The rain fell and the wind blew. "
            "When she reached the corner, she stopped. "
            "What a beautiful sight!"
        )
        result = compute_sentence_types(text)

        # Fiction: mixed types
        types_present = sum(
            [
                result.simple_count > 0,
                result.compound_count > 0,
                result.complex_count > 0,
            ]
        )
        assert types_present >= 2

    def test_news_text(self):
        """News should have simple/compound dominant."""
        text = (
            "The mayor announced new policies yesterday. "
            "The changes will affect thousands of residents. "
            "Officials said the measures were necessary. "
            "Critics argued against the proposal."
        )
        result = compute_sentence_types(text)

        # News: mostly simple and declarative
        assert result.simple_ratio + result.compound_ratio >= 0.5
        assert result.declarative_ratio >= 0.9

    def test_instructional_text(self):
        """Instructional should have high imperative."""
        text = (
            "Open the package carefully. "
            "Remove the contents. "
            "Place the item on a flat surface. "
            "Connect the power cord."
        )
        result = compute_sentence_types(text)

        # Instructional: high imperative
        assert result.imperative_count >= 2

    def test_dialog_text(self):
        """Dialog should have interrogative/exclamatory."""
        text = "Are you ready? Yes, I am! What should we do? Let's go now!"
        result = compute_sentence_types(text)

        # Dialog: questions and exclamations
        assert result.interrogative_count + result.exclamatory_count >= 2
