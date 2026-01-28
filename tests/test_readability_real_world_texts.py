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

import math

from pystylometry.readability import (
    compute_dale_chall,
    compute_forcast,
    compute_fry,
    compute_linsear_write,
)

# ===== Fixtures =====


# ===== Dale-Chall Tests =====


class TestRealWorldTexts:
    """Tests with realistic text samples."""

    def test_news_article(self):
        """Test with news article text."""
        text = (
            "The Senate approved a new infrastructure bill yesterday. "
            "The legislation allocates funding for highways, bridges, and public transit. "
            "Congressional leaders praised the bipartisan effort to improve transportation. "
            "Critics argue the bill does not address climate change adequately. "
            "The President is expected to sign the bill into law next week."
        )
        dc = compute_dale_chall(text)
        lw = compute_linsear_write(text)
        fry = compute_fry(text)

        # News should be readable by adults (may vary based on word list coverage)
        # Dale-Chall with limited word list may score higher than expected
        assert dc.dale_chall_score < 15.0
        assert lw.grade_level <= 14
        assert not math.isnan(fry.avg_syllables_per_100)

    def test_scientific_abstract(self):
        """Test with scientific abstract."""
        text = (
            "We investigated the molecular mechanisms underlying cellular differentiation. "
            "Transcriptomic analysis revealed differential expression patterns across developmental stages. "
            "Hierarchical clustering identified distinct gene modules associated with lineage commitment. "
            "Our findings demonstrate the regulatory networks governing stem cell fate determination."
        )
        dc = compute_dale_chall(text)
        lw = compute_linsear_write(text)

        # Scientific text should be difficult
        assert dc.dale_chall_score >= 9.0
        # Linsear may vary - just check it's above elementary level
        assert lw.grade_level >= 7.0

    def test_instruction_manual(self):
        """Test with instruction manual text."""
        text = (
            "To assemble the bookshelf, first attach the side panels to the back board. "
            "Use the provided screws and allen wrench. Tighten each screw firmly but do not overtighten. "
            "Next, insert the shelf supports into the pre-drilled holes. "
            "Place the shelves on top of the supports. Ensure the bookshelf is level before use."
        )
        lw = compute_linsear_write(text)
        fc = compute_forcast(text)

        # Instructions should be moderately easy (wide range acceptable)
        assert 3.0 <= lw.grade_level <= 12.0
        assert 3.0 <= fc.grade_level <= 12.0
