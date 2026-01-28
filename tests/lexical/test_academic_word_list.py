"""Tests for word frequency sophistication metrics.

Tests the implementation of vocabulary sophistication measurement using
corpus frequency data. Related to GitHub Issue #15.
"""

import pytest

from pystylometry.lexical import compute_word_frequency_sophistication

# ===== Fixtures =====


# ===== Basic Functionality Tests =====


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
        "The investigation utilized rigorous statistical procedures to evaluate "
        "the correlation between independent and dependent variables."
    )


@pytest.fixture
def childrens_text():
    """Children's text with simple vocabulary."""
    return (
        "The dog is big. The cat is small. I like the dog. "
        "I like the cat. The dog runs. The cat jumps. "
        "The boy has a ball. The girl has a doll. "
        "They play in the sun. It is fun. "
        "The ball is red. The doll is pink. "
        "I see a bird. The bird can fly. "
    ) * 3


class TestAcademicWordList:
    """Academic Word List tests."""

    def test_high_academic_ratio(self, academic_text):
        """Test text with many academic words."""
        result = compute_word_frequency_sophistication(academic_text)

        # Academic text should have reasonable academic word ratio
        # "analyze", "approach", "data", "research", "method", etc. are in AWL
        assert result.academic_word_ratio > 0.05  # At least 5% academic words

    def test_zero_academic_ratio(self, childrens_text):
        """Test text with no academic words."""
        result = compute_word_frequency_sophistication(childrens_text)

        # Children's text should have very few or no academic words
        assert result.academic_word_ratio < 0.1  # Less than 10%

    def test_academic_case_insensitive(self):
        """Test AWL matching is case-insensitive."""
        text_lower = "the research method is good"
        text_upper = "The RESEARCH METHOD is good"
        text_mixed = "The Research Method Is Good"

        result_lower = compute_word_frequency_sophistication(text_lower)
        result_upper = compute_word_frequency_sophistication(text_upper)
        result_mixed = compute_word_frequency_sophistication(text_mixed)

        # All should detect "research" and "method" as academic words
        assert result_lower.academic_word_ratio == result_upper.academic_word_ratio
        assert result_lower.academic_word_ratio == result_mixed.academic_word_ratio

    def test_academic_in_advanced(self, academic_text):
        """Test academic words contribute to advanced ratio."""
        result = compute_word_frequency_sophistication(academic_text)

        # Advanced ratio should be at least as high as academic ratio
        # (since advanced = rare OR academic)
        assert result.advanced_word_ratio >= result.academic_word_ratio
