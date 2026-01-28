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
)

# ===== Fixtures =====


# ===== Dale-Chall Tests =====


class TestDaleChallEdgeCases:
    """Edge case tests for Dale-Chall."""

    def test_empty_text(self):
        """Test with empty text."""
        result = compute_dale_chall("")
        assert math.isnan(result.dale_chall_score)
        assert result.grade_level == "Unknown"
        assert result.total_words == 0

    def test_very_short_text(self):
        """Test with very short text."""
        result = compute_dale_chall("The cat sat on the mat.")
        assert not math.isnan(result.dale_chall_score)
        assert result.total_words == 6

    def test_all_difficult_words(self):
        """Test with many difficult/technical words."""
        text = (
            "The epistemological paradigm necessitates comprehensive methodological "
            "scrutiny through empirical investigation."
        )
        result = compute_dale_chall(text)
        # Should have high difficult word ratio
        assert result.difficult_word_ratio > 0.5
        # Should be college level or higher
        assert result.grade_level in ["College", "College Graduate"]
