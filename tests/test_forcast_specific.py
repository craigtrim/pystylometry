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
    compute_forcast,
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


class TestFORCASTSpecific:
    """FORCAST specific feature tests."""

    def test_sample_extraction(self):
        """Test 150-word sample extraction."""
        # Create text with > 150 words
        text = " ".join(["word"] * 200) + "."
        result = compute_forcast(text)
        # With chunked analysis, total_words is the actual total
        assert result.total_words == 200
        # sample_size in metadata reflects the sampling approach
        assert result.metadata["sample_size"] == 150

    def test_short_text_scaling(self):
        """Test scaling for texts < 150 words."""
        text = " ".join(["cat"] * 75) + "."  # All 1-syllable words
        result = compute_forcast(text)
        # Should scale N to 150-word basis
        assert result.metadata["sample_size"] == 75
        # Scaled N should be approximately 150 (all single-syllable)
        assert result.metadata["scaled_n"] > 140

    def test_single_syllable_ratio(self, childrens_text):
        """Test single-syllable ratio calculation."""
        result = compute_forcast(childrens_text)
        # Children's text should have high single-syllable ratio
        assert result.single_syllable_ratio > 0.5
        assert result.single_syllable_count > 0

    def test_grade_calculation(self):
        """Test grade level calculation: 20 - (N / 10)."""
        # Create text with known single-syllable count
        # If we have 100 single-syllable words in 150-word sample:
        # N = 100, grade = 20 - (100 / 10) = 10
        text = " ".join(["cat"] * 100 + ["butterfly"] * 50) + "."
        result = compute_forcast(text)
        # Scaled N should be close to 100
        # Grade should be close to 10
        assert 8.0 <= result.grade_level <= 12.0
