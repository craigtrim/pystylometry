"""Tests for advanced syntactic analysis (Issue #17)."""

import pytest

from pystylometry.syntactic.advanced_syntactic import compute_advanced_syntactic

# ===== Fixtures =====


# ===== Basic Functionality Tests =====


@pytest.fixture
def academic_text():
    """Academic text with high clausal density."""
    return (
        "The study examined the relationship between syntactic complexity "
        "and readability, considering factors such as parse tree depth, "
        "clausal density, and T-unit length. Results indicated that texts "
        "with higher subordination indices were perceived as more difficult, "
        "which suggests that dependency distance plays a crucial role in "
        "processing difficulty."
    )


@pytest.fixture
def simple_text():
    """Simple sentences with basic structure."""
    return "The cat sat on the mat. The dog ran in the park. A bird flew over the tree."


class TestBranchingDirection:
    """Test branching direction calculations."""

    def test_right_branching_dominant(self, simple_text):
        """English should be predominantly right-branching."""
        result = compute_advanced_syntactic(simple_text)

        # English is typically 50-80% right-branching
        # Simple sentences may be balanced, so we use >=
        assert result.right_branching_ratio >= result.left_branching_ratio

    def test_branching_ratios_sum(self, academic_text):
        """Left and right branching should sum to ~1.0."""
        result = compute_advanced_syntactic(academic_text)

        total_branching = result.left_branching_ratio + result.right_branching_ratio
        assert total_branching == pytest.approx(1.0, abs=0.01)

    def test_branching_counts_in_metadata(self, simple_text):
        """Metadata should contain branching counts."""
        result = compute_advanced_syntactic(simple_text)

        metadata = result.metadata
        assert "left_branching_count" in metadata
        assert "right_branching_count" in metadata
        assert metadata["left_branching_count"] >= 0
        assert metadata["right_branching_count"] >= 0
