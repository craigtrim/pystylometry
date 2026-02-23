"""Shared utility functions for pystylometry."""

from __future__ import annotations

import statistics

from .tokenizer import Tokenizer

# ===== Convenience Functions =====

# Default tokenizer instance for backward compatibility
# Preserves emails and URLs to allow readability metrics (like Coleman-Liau)
# to count their alphabetic characters
_default_tokenizer = Tokenizer(
    lowercase=False,
    strip_punctuation=False,
    preserve_urls=True,
    preserve_emails=True,
)


def tokenize(text: str) -> list[str]:
    """
    Simple tokenization using default settings.

    Convenience function that maintains backward compatibility
    with the original simple tokenizer interface.

    Args:
        text: Input text to tokenize

    Returns:
        List of tokens

    Example:
        >>> tokens = tokenize("Hello, world!")
        >>> print(tokens)
        ['Hello', ',', 'world', '!']
    """
    return _default_tokenizer.tokenize(text)


def advanced_tokenize(
    text: str,
    lowercase: bool = True,
    strip_punctuation: bool = True,
    expand_contractions: bool = False,
) -> list[str]:
    """
    Tokenization with commonly-used advanced options.

    Args:
        text: Input text to tokenize
        lowercase: Convert to lowercase (default: True)
        strip_punctuation: Remove punctuation tokens (default: True)
        expand_contractions: Expand contractions (default: False)

    Returns:
        List of tokens

    Example:
        >>> tokens = advanced_tokenize("Hello, world! It's nice.", lowercase=True)
        >>> print(tokens)
        ['hello', 'world', "it's", 'nice']
    """
    tokenizer = Tokenizer(
        lowercase=lowercase,
        strip_punctuation=strip_punctuation,
        expand_contractions=expand_contractions,
    )
    return tokenizer.tokenize(text)


# ===== Sentence Splitting =====

# Related GitHub Issue:
#     #69 - Replace custom regex sentence segmentation with fast-sentence-segment
#     https://github.com/craigtrim/pystylometry/issues/69
#     #68 - Replace spaCy with built-in utilities
#     https://github.com/craigtrim/pystylometry/issues/68
try:
    from fast_sentence_segment import segment
except ImportError:
    raise ImportError(
        "The 'fast-sentence-segment' library is required for sentence segmentation. "
        "Install it with: pip install pystylometry"
    )


def split_sentences(text: str) -> list[str]:
    """Split text into sentences using fast-sentence-segment.

    Uses the fast-sentence-segment library for accurate, reliable
    sentence boundary detection. Handles abbreviations, edge cases,
    and complex punctuation patterns automatically using spaCy's
    sentence segmentation engine with English-specific rules.

    This replaces the previous custom regex implementation (Issue #69)
    which had issues with mid-sentence splits, fragment detection, and
    inconsistent segmentation.

    Related GitHub Issue:
        #69 - Replace custom regex with fast-sentence-segment
        https://github.com/craigtrim/pystylometry/issues/69
        #68 - Replace spaCy with built-in utilities
        https://github.com/craigtrim/pystylometry/issues/68

    Args:
        text: Input text to split

    Returns:
        List of sentences

    Example:
        >>> sentences = split_sentences("Dr. Smith arrived. He was happy.")
        >>> print(sentences)
        ['Dr. Smith arrived.', 'He was happy.']

    Note:
        Requires spaCy's English model (en_core_web_sm) to be installed.
        Run: python -m spacy download en_core_web_sm

    References:
        fast-sentence-segment: https://pypi.org/project/fast-sentence-segment/
    """
    if not text or not text.strip():
        return []

    # Use fast-sentence-segment for accurate sentence boundary detection
    #
    # Related GitHub Issue:
    #     #69 - Replaces 70+ lines of custom regex with battle-tested library
    #     https://github.com/craigtrim/pystylometry/issues/69
    #
    # Note: segment() returns list of paragraphs (each paragraph is a list of sentences)
    # We flatten this to return a simple list of all sentences
    paragraphs = segment(text)
    return [sentence for paragraph in paragraphs for sentence in paragraph]


def split_paragraphs(text: str) -> list[list[str]]:
    """Split text into paragraphs, each containing a list of sentences.

    Returns the native paragraph-structured output of ``fast-sentence-segment``
    without flattening. Each outer list element is a paragraph; each inner list
    contains the sentences in that paragraph.

    This is the paragraph-aware counterpart to ``split_sentences()``, which
    flattens the same output into a single sentence list. Use this function
    when paragraph boundaries are needed — e.g., for mic drop detection,
    stacked paragraph detection, or any metric that operates at the paragraph
    level rather than the document level.

    Related GitHub Issues:
        #71 - Paragraph-Level Segmentation
        https://github.com/craigtrim/pystylometry/issues/71
        #69 - AI Stylistic Tell Detection (parent feature)
        https://github.com/craigtrim/pystylometry/issues/69

    Args:
        text: Input text to segment.

    Returns:
        list[list[str]]: Each outer element is a paragraph (list of sentences).
        Returns an empty list for empty or whitespace-only input.

    Example:
        >>> paragraphs = split_paragraphs("First sentence. Second sentence.\\n\\nThird sentence.")
        >>> len(paragraphs)
        2
        >>> paragraphs[0]
        ['First sentence.', 'Second sentence.']
        >>> paragraphs[1]
        ['Third sentence.']

    References:
        fast-sentence-segment: https://pypi.org/project/fast-sentence-segment/
    """
    if not text or not text.strip():
        return []

    # segment() returns list[list[str]]: paragraphs → sentences
    # This is the un-flattened form; split_sentences() flattens it.
    return segment(text)


