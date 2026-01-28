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

from pystylometry.dialect import clear_cache, get_markers


class TestDialectMarkersLoader:
    """Test dialect markers loading and caching."""

    def test_markers_load_successfully(self):
        """Test that markers load without error."""
        markers = get_markers()
        assert markers is not None
        assert len(markers.vocabulary_pairs) > 0

    def test_markers_cache(self):
        """Test that markers are cached."""
        markers1 = get_markers()
        markers2 = get_markers()
        assert markers1 is markers2  # Same object due to caching

    def test_cache_clear(self):
        """Test that cache can be cleared."""
        get_markers()  # Prime the cache
        clear_cache()
        markers_after_clear = get_markers()
        # After clearing, should still work
        assert markers_after_clear is not None

    def test_markers_contain_expected_data(self):
        """Test that markers contain expected data structures."""
        markers = get_markers()

        assert hasattr(markers, "vocabulary_pairs")
        assert hasattr(markers, "vocabulary_exclusive")
        assert hasattr(markers, "spelling_patterns")
        assert hasattr(markers, "grammar_patterns")
        assert hasattr(markers, "eye_dialect_words")
