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
def mixed_sophistication_text():
    """Text with mixed sophistication levels."""
    return (
        "The quick brown fox jumps over the lazy dog. However, this "
        "exemplifies the utilization of both rudimentary and sophisticated "
        "lexical constructs. Basic words and complex terminology coexist "
        "within the same discourse, demonstrating heterogeneous vocabulary. "
        "The analysis requires interpretation of multifaceted linguistic patterns."
    )


@pytest.fixture
def simple_text():
    """Simple text with common words."""
    return (
        "The cat sat on the mat. The dog ran in the park. "
        "A boy and a girl play with a ball. "
        "The sun is hot. The sky is blue. "
    ) * 5  # Repeat to get enough tokens


class TestWordFrequencyConstraints:
    """Constraint validation tests."""

    def test_ratios_in_range(self, academic_text):
        """Test all ratios are between 0 and 1."""
        result = compute_word_frequency_sophistication(academic_text)

        assert 0.0 <= result.rare_word_ratio <= 1.0
        assert 0.0 <= result.common_word_ratio <= 1.0
        assert 0.0 <= result.academic_word_ratio <= 1.0
        assert 0.0 <= result.advanced_word_ratio <= 1.0
        assert 0.0 <= result.metadata["unknown_word_ratio"] <= 1.0

    def test_ranks_positive(self, simple_text):
        """Test mean and median ranks are positive."""
        result = compute_word_frequency_sophistication(simple_text)

        assert result.mean_frequency_rank >= 1.0
        assert result.median_frequency_rank >= 1.0

    def test_frequency_band_sum(self, academic_text):
        """Test frequency band distribution sums to 1.0."""
        result = compute_word_frequency_sophistication(academic_text)

        band_sum = sum(result.frequency_band_distribution.values())
        # Allow small floating point error
        assert abs(band_sum - 1.0) < 1e-9

    def test_rarest_vs_common_ranks(self, mixed_sophistication_text):
        """Test rarest words have higher ranks than common words."""
        result = compute_word_frequency_sophistication(mixed_sophistication_text)

        if result.rarest_words and result.most_common_words:
            # Rarest words should have higher ranks than common words
            # Check the top rarest vs top common
            assert result.rarest_words[0][1] >= result.most_common_words[0][1]
