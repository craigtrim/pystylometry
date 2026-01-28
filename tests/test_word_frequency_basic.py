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


class TestWordFrequencyBasic:
    """Basic functionality tests."""

    def test_basic_computation(self, simple_text):
        """Test basic frequency sophistication computation."""
        result = compute_word_frequency_sophistication(simple_text)

        assert isinstance(result.mean_frequency_rank, float)
        assert isinstance(result.median_frequency_rank, float)
        assert isinstance(result.rare_word_ratio, float)
        assert isinstance(result.common_word_ratio, float)
        assert isinstance(result.academic_word_ratio, float)
        assert isinstance(result.advanced_word_ratio, float)
        assert isinstance(result.frequency_band_distribution, dict)
        assert isinstance(result.rarest_words, list)
        assert isinstance(result.most_common_words, list)
        assert isinstance(result.metadata, dict)

    def test_all_fields_present(self, academic_text):
        """Test all result fields are present and correct types."""
        result = compute_word_frequency_sophistication(academic_text)

        # Check all dataclass fields exist
        assert hasattr(result, "mean_frequency_rank")
        assert hasattr(result, "median_frequency_rank")
        assert hasattr(result, "rare_word_ratio")
        assert hasattr(result, "common_word_ratio")
        assert hasattr(result, "academic_word_ratio")
        assert hasattr(result, "advanced_word_ratio")
        assert hasattr(result, "frequency_band_distribution")
        assert hasattr(result, "rarest_words")
        assert hasattr(result, "most_common_words")
        assert hasattr(result, "metadata")

    def test_metadata_complete(self, simple_text):
        """Test metadata contains all required fields."""
        result = compute_word_frequency_sophistication(simple_text)

        # Required metadata fields
        assert "frequency_corpus" in result.metadata
        assert "rare_threshold" in result.metadata
        assert "common_threshold" in result.metadata
        assert "total_words" in result.metadata
        assert "unique_words" in result.metadata
        assert "unknown_words" in result.metadata
        assert "unknown_word_ratio" in result.metadata
        assert "frequency_list_size" in result.metadata
        assert "max_frequency_rank" in result.metadata
