"""Stylistic flourishes and rhetorical device detection for authorship attribution.

This module detects and quantifies deliberate or habitual writing embellishments
that distinguish an author's voice. Unlike the word-level marker counting in
markers.py (which uses dictionary lookup for individual tokens), this module
analyzes multi-word and structural patterns: alliteration, anaphora, epistrophe,
punctuation style, and serial comma usage.

Architectural Note:
    This module is intentionally separate from stylistic/markers.py. The two
    modules analyze different levels of linguistic structure:
    - markers.py: Word-level features via dictionary lookup (contractions,
      intensifiers, hedges, modals, negation)
    - flourishes.py: Multi-word and structural patterns via sequence analysis
      (alliteration, anaphora, epistrophe, punctuation conventions)

    Combining them would create an unwieldy monolithic function. Keeping them
    separate follows the single-responsibility principle and allows users to
    run only the analysis they need.

Related GitHub Issue:
    #30 - Whonix stylometric features (stylistic flourishes)
    https://github.com/craigtrim/pystylometry/issues/30

Whonix Source:
    The Whonix Stylometry documentation identifies "stylistic flourishes"
    and "sentence/phrasing patterns" as deanonymization vectors. Rhetorical
    devices like alliteration, anaphora, and distinctive punctuation habits
    form stable authorial signatures.
    https://www.whonix.org/wiki/Stylometry

Categories of stylistic flourishes analyzed:

    1. Alliteration:
       Consecutive words sharing the same initial consonant sound.
       Example: "Peter Piper picked a peck of pickled peppers."
       Authors with literary training show higher alliteration rates.

    2. Anaphora:
       Repeated word or phrase at the beginning of successive sentences.
       Example: "We shall fight on the beaches. We shall fight on the
       landing grounds. We shall fight in the fields."
       A deliberate rhetorical device common in persuasive and literary text.

    3. Epistrophe:
       Repeated word or phrase at the end of successive sentences.
       Example: "When I was a child, I spoke as a child. I understood as
       a child. I thought as a child."
       Less common than anaphora but equally distinctive when present.

    4. Em-dash and En-dash:
       Distinguished from each other because their usage reflects different
       conventions. Em-dashes (—) indicate parenthetical asides; en-dashes
       (–) indicate ranges. Some authors heavily favor em-dashes while
       others avoid them entirely.

    5. Ellipsis:
       Trailing dots (... or …) indicating omission, hesitation, or
       trailing off. Frequency is a strong stylistic marker.

    6. Serial Comma (Oxford Comma):
       Whether the author uses a comma before the final conjunction in
       a list (e.g., "red, white, and blue" vs. "red, white and blue").
       This is one of the most consistent stylistic habits — authors
       almost never switch between conventions.

    7. Quotation Style:
       Preference for double quotes ("") vs. single quotes ('').
       Reflects national conventions and personal style.

    8. Rhetorical Questions:
       Questions posed for effect rather than to elicit an answer.
       Frequency varies significantly by genre and author.

References:
    Stamatatos, E. (2009). A survey of modern authorship attribution
        methods. JASIST, 60(3), 538-556.
    Fahnestock, J. (2011). Rhetorical style: The uses of language in
        persuasion. Oxford University Press.
    Biber, D. (1988). Variation across speech and writing. Cambridge
        University Press.
    Corbett, E. P. J., & Connors, R. J. (1999). Classical rhetoric for
        the modern student (4th ed.). Oxford University Press.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

from .._types import StylisticFlourishesResult

# =============================================================================
# SENTENCE SPLITTING
# =============================================================================
# A simple regex-based sentence splitter. This intentionally avoids requiring
# spaCy or NLTK, keeping the module dependency-free. The pattern handles
# common abbreviations (Mr., Dr., etc.) and decimal numbers to reduce
# false splits.
#
# For more accurate sentence splitting, users can preprocess with spaCy
# and join sentences with explicit delimiters before calling this module.

# Common abbreviations that end with a period but don't end a sentence.
# These are used to suppress false sentence splits at abbreviation periods.
_ABBREV_SET: set[str] = {
    "mr", "mrs", "ms", "dr", "prof", "jr", "sr", "st", "rev", "gen",
    "sgt", "capt", "lt", "col", "vs", "etc", "approx", "ca", "al",
}

# Two-part abbreviations with internal periods: "e.g.", "i.e."
_DOTTED_ABBREVS: set[str] = {"e.g", "i.e"}

# Sentence boundary candidates: period/question/exclamation followed by
# whitespace and an uppercase letter or opening quote.
_SENTENCE_BOUNDARY = re.compile(
    r'([.!?]+)'        # Group 1: sentence-ending punctuation
    r'(\s+)'            # Group 2: whitespace
    r'(?=[A-Z"\'\(\[])'  # Lookahead: uppercase letter or opening quote
)


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences using regex heuristics.

    Finds candidate sentence boundaries (punctuation + whitespace +
    uppercase letter) and then filters out false positives caused by
    abbreviations (Mr., Dr., etc.) and decimal numbers (3.14).

    This is a simple heuristic splitter. For higher accuracy, consider
    preprocessing with spaCy's sentencizer.

    Args:
        text: Raw input text.

    Returns:
        List of sentence strings. Empty sentences are filtered out.
    """
    # Find all candidate split positions
    sentences: list[str] = []
    last_end = 0

    for match in _SENTENCE_BOUNDARY.finditer(text):
        punct = match.group(1)
        split_start = match.start()
        split_end = match.start(2) + len(match.group(2))

        # Check for false positives:

        # 1. Preceded by a digit (e.g., "3.14") — only for periods
        if punct == "." and split_start > 0 and text[split_start - 1].isdigit():
            continue

        # 2. Preceded by a known abbreviation
        # Extract the word immediately before the period
        if punct == ".":
            # Walk backwards to find the word before the period
            word_end = split_start
            word_start = word_end
            while word_start > 0 and text[word_start - 1].isalpha():
                word_start -= 1
            preceding_word = text[word_start:word_end].lower()

            if preceding_word in _ABBREV_SET:
                continue

            # Check for dotted abbreviations like "e.g" or "i.e"
            # (the period we matched is the trailing one in "e.g." / "i.e.")
            if word_start >= 2 and text[word_start - 1] == ".":
                # Look for pattern like "e.g" before the dot
                dot_word_start = word_start - 1
                while dot_word_start > 0 and (
                    text[dot_word_start - 1].isalpha()
                    or text[dot_word_start - 1] == "."
                ):
                    dot_word_start -= 1
                dotted = text[dot_word_start:word_end].lower()
                if dotted in _DOTTED_ABBREVS:
                    continue

        # This is a real sentence boundary — split here
        sentence = text[last_end:split_start + len(punct)].strip()
        if sentence:
            sentences.append(sentence)
        last_end = split_end

    # Add the final segment
    remainder = text[last_end:].strip()
    if remainder:
        sentences.append(remainder)

    return sentences if sentences else [text.strip()] if text.strip() else []


