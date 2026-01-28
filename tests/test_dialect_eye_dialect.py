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


class TestDialectEyeDialect:
    """Test eye dialect detection (register markers, not true dialect)."""

    def test_eye_dialect_detection(self):
        """Test detection of eye dialect markers."""
        text = "I'm gonna wanna get some food cuz I'm kinda hungry."
        result = compute_dialect(text)

        # Should detect eye dialect markers
        assert result.eye_dialect_count > 0
        assert result.eye_dialect_ratio > 0

    def test_eye_dialect_separate_from_dialect(self):
        """Test that eye dialect doesn't skew dialect classification."""
        # British text with eye dialect
        text = "The colour of the programme was gonna be brilliant, you know."
        result = compute_dialect(text)

        # Should still detect British despite eye dialect
        assert result.british_score > 0
        # Eye dialect should be separately tracked
        assert result.eye_dialect_count > 0
