"""Tests for advanced syntactic analysis (Issue #17)."""

import pytest

from pystylometry.syntactic.advanced_syntactic import compute_advanced_syntactic

# ===== Fixtures =====


# ===== Basic Functionality Tests =====


@pytest.fixture
def simple_text():
    """Simple sentences with basic structure."""
    return "The cat sat on the mat. The dog ran in the park. A bird flew over the tree."


class TestBasicFunctionality:
    """Test basic functionality with normal text."""

    def test_basic_computation(self, simple_text):
        """Test basic computation with simple text."""
        result = compute_advanced_syntactic(simple_text)

        # Should return result without errors
        assert result is not None

        # Basic sanity checks
        assert result.mean_parse_tree_depth > 0
        assert result.max_parse_tree_depth >= result.mean_parse_tree_depth
        assert result.t_unit_count > 0

    def test_all_fields_present(self, simple_text):
        """Verify all required fields are present."""
        result = compute_advanced_syntactic(simple_text)

        # Check all numeric fields
        assert isinstance(result.mean_parse_tree_depth, float)
        assert isinstance(result.max_parse_tree_depth, int)
        assert isinstance(result.t_unit_count, int)
        assert isinstance(result.mean_t_unit_length, float)
        assert isinstance(result.clausal_density, float)
        assert isinstance(result.dependent_clause_ratio, float)
        assert isinstance(result.passive_voice_ratio, float)
        assert isinstance(result.subordination_index, float)
        assert isinstance(result.coordination_index, float)
        assert isinstance(result.sentence_complexity_score, float)
        assert isinstance(result.dependency_distance, float)
        assert isinstance(result.left_branching_ratio, float)
        assert isinstance(result.right_branching_ratio, float)

        # Check metadata
        assert isinstance(result.metadata, dict)

    def test_metadata_completeness(self, simple_text):
        """Verify metadata contains all expected fields."""
        result = compute_advanced_syntactic(simple_text)

        metadata = result.metadata

        # Check required metadata fields
        assert "sentence_count" in metadata
        assert "word_count" in metadata
        assert "total_clauses" in metadata
        assert "independent_clause_count" in metadata
        assert "dependent_clause_count" in metadata
        assert "passive_sentence_count" in metadata
        assert "parse_depths_per_sentence" in metadata
        assert "t_unit_lengths" in metadata
        assert "model_used" in metadata

        # Verify types
        assert isinstance(metadata["sentence_count"], int)
        assert isinstance(metadata["word_count"], int)
        assert isinstance(metadata["total_clauses"], int)
        assert isinstance(metadata["parse_depths_per_sentence"], list)
        assert isinstance(metadata["t_unit_lengths"], list)
