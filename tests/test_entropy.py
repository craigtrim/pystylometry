"""Comprehensive tests for n-gram entropy and perplexity calculations."""

import math

from pystylometry.ngrams.entropy import (
    compute_character_bigram_entropy,
    compute_ngram_entropy,
    compute_word_bigram_entropy,
)


class TestEntropyBasicFunctionality:
    """Test basic entropy computation functionality."""

    def test_word_bigram_entropy(self):
        """Test word bigram entropy computation."""
        text = "The quick brown fox jumps over the lazy dog"
        result = compute_word_bigram_entropy(text)

        # Should return valid entropy and perplexity
        assert result.entropy > 0.0, "Entropy should be positive for diverse text"
        assert result.perplexity > 1.0, "Perplexity should be > 1"
        assert result.ngram_type == "word_2gram"

        # Metadata should contain expected fields
        assert "n" in result.metadata
        assert "ngram_type" in result.metadata
        assert "unique_ngrams" in result.metadata
        assert "total_ngrams" in result.metadata

        assert result.metadata["n"] == 2
        assert result.metadata["ngram_type"] == "word"

    def test_character_bigram_entropy(self):
        """Test character bigram entropy computation."""
        text = "The quick brown fox"
        result = compute_character_bigram_entropy(text)

        # Should return valid entropy and perplexity
        assert result.entropy > 0.0
        assert result.perplexity > 1.0
        assert result.ngram_type == "character_2gram"

        assert result.metadata["n"] == 2
        assert result.metadata["ngram_type"] == "character"

    def test_word_trigram_entropy(self):
        """Test word trigram entropy computation."""
        text = "The quick brown fox jumps over the lazy dog"
        result = compute_ngram_entropy(text, n=3, ngram_type="word")

        # Should return valid entropy and perplexity
        assert result.entropy > 0.0
        assert result.perplexity > 1.0
        assert result.ngram_type == "word_3gram"

        assert result.metadata["n"] == 3


class TestEntropyEdgeCases:
    """Test edge cases for entropy computation."""

    def test_empty_text(self):
        """Test entropy with empty text."""
        result = compute_word_bigram_entropy("")

        # Empty text should return 0 entropy, perplexity 1
        assert result.entropy == 0.0
        assert result.perplexity == 1.0
        assert result.metadata["item_count"] == 0
        assert "warning" in result.metadata

    def test_text_too_short_for_bigrams(self):
        """Test text shorter than n-gram size."""
        result = compute_ngram_entropy("one", n=2, ngram_type="word")

        # Single word can't make bigrams
        assert result.entropy == 0.0
        assert result.perplexity == 1.0
        assert "warning" in result.metadata
        assert result.metadata["warning"] == "Text too short for n-gram analysis"

    def test_text_too_short_for_trigrams(self):
        """Test text too short for trigrams."""
        result = compute_ngram_entropy("one two", n=3, ngram_type="word")

        # Two words can't make trigrams
        assert result.entropy == 0.0
        assert result.perplexity == 1.0
        assert "warning" in result.metadata

    def test_single_character(self):
        """Test with single character."""
        result = compute_character_bigram_entropy("a")

        assert result.entropy == 0.0
        assert result.perplexity == 1.0
        assert result.metadata["item_count"] == 1

    def test_whitespace_only(self):
        """Test with whitespace only."""
        result = compute_word_bigram_entropy("   \n\t  ")

        assert result.entropy == 0.0
        assert result.metadata["item_count"] == 0


