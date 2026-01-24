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

    import spacy

    # Load spaCy model
    try:
        nlp = spacy.load(model)
    except OSError:
        raise OSError(
            f"spaCy model '{model}' not found. "
            f"Download it with: python -m spacy download {model}"
        )

    # Process text with spaCy
    doc = nlp(text)

    # Extract sentences and count words in each
    sentence_lengths = []
    for sent in doc.sents:
        # Count only alphabetic tokens (exclude punctuation)
        word_count = sum(1 for token in sent if token.is_alpha)
        if word_count > 0:  # Only include non-empty sentences
            sentence_lengths.append(word_count)

    # Handle empty text
    if len(sentence_lengths) == 0:
        return SentenceStatsResult(
            mean_sentence_length=float("nan"),
            sentence_length_std=float("nan"),
            sentence_length_range=0,
            min_sentence_length=0,
            max_sentence_length=0,
            sentence_count=0,
            metadata={
                "model": model,
            },
        )

    # Calculate statistics
    mean_length = sum(sentence_lengths) / len(sentence_lengths)

    # Standard deviation
    if len(sentence_lengths) > 1:
        variance = sum((x - mean_length) ** 2 for x in sentence_lengths) / (
            len(sentence_lengths) - 1
        )
        std_dev = variance**0.5
    else:
        std_dev = 0.0

    min_length = min(sentence_lengths)
    max_length = max(sentence_lengths)
    length_range = max_length - min_length

    return SentenceStatsResult(
        mean_sentence_length=mean_length,
        sentence_length_std=std_dev,
        sentence_length_range=length_range,
        min_sentence_length=min_length,
        max_sentence_length=max_length,
        sentence_count=len(sentence_lengths),
        metadata={
            "model": model,
            "sentence_lengths": sentence_lengths,
        },
    )
