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


class TestDialectRegisterHints:
    """Test register hints in dialect results."""

    def test_register_hints_structure(self):
        """Test that register hints has expected structure."""
        text = "The colour was nice."
        result = compute_dialect(text)

        assert isinstance(result.register_hints, dict)
        assert "eye_dialect_density" in result.register_hints
        assert "marker_density" in result.register_hints