class TestEntropyFormula:
    """Test entropy formula: H(X) = -Σ p(x) × log₂(p(x))."""

    def test_entropy_formula_manual_calculation(self):
        """Test entropy with manually verified calculation."""
        # Simple case: "A B A B" → bigrams: (A,B), (B,A), (A,B)
        # Frequencies: (A,B)=2, (B,A)=1, total=3
        # p(A,B) = 2/3, p(B,A) = 1/3
        # H = -(2/3 × log₂(2/3) + 1/3 × log₂(1/3))
        # H = -(2/3 × -0.585 + 1/3 × -1.585)
        # H = -(-0.390 + -0.528) = 0.918

        text = "A B A B"
        result = compute_ngram_entropy(text, n=2, ngram_type="word")

        # Manual calculation
        p1 = 2.0 / 3.0  # probability of (A, B)
        p2 = 1.0 / 3.0  # probability of (B, A)
        expected_entropy = -(p1 * math.log2(p1) + p2 * math.log2(p2))

        assert abs(result.entropy - expected_entropy) < 0.001, (
            f"Entropy should be {expected_entropy:.3f}"
        )

    def test_zero_entropy_for_uniform_ngrams(self):
        """Test that uniform n-grams produce maximum entropy."""
        # All n-grams identical → entropy should be 0
        text = "A A A A A"
        result = compute_ngram_entropy(text, n=2, ngram_type="word")

        # All bigrams are (A, A), so p=1, H = -(1 × log₂(1)) = 0
        assert result.entropy == 0.0, "Uniform n-grams should have zero entropy"
        assert result.perplexity == 1.0, "Perplexity should be 1 for zero entropy"

    def test_perplexity_formula(self):
        """Test perplexity = 2^entropy."""
        text = "The quick brown fox jumps over the lazy dog"
        result = compute_word_bigram_entropy(text)

        # Perplexity should equal 2^entropy
        expected_perplexity = 2**result.entropy
        assert abs(result.perplexity - expected_perplexity) < 0.001, (
            "Perplexity should equal 2^entropy"
        )


class TestEntropyDiversity:
    """Test entropy behavior with varying diversity levels."""

    def test_entropy_increases_with_diversity(self):
        """Test that entropy increases with more diverse n-grams."""
        # Low diversity (repetitive)
        repetitive_text = "the the the the the the the the"

        # High diversity (varied)
        diverse_text = "one two three four five six seven eight"

        result_repetitive = compute_word_bigram_entropy(repetitive_text)
        result_diverse = compute_word_bigram_entropy(diverse_text)

        # More diverse text should have higher entropy
        assert result_diverse.entropy > result_repetitive.entropy, (
            "Diverse text should have higher entropy"
        )
        assert result_diverse.perplexity > result_repetitive.perplexity, (
            "Diverse text should have higher perplexity"
        )

    def test_all_unique_ngrams_high_entropy(self):
        """Test that all unique n-grams produce maximum entropy."""
        # Every bigram is unique
        text = "A B C D E F G H"
        result = compute_ngram_entropy(text, n=2, ngram_type="word")

        # With all unique bigrams, entropy should be maximal
        # H_max = log₂(N) where N is number of unique n-grams
        unique_bigrams = result.metadata["unique_ngrams"]
        max_entropy = math.log2(unique_bigrams)

        assert abs(result.entropy - max_entropy) < 0.001, (
            "All unique n-grams should produce maximum entropy"
        )

    def test_character_vs_word_entropy(self):
        """Test that character and word entropy differ."""
        text = "The quick brown fox"

        result_char = compute_character_bigram_entropy(text)
        result_word = compute_word_bigram_entropy(text)

        # Character and word entropy should be different
        assert result_char.entropy != result_word.entropy, (
            "Character and word entropy should differ"
        )

        # Character entropy typically higher (more possible bigrams)
        assert result_char.perplexity != result_word.perplexity


class TestEntropyNgramSizes:
    """Test entropy with different n-gram sizes."""

    def test_bigrams_vs_trigrams(self):
        """Test that bigrams and trigrams produce different results."""
        text = "The quick brown fox jumps over the lazy dog"

        result_bigram = compute_ngram_entropy(text, n=2, ngram_type="word")
        result_trigram = compute_ngram_entropy(text, n=3, ngram_type="word")

        # Bigrams and trigrams should differ
        assert result_bigram.entropy != result_trigram.entropy
        assert result_bigram.metadata["unique_ngrams"] != result_trigram.metadata["unique_ngrams"]

        # Verify n values in metadata
        assert result_bigram.metadata["n"] == 2
        assert result_trigram.metadata["n"] == 3

    def test_higher_n_fewer_ngrams(self):
        """Test that higher n produces fewer total n-grams."""
        text = "one two three four five six seven"

        result_2 = compute_ngram_entropy(text, n=2, ngram_type="word")
        result_3 = compute_ngram_entropy(text, n=3, ngram_type="word")
        result_4 = compute_ngram_entropy(text, n=4, ngram_type="word")

        # Total n-grams decreases as n increases
        # For N items: N-n+1 total n-grams
        assert result_2.metadata["total_ngrams"] > result_3.metadata["total_ngrams"]
        assert result_3.metadata["total_ngrams"] > result_4.metadata["total_ngrams"]


