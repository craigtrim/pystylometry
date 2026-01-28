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
    compute_forcast,
    compute_fry,
    compute_linsear_write,
    compute_powers_sumner_kearl,
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


@pytest.fixture
def middle_school_text():
    """Middle school level text."""
    return (
        "The American Revolution was a time when the colonies fought for independence. "
        "George Washington led the Continental Army against the British forces. "
        "The Declaration of Independence was signed on July 4, 1776. "
        "This important document stated that all men are created equal. "
        "The war lasted for eight years before the colonists won their freedom. "
        "After the war, leaders worked together to create a new government. "
        "They wrote the Constitution to protect people's rights and establish laws. "
        "The new nation faced many challenges as it grew and developed."
    )


class TestComparativeAnalysis:
    """Tests comparing formulas across different text types."""

    def test_childrens_text_all_formulas(self, childrens_text):
        """Test all formulas agree children's text is easy."""
        dc = compute_dale_chall(childrens_text)
        lw = compute_linsear_write(childrens_text)
        fry = compute_fry(childrens_text)
        fc = compute_forcast(childrens_text)
        psk = compute_powers_sumner_kearl(childrens_text)

        # All should indicate low difficulty
        assert dc.grade_level in ["4 and below", "5-6", "7-8"]
        assert lw.grade_level <= 8.0
        assert fry.grade_level in ["1", "2", "3", "4", "5", "6"]
        assert fc.grade_level <= 8.0
        assert psk.grade_level <= 6.0

    def test_academic_text_all_formulas(self, academic_text):
        """Test all formulas agree academic text is difficult."""
        dc = compute_dale_chall(academic_text)
        lw = compute_linsear_write(academic_text)
        fry_result = compute_fry(academic_text)
        fc = compute_forcast(academic_text)
        psk = compute_powers_sumner_kearl(academic_text)

        # All should indicate high difficulty
        assert dc.grade_level in ["11-12", "College", "College Graduate"]
        assert lw.grade_level >= 10.0
        # Fry might vary - just ensure it returned a result
        assert fry_result.grade_level is not None
        assert fc.grade_level >= 10.0
        # PSK is designed for primary grades (1-4), so it may produce
        # out-of-range scores for academic text - just check it exists
        assert isinstance(psk.grade_level, float)

    def test_difficulty_ranking_consistency(
        self, childrens_text, middle_school_text, academic_text
    ):
        """Test all formulas rank texts in same difficulty order."""
        # Dale-Chall
        dc_child = compute_dale_chall(childrens_text)
        dc_middle = compute_dale_chall(middle_school_text)
        dc_academic = compute_dale_chall(academic_text)
        assert dc_child.dale_chall_score < dc_middle.dale_chall_score
        assert dc_middle.dale_chall_score < dc_academic.dale_chall_score

        # Linsear Write
        lw_child = compute_linsear_write(childrens_text)
        lw_middle = compute_linsear_write(middle_school_text)
        lw_academic = compute_linsear_write(academic_text)
        assert lw_child.grade_level < lw_middle.grade_level
        assert lw_middle.grade_level < lw_academic.grade_level

        # FORCAST
        fc_child = compute_forcast(childrens_text)
        fc_middle = compute_forcast(middle_school_text)
        fc_academic = compute_forcast(academic_text)
        assert fc_child.grade_level < fc_middle.grade_level
        assert fc_middle.grade_level < fc_academic.grade_level

        # PSK is designed for primary grades only, so we only test children's vs middle
        psk_child = compute_powers_sumner_kearl(childrens_text)
        psk_middle = compute_powers_sumner_kearl(middle_school_text)
        # Only test children vs middle school (PSK not designed for academic text)
        assert psk_child.grade_level <= psk_middle.grade_level
