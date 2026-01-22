"""N-gram entropy and perplexity calculations."""

from typing import List
from collections import Counter
import math
from .._types import EntropyResult
from .._utils import tokenize


def compute_ngram_entropy(
    text: str,
    n: int = 2,
    ngram_type: str = "word"
) -> EntropyResult:
    """
    Compute n-gram entropy and perplexity for text.

    Entropy measures the unpredictability of the next item in a sequence.
    Higher entropy = more unpredictable = more diverse/complex text.

    Formula:
        H(X) = -Σ p(x) × log₂(p(x))
        Perplexity = 2^H(X)

    Where p(x) is the probability of n-gram x occurring.

    References:
        Shannon, C. E. (1948). A mathematical theory of communication.
        Bell System Technical Journal, 27(3), 379-423.

        Manning, C. D., & Schütze, H. (1999). Foundations of Statistical
        Natural Language Processing. MIT Press.

    Args:
        text: Input text to analyze
        n: N-gram size (2 for bigrams, 3 for trigrams, etc.)
        ngram_type: "word" or "character" (default: "word")

    Returns:
        EntropyResult with entropy, perplexity, and metadata

    Example:
        >>> result = compute_ngram_entropy("The quick brown fox jumps", n=2, ngram_type="word")
        >>> print(f"Bigram entropy: {result.entropy:.3f}")
        >>> print(f"Perplexity: {result.perplexity:.3f}")
    """
    # Generate n-grams
    if ngram_type == "character":
        items = list(text)
    else:  # word
        items = tokenize(text)

    if len(items) < n:
        return EntropyResult(
            entropy=0.0,
            perplexity=1.0,
            ngram_type=f"{ngram_type}_{n}gram",
            metadata={
                "n": n,
                "ngram_type": ngram_type,
                "item_count": len(items),
                "warning": "Text too short for n-gram analysis"
            }
        )

    # Create n-grams using sliding window
    ngram_list = []
    for i in range(len(items) - n + 1):
        ngram = tuple(items[i:i + n])
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
    perplexity = 2 ** entropy

    return EntropyResult(
        entropy=entropy,
        perplexity=perplexity,
        ngram_type=f"{ngram_type}_{n}gram",
        metadata={
            "n": n,
            "ngram_type": ngram_type,
            "item_count": len(items),
            "unique_ngrams": len(ngram_counts),
            "total_ngrams": total_ngrams,
        }
    )


def compute_character_bigram_entropy(text: str) -> EntropyResult:
    """
    Compute character bigram entropy.

    Convenience function that calls compute_ngram_entropy with n=2, ngram_type="character".

    Args:
        text: Input text to analyze

    Returns:
        EntropyResult with character bigram entropy and perplexity

    Example:
        >>> result = compute_character_bigram_entropy("The quick brown fox")
        >>> print(f"Character bigram entropy: {result.entropy:.3f}")
    """
    return compute_ngram_entropy(text, n=2, ngram_type="character")


def compute_word_bigram_entropy(text: str) -> EntropyResult:
    """
    Compute word bigram entropy.

    Convenience function that calls compute_ngram_entropy with n=2, ngram_type="word".

    Args:
        text: Input text to analyze

    Returns:
        EntropyResult with word bigram entropy and perplexity

    Example:
        >>> result = compute_word_bigram_entropy("The quick brown fox jumps")
        >>> print(f"Word bigram entropy: {result.entropy:.3f}")
    """
    return compute_ngram_entropy(text, n=2, ngram_type="word")
