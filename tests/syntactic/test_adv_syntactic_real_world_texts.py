"""Tests for advanced syntactic analysis (Issue #17)."""

from pystylometry.syntactic.advanced_syntactic import compute_advanced_syntactic

# ===== Fixtures =====


# ===== Basic Functionality Tests =====


class TestRealWorldTexts:
    """Test with real-world text samples."""

    def test_news_article(self):
        """Test with news article text."""
        text = (
            "The government announced new policies yesterday. "
            "The policies will affect thousands of citizens. "
            "Officials said the changes were necessary for economic growth. "
            "Critics argued that the measures would harm vulnerable populations."
        )
        result = compute_advanced_syntactic(text)

        # News should have moderate complexity
        assert 0.2 <= result.sentence_complexity_score <= 0.6
        assert result.t_unit_count == 4

    def test_scientific_abstract(self):
        """Test with scientific abstract text."""
        text = (
            "This study investigated the effects of temperature on enzyme activity. "
            "The results demonstrated that optimal activity occurred at 37 degrees Celsius, "
            "which aligns with previous findings. "
            "These findings suggest that temperature regulation is critical for maintaining "
            "enzymatic function in biological systems."
        )
        result = compute_advanced_syntactic(text)

        # Scientific text should have high complexity
        assert result.sentence_complexity_score > 0.3
        assert result.clausal_density > 1.0

    def test_legal_document(self):
        """Test with legal document text."""
        text = (
            "The party of the first part agrees that they shall not disclose "
            "any confidential information that was obtained during the course "
            "of this agreement, unless such disclosure is required by law or "
            "authorized in writing by the party of the second part."
        )
        result = compute_advanced_syntactic(text)

        # Legal text should have very high complexity
        assert result.sentence_complexity_score > 0.4
        assert result.mean_parse_tree_depth > 4

    def test_fiction_narrative(self):
        """Test with fiction narrative text."""
        text = (
            "She walked slowly down the street. "
            "The rain fell steadily on her umbrella. "
            "She thought about the letter she had received. "
            "It changed everything."
        )
        result = compute_advanced_syntactic(text)

        # Fiction should have moderate complexity
        assert 0.1 <= result.sentence_complexity_score <= 0.5
        assert result.passive_voice_ratio < 0.3  # Mostly active voice
