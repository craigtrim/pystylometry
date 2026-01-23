"""Advanced tokenizer for stylometric analysis."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Iterator

# ===== Unicode Normalization Tables =====

# Single-character replacements (fast lookup with str.maketrans)
_UNICODE_REPLACEMENTS = str.maketrans(
    {
        # Smart quotes
        "\u2018": "'",  # Left single quote
        "\u2019": "'",  # Right single quote
        "\u201a": "'",  # Single low-9 quote
        "\u201b": "'",  # Single high-reversed-9 quote
        "\u201c": '"',  # Left double quote
        "\u201d": '"',  # Right double quote
        "\u201e": '"',  # Double low-9 quote
        "\u201f": '"',  # Double high-reversed-9 quote
        # Dashes
        "\u2013": "-",  # En dash
        "\u2014": "-",  # Em dash
        "\u2015": "-",  # Horizontal bar
        "\u2212": "-",  # Minus sign
        # Spaces
        "\u00a0": " ",  # Non-breaking space
        "\u2002": " ",  # En space
        "\u2003": " ",  # Em space
        "\u2009": " ",  # Thin space
        "\u200a": " ",  # Hair space
        # Apostrophes and primes
        "\u02bc": "'",  # Modifier letter apostrophe
        "\u2032": "'",  # Prime
        "\u2033": '"',  # Double prime
        # Ellipsis
        "\u2026": "...",  # Horizontal ellipsis
        # Ligatures (decompose)
        "\ufb01": "fi",
        "\ufb02": "fl",
        "\ufb03": "ffi",
        "\ufb04": "ffl",
        "\u00e6": "ae",  # æ
        "\u00c6": "AE",  # Æ
        "\u0153": "oe",  # œ
        "\u0152": "OE",  # Œ
        # Mathematical operators
        "\u00d7": "x",  # Multiplication sign
        "\u00f7": "/",  # Division sign
        "\u00b1": "+/-",  # Plus-minus
        # Currency (normalize for analysis)
        "\u00a3": "GBP",  # Pound
        "\u00a5": "JPY",  # Yen
        "\u20ac": "EUR",  # Euro
        # Fractions
        "\u00bc": "1/4",
        "\u00bd": "1/2",
        "\u00be": "3/4",
        "\u2153": "1/3",
        "\u2154": "2/3",
    }
)

# Multi-character patterns (regex-based)
_MULTI_CHAR_PATTERNS = [
    # Multiple dashes to single dash
    (re.compile(r"[-\u2013\u2014]{2,}"), "-"),
    # Multiple dots (not ellipsis)
    (re.compile(r"\.{4,}"), "..."),
    # Zero-width characters
    (re.compile(r"[\u200b-\u200d\ufeff]"), ""),
    # Control characters except newline/tab
    (re.compile(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]"), ""),
    # Multiple spaces/tabs to single space
    (re.compile(r"[ \t]+"), " "),
    # HTML entities (common ones)
    (re.compile(r"&nbsp;"), " "),
    (re.compile(r"&quot;"), '"'),
    (re.compile(r"&apos;"), "'"),
    (re.compile(r"&amp;"), "&"),
    (re.compile(r"&lt;"), "<"),
    (re.compile(r"&gt;"), ">"),
]


# ===== Text Cleaning Patterns =====


def _remove_italics_markers(text: str) -> str:
    """Remove markdown/formatting italics markers."""
    # Remove asterisk/underscore pairs around words
    text = re.sub(r"\*([^\*]+)\*", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)
    return text


def _remove_brackets(text: str) -> str:
    """Remove bracketed content [like this] and {like this}."""
    text = re.sub(r"\[([^\]]+)\]", r"\1", text)
    text = re.sub(r"\{([^\}]+)\}", r"\1", text)
    return text


def _remove_line_break_hyphens(text: str) -> str:
    """Remove hyphens at line breaks (word-\nbreak -> wordbreak)."""
    return re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)


def _remove_page_markers(text: str) -> str:
    """Remove page numbers and headers like [Page 123] or --- Page 45 ---."""
    text = re.sub(r"\[Page\s+\d+\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"[-=]{2,}\s*Page\s+\d+\s*[-=]{2,}", "", text, flags=re.IGNORECASE)
    return text


def _normalize_whitespace(text: str) -> str:
    """Normalize all whitespace to single spaces."""
    # Collapse multiple newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Normalize spaces
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


# ===== Token Pattern =====

# Comprehensive token pattern with priority-ordered alternations
_TOKEN_PATTERN = re.compile(
    r"""
    # URLs (highest priority to avoid splitting)
    (?P<url>https?://\S+)|

    # Email addresses
    (?P<email>\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b)|

    # Hashtags and mentions (social media)
    (?P<hashtag>\#\w+)|
    (?P<mention>@\w+)|

    # Time expressions (3:45pm, 10:30:15)
    (?P<time>\d{1,2}:\d{2}(?::\d{2})?(?:[ap]m)?)|

    # Dates (ISO format: 2024-01-15)
    (?P<date>\d{4}-\d{2}-\d{2})|

    # Acronyms with periods (U.S.A., Ph.D.)
    (?P<acronym>(?:[A-Z]\.){2,})|

    # Contractions and possessives (complex patterns)
    (?P<contraction_start>
        '(?:tis|twas|twere|twould|twill|em|gainst|cause|bout|til|way)(?![a-z])
    )|
    (?P<internal_elision>
        \w+[''](?:er|re|ve|ll|d|m|s|t|clock)(?![a-z])
    )|
    (?P<hyphen_possessive>
        (?:\w+(?:-\w+)+)['']s?
    )|
    (?P<standard_contraction>
        \w+[''][a-z]{1,3}(?![a-z])
    )|
    (?P<possessive>
        \w+['']s?(?![a-z])
    )|

    # Roman numerals
    (?P<roman>\b[IVXLCDM]+\b)|

    # Ordinals (1st, 2nd, 3rd, 4th, etc.)
    (?P<ordinal>\d+(?:st|nd|rd|th))|

    # Numbers with commas and decimals ($1,234.56)
    (?P<number_currency>\$?\d{1,3}(?:,\d{3})*(?:\.\d+)?)|

    # Abbreviations (Dr., Mr., Mrs., etc.)
    (?P<abbreviation>(?:Dr|Mr|Mrs|Ms|Prof|Sr|Jr|vs|etc|e\.g|i\.e)\.)|

    # G-dropping (singin', dancin')
    (?P<g_drop>\w+in[''])|

    # Hyphenated compounds (mother-in-law, well-known)
    (?P<hyphenated>(?:\w+-)+\w+)|

    # Regular words (including internal apostrophes like "o'clock")
    (?P<word>\w+(?:[']\w+)*)|

    # Ellipsis
    (?P<ellipsis>\.{3}|…)|

    # Individual punctuation
    (?P<punct>[^\w\s])
    """,
    re.VERBOSE | re.IGNORECASE | re.UNICODE,
)


# ===== Common Abbreviations =====

_COMMON_ABBREV = {
    # Titles
    "Dr.": "Doctor",
    "Mr.": "Mister",
    "Mrs.": "Misses",
    "Ms.": "Miss",
    "Prof.": "Professor",
    "Sr.": "Senior",
    "Jr.": "Junior",
    # Latin
    "e.g.": "for example",
    "i.e.": "that is",
    "etc.": "et cetera",
    "vs.": "versus",
    # Time
    "a.m.": "AM",
    "p.m.": "PM",
}

# Contraction expansions
_CONTRACTIONS = {
    "ain't": "am not",
    "aren't": "are not",
    "can't": "cannot",
    "won't": "will not",
    "shan't": "shall not",
    "couldn't": "could not",
    "shouldn't": "should not",
    "wouldn't": "would not",
    "didn't": "did not",
    "doesn't": "does not",
    "don't": "do not",
    "hadn't": "had not",
    "hasn't": "has not",
    "haven't": "have not",
    "he'd": "he would",
    "he'll": "he will",
    "he's": "he is",
    "i'd": "I would",
    "i'll": "I will",
    "i'm": "I am",
    "i've": "I have",
    "isn't": "is not",
    "it's": "it is",
    "let's": "let us",
    "she'd": "she would",
    "she'll": "she will",
    "she's": "she is",
    "that's": "that is",
    "there's": "there is",
    "they'd": "they would",
    "they'll": "they will",
    "they're": "they are",
    "they've": "they have",
    "we'd": "we would",
    "we'll": "we will",
    "we're": "we are",
    "we've": "we have",
    "weren't": "were not",
    "what's": "what is",
    "where's": "where is",
    "who's": "who is",
    "you'd": "you would",
    "you'll": "you will",
    "you're": "you are",
    "you've": "you have",
    "'tis": "it is",
    "'twas": "it was",
    "'em": "them",
}


@dataclass
class TokenMetadata:
    """Metadata about a token."""

    token: str
    start: int
    end: int
    token_type: str  # word, url, email, number, punctuation, etc.


@dataclass
class TokenizationStats:
    """Statistics from tokenization."""

    total_tokens: int
    unique_tokens: int
    word_tokens: int
    number_tokens: int
    punctuation_tokens: int
    url_tokens: int
    email_tokens: int
    hashtag_tokens: int
    mention_tokens: int
    average_token_length: float
    min_token_length: int
    max_token_length: int


class Tokenizer:
    """
    Advanced tokenizer for stylometric analysis.

    Features:
    - Comprehensive unicode normalization
    - Text cleaning (italics, brackets, page markers)
    - Sophisticated token pattern matching
    - Configurable filtering options
    - Token metadata tracking
    - Memory-efficient iteration

    Args:
        lowercase: Convert tokens to lowercase (default: True)
        min_length: Minimum token length (default: 1)
        max_length: Maximum token length (default: None)
        strip_numbers: Remove numeric tokens (default: False)
        strip_punctuation: Remove pure punctuation tokens (default: True)
        preserve_urls: Keep URL tokens (default: False)
        preserve_emails: Keep email tokens (default: False)
        preserve_hashtags: Keep hashtag tokens (default: False)
        preserve_mentions: Keep @mention tokens (default: False)
        expand_contractions: Expand contractions to full words (default: False)
        expand_abbreviations: Expand common abbreviations (default: False)
        strip_accents: Remove accents from characters (default: False)
        normalize_unicode: Apply unicode normalization (default: True)
        clean_text: Apply text cleaning (default: True)

    Example:
        >>> tokenizer = Tokenizer(lowercase=True, strip_punctuation=True)
        >>> tokens = tokenizer.tokenize("Hello, world! It's a test.")
        >>> print(tokens)
        ['hello', 'world', "it's", 'a', 'test']

        >>> # With metadata
        >>> metadata = tokenizer.tokenize_with_metadata("Test text")
        >>> for item in metadata:
        ...     print(f"{item.token} [{item.token_type}] at {item.start}-{item.end}")
    """

    def __init__(
        self,
        lowercase: bool = True,
        min_length: int = 1,
        max_length: int | None = None,
        strip_numbers: bool = False,
        strip_punctuation: bool = True,
        preserve_urls: bool = False,
        preserve_emails: bool = False,
        preserve_hashtags: bool = False,
        preserve_mentions: bool = False,
        expand_contractions: bool = False,
        expand_abbreviations: bool = False,
        strip_accents: bool = False,
        normalize_unicode: bool = True,
        clean_text: bool = True,
    ):
        self.lowercase = lowercase
        self.min_length = min_length
        self.max_length = max_length
        self.strip_numbers = strip_numbers
        self.strip_punctuation = strip_punctuation
        self.preserve_urls = preserve_urls
        self.preserve_emails = preserve_emails
        self.preserve_hashtags = preserve_hashtags
        self.preserve_mentions = preserve_mentions
        self.expand_contractions = expand_contractions
        self.expand_abbreviations = expand_abbreviations
        self.strip_accents = strip_accents
        self.normalize_unicode = normalize_unicode
        self.clean_text = clean_text

    def _preprocess_text(self, text: str) -> str:
        """Apply unicode normalization and text cleaning."""
        if not text:
            return ""

        # Unicode normalization
        if self.normalize_unicode:
            # Apply character replacements
            text = text.translate(_UNICODE_REPLACEMENTS)

            # Apply multi-character patterns
            for pattern, replacement in _MULTI_CHAR_PATTERNS:
                text = pattern.sub(replacement, text)

        # Text cleaning
        if self.clean_text:
            text = _remove_italics_markers(text)
            text = _remove_brackets(text)
            text = _remove_line_break_hyphens(text)
            text = _remove_page_markers(text)
            text = _normalize_whitespace(text)

        # Strip accents if requested
        if self.strip_accents:
            # NFD decomposition then filter out combining marks
            text = unicodedata.normalize("NFD", text)
            text = "".join(c for c in text if unicodedata.category(c) != "Mn")

        return text

    def _expand_token(self, token: str) -> str:
        """Expand contractions and abbreviations if configured."""
        if self.expand_contractions:
            lower_token = token.lower()
            if lower_token in _CONTRACTIONS:
                expanded = _CONTRACTIONS[lower_token]
                # Preserve case for first character
                if token[0].isupper():
                    expanded = expanded.capitalize()
                return expanded

        if self.expand_abbreviations:
            if token in _COMMON_ABBREV:
                return _COMMON_ABBREV[token]

        return token

    def _should_keep_token(self, token: str, token_type: str) -> bool:
        """Determine if token should be kept based on filters."""
        # Length filters
        if len(token) < self.min_length:
            return False
        if self.max_length and len(token) > self.max_length:
            return False

        # Type-based filters
        if token_type == "url" and not self.preserve_urls:
            return False
        if token_type == "email" and not self.preserve_emails:
            return False
        if token_type == "hashtag" and not self.preserve_hashtags:
            return False
        if token_type == "mention" and not self.preserve_mentions:
            return False
        if token_type == "punct" and self.strip_punctuation:
            return False
        if self.strip_numbers and token_type in ("number_currency", "ordinal", "time", "date"):
            return False

        return True

    def tokenize(self, text: str) -> list[str]:
        """
        Tokenize text into a list of tokens.

        Args:
            text: Input text to tokenize

        Returns:
            List of tokens
        """
        return list(self.tokenize_iter(text))

    def tokenize_iter(self, text: str) -> Iterator[str]:
        """
        Tokenize text and return an iterator (memory efficient).

        Args:
            text: Input text to tokenize

        Yields:
            Individual tokens
        """
        text = self._preprocess_text(text)

        for match in _TOKEN_PATTERN.finditer(text):
            # Determine token type
            token_type = match.lastgroup or "unknown"
            token = match.group(0)

            # Expand if needed
            token = self._expand_token(token)

            # Apply case transformation
            if self.lowercase:
                token = token.lower()

            # Check filters
            if self._should_keep_token(token, token_type):
                # Handle expanded tokens (may contain spaces)
                if " " in token:
                    yield from token.split()
                else:
                    yield token

    def tokenize_with_metadata(self, text: str) -> list[TokenMetadata]:
        """
        Tokenize text and return tokens with metadata.

        Args:
            text: Input text to tokenize

        Returns:
            List of TokenMetadata objects
        """
        preprocessed = self._preprocess_text(text)
        result = []

        for match in _TOKEN_PATTERN.finditer(preprocessed):
            token_type = match.lastgroup or "unknown"
            token = match.group(0)

            # Expand if needed
            token = self._expand_token(token)

            # Apply case transformation
            if self.lowercase:
                token = token.lower()

            # Check filters
            if self._should_keep_token(token, token_type):
                result.append(
                    TokenMetadata(
                        token=token, start=match.start(), end=match.end(), token_type=token_type
                    )
                )

        return result

    def get_statistics(self, text: str) -> TokenizationStats:
        """
        Get tokenization statistics.

        Args:
            text: Input text to analyze

        Returns:
            TokenizationStats object
        """
        metadata = self.tokenize_with_metadata(text)

        if not metadata:
            return TokenizationStats(
                total_tokens=0,
                unique_tokens=0,
                word_tokens=0,
                number_tokens=0,
                punctuation_tokens=0,
                url_tokens=0,
                email_tokens=0,
                hashtag_tokens=0,
                mention_tokens=0,
                average_token_length=0.0,
                min_token_length=0,
                max_token_length=0,
            )

        tokens = [m.token for m in metadata]
        unique_tokens = set(tokens)

        # Count by type
        type_counts = {
            "word": 0,
            "number": 0,
            "punct": 0,
            "url": 0,
            "email": 0,
            "hashtag": 0,
            "mention": 0,
        }

        for item in metadata:
            if item.token_type in type_counts:
                type_counts[item.token_type] += 1
            elif item.token_type in (
                "word",
                "contraction_start",
                "internal_elision",
                "standard_contraction",
                "possessive",
                "hyphenated",
                "g_drop",
                "roman",
                "abbreviation",
            ):
                type_counts["word"] += 1
            elif item.token_type in ("number_currency", "ordinal", "time", "date", "acronym"):
                type_counts["number"] += 1

        lengths = [len(t) for t in tokens]

        return TokenizationStats(
            total_tokens=len(tokens),
            unique_tokens=len(unique_tokens),
            word_tokens=type_counts["word"],
            number_tokens=type_counts["number"],
            punctuation_tokens=type_counts["punct"],
            url_tokens=type_counts["url"],
            email_tokens=type_counts["email"],
            hashtag_tokens=type_counts["hashtag"],
            mention_tokens=type_counts["mention"],
            average_token_length=sum(lengths) / len(lengths) if lengths else 0.0,
            min_token_length=min(lengths) if lengths else 0,
            max_token_length=max(lengths) if lengths else 0,
        )
