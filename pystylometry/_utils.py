"""Shared utility functions for pystylometry."""

from __future__ import annotations

import re

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

# Common abbreviations that shouldn't trigger sentence boundaries
_ABBREVIATIONS = {
    "mr.",
    "mrs.",
    "ms.",
    "dr.",
    "prof.",
    "sr.",
    "jr.",
    "st.",
    "vs.",
    "etc.",
    "e.g.",
    "i.e.",
    "al.",
    "fig.",
    "vol.",
    "no.",
    "inc.",
    "corp.",
    "ltd.",
    "co.",
    "ph.d.",
    "m.d.",
    "b.a.",
    "m.a.",
    "j.d.",
    "rev.",
    "gen.",
    "rep.",
    "sen.",
    "capt.",
}


def split_sentences(text: str) -> list[str]:
    """
    Split text into sentences with improved boundary detection.

    Handles common abbreviations and edge cases better than simple
    splitting on sentence-ending punctuation. Uses a two-pass approach:
    1. Protect known abbreviations from splitting
    2. Split on sentence boundaries
    3. Restore abbreviations

    Args:
        text: Input text to split

    Returns:
        List of sentences

    Example:
        >>> sentences = split_sentences("Dr. Smith arrived. He was happy.")
        >>> print(sentences)
        ['Dr. Smith arrived.', 'He was happy.']
    """
    if not text:
        return []

    # Temporarily replace abbreviations with placeholders
    protected_text = text
    replacements = {}
    for i, abbr in enumerate(_ABBREVIATIONS):
        if abbr in text.lower():
            placeholder = f"__ABBR{i}__"
            # Case-insensitive replacement
            pattern = re.compile(re.escape(abbr), re.IGNORECASE)
            matches = pattern.findall(protected_text)
            if matches:
                replacements[placeholder] = matches[0]
                protected_text = pattern.sub(placeholder, protected_text, count=1)

    # Split on sentence boundaries: period/question/exclamation + whitespace + capital letter
    # Simple pattern that avoids variable-width look-behind
    sentences = re.split(r"([.!?]+)\s+(?=[A-Z])", protected_text)

    # Reconstruct sentences (regex split includes the captured groups)
    result = []
    i = 0
    while i < len(sentences):
        if i + 1 < len(sentences) and sentences[i + 1] in (".", "!", "?", ".!", "!?", "?.", "..."):
            # Combine text with its punctuation
            sentence = sentences[i] + sentences[i + 1]
            i += 2
        else:
            sentence = sentences[i]
            i += 1

        # Restore abbreviations
        for placeholder, original in replacements.items():
            sentence = sentence.replace(placeholder, original)

        sentence = sentence.strip()
        if sentence:
            result.append(sentence)

    # Fallback: if we only got one sentence, try simpler split
    if len(result) <= 1 and text:
        sentences = re.split(r"[.!?]+\s+", text)
        result = [s.strip() for s in sentences if s.strip()]

    return result


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
