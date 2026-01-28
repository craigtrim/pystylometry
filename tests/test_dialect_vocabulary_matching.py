"""Comprehensive tests for dialect detection module.

This module tests the dialect detection functionality, including vocabulary
matching, spelling pattern detection, grammar patterns, eye dialect
identification, and the chunking/distribution pattern from Issue #27.

Related GitHub Issues:
    #35 - Dialect detection with extensible JSON markers
    https://github.com/craigtrim/pystylometry/issues/35
    #30 - Whonix stylometry features (regional linguistic preferences)
    https://github.com/craigtrim/pystylometry/issues/30
    #27 - Native chunked analysis with Distribution dataclass
    https://github.com/craigtrim/pystylometry/issues/27
"""

from pystylometry.dialect import compute_dialect


class TestDialectVocabularyMatching:
    """Test vocabulary-based dialect detection."""

    def test_british_vocabulary(self):
        """Test detection of British vocabulary items."""
        # Use strongly British vocabulary without words that have dual meanings
        text = "I took the lift to my flat. The lorry drove past the petrol station."
        result = compute_dialect(text)

        # Should detect British vocabulary
        assert result.dialect == "british"
        assert "lexical" in result.markers_by_level
        # Check that British vocabulary was detected
        assert result.british_score > 0

    def test_american_vocabulary(self):
        """Test detection of American vocabulary items."""
        text = "I took the elevator to my apartment and had a cookie with my coffee."
        result = compute_dialect(text)

        # Should detect American vocabulary
        assert result.dialect == "american"
        assert result.american_score > 0

    def test_vocabulary_markers_recorded(self):
        """Test that vocabulary markers are recorded in results."""
        text = "The lorry drove past the petrol station."
        result = compute_dialect(text)

        # Should have vocabulary markers recorded
        assert len(result.vocabulary_markers) > 0
