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


class TestClausalDensity:
    """Test clausal density calculations."""

    def test_low_clausal_density(self, childrens_text):
        """Simple text should have low clausal density."""
        result = compute_advanced_syntactic(childrens_text)

        # Children's text: mostly 1 clause per sentence
        assert result.clausal_density <= 1.5

    def test_high_clausal_density(self, academic_text):
        """Academic text should have higher clausal density."""
        result = compute_advanced_syntactic(academic_text)

        # Academic text: multiple clauses per sentence
        assert result.clausal_density > 1.0

    def test_dependent_clause_ratio(self, complex_text):
        """Complex text should have dependent clauses."""
        result = compute_advanced_syntactic(complex_text)

        # Should have some dependent clauses
        assert result.dependent_clause_ratio > 0
        assert result.dependent_clause_ratio <= 1.0

    def test_clause_counts_in_metadata(self, academic_text):
        """Metadata should contain clause counts."""
        result = compute_advanced_syntactic(academic_text)

        metadata = result.metadata
        assert metadata["total_clauses"] > 0
        assert metadata["independent_clause_count"] > 0
        assert metadata["dependent_clause_count"] >= 0
        assert (
            metadata["total_clauses"]
            == metadata["independent_clause_count"] + metadata["dependent_clause_count"]
        )
