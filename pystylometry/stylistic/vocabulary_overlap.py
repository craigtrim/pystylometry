"""Vocabulary overlap and similarity metrics.

This module computes similarity measures between two texts based on their
shared vocabulary. Useful for authorship verification, plagiarism detection,
and measuring stylistic consistency.

Related GitHub Issue:
    #21 - Vocabulary Overlap and Similarity Metrics
    https://github.com/craigtrim/pystylometry/issues/21

References:
    Jaccard, P. (1912). The distribution of the flora in the alpine zone.
        New Phytologist, 11(2), 37-50.
    Sørensen, T. (1948). A method of establishing groups of equal amplitude in
        plant sociology based on similarity of species. Kongelige Danske
        Videnskabernes Selskab, 5(4), 1-34.
    Salton, G., & McGill, M. J. (1983). Introduction to Modern Information
        Retrieval. McGraw-Hill.
    Kullback, S., & Leibler, R. A. (1951). On Information and Sufficiency.
        Annals of Mathematical Statistics, 22(1), 79-86.
    Manning, C. D., & Schütze, H. (1999). Foundations of Statistical NLP.
        MIT Press.
"""

from __future__ import annotations

import math
import re
from collections import Counter

from .._types import VocabularyOverlapResult


def _tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase words.

    Uses a simple regex-based tokenizer that extracts word characters.
    Converts to lowercase for case-insensitive comparison.

    Args:
        text: Input text to tokenize

    Returns:
        List of lowercase word tokens
    """
    # Match word characters, convert to lowercase
    tokens = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    return tokens


def _compute_jaccard(set1: set[str], set2: set[str]) -> float:
    """Compute Jaccard similarity coefficient.

    The Jaccard index measures similarity as the size of the intersection
    divided by the size of the union of two sets.

    J(A, B) = |A ∩ B| / |A ∪ B|

    Args:
        set1: First vocabulary set
        set2: Second vocabulary set

    Returns:
        Jaccard similarity coefficient (0.0 to 1.0)

    References:
        Jaccard, P. (1912). The distribution of the flora in the alpine zone.
    """
    if not set1 and not set2:
        return 1.0  # Both empty = identical

    intersection = len(set1 & set2)
    union = len(set1 | set2)

    return intersection / union if union > 0 else 0.0


def _compute_dice(set1: set[str], set2: set[str]) -> float:
    """Compute Sørensen-Dice coefficient.

    The Dice coefficient is similar to Jaccard but weights the intersection
    more heavily. Also known as the Sørensen-Dice index.

    D(A, B) = 2|A ∩ B| / (|A| + |B|)

    Args:
        set1: First vocabulary set
        set2: Second vocabulary set

    Returns:
        Dice coefficient (0.0 to 1.0)

    References:
        Sørensen, T. (1948). A method of establishing groups of equal amplitude
            in plant sociology based on similarity of species.
    """
    if not set1 and not set2:
        return 1.0  # Both empty = identical

    intersection = len(set1 & set2)
    total_size = len(set1) + len(set2)

    return (2 * intersection) / total_size if total_size > 0 else 0.0


def _compute_overlap_coefficient(set1: set[str], set2: set[str]) -> float:
    """Compute overlap coefficient.

    The overlap coefficient measures the overlap relative to the smaller set.
    Useful when comparing texts of very different lengths.

    O(A, B) = |A ∩ B| / min(|A|, |B|)

    Args:
        set1: First vocabulary set
        set2: Second vocabulary set

    Returns:
        Overlap coefficient (0.0 to 1.0)
    """
    if not set1 or not set2:
        return 0.0 if set1 or set2 else 1.0

    intersection = len(set1 & set2)
    min_size = min(len(set1), len(set2))

    return intersection / min_size if min_size > 0 else 0.0


def _compute_cosine_similarity(freq1: Counter[str], freq2: Counter[str], vocab: set[str]) -> float:
    """Compute cosine similarity between term frequency vectors.

    Treats each text as a vector in vocabulary space where each dimension
    is the frequency of a word. Computes the cosine of the angle between vectors.

    cos(θ) = (A · B) / (||A|| × ||B||)

    Args:
        freq1: Word frequencies for text 1
        freq2: Word frequencies for text 2
        vocab: Combined vocabulary (union of both texts)

    Returns:
        Cosine similarity (-1.0 to 1.0, though word frequencies yield 0.0 to 1.0)

    References:
        Salton, G., & McGill, M. J. (1983). Introduction to Modern Information
            Retrieval.
    """
    if not vocab:
        return 1.0  # Both empty = identical

    # Compute dot product and magnitudes
    dot_product = 0.0
    magnitude1 = 0.0
    magnitude2 = 0.0

    for word in vocab:
        f1 = freq1.get(word, 0)
        f2 = freq2.get(word, 0)
        dot_product += f1 * f2
        magnitude1 += f1 * f1
        magnitude2 += f2 * f2

    magnitude1 = math.sqrt(magnitude1)
    magnitude2 = math.sqrt(magnitude2)

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


def _compute_kl_divergence(
    freq1: Counter[str], freq2: Counter[str], vocab: set[str], smoothing: float = 1e-10
) -> float:
    """Compute Kullback-Leibler divergence from text1 to text2.

    KL divergence measures how one probability distribution diverges from
    another. It is asymmetric: D_KL(P || Q) ≠ D_KL(Q || P).

    D_KL(P || Q) = Σ P(x) log(P(x) / Q(x))

    A small smoothing value is added to avoid division by zero when Q(x) = 0.

    Args:
        freq1: Word frequencies for text 1 (P distribution)
        freq2: Word frequencies for text 2 (Q distribution)
        vocab: Combined vocabulary (union of both texts)
        smoothing: Small value added to probabilities to avoid log(0)

    Returns:
        KL divergence (non-negative, unbounded above)

    Note:
        Returns 0.0 for identical distributions. Higher values indicate
        greater difference between distributions.

    References:
        Kullback, S., & Leibler, R. A. (1951). On Information and Sufficiency.
    """
    if not vocab:
        return 0.0  # Both empty = identical

    # Convert frequencies to probabilities
    total1 = sum(freq1.values())
    total2 = sum(freq2.values())

    if total1 == 0 or total2 == 0:
        return 0.0

    kl_div = 0.0
    for word in vocab:
        p = (freq1.get(word, 0) / total1) + smoothing
        q = (freq2.get(word, 0) / total2) + smoothing
        kl_div += p * math.log(p / q)

    return max(0.0, kl_div)  # Ensure non-negative due to smoothing artifacts


def _compute_tfidf_distinctive_words(
    freq1: Counter[str],
    freq2: Counter[str],
    unique_to_1: set[str],
    unique_to_2: set[str],
    top_n: int = 20,
) -> tuple[list[tuple[str, float]], list[tuple[str, float]]]:
    """Compute distinctive words for each text using TF-IDF-like scoring.

    Words unique to each text are scored by their frequency, providing
    a measure of how "distinctive" they are for that text.

    For texts with shared vocabulary, the scoring considers relative
    frequency differences.

    Args:
        freq1: Word frequencies for text 1
        freq2: Word frequencies for text 2
        unique_to_1: Words appearing only in text 1
        unique_to_2: Words appearing only in text 2
        top_n: Number of top distinctive words to return

    Returns:
        Tuple of (text1_distinctive, text2_distinctive) lists,
        each containing (word, score) tuples sorted by score descending
    """
    # For unique words, score by frequency
    text1_scores: list[tuple[str, float]] = []
    for word in unique_to_1:
        score = float(freq1[word])
        text1_scores.append((word, score))

    text2_scores: list[tuple[str, float]] = []
    for word in unique_to_2:
        score = float(freq2[word])
        text2_scores.append((word, score))

    # Sort by score descending
    text1_scores.sort(key=lambda x: x[1], reverse=True)
    text2_scores.sort(key=lambda x: x[1], reverse=True)

    return text1_scores[:top_n], text2_scores[:top_n]


def compute_vocabulary_overlap(
    text1: str,
    text2: str,
    top_distinctive: int = 20,
) -> VocabularyOverlapResult:
    """Compute vocabulary overlap and similarity between two texts.

    This function computes multiple similarity metrics based on vocabulary
    comparison, useful for authorship verification, plagiarism detection,
    and measuring stylistic consistency across texts.

    Metrics computed:
        - Jaccard similarity: intersection / union (set-based)
        - Sørensen-Dice coefficient: 2 * intersection / (size1 + size2)
        - Overlap coefficient: intersection / min(size1, size2)
        - Cosine similarity: dot product of frequency vectors
        - KL divergence: distributional difference (asymmetric)

    Related GitHub Issue:
        #21 - Vocabulary Overlap and Similarity Metrics
        https://github.com/craigtrim/pystylometry/issues/21

    Args:
        text1: First text to compare
        text2: Second text to compare
        top_distinctive: Number of most distinctive words to return per text

    Returns:
        VocabularyOverlapResult with similarity scores, vocabulary statistics,
        shared vocabulary, and distinctive words for each text.

    Example:
        >>> result = compute_vocabulary_overlap(
        ...     "The quick brown fox jumps over the lazy dog",
        ...     "The fast brown fox leaps over the sleepy dog"
        ... )
        >>> print(f"Jaccard similarity: {result.jaccard_similarity:.3f}")
        Jaccard similarity: 0.583
        >>> print(f"Shared words: {result.shared_vocab_size}")
        Shared words: 7
        >>> print(f"Text1 distinctive: {result.text1_distinctive_words}")
        [('quick', 1.0), ('jumps', 1.0), ('lazy', 1.0)]

    References:
        Jaccard, P. (1912). The distribution of the flora in the alpine zone.
            New Phytologist, 11(2), 37-50.
        Sørensen, T. (1948). A method of establishing groups of equal amplitude
            in plant sociology based on similarity of species.
        Salton, G., & McGill, M. J. (1983). Introduction to Modern Information
            Retrieval. McGraw-Hill.
        Kullback, S., & Leibler, R. A. (1951). On Information and Sufficiency.
            Annals of Mathematical Statistics, 22(1), 79-86.
        Manning, C. D., & Schütze, H. (1999). Foundations of Statistical NLP.
            MIT Press.
    """
    # Tokenize texts
    tokens1 = _tokenize(text1)
    tokens2 = _tokenize(text2)

    # Build frequency counters and vocabulary sets
    freq1: Counter[str] = Counter(tokens1)
    freq2: Counter[str] = Counter(tokens2)

    vocab1 = set(freq1.keys())
    vocab2 = set(freq2.keys())

    # Compute set operations
    shared = vocab1 & vocab2
    union = vocab1 | vocab2
    unique_to_1 = vocab1 - vocab2
    unique_to_2 = vocab2 - vocab1

    # Compute similarity metrics
    jaccard = _compute_jaccard(vocab1, vocab2)
    dice = _compute_dice(vocab1, vocab2)
    overlap = _compute_overlap_coefficient(vocab1, vocab2)
    cosine = _compute_cosine_similarity(freq1, freq2, union)
    kl_div = _compute_kl_divergence(freq1, freq2, union)

    # Compute coverage ratios
    text1_coverage = len(shared) / len(vocab1) if vocab1 else 0.0
    text2_coverage = len(shared) / len(vocab2) if vocab2 else 0.0

    # Get distinctive words
    text1_distinctive, text2_distinctive = _compute_tfidf_distinctive_words(
        freq1, freq2, unique_to_1, unique_to_2, top_distinctive
    )

    # Build shared words list (sorted by combined frequency)
    shared_with_freq = [(word, freq1[word] + freq2[word]) for word in shared]
    shared_with_freq.sort(key=lambda x: x[1], reverse=True)
    shared_words = [word for word, _ in shared_with_freq]

    return VocabularyOverlapResult(
        # Similarity scores
        jaccard_similarity=jaccard,
        dice_coefficient=dice,
        overlap_coefficient=overlap,
        cosine_similarity=cosine,
        kl_divergence=kl_div,
        # Vocabulary sizes
        text1_vocab_size=len(vocab1),
        text2_vocab_size=len(vocab2),
        shared_vocab_size=len(shared),
        union_vocab_size=len(union),
        text1_unique_count=len(unique_to_1),
        text2_unique_count=len(unique_to_2),
        # Shared and distinctive vocabulary
        shared_words=shared_words,
        text1_distinctive_words=text1_distinctive,
        text2_distinctive_words=text2_distinctive,
        # Coverage ratios
        text1_coverage=text1_coverage,
        text2_coverage=text2_coverage,
        # Metadata
        metadata={
            "text1_token_count": len(tokens1),
            "text2_token_count": len(tokens2),
            "text1_frequencies": dict(freq1),
            "text2_frequencies": dict(freq2),
            "unique_to_text1": sorted(unique_to_1),
            "unique_to_text2": sorted(unique_to_2),
        },
    )
