"""Comprehensive tests for vocabulary overlap and similarity metrics.

This module tests the vocabulary overlap functionality, including Jaccard
similarity, Sørensen-Dice coefficient, overlap coefficient, cosine similarity,
and KL divergence.

Related GitHub Issue:
    #21 - Vocabulary Overlap and Similarity Metrics
    https://github.com/craigtrim/pystylometry/issues/21

References:
    Jaccard, P. (1912). The distribution of the flora in the alpine zone.
    Sørensen, T. (1948). A method of establishing groups of equal amplitude.
    Salton, G., & McGill, M. J. (1983). Introduction to Modern Information Retrieval.
    Kullback, S., & Leibler, R. A. (1951). On Information and Sufficiency.
    Manning, C. D., & Schütze, H. (1999). Foundations of Statistical NLP.
"""

from pystylometry.stylistic import compute_vocabulary_overlap


class TestEdgeCases:
    """Test edge cases and special inputs."""

    def test_empty_text1(self):
        """Test with empty first text."""
        text1 = ""
        text2 = "some words here"
        result = compute_vocabulary_overlap(text1, text2)

        assert result.text1_vocab_size == 0
        assert result.jaccard_similarity == 0.0
        assert result.shared_vocab_size == 0

    def test_empty_text2(self):
        """Test with empty second text."""
        text1 = "some words here"
        text2 = ""
        result = compute_vocabulary_overlap(text1, text2)

        assert result.text2_vocab_size == 0
        assert result.jaccard_similarity == 0.0
        assert result.shared_vocab_size == 0

    def test_both_empty(self):
        """Test with both texts empty."""
        result = compute_vocabulary_overlap("", "")

        assert result.jaccard_similarity == 1.0  # Both empty = identical
        assert result.dice_coefficient == 1.0
        assert result.overlap_coefficient == 1.0

    def test_single_word_texts(self):
        """Test with single word texts."""
        result = compute_vocabulary_overlap("hello", "hello")

        assert result.jaccard_similarity == 1.0
        assert result.shared_vocab_size == 1
        assert result.text1_vocab_size == 1
        assert result.text2_vocab_size == 1

    def test_case_insensitive(self):
        """Test that comparison is case-insensitive."""
        text1 = "The QUICK Brown Fox"
        text2 = "the quick brown fox"
        result = compute_vocabulary_overlap(text1, text2)

        assert result.jaccard_similarity == 1.0
        assert result.text1_unique_count == 0
        assert result.text2_unique_count == 0

    def test_punctuation_ignored(self):
        """Test that punctuation is properly handled."""
        text1 = "Hello, world! How are you?"
        text2 = "Hello world how are you"
        result = compute_vocabulary_overlap(text1, text2)

        # Should be identical after tokenization
        assert result.jaccard_similarity == 1.0

    def test_numbers_ignored(self):
        """Test that numbers are excluded from vocabulary."""
        text1 = "I have 3 apples and 5 oranges"
        text2 = "I have apples and oranges"
        result = compute_vocabulary_overlap(text1, text2)

        # Numbers should be stripped, leaving same vocabulary
        assert result.jaccard_similarity == 1.0

    def test_large_texts(self):
        """Test with larger texts to ensure performance."""
        # Generate large texts with known overlap using alphabetic-only words
        # Use letter combinations to create unique words
        letters = "abcdefghij"
        common_words = [f"common{a}{b}" for a in letters for b in letters][:100]
        unique1_words = [f"firsttext{a}{b}" for a in letters for b in letters[:5]]
        unique2_words = [f"secondtext{a}{b}" for a in letters for b in letters[:5]]

        common = " ".join(common_words)
        unique1 = " ".join(unique1_words)
        unique2 = " ".join(unique2_words)

        text1 = common + " " + unique1
        text2 = common + " " + unique2

        result = compute_vocabulary_overlap(text1, text2)

        assert result.text1_vocab_size == 150  # 100 common + 50 unique
        assert result.text2_vocab_size == 150
        assert result.shared_vocab_size == 100
        assert result.text1_unique_count == 50
        assert result.text2_unique_count == 50
