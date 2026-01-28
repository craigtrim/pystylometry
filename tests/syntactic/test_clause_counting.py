"""Tests for sentence type classification (Issue #18)."""

from pystylometry.syntactic.sentence_types import compute_sentence_types

# ===== Fixtures =====


# ===== Basic Functionality Tests =====


class TestClauseCounting:
    """Test clause counting accuracy."""

    def test_independent_clause_count(self):
        """Test counting independent clauses."""
        # Simple: 1 independent
        simple = "The cat sat."
        result = compute_sentence_types(simple)
        clause_counts = result.metadata["clause_counts_per_sentence"][0]
        assert clause_counts[0] == 1  # 1 independent

    def test_dependent_clause_count(self):
        """Test counting dependent clauses."""
        # Complex: 1 independent, 1+ dependent
        complex_text = "When I arrived, I saw her."
        result = compute_sentence_types(complex_text)
        clause_counts = result.metadata["clause_counts_per_sentence"][0]
        assert clause_counts[0] == 1  # 1 independent
        assert clause_counts[1] >= 1  # At least 1 dependent

    def test_coordinated_clauses(self):
        """Test counting coordinated independent clauses."""
        # Compound: 2+ independent
        compound = "I came and I saw."
        result = compute_sentence_types(compound)
        clause_counts = result.metadata["clause_counts_per_sentence"][0]
        assert clause_counts[0] >= 2  # 2+ independent

    def test_multiple_dependent_clauses(self):
        """Test counting multiple dependent clauses."""
        # Multiple dependent clauses
        text = "Although it was late when I arrived, I saw her."
        result = compute_sentence_types(text)
        clause_counts = result.metadata["clause_counts_per_sentence"][0]
        assert clause_counts[1] >= 1  # At least 1 dependent
