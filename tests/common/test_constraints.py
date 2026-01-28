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
    compute_linsear_write,
    compute_powers_sumner_kearl,
)

# ===== Fixtures =====


# ===== Dale-Chall Tests =====


@pytest.fixture
def simple_text():
    """Simple text with common words for children."""
    return (
        "The cat sat on the mat. The dog ran in the park. "
        "A boy and a girl play with a ball. The sun is hot. "
        "I like to run and jump. We can go to the zoo. "
    ) * 5  # Repeat to get enough tokens


class TestConstraints:
    """Tests for output constraints and validation."""

    def test_dale_chall_ratios(self, simple_text):
        """Test Dale-Chall ratios are in valid range."""
        result = compute_dale_chall(simple_text)
        assert 0.0 <= result.difficult_word_ratio <= 1.0

    def test_linsear_grade_positive(self, simple_text):
        """Test Linsear grade level is non-negative."""
        result = compute_linsear_write(simple_text)
        assert result.grade_level >= 0.0

    def test_forcast_ratios(self, simple_text):
        """Test FORCAST ratios are in valid range."""
        result = compute_forcast(simple_text)
        assert 0.0 <= result.single_syllable_ratio <= 1.0

    def test_psk_syllables_positive(self, simple_text):
        """Test PSK syllable metrics are positive."""
        result = compute_powers_sumner_kearl(simple_text)
        assert result.avg_syllables_per_word > 0
        assert result.total_syllables > 0

    def test_metadata_consistency(self, simple_text):
        """Test metadata is consistent across formulas."""
        # With chunked analysis, metadata structure varies by formula
        lw = compute_linsear_write(simple_text)
        psk = compute_powers_sumner_kearl(simple_text)

        # Both should have consistent total_words
        assert lw.metadata["total_words"] == psk.total_words
