"""Tests for n-gram entropy and perplexity calculations.

Related GitHub Issue:
    #27 - Native chunked analysis with Distribution dataclass
    https://github.com/craigtrim/pystylometry/issues/27

Tests cover:
    - _compute_ngram_entropy_single: character/word bigrams, trigrams,
      short text, empty text, uniform distribution, maximum entropy
    - compute_ngram_entropy: single chunk, multiple chunks, empty text,
      entropy/perplexity relationship, distribution stats, metadata fields
    - Character vs word bigrams: same text gives different results
    - Convenience functions: compute_character_bigram_entropy,
      compute_word_bigram_entropy
    - Edge cases: single word, single character, very long text,
      text shorter than chunk_size
    - Mathematical properties: entropy >= 0, perplexity >= 1,
      higher diversity = higher entropy
"""

import math

from pystylometry.ngrams.entropy import (
    _compute_ngram_entropy_single,
    compute_character_bigram_entropy,
    compute_ngram_entropy,
    compute_word_bigram_entropy,
)


# =============================================================================
# _compute_ngram_entropy_single TESTS
# =============================================================================


class TestComputeNgramEntropySingleCharacterBigrams:
    """Tests for _compute_ngram_entropy_single with character bigrams."""

    def test_character_bigram_basic(self):
        """Character bigrams produce finite entropy for normal text."""
        text = "abcdefghij"
        entropy, perplexity, meta = _compute_ngram_entropy_single(text, n=2, ngram_type="character")
        assert not math.isnan(entropy)
        assert entropy > 0
        assert meta["total_ngrams"] == 9  # 10 chars -> 9 bigrams

    def test_character_bigram_repeated_pair(self):
        """Repeating an alternating pattern produces exactly 2 unique bigrams."""
        # "abababab" (8 chars) -> bigrams: (a,b),(b,a),(a,b),(b,a),(a,b),(b,a),(a,b)
        # 4 x (a,b) and 3 x (b,a) -- not quite uniform, but close to log2(2)=1.0
        # With even count "abab" (4 chars) -> (a,b),(b,a),(a,b) = 2x(a,b) + 1x(b,a)
        # Use 2-char repeat "ababababab" (10 chars) -> 5x(a,b) + 4x(b,a) = 9 total
        # For perfect uniformity: "abba" -> (a,b),(b,b),(b,a) = 3 unique, not what we want
        # Just verify 2 unique bigrams and entropy between 0 and 1
        text = "ababab"
        entropy, perplexity, meta = _compute_ngram_entropy_single(text, n=2, ngram_type="character")
        assert meta["unique_ngrams"] == 2
        assert 0 < entropy < 1.01  # close to 1.0 but not exact due to uneven counts

    def test_character_bigram_all_same(self):
        """All identical characters means one bigram -> zero entropy."""
        text = "aaaaaaa"
        entropy, perplexity, meta = _compute_ngram_entropy_single(text, n=2, ngram_type="character")
        assert entropy == 0.0
        assert perplexity == 1.0
        assert meta["unique_ngrams"] == 1


class TestComputeNgramEntropySingleWordBigrams:
    """Tests for _compute_ngram_entropy_single with word bigrams."""

    def test_word_bigram_basic(self):
        """Word bigrams produce finite entropy for multi-word text."""
        text = "the cat sat on the mat near the hat"
        entropy, perplexity, meta = _compute_ngram_entropy_single(text, n=2, ngram_type="word")
        assert not math.isnan(entropy)
        assert entropy > 0
        assert meta["total_ngrams"] > 0

    def test_word_bigram_two_words(self):
        """Exactly two words yield exactly one bigram -> zero entropy."""
        text = "hello world"
        entropy, perplexity, meta = _compute_ngram_entropy_single(text, n=2, ngram_type="word")
        assert entropy == 0.0
        assert meta["total_ngrams"] == 1
        assert meta["unique_ngrams"] == 1

    def test_word_bigram_repeated_phrase(self):
        """Repeated two-word phrase means one bigram type -> zero entropy."""
        text = "go go go go go"
        entropy, perplexity, meta = _compute_ngram_entropy_single(text, n=2, ngram_type="word")
        # All bigrams are ("go", "go") -> zero entropy
        assert entropy == 0.0
        assert meta["unique_ngrams"] == 1


