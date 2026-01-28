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
    compute_fry,
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


class TestFryBasic:
    """Basic functionality tests for Fry."""

    def test_basic_computation(self, simple_text):
        """Test basic Fry computation."""
        result = compute_fry(simple_text)
        assert isinstance(result.avg_sentence_length, float)
        assert isinstance(result.avg_syllables_per_100, float)
        assert isinstance(result.grade_level, str)
        assert isinstance(result.graph_zone, str)

    def test_all_fields_present(self, simple_text):
        """Test all result fields are present."""
        result = compute_fry(simple_text)
        assert hasattr(result, "avg_sentence_length")
        assert hasattr(result, "avg_syllables_per_100")
        assert hasattr(result, "grade_level")
        assert hasattr(result, "graph_zone")
        assert hasattr(result, "metadata")

    def test_empty_text(self):
        """Test with empty text."""
        result = compute_fry("")
        assert math.isnan(result.avg_sentence_length)
        assert result.grade_level == "Unknown"
        assert result.graph_zone == "invalid"
