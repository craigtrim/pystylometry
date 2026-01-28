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
    compute_forcast,
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


class TestFORCASTBasic:
    """Basic functionality tests for FORCAST."""

    def test_basic_computation(self, simple_text):
        """Test basic FORCAST computation."""
        result = compute_forcast(simple_text)
        assert isinstance(result.forcast_score, float)
        assert isinstance(result.grade_level, float)  # Now float (mean across chunks)
        assert result.grade_level >= 0

    def test_all_fields_present(self, simple_text):
        """Test all result fields are present."""
        result = compute_forcast(simple_text)
        assert hasattr(result, "forcast_score")
        assert hasattr(result, "grade_level")
        assert hasattr(result, "single_syllable_ratio")
        assert hasattr(result, "single_syllable_count")
        assert hasattr(result, "total_words")
        assert hasattr(result, "metadata")

    def test_empty_text(self):
        """Test with empty text."""
        result = compute_forcast("")
        assert math.isnan(result.forcast_score)
        assert math.isnan(result.grade_level)  # Now nan for empty
