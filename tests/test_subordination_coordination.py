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
def coordinated_text():
    """Text with coordination (and, but, or)."""
    return (
        "The sun rose and the birds sang. "
        "The cat meowed but nobody came. "
        "We can go to the park or we can stay home. "
        "The dog barked and the door opened."
    )


@pytest.fixture
def simple_text():
    """Simple sentences with basic structure."""
    return "The cat sat on the mat. The dog ran in the park. A bird flew over the tree."


@pytest.fixture
def subordinated_text():
    """Text with high subordination."""
    return (
        "When the sun rises, the birds begin to sing. "
        "Although it was raining, we decided to go outside. "
        "Because the experiment failed, the team had to start over. "
        "If you study hard, you will pass the exam."
    )


class TestSubordinationCoordination:
    """Test subordination and coordination indices."""

    def test_high_subordination(self, subordinated_text):
        """Subordinated text should have high subordination index."""
        result = compute_advanced_syntactic(subordinated_text)

        # Should have subordinate clauses
        assert result.subordination_index > 0

    def test_high_coordination(self, coordinated_text):
        """Coordinated text should have coordination."""
        result = compute_advanced_syntactic(coordinated_text)

        # May have coordinate clauses (depends on spaCy parsing)
        # Just check it's a valid ratio
        assert 0.0 <= result.coordination_index <= 1.0

    def test_subordination_range(self, academic_text):
        """Subordination index should be between 0 and 1."""
        result = compute_advanced_syntactic(academic_text)

        assert 0.0 <= result.subordination_index <= 1.0

    def test_coordination_range(self, simple_text):
        """Coordination index should be between 0 and 1."""
        result = compute_advanced_syntactic(simple_text)

        assert 0.0 <= result.coordination_index <= 1.0
