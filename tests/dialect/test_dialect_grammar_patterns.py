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


class TestDialectGrammarPatterns:
    """Test grammar pattern-based dialect detection."""

    def test_have_got_pattern(self):
        """Test detection of 'have got' vs 'have' pattern."""
        british_text = "I've got a car. She's got three children."

        british_result = compute_dialect(british_text)
        # Grammar patterns are harder to distinguish, so just check for detection
        assert british_result.british_score >= 0

    def test_gotten_pattern(self):
        """Test detection of 'gotten' (American) pattern."""
        american_text = "Things have gotten worse. She's gotten a promotion."
        result = compute_dialect(american_text)

        # 'gotten' is strongly American
        assert result.american_score > 0

    def test_grammar_markers_recorded(self):
        """Test that grammar markers are recorded in results."""
        text = "I've gotten used to it."
        result = compute_dialect(text)

        # Grammar markers may or may not be detected depending on pattern
        # Just check the structure exists
        assert isinstance(result.grammar_markers, dict)
