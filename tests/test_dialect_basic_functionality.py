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


class TestDialectBasicFunctionality:
    """Test basic dialect detection functionality."""

    def test_british_text_detection(self):
        """Test detection of British English text."""
        text = "The colour of the programme was brilliant. I've got a flat in the city centre."
        result = compute_dialect(text)

        assert result.dialect == "british"
        assert result.british_score > result.american_score
        assert result.confidence > 0.5

    def test_american_text_detection(self):
        """Test detection of American English text."""
        text = "The color of the program was awesome. I have an apartment in the city center."
        result = compute_dialect(text)

        assert result.dialect == "american"
        assert result.american_score > result.british_score
        assert result.confidence > 0.5

    def test_mixed_dialect_detection(self):
        """Test detection of mixed British/American text."""
        text = "The colour of the program was good. I have a flat in the center."
        result = compute_dialect(text)

        # Should detect mixed or have close scores
        assert result.dialect in ["mixed", "british", "american"]
        # Both dialects should have some presence
        assert result.british_score > 0 or result.american_score > 0

    def test_neutral_text_detection(self):
        """Test detection of neutral text with no dialect markers."""
        text = "The sun rose over the mountains. Birds sang in the trees."
        result = compute_dialect(text)

        # Should be neutral or have very low scores
        assert result.dialect in ["neutral", "mixed"]
        # Scores should be low
        assert result.british_score < 0.3 or result.american_score < 0.3
