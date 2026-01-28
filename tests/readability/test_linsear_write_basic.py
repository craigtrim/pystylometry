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

import math

import pytest

from pystylometry.readability import (
    compute_linsear_write,
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


class TestLinsearWriteBasic:
    """Basic functionality tests for Linsear Write."""

    def test_basic_computation(self, simple_text):
        """Test basic Linsear Write computation."""
        result = compute_linsear_write(simple_text)
        assert isinstance(result.linsear_score, float)
        assert isinstance(result.grade_level, float)  # Now float (mean across chunks)
        assert result.grade_level >= 0

    def test_all_fields_present(self, simple_text):
        """Test all result fields are present."""
        result = compute_linsear_write(simple_text)
        assert hasattr(result, "linsear_score")
        assert hasattr(result, "grade_level")
        assert hasattr(result, "easy_word_count")
        assert hasattr(result, "hard_word_count")
        assert hasattr(result, "avg_sentence_length")
        assert hasattr(result, "metadata")

    def test_empty_text(self):
        """Test with empty text."""
        result = compute_linsear_write("")
        assert math.isnan(result.linsear_score)
        assert math.isnan(result.grade_level)  # Now nan for empty