class TestComputeNgramEntropySingleTrigrams:
    """Tests for _compute_ngram_entropy_single with trigrams (n=3)."""

    def test_word_trigram_basic(self):
        """Word trigrams produce finite entropy for adequate text."""
        text = "one two three four five six seven eight nine ten"
        entropy, perplexity, meta = _compute_ngram_entropy_single(text, n=3, ngram_type="word")
        assert not math.isnan(entropy)
        assert entropy > 0

    def test_character_trigram_basic(self):
        """Character trigrams work correctly."""
        text = "abcdefghijklmno"
        entropy, perplexity, meta = _compute_ngram_entropy_single(text, n=3, ngram_type="character")
        assert not math.isnan(entropy)
        # 15 chars -> 13 trigrams, all unique -> entropy = log2(13)
        assert meta["total_ngrams"] == 13
        assert meta["unique_ngrams"] == 13
        assert abs(entropy - math.log2(13)) < 0.001


class TestComputeNgramEntropySingleShortText:
    """Tests for _compute_ngram_entropy_single with text shorter than n."""

    def test_single_char_with_bigram(self):
        """A single character cannot form a bigram -> NaN."""
        entropy, perplexity, meta = _compute_ngram_entropy_single("a", n=2, ngram_type="character")
        assert math.isnan(entropy)
        assert math.isnan(perplexity)
        assert meta["unique_ngrams"] == 0
        assert meta["total_ngrams"] == 0

    def test_single_word_with_word_bigram(self):
        """A single word cannot form a word bigram -> NaN."""
        entropy, perplexity, meta = _compute_ngram_entropy_single("hello", n=2, ngram_type="word")
        assert math.isnan(entropy)
        assert math.isnan(perplexity)

    def test_two_chars_with_trigram(self):
        """Two characters cannot form a trigram -> NaN."""
        entropy, perplexity, meta = _compute_ngram_entropy_single("ab", n=3, ngram_type="character")
        assert math.isnan(entropy)
        assert meta["item_count"] == 2


class TestComputeNgramEntropySingleEmptyText:
    """Tests for _compute_ngram_entropy_single with empty text."""

    def test_empty_string(self):
        """Empty string returns NaN entropy and zero counts."""
        entropy, perplexity, meta = _compute_ngram_entropy_single("", n=2, ngram_type="word")
        assert math.isnan(entropy)
        assert math.isnan(perplexity)
        assert meta["item_count"] == 0
        assert meta["unique_ngrams"] == 0
        assert meta["total_ngrams"] == 0

    def test_empty_string_character(self):
        """Empty string with character bigrams also returns NaN."""
        entropy, perplexity, meta = _compute_ngram_entropy_single("", n=2, ngram_type="character")
        assert math.isnan(entropy)
        assert meta["item_count"] == 0


class TestComputeNgramEntropySingleMaximumEntropy:
    """Tests for maximum entropy (uniform distribution)."""

    def test_uniform_character_bigrams(self):
        """All unique bigrams -> maximum entropy = log2(count)."""
        # "abcdef" -> 5 unique bigrams: ab, bc, cd, de, ef
        text = "abcdef"
        entropy, perplexity, meta = _compute_ngram_entropy_single(text, n=2, ngram_type="character")
        expected = math.log2(5)
        assert abs(entropy - expected) < 0.001
        assert meta["unique_ngrams"] == 5

    def test_perplexity_equals_unique_count_for_uniform(self):
        """When all bigrams are unique, perplexity == number of bigrams."""
        text = "abcdefghij"
        entropy, perplexity, meta = _compute_ngram_entropy_single(text, n=2, ngram_type="character")
        # 9 unique bigrams, uniform -> perplexity = 9
        assert abs(perplexity - 9.0) < 0.001


# =============================================================================
# compute_ngram_entropy TESTS
# =============================================================================


