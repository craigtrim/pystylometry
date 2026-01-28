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
def childrens_text():
    """Simple children's text."""
    return (
        "The dog is big. The cat is small. I like the dog. "
        "I like the cat. The dog runs fast. The cat jumps high. "
        "We play with the dog. We play with the cat."
    )


@pytest.fixture
def simple_text():
    """Simple sentences with basic structure."""
    return "The cat sat on the mat. The dog ran in the park. A bird flew over the tree."


class TestTUnits:
    """Test T-unit analysis."""

    def test_single_t_unit(self):
        """Single simple sentence = 1 T-unit."""
        text = "The cat sat on the mat."
        result = compute_advanced_syntactic(text)

        assert result.t_unit_count == 1

    def test_multiple_t_units(self, simple_text):
        """Multiple sentences = multiple T-units."""
        result = compute_advanced_syntactic(simple_text)

        # Simple_text has 3 sentences
        assert result.t_unit_count == 3

    def test_mean_t_unit_length(self, childrens_text):
        """Test mean T-unit length calculation."""
        result = compute_advanced_syntactic(childrens_text)

        # Children's text has short sentences
        assert result.mean_t_unit_length < 10

    def test_long_t_units(self, academic_text):
        """Academic text should have longer T-units."""
        result = compute_advanced_syntactic(academic_text)

        # Academic text typically has longer T-units
        assert result.mean_t_unit_length > 10

    def test_t_unit_lengths_in_metadata(self, simple_text):
        """Metadata should contain T-unit lengths."""
        result = compute_advanced_syntactic(simple_text)

        t_unit_lengths = result.metadata["t_unit_lengths"]
        assert isinstance(t_unit_lengths, list)
        assert len(t_unit_lengths) == result.t_unit_count
        assert all(isinstance(length, int) for length in t_unit_lengths)
