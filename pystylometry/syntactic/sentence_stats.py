"""Sentence-level statistics using spaCy."""

from .._types import SentenceStatsResult
from .._utils import check_optional_dependency, split_sentences


def compute_sentence_stats(text: str, model: str = "en_core_web_sm") -> SentenceStatsResult:
    """
    Compute sentence-level statistics using spaCy.

    Metrics computed:
    - Mean sentence length (in words)
    - Standard deviation of sentence lengths
    - Range of sentence lengths (max - min)
    - Minimum sentence length
    - Maximum sentence length
    - Total sentence count

    References:
        Hunt, K. W. (1965). Grammatical structures written at three grade levels.
        NCTE Research Report No. 3.

    Args:
        text: Input text to analyze
        model: spaCy model name (default: "en_core_web_sm")

    Returns:
        SentenceStatsResult with sentence statistics and metadata

    Raises:
        ImportError: If spaCy is not installed

    Example:
        >>> result = compute_sentence_stats("The quick brown fox. It jumps over the lazy dog.")
        >>> print(f"Mean length: {result.mean_sentence_length:.1f} words")
        >>> print(f"Std dev: {result.sentence_length_std:.1f}")
        >>> print(f"Sentence count: {result.sentence_count}")
    """
    check_optional_dependency("spacy", "syntactic")

    # TODO: Implement spaCy-based sentence analysis
    # import spacy
    # nlp = spacy.load(model)
    # doc = nlp(text)
    # sentences = list(doc.sents)

    # For now, use simple fallback
    sentences = split_sentences(text)

    return SentenceStatsResult(
        mean_sentence_length=0.0,
        sentence_length_std=0.0,
        sentence_length_range=0,
        min_sentence_length=0,
        max_sentence_length=0,
        sentence_count=len(sentences),
        metadata={
            "model": model,
        }
    )
