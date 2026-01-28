"""Comprehensive tests for hapax legomena and vocabulary richness metrics."""

from pystylometry.lexical import compute_hapax_with_lexicon_analysis


class TestHapaxLexiconAnalysis:
    """Test hapax legomena with lexicon-based categorization."""

    def test_basic_lexicon_categorization(self):
        """Test basic lexicon categorization of hapax words."""
        # Mix of common words and a neologism
        text = "The xyzabc platform facilitates collaboration"
        result = compute_hapax_with_lexicon_analysis(text)

        # Should have neologisms (xyzabc)
        assert "xyzabc" in result.lexicon_analysis.neologisms

        # Common words should be categorized
        assert len(result.lexicon_analysis.common_words) > 0

        # Ratios should sum to approximately 1.0
        total_ratio = (
            result.lexicon_analysis.neologism_ratio
            + result.lexicon_analysis.rare_word_ratio
            + result.lexicon_analysis.metadata["common_word_ratio"]
        )
        assert abs(total_ratio - 1.0) < 0.001

    def test_neologism_detection(self):
        """Test detection of neologisms (words not in either lexicon)."""
        # Made-up words that shouldn't be in BNC or WordNet
        text = "The xyzbot facilitates qwerty123 synergy"
        result = compute_hapax_with_lexicon_analysis(text)

        # xyzbot and qwerty123 should be neologisms
        neologisms = result.lexicon_analysis.neologisms
        assert len(neologisms) >= 2, "Should detect multiple neologisms"

        # Neologism ratio should be > 0
        assert result.lexicon_analysis.neologism_ratio > 0

    def test_common_word_detection(self):
        """Test detection of common words (in both lexicons)."""
        # All common English words
        text = "the quick brown fox jumps over lazy dog"
        result = compute_hapax_with_lexicon_analysis(text)

        # All hapax words should be common (in both BNC and WordNet)
        assert len(result.lexicon_analysis.common_words) > 0

        # Should have high common word ratio
        common_ratio = result.lexicon_analysis.metadata["common_word_ratio"]
        assert common_ratio > 0.5, "Most words should be common"

    def test_empty_text_lexicon_analysis(self):
        """Test lexicon analysis with empty text."""
        result = compute_hapax_with_lexicon_analysis("")

        # Should return empty categorization
        assert result.lexicon_analysis.neologisms == []
        assert result.lexicon_analysis.rare_words == []
        assert result.lexicon_analysis.common_words == []
        assert result.lexicon_analysis.neologism_ratio == 0.0
        assert result.lexicon_analysis.rare_word_ratio == 0.0

    def test_no_hapax_lexicon_analysis(self):
        """Test lexicon analysis when there are no hapax legomena."""
        # All words repeat
        text = "the the cat cat dog dog"
        result = compute_hapax_with_lexicon_analysis(text)

        # No hapax means no categorization
        assert result.hapax_result.hapax_count == 0
        assert result.lexicon_analysis.neologisms == []
        assert result.lexicon_analysis.rare_words == []
        assert result.lexicon_analysis.common_words == []

    def test_lexicon_result_structure(self):
        """Test that lexicon result has correct structure."""
        text = "The quick brown fox jumps"
        result = compute_hapax_with_lexicon_analysis(text)

        # Should have both hapax result and lexicon analysis
        assert hasattr(result, "hapax_result")
        assert hasattr(result, "lexicon_analysis")
        assert hasattr(result, "metadata")

        # Hapax result should be valid
        assert result.hapax_result.hapax_count > 0

        # Lexicon analysis should have all required fields
        assert hasattr(result.lexicon_analysis, "neologisms")
        assert hasattr(result.lexicon_analysis, "rare_words")
        assert hasattr(result.lexicon_analysis, "common_words")
        assert hasattr(result.lexicon_analysis, "neologism_ratio")
        assert hasattr(result.lexicon_analysis, "rare_word_ratio")

    def test_lexicon_analysis_metadata(self):
        """Test metadata in lexicon analysis."""
        text = "The xyzabc platform facilitates collaboration"
        result = compute_hapax_with_lexicon_analysis(text)

        # Should have metadata with counts
        meta = result.lexicon_analysis.metadata
        assert "total_hapax" in meta
        assert "neologism_count" in meta
        assert "rare_word_count" in meta
        assert "common_word_count" in meta

        # Counts should sum to total hapax
        total = meta["neologism_count"] + meta["rare_word_count"] + meta["common_word_count"]
        assert total == meta["total_hapax"]

    def test_sorted_word_lists(self):
        """Test that word lists are sorted alphabetically."""
        text = "The zebra xyzabc apple banana platform"
        result = compute_hapax_with_lexicon_analysis(text)

        # Lists should be sorted
        if result.lexicon_analysis.neologisms:
            assert result.lexicon_analysis.neologisms == sorted(result.lexicon_analysis.neologisms)

        if result.lexicon_analysis.rare_words:
            assert result.lexicon_analysis.rare_words == sorted(result.lexicon_analysis.rare_words)

        if result.lexicon_analysis.common_words:
            assert result.lexicon_analysis.common_words == sorted(
                result.lexicon_analysis.common_words
            )
