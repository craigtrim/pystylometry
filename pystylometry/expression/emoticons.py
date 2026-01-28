"""Emoticon and emoji expression analysis for authorship attribution.

This module detects and quantifies expressive elements in text — emoji,
text emoticons, expressive punctuation, emphasis markers, and laughter
expressions — that serve as reliable stylometric fingerprints. These
features are especially powerful in informal writing contexts (social
media, forums, messaging) where authors develop distinctive, habitual
patterns of emotional expression.

Related GitHub Issue:
    #30 - Whonix stylometric features (expressive elements)
    https://github.com/craigtrim/pystylometry/issues/30

Whonix Source:
    The Whonix Stylometry documentation lists "emoticons" and "expressive
    elements" as stylometric features used for deanonymization. The specific
    emoji an author uses, their frequency, and combination patterns form a
    reliable behavioral signature.
    https://www.whonix.org/wiki/Stylometry

Categories of expressive elements analyzed:

    1. Unicode Emoji:
       Detected via Unicode code point ranges. No external library required.
       Emoji are categorized into broad groups (smileys/emotion, people/body,
       animals/nature, food/drink, travel/places, activities, objects,
       symbols, flags) based on Unicode block assignments.

    2. Text Emoticons:
       ASCII art emoticons like :), :(, :D, ;), <3, :/. These predate emoji
       and remain common in certain author demographics and platforms. The
       specific emoticons an author uses are habitual.

    3. Expressive Punctuation:
       Repeated or mixed punctuation that conveys emphasis or emotion:
       multiple exclamation marks (!!!), multiple question marks (???),
       and interrobangs (!? or ?!). Usage frequency is a strong
       stylometric signal.

    4. Emphasis Markers:
       Text formatting used for emphasis: *asterisk emphasis*, _underscore
       emphasis_, and ALL CAPS words. These patterns reflect an author's
       platform habits and emotional expression style.

    5. Laughter Expressions:
       Textual representations of laughter: haha, hehe, lol, lmao, rofl,
       etc. Authors develop strong preferences for specific laughter
       expressions (e.g., consistently using "haha" vs. "lol").

References:
    Grieve, J. (2007). Quantitative authorship attribution: An evaluation
        of techniques. LLC, 22(3), 251-270.
    Stamatatos, E. (2009). A survey of modern authorship attribution
        methods. JASIST, 60(3), 538-556.
    Argamon, S., et al. (2007). Stylistic text classification using
        functional lexical features. JASIST, 58(6), 802-822.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

from .._types import EmoticonResult

# =============================================================================
# EMOJI DETECTION VIA UNICODE RANGES
# =============================================================================
# Emoji are detected by checking whether each character falls within known
# Unicode emoji ranges. This approach avoids requiring the third-party
# `emoji` library. The ranges cover the main emoji blocks defined in
# Unicode 15.0.
#
# Major Unicode emoji blocks:
#   - Emoticons: U+1F600–U+1F64F (smileys, people)
#   - Miscellaneous Symbols and Pictographs: U+1F300–U+1F5FF
#   - Transport and Map Symbols: U+1F680–U+1F6FF
#   - Supplemental Symbols and Pictographs: U+1F900–U+1F9FF
#   - Symbols and Pictographs Extended-A: U+1FA00–U+1FA6F
#   - Symbols and Pictographs Extended-B: U+1FA70–U+1FAFF
#   - Dingbats: U+2702–U+27B0
#   - Misc Symbols: U+2600–U+26FF
#   - Various individual emoji (e.g., U+200D ZWJ, U+FE0F VS16)
#
# We categorize detected emoji into broad groups based on their Unicode
# block for the emoji_categories metric.

# Ranges for emoji detection: (start, end, category_name)
EMOJI_RANGES: list[tuple[int, int, str]] = [
    # Emoticons block: smileys, hand gestures, people
    (0x1F600, 0x1F64F, "smileys_emotion"),
    # Miscellaneous Symbols and Pictographs: weather, plants, food, objects
    (0x1F300, 0x1F5FF, "objects_nature"),
    # Transport and Map Symbols: vehicles, places
    (0x1F680, 0x1F6FF, "travel_places"),
    # Supplemental Symbols: animals, people, food, activities
    (0x1F900, 0x1F9FF, "people_activities"),
    # Extended-A: additional symbols
    (0x1FA00, 0x1FA6F, "symbols"),
    # Extended-B: additional symbols (faces, hands, objects)
    (0x1FA70, 0x1FAFF, "symbols"),
    # Dingbats: arrows, stars, crosses
    (0x2702, 0x27B0, "symbols"),
    # Miscellaneous Symbols: weather, zodiac, chess, playing cards
    (0x2600, 0x26FF, "symbols"),
    # CJK Symbols that are sometimes emoji
    (0x2300, 0x23FF, "symbols"),
    # Enclosed Alphanumeric Supplement
    (0x1F100, 0x1F1FF, "flags"),
]


def _is_emoji(char: str) -> bool:
    """Check if a character is an emoji based on Unicode code point.

    Uses the EMOJI_RANGES table to determine whether a character falls
    within a known emoji Unicode block. This is a conservative check
    that avoids false positives from common symbols like © or ®.

    Args:
        char: A single character to check.

    Returns:
        True if the character is in an emoji Unicode range.
    """
    code_point = ord(char)
    for start, end, _ in EMOJI_RANGES:
        if start <= code_point <= end:
            return True
    return False


def _categorize_emoji(char: str) -> str:
    """Determine the category of an emoji character.

    Maps an emoji character to its broad category based on which Unicode
    block it falls in. Returns "uncategorized" if the character is not
    in any known emoji range (should not happen if _is_emoji was True).

    Args:
        char: A single emoji character.

    Returns:
        Category string (e.g., "smileys_emotion", "objects_nature").
    """
    code_point = ord(char)
    for start, end, category in EMOJI_RANGES:
        if start <= code_point <= end:
            return category
    return "uncategorized"


# =============================================================================
# TEXT EMOTICON PATTERNS
# =============================================================================
# Common ASCII-art emoticons. These are detected via regex patterns.
# The patterns are ordered to avoid substring conflicts (e.g., ":D" must
# not match inside a longer pattern). Each pattern captures the emoticon
# as a group.
#
# Emoticon categories:
#   - Happy: :), :-), :D, :-D, =), =D, :], ^^
#   - Sad: :(, :-(, :[, ='(
#   - Winking: ;), ;-), ;D
#   - Tongue: :P, :-P, :p, :-p, xP
#   - Surprise: :O, :-O, :o, :-o
#   - Neutral/skeptical: :/, :-/, :|, :-|
#   - Heart: <3
#   - Crying: ;(, ;-(, T_T, T.T
#   - Misc: xD, XD, >_<, -_-

TEXT_EMOTICON_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # Happy emoticons — detected with optional nose (-)
    (":)", re.compile(r"(?<![:\w]):\)(?!\w)")),
    (":-)", re.compile(r"(?<![:\w]):-\)(?!\w)")),
    (":D", re.compile(r"(?<![:\w]):D(?!\w)")),
    (":-D", re.compile(r"(?<![:\w]):-D(?!\w)")),
    ("=)", re.compile(r"(?<![=\w])=\)(?!\w)")),
    ("=D", re.compile(r"(?<![=\w])=D(?!\w)")),
    # Sad emoticons
    (":(", re.compile(r"(?<![:\w]):\((?!\w)")),
    (":-(", re.compile(r"(?<![:\w]):-\((?!\w)")),
    # Winking
    (";)", re.compile(r"(?<![;\w]);\)(?!\w)")),
    (";-)", re.compile(r"(?<![;\w]);-\)(?!\w)")),
    # Tongue
    (":P", re.compile(r"(?<![:\w]):[Pp](?!\w)")),
    (":-P", re.compile(r"(?<![:\w]):-[Pp](?!\w)")),
    # Surprise
    (":O", re.compile(r"(?<![:\w]):[Oo](?!\w)")),
    (":-O", re.compile(r"(?<![:\w]):-[Oo](?!\w)")),
    # Neutral / skeptical
    (":/", re.compile(r"(?<![:\w]):/(?!\w)")),
    (":-/", re.compile(r"(?<![:\w]):-/(?!\w)")),
    (":|", re.compile(r"(?<![:\w]):\|(?!\w)")),
    # Heart
    ("<3", re.compile(r"(?<!\w)<3(?!\d)")),
    # Misc expressive
    ("xD", re.compile(r"(?<!\w)[xX]D(?!\w)")),
    (">_<", re.compile(r">_<")),
    ("-_-", re.compile(r"-_-")),
    ("T_T", re.compile(r"T[_.]T")),
    ("^^", re.compile(r"\^\^")),
]

# =============================================================================
# EXPRESSIVE PUNCTUATION PATTERNS
# =============================================================================
# Repeated or mixed punctuation that conveys emphasis or emotion.
# These patterns capture sequences of 2+ identical marks or mixed
# exclamation/question marks.

# Multiple exclamation marks: !! or !!! or !!!!...
MULTI_EXCLAMATION = re.compile(r"!{2,}")

# Multiple question marks: ?? or ??? or ????...
MULTI_QUESTION = re.compile(r"\?{2,}")

# Interrobang: mixed ! and ? in sequence (e.g., "!?", "?!", "?!?", "!?!")
INTERROBANG = re.compile(r"[!?]{2,}")

# =============================================================================
# EMPHASIS MARKERS
# =============================================================================
# Text formatting used for emphasis in plain-text contexts.

# Asterisk emphasis: *word* or *multiple words*
# Must have non-space content between asterisks
ASTERISK_EMPHASIS = re.compile(r"\*([^\s*][^*]*[^\s*]|[^\s*])\*")

# Underscore emphasis: _word_ or _multiple words_
# Must have non-space content between underscores
UNDERSCORE_EMPHASIS = re.compile(r"(?<!\w)_([^\s_][^_]*[^\s_]|[^\s_])_(?!\w)")

# ALL CAPS words: 2+ uppercase letters, excluding common acronyms
# We filter out known acronyms separately; this pattern captures any
# sequence of 2+ uppercase letters bounded by word boundaries.
ALL_CAPS_WORD = re.compile(r"\b([A-Z]{2,})\b")

# Words that commonly appear in all-caps but are not emphasis.
# These are excluded from the caps_emphasis_count.
CAPS_NON_EMPHASIS: set[str] = {
    "I", "A", "OK", "AM", "PM", "AD", "BC", "TV", "ID", "US", "UK",
    "EU", "UN", "AI", "IT", "HR", "PR", "VP", "CEO", "CTO", "CFO",
    "COO", "PhD", "MBA", "USA", "FBI", "CIA", "NASA", "NATO", "HTML",
    "CSS", "HTTP", "HTTPS", "URL", "API", "SQL", "PDF", "FAQ", "DIY",
    "RSVP", "ASAP", "FYI", "TBD", "TBA", "ETA", "GDP", "GPA", "IQ",
    "DNA", "RNA", "HIV", "AIDS", "MRI", "ICU", "CPR", "EMT", "ADHD",
    "PTSD", "OCD", "PhD", "MD", "RN", "LPN",
}

# =============================================================================
# LAUGHTER EXPRESSIONS
# =============================================================================
# Textual representations of laughter. Authors strongly prefer specific
# laughter expressions: someone who uses "lol" rarely switches to "haha"
# in the same text, and vice versa. This makes laughter expression choice
# a reliable stylometric marker.
#
# Patterns use word-boundary matching and case-insensitive flags.

LAUGHTER_PATTERNS: dict[str, re.Pattern[str]] = {
    # "haha" variants: haha, hahaha, hahahaha... (2+ "ha" repetitions)
    "haha": re.compile(r"\b(ha){2,}\b", re.IGNORECASE),
    # "hehe" variants: hehe, hehehe... (2+ "he" repetitions)
    "hehe": re.compile(r"\b(he){2,}\b", re.IGNORECASE),
    # "hihi" variants
    "hihi": re.compile(r"\b(hi){2,}\b", re.IGNORECASE),
    # Internet laughter acronyms
    "lol": re.compile(r"\blol\b", re.IGNORECASE),
    "lmao": re.compile(r"\blmao\b", re.IGNORECASE),
    "lmfao": re.compile(r"\blmfao\b", re.IGNORECASE),
    "rofl": re.compile(r"\brofl\b", re.IGNORECASE),
    "roflmao": re.compile(r"\broflmao\b", re.IGNORECASE),
    # Informal
    "heh": re.compile(r"\bheh\b", re.IGNORECASE),
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _count_emoji(text: str) -> tuple[int, dict[str, int], Counter[str]]:
    """Count and categorize emoji in text.

    Scans each character in the text, checks if it falls within a known
    emoji Unicode range, and tallies counts by category and by individual
    emoji character.

    Args:
        text: Raw input text.

    Returns:
        Tuple of:
            - Total emoji count
            - Category distribution dict (category → count)
            - Counter of individual emoji characters
    """
    categories: dict[str, int] = {}
    individual: Counter[str] = Counter()
    total = 0

    for char in text:
        if _is_emoji(char):
            total += 1
            category = _categorize_emoji(char)
            categories[category] = categories.get(category, 0) + 1
            individual[char] += 1

    return total, categories, individual


def _count_text_emoticons(text: str) -> dict[str, int]:
    """Count text emoticons in text.

    Applies each emoticon regex pattern to the text and tallies matches.
    Only emoticons with at least one occurrence are included in the result.

    Args:
        text: Raw input text.

    Returns:
        Dict mapping emoticon strings to their occurrence counts.
    """
    counts: dict[str, int] = {}
    for emoticon, pattern in TEXT_EMOTICON_PATTERNS:
        count = len(pattern.findall(text))
        if count > 0:
            # Merge similar emoticons (e.g., :-) and :) both count as ":)")
            # by using the canonical short form as the key
            canonical = emoticon.replace("-", "") if "-" in emoticon else emoticon
            counts[canonical] = counts.get(canonical, 0) + count
    return counts


def _count_expressive_punctuation(
    text: str,
) -> tuple[int, int, int]:
    """Count expressive punctuation patterns.

    Detects three types of expressive punctuation:
    - Multiple exclamation marks (!! or more)
    - Multiple question marks (?? or more)
    - Interrobangs (mixed !? sequences)

    To avoid double-counting, interrobangs are counted from mixed-mark
    sequences only (sequences containing both ! and ?). Pure !! or ??
    sequences are counted separately.

    Args:
        text: Raw input text.

    Returns:
        Tuple of (multi_exclamation, multi_question, interrobang) counts.
    """
    # Find all sequences of 2+ punctuation marks that are ! or ?
    all_sequences = INTERROBANG.findall(text)

    multi_excl = 0
    multi_ques = 0
    interrobang = 0

    for seq in all_sequences:
        has_excl = "!" in seq
        has_ques = "?" in seq

        if has_excl and has_ques:
            # Mixed sequence: count as interrobang
            interrobang += 1
        elif has_excl:
            # Pure exclamation sequence
            multi_excl += 1
        elif has_ques:
            # Pure question sequence
            multi_ques += 1

    return multi_excl, multi_ques, interrobang


def _count_emphasis(text: str) -> tuple[int, int, int]:
    """Count emphasis markers in text.

    Detects three types of emphasis:
    - ALL CAPS words (excluding known acronyms and short words)
    - *asterisk emphasis* patterns
    - _underscore emphasis_ patterns

    Args:
        text: Raw input text.

    Returns:
        Tuple of (caps_count, asterisk_count, underscore_count).
    """
    # ALL CAPS words (excluding known non-emphasis caps)
    caps_count = 0
    for match in ALL_CAPS_WORD.finditer(text):
        word = match.group(1)
        if word not in CAPS_NON_EMPHASIS and len(word) >= 2:
            caps_count += 1

    # Asterisk emphasis
    asterisk_count = len(ASTERISK_EMPHASIS.findall(text))

    # Underscore emphasis
    underscore_count = len(UNDERSCORE_EMPHASIS.findall(text))

    return caps_count, asterisk_count, underscore_count


def _count_laughter(text: str) -> dict[str, int]:
    """Count laughter expressions in text.

    Applies each laughter regex pattern to the text. Only expressions
    with at least one occurrence are included.

    Args:
        text: Raw input text.

    Returns:
        Dict mapping laughter expression type to occurrence count.
    """
    counts: dict[str, int] = {}
    for laughter_type, pattern in LAUGHTER_PATTERNS.items():
        count = len(pattern.findall(text))
        if count > 0:
            counts[laughter_type] = count
    return counts


def _compute_expressiveness_score(
    emoji_density: float,
    text_emoticon_density: float,
    expressive_punct_density: float,
    emphasis_density: float,
    laughter_density: float,
) -> float:
    """Compute a composite expressiveness score.

    The expressiveness score is a weighted combination of all expressive
    element signals, scaled to a 0.0-1.0 range where 0.0 indicates
    completely neutral text and 1.0 indicates highly expressive text.

    Weighting rationale:
        - Emoji density (0.30): Strongest single expressiveness signal in
          modern text. High frequency is a clear marker of expressive style.
        - Text emoticon density (0.20): Slightly lower weight than emoji
          because emoticons are less visually distinctive and more ambiguous
          (e.g., ":)" in code contexts).
        - Expressive punctuation (0.20): Strong signal. Authors who use "!!!"
          and "???" do so habitually.
        - Emphasis markers (0.15): Moderate signal. ALL CAPS and *emphasis*
          are platform-specific habits.
        - Laughter expressions (0.15): Strong stylistic marker but less
          common overall, so weighted slightly lower.

    Each component is capped at a saturation point before weighting to
    prevent any single extreme value from dominating the score.

    Args:
        emoji_density: Emoji per 100 words.
        text_emoticon_density: Text emoticons per 100 words.
        expressive_punct_density: Expressive punctuation per 100 words.
        emphasis_density: Emphasis markers per 100 words.
        laughter_density: Laughter expressions per 100 words.

    Returns:
        Expressiveness score between 0.0 and 1.0.
    """
    # Cap each density at its saturation point, then normalize to 0-1
    emoji_component = min(emoji_density / 5.0, 1.0) * 0.30
    emoticon_component = min(text_emoticon_density / 3.0, 1.0) * 0.20
    punct_component = min(expressive_punct_density / 3.0, 1.0) * 0.20
    emphasis_component = min(emphasis_density / 3.0, 1.0) * 0.15
    laughter_component = min(laughter_density / 2.0, 1.0) * 0.15

    raw_score = (
        emoji_component
        + emoticon_component
        + punct_component
        + emphasis_component
        + laughter_component
    )

    return max(0.0, min(1.0, raw_score))


# =============================================================================
# MAIN FUNCTION
# =============================================================================


def compute_emoticons(text: str) -> EmoticonResult:
    """Analyze emoticon and emoji expression patterns for authorship attribution.

    Detects and quantifies expressive elements across five categories: emoji,
    text emoticons, expressive punctuation, emphasis markers, and laughter
    expressions. Computes a composite expressiveness score based on the
    weighted combination of these signals.

    Related GitHub Issue:
        #30 - Whonix stylometric features (expressive elements)
        https://github.com/craigtrim/pystylometry/issues/30

    Whonix Source:
        The Whonix Stylometry documentation lists "emoticons" and "expressive
        elements" as stylometric features used for deanonymization:
        https://www.whonix.org/wiki/Stylometry

    Algorithm:
        1. Count words for density calculations
        2. Scan text for Unicode emoji (via code point ranges)
        3. Detect text emoticons via regex patterns
        4. Count expressive punctuation (!!!, ???, !?)
        5. Count emphasis markers (*bold*, _italic_, ALL CAPS)
        6. Count laughter expressions (haha, lol, lmao, etc.)
        7. Compute composite expressiveness score from weighted components

    Args:
        text: Input text to analyze. Works with any length, but very short
              texts (< 20 words) may produce unreliable density values.

    Returns:
        EmoticonResult with counts, densities, and composite expressiveness
        score. See _types.py for complete field list.

    Example:
        >>> result = compute_emoticons("Great job!!! :D I'm so happy 🎉🎉")
        >>> print(f"Emoji: {result.emoji_count}")
        >>> print(f"Emoticons: {result.text_emoticon_count}")
        >>> print(f"Expressiveness: {result.expressiveness_score:.2f}")

    Note:
        - Emoji detection uses Unicode ranges (no external library needed)
        - Densities are per 100 words for interpretability
        - ALL CAPS detection excludes known acronyms (NASA, FBI, etc.)
        - Emoticon detection uses conservative regex to reduce false positives
        - Empty text returns zero counts and 0.0 for all metrics
    """
    # Handle empty text edge case
    if not text or not text.strip():
        return EmoticonResult(
            emoji_count=0,
            emoji_density=0.0,
            emoji_categories={},
            top_emoji=[],
            text_emoticon_count=0,
            text_emoticon_density=0.0,
            text_emoticons={},
            multiple_exclamation_count=0,
            multiple_question_count=0,
            interrobang_count=0,
            expressive_punctuation_density=0.0,
            caps_emphasis_count=0,
            asterisk_emphasis_count=0,
            underscore_emphasis_count=0,
            emphasis_density=0.0,
            laughter_count=0,
            laughter_density=0.0,
            laughter_types={},
            expressiveness_score=0.0,
            metadata={"word_count": 0, "warning": "Empty text"},
        )

    # Word count for density calculations
    words = text.split()
    word_count = len(words)

    # Guard against zero-word edge case
    if word_count == 0:
        return EmoticonResult(
            emoji_count=0,
            emoji_density=0.0,
            emoji_categories={},
            top_emoji=[],
            text_emoticon_count=0,
            text_emoticon_density=0.0,
            text_emoticons={},
            multiple_exclamation_count=0,
            multiple_question_count=0,
            interrobang_count=0,
            expressive_punctuation_density=0.0,
            caps_emphasis_count=0,
            asterisk_emphasis_count=0,
            underscore_emphasis_count=0,
            emphasis_density=0.0,
            laughter_count=0,
            laughter_density=0.0,
            laughter_types={},
            expressiveness_score=0.0,
            metadata={"word_count": 0, "warning": "No words found"},
        )

    # Density multiplier: converts raw counts to per-100-words
    density_multiplier = 100.0 / word_count

    # =========================================================================
    # EMOJI
    # =========================================================================
    emoji_count, emoji_categories, emoji_counter = _count_emoji(text)
    emoji_density = emoji_count * density_multiplier
    top_emoji = emoji_counter.most_common(10)

    # =========================================================================
    # TEXT EMOTICONS
    # =========================================================================
    text_emoticons = _count_text_emoticons(text)
    text_emoticon_count = sum(text_emoticons.values())
    text_emoticon_density = text_emoticon_count * density_multiplier

    # =========================================================================
    # EXPRESSIVE PUNCTUATION
    # =========================================================================
    multi_excl, multi_ques, interrobang = _count_expressive_punctuation(text)
    total_expressive_punct = multi_excl + multi_ques + interrobang
    expressive_punctuation_density = total_expressive_punct * density_multiplier

    # =========================================================================
    # EMPHASIS MARKERS
    # =========================================================================
    caps_count, asterisk_count, underscore_count = _count_emphasis(text)
    total_emphasis = caps_count + asterisk_count + underscore_count
    emphasis_density = total_emphasis * density_multiplier

    # =========================================================================
    # LAUGHTER EXPRESSIONS
    # =========================================================================
    laughter_types = _count_laughter(text)
    laughter_count = sum(laughter_types.values())
    laughter_density = laughter_count * density_multiplier

    # =========================================================================
    # COMPOSITE EXPRESSIVENESS SCORE
    # =========================================================================
    expressiveness_score = _compute_expressiveness_score(
        emoji_density=emoji_density,
        text_emoticon_density=text_emoticon_density,
        expressive_punct_density=expressive_punctuation_density,
        emphasis_density=emphasis_density,
        laughter_density=laughter_density,
    )

    # =========================================================================
    # BUILD RESULT
    # =========================================================================
    metadata: dict[str, Any] = {
        "word_count": word_count,
        "total_expressive_elements": (
            emoji_count
            + text_emoticon_count
            + total_expressive_punct
            + total_emphasis
            + laughter_count
        ),
        "all_emoji_counts": dict(emoji_counter),
        "all_emoticon_counts": text_emoticons,
        "all_laughter_counts": laughter_types,
        "expressive_punctuation_breakdown": {
            "multiple_exclamation": multi_excl,
            "multiple_question": multi_ques,
            "interrobang": interrobang,
        },
        "emphasis_breakdown": {
            "all_caps": caps_count,
            "asterisk": asterisk_count,
            "underscore": underscore_count,
        },
    }

    return EmoticonResult(
        emoji_count=emoji_count,
        emoji_density=emoji_density,
        emoji_categories=emoji_categories,
        top_emoji=top_emoji,
        text_emoticon_count=text_emoticon_count,
        text_emoticon_density=text_emoticon_density,
        text_emoticons=text_emoticons,
        multiple_exclamation_count=multi_excl,
        multiple_question_count=multi_ques,
        interrobang_count=interrobang,
        expressive_punctuation_density=expressive_punctuation_density,
        caps_emphasis_count=caps_count,
        asterisk_emphasis_count=asterisk_count,
        underscore_emphasis_count=underscore_count,
        emphasis_density=emphasis_density,
        laughter_count=laughter_count,
        laughter_density=laughter_density,
        laughter_types=laughter_types,
        expressiveness_score=expressiveness_score,
        metadata=metadata,
    )