# =============================================================================
# ALLITERATION DETECTION
# =============================================================================
# Alliteration: consecutive words sharing the same initial consonant sound.
# We use a simplified phonetic approach based on the first letter (or first
# consonant cluster) of each word. This is an approximation — true
# alliteration is phonetic (e.g., "phone" and "far" alliterate), but
# letter-based detection captures most cases without requiring a
# pronunciation dictionary.

# Consonants for alliteration detection. Vowels are excluded because
# vowel-initial alliteration (assonance) is a different device.
_CONSONANTS = set("bcdfghjklmnpqrstvwxyz")

# Minimum consecutive alliterative words to count as alliteration
_MIN_ALLITERATION_LENGTH = 3


def _detect_alliteration(text: str) -> tuple[int, list[str]]:
    """Detect alliterative sequences in text.

    Scans consecutive words for shared initial consonant letters. A
    sequence of 3+ words starting with the same consonant is counted
    as one alliterative instance. Words starting with vowels break
    the sequence.

    Limitation: This is letter-based, not phonetic. "City" and "cent"
    will match (both start with 'c'), but "phone" and "far" will not
    (different starting letters despite same sound). This is a known
    trade-off to avoid requiring a pronunciation dictionary.

    Args:
        text: Raw input text.

    Returns:
        Tuple of (count, examples) where count is the number of
        alliterative sequences found, and examples is a list of
        sample alliterative word groups (up to 10).
    """
    # Tokenize: extract words, lowercase
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())

    alliterations: list[str] = []
    current_letter: str | None = None
    current_run: list[str] = []

    for word in words:
        if not word:
            continue

        first_letter = word[0]

        # Only track consonant-initial words for alliteration
        if first_letter in _CONSONANTS:
            if first_letter == current_letter:
                # Continue the current alliterative run
                current_run.append(word)
            else:
                # New consonant letter: flush previous run if long enough
                if len(current_run) >= _MIN_ALLITERATION_LENGTH:
                    alliterations.append(" ".join(current_run))
                # Start a new run
                current_letter = first_letter
                current_run = [word]
        else:
            # Vowel-initial word breaks the alliterative sequence
            if len(current_run) >= _MIN_ALLITERATION_LENGTH:
                alliterations.append(" ".join(current_run))
            current_letter = None
            current_run = []

    # Flush final run
    if len(current_run) >= _MIN_ALLITERATION_LENGTH:
        alliterations.append(" ".join(current_run))

    return len(alliterations), alliterations[:10]


