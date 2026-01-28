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


class TestDialectSpellingPatterns:
    """Test spelling pattern-based dialect detection."""

    def test_our_or_pattern(self):
        """Test detection of -our/-or spelling pattern."""
        british_text = "The colour and flavour of the dish showed great honour."
        american_text = "The color and flavor of the dish showed great honor."

        british_result = compute_dialect(british_text)
        american_result = compute_dialect(american_text)

        assert british_result.british_score > american_result.british_score
        assert american_result.american_score > british_result.american_score

    def test_ise_ize_pattern(self):
        """Test detection of -ise/-ize spelling pattern."""
        british_text = "We need to organise and realise our plans to finalise the report."
        american_text = "We need to organize and realize our plans to finalize the report."

        british_result = compute_dialect(british_text)
        american_result = compute_dialect(american_text)

        assert british_result.british_score > american_result.british_score

    def test_re_er_pattern(self):
        """Test detection of -re/-er spelling pattern."""
        # Use texts without shared vocabulary that might skew results
        british_text = "The theatre in the city centre was good."
        american_text = "The theater in the city center was good."

        british_result = compute_dialect(british_text)
        american_result = compute_dialect(american_text)

        # British text should have British markers, American should have American markers
        assert british_result.british_score > 0
        assert american_result.american_score > 0
        # British text should score higher on British than American text does
        assert british_result.british_score >= american_result.british_score

    def test_doubled_l_pattern(self):
        """Test detection of doubled L pattern (travelled/traveled)."""
        british_text = "She travelled extensively and marvelled at the sights."
        american_text = "She traveled extensively and marveled at the sights."

        british_result = compute_dialect(british_text)
        american_result = compute_dialect(american_text)

        assert british_result.british_score >= american_result.british_score

    def test_spelling_markers_recorded(self):
        """Test that spelling markers are recorded in results."""
        text = "The colour was brilliant."
        result = compute_dialect(text)

        # Should have spelling markers recorded
        assert len(result.spelling_markers) > 0
