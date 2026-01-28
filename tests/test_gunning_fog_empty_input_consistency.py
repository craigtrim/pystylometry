"""Comprehensive tests for Gunning Fog Index computation."""

from pystylometry.readability import compute_gunning_fog

# Try to import spaCy to determine if enhanced mode tests can run
try:
    import spacy

    # Try to load the model to see if it's downloaded
    try:
        spacy.load("en_core_web_sm")
        SPACY_AVAILABLE = True
    except OSError:
        # spaCy installed but model not downloaded
        SPACY_AVAILABLE = False
except ImportError:
    SPACY_AVAILABLE = False


class TestGunningFogEmptyInputConsistency:
    """Test empty input handling matches Flesch/SMOG convention."""

    def test_empty_returns_nan_not_zero(self):
        """Empty input should return NaN, not 0.0."""
        result = compute_gunning_fog("")

        # After fix: Should return NaN like Flesch and SMOG
        # 0.0 is a valid fog index (extremely simple text)
        # NaN correctly indicates "undefined"
        import math

        assert math.isnan(result.fog_index), "Empty input should return NaN, not 0.0"
        assert math.isnan(result.grade_level), "Empty input grade level should be NaN, not 0"

    def test_whitespace_returns_nan(self):
        """Whitespace-only input should return NaN."""
        result = compute_gunning_fog("   \n\t  ")

        import math

        assert math.isnan(result.fog_index)
        assert math.isnan(result.grade_level)
