"""Sentence-level statistics using spaCy.

Related GitHub Issue:
    #27 - Native chunked analysis with Distribution dataclass
    https://github.com/craigtrim/pystylometry/issues/27
"""

from .._types import Distribution, SentenceStatsResult, make_distribution
from .._utils import check_optional_dependency


def compute_sentence_stats(
    text: str, model: str = "en_core_web_sm", chunk_size: int = 1000
) -> SentenceStatsResult:
    """
    Compute sentence-level statistics using spaCy.

    Metrics computed:
    - Mean sentence length (in words)
    - Standard deviation of sentence lengths
    - Range of sentence lengths (max - min)
    - Minimum sentence length
    - Maximum sentence length
    - Total sentence count

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27

    References:
        Hunt, K. W. (1965). Grammatical structures written at three grade levels.
        NCTE Research Report No. 3.

    Args:
        text: Input text to analyze
        model: spaCy model name (default: "en_core_web_sm")
        chunk_size: Number of words per chunk (default: 1000).
            Note: Sentence analysis is performed on the full text for accuracy,
            so this parameter is included for API consistency but actual
            results are from a single pass.

    Returns:
        SentenceStatsResult with sentence statistics, distributions, and metadata

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
            f"spaCy model '{model}' not found. Download it with: python -m spacy download {model}"
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
        empty_dist = Distribution(
            values=[],
            mean=float("nan"),
            median=float("nan"),
            std=0.0,
            range=0.0,
            iqr=0.0,
        )
        return SentenceStatsResult(
            mean_sentence_length=float("nan"),
            sentence_length_std=float("nan"),
            sentence_length_range=0.0,
            min_sentence_length=0.0,
            max_sentence_length=0.0,
            sentence_count=0,
            mean_sentence_length_dist=empty_dist,
            sentence_length_std_dist=empty_dist,
            sentence_length_range_dist=empty_dist,
            min_sentence_length_dist=empty_dist,
            max_sentence_length_dist=empty_dist,
            chunk_size=chunk_size,
            chunk_count=0,
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

    min_length = float(min(sentence_lengths))
    max_length = float(max(sentence_lengths))
    length_range = max_length - min_length

    # Create single-value distributions (sentence analysis is done on full text)
    mean_dist = make_distribution([mean_length])
    std_dist = make_distribution([std_dev])
    range_dist = make_distribution([length_range])
    min_dist = make_distribution([min_length])
    max_dist = make_distribution([max_length])

    return SentenceStatsResult(
        mean_sentence_length=mean_length,
        sentence_length_std=std_dev,
        sentence_length_range=length_range,
        min_sentence_length=min_length,
        max_sentence_length=max_length,
        sentence_count=len(sentence_lengths),
        mean_sentence_length_dist=mean_dist,
        sentence_length_std_dist=std_dist,
        sentence_length_range_dist=range_dist,
        min_sentence_length_dist=min_dist,
        max_sentence_length_dist=max_dist,
        chunk_size=chunk_size,
        chunk_count=1,  # Single pass analysis
        metadata={
            "model": model,
            "sentence_lengths": sentence_lengths,
        },
    )
