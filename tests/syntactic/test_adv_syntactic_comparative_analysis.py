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
def active_text():
    """Text with active voice only."""
    return (
        "The researchers conducted the experiment. "
        "They analyzed the results carefully. "
        "They published the findings in the journal."
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
def coordinated_text():
    """Text with coordination (and, but, or)."""
    return (
        "The sun rose and the birds sang. "
        "The cat meowed but nobody came. "
        "We can go to the park or we can stay home. "
        "The dog barked and the door opened."
    )


@pytest.fixture
def passive_text():
    """Text with passive voice constructions."""
    return (
        "The experiment was conducted by the researchers. "
        "The results were analyzed carefully. "
        "The findings have been published in the journal."
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


class TestComparativeAnalysis:
    """Test comparative analysis across text types."""

    def test_childrens_vs_academic(self, childrens_text, academic_text):
        """Academic text should be more complex than children's text."""
        children_result = compute_advanced_syntactic(childrens_text)
        academic_result = compute_advanced_syntactic(academic_text)

        # Academic should have deeper parse trees
        assert academic_result.mean_parse_tree_depth > children_result.mean_parse_tree_depth

        # Academic should have longer T-units
        assert academic_result.mean_t_unit_length > children_result.mean_t_unit_length

        # Academic should have higher complexity score
        assert academic_result.sentence_complexity_score > children_result.sentence_complexity_score

    def test_passive_vs_active(self, passive_text, active_text):
        """Passive text should have higher passive voice ratio."""
        passive_result = compute_advanced_syntactic(passive_text)
        active_result = compute_advanced_syntactic(active_text)

        # Passive text should have higher ratio
        assert passive_result.passive_voice_ratio > active_result.passive_voice_ratio

    def test_subordinated_vs_coordinated(self, subordinated_text, coordinated_text):
        """Subordinated text should have higher subordination index."""
        subordinated_result = compute_advanced_syntactic(subordinated_text)
        coordinated_result = compute_advanced_syntactic(coordinated_text)

        # Subordinated should have higher subordination
        assert subordinated_result.subordination_index > 0
        # coordinated_result computed for comparison (may have lower subordination)
        assert coordinated_result.subordination_index >= 0

    def test_complexity_ranking_consistency(self, childrens_text, simple_text, academic_text):
        """Complexity should increase: children's < simple < academic."""
        children_result = compute_advanced_syntactic(childrens_text)
        simple_result = compute_advanced_syntactic(simple_text)
        academic_result = compute_advanced_syntactic(academic_text)

        # Check consistent ranking
        assert children_result.sentence_complexity_score <= simple_result.sentence_complexity_score
        assert simple_result.sentence_complexity_score <= academic_result.sentence_complexity_score
