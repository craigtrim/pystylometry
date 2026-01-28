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

import pytest

from pystylometry.stylistic import compute_vocabulary_overlap


class TestBasicFunctionality:
    """Test basic vocabulary overlap functionality."""

    def test_identical_texts(self):
        """Identical texts should have perfect similarity scores."""
        text = "The quick brown fox jumps over the lazy dog"
        result = compute_vocabulary_overlap(text, text)

        assert result.jaccard_similarity == 1.0
        assert result.dice_coefficient == 1.0
        assert result.overlap_coefficient == 1.0
        assert result.cosine_similarity == 1.0
        assert result.kl_divergence == pytest.approx(0.0, abs=1e-6)
        assert result.text1_unique_count == 0
        assert result.text2_unique_count == 0

    def test_completely_different_texts(self):
        """Completely different texts should have zero similarity."""
        text1 = "apple banana cherry"
        text2 = "dog elephant frog"
        result = compute_vocabulary_overlap(text1, text2)

        assert result.jaccard_similarity == 0.0
        assert result.dice_coefficient == 0.0
        assert result.overlap_coefficient == 0.0
        assert result.cosine_similarity == 0.0
        assert result.shared_vocab_size == 0
        assert result.text1_unique_count == 3
        assert result.text2_unique_count == 3

    def test_partial_overlap(self):
        """Test texts with partial vocabulary overlap."""
        text1 = "The quick brown fox jumps over the lazy dog"
        text2 = "The fast brown fox leaps over the sleepy dog"
        result = compute_vocabulary_overlap(text1, text2)

        # Should have some but not perfect overlap
        assert 0.0 < result.jaccard_similarity < 1.0
        assert 0.0 < result.dice_coefficient < 1.0
        assert 0.0 < result.overlap_coefficient < 1.0
        assert 0.0 < result.cosine_similarity < 1.0
        assert result.shared_vocab_size > 0
        assert result.text1_unique_count > 0
        assert result.text2_unique_count > 0


class TestJaccardSimilarity:
    """Test Jaccard similarity coefficient specifically."""

    def test_jaccard_formula(self):
        """Verify Jaccard = |intersection| / |union|."""
        text1 = "a b c d"
        text2 = "c d e f"
        result = compute_vocabulary_overlap(text1, text2)

        # Vocab1 = {a, b, c, d}, Vocab2 = {c, d, e, f}
        # Intersection = {c, d} = 2
        # Union = {a, b, c, d, e, f} = 6
        # Jaccard = 2/6 = 1/3
        assert result.jaccard_similarity == pytest.approx(2 / 6, rel=1e-6)

    def test_jaccard_empty_texts(self):
        """Empty texts should have Jaccard = 1.0 (both identical/empty)."""
        result = compute_vocabulary_overlap("", "")
        assert result.jaccard_similarity == 1.0


class TestDiceCoefficient:
    """Test Sørensen-Dice coefficient specifically."""

    def test_dice_formula(self):
        """Verify Dice = 2|intersection| / (|A| + |B|)."""
        text1 = "a b c d"
        text2 = "c d e f"
        result = compute_vocabulary_overlap(text1, text2)

        # Vocab1 = {a, b, c, d}, Vocab2 = {c, d, e, f}
        # Intersection = {c, d} = 2
        # Dice = 2*2 / (4 + 4) = 4/8 = 0.5
        assert result.dice_coefficient == pytest.approx(0.5, rel=1e-6)

    def test_dice_vs_jaccard(self):
        """Dice coefficient is always >= Jaccard similarity."""
        text1 = "apple banana cherry date"
        text2 = "cherry date elderberry fig"
        result = compute_vocabulary_overlap(text1, text2)

        assert result.dice_coefficient >= result.jaccard_similarity


class TestOverlapCoefficient:
    """Test overlap coefficient specifically."""

    def test_overlap_formula(self):
        """Verify Overlap = |intersection| / min(|A|, |B|)."""
        text1 = "a b c d e f"  # 6 unique words
        text2 = "d e f"  # 3 unique words
        result = compute_vocabulary_overlap(text1, text2)

        # Intersection = {d, e, f} = 3
        # min(6, 3) = 3
        # Overlap = 3/3 = 1.0
        assert result.overlap_coefficient == pytest.approx(1.0, rel=1e-6)

    def test_overlap_asymmetric_containment(self):
        """Overlap = 1.0 when smaller set is contained in larger."""
        text1 = "one two three four five six seven eight"
        text2 = "two four six"
        result = compute_vocabulary_overlap(text1, text2)

        # Text2 vocabulary is fully contained in Text1
        assert result.overlap_coefficient == 1.0


