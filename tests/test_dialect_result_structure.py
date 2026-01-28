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


class TestDialectResultStructure:
    """Test DialectResult dataclass structure."""

    def test_result_has_required_fields(self):
        """Test that result has all required fields."""
        text = "The colour was nice."
        result = compute_dialect(text)

        # Classification
        assert hasattr(result, "dialect")
        assert hasattr(result, "confidence")

        # Scores
        assert hasattr(result, "british_score")
        assert hasattr(result, "american_score")
        assert hasattr(result, "markedness_score")

        # Distributions
        assert hasattr(result, "british_score_dist")
        assert hasattr(result, "american_score_dist")
        assert hasattr(result, "markedness_score_dist")

        # Marker breakdowns
        assert hasattr(result, "markers_by_level")
        assert hasattr(result, "spelling_markers")
        assert hasattr(result, "vocabulary_markers")
        assert hasattr(result, "grammar_markers")

        # Eye dialect
        assert hasattr(result, "eye_dialect_count")
        assert hasattr(result, "eye_dialect_ratio")

        # Register hints
        assert hasattr(result, "register_hints")

        # Chunking context
        assert hasattr(result, "chunk_size")
        assert hasattr(result, "chunk_count")

        # Metadata
        assert hasattr(result, "metadata")

    def test_dialect_values(self):
        """Test that dialect field has valid values."""
        texts = [
            "The colour was brilliant.",  # British
            "The color was awesome.",  # American
            "The sun rose.",  # Neutral
            "The colour of the color.",  # Mixed
        ]

        for text in texts:
            result = compute_dialect(text)
            assert result.dialect in ["british", "american", "mixed", "neutral"]
