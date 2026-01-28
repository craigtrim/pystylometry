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

import math

from pystylometry.dialect import compute_dialect


class TestDialectEdgeCases:
    """Test edge cases for dialect detection."""

    def test_empty_text(self):
        """Test dialect detection with empty text."""
        result = compute_dialect("")

        assert result.dialect == "neutral"
        assert result.confidence == 0.0
        assert math.isnan(result.british_score)
        assert math.isnan(result.american_score)

    def test_whitespace_only(self):
        """Test dialect detection with whitespace only."""
        result = compute_dialect("   \n\t  ")

        assert result.dialect == "neutral"
        assert result.confidence == 0.0

    def test_single_word(self):
        """Test dialect detection with single word."""
        # British word
        result = compute_dialect("colour")
        assert result.british_score > 0

        # American word
        result = compute_dialect("color")
        assert result.american_score > 0

    def test_numbers_only(self):
        """Test dialect detection with numbers only."""
        result = compute_dialect("123 456 789")
        # Should handle gracefully
        assert result.dialect in ["neutral", "mixed"]
