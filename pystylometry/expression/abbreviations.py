"""Abbreviation pattern analysis for authorship attribution.

This module detects and quantifies abbreviation usage patterns that serve as
reliable stylometric fingerprints. Authors develop habitual preferences for
contracted vs. expanded forms, acronym formatting conventions, and shorthand
usage that persist across topics and are difficult to consciously alter.

Related GitHub Issue:
    #30 - Whonix stylometric features (abbreviation analysis)
    https://github.com/craigtrim/pystylometry/issues/30

Whonix Source:
    The Whonix Stylometry documentation identifies abbreviation patterns as
    a key deanonymization vector:
    https://www.whonix.org/wiki/Stylometry

Categories of abbreviation patterns analyzed:

    1. Contractions:
       Preference for contracted vs. expanded forms (can't vs. cannot,
       I'm vs. I am). Contraction ratio is a strong formality indicator
       and remains stable within an author's writing style.

    2. Acronyms:
       Frequency and formatting style of acronyms. Some authors prefer
       periods between letters (U.S.A.), others omit them (USA), and
       some use lowercase with periods (u.s.a.). The formatting choice
       is a stylistic habit.

    3. Latin Abbreviations:
       Usage of scholarly Latin abbreviations (etc., e.g., i.e., vs.,
       viz., cf., et al., approx., ca.). Frequency varies significantly
       between academic and informal writing, and between authors within
       the same register.

    4. Informal Shortenings:
       Clipped forms of words (info, intro, photo, phone, exam, lab,
       memo, deli). These indicate register awareness and habitual
       vocabulary choices.

    5. Text-Speak Patterns:
       Internet-era abbreviations (u, ur, thx, pls, bc, btw, imo, tbh).
       Presence and frequency are strong generational and stylistic markers.

    6. Title Abbreviations:
       Abbreviated titles (Mr., Dr., Prof., Mrs., Ms., Jr., Sr.) vs.
       full forms (Mister, Doctor, Professor). Convention choice reflects
       formality habits.

References:
    Argamon, S., et al. (2007). Stylistic text classification using
        functional lexical features. JASIST, 58(6), 802-822.
    Koppel, M., Schler, J., & Argamon, S. (2009). Computational methods
        in authorship attribution. JASIST, 60(1), 9-26.
    Pennebaker, J. W. (2011). The secret life of pronouns. Bloomsbury Press.
    Biber, D. (1988). Variation across speech and writing. Cambridge
        University Press.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

from .._types import AbbreviationResult

# =============================================================================
# CONTRACTION DATA
# =============================================================================
# Map of contractions to their expanded forms. Used both for contraction
# detection and for counting "missed opportunities" (expanded forms that
# could have been contracted). This is intentionally self-contained rather
# than importing from stylistic/markers.py to keep the expression subpackage
# independent and to allow for future divergence in contraction coverage.

CONTRACTIONS: dict[str, str] = {
    # Negative contractions — the most common contraction category.
    # These are strong formality markers: formal writing avoids them,
    # informal writing uses them almost exclusively.
    "aren't": "are not",
    "can't": "cannot",
    "couldn't": "could not",
    "didn't": "did not",
    "doesn't": "does not",
    "don't": "do not",
    "hadn't": "had not",
    "hasn't": "has not",
    "haven't": "have not",
    "isn't": "is not",
    "mightn't": "might not",
    "mustn't": "must not",
    "needn't": "need not",
    "shan't": "shall not",
    "shouldn't": "should not",
    "wasn't": "was not",
    "weren't": "were not",
    "won't": "will not",
    "wouldn't": "would not",
    # Pronoun contractions — frequency varies significantly by author.
    # Some authors habitually use "I'm" while others write "I am".
    "i'm": "i am",
    "i've": "i have",
    "i'll": "i will",
    "i'd": "i would",
    "you're": "you are",
    "you've": "you have",
    "you'll": "you will",
    "you'd": "you would",
    "he's": "he is",
    "he'll": "he will",
    "he'd": "he would",
    "she's": "she is",
    "she'll": "she will",
    "she'd": "she would",
    "it's": "it is",
    "it'll": "it will",
    "it'd": "it would",
    "we're": "we are",
    "we've": "we have",
    "we'll": "we will",
    "we'd": "we would",
    "they're": "they are",
    "they've": "they have",
    "they'll": "they will",
    "they'd": "they would",
    "that's": "that is",
    "who's": "who is",
    "what's": "what is",
    "where's": "where is",
    "there's": "there is",
    "here's": "here is",
    # Other contractions
    "let's": "let us",
    "ain't": "am not",
}

# =============================================================================
# EXPANDED FORM PATTERNS
# =============================================================================
# Regex patterns for detecting expanded forms that could have been contracted.
# Each tuple is (compiled_pattern, equivalent_contraction).
# These allow us to compute the contraction ratio: how often an author
# chooses the contracted form when the expanded form was available.

EXPANDED_FORM_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b(are)\s+(not)\b", re.IGNORECASE), "aren't"),
    (re.compile(r"\b(can)\s*(?:not)\b", re.IGNORECASE), "can't"),
    (re.compile(r"\b(could)\s+(not)\b", re.IGNORECASE), "couldn't"),
    (re.compile(r"\b(did)\s+(not)\b", re.IGNORECASE), "didn't"),
    (re.compile(r"\b(does)\s+(not)\b", re.IGNORECASE), "doesn't"),
    (re.compile(r"\b(do)\s+(not)\b", re.IGNORECASE), "don't"),
    (re.compile(r"\b(had)\s+(not)\b", re.IGNORECASE), "hadn't"),
    (re.compile(r"\b(has)\s+(not)\b", re.IGNORECASE), "hasn't"),
    (re.compile(r"\b(have)\s+(not)\b", re.IGNORECASE), "haven't"),
    (re.compile(r"\b(is)\s+(not)\b", re.IGNORECASE), "isn't"),
    (re.compile(r"\b(should)\s+(not)\b", re.IGNORECASE), "shouldn't"),
    (re.compile(r"\b(was)\s+(not)\b", re.IGNORECASE), "wasn't"),
    (re.compile(r"\b(were)\s+(not)\b", re.IGNORECASE), "weren't"),
    (re.compile(r"\b(will)\s+(not)\b", re.IGNORECASE), "won't"),
    (re.compile(r"\b(would)\s+(not)\b", re.IGNORECASE), "wouldn't"),
    (re.compile(r"\b(i)\s+(am)\b", re.IGNORECASE), "i'm"),
    (re.compile(r"\b(i)\s+(have)\b", re.IGNORECASE), "i've"),
    (re.compile(r"\b(i)\s+(will)\b", re.IGNORECASE), "i'll"),
    (re.compile(r"\b(i)\s+(would)\b", re.IGNORECASE), "i'd"),
    (re.compile(r"\b(you)\s+(are)\b", re.IGNORECASE), "you're"),
    (re.compile(r"\b(we)\s+(are)\b", re.IGNORECASE), "we're"),
    (re.compile(r"\b(they)\s+(are)\b", re.IGNORECASE), "they're"),
    (re.compile(r"\b(let)\s+(us)\b", re.IGNORECASE), "let's"),
]

# =============================================================================
# ACRONYM PATTERNS
# =============================================================================
# Acronyms are detected via regex. We distinguish between:
#   - No-period style: "NASA", "FBI", "CEO" (2+ uppercase letters)
#   - Period style: "U.S.A.", "N.A.S.A." (letter-dot sequences)
# Single uppercase letters (I, A) are excluded to avoid false positives.
# Common all-caps words that are not acronyms are also excluded.

# Words that appear in all-caps but are NOT acronyms. This list prevents
# false positives from emphasis-caps and common short words.
CAPS_EXCLUSIONS: set[str] = {
    "I", "A", "OK", "AM", "PM", "AN", "AS", "AT", "BE", "BY", "DO",
    "GO", "HE", "IF", "IN", "IS", "IT", "ME", "MY", "NO", "OF", "ON",
    "OR", "SO", "TO", "UP", "US", "WE",
}

# Pattern for no-period acronyms: 2+ consecutive uppercase letters
# bounded by word boundaries. Example: "NASA", "FBI"
ACRONYM_NO_PERIOD = re.compile(r"\b([A-Z]{2,})\b")

# Pattern for period-style acronyms: letter-dot sequences of 2+ letters.
# Example: "U.S.A.", "N.A.T.O."
ACRONYM_WITH_PERIOD = re.compile(r"\b([A-Z]\.){2,}")

# =============================================================================
# LATIN ABBREVIATIONS
# =============================================================================
# Scholarly Latin abbreviations common in academic and formal writing.
# These are matched case-insensitively with word boundary checks.
# The frequency of Latin abbreviations is a strong register marker —
# academic writers use them far more than informal writers.

LATIN_ABBREVIATIONS: dict[str, re.Pattern[str]] = {
    # Note: We omit the trailing \b because \b does not match at the
    # boundary between a period (non-word char) and a space or comma
    # (also non-word char). The leading \b is sufficient to prevent
    # mid-word false positives.
    "etc.": re.compile(r"\betc\.", re.IGNORECASE),
    "e.g.": re.compile(r"\be\.g\.", re.IGNORECASE),
    "i.e.": re.compile(r"\bi\.e\.", re.IGNORECASE),
    "vs.": re.compile(r"\bvs\.", re.IGNORECASE),
    "viz.": re.compile(r"\bviz\.", re.IGNORECASE),
    "cf.": re.compile(r"\bcf\.", re.IGNORECASE),
    "et al.": re.compile(r"\bet\s+al\.", re.IGNORECASE),
    "approx.": re.compile(r"\bapprox\.", re.IGNORECASE),
    "ca.": re.compile(r"\bca\.", re.IGNORECASE),
    "ibid.": re.compile(r"\bibid\.", re.IGNORECASE),
    "op. cit.": re.compile(r"\bop\.\s*cit\.", re.IGNORECASE),
    "loc. cit.": re.compile(r"\bloc\.\s*cit\.", re.IGNORECASE),
    "N.B.": re.compile(r"\bN\.B\."),
    "P.S.": re.compile(r"\bP\.S\."),
}

# =============================================================================
# INFORMAL SHORTENINGS
# =============================================================================
# Clipped forms of common words. These are vocabulary-level abbreviations
# where a longer word has been informally shortened. Their presence indicates
# informal register, and specific choices (e.g., "info" vs. "information")
# are habitual authorial preferences.
#
# Each entry maps the shortened form to the full word for reference.

INFORMAL_SHORTENINGS: dict[str, str] = {
    "info": "information",
    "intro": "introduction",
    "photo": "photograph",
    "phone": "telephone",
    "exam": "examination",
    "lab": "laboratory",
    "memo": "memorandum",
    "deli": "delicatessen",
    "demo": "demonstration",
    "auto": "automobile",
    "bio": "biography",
    "chem": "chemistry",
    "diff": "difference",
    "doc": "document",
    "fridge": "refrigerator",
    "gym": "gymnasium",
    "limo": "limousine",
    "math": "mathematics",
    "max": "maximum",
    "min": "minimum",
    "ref": "reference",
    "rep": "representative",
    "temp": "temperature",
    "vet": "veterinarian",
    "vocab": "vocabulary",
}

# =============================================================================
# TEXT-SPEAK PATTERNS
# =============================================================================
# Internet-era abbreviations and text-speak. Presence and frequency of
# these tokens are strong generational and register markers. Authors who
# use text-speak in one context tend to use it consistently.
#
# Each entry maps the text-speak form to its expanded meaning.

TEXT_SPEAK: dict[str, str] = {
    "u": "you",
    "ur": "your/you're",
    "r": "are",
    "thx": "thanks",
    "thnx": "thanks",
    "pls": "please",
    "plz": "please",
    "bc": "because",
    "b4": "before",
    "btw": "by the way",
    "imo": "in my opinion",
    "imho": "in my humble opinion",
    "tbh": "to be honest",
    "idk": "I don't know",
    "iirc": "if I recall correctly",
    "afaik": "as far as I know",
    "fyi": "for your information",
    "brb": "be right back",
    "omg": "oh my god",
    "smh": "shaking my head",
    "nvm": "never mind",
    "ty": "thank you",
    "np": "no problem",
    "rn": "right now",
    "fr": "for real",
    "w/": "with",
    "w/o": "without",
}

# =============================================================================
# TITLE ABBREVIATIONS
# =============================================================================
# Abbreviated titles and their full forms. The choice between abbreviated
# and full title forms (Mr. vs. Mister, Dr. vs. Doctor) is a stylistic
# habit that reflects formality preferences and regional conventions.
#
# Patterns use word-boundary matching to avoid false positives within
# longer words. The period after the abbreviation is required to
# distinguish "Dr." from the word "Dr" used in other contexts.

TITLE_ABBREVIATIONS: dict[str, re.Pattern[str]] = {
    # Note: Trailing \b is omitted because \b does not match at the
    # boundary between a period and a space (both are non-word chars).
    "Mr.": re.compile(r"\bMr\."),
    "Mrs.": re.compile(r"\bMrs\."),
    "Ms.": re.compile(r"\bMs\."),
    "Dr.": re.compile(r"\bDr\."),
    "Prof.": re.compile(r"\bProf\."),
    "Jr.": re.compile(r"\bJr\."),
    "Sr.": re.compile(r"\bSr\."),
    "St.": re.compile(r"\bSt\."),
    "Rev.": re.compile(r"\bRev\."),
    "Gen.": re.compile(r"\bGen\."),
    "Sgt.": re.compile(r"\bSgt\."),
    "Capt.": re.compile(r"\bCapt\."),
    "Lt.": re.compile(r"\bLt\."),
    "Col.": re.compile(r"\bCol\."),
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _tokenize(text: str) -> list[str]:
    """Simple word tokenization preserving contractions.

    Splits text into tokens on whitespace and punctuation boundaries while
    keeping apostrophe-containing words (contractions) as single tokens.
    All tokens are lowercased for consistent matching.

    Args:
        text: Raw input text.

    Returns:
        List of lowercase tokens.
    """
    # Normalize curly apostrophes to straight apostrophes
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    # Match word characters and apostrophes as tokens
    return re.findall(r"\b[\w']+\b", text.lower())


def _count_contractions(text: str) -> tuple[Counter[str], int]:
    """Count contractions and their expandable counterparts in text.

    Scans for both contracted forms (don't, can't) and expanded forms
    (do not, cannot) to enable computation of the contraction ratio.

    Args:
        text: Raw input text.

    Returns:
        Tuple of:
            - Counter of contraction occurrences
            - Count of expanded forms that could have been contracted
    """
    # Normalize curly apostrophes for consistent matching
    text_normalized = text.replace("\u2019", "'").replace("\u2018", "'")
    text_lower = text_normalized.lower()

    contraction_counts: Counter[str] = Counter()

    # Count each known contraction using word-boundary regex
    for contraction in CONTRACTIONS:
        pattern = r"\b" + re.escape(contraction) + r"\b"
        matches = re.findall(pattern, text_lower)
        if matches:
            contraction_counts[contraction] = len(matches)

    # Count expanded forms (opportunities where contraction was not used)
    expanded_count = 0
    for pattern, _ in EXPANDED_FORM_PATTERNS:
        matches = pattern.findall(text_lower)
        expanded_count += len(matches)

    return contraction_counts, expanded_count


def _detect_acronyms(text: str) -> tuple[Counter[str], str]:
    """Detect acronyms and classify their formatting style.

    Identifies both no-period (NASA, FBI) and period-style (U.S.A., N.A.T.O.)
    acronyms. Classifies the dominant formatting style based on which pattern
    appears more frequently.

    Args:
        text: Raw input text.

    Returns:
        Tuple of:
            - Counter of acronym occurrences
            - Style classification: "no_periods", "with_periods", "mixed", or "none"
    """
    acronym_counts: Counter[str] = Counter()

    no_period_count = 0
    period_count = 0

    # Detect no-period acronyms (e.g., "NASA", "FBI")
    for match in ACRONYM_NO_PERIOD.finditer(text):
        candidate = match.group(1)
        # Exclude common all-caps words that aren't acronyms
        if candidate not in CAPS_EXCLUSIONS:
            acronym_counts[candidate] += 1
            no_period_count += 1

    # Detect period-style acronyms (e.g., "U.S.A.", "N.A.T.O.")
    for match in ACRONYM_WITH_PERIOD.finditer(text):
        candidate = match.group(0)
        acronym_counts[candidate] += 1
        period_count += 1

    # Classify the dominant acronym style
    if no_period_count == 0 and period_count == 0:
        style = "none"
    elif period_count == 0:
        style = "no_periods"
    elif no_period_count == 0:
        style = "with_periods"
    else:
        style = "mixed"

    return acronym_counts, style


def _count_latin_abbreviations(text: str) -> dict[str, int]:
    """Count Latin abbreviations in text.

    Scans for scholarly Latin abbreviations (etc., e.g., i.e., vs., etc.)
    using pre-compiled regex patterns with word-boundary matching.

    Args:
        text: Raw input text.

    Returns:
        Dict mapping each Latin abbreviation to its occurrence count.
        Only abbreviations with count > 0 are included.
    """
    counts: dict[str, int] = {}
    for abbrev, pattern in LATIN_ABBREVIATIONS.items():
        count = len(pattern.findall(text))
        if count > 0:
            counts[abbrev] = count
    return counts


def _count_text_speak(tokens: list[str]) -> Counter[str]:
    """Count text-speak tokens.

    Matches lowercased tokens against the known text-speak vocabulary.
    Only exact matches are counted to avoid false positives (e.g., "u"
    appearing as part of a sentence fragment).

    Note: Single-letter text-speak ("u", "r") can produce false positives
    in certain contexts. The informality_score weighting accounts for this
    by giving less weight to single-letter matches.

    Args:
        tokens: List of lowercased tokens from _tokenize().

    Returns:
        Counter of text-speak token occurrences.
    """
    counts: Counter[str] = Counter()
    for token in tokens:
        if token in TEXT_SPEAK:
            counts[token] += 1
    return counts


def _count_title_abbreviations(text: str) -> dict[str, int]:
    """Count title abbreviations in text.

    Scans for abbreviated titles (Mr., Dr., Prof., etc.) using
    pre-compiled regex patterns.

    Args:
        text: Raw input text.

    Returns:
        Dict mapping each title abbreviation to its occurrence count.
        Only abbreviations with count > 0 are included.
    """
    counts: dict[str, int] = {}
    for title, pattern in TITLE_ABBREVIATIONS.items():
        count = len(pattern.findall(text))
        if count > 0:
            counts[title] = count
    return counts


def _compute_informality_score(
    contraction_ratio: float,
    text_speak_density: float,
    informal_shortening_density: float,
    latin_abbreviation_density: float,
) -> float:
    """Compute a composite informality score from abbreviation patterns.

    The informality score is a weighted combination of multiple abbreviation
    signals, scaled to a 0.0-1.0 range where 0.0 indicates highly formal
    writing and 1.0 indicates highly informal writing.

    Weighting rationale:
        - Contraction ratio (0.35): Strongest single formality indicator.
          Formal writing avoids contractions almost entirely; informal writing
          uses them freely. Well-established in the Biber (1988) dimension
          framework as a primary formality marker.
        - Text-speak density (0.35): Very strong informality signal. Presence
          of any text-speak tokens strongly indicates informal register.
          Weighted equally with contractions because it is equally distinctive.
        - Informal shortenings (0.15): Moderate signal. Words like "info" and
          "phone" appear in semi-formal contexts, so they receive less weight.
        - Latin abbreviation density (0.15): Negative signal (reduces score).
          Latin abbreviations correlate with formal/academic register, so
          their presence counterbalances informality signals.

    The result is clamped to [0.0, 1.0].

    Args:
        contraction_ratio: Fraction of contraction opportunities used (0-1).
        text_speak_density: Text-speak tokens per 100 words.
        informal_shortening_density: Informal shortenings per 100 words.
        latin_abbreviation_density: Latin abbreviations per 100 words.

    Returns:
        Informality score between 0.0 (formal) and 1.0 (informal).
    """
    # Contraction ratio is already on a 0-1 scale
    contraction_component = contraction_ratio * 0.35

    # Text-speak density: cap at 5.0 per 100 words (saturation point),
    # then normalize to 0-1 range before applying weight
    text_speak_component = min(text_speak_density / 5.0, 1.0) * 0.35

    # Informal shortening density: cap at 3.0 per 100 words
    shortening_component = min(informal_shortening_density / 3.0, 1.0) * 0.15

    # Latin abbreviations: negative contribution (formality signal)
    # Cap at 2.0 per 100 words
    latin_component = min(latin_abbreviation_density / 2.0, 1.0) * 0.15

    # Combine components. Latin abbreviations reduce informality.
    raw_score = (
        contraction_component
        + text_speak_component
        + shortening_component
        - latin_component
    )

    # Clamp to [0.0, 1.0]
    return max(0.0, min(1.0, raw_score))


# =============================================================================
# MAIN FUNCTION
# =============================================================================


def compute_abbreviations(text: str) -> AbbreviationResult:
    """Analyze abbreviation patterns for authorship attribution.

    Detects and quantifies abbreviation usage patterns across six categories:
    contractions, acronyms, Latin abbreviations, informal shortenings,
    text-speak, and title abbreviations. Computes a composite informality
    score based on the weighted combination of these signals.

    Related GitHub Issue:
        #30 - Whonix stylometric features (abbreviation analysis)
        https://github.com/craigtrim/pystylometry/issues/30

    Whonix Source:
        The Whonix Stylometry documentation identifies abbreviation patterns
        as a key deanonymization vector:
        https://www.whonix.org/wiki/Stylometry

    Algorithm:
        1. Tokenize text (preserving contractions as single tokens)
        2. Count contractions and their expandable counterparts
        3. Detect acronyms and classify formatting style
        4. Count Latin abbreviations via regex
        5. Count informal shortenings via token matching
        6. Count text-speak patterns via token matching
        7. Count title abbreviations via regex
        8. Compute composite informality score from weighted components

    Args:
        text: Input text to analyze. Should contain at least 100+ words
              for meaningful statistics. Shorter texts may produce
              unstable ratios.

    Returns:
        AbbreviationResult with abbreviation counts, densities, and
        composite informality score. See _types.py for complete field list.

    Example:
        >>> result = compute_abbreviations(
        ...     "I can't believe Dr. Smith didn't mention the info "
        ...     "about NASA's findings, e.g., the atmospheric data."
        ... )
        >>> print(f"Contraction ratio: {result.contraction_ratio:.2f}")
        >>> print(f"Acronym style: {result.acronym_style}")
        >>> print(f"Latin abbreviations: {result.latin_abbreviation_count}")
        >>> print(f"Informality score: {result.informality_score:.2f}")

    Note:
        - Densities are computed per 100 words for interpretability
        - Single-letter text-speak ("u", "r") may produce false positives
          in certain contexts; the informality score weighting accounts
          for this by capping text-speak contribution
        - Acronym detection excludes common all-caps words (I, A, OK, etc.)
        - Empty text returns zero counts and 0.0 for all ratios
    """
    # Handle empty text edge case
    if not text or not text.strip():
        return AbbreviationResult(
            contraction_ratio=0.0,
            contraction_count=0,
            expanded_form_count=0,
            top_contractions=[],
            acronym_count=0,
            acronym_style="none",
            top_acronyms=[],
            latin_abbreviation_count=0,
            latin_abbreviation_density=0.0,
            latin_abbreviations={},
            informal_shortening_count=0,
            informal_shortening_density=0.0,
            top_informal_shortenings=[],
            text_speak_count=0,
            text_speak_density=0.0,
            top_text_speak=[],
            title_abbreviation_count=0,
            title_abbreviation_density=0.0,
            title_abbreviations={},
            informality_score=0.0,
            metadata={"word_count": 0, "warning": "Empty text"},
        )

    # Tokenize for word-level matching
    tokens = _tokenize(text)
    word_count = len(tokens)

    # Guard against zero-word edge case (e.g., text is only punctuation)
    if word_count == 0:
        return AbbreviationResult(
            contraction_ratio=0.0,
            contraction_count=0,
            expanded_form_count=0,
            top_contractions=[],
            acronym_count=0,
            acronym_style="none",
            top_acronyms=[],
            latin_abbreviation_count=0,
            latin_abbreviation_density=0.0,
            latin_abbreviations={},
            informal_shortening_count=0,
            informal_shortening_density=0.0,
            top_informal_shortenings=[],
            text_speak_count=0,
            text_speak_density=0.0,
            top_text_speak=[],
            title_abbreviation_count=0,
            title_abbreviation_density=0.0,
            title_abbreviations={},
            informality_score=0.0,
            metadata={"word_count": 0, "warning": "No tokens found"},
        )

    # Density multiplier: converts raw counts to per-100-words
    density_multiplier = 100.0 / word_count

    # =========================================================================
    # CONTRACTIONS
    # =========================================================================
    contraction_counts, expanded_form_count = _count_contractions(text)
    contraction_count = sum(contraction_counts.values())
    # Contraction ratio: what fraction of "contraction opportunities" used
    # the contracted form? 1.0 = always contracts, 0.0 = never contracts
    total_opportunities = contraction_count + expanded_form_count
    contraction_ratio = (
        contraction_count / total_opportunities if total_opportunities > 0 else 0.0
    )
    top_contractions = contraction_counts.most_common(10)

    # =========================================================================
    # ACRONYMS
    # =========================================================================
    acronym_counts, acronym_style = _detect_acronyms(text)
    acronym_count = sum(acronym_counts.values())
    top_acronyms = acronym_counts.most_common(10)

    # =========================================================================
    # LATIN ABBREVIATIONS
    # =========================================================================
    latin_abbrevs = _count_latin_abbreviations(text)
    latin_abbreviation_count = sum(latin_abbrevs.values())
    latin_abbreviation_density = latin_abbreviation_count * density_multiplier

    # =========================================================================
    # INFORMAL SHORTENINGS
    # =========================================================================
    informal_counts: Counter[str] = Counter()
    for token in tokens:
        if token in INFORMAL_SHORTENINGS:
            informal_counts[token] += 1
    informal_shortening_count = sum(informal_counts.values())
    informal_shortening_density = informal_shortening_count * density_multiplier
    top_informal_shortenings = informal_counts.most_common(10)

    # =========================================================================
    # TEXT-SPEAK
    # =========================================================================
    text_speak_counts = _count_text_speak(tokens)
    text_speak_count = sum(text_speak_counts.values())
    text_speak_density = text_speak_count * density_multiplier
    top_text_speak = text_speak_counts.most_common(10)

    # =========================================================================
    # TITLE ABBREVIATIONS
    # =========================================================================
    title_abbrevs = _count_title_abbreviations(text)
    title_abbreviation_count = sum(title_abbrevs.values())
    title_abbreviation_density = title_abbreviation_count * density_multiplier

    # =========================================================================
    # COMPOSITE INFORMALITY SCORE
    # =========================================================================
    informality_score = _compute_informality_score(
        contraction_ratio=contraction_ratio,
        text_speak_density=text_speak_density,
        informal_shortening_density=informal_shortening_density,
        latin_abbreviation_density=latin_abbreviation_density,
    )

    # =========================================================================
    # BUILD RESULT
    # =========================================================================
    metadata: dict[str, Any] = {
        "word_count": word_count,
        "total_abbreviation_count": (
            contraction_count
            + acronym_count
            + latin_abbreviation_count
            + informal_shortening_count
            + text_speak_count
            + title_abbreviation_count
        ),
        "all_contraction_counts": dict(contraction_counts),
        "all_acronym_counts": dict(acronym_counts),
        "all_informal_shortening_counts": dict(informal_counts),
        "all_text_speak_counts": dict(text_speak_counts),
        "contraction_map": CONTRACTIONS,
        "text_speak_map": TEXT_SPEAK,
        "informal_shortening_map": INFORMAL_SHORTENINGS,
    }

    return AbbreviationResult(
        contraction_ratio=contraction_ratio,
        contraction_count=contraction_count,
        expanded_form_count=expanded_form_count,
        top_contractions=top_contractions,
        acronym_count=acronym_count,
        acronym_style=acronym_style,
        top_acronyms=top_acronyms,
        latin_abbreviation_count=latin_abbreviation_count,
        latin_abbreviation_density=latin_abbreviation_density,
        latin_abbreviations=latin_abbrevs,
        informal_shortening_count=informal_shortening_count,
        informal_shortening_density=informal_shortening_density,
        top_informal_shortenings=top_informal_shortenings,
        text_speak_count=text_speak_count,
        text_speak_density=text_speak_density,
        top_text_speak=top_text_speak,
        title_abbreviation_count=title_abbreviation_count,
        title_abbreviation_density=title_abbreviation_density,
        title_abbreviations=title_abbrevs,
        informality_score=informality_score,
        metadata=metadata,
    )