class TestEntropyMetadata:
    """Test metadata returned with entropy results."""

    def test_metadata_contains_required_fields(self):
        """Test that metadata contains all required fields."""
        text = "The quick brown fox"
        result = compute_word_bigram_entropy(text)

        # Check all expected metadata fields
        assert "n" in result.metadata
        assert "ngram_type" in result.metadata
        assert "item_count" in result.metadata
        assert "unique_ngrams" in result.metadata
        assert "total_ngrams" in result.metadata

    def test_metadata_counts_accurate(self):
        """Test that metadata counts are accurate."""
        text = "one two three four"  # 4 words
        result = compute_ngram_entropy(text, n=2, ngram_type="word")

        # Should have 4 items (words)
        assert result.metadata["item_count"] == 4

        # Should have 3 total bigrams (4-2+1=3)
        assert result.metadata["total_ngrams"] == 3

        # All bigrams unique in this case
        assert result.metadata["unique_ngrams"] == 3

    def test_ngram_type_string_format(self):
        """Test that ngram_type is correctly formatted."""
        result_word = compute_ngram_entropy("one two three", n=2, ngram_type="word")
        result_char = compute_ngram_entropy("abc", n=2, ngram_type="character")

        assert result_word.ngram_type == "word_2gram"
        assert result_char.ngram_type == "character_2gram"

        result_trigram = compute_ngram_entropy("one two three four", n=3, ngram_type="word")
        assert result_trigram.ngram_type == "word_3gram"


class TestEntropyCharacterSpecific:
    """Test character-specific n-gram entropy."""

    def test_character_bigram_includes_spaces(self):
        """Test that character bigrams include spaces."""
        text = "a b"
        result = compute_character_bigram_entropy(text)

        # Should include: (a, ), ( ,b)
        # item_count includes all characters including spaces
        assert result.metadata["item_count"] == 3  # 'a', ' ', 'b'
        assert result.metadata["total_ngrams"] == 2  # (a, ), ( ,b)

    def test_character_entropy_case_sensitive(self):
        """Test that character entropy is case-sensitive."""
        text1 = "AAA"
        text2 = "AaA"

        result1 = compute_character_bigram_entropy(text1)
        result2 = compute_character_bigram_entropy(text2)

        # Same letters but different cases should produce different entropy
        # text1: (A,A), (A,A) - all same
        # text2: (A,a), (a,A) - different
        assert result2.entropy > result1.entropy


class TestEntropyWordSpecific:
    """Test word-specific n-gram entropy."""

    def test_word_tokenization(self):
        """Test that words are properly tokenized."""
        text = "one, two. three!"
        result = compute_word_bigram_entropy(text)

        # Should tokenize into words (punctuation removed)
        # Exact count depends on tokenizer, but should work
        assert result.metadata["item_count"] > 0
        assert result.entropy >= 0.0

    def test_word_case_handling(self):
        """Test word entropy with different cases."""
        # Word tokenization typically lowercases
        text = "The the THE"
        result = compute_word_bigram_entropy(text)

        # Should handle case (tokenizer behavior)
        assert result.metadata["item_count"] == 3


class TestEntropyRealText:
    """Test entropy with realistic text samples."""

    def test_prose_entropy(self):
        """Test entropy with prose sample."""
        text = (
            "The sun rose over the distant mountains, casting long shadows "
            "across the valley. Birds began their morning songs, and the "
            "world slowly awakened to a new day."
        )
        result = compute_word_bigram_entropy(text)

        # Should have reasonable entropy for natural prose
        assert result.entropy > 0.0
        assert result.perplexity > 1.0
        assert result.metadata["unique_ngrams"] > 0

    def test_repetitive_prose_lower_entropy(self):
        """Test that repetitive prose has lower entropy."""
        repetitive = (
            "The cat sat on the mat. The cat sat on the mat. "
            "The cat sat on the mat. The cat sat on the mat."
        )

        diverse = (
            "A quick brown fox jumps high. The lazy dog sleeps soundly. "
            "Birds fly south for winter. Fish swim in the ocean."
        )

        result_repetitive = compute_word_bigram_entropy(repetitive)
        result_diverse = compute_word_bigram_entropy(diverse)

        # Repetitive text should have lower entropy
        assert result_repetitive.entropy < result_diverse.entropy