def compute_paragraph_stats(text: str) -> "ParagraphStatsResult":
    """Compute paragraph-level structural statistics for AI-tell detection.

    Analyzes text at the paragraph level to produce signals used by two
    AI stylistic tell detectors:

    **Mic Drop Detection** — ``terminal_brevity_ratio`` per paragraph.
    A paragraph whose last sentence is dramatically shorter than the mean
    (ratio < 0.5) exhibits the LLM-favoured rhetorical deceleration pattern.
    Example: three substantive sentences followed by "And that changes
    everything." The pattern is not absent in human writing, but its
    *frequency* and *consistency* across paragraphs is anomalously high
    in LLM-generated text.

    **Stacked Short Paragraph Detection** — ``single_sentence_paragraph_ratio``
    and ``short_paragraph_run_length``. LLMs disproportionately use consecutive
    one-sentence paragraphs as an emphasis technique. A run_length of 3+ or
    a ratio above ~0.4 are candidate signals.

    Both signals feed the co-occurrence scorer in Issue #75, where weak
    individual signals combine into a stronger aggregate confidence score.

    Related GitHub Issues:
        #71 - Paragraph-Level Segmentation
        https://github.com/craigtrim/pystylometry/issues/71
        #69 - AI Stylistic Tell Detection
        https://github.com/craigtrim/pystylometry/issues/69
        #75 - AI-Tell Co-occurrence Scorer
        https://github.com/craigtrim/pystylometry/issues/75

    Args:
        text: Input text to analyse.

    Returns:
        ParagraphStatsResult with all paragraph-level metrics.
        Returns a zeroed result for empty or single-paragraph input.

    Example:
        >>> result = compute_paragraph_stats("Short para.\\n\\nLonger paragraph here. Two sentences. Then a mic drop.")
        >>> result.paragraph_count
        2
        >>> result.single_sentence_paragraph_ratio
        0.5

    References:
        Johnston, C. (2024). AI stylistic tell detection via co-occurrence
            of tricolon, mic drop, and stacked paragraph patterns.
    """
    from ._types import ParagraphStatsResult

    paragraphs = split_paragraphs(text)

    if not paragraphs:
        return ParagraphStatsResult(
            paragraph_count=0,
            sentences_per_paragraph=[],
            words_per_paragraph=[],
            mean_sentences_per_paragraph=0.0,
            std_sentences_per_paragraph=0.0,
            mean_words_per_paragraph=0.0,
            std_words_per_paragraph=0.0,
            single_sentence_paragraph_ratio=0.0,
            short_paragraph_run_length=0,
            terminal_brevity_ratios=[],
            metadata={"paragraph_count": 0},
        )

    sentences_per_paragraph = [len(para) for para in paragraphs]
    words_per_paragraph = [
        sum(len(tokenize(sentence)) for sentence in para) for para in paragraphs
    ]

    mean_spp = statistics.mean(sentences_per_paragraph)
    std_spp = statistics.stdev(sentences_per_paragraph) if len(paragraphs) > 1 else 0.0

    mean_wpp = statistics.mean(words_per_paragraph)
    std_wpp = statistics.stdev(words_per_paragraph) if len(paragraphs) > 1 else 0.0

    # Single-sentence paragraph ratio — stacked paragraph signal
    single_sentence_count = sum(1 for n in sentences_per_paragraph if n == 1)
    single_sentence_ratio = single_sentence_count / len(paragraphs)

    # Longest consecutive run of single-sentence paragraphs
    max_run = current_run = 0
    for n in sentences_per_paragraph:
        if n == 1:
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 0

    # Terminal brevity ratios — mic drop signal
    # Per paragraph: last_sentence_word_count / mean_sentence_word_count
    terminal_brevity_ratios: list[float] = []
    for para in paragraphs:
        word_counts = [len(tokenize(s)) for s in para]
        if not word_counts:
            continue
        mean_wc = statistics.mean(word_counts)
        if mean_wc == 0:
            terminal_brevity_ratios.append(1.0)
        else:
            terminal_brevity_ratios.append(word_counts[-1] / mean_wc)

    return ParagraphStatsResult(
        paragraph_count=len(paragraphs),
        sentences_per_paragraph=sentences_per_paragraph,
        words_per_paragraph=words_per_paragraph,
        mean_sentences_per_paragraph=mean_spp,
        std_sentences_per_paragraph=std_spp,
        mean_words_per_paragraph=mean_wpp,
        std_words_per_paragraph=std_wpp,
        single_sentence_paragraph_ratio=single_sentence_ratio,
        short_paragraph_run_length=max_run,
        terminal_brevity_ratios=terminal_brevity_ratios,
        metadata={
            "paragraph_count": len(paragraphs),
            "single_sentence_paragraphs": single_sentence_count,
        },
    )


def check_optional_dependency(module_name: str, extra_name: str) -> bool:
    """
    Check if an optional dependency is installed.

    Args:
        module_name: Name of the module to check
        extra_name: Name of the extra in pyproject.toml

    Returns:
        True if module is available

    Raises:
        ImportError: If module is not installed with instructions
    """
    try:
        __import__(module_name)
        return True
    except ImportError:
        raise ImportError(
            f"The '{module_name}' package is required for this functionality. "
            f"Install it with: pip install pystylometry[{extra_name}]"
        )