# =============================================================================
# ANAPHORA DETECTION
# =============================================================================
# Anaphora: repeated word or phrase at the beginning of successive sentences.
# We extract the first N words of each sentence and look for patterns where
# consecutive sentences share the same opening.


def _detect_anaphora(
    sentences: list[str], max_words: int = 4
) -> tuple[int, list[tuple[str, int]]]:
    """Detect anaphoric patterns (repeated sentence beginnings).

    Examines the first 1-4 words of each sentence and identifies cases
    where 2+ consecutive sentences share the same opening words. The
    longest matching prefix is used.

    Args:
        sentences: List of sentence strings.
        max_words: Maximum number of opening words to compare (default: 4).
                   Longer prefixes are checked first for greedy matching.

    Returns:
        Tuple of (total_count, patterns) where total_count is the total
        number of anaphoric patterns detected, and patterns is a list
        of (repeated_phrase, count) tuples sorted by count descending.
    """
    if len(sentences) < 2:
        return 0, []

    # Extract opening words from each sentence
    openings: list[list[str]] = []
    for sentence in sentences:
        words = re.findall(r"\b\w+\b", sentence.lower())
        openings.append(words[:max_words] if words else [])

    # Track anaphoric patterns across all prefix lengths
    pattern_counts: Counter[str] = Counter()

    # Check for consecutive sentences sharing openings
    # Start with longest prefix and work down for greedy matching
    matched_indices: set[int] = set()

    for prefix_len in range(max_words, 0, -1):
        i = 0
        while i < len(openings) - 1:
            if i in matched_indices:
                i += 1
                continue

            # Get the prefix of sentence i
            if len(openings[i]) < prefix_len:
                i += 1
                continue

            prefix = " ".join(openings[i][:prefix_len])
            run_length = 1

            # Count consecutive sentences with the same prefix
            j = i + 1
            while j < len(openings):
                if (
                    len(openings[j]) >= prefix_len
                    and " ".join(openings[j][:prefix_len]) == prefix
                    and j not in matched_indices
                ):
                    run_length += 1
                    j += 1
                else:
                    break

            # If 2+ consecutive sentences share the prefix, record it
            if run_length >= 2:
                pattern_counts[prefix] += run_length
                # Mark these indices as matched to prevent shorter
                # prefix matches from double-counting
                for k in range(i, i + run_length):
                    matched_indices.add(k)

            i += 1

    total_count = sum(pattern_counts.values())
    patterns = pattern_counts.most_common()

    return total_count, patterns


# =============================================================================
# EPISTROPHE DETECTION
# =============================================================================
# Epistrophe: repeated word or phrase at the end of successive sentences.
# Mirror of anaphora detection but examines sentence endings.


