"""Tests for advanced syntactic analysis (Issue #17)."""

import pytest

from pystylometry.syntactic.advanced_syntactic import compute_advanced_syntactic

# ===== Fixtures =====


# ===== Basic Functionality Tests =====


@pytest.fixture
def simple_text():
    """Simple sentences with basic structure."""
    return "The cat sat on the mat. The dog ran in the park. A bird flew over the tree."


class TestSpacyIntegration:
    """Test spaCy model integration."""

    def test_default_model(self, simple_text):
        """Test with default spaCy model."""
        result = compute_advanced_syntactic(simple_text)

        # Should use default model
        assert result.metadata["model_used"] == "en_core_web_sm"

    def test_model_name_in_metadata(self, simple_text):
        """Verify model name is recorded in metadata."""
        model_name = "en_core_web_sm"
        result = compute_advanced_syntactic(simple_text, model=model_name)

        assert result.metadata["model_used"] == model_name