class TestComputeNgramEntropySingleChunk:
    """Tests for compute_ngram_entropy with text fitting in one chunk."""

    def test_single_chunk_returns_valid_result(self):
        """Short text that fits in one chunk produces a valid EntropyResult."""
        text = "the cat sat on the mat by the hat"
        result = compute_ngram_entropy(text, n=2, ngram_type="word", chunk_size=1000)
        assert not math.isnan(result.entropy)
        assert not math.isnan(result.perplexity)
        assert result.chunk_count == 1

    def test_single_chunk_distribution_has_one_value(self):
        """Single chunk means the distribution has exactly one value."""
        text = "the cat sat on the mat by the hat"
        result = compute_ngram_entropy(text, n=2, ngram_type="word", chunk_size=1000)
        assert len(result.entropy_dist.values) == 1
        assert result.entropy_dist.std == 0.0


class TestComputeNgramEntropyMultipleChunks:
    """Tests for compute_ngram_entropy with text spanning multiple chunks."""

    def test_multiple_chunks(self):
        """Text larger than chunk_size produces multiple chunks."""
        # Create text with 150 words, chunk_size=50 -> 3 chunks
        words = [f"word{i % 30}" for i in range(150)]
        text = " ".join(words)
        result = compute_ngram_entropy(text, n=2, ngram_type="word", chunk_size=50)
        assert result.chunk_count == 3
        assert len(result.entropy_dist.values) == 3

    def test_multiple_chunks_distribution_stats(self):
        """Distribution stats are computed across multiple chunks."""
        words = [f"word{i % 20}" for i in range(200)]
        text = " ".join(words)
        result = compute_ngram_entropy(text, n=2, ngram_type="word", chunk_size=50)
        # With 4 chunks, we get a proper distribution
        assert result.chunk_count == 4
        assert result.entropy_dist.mean == result.entropy
        assert result.perplexity_dist.mean == result.perplexity


class TestComputeNgramEntropyEmptyText:
    """Tests for compute_ngram_entropy with empty input."""

    def test_empty_text_returns_nan(self):
        """Empty text returns NaN entropy and perplexity."""
        result = compute_ngram_entropy("", n=2, ngram_type="word", chunk_size=1000)
        assert math.isnan(result.entropy)
        assert math.isnan(result.perplexity)
        assert result.chunk_count == 1  # chunk_text returns [""] for empty

    def test_empty_text_has_warning_metadata(self):
        """Empty text result metadata contains a warning."""
        result = compute_ngram_entropy("", n=2, ngram_type="word", chunk_size=1000)
        assert "warning" in result.metadata


class TestComputeNgramEntropyPerplexityRelationship:
    """Tests that perplexity = 2^entropy."""

    def test_perplexity_is_2_to_the_entropy(self):
        """Per-chunk perplexity values equal 2^(per-chunk entropy)."""
        text = "the quick brown fox jumps over the lazy dog near the old log"
        result = compute_ngram_entropy(text, n=2, ngram_type="word", chunk_size=1000)
        for ent, perp in zip(result.entropy_dist.values, result.perplexity_dist.values):
            assert abs(perp - 2**ent) < 0.001

    def test_perplexity_relationship_character(self):
        """Perplexity = 2^entropy also holds for character n-grams."""
        text = "abcdefghijklmnopqrstuvwxyz" * 3
        result = compute_ngram_entropy(text, n=2, ngram_type="character", chunk_size=1000)
        for ent, perp in zip(result.entropy_dist.values, result.perplexity_dist.values):
            assert abs(perp - 2**ent) < 0.001


class TestComputeNgramEntropyMetadata:
    """Tests for metadata fields in compute_ngram_entropy results."""

    def test_metadata_contains_n(self):
        """Metadata includes the n-gram size."""
        result = compute_ngram_entropy("one two three four five", n=3, ngram_type="word", chunk_size=1000)
        assert result.metadata["n"] == 3

    def test_metadata_contains_ngram_type(self):
        """Metadata includes the n-gram type."""
        result = compute_ngram_entropy("some text here now", n=2, ngram_type="character", chunk_size=1000)
        assert result.metadata["ngram_type"] == "character"

    def test_ngram_type_label_format(self):
        """The ngram_type field follows the pattern '<type>_<n>gram'."""
        result = compute_ngram_entropy("some text here now", n=2, ngram_type="word", chunk_size=1000)
        assert result.ngram_type == "word_2gram"

    def test_ngram_type_label_trigram(self):
        """Trigram label is correct."""
        result = compute_ngram_entropy("a b c d e f g h", n=3, ngram_type="word", chunk_size=1000)
        assert result.ngram_type == "word_3gram"

    def test_metadata_total_counts(self):
        """Metadata includes total item, unique n-gram, and total n-gram counts."""
        result = compute_ngram_entropy("hello world foo bar", n=2, ngram_type="word", chunk_size=1000)
        assert "total_item_count" in result.metadata
        assert "total_unique_ngrams" in result.metadata
        assert "total_ngrams" in result.metadata
        assert result.metadata["total_item_count"] > 0


