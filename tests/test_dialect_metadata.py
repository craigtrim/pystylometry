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


class TestDialectMetadata:
    """Test metadata in dialect results."""

    def test_metadata_contains_word_count(self):
        """Test that metadata contains total word count."""
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_dialect(text)

        assert "total_word_count" in result.metadata
        assert result.metadata["total_word_count"] > 0

    def test_metadata_contains_version(self):
        """Test that metadata contains markers version."""
        text = "The colour was nice."
        result = compute_dialect(text)

        assert "markers_version" in result.metadata
