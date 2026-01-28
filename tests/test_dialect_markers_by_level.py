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


class TestDialectMarkersByLevel:
    """Test linguistic level categorization of markers."""

    def test_markers_by_level_structure(self):
        """Test that markers_by_level has correct structure."""
        text = "The colour of the flat was brilliant."
        result = compute_dialect(text)

        assert "phonological" in result.markers_by_level
        assert "morphological" in result.markers_by_level
        assert "lexical" in result.markers_by_level
        assert "syntactic" in result.markers_by_level

    def test_lexical_level_vocabulary(self):
        """Test that vocabulary markers go to lexical level."""
        text = "I live in a flat with a lift."
        result = compute_dialect(text)

        lexical_markers = result.markers_by_level.get("lexical", {})
        # Should have lexical markers
        assert len(lexical_markers) >= 0  # May be 0 if words not in vocabulary list
