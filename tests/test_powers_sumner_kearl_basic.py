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
    compute_powers_sumner_kearl,
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


class TestPowersSumnerKearlBasic:
    """Basic functionality tests for Powers-Sumner-Kearl."""

    def test_basic_computation(self, simple_text):
        """Test basic PSK computation."""
        result = compute_powers_sumner_kearl(simple_text)
        assert isinstance(result.psk_score, float)
        assert isinstance(result.grade_level, float)

    def test_all_fields_present(self, simple_text):
        """Test all result fields are present."""
        result = compute_powers_sumner_kearl(simple_text)
        assert hasattr(result, "psk_score")
        assert hasattr(result, "grade_level")
        assert hasattr(result, "avg_sentence_length")
        assert hasattr(result, "avg_syllables_per_word")
        assert hasattr(result, "total_sentences")
        assert hasattr(result, "total_words")
        assert hasattr(result, "total_syllables")
        assert hasattr(result, "metadata")

    def test_empty_text(self):
        """Test with empty text."""
        result = compute_powers_sumner_kearl("")
        assert math.isnan(result.psk_score)
        assert math.isnan(result.grade_level)