def _detect_epistrophe(
    sentences: list[str], max_words: int = 4
) -> tuple[int, list[tuple[str, int]]]:
    """Detect epistrophe patterns (repeated sentence endings).

    Examines the last 1-4 words of each sentence and identifies cases
    where 2+ consecutive sentences share the same ending words.

    Args:
        sentences: List of sentence strings.
        max_words: Maximum number of ending words to compare (default: 4).

    Returns:
        Tuple of (total_count, patterns) where total_count is the total
        number of epistrophe patterns detected, and patterns is a list
        of (repeated_phrase, count) tuples sorted by count descending.
    """
    if len(sentences) < 2:
        return 0, []

    # Extract ending words from each sentence (strip trailing punctuation)
    endings: list[list[str]] = []
    for sentence in sentences:
        # Remove trailing punctuation before extracting words
        cleaned = re.sub(r"[.!?;:]+$", "", sentence)
        words = re.findall(r"\b\w+\b", cleaned.lower())
        endings.append(words[-max_words:] if words else [])

    # Track epistrophe patterns
    pattern_counts: Counter[str] = Counter()
    matched_indices: set[int] = set()

    for suffix_len in range(max_words, 0, -1):
        i = 0
        while i < len(endings) - 1:
            if i in matched_indices:
                i += 1
                continue

            if len(endings[i]) < suffix_len:
                i += 1
                continue

            suffix = " ".join(endings[i][-suffix_len:])
            run_length = 1

            j = i + 1
            while j < len(endings):
                if (
                    len(endings[j]) >= suffix_len
                    and " ".join(endings[j][-suffix_len:]) == suffix
                    and j not in matched_indices
                ):
                    run_length += 1
                    j += 1
                else:
                    break

            if run_length >= 2:
                pattern_counts[suffix] += run_length
                for k in range(i, i + run_length):
                    matched_indices.add(k)

            i += 1

    total_count = sum(pattern_counts.values())
    patterns = pattern_counts.most_common()

    return total_count, patterns


# =============================================================================
# PUNCTUATION ANALYSIS
# =============================================================================

# Em-dash patterns: Unicode em-dash (—) or double hyphen (--)
_EM_DASH = re.compile(r"—|--")

# En-dash pattern: Unicode en-dash (–) — distinguished from hyphen
_EN_DASH = re.compile(r"–")

# Ellipsis pattern: three dots or Unicode ellipsis character
_ELLIPSIS = re.compile(r"\.{3}|…")

# =============================================================================
# SERIAL COMMA (OXFORD COMMA) DETECTION
# =============================================================================
# The serial comma pattern detects lists of 3+ items joined by a conjunction.
# We look for patterns like:
#   - "A, B, and C" (serial comma present)
#   - "A, B and C" (serial comma absent)
#
# This is a heuristic: false positives can occur with compound subjects
# or other comma-separated structures. However, for stylometric purposes,
# even approximate detection is useful because authors are highly consistent
# in their serial comma usage.

# Pattern for serial comma: word, word, and/or word
# The final comma before "and"/"or" is the serial comma
_SERIAL_COMMA = re.compile(
    r"\b\w+\s*,\s*\w+\s*,\s+(?:and|or)\s+\w+",
    re.IGNORECASE,
)

# Pattern for NO serial comma: word, word and/or word
# Missing comma before "and"/"or"
_NO_SERIAL_COMMA = re.compile(
    r"\b\w+\s*,\s*\w+\s+(?:and|or)\s+\w+",
    re.IGNORECASE,
)


def _detect_serial_comma(text: str) -> tuple[int, int, str, float]:
    """Detect serial comma (Oxford comma) preference.

    Counts instances where a serial comma IS used and instances where
    it is NOT used, then classifies the author's preference.

    Methodology:
        1. Find all "A, B, and C" patterns (serial comma present)
        2. Find all "A, B and C" patterns (serial comma absent)
        3. Exclude overlapping matches (serial comma matches are a subset
           of no-serial matches, so we subtract to avoid double-counting)
        4. Classify: oxford / no_oxford / mixed / insufficient_data

    Args:
        text: Raw input text.

    Returns:
        Tuple of (serial_count, no_serial_count, preference, ratio).
    """
    serial_matches = _SERIAL_COMMA.findall(text)
    no_serial_matches = _NO_SERIAL_COMMA.findall(text)

    serial_count = len(serial_matches)
    # no_serial_matches includes serial_comma matches (superset pattern),
    # so subtract to get the true "no serial comma" count
    no_serial_count = max(0, len(no_serial_matches) - serial_count)

    total = serial_count + no_serial_count

    if total == 0:
        return 0, 0, "insufficient_data", 0.0

    ratio = serial_count / total

    # Classify preference
    if ratio >= 0.8:
        preference = "oxford"
    elif ratio <= 0.2:
        preference = "no_oxford"
    else:
        preference = "mixed"

    return serial_count, no_serial_count, preference, ratio


# =============================================================================
# QUOTATION STYLE DETECTION
# =============================================================================

# Double quotation marks: straight and curly
_DOUBLE_QUOTES = re.compile(r'["""]')

# Single quotation marks: straight and curly (excluding apostrophes)
# We try to distinguish apostrophes from single quotes by context:
# single quotes typically appear at the start/end of a word or phrase,
# while apostrophes appear mid-word.
_SINGLE_QUOTES = re.compile(r"(?<!\w)['''](?=\w)|(?<=\w)['''](?!\w)")