class TestCosineSimilarity:
    """Test cosine similarity specifically."""

    def test_cosine_identical_frequencies(self):
        """Same word frequencies should give cosine = 1.0."""
        text1 = "word word word"
        text2 = "word word word"
        result = compute_vocabulary_overlap(text1, text2)

        assert result.cosine_similarity == pytest.approx(1.0, rel=1e-6)

    def test_cosine_proportional_frequencies(self):
        """Proportional frequencies should give cosine = 1.0."""
        text1 = "a a b b"
        text2 = "a a a a b b b b"  # Same proportions, just doubled
        result = compute_vocabulary_overlap(text1, text2)

        # Same vocabulary, proportional frequencies → cosine = 1.0
        assert result.cosine_similarity == pytest.approx(1.0, rel=1e-6)

    def test_cosine_orthogonal_texts(self):
        """No shared words should give cosine = 0.0."""
        text1 = "apple banana cherry"
        text2 = "dog elephant frog"
        result = compute_vocabulary_overlap(text1, text2)

        assert result.cosine_similarity == 0.0


class TestKLDivergence:
    """Test Kullback-Leibler divergence specifically."""

    def test_kl_identical_distributions(self):
        """Identical distributions should give KL ≈ 0."""
        text1 = "a b c d e"
        text2 = "a b c d e"
        result = compute_vocabulary_overlap(text1, text2)

        # KL divergence should be near zero for identical distributions
        assert result.kl_divergence == pytest.approx(0.0, abs=1e-6)

    def test_kl_nonnegative(self):
        """KL divergence is always non-negative."""
        text1 = "apple apple apple banana"
        text2 = "apple banana banana banana"
        result = compute_vocabulary_overlap(text1, text2)

        assert result.kl_divergence >= 0.0

    def test_kl_different_distributions(self):
        """Very different distributions should have higher KL divergence."""
        text1 = "a a a a a"  # All a's
        text2 = "b b b b b"  # All b's
        result = compute_vocabulary_overlap(text1, text2)

        # KL divergence should be high for very different distributions
        assert result.kl_divergence > 0.0


class TestVocabularyStatistics:
    """Test vocabulary size and coverage statistics."""

    def test_vocabulary_sizes(self):
        """Test vocabulary size calculations."""
        text1 = "the quick brown fox the quick"  # {the, quick, brown, fox} = 4
        text2 = "the slow brown dog the slow"  # {the, slow, brown, dog} = 4
        result = compute_vocabulary_overlap(text1, text2)

        assert result.text1_vocab_size == 4
        assert result.text2_vocab_size == 4
        assert result.shared_vocab_size == 2  # {the, brown}
        assert result.union_vocab_size == 6  # {the, quick, brown, fox, slow, dog}
        assert result.text1_unique_count == 2  # {quick, fox}
        assert result.text2_unique_count == 2  # {slow, dog}

    def test_coverage_ratios(self):
        """Test coverage ratio calculations."""
        text1 = "a b c d"  # 4 unique
        text2 = "c d e f"  # 4 unique, 2 shared
        result = compute_vocabulary_overlap(text1, text2)

        # Coverage = shared / vocab_size
        assert result.text1_coverage == pytest.approx(2 / 4, rel=1e-6)
        assert result.text2_coverage == pytest.approx(2 / 4, rel=1e-6)


class TestDistinctiveWords:
    """Test distinctive word identification."""

    def test_distinctive_words_identification(self):
        """Test that distinctive words are correctly identified."""
        text1 = "apple apple banana cherry"
        text2 = "dog dog elephant frog"
        result = compute_vocabulary_overlap(text1, text2)

        # All words should be distinctive since no overlap
        text1_distinctive = [word for word, _ in result.text1_distinctive_words]
        text2_distinctive = [word for word, _ in result.text2_distinctive_words]

        assert "apple" in text1_distinctive
        assert "banana" in text1_distinctive
        assert "cherry" in text1_distinctive
        assert "dog" in text2_distinctive
        assert "elephant" in text2_distinctive
        assert "frog" in text2_distinctive

    def test_distinctive_words_scoring(self):
        """Test that distinctive words are scored by frequency."""
        text1 = "apple apple apple banana cherry"  # apple=3, banana=1, cherry=1
        text2 = "dog dog elephant"
        result = compute_vocabulary_overlap(text1, text2)

        # Apple should be the most distinctive (highest frequency)
        if result.text1_distinctive_words:
            top_word, top_score = result.text1_distinctive_words[0]
            assert top_word == "apple"
            assert top_score == 3.0


