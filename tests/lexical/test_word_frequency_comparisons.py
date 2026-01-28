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
def simple_text():
    """Simple text with common words."""
    return (
        "The cat sat on the mat. The dog ran in the park. "
        "A boy and a girl play with a ball. "
        "The sun is hot. The sky is blue. "
    ) * 5  # Repeat to get enough tokens


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


class TestWordFrequencyComparisons:
    """Comparative tests across different text types."""

    def test_academic_vs_simple(self, academic_text, simple_text):
        """Test academic text has higher sophistication than simple text."""
        result_academic = compute_word_frequency_sophistication(academic_text)
        result_simple = compute_word_frequency_sophistication(simple_text)

        # Academic text should have higher mean rank (less common words)
        assert result_academic.mean_frequency_rank > result_simple.mean_frequency_rank

        # Academic text should have higher rare word ratio
        assert result_academic.rare_word_ratio > result_simple.rare_word_ratio

        # Academic text should have higher academic word ratio
        assert result_academic.academic_word_ratio > result_simple.academic_word_ratio

    def test_childrens_text_common(self, childrens_text):
        """Test children's text has high common_word_ratio."""
        result = compute_word_frequency_sophistication(childrens_text)

        # Children's text should have high common word ratio
        assert result.common_word_ratio > 0.5  # At least 50% common words

        # Children's text should have low median rank (median less affected by unknown words)
        assert result.median_frequency_rank < 500

    def test_technical_unknown_words(self, technical_text):
        """Test technical text has many unknown words."""
        result = compute_word_frequency_sophistication(technical_text)

        # Technical jargon should result in many unknown words
        # "OAuth2", "WebSocket", "Kubernetes", "microservice", etc.
        assert result.metadata["unknown_words"] > 0
