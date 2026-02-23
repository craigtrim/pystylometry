"""Shared utility functions for pystylometry."""

from __future__ import annotations

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
