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
