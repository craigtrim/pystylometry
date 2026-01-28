"""Tests for extended n-gram features.

Related GitHub Issue:
    #19 - Extended N-gram Features
    https://github.com/craigtrim/pystylometry/issues/19

Tests cover:
    - Word n-grams (trigrams, 4-grams)
    - Skipgrams (n-grams with gaps)
    - Character n-grams (trigrams, 4-grams)
    - Shannon entropy calculations
    - POS n-grams (optional, requires spaCy)
"""

import pytest

from pystylometry.ngrams.extended_ngrams import (
    compute_extended_ngrams,
)

# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================


class TestComputeExtendedNgramsWithPOS:
    """Tests for POS n-gram functionality (requires spaCy)."""

    @pytest.fixture
    def spacy_available(self):
        """Check if spaCy is available."""
        try:
            import spacy

            spacy.load("en_core_web_sm")
            return True
        except (ImportError, OSError):
            return False

    def test_pos_ngrams_enabled(self, long_text, spacy_available):
        """Test POS n-grams when spaCy is available."""
        if not spacy_available:
            pytest.skip("spaCy not available")

        result = compute_extended_ngrams(long_text, include_pos_ngrams=True)

        assert result.pos_trigram_count > 0
        assert result.pos_4gram_count > 0
        assert len(result.top_pos_trigrams) > 0
        assert result.pos_trigram_entropy > 0

        # POS tags should be uppercase
        for ngram, count in result.top_pos_trigrams:
            assert isinstance(ngram, str)
            # POS tags are typically uppercase
            parts = ngram.split()
            for part in parts:
                assert part.isupper() or part.isalpha()
