"""Tests for sentence type classification (Issue #18)."""

import pytest

from pystylometry.syntactic.sentence_types import compute_sentence_types

# ===== Fixtures =====


# ===== Basic Functionality Tests =====


@pytest.fixture
def mixed_structural():
    """Text with mixed structural types."""
    return (
        "The cat sat. "  # Simple
        "I came and I saw. "  # Compound
        "When I arrived, I saw her. "  # Complex
        "When I called, she came and she stayed."  # Compound-complex
    )


class TestBasicFunctionality:
    """Test basic functionality with normal text."""

    def test_basic_computation(self, mixed_structural):
        """Test basic computation with mixed text."""
        result = compute_sentence_types(mixed_structural)

        # Should return result without errors
        assert result is not None
        assert result.total_sentences > 0

    def test_all_fields_present(self, mixed_structural):
        """Verify all required fields are present."""
        result = compute_sentence_types(mixed_structural)

        # Check structural ratio fields
        assert isinstance(result.simple_ratio, float)
        assert isinstance(result.compound_ratio, float)
        assert isinstance(result.complex_ratio, float)
        assert isinstance(result.compound_complex_ratio, float)

        # Check functional ratio fields
        assert isinstance(result.declarative_ratio, float)
        assert isinstance(result.interrogative_ratio, float)
        assert isinstance(result.imperative_ratio, float)
        assert isinstance(result.exclamatory_ratio, float)

        # Check count fields
        assert isinstance(result.simple_count, int)
        assert isinstance(result.compound_count, int)
        assert isinstance(result.complex_count, int)
        assert isinstance(result.compound_complex_count, int)
        assert isinstance(result.declarative_count, int)
        assert isinstance(result.interrogative_count, int)
        assert isinstance(result.imperative_count, int)
        assert isinstance(result.exclamatory_count, int)
        assert isinstance(result.total_sentences, int)

        # Check diversity metrics
        assert isinstance(result.structural_diversity, float)
        assert isinstance(result.functional_diversity, float)

        # Check metadata
        assert isinstance(result.metadata, dict)

    def test_metadata_completeness(self, mixed_structural):
        """Verify metadata contains all expected fields."""
        result = compute_sentence_types(mixed_structural)

        metadata = result.metadata

        # Check required metadata fields
        assert "sentence_count" in metadata
        assert "sentence_classifications" in metadata
        assert "clause_counts_per_sentence" in metadata
        assert "structural_counts" in metadata
        assert "functional_counts" in metadata
        assert "model_used" in metadata
