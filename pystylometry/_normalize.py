"""Token normalization for stylometric analysis.

This module provides token filtering and normalization utilities for different
analysis scenarios. The primary use case is filtering out non-words (numbers,
URLs, emails, etc.) before passing tokens to readability metrics that rely on
syllable counting.

Design Philosophy:
-----------------
Different stylometric analyses require different normalization strategies:

1. **Readability Metrics** (Flesch, SMOG, etc.):
   - Strict filtering: only alphabetic words
   - Removes numbers, URLs, emails, punctuation
   - Prevents garbage/crashes in syllable counting

2. **Authorship Attribution**:
   - Preserve stylistic markers
   - Keep contractions, hyphens, apostrophes
   - More permissive filtering

3. **Lexical Diversity**:
   - Balance between cleanliness and vocabulary richness
   - May keep some punctuation patterns
   - Configurable based on research question

Critical Issue Addressed:
------------------------
Without normalization, readability metrics receive non-words from the tokenizer:
- count_syllables("2026") → undefined behavior (crash or garbage)
- count_syllables("test@example.com") → undefined behavior
- count_syllables("C++") → undefined behavior
- count_syllables("$99.99") → undefined behavior

This module ensures only syllabifiable words reach syllable counting functions.
"""

from __future__ import annotations

import re


def is_word_token(token: str) -> bool:
    """
    Check if a token is a valid word for readability analysis.

    A valid word token is:
    - Purely alphabetic (including accented characters)
    - May contain internal apostrophes (contractions like "don't")
    - May contain internal hyphens (compound words like "co-operate")
    - Does NOT start or end with punctuation

    Args:
        token: Token to validate

    Returns:
        True if token is a valid word

    Examples:
        >>> is_word_token("hello")
        True
        >>> is_word_token("don't")
        True
        >>> is_word_token("co-operate")
        True
        >>> is_word_token("123")
        False
        >>> is_word_token("test@example.com")
        False
        >>> is_word_token("...")
        False
    """
    if not token or len(token) == 0:
        return False

    # Must start and end with alphabetic character
    if not (token[0].isalpha() and token[-1].isalpha()):
        return False

    # Check middle characters - allow letters, apostrophes, hyphens
    for char in token:
        if not (char.isalpha() or char in ("'", "-")):
            return False

    return True


def normalize_for_readability(tokens: list[str]) -> list[str]:
    """
    Normalize tokens for readability metrics (e.g., Flesch, SMOG).

    Filters tokens to only include valid words that can have syllables counted.
    This prevents errors and garbage results from non-word tokens.

    Filtering rules:
    - Keep only alphabetic words (a-zA-Z)
    - Keep contractions with apostrophes ("don't", "we're")
    - Keep hyphenated compound words ("co-operate", "re-enter")
    - Remove pure numbers ("2026", "3.14")
    - Remove URLs ("http://example.com")
    - Remove emails ("test@example.com")
    - Remove special characters ("C++", "O'Brian" → keep, "$99.99" → remove)
    - Remove pure punctuation ("...", "—", "!!!")

    Args:
        tokens: List of tokens from tokenizer

    Returns:
        Filtered list containing only valid word tokens

    Examples:
        >>> tokens = ["The", "year", "2026", "had", "365", "days"]
        >>> normalize_for_readability(tokens)
        ['The', 'year', 'had', 'days']

        >>> tokens = ["Dr", "Smith", "works", "at", "U", ".", "S", ".", "Steel"]
        >>> normalize_for_readability(tokens)
        ['Dr', 'Smith', 'works', 'at', 'U', 'S', 'Steel']

        >>> tokens = ["Email", "test@example.com", "for", "help"]
        >>> normalize_for_readability(tokens)
        ['Email', 'for', 'help']
    """
    return [token for token in tokens if is_word_token(token)]