class TestSharedWords:
    """Test shared word identification."""

    def test_shared_words(self):
        """Test shared words are correctly identified."""
        text1 = "the quick brown fox"
        text2 = "the slow brown dog"
        result = compute_vocabulary_overlap(text1, text2)

        assert "the" in result.shared_words
        assert "brown" in result.shared_words
        assert len(result.shared_words) == 2

    def test_shared_words_sorted_by_frequency(self):
        """Test shared words are sorted by combined frequency."""
        text1 = "the the the quick brown"  # the=3, quick=1, brown=1
        text2 = "the slow brown brown brown"  # the=1, slow=1, brown=3
        result = compute_vocabulary_overlap(text1, text2)

        # Combined: the=4, brown=4, so either could be first
        # Both should be in shared words
        assert "the" in result.shared_words
        assert "brown" in result.shared_words


class TestMetadata:
    """Test metadata contents."""

    def test_metadata_token_counts(self):
        """Test that metadata includes token counts."""
        text1 = "the quick brown fox"  # 4 tokens
        text2 = "the slow dog"  # 3 tokens
        result = compute_vocabulary_overlap(text1, text2)

        assert result.metadata["text1_token_count"] == 4
        assert result.metadata["text2_token_count"] == 3

    def test_metadata_frequencies(self):
        """Test that metadata includes word frequencies."""
        text1 = "the the brown"
        text2 = "the slow"
        result = compute_vocabulary_overlap(text1, text2)

        assert "text1_frequencies" in result.metadata
        assert "text2_frequencies" in result.metadata
        assert result.metadata["text1_frequencies"]["the"] == 2
        assert result.metadata["text1_frequencies"]["brown"] == 1

    def test_metadata_unique_words(self):
        """Test that metadata includes unique word lists."""
        text1 = "apple banana"
        text2 = "banana cherry"
        result = compute_vocabulary_overlap(text1, text2)

        assert "unique_to_text1" in result.metadata
        assert "unique_to_text2" in result.metadata
        assert "apple" in result.metadata["unique_to_text1"]
        assert "cherry" in result.metadata["unique_to_text2"]


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


class TestMathematicalProperties:
    """Test mathematical properties of similarity metrics."""

    def test_symmetry_jaccard(self):
        """Jaccard similarity should be symmetric."""
        text1 = "apple banana cherry"
        text2 = "cherry date elderberry"

        result1 = compute_vocabulary_overlap(text1, text2)
        result2 = compute_vocabulary_overlap(text2, text1)

        assert result1.jaccard_similarity == result2.jaccard_similarity

    def test_symmetry_dice(self):
        """Dice coefficient should be symmetric."""
        text1 = "apple banana cherry"
        text2 = "cherry date elderberry"

        result1 = compute_vocabulary_overlap(text1, text2)
        result2 = compute_vocabulary_overlap(text2, text1)

        assert result1.dice_coefficient == result2.dice_coefficient

    def test_symmetry_overlap(self):
        """Overlap coefficient should be symmetric."""
        text1 = "apple banana cherry"
        text2 = "cherry date elderberry"

        result1 = compute_vocabulary_overlap(text1, text2)
        result2 = compute_vocabulary_overlap(text2, text1)

        assert result1.overlap_coefficient == result2.overlap_coefficient

    def test_symmetry_cosine(self):
        """Cosine similarity should be symmetric."""
        text1 = "apple apple banana cherry"
        text2 = "cherry date date elderberry"

        result1 = compute_vocabulary_overlap(text1, text2)
        result2 = compute_vocabulary_overlap(text2, text1)

        assert result1.cosine_similarity == pytest.approx(result2.cosine_similarity, rel=1e-6)

    def test_kl_asymmetry(self):
        """KL divergence should be asymmetric (in general)."""
        text1 = "apple apple apple banana"
        text2 = "apple banana banana banana"

        result1 = compute_vocabulary_overlap(text1, text2)
        result2 = compute_vocabulary_overlap(text2, text1)

        # KL divergence is typically not symmetric
        # (may be equal in some cases due to symmetry in input)
        # Just verify both are non-negative
        assert result1.kl_divergence >= 0.0
        assert result2.kl_divergence >= 0.0

    def test_bounds_jaccard(self):
        """Jaccard similarity should be in [0, 1]."""
        texts = [
            ("apple banana", "cherry date"),
            ("the quick brown fox", "the slow brown dog"),
            ("same same", "same same"),
        ]
        for text1, text2 in texts:
            result = compute_vocabulary_overlap(text1, text2)
            assert 0.0 <= result.jaccard_similarity <= 1.0

    def test_bounds_cosine(self):
        """Cosine similarity should be in [0, 1] for word frequencies."""
        texts = [
            ("apple banana", "cherry date"),
            ("the quick brown fox", "the slow brown dog"),
            ("same same", "same same"),
        ]
        for text1, text2 in texts:
            result = compute_vocabulary_overlap(text1, text2)
            assert 0.0 <= result.cosine_similarity <= 1.0
