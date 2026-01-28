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


class TestRarestCommonWords:
    """Rarest and most common words tests."""

    def test_rarest_words_count(self, academic_text):
        """Test rarest_words has up to 10 items."""
        result = compute_word_frequency_sophistication(academic_text)

        assert len(result.rarest_words) <= 10
        assert len(result.rarest_words) > 0  # Should have at least some words

    def test_most_common_words_count(self, simple_text):
        """Test most_common_words has up to 10 items."""
        result = compute_word_frequency_sophistication(simple_text)

        assert len(result.most_common_words) <= 10
        assert len(result.most_common_words) > 0

    def test_rarest_words_order(self, mixed_sophistication_text):
        """Test rarest words are in descending rank order."""
        result = compute_word_frequency_sophistication(mixed_sophistication_text)

        ranks = [rank for _, rank in result.rarest_words]
        # Should be in descending order (highest ranks first)
        assert ranks == sorted(ranks, reverse=True)

    def test_common_words_order(self, simple_text):
        """Test common words are in ascending rank order."""
        result = compute_word_frequency_sophistication(simple_text)

        ranks = [rank for _, rank in result.most_common_words]
        # Should be in ascending order (lowest ranks first)
        assert ranks == sorted(ranks)

    def test_no_duplicates_in_lists(self, academic_text):
        """Test no duplicate words in rarest/common lists."""
        result = compute_word_frequency_sophistication(academic_text)

        rarest_words = [word for word, _ in result.rarest_words]
        common_words = [word for word, _ in result.most_common_words]

        # No duplicates within each list
        assert len(rarest_words) == len(set(rarest_words))
        assert len(common_words) == len(set(common_words))

    def test_few_unique_words(self):
        """Test with text having fewer than 10 unique words."""
        text = "the cat and the dog and the bird and the fish"
        result = compute_word_frequency_sophistication(text)

        # Should have fewer than 10 items since there are only 6 unique words
        assert len(result.rarest_words) <= 6
        assert len(result.most_common_words) <= 6
