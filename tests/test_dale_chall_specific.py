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
    compute_dale_chall,
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


class TestDaleChallSpecific:
    """Dale-Chall specific feature tests."""

    def test_adjustment_triggered(self):
        """Test that adjustment is triggered when difficult % > 5%."""
        # Academic text should have > 5% difficult words
        text = (
            "The comprehensive investigation utilized sophisticated methodological "
            "frameworks to analyze multifaceted phenomena. Researchers employed "
            "rigorous empirical techniques to establish definitive conclusions."
        ) * 3
        result = compute_dale_chall(text)
        # Check that adjustment was applied
        assert result.metadata["adjusted"] is True
        # Adjusted score should be higher than raw
        assert result.dale_chall_score > result.metadata["raw_score"]

    def test_no_adjustment(self, childrens_text):
        """Test no adjustment for text with < 5% difficult words."""
        result = compute_dale_chall(childrens_text)
        # Children's text should have low difficult word %
        if result.metadata["difficult_word_pct"] <= 5.0:
            assert result.metadata["adjusted"] is False
            assert result.dale_chall_score == result.metadata["raw_score"]

    def test_case_insensitive(self):
        """Test case-insensitive familiar word matching."""
        text1 = "The Dog Runs Fast."
        text2 = "the dog runs fast."
        result1 = compute_dale_chall(text1)
        result2 = compute_dale_chall(text2)
        # Should have same difficult word count regardless of case
        assert result1.difficult_word_count == result2.difficult_word_count

    def test_grade_level_mapping(self, childrens_text, academic_text):
        """Test grade level mapping."""
        result_easy = compute_dale_chall(childrens_text)
        result_hard = compute_dale_chall(academic_text)
        # Children's text should be easier
        grade_order = [
            "4 and below",
            "5-6",
            "7-8",
            "9-10",
            "11-12",
            "College",
            "College Graduate",
        ]
        idx_easy = grade_order.index(result_easy.grade_level)
        idx_hard = grade_order.index(result_hard.grade_level)
        assert idx_easy < idx_hard
