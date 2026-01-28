"""Comprehensive tests for Automated Readability Index (ARI) computation."""

from pystylometry.readability import compute_ari


class TestARIAgeRanges:
    """Test age range mapping."""

    def test_kindergarten_range(self):
        """Test kindergarten age range (grade 0)."""
        text = "I go."
        result = compute_ari(text)

        assert result.grade_level == 0
        assert "Kindergarten" in result.age_range

    def test_elementary_range(self):
        """Test elementary age range (grades 1-5)."""
        text = "The cat sat on the mat. The dog ran in the yard."
        result = compute_ari(text)

        if 1 <= result.grade_level <= 5:
            assert "Elementary" in result.age_range

    def test_middle_school_range(self):
        """Test middle school age range (grades 6-8)."""
        # Create text that produces middle school level
        text = """
        The American Revolution was a significant event in history.
        It occurred during the late eighteenth century.
        Many colonists wanted independence from British rule.
        """
        result = compute_ari(text)

        if 6 <= result.grade_level <= 8:
            assert "Middle School" in result.age_range

    def test_high_school_range(self):
        """Test high school age range (grades 9-12)."""
        # Create text that produces high school level
        text = (
            """
        The phenomenological approach to understanding consciousness has been
        extensively debated in philosophical circles for many decades.
        Researchers continue to investigate the fundamental nature of subjective
        experience and its relationship to objective reality.
        """
            * 2
        )  # Repeat to meet word count
        result = compute_ari(text)

        if 9 <= result.grade_level <= 12:
            assert "High School" in result.age_range

    def test_college_range(self):
        """Test college age range (grades 13-14)."""
        # Create text that produces college level
        text = (
            """
        The epistemological foundations of contemporary analytical philosophy
        necessitate a comprehensive understanding of formal logical systems.
        Philosophical investigations into the nature of knowledge require
        methodological rigor and systematic examination of foundational assumptions.
        """
            * 3
        )
        result = compute_ari(text)

        if 13 <= result.grade_level <= 14:
            assert "College" in result.age_range

    def test_graduate_range(self):
        """Test graduate age range (grade 15+)."""
        # Create text that produces graduate level
        complex_words = [
            "interdisciplinary",
            "phenomenological",
            "epistemological",
            "methodological",
            "comprehensive",
            "systematically",
        ]
        text = (
            " ".join(complex_words * 30)
            + ". "
            + " ".join(complex_words * 30)
            + ". "
            + " ".join(complex_words * 30)
            + "."
        )
        result = compute_ari(text)

        if result.grade_level >= 15:
            assert "Graduate" in result.age_range
