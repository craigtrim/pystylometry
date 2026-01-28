"""Comprehensive tests for Automated Readability Index (ARI) computation."""

from pystylometry.readability import compute_ari


class TestARIComplexityLevels:
    """Test across various text complexity levels."""

    def test_children_book_simple(self):
        """Test very simple children's book style text."""
        text = """
        The cat is big. The dog is small. They play together.
        The cat runs fast. The dog runs too. They are friends.
        The sun is out. It is a nice day. They have fun.
        """
        result = compute_ari(text)

        # Should be low grade level
        assert result.grade_level <= 5

    def test_middle_school_text(self):
        """Test middle school level text."""
        text = """
        The American Revolution began in 1775 when colonists rebelled against
        British rule. They were angry about taxes and wanted independence.
        Important leaders like George Washington and Thomas Jefferson helped
        guide the colonists to victory. The war ended in 1783, and America
        became a new nation.
        """
        result = compute_ari(text)

        # Should be middle grade level
        assert 5 <= result.grade_level <= 10

    def test_academic_text(self):
        """Test academic/technical text."""
        text = """
        The phenomenological hermeneutics of continental philosophy necessitates
        a comprehensive understanding of existential ontology. Heidegger's
        deconstruction of metaphysical presuppositions requires epistemological
        rigor and methodological consistency. The intersubjective constitution
        of meaning emerges through dialectical engagement with transcendental
        subjectivity.
        """
        result = compute_ari(text)

        # Should be high grade level
        assert result.grade_level >= 10
