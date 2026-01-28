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
def complex_text():
    """Complex sentences with subordination and embedding."""
    return (
        "Although the research methodology that was employed demonstrated "
        "significant theoretical implications, the findings, which were "
        "published in a peer-reviewed journal, suggested that further "
        "investigation would be necessary before definitive conclusions "
        "could be drawn about the phenomena."
    )


@pytest.fixture
def simple_text():
    """Simple sentences with basic structure."""
    return "The cat sat on the mat. The dog ran in the park. A bird flew over the tree."


class TestParseTreeDepth:
    """Test parse tree depth calculations."""

    def test_simple_sentence_depth(self, simple_text):
        """Simple sentences should have shallow parse trees."""
        result = compute_advanced_syntactic(simple_text)

        # Simple sentences typically depth 2-4
        assert 1 <= result.mean_parse_tree_depth <= 5
        assert result.max_parse_tree_depth <= 6

    def test_complex_sentence_depth(self, complex_text):
        """Complex sentences should have deeper parse trees."""
        result = compute_advanced_syntactic(complex_text)

        # Complex sentences typically depth 5-8
        assert result.mean_parse_tree_depth >= 3
        assert result.max_parse_tree_depth >= 5

    def test_depth_mean_max_relationship(self, academic_text):
        """Max depth should be >= mean depth."""
        result = compute_advanced_syntactic(academic_text)

        assert result.max_parse_tree_depth >= result.mean_parse_tree_depth

    def test_parse_depths_in_metadata(self, simple_text):
        """Metadata should contain depths for each sentence."""
        result = compute_advanced_syntactic(simple_text)

        depths = result.metadata["parse_depths_per_sentence"]
        assert isinstance(depths, list)
        assert len(depths) == result.metadata["sentence_count"]
        assert all(isinstance(d, int) for d in depths)
