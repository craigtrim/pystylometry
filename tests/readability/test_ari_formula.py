"""Comprehensive tests for Automated Readability Index (ARI) computation."""

from pystylometry.readability import compute_ari


class TestARIFormula:
    """Test formula correctness."""

    def test_formula_components(self):
        """Verify formula components are calculated correctly."""
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_ari(text)

        chars_per_word = result.metadata["characters_per_word"]
        words_per_sent = result.metadata["words_per_sentence"]

        # Manual calculation: ARI = 4.71 × chars_per_word + 0.5 × words_per_sent - 21.43
        expected_ari = 4.71 * chars_per_word + 0.5 * words_per_sent - 21.43

        # Should match within floating point precision
        assert abs(result.ari_score - expected_ari) < 0.0001

    def test_longer_words_increase_score(self):
        """Test that longer words increase ARI score."""
        short_words = "The cat sat on the mat and ate the food."
        long_words = "The feline positioned itself upon the textile floor covering."

        result_short = compute_ari(short_words)
        result_long = compute_ari(long_words)

        # Longer words should produce higher character count per word
        assert (
            result_long.metadata["characters_per_word"]
            > result_short.metadata["characters_per_word"]
        )

    def test_longer_sentences_increase_score(self):
        """Test that longer sentences increase ARI score."""
        short_sentences = "The cat sat. The dog ran. The bird flew."
        long_sentence = "The cat sat on the mat while the dog ran around the yard."

        result_short = compute_ari(short_sentences)
        result_long = compute_ari(long_sentence)

        # Longer average sentence length should produce higher words per sentence
        assert (
            result_long.metadata["words_per_sentence"] > result_short.metadata["words_per_sentence"]
        )
