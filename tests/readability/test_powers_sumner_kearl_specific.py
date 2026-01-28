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
    compute_powers_sumner_kearl,
)

# ===== Fixtures =====


# ===== Dale-Chall Tests =====


@pytest.fixture
def childrens_text():
    """Children's book text with very simple vocabulary."""
    return (
        "The dog is big. The cat is small. I like the dog. "
        "I like the cat. The dog runs fast. The cat jumps high. "
        "The boy has a red ball. The girl has a blue doll. "
        "They play in the sun. It is fun to play. "
        "The dog can run. The cat can jump. I can play too. "
        "We go to the park. The park is big and green. "
    ) * 3


@pytest.fixture
def middle_school_text():
    """Middle school level text."""
    return (
        "The American Revolution was a time when the colonies fought for independence. "
        "George Washington led the Continental Army against the British forces. "
        "The Declaration of Independence was signed on July 4, 1776. "
        "This important document stated that all men are created equal. "
        "The war lasted for eight years before the colonists won their freedom. "
        "After the war, leaders worked together to create a new government. "
        "They wrote the Constitution to protect people's rights and establish laws. "
        "The new nation faced many challenges as it grew and developed."
    )


@pytest.fixture
def simple_text():
    """Simple text with common words for children."""
    return (
        "The cat sat on the mat. The dog ran in the park. "
        "A boy and a girl play with a ball. The sun is hot. "
        "I like to run and jump. We can go to the zoo. "
    ) * 5  # Repeat to get enough tokens


class TestPowersSumnerKearlSpecific:
    """PSK specific feature tests."""

    def test_primary_grade_text(self, childrens_text):
        """Test PSK on primary grade text."""
        result = compute_powers_sumner_kearl(childrens_text)
        # Children's text should be low grade (1-4)
        assert result.grade_level <= 5.0

    def test_comparison_to_flesch(self, simple_text):
        """Test PSK includes Flesch comparison."""
        result = compute_powers_sumner_kearl(simple_text)
        # Metadata should include Flesch scores
        assert "flesch_reading_ease" in result.metadata
        assert "flesch_kincaid_grade" in result.metadata
        assert "difference_from_flesch" in result.metadata

    def test_negative_score_handling(self):
        """Test handling of very simple text (can produce negative scores)."""
        # Very short sentences with simple words
        text = "I go. We go. You go. He goes. She goes."
        result = compute_powers_sumner_kearl(text)
        # PSK can produce negative scores for very simple text
        # grade_level should handle this (might be negative)
        assert isinstance(result.grade_level, float)

    def test_decimal_grade_level(self, middle_school_text):
        """Test grade level is continuous (decimal)."""
        result = compute_powers_sumner_kearl(middle_school_text)
        # Grade level should be rounded to 1 decimal place
        assert result.grade_level == round(result.psk_score, 1)