# =============================================================================
# CHARACTER VS WORD BIGRAMS
# =============================================================================


class TestCharacterVsWordBigrams:
    """Tests that character and word bigrams give different results on the same text."""

    def test_different_entropy_values(self):
        """Character and word bigrams yield different entropy for the same text."""
        text = "the quick brown fox jumped over the lazy dog"
        char_result = compute_ngram_entropy(text, n=2, ngram_type="character", chunk_size=1000)
        word_result = compute_ngram_entropy(text, n=2, ngram_type="word", chunk_size=1000)
        assert char_result.entropy != word_result.entropy

    def test_different_ngram_type_labels(self):
        """Character and word results have distinct ngram_type labels."""
        text = "some sample text for testing"
        char_result = compute_ngram_entropy(text, n=2, ngram_type="character", chunk_size=1000)
        word_result = compute_ngram_entropy(text, n=2, ngram_type="word", chunk_size=1000)
        assert char_result.ngram_type == "character_2gram"
        assert word_result.ngram_type == "word_2gram"


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


class TestComputeCharacterBigramEntropy:
    """Tests for the compute_character_bigram_entropy convenience function."""

    def test_returns_character_bigram_result(self):
        """Convenience function returns a character bigram result."""
        text = "abcdefghijklmnopqrstuvwxyz"
        result = compute_character_bigram_entropy(text)
        assert result.ngram_type == "character_2gram"
        assert result.metadata["n"] == 2
        assert result.metadata["ngram_type"] == "character"

    def test_matches_direct_call(self):
        """Convenience function matches calling compute_ngram_entropy directly."""
        text = "the quick brown fox jumps over the lazy dog near the old mill"
        direct = compute_ngram_entropy(text, n=2, ngram_type="character", chunk_size=1000)
        convenience = compute_character_bigram_entropy(text, chunk_size=1000)
        assert direct.entropy == convenience.entropy
        assert direct.perplexity == convenience.perplexity
        assert direct.ngram_type == convenience.ngram_type

    def test_custom_chunk_size(self):
        """Convenience function respects custom chunk_size."""
        words = [f"word{i}" for i in range(100)]
        text = " ".join(words)
        result = compute_character_bigram_entropy(text, chunk_size=30)
        assert result.chunk_size == 30


class TestComputeWordBigramEntropy:
    """Tests for the compute_word_bigram_entropy convenience function."""

    def test_returns_word_bigram_result(self):
        """Convenience function returns a word bigram result."""
        text = "the cat sat on the mat near the hat"
        result = compute_word_bigram_entropy(text)
        assert result.ngram_type == "word_2gram"
        assert result.metadata["n"] == 2
        assert result.metadata["ngram_type"] == "word"

    def test_matches_direct_call(self):
        """Convenience function matches calling compute_ngram_entropy directly."""
        text = "the quick brown fox jumps over the lazy dog near the old mill"
        direct = compute_ngram_entropy(text, n=2, ngram_type="word", chunk_size=1000)
        convenience = compute_word_bigram_entropy(text, chunk_size=1000)
        assert direct.entropy == convenience.entropy
        assert direct.perplexity == convenience.perplexity


# =============================================================================
# EDGE CASES
# =============================================================================


