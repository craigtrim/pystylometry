"""Tests for additional readability formulas.

Related GitHub Issue:
    #16 - Additional Readability Formulas
    https://github.com/craigtrim/pystylometry/issues/16

Tests all 5 additional readability formulas:
    - Dale-Chall Readability
    - Linsear Write Formula
    - Fry Readability Graph
    - FORCAST Formula
    - Powers-Sumner-Kearl Formula
"""

import pytest

from pystylometry.readability import (
    compute_dale_chall,
)

# ===== Fixtures =====


# ===== Dale-Chall Tests =====


@pytest.fixture
def simple_text():
    """Simple text with common words for children."""
    return (
        "The cat sat on the mat. The dog ran in the park. "
        "A boy and a girl play with a ball. The sun is hot. "
        "I like to run and jump. We can go to the zoo. "
    ) * 5  # Repeat to get enough tokens


class TestDaleChallBasic:
    """Basic functionality tests for Dale-Chall."""

    def test_basic_computation(self, simple_text):
        """Test basic Dale-Chall computation."""
        result = compute_dale_chall(simple_text)
        assert isinstance(result.dale_chall_score, float)
        assert isinstance(result.grade_level, str)
        assert isinstance(result.difficult_word_count, int)
        assert result.total_words > 0

    def test_all_fields_present(self, simple_text):
        """Test all result fields are present."""
        result = compute_dale_chall(simple_text)
        assert hasattr(result, "dale_chall_score")
        assert hasattr(result, "grade_level")
        assert hasattr(result, "difficult_word_count")
        assert hasattr(result, "difficult_word_ratio")
        assert hasattr(result, "avg_sentence_length")
        assert hasattr(result, "total_words")
        assert hasattr(result, "metadata")

    def test_metadata_complete(self, simple_text):
        """Test metadata contains required fields."""
        result = compute_dale_chall(simple_text)
        assert "sentence_count" in result.metadata
        assert "raw_score" in result.metadata
        assert "adjusted" in result.metadata
        assert "difficult_word_pct" in result.metadata