def _detect_quotation_style(text: str) -> tuple[int, int, str]:
    """Detect quotation mark style preference.

    Counts double and single quotation marks and classifies the
    author's preference. Attempts to exclude apostrophes from the
    single-quote count.

    Args:
        text: Raw input text.

    Returns:
        Tuple of (double_count, single_count, style).
    """
    double_count = len(_DOUBLE_QUOTES.findall(text))
    single_count = len(_SINGLE_QUOTES.findall(text))

    if double_count == 0 and single_count == 0:
        style = "none"
    elif single_count == 0:
        style = "double"
    elif double_count == 0:
        style = "single"
    else:
        # Both present: classify based on dominance
        ratio = double_count / (double_count + single_count)
        if ratio >= 0.7:
            style = "double"
        elif ratio <= 0.3:
            style = "single"
        else:
            style = "mixed"

    return double_count, single_count, style


# =============================================================================
# RHETORICAL QUESTION DETECTION
# =============================================================================
# A simple heuristic: count sentences ending with "?" that are not
# clearly seeking information (e.g., not starting with interrogative
# words in a dialogue context). For stylometric purposes, all question
# marks are counted since the distinction between rhetorical and genuine
# questions is context-dependent and less important than frequency.


def _count_rhetorical_questions(sentences: list[str]) -> int:
    """Count sentences that end with a question mark.

    For stylometric purposes, all interrogative sentences are counted.
    The distinction between rhetorical and genuine questions is context-
    dependent and less important than the overall frequency of question
    usage, which varies significantly by author.

    Args:
        sentences: List of sentence strings.

    Returns:
        Count of sentences ending with "?".
    """
    count = 0
    for sentence in sentences:
        stripped = sentence.rstrip()
        if stripped.endswith("?"):
            count += 1
    return count


# =============================================================================
# COMPOSITE FLOURISH SCORE
# =============================================================================


def _compute_flourish_score(
    alliteration_density: float,
    anaphora_density: float,
    epistrophe_density: float,
    em_dash_density: float,
    ellipsis_density: float,
    rhetorical_question_density: float,
) -> float:
    """Compute a composite stylistic flourish score.

    The flourish score is a weighted combination of all flourish signals,
    scaled to a 0.0-1.0 range. Higher values indicate more "embellished"
    or "literary" writing style. A score of 0.0 indicates plain,
    unadorned prose.

    Weighting rationale:
        - Alliteration (0.20): Common literary device, moderate distinctiveness.
        - Anaphora (0.25): Strong rhetorical device, highly intentional when
          present. Weighted higher because it requires conscious effort.
        - Epistrophe (0.15): Less common than anaphora, lower weight due to
          rarity, but still distinctive when present.
        - Em-dash density (0.15): Common stylistic choice, varies by author.
        - Ellipsis density (0.10): Less discriminating on its own.
        - Rhetorical questions (0.15): Varies by genre and author.

    Each component is capped at a saturation point before weighting.

    Args:
        alliteration_density: Alliterative sequences per 100 words.
        anaphora_density: Anaphoric patterns per 100 sentences.
        epistrophe_density: Epistrophe patterns per 100 sentences.
        em_dash_density: Em-dashes per 100 words.
        ellipsis_density: Ellipses per 100 words.
        rhetorical_question_density: Questions per 100 sentences.

    Returns:
        Flourish score between 0.0 and 1.0.
    """
    # Cap each component at its saturation point, then normalize to 0-1
    allit = min(alliteration_density / 2.0, 1.0) * 0.20
    anaph = min(anaphora_density / 30.0, 1.0) * 0.25
    epist = min(epistrophe_density / 20.0, 1.0) * 0.15
    em = min(em_dash_density / 3.0, 1.0) * 0.15
    ellip = min(ellipsis_density / 2.0, 1.0) * 0.10
    rhet = min(rhetorical_question_density / 20.0, 1.0) * 0.15

    raw_score = allit + anaph + epist + em + ellip + rhet
    return max(0.0, min(1.0, raw_score))


# =============================================================================
# MAIN FUNCTION
# =============================================================================