class TestEdgeCases:
    """Edge-case tests for robustness."""

    def test_single_word_word_bigram(self):
        """Single word cannot form a word bigram -> NaN result."""
        result = compute_ngram_entropy("hello", n=2, ngram_type="word", chunk_size=1000)
        assert math.isnan(result.entropy)
        assert math.isnan(result.perplexity)

    def test_single_character_char_bigram(self):
        """Single character cannot form a character bigram -> NaN result."""
        result = compute_ngram_entropy("x", n=2, ngram_type="character", chunk_size=1000)
        assert math.isnan(result.entropy)

    def test_text_shorter_than_chunk_size(self):
        """Text shorter than chunk_size produces exactly one chunk."""
        text = "a short sentence"
        result = compute_ngram_entropy(text, n=2, ngram_type="word", chunk_size=1000)
        assert result.chunk_count == 1

    def test_very_long_text(self):
        """Very long text still produces a valid result with many chunks."""
        # 5000 words -> at chunk_size=500, that is 10 chunks
        words = [f"token{i % 100}" for i in range(5000)]
        text = " ".join(words)
        result = compute_ngram_entropy(text, n=2, ngram_type="word", chunk_size=500)
        assert result.chunk_count == 10
        assert len(result.entropy_dist.values) == 10
        assert not math.isnan(result.entropy)

    def test_whitespace_only(self):
        """Whitespace-only text has no tokens -> NaN result."""
        result = compute_ngram_entropy("     ", n=2, ngram_type="word", chunk_size=1000)
        assert math.isnan(result.entropy)

    def test_chunk_size_one(self):
        """chunk_size=1 means each word becomes its own chunk."""
        text = "alpha beta gamma delta epsilon"
        result = compute_ngram_entropy(text, n=2, ngram_type="word", chunk_size=1)
        # Each chunk is a single word, which cannot form a word bigram
        # All chunks should produce NaN -> overall NaN
        assert math.isnan(result.entropy)


# =============================================================================
# MATHEMATICAL PROPERTIES
# =============================================================================


class TestMathematicalProperties:
    """Tests for mathematical invariants of entropy and perplexity."""

    def test_entropy_non_negative(self):
        """Entropy is always >= 0 for any valid input."""
        texts = [
            "the cat sat on the mat",
            "aaaa bbbb cccc",
            "x y z x y z x y z",
        ]
        for text in texts:
            result = compute_ngram_entropy(text, n=2, ngram_type="word", chunk_size=1000)
            if not math.isnan(result.entropy):
                assert result.entropy >= 0

    def test_perplexity_at_least_one(self):
        """Perplexity is always >= 1 for valid input (since entropy >= 0)."""
        text = "the quick brown fox jumps over the lazy dog"
        result = compute_ngram_entropy(text, n=2, ngram_type="word", chunk_size=1000)
        assert result.perplexity >= 1.0

    def test_zero_entropy_gives_perplexity_one(self):
        """Zero entropy -> perplexity of exactly 1."""
        # "go go go" -> only one unique bigram ("go", "go") -> entropy = 0
        text = "go go go go"
        result = compute_ngram_entropy(text, n=2, ngram_type="word", chunk_size=1000)
        assert result.entropy == 0.0
        assert result.perplexity == 1.0

    def test_higher_diversity_higher_entropy(self):
        """More diverse text produces higher entropy than repetitive text."""
        repetitive = "the the the the the the the the the the"
        diverse = "the quick brown fox jumps over a lazy old dog"
        rep_result = compute_ngram_entropy(repetitive, n=2, ngram_type="word", chunk_size=1000)
        div_result = compute_ngram_entropy(diverse, n=2, ngram_type="word", chunk_size=1000)
        assert div_result.entropy > rep_result.entropy

    def test_uniform_distribution_maximum_entropy(self):
        """Uniform distribution over k outcomes yields entropy = log2(k)."""
        # "abcde" produces 4 unique, equally frequent bigrams
        text = "abcde"
        entropy, perplexity, meta = _compute_ngram_entropy_single(text, n=2, ngram_type="character")
        k = meta["unique_ngrams"]  # should be 4
        expected = math.log2(k)
        assert abs(entropy - expected) < 0.001

    def test_entropy_bounded_by_log2_of_unique_ngrams(self):
        """Entropy never exceeds log2(number of unique n-grams)."""
        text = "the cat sat on the mat near the hat on the flat"
        entropy, perplexity, meta = _compute_ngram_entropy_single(text, n=2, ngram_type="word")
        upper_bound = math.log2(meta["unique_ngrams"])
        assert entropy <= upper_bound + 0.001  # small tolerance for float math
