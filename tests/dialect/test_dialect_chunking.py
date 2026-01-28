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


class TestDialectChunking:
    """Test chunked analysis per Issue #27."""

    def test_chunking_creates_distribution(self):
        """Test that chunking creates distribution objects."""
        # Create text long enough for multiple chunks
        text = " ".join(["The colour of the programme was brilliant."] * 500)
        result = compute_dialect(text, chunk_size=100)

        # Should have distributions
        assert hasattr(result, "british_score_dist")
        assert hasattr(result, "american_score_dist")
        assert hasattr(result, "markedness_score_dist")

        # Mean should match the scalar value
        assert result.british_score == result.british_score_dist.mean

    def test_chunk_count_recorded(self):
        """Test that chunk count is recorded."""
        text = " ".join(["The colour was nice."] * 200)
        result = compute_dialect(text, chunk_size=50)

        assert result.chunk_count > 0
        assert result.chunk_size == 50

    def test_distribution_statistics(self):
        """Test that distributions have statistics."""
        text = " ".join(["The colour of the program was nice."] * 300)
        result = compute_dialect(text, chunk_size=50)

        dist = result.british_score_dist
        assert hasattr(dist, "mean")
        assert hasattr(dist, "median")
        assert hasattr(dist, "std")
        assert hasattr(dist, "range")
        assert hasattr(dist, "iqr")
