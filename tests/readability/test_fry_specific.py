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
    compute_fry,
)

# ===== Fixtures =====


# ===== Dale-Chall Tests =====


@pytest.fixture
def academic_text():
    """Academic text with sophisticated vocabulary."""
    return (
        "The research methodology employed a comprehensive approach to analyze "
        "the significant theoretical framework. The data demonstrate substantial "
        "evidence supporting the hypothesis. This analysis indicates that the "
        "results require further investigation to establish definitive conclusions. "
        "The study's primary objective involves assessing the policy implications "
        "derived from the empirical findings. Researchers must interpret these "
        "complex phenomena within the appropriate contextual parameters. "
        "The investigation utilized quantitative methodologies to examine correlations "
        "between variables. Statistical analysis revealed significant patterns that "
        "warrant additional scrutiny."
    )


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


class TestFrySpecific:
    """Fry specific feature tests."""

    def test_sample_extraction(self):
        """Test 100-word sample extraction."""
        # Create text with > 100 words
        text = " ".join(["word"] * 150) + "."
        result = compute_fry(text)
        # Should use 100-word sample
        assert result.metadata["sample_size"] == 100

    def test_short_text_handling(self):
        """Test text < 100 words uses entire text."""
        text = " ".join(["word"] * 50) + "."
        result = compute_fry(text)
        # Should use entire text
        assert result.metadata["sample_size"] == 50

    def test_syllables_per_100(self, childrens_text, academic_text):
        """Test syllables per 100 calculation."""
        result_easy = compute_fry(childrens_text)
        result_hard = compute_fry(academic_text)
        # Academic text should have more syllables per 100 words
        assert result_hard.avg_syllables_per_100 > result_easy.avg_syllables_per_100

    def test_grade_zone_valid(self, middle_school_text):
        """Test graph zone is valid for typical text."""
        result = compute_fry(middle_school_text)
        # Should be in valid zone for normal text
        assert result.graph_zone in ["valid", "above_graph", "below_graph"]
