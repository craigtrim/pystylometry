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


@pytest.fixture
def news_text():
    """News article with moderate sophistication."""
    return (
        "Officials announced today that the new policy will take effect next month. "
        "The decision comes after months of debate among lawmakers. "
        "Experts predict the changes will significantly impact local communities. "
        "Critics argue the proposal doesn't address underlying problems, while "
        "supporters maintain it represents an important step forward. "
        "The government plans to monitor implementation closely."
    )


@pytest.fixture
def technical_text():
    """Technical text with specialized jargon (many unknown words)."""
    return (
        "The API endpoint requires authentication using OAuth2 tokens. "
        "Initialize the WebSocket connection with proper SSL certificates. "
        "The microservice architecture utilizes RESTful paradigms for "
        "inter-process communication. Kubernetes orchestration handles "
        "containerized deployment across distributed clusters. "
        "Implement the asynchronous callback mechanism for event-driven processing. "
        "The middleware validates incoming JSON payloads against predefined schemas."
    )


class TestWordFrequencyRealWorld:
    """Tests with realistic text samples."""

    def test_academic_text(self, academic_text):
        """Test with academic prose sample."""
        result = compute_word_frequency_sophistication(academic_text)

        # Academic text characteristics
        assert result.academic_word_ratio > 0.05
        assert result.mean_frequency_rank > 1500
        assert result.rare_word_ratio > 0.2
        assert 0.0 <= result.advanced_word_ratio <= 1.0

    def test_childrens_text(self, childrens_text):
        """Test with children's book sample."""
        result = compute_word_frequency_sophistication(childrens_text)

        # Children's text characteristics
        assert result.common_word_ratio > 0.4
        assert result.median_frequency_rank < 500  # Low median rank
        assert result.rare_word_ratio < 0.3

    def test_news_text(self, news_text):
        """Test with news article."""
        result = compute_word_frequency_sophistication(news_text)

        # News text has moderate sophistication
        # With limited dictionary, check median instead of mean
        assert result.median_frequency_rank > 10  # Not all super common words
        assert 0.0 <= result.rare_word_ratio <= 1.0
        assert 0.0 <= result.common_word_ratio <= 1.0
        assert result.common_word_ratio > 0.2  # Some common words present

    def test_technical_text(self, technical_text):
        """Test with technical documentation."""
        result = compute_word_frequency_sophistication(technical_text)

        # Technical text has many specialized terms
        assert result.metadata["unknown_word_ratio"] > 0.0
        # Could have mix of very common words ("the", "a") and very rare jargon
        assert 0.0 <= result.advanced_word_ratio <= 1.0
