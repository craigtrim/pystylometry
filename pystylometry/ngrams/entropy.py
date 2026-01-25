"""N-gram entropy and perplexity calculations.

This module implements n-gram entropy computation with native chunked analysis
for stylometric fingerprinting.

Related GitHub Issue:
    #27 - Native chunked analysis with Distribution dataclass
    https://github.com/craigtrim/pystylometry/issues/27
"""

import math
from collections import Counter

from .._types import Distribution, EntropyResult, chunk_text, make_distribution
from .._utils import tokenize


def _compute_ngram_entropy_single(text: str, n: int, ngram_type: str) -> tuple[float, float, dict]:
    """Compute n-gram entropy for a single chunk of text.

    Returns:
        Tuple of (entropy, perplexity, metadata_dict).
        Returns (nan, nan, metadata) for empty/invalid input.
    """
    # Generate n-grams
    if ngram_type == "character":
        items = list(text)
    else:  # word
        items = tokenize(text)

    if len(items) < n:
        return (
            float("nan"),
            float("nan"),
            {
                "item_count": len(items),
                "unique_ngrams": 0,
                "total_ngrams": 0,
            },
        )

    # Create n-grams using sliding window
    ngram_list = []
    for i in range(len(items) - n + 1):
        ngram = tuple(items[i : i + n])
        ngram_list.append(ngram)

    # Count n-gram frequencies
    ngram_counts = Counter(ngram_list)
    total_ngrams = len(ngram_list)

    # Calculate entropy: H(X) = -Σ p(x) × log₂(p(x))
    entropy = 0.0
    for count in ngram_counts.values():
        probability = count / total_ngrams
        entropy -= probability * math.log2(probability)

    # Calculate perplexity: 2^H(X)
    perplexity = 2**entropy

    return (
        entropy,
        perplexity,
        {
            "item_count": len(items),
            "unique_ngrams": len(ngram_counts),
            "total_ngrams": total_ngrams,
        },
    )


def compute_ngram_entropy(
    text: str, n: int = 2, ngram_type: str = "word", chunk_size: int = 1000
) -> EntropyResult:
    """
    Compute n-gram entropy and perplexity for text.

    This function uses native chunked analysis to capture variance and patterns
    across the text, which is essential for stylometric fingerprinting.

    Entropy measures the unpredictability of the next item in a sequence.
    Higher entropy = more unpredictable = more diverse/complex text.

    Formula:
        H(X) = -Σ p(x) × log₂(p(x))
        Perplexity = 2^H(X)

    Where p(x) is the probability of n-gram x occurring.

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27

    References:
        Shannon, C. E. (1948). A mathematical theory of communication.
        Bell System Technical Journal, 27(3), 379-423.

        Manning, C. D., & Schütze, H. (1999). Foundations of Statistical
        Natural Language Processing. MIT Press.

    Args:
        text: Input text to analyze
        n: N-gram size (2 for bigrams, 3 for trigrams, etc.)
        ngram_type: "word" or "character" (default: "word")
        chunk_size: Number of words per chunk (default: 1000)

    Returns:
        EntropyResult with entropy, perplexity, distributions, and metadata

    Example:
        >>> result = compute_ngram_entropy("Long text here...", n=2, chunk_size=1000)
        >>> result.entropy  # Mean across chunks
        5.2
        >>> result.entropy_dist.std  # Variance reveals fingerprint
        0.3
    """
    # Chunk the text
    chunks = chunk_text(text, chunk_size)

    # Compute metrics per chunk
    entropy_values = []
    perplexity_values = []
    total_items = 0
    total_unique_ngrams = 0
    total_ngrams = 0

    for chunk in chunks:
        ent, perp, meta = _compute_ngram_entropy_single(chunk, n, ngram_type)
        if not math.isnan(ent):
            entropy_values.append(ent)
            perplexity_values.append(perp)
        total_items += meta.get("item_count", 0)
        total_unique_ngrams += meta.get("unique_ngrams", 0)
        total_ngrams += meta.get("total_ngrams", 0)

    # Handle empty or all-invalid chunks
    if not entropy_values:
        empty_dist = Distribution(
            values=[],
            mean=float("nan"),
            median=float("nan"),
            std=0.0,
            range=0.0,
            iqr=0.0,
        )
        return EntropyResult(
            entropy=float("nan"),
            perplexity=float("nan"),
            ngram_type=f"{ngram_type}_{n}gram",
            entropy_dist=empty_dist,
            perplexity_dist=empty_dist,
            chunk_size=chunk_size,
            chunk_count=len(chunks),
            metadata={
                "n": n,
                "ngram_type": ngram_type,
                "total_item_count": total_items,
                "warning": "Text too short for n-gram analysis",
            },
        )

    # Build distributions
    entropy_dist = make_distribution(entropy_values)
    perplexity_dist = make_distribution(perplexity_values)

    return EntropyResult(
        entropy=entropy_dist.mean,
        perplexity=perplexity_dist.mean,
        ngram_type=f"{ngram_type}_{n}gram",
        entropy_dist=entropy_dist,
        perplexity_dist=perplexity_dist,
        chunk_size=chunk_size,
        chunk_count=len(chunks),
        metadata={
            "n": n,
            "ngram_type": ngram_type,
            "total_item_count": total_items,
            "total_unique_ngrams": total_unique_ngrams,
            "total_ngrams": total_ngrams,
        },
    )


def compute_character_bigram_entropy(text: str, chunk_size: int = 1000) -> EntropyResult:
    """
    Compute character bigram entropy.

    Convenience function that calls compute_ngram_entropy with n=2, ngram_type="character".

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27

    Args:
        text: Input text to analyze
        chunk_size: Number of words per chunk (default: 1000)

    Returns:
        EntropyResult with character bigram entropy, perplexity, and distributions

    Example:
        >>> result = compute_character_bigram_entropy("Long text here...", chunk_size=1000)
        >>> result.entropy  # Mean across chunks
        3.8
    """
    return compute_ngram_entropy(text, n=2, ngram_type="character", chunk_size=chunk_size)


def compute_word_bigram_entropy(text: str, chunk_size: int = 1000) -> EntropyResult:
    """
    Compute word bigram entropy.

    Convenience function that calls compute_ngram_entropy with n=2, ngram_type="word".

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27

    Args:
        text: Input text to analyze
        chunk_size: Number of words per chunk (default: 1000)

    Returns:
        EntropyResult with word bigram entropy, perplexity, and distributions

    Example:
        >>> result = compute_word_bigram_entropy("Long text here...", chunk_size=1000)
        >>> result.entropy  # Mean across chunks
        5.2
    """
    return compute_ngram_entropy(text, n=2, ngram_type="word", chunk_size=chunk_size)
