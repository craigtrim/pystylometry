"""BNC (British National Corpus) frequency analysis for stylometric comparison.

This module computes word frequency ratios by comparing observed word frequencies
in a text against expected frequencies from the British National Corpus (BNC).
Words can be categorized as:
- Overused: appear more frequently than expected (ratio > 1)
- Underused: appear less frequently than expected (ratio < 1)
- Not in BNC: words that don't exist in the BNC corpus

Related GitHub Issue:
    #TBD - BNC frequency analysis CLI
    https://github.com/craigtrim/pystylometry/issues/TBD

References:
    British National Corpus: http://www.natcorp.ox.ac.uk/
    The BNC is a 100-million word collection of samples of written and spoken
    language from a wide range of sources, designed to represent a wide
    cross-section of British English from the late 20th century.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from typing import Literal

from .._utils import advanced_tokenize, check_optional_dependency

# Unicode apostrophe variants to normalize to ASCII apostrophe (U+0027).
# See: https://github.com/craigtrim/pystylometry/issues/45
#      https://github.com/craigtrim/pystylometry/issues/58
_APOSTROPHE_VARIANTS = (
    # Spacing clones of diacritics commonly used as quotes
    "\u0060"  # GRAVE ACCENT
    "\u00b4"  # ACUTE ACCENT
    # General punctuation — single quotation marks
    "\u2018"  # LEFT SINGLE QUOTATION MARK
    "\u2019"  # RIGHT SINGLE QUOTATION MARK
    "\u201a"  # SINGLE LOW-9 QUOTATION MARK
    "\u201b"  # SINGLE HIGH-REVERSED-9 QUOTATION MARK
    # General punctuation — prime family
    "\u2032"  # PRIME
    "\u2035"  # REVERSED PRIME
    # Single-pointing angle quotation marks (guillemets)
    # Left out: structural quote marks, not apostrophes. See Issue #58.
    # Modifier letter apostrophe / prime variants
    "\u02b9"  # MODIFIER LETTER PRIME
    "\u02bb"  # MODIFIER LETTER TURNED COMMA (Hawaiʻian ʻokina)
    "\u02bc"  # MODIFIER LETTER APOSTROPHE
    "\u02bd"  # MODIFIER LETTER REVERSED COMMA
    "\u02be"  # MODIFIER LETTER RIGHT HALF RING (Arabic hamza transliteration)
    "\u02bf"  # MODIFIER LETTER LEFT HALF RING (Arabic ʿayn transliteration)
    "\u02c8"  # MODIFIER LETTER VERTICAL LINE
    "\u02ca"  # MODIFIER LETTER ACUTE ACCENT
    "\u02cb"  # MODIFIER LETTER GRAVE ACCENT
    "\u02dd"  # DOUBLE ACUTE ACCENT (occasionally misused as quote)
    "\u02f4"  # MODIFIER LETTER MIDDLE GRAVE ACCENT
    # Combining marks used as apostrophes
    "\u0313"  # COMBINING COMMA ABOVE
    "\u0315"  # COMBINING COMMA ABOVE RIGHT
    # Script-specific apostrophe marks
    "\u055a"  # ARMENIAN APOSTROPHE
    "\u05f3"  # HEBREW PUNCTUATION GERESH
    "\u07f4"  # NKO HIGH TONE APOSTROPHE
    "\u07f5"  # NKO LOW TONE APOSTROPHE
    # Fullwidth / compatibility forms
    "\uff07"  # FULLWIDTH APOSTROPHE
    "\uff40"  # FULLWIDTH GRAVE ACCENT
    # Greek breathing marks
    "\u1fbf"  # GREEK PSILI
    "\u1fbd"  # GREEK KORONIS
    # Latin extended
    "\ua78c"  # LATIN SMALL LETTER SALTILLO
    # Ornamental single quotation marks
    "\u275b"  # HEAVY SINGLE TURNED COMMA QUOTATION MARK ORNAMENT
    "\u275c"  # HEAVY SINGLE COMMA QUOTATION MARK ORNAMENT
    "\u275f"  # HEAVY LOW SINGLE COMMA QUOTATION MARK ORNAMENT
)


def _normalize_apostrophes(text: str) -> str:
    """Normalize Unicode apostrophe variants to ASCII apostrophe.

    Many texts (especially ebooks, PDFs, and word processor output) use
    typographic "smart quotes" instead of ASCII apostrophes. This function
    normalizes all variants to the standard ASCII apostrophe (U+0027) to
    ensure consistent BNC lookups.

    Args:
        text: Input text potentially containing apostrophe variants

    Returns:
        Text with all apostrophe variants normalized to ASCII apostrophe

    Example:
        >>> _normalize_apostrophes("don't")  # curly apostrophe
        "don't"  # ASCII apostrophe
    """
    for char in _APOSTROPHE_VARIANTS:
        text = text.replace(char, "'")
    return text


# Unicode dash / hyphen variants to normalize.
# See: https://github.com/craigtrim/pystylometry/issues/58
#
# Category 1 — em-dashes and long dashes: join words without whitespace.
# These are replaced with a SPACE so that "and—and" becomes two tokens.
_EM_DASH_CHARS = (
    # General punctuation dashes (word-joining)
    "\u2013"  # EN DASH (often used as em-dash in ebooks)
    "\u2014"  # EM DASH
    "\u2015"  # HORIZONTAL BAR
    # Additional dash-like punctuation
    "\u2e17"  # DOUBLE OBLIQUE HYPHEN
    "\u2e1a"  # HYPHEN WITH DIAERESIS
    "\u2e3a"  # TWO-EM DASH
    "\u2e3b"  # THREE-EM DASH
)

# Category 2 — hyphen variants: part of compound words.
# These are replaced with ASCII HYPHEN-MINUS (U+002D) so that
# "re‑enter" (U+2011) correctly matches the hyphenated.prefixed pattern.
_HYPHEN_VARIANTS = (
    # General punctuation hyphens
    "\u2010"  # HYPHEN
    "\u2011"  # NON-BREAKING HYPHEN
    "\u2012"  # FIGURE DASH
    # Mathematical minus / dash-like operators
    "\u2212"  # MINUS SIGN
    "\u2796"  # HEAVY MINUS SIGN
    # Compatibility / presentation forms
    "\ufe58"  # SMALL EM DASH
    "\ufe63"  # SMALL HYPHEN-MINUS
    "\uff0d"  # FULLWIDTH HYPHEN-MINUS
    # Script-specific hyphenation marks
    "\u058a"  # ARMENIAN HYPHEN
    "\u05be"  # HEBREW MAQAF
    "\u1400"  # CANADIAN SYLLABICS HYPHEN
    "\u30a0"  # KATAKANA-HIRAGANA DOUBLE HYPHEN
)

# Category 3 — invisible / soft hyphens and variation selectors: removed entirely.
_SOFT_HYPHENS = (
    "\u00ad"  # SOFT HYPHEN
    "\u1806"  # MONGOLIAN TODO SOFT HYPHEN
    "\u2063"  # INVISIBLE SEPARATOR
    # Mongolian free variation selectors (invisible formatting; appear in
    # apostrophe-like shaping contexts but carry no glyph of their own).
    "\u180b"  # MONGOLIAN FREE VARIATION SELECTOR ONE
    "\u180c"  # MONGOLIAN FREE VARIATION SELECTOR TWO
    "\u180d"  # MONGOLIAN FREE VARIATION SELECTOR THREE
)


def _normalize_dashes(text: str) -> str:
    """Normalize Unicode dash and hyphen variants for consistent tokenization.

    Performs three operations in order:

    1. **Em-dash splitting** — replace em-dashes, horizontal bars, two/three-em
       dashes, and other long dash punctuation with a space so that joined
       words like ``and—and`` become separate tokens.
    2. **Hyphen normalization** — replace Unicode hyphen variants (general
       punctuation, mathematical, compatibility forms, script-specific) with
       ASCII hyphen-minus (U+002D) so that compound words like ``re‑enter``
       classify correctly as ``hyphenated.prefixed``.
    3. **Soft-hyphen removal** — delete invisible line-break hints (U+00AD,
       U+1806, U+2063).

    Args:
        text: Input text potentially containing Unicode dash/hyphen variants.

    Returns:
        Text with dashes and hyphens normalized.

    Related GitHub Issue:
        #58 -- Add centralized Unicode dash & hyphen normalization
        https://github.com/craigtrim/pystylometry/issues/58

    Example:
        >>> _normalize_dashes("and\u2014and")      # em-dash → space
        'and and'
        >>> _normalize_dashes("re\u2011enter")      # non-breaking hyphen → ASCII -
        're-enter'
        >>> _normalize_dashes("beau\u00adtiful")    # soft hyphen → removed
        'beautiful'
    """
    # 1. Em-dashes → space (must happen before whitespace split)
    for char in _EM_DASH_CHARS:
        text = text.replace(char, " ")

    # 2. Hyphen variants → ASCII hyphen-minus
    for char in _HYPHEN_VARIANTS:
        text = text.replace(char, "-")

    # 3. Soft / invisible hyphens → removed
    for char in _SOFT_HYPHENS:
        text = text.replace(char, "")

    return text


@dataclass
class WordAnalysis:
    """Analysis of a single word against BNC frequency.

    Attributes:
        word: The word being analyzed (lowercase)
        observed: Number of times the word appears in the text
        expected: Expected count based on BNC relative frequency
        ratio: observed / expected (None if not in BNC)
        in_wordnet: Whether the word exists in WordNet
        in_gngram: Whether the word exists in Google Books Ngram data
        char_type: Classification of character content

    Related GitHub Issue:
        #47 - Integrate gngram-lookup into BNC frequency analysis
        https://github.com/craigtrim/pystylometry/issues/47
    """

    word: str
    observed: int
    expected: float | None
    ratio: float | None
    in_wordnet: bool | None
    in_gngram: bool | None
    char_type: Literal["latin", "unicode", "numeric", "mixed", "punctuation"]


@dataclass
class BNCFrequencyResult:
    """Result of BNC frequency analysis.

    Attributes:
        overused: Words appearing more frequently than expected (ratio > threshold)
        underused: Words appearing less frequently than expected (ratio < threshold)
        not_in_bnc: Words not found in the BNC corpus
        total_tokens: Total word count in the text
        unique_tokens: Number of unique words
        overuse_threshold: Ratio above which words are considered overused
        underuse_threshold: Ratio below which words are considered underused
        metadata: Additional analysis metadata
    """

    overused: list[WordAnalysis]
    underused: list[WordAnalysis]
    not_in_bnc: list[WordAnalysis]
    total_tokens: int
    unique_tokens: int
    overuse_threshold: float
    underuse_threshold: float
    metadata: dict


def _classify_char_type(
    word: str,
) -> Literal["latin", "unicode", "numeric", "mixed", "punctuation"]:
    """Classify the character content of a word.

    Args:
        word: Word to classify

    Returns:
        Character type classification:
        - latin: Pure ASCII alphabetic characters (a-z, A-Z)
        - unicode: Contains non-ASCII characters (accents, etc.)
        - numeric: Contains only digits
        - mixed: Contains letters and numbers or other combinations
        - punctuation: Contains only punctuation
    """
    if not word:
        return "punctuation"

    has_ascii_alpha = bool(re.search(r"[a-zA-Z]", word))
    has_unicode_alpha = any(unicodedata.category(c).startswith("L") and ord(c) > 127 for c in word)
    has_digit = any(c.isdigit() for c in word)
    has_punct = any(unicodedata.category(c).startswith("P") for c in word)

    # Determine classification
    if has_unicode_alpha:
        return "unicode"
    elif has_digit and not has_ascii_alpha:
        return "numeric"
    elif has_digit and has_ascii_alpha:
        return "mixed"
    elif has_ascii_alpha and not has_punct:
        return "latin"
    elif has_ascii_alpha and has_punct:
        return "mixed"
    elif not has_ascii_alpha and not has_digit:
        return "punctuation"
    else:
        return "mixed"


def compute_bnc_frequency(
    text: str,
    overuse_threshold: float = 1.3,
    underuse_threshold: float = 0.8,
    include_wordnet: bool = True,
    include_gngram: bool = True,
    min_mentions: int = 1,
) -> BNCFrequencyResult:
    """Compute BNC frequency analysis for a text.

    Compares observed word frequencies against expected frequencies from the
    British National Corpus. Words are categorized as overused, underused,
    or not in BNC based on their frequency ratios.

    Args:
        text: Input text to analyze
        overuse_threshold: Ratio above which words are considered overused (default: 1.3)
        underuse_threshold: Ratio below which words are considered underused (default: 0.8)
        include_wordnet: Whether to check WordNet for unknown words (default: True)
        include_gngram: Whether to check Google Books Ngram data (default: True)
        min_mentions: Minimum number of mentions to include word (default: 1)

    Returns:
        BNCFrequencyResult with categorized word lists

    Raises:
        ImportError: If bnc-lookup package is not installed

    Related GitHub Issue:
        #47 - Integrate gngram-lookup into BNC frequency analysis
        https://github.com/craigtrim/pystylometry/issues/47

    Example:
        >>> result = compute_bnc_frequency("The captain ordered the larboard watch...")
        >>> result.overused[:3]  # Top 3 overused words
        [WordAnalysis(word='larboard', ratio=33153.5, ...), ...]
        >>> result.not_in_bnc[:3]  # Words not in BNC
        [WordAnalysis(word='xyzbot', ...), ...]
    """
    # Check dependency
    check_optional_dependency("bnc_lookup", "lexical")
    from bnc_lookup import relative_frequency  # type: ignore[import-untyped]

    # Optional wordnet lookup
    wordnet_checker = None
    if include_wordnet:
        try:
            from wordnet_lookup import (
                is_wordnet_term as _is_wordnet_term,  # type: ignore[import-untyped]
            )

            wordnet_checker = _is_wordnet_term
        except ImportError:
            # WordNet lookup is optional
            pass

    # Optional Google Books Ngram lookup (Issue #47)
    # Uses batch_frequency() for O(1) hash-based lookups grouped by bucket
    gngram_available = False
    gngram_results: dict[str, bool] = {}
    if include_gngram:
        try:
            from gngram_counter import batch_frequency  # type: ignore[import-untyped]

            gngram_available = True
        except ImportError:
            # gngram-lookup is optional
            pass

    # ── Tokenization ─────────────────────────────────────────────────────
    #
    # Use the central tokenizer (advanced_tokenize) instead of a naive
    # whitespace split.  This was a deliberate decision to begin
    # standardizing tokenization across all analysis modules.
    #
    # Related GitHub Issue:
    #     #56 — Standardize tokenization across all analysis modules
    #     https://github.com/craigtrim/pystylometry/issues/56
    #
    # Why advanced_tokenize and not raw .split()?
    #   • The central tokenizer normalizes Unicode (smart quotes, curly
    #     apostrophes, ligatures, zero-width chars) via _UNICODE_REPLACEMENTS
    #     in tokenizer.py.  This supersedes the narrower _normalize_apostrophes()
    #     call that was here before — except for a handful of exotic codepoints
    #     (Armenian apostrophe, Hebrew geresh, etc.) that the central tokenizer
    #     does not cover.  We keep _normalize_apostrophes() as a pre-pass for
    #     those edge cases.
    #   • Punctuation tokens are stripped (strip_punctuation=True), giving us
    #     clean word tokens without a manual regex pass.
    #   • Contractions like "don't" are preserved as single tokens, which is
    #     what BNC lookups expect.
    #
    # Em-dash / en-dash handling:
    #   The central tokenizer normalizes em/en dashes to ASCII hyphens, but
    #   its regex then captures "acted-loud" as a single hyphenated compound
    #   token.  For BNC lookups we need these as separate words, so we
    #   pre-split on em/en dashes by inserting spaces before tokenizing.
    #   The central tokenizer is not modified — this is BNC-side pre-processing.
    #
    # ──────────────────────────────────────────────────────────────────────

    # Pre-pass 1: normalize exotic apostrophe variants (Issue #45)
    # Covers codepoints not in the central tokenizer's _UNICODE_REPLACEMENTS.
    prepared_text = _normalize_apostrophes(text)

    # Pre-pass 2: normalize dashes and hyphens (Issue #58).
    # Splits em-dashes into spaces, normalizes Unicode hyphens to ASCII,
    # and removes soft hyphens.
    prepared_text = _normalize_dashes(prepared_text)

    # Central tokenizer: lowercase, strip punctuation, preserve contractions.
    tokens = advanced_tokenize(
        prepared_text,
        lowercase=True,
        strip_punctuation=True,
        expand_contractions=False,
    )

    total_tokens = len(tokens)

    # Count observed frequency of each word
    observed = Counter(tokens)
    unique_words = list(observed.keys())

    # Get BNC relative frequencies (one at a time - bnc_lookup doesn't have batch)
    bnc_freqs = {word: relative_frequency(word) for word in unique_words}

    # Batch lookup Google Books Ngram data (Issue #47)
    # batch_frequency returns dict[str, FrequencyData | None] — None means not found
    if gngram_available:
        gngram_batch = batch_frequency(unique_words)  # type: ignore[possibly-undefined]
        gngram_results = {word: gngram_batch.get(word) is not None for word in unique_words}

    # Analyze each word
    overused: list[WordAnalysis] = []
    underused: list[WordAnalysis] = []
    not_in_bnc: list[WordAnalysis] = []

    for word, obs_count in observed.items():
        if obs_count < min_mentions:
            continue

        # Classify character type
        char_type = _classify_char_type(word)

        # Get BNC frequency
        rel_freq = bnc_freqs.get(word)

        # Check WordNet if requested
        in_wordnet = None
        if wordnet_checker is not None:
            in_wordnet = wordnet_checker(word)

        # Check Google Books Ngram if available (Issue #47)
        in_gngram: bool | None = None
        if gngram_available:
            in_gngram = gngram_results.get(word, False)

        if rel_freq is None or rel_freq == 0:
            # Word not in BNC
            analysis = WordAnalysis(
                word=word,
                observed=obs_count,
                expected=None,
                ratio=None,
                in_wordnet=in_wordnet,
                in_gngram=in_gngram,
                char_type=char_type,
            )
            not_in_bnc.append(analysis)
        else:
            # Compute expected count and ratio
            expected = rel_freq * total_tokens
            ratio = obs_count / expected if expected > 0 else None

            analysis = WordAnalysis(
                word=word,
                observed=obs_count,
                expected=expected,
                ratio=ratio,
                in_wordnet=in_wordnet,
                in_gngram=in_gngram,
                char_type=char_type,
            )

            if ratio is not None:
                if ratio > overuse_threshold:
                    overused.append(analysis)
                elif ratio < underuse_threshold:
                    underused.append(analysis)

    # Sort by ratio (highest first for overused, lowest first for underused)
    overused.sort(key=lambda x: x.ratio or 0, reverse=True)
    underused.sort(key=lambda x: x.ratio or float("inf"))
    # Sort not_in_bnc by observed count
    not_in_bnc.sort(key=lambda x: x.observed, reverse=True)

    return BNCFrequencyResult(
        overused=overused,
        underused=underused,
        not_in_bnc=not_in_bnc,
        total_tokens=total_tokens,
        unique_tokens=len(unique_words),
        overuse_threshold=overuse_threshold,
        underuse_threshold=underuse_threshold,
        metadata={
            "include_wordnet": include_wordnet,
            "include_gngram": include_gngram,
            "gngram_available": gngram_available,
            "min_mentions": min_mentions,
            "overused_count": len(overused),
            "underused_count": len(underused),
            "not_in_bnc_count": len(not_in_bnc),
        },
    )
