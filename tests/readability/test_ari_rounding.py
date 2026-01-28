"""Comprehensive tests for Automated Readability Index (ARI) computation."""

from pystylometry.readability import compute_ari


class TestARIRounding:
    """Test rounding behavior and boundary values."""

    def test_grade_level_is_numeric(self):
        """Verify grade level is always a number (float for mean across chunks)."""
        texts = [
            "The cat sat on the mat.",
            "A very long and complex sentence with many subordinate clauses.",
            "Go.",
        ]

        for text in texts:
            result = compute_ari(text)
            assert isinstance(result.grade_level, (int, float))

    def test_lower_bound_clamping(self):
        """Test that very simple text is clamped to grade 0."""
        simple = "Go. Run. Stop."
        result = compute_ari(simple)

        assert result.grade_level >= 0

    def test_upper_bound_clamping(self):
        """Test that very high ARI is clamped to grade 20."""
        # Create extremely complex text with very long words and long sentences
        complex_words = [
            "antidisestablishmentarianism",
            "supercalifragilisticexpialidocious",
            "pneumonoultramicroscopicsilicovolcanoconiosis",
        ]
        # One very long sentence
        text = " ".join(complex_words * 50) + "."

        result = compute_ari(text)
        assert result.grade_level <= 20
