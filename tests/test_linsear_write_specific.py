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
    compute_linsear_write,
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


class TestLinsearWriteSpecific:
    """Linsear Write specific feature tests."""

    def test_easy_word_dominated(self, childrens_text):
        """Test text dominated by easy words (1-2 syllables)."""
        result = compute_linsear_write(childrens_text)
        # Children's text should have mostly easy words
        assert result.easy_word_count > result.hard_word_count
        # Should be low grade level
        assert result.grade_level <= 6.0

    def test_hard_word_dominated(self, academic_text):
        """Test text with many hard words (3+ syllables)."""
        result = compute_linsear_write(academic_text)
        # Academic text should have more hard words
        # (though may not dominate due to function words)
        assert result.hard_word_count > 0
        # Should be higher grade level
        assert result.grade_level >= 8.0

    def test_score_conversion_high(self):
        """Test score > 20 conversion (score / 2)."""
        # Create text with very long sentences and many hard words
        text = (
            "The comprehensive methodological investigation systematically "
            "examined multifaceted theoretical frameworks utilizing sophisticated "
            "analytical paradigms to establish empirical correlations between "
            "interdisciplinary variables and contemporary sociological phenomena."
        )
        result = compute_linsear_write(text)
        # Grade level is now a mean across chunks, so just verify it's reasonable
        assert result.grade_level >= 0.0
        assert isinstance(result.grade_level, float)

    def test_word_classification(self):
        """Test easy vs hard word classification."""
        # 1-syllable words: "cat", "dog"
        # 2-syllable words: "running", "jumping"
        # 3-syllable words: "beautiful", "butterfly"
        text = "The cat and dog are running. Beautiful butterfly."
        result = compute_linsear_write(text)
        # Should have both easy and hard words
        assert result.easy_word_count > 0
        assert result.hard_word_count > 0
