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
def complex_text():
    """Complex sentences with subordination and embedding."""
    return (
        "Although the research methodology that was employed demonstrated "
        "significant theoretical implications, the findings, which were "
        "published in a peer-reviewed journal, suggested that further "
        "investigation would be necessary before definitive conclusions "
        "could be drawn about the phenomena."
    )


class TestDependencyDistance:
    """Test mean dependency distance calculations."""

    def test_short_dependencies(self, childrens_text):
        """Simple text should have shorter dependencies."""
        result = compute_advanced_syntactic(childrens_text)

        # Children's text: short sentences, short dependencies
        assert result.dependency_distance < 4.0

    def test_long_dependencies(self, complex_text):
        """Complex text may have longer dependencies."""
        result = compute_advanced_syntactic(complex_text)

        # Complex text can have longer dependencies
        assert result.dependency_distance > 0

    def test_dependency_distance_positive(self, academic_text):
        """Dependency distance should be positive."""
        result = compute_advanced_syntactic(academic_text)

        assert result.dependency_distance > 0