def normalize_for_stylometry(
    tokens: list[str],
    preserve_contractions: bool = True,
    preserve_hyphens: bool = True,
    min_length: int = 1,
) -> list[str]:
    """
    Normalize tokens for stylometric analysis (authorship attribution, etc.).

    More permissive than readability normalization. Preserves stylistic markers
    that may be relevant for authorship analysis.

    Args:
        tokens: List of tokens from tokenizer
        preserve_contractions: Keep contracted forms (default: True)
        preserve_hyphens: Keep hyphenated words (default: True)
        min_length: Minimum token length (default: 1)

    Returns:
        Filtered list of tokens suitable for stylometric analysis

    Examples:
        >>> tokens = ["don't", "re-enter", "test@example.com", "..."]
        >>> normalize_for_stylometry(tokens)
        ["don't", "re-enter"]

        >>> normalize_for_stylometry(tokens, preserve_contractions=False)
        ['re-enter']
    """
    result = []
    for token in tokens:
        # Check minimum length
        if len(token) < min_length:
            continue

        # Skip URLs and emails (not stylistically relevant)
        if "@" in token or token.startswith(("http://", "https://", "www.")):
            continue

        # Must contain at least one alphabetic character
        if not any(c.isalpha() for c in token):
            continue

        # Handle contractions and hyphenated words (including tokens with both)
        has_apostrophe = "'" in token
        has_hyphen = "-" in token

        if has_apostrophe or has_hyphen:
            # Only consider valid word tokens
            if not is_word_token(token):
                continue

            # Respect configuration flags for each stylistic feature present
            if (has_apostrophe and not preserve_contractions) or (
                has_hyphen and not preserve_hyphens
            ):
                continue

            result.append(token)
            continue

        # Default: keep if it's a valid word
        if is_word_token(token):
            result.append(token)

    return result


def clean_for_syllable_counting(text: str) -> str:
    """
    Pre-clean text before tokenization for syllable-based readability metrics.

    This is a defensive normalization layer that removes known problematic
    patterns BEFORE tokenization, reducing the burden on token filtering.

    Transformations:
    - Remove URLs
    - Remove email addresses
    - Remove currency symbols with numbers ($99, £50, €100)
    - Remove standalone numbers
    - Normalize multiple spaces

    Note: This is complementary to token-level filtering, not a replacement.
    Both layers provide defense-in-depth against garbage syllable counts.

    Args:
        text: Raw input text

    Returns:
        Cleaned text ready for tokenization

    Examples:
        >>> clean_for_syllable_counting("Visit http://example.com today!")
        'Visit  today!'

        >>> clean_for_syllable_counting("Email test@example.com for help")
        'Email  for help'

        >>> clean_for_syllable_counting("The price is $99.99 on sale")
        'The price is  on sale'
    """
    # Remove URLs (http, https, www)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"www\.\S+", "", text)

    # Remove email addresses
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "", text)

    # Remove currency patterns ($99, £50, €100, $50,000, etc.)
    text = re.sub(r"[$£€¥]\d+(?:[,.]\d+)*", "", text)

    # Remove standalone numbers (with optional decimals, commas)
    text = re.sub(r"\b\d+(?:[,.]\d+)*\b", "", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def validate_tokens_for_readability(tokens: list[str]) -> tuple[list[str], list[str]]:
    """
    Validate tokens for readability analysis and report problematic tokens.

    This is a diagnostic function useful for debugging tokenization issues.
    It separates valid word tokens from problematic non-words.

    Args:
        tokens: List of tokens to validate

    Returns:
        Tuple of (valid_tokens, invalid_tokens)

    Examples:
        >>> tokens = ["Hello", "2026", "test@example.com", "world"]
        >>> valid, invalid = validate_tokens_for_readability(tokens)
        >>> print(valid)
        ['Hello', 'world']
        >>> print(invalid)
        ['2026', 'test@example.com']
    """
    valid = []
    invalid = []

    for token in tokens:
        if is_word_token(token):
            valid.append(token)
        else:
            invalid.append(token)

    return valid, invalid
