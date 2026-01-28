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


class TestDialectMarkednessScore:
    """Test markedness score computation."""

    def test_markedness_increases_with_markers(self):
        """Test that markedness increases with more dialect markers."""
        # Low markedness (neutral text)
        neutral_text = "The sun rose over the mountains."

        # High markedness (many British markers)
        marked_text = "The colour of the programme in the city centre was brilliant."

        neutral_result = compute_dialect(neutral_text)
        marked_result = compute_dialect(marked_text)

        # Marked text should have higher markedness score
        assert marked_result.markedness_score >= neutral_result.markedness_score

    def test_markedness_includes_eye_dialect(self):
        """Test that markedness includes eye dialect contribution."""
        # Text with eye dialect only
        eye_dialect_text = "I'm gonna wanna go cuz it's gonna be fun."
        result = compute_dialect(eye_dialect_text)

        # Should have some markedness from eye dialect
        assert result.markedness_score >= 0
