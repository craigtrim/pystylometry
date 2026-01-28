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


@pytest.fixture
def very_common_text():
    """Text with only very common words (top 100)."""
    return (
        "The man and the woman are in the house. They have a dog and a cat. "
        "The dog is big and the cat is small. The man is good and the woman "
        "is good too. They go to the store. The store is not far from the house. "
        "It is a good day. The sun is out and it is not cold."
    ) * 2


class TestFrequencyBands:
    """Frequency band distribution tests."""

    def test_all_bands_present(self, mixed_sophistication_text):
        """Test all 5 frequency bands are in distribution."""
        result = compute_word_frequency_sophistication(mixed_sophistication_text)

        expected_bands = {
            "very_common",
            "common",
            "moderate",
            "rare",
            "very_rare",
        }
        assert set(result.frequency_band_distribution.keys()) == expected_bands

    def test_band_sum(self, academic_text):
        """Test band proportions sum to 1.0."""
        result = compute_word_frequency_sophistication(academic_text)

        band_sum = sum(result.frequency_band_distribution.values())
        assert abs(band_sum - 1.0) < 1e-9

    def test_very_common_dominated(self, very_common_text):
        """Test text dominated by very common words."""
        result = compute_word_frequency_sophistication(very_common_text)

        # Very common band should dominate
        assert (
            result.frequency_band_distribution["very_common"]
            > result.frequency_band_distribution["rare"]
        )
        assert (
            result.frequency_band_distribution["very_common"]
            > result.frequency_band_distribution["very_rare"]
        )

    def test_rare_dominated(self, technical_text):
        """Test technical text has many unknown/rare words."""
        result = compute_word_frequency_sophistication(technical_text)

        # Rare or very_rare bands should be substantial
        rare_plus_very_rare = (
            result.frequency_band_distribution["rare"]
            + result.frequency_band_distribution["very_rare"]
        )
        assert rare_plus_very_rare > 0.2  # At least 20% rare/very_rare
