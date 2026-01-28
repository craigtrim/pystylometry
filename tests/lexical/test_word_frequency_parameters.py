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
def simple_text():
    """Simple text with common words."""
    return (
        "The cat sat on the mat. The dog ran in the park. "
        "A boy and a girl play with a ball. "
        "The sun is hot. The sky is blue. "
    ) * 5  # Repeat to get enough tokens


class TestWordFrequencyParameters:
    """Parameter validation tests."""

    def test_invalid_corpus(self, simple_text):
        """Test invalid corpus name raises ValueError."""
        with pytest.raises(ValueError, match="Only 'coca' corpus"):
            compute_word_frequency_sophistication(simple_text, frequency_corpus="invalid")

    def test_custom_rare_threshold(self, academic_text):
        """Test with custom rare_threshold."""
        result_default = compute_word_frequency_sophistication(academic_text)
        result_custom = compute_word_frequency_sophistication(academic_text, rare_threshold=5000)

        # With lower threshold, more words should be classified as rare
        assert result_custom.rare_word_ratio >= result_default.rare_word_ratio
        assert result_custom.metadata["rare_threshold"] == 5000

    def test_custom_common_threshold(self, academic_text):
        """Test with custom common_threshold."""
        result_default = compute_word_frequency_sophistication(academic_text)
        result_custom = compute_word_frequency_sophistication(academic_text, common_threshold=2000)

        # With higher threshold, more words should be classified as common
        assert result_custom.common_word_ratio >= result_default.common_word_ratio
        assert result_custom.metadata["common_threshold"] == 2000