def compute_stylistic_flourishes(text: str) -> StylisticFlourishesResult:
    """Analyze stylistic flourishes and rhetorical devices for authorship attribution.

    Detects and quantifies multi-word and structural patterns that distinguish
    an author's voice: alliteration, anaphora, epistrophe, punctuation
    conventions (em-dash, ellipsis, serial comma, quotation style), and
    rhetorical question frequency.

    This function complements compute_stylistic_markers() in markers.py,
    which handles word-level features. Together they provide comprehensive
    stylistic analysis.

    Related GitHub Issue:
        #30 - Whonix stylometric features (stylistic flourishes)
        https://github.com/craigtrim/pystylometry/issues/30

    Whonix Source:
        The Whonix Stylometry documentation identifies "stylistic flourishes"
        and "sentence/phrasing patterns" as deanonymization vectors:
        https://www.whonix.org/wiki/Stylometry

    Algorithm:
        1. Split text into sentences (regex heuristic)
        2. Detect alliteration (consecutive consonant-initial words)
        3. Detect anaphora (repeated sentence beginnings)
        4. Detect epistrophe (repeated sentence endings)
        5. Count em-dashes, en-dashes, and ellipses
        6. Detect serial comma preference
        7. Detect quotation style preference
        8. Count rhetorical questions (question-mark sentences)
        9. Compute composite flourish score from weighted components

    Args:
        text: Input text to analyze. Should contain multiple sentences for
              meaningful anaphora/epistrophe detection. Minimum recommended
              length is 5+ sentences.

    Returns:
        StylisticFlourishesResult with counts, densities, preferences,
        and composite flourish score. See _types.py for complete field list.

    Example:
        >>> text = (
        ...     "We shall fight on the beaches. We shall fight on the landing "
        ...     "grounds. We shall fight in the fields and in the streets."
        ... )
        >>> result = compute_stylistic_flourishes(text)
        >>> print(f"Anaphora: {result.anaphora_count}")
        >>> print(f"Serial comma: {result.serial_comma_preference}")
        >>> print(f"Flourish score: {result.flourish_score:.2f}")

    Note:
        - Sentence splitting uses regex heuristics (no spaCy required)
        - Alliteration detection is letter-based, not phonetic
        - Serial comma detection is approximate (heuristic regex)
        - Densities use per-100-words (word metrics) or per-100-sentences
          (sentence-level metrics) for interpretability
        - Empty text returns zero counts and 0.0 for all metrics

    References:
        Stamatatos, E. (2009). A survey of modern authorship attribution
            methods. JASIST, 60(3), 538-556.
        Fahnestock, J. (2011). Rhetorical style: The uses of language in
            persuasion. Oxford University Press.
    """
    # Handle empty text edge case
    if not text or not text.strip():
        return StylisticFlourishesResult(
            alliteration_count=0,
            alliteration_density=0.0,
            alliteration_examples=[],
            anaphora_count=0,
            anaphora_density=0.0,
            anaphora_patterns=[],
            epistrophe_count=0,
            epistrophe_density=0.0,
            epistrophe_patterns=[],
            em_dash_count=0,
            en_dash_count=0,
            em_dash_density=0.0,
            en_dash_density=0.0,
            ellipsis_count=0,
            ellipsis_density=0.0,
            serial_comma_count=0,
            no_serial_comma_count=0,
            serial_comma_preference="insufficient_data",
            serial_comma_ratio=0.0,
            double_quote_count=0,
            single_quote_count=0,
            quotation_style="none",
            rhetorical_question_count=0,
            rhetorical_question_density=0.0,
            flourish_score=0.0,
            metadata={"word_count": 0, "sentence_count": 0, "warning": "Empty text"},
        )

    # =========================================================================
    # BASIC COUNTS
    # =========================================================================
    words = text.split()
    word_count = len(words)
    sentences = _split_sentences(text)
    sentence_count = len(sentences)

    # Guard against zero-word edge case
    if word_count == 0:
        return StylisticFlourishesResult(
            alliteration_count=0,
            alliteration_density=0.0,
            alliteration_examples=[],
            anaphora_count=0,
            anaphora_density=0.0,
            anaphora_patterns=[],
            epistrophe_count=0,
            epistrophe_density=0.0,
            epistrophe_patterns=[],
            em_dash_count=0,
            en_dash_count=0,
            em_dash_density=0.0,
            en_dash_density=0.0,
            ellipsis_count=0,
            ellipsis_density=0.0,
            serial_comma_count=0,
            no_serial_comma_count=0,
            serial_comma_preference="insufficient_data",
            serial_comma_ratio=0.0,
            double_quote_count=0,
            single_quote_count=0,
            quotation_style="none",
            rhetorical_question_count=0,
            rhetorical_question_density=0.0,
            flourish_score=0.0,
            metadata={
                "word_count": 0,
                "sentence_count": sentence_count,
                "warning": "No words found",
            },
        )

    # Density multipliers
    word_density = 100.0 / word_count
    sentence_density = 100.0 / sentence_count if sentence_count > 0 else 0.0

    # =========================================================================
    # ALLITERATION
    # =========================================================================
    alliteration_count, alliteration_examples = _detect_alliteration(text)
    alliteration_density = alliteration_count * word_density

    # =========================================================================
    # ANAPHORA
    # =========================================================================
    anaphora_count, anaphora_patterns = _detect_anaphora(sentences)
    anaphora_density = anaphora_count * sentence_density

    # =========================================================================
    # EPISTROPHE
    # =========================================================================
    epistrophe_count, epistrophe_patterns = _detect_epistrophe(sentences)
    epistrophe_density = epistrophe_count * sentence_density

    # =========================================================================
    # PUNCTUATION: EM-DASH, EN-DASH, ELLIPSIS
    # =========================================================================
    em_dash_count = len(_EM_DASH.findall(text))
    en_dash_count = len(_EN_DASH.findall(text))
    ellipsis_count = len(_ELLIPSIS.findall(text))

    em_dash_density = em_dash_count * word_density
    en_dash_density = en_dash_count * word_density
    ellipsis_density = ellipsis_count * word_density

    # =========================================================================
    # SERIAL COMMA
    # =========================================================================
    (
        serial_comma_count,
        no_serial_comma_count,
        serial_comma_preference,
        serial_comma_ratio,
    ) = _detect_serial_comma(text)

    # =========================================================================
    # QUOTATION STYLE
    # =========================================================================
    double_quote_count, single_quote_count, quotation_style = (
        _detect_quotation_style(text)
    )

    # =========================================================================
    # RHETORICAL QUESTIONS
    # =========================================================================
    rhetorical_question_count = _count_rhetorical_questions(sentences)
    rhetorical_question_density = rhetorical_question_count * sentence_density

    # =========================================================================
    # COMPOSITE FLOURISH SCORE
    # =========================================================================
    flourish_score = _compute_flourish_score(
        alliteration_density=alliteration_density,
        anaphora_density=anaphora_density,
        epistrophe_density=epistrophe_density,
        em_dash_density=em_dash_density,
        ellipsis_density=ellipsis_density,
        rhetorical_question_density=rhetorical_question_density,
    )

    # =========================================================================
    # BUILD RESULT
    # =========================================================================
    metadata: dict[str, Any] = {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "punctuation_counts": {
            "em_dash": em_dash_count,
            "en_dash": en_dash_count,
            "ellipsis": ellipsis_count,
            "double_quote": double_quote_count,
            "single_quote": single_quote_count,
        },
        "serial_comma_analysis": {
            "serial_comma_instances": serial_comma_count,
            "no_serial_comma_instances": no_serial_comma_count,
            "preference": serial_comma_preference,
            "ratio": serial_comma_ratio,
        },
    }

    return StylisticFlourishesResult(
        alliteration_count=alliteration_count,
        alliteration_density=alliteration_density,
        alliteration_examples=alliteration_examples,
        anaphora_count=anaphora_count,
        anaphora_density=anaphora_density,
        anaphora_patterns=anaphora_patterns,
        epistrophe_count=epistrophe_count,
        epistrophe_density=epistrophe_density,
        epistrophe_patterns=epistrophe_patterns,
        em_dash_count=em_dash_count,
        en_dash_count=en_dash_count,
        em_dash_density=em_dash_density,
        en_dash_density=en_dash_density,
        ellipsis_count=ellipsis_count,
        ellipsis_density=ellipsis_density,
        serial_comma_count=serial_comma_count,
        no_serial_comma_count=no_serial_comma_count,
        serial_comma_preference=serial_comma_preference,
        serial_comma_ratio=serial_comma_ratio,
        double_quote_count=double_quote_count,
        single_quote_count=single_quote_count,
        quotation_style=quotation_style,
        rhetorical_question_count=rhetorical_question_count,
        rhetorical_question_density=rhetorical_question_density,
        flourish_score=flourish_score,
        metadata=metadata,
    )
