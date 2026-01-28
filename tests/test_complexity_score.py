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


@pytest.fixture
def simple_text():
    """Simple sentences with basic structure."""
    return "The cat sat on the mat. The dog ran in the park. A bird flew over the tree."


class TestComplexityScore:
    """Test composite complexity score."""

    def test_low_complexity(self, childrens_text):
        """Children's text should have low complexity score."""
        result = compute_advanced_syntactic(childrens_text)

        # Should be relatively low
        assert result.sentence_complexity_score < 0.5

    def test_medium_complexity(self, simple_text):
        """Simple text should have medium complexity."""
        result = compute_advanced_syntactic(simple_text)

        # Should be moderate
        assert 0.1 <= result.sentence_complexity_score <= 0.7

    def test_high_complexity(self, complex_text):
        """Complex text should have higher complexity score."""
        result = compute_advanced_syntactic(complex_text)

        # Should be relatively high
        assert result.sentence_complexity_score > 0.3

    def test_complexity_score_range(self, academic_text):
        """Complexity score should be between 0 and 1."""
        result = compute_advanced_syntactic(academic_text)

        assert 0.0 <= result.sentence_complexity_score <= 1.0
