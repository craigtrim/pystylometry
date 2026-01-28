"""Tests for sentence type classification (Issue #18)."""

from pystylometry.syntactic.sentence_types import compute_sentence_types

# ===== Fixtures =====


# ===== Basic Functionality Tests =====


class TestRealWorldTexts:
    """Test with real-world text samples."""

    def test_academic_abstract(self):
        """Test with academic journal abstract."""
        text = (
            "This study investigated the effects of syntactic complexity on readability. "
            "The results demonstrated that parse tree depth correlates with perceived difficulty, "
            "which aligns with previous findings. "
            "These findings suggest that syntactic analysis provides valuable insights into text complexity."
        )
        result = compute_sentence_types(text)

        # Academic: mostly declarative, some complex
        assert result.declarative_ratio >= 0.9
        assert result.complex_ratio > 0

    def test_news_article(self):
        """Test with news article text."""
        text = (
            "The government announced new policies yesterday. "
            "The policies will affect thousands of citizens. "
            "Officials said the changes were necessary for economic growth. "
            "Critics argued that the measures would harm vulnerable populations."
        )
        result = compute_sentence_types(text)

        # News: declarative dominant, mix of simple/complex
        assert result.declarative_ratio >= 0.9
        assert result.simple_count + result.complex_count >= 2

    def test_fiction_narrative(self):
        """Test with fiction narrative."""
        text = (
            "She walked slowly down the dark street. "
            "The rain fell and the wind howled. "
            "When she reached the corner, she stopped. "
            "What should she do now?"
        )
        result = compute_sentence_types(text)

        # Fiction: variety of types
        assert result.total_sentences == 4
        assert result.structural_diversity > 0

    def test_instruction_manual(self):
        """Test with instruction manual."""
        text = (
            "Read all instructions before beginning. "
            "Remove all parts from the packaging. "
            "Place the base on a flat surface. "
            "Tighten all screws firmly."
        )
        result = compute_sentence_types(text)

        # Instructions: high imperative ratio
        assert result.imperative_count >= 2

    def test_conversational_dialog(self):
        """Test with conversational dialog."""
        text = (
            "How are you today? "
            "I'm doing well, thank you! "
            "What have you been up to? "
            "Just working on some projects."
        )
        result = compute_sentence_types(text)

        # Dialog: questions and variety
        assert result.interrogative_count >= 1
        assert result.total_sentences == 4
