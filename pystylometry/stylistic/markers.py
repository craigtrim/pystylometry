"""Stylistic markers for authorship attribution.

This module identifies and analyzes specific linguistic features that authors
use consistently and often subconsciously. These markers include contraction
preferences, intensifier usage, hedging patterns, modal auxiliaries, negation
patterns, and punctuation style habits.

Related GitHub Issue:
    #20 - Stylistic Markers
    https://github.com/craigtrim/pystylometry/issues/20

Categories of stylistic markers:
    - Contraction patterns (can't vs. cannot, I'm vs. I am)
    - Intensifiers (very, really, extremely, quite)
    - Hedges (maybe, perhaps, probably, somewhat)
    - Modal auxiliaries (can, could, may, might, must, should, will, would)
    - Negation patterns (not, no, never, none, neither)
    - Punctuation style (exclamations, questions, quotes, parentheticals)

References:
    Argamon, S., & Levitan, S. (2005). Measuring the usefulness of function
        words for authorship attribution. ACH/ALLC.
    Pennebaker, J. W. (2011). The secret life of pronouns. Bloomsbury Press.
    Biber, D. (1988). Variation across speech and writing. Cambridge University Press.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

from .._types import StylisticMarkersResult

# =============================================================================
# CONTRACTION PATTERNS
# =============================================================================
# Map contractions to their expanded forms for detection and ratio calculation
# Related GitHub Issue #20: https://github.com/craigtrim/pystylometry/issues/20

CONTRACTIONS: dict[str, str] = {
    # Negative contractions
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
    # Pronoun contractions
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
    "that'll": "that will",
    "that'd": "that would",
    "who's": "who is",
    "who'll": "who will",
    "who'd": "who would",
    "what's": "what is",
    "what'll": "what will",
    "what'd": "what would",
    "where's": "where is",
    "where'll": "where will",
    "where'd": "where would",
    "when's": "when is",
    "when'll": "when will",
    "when'd": "when would",
    "why's": "why is",
    "why'll": "why will",
    "why'd": "why would",
    "how's": "how is",
    "how'll": "how will",
    "how'd": "how would",
    "there's": "there is",
    "there'll": "there will",
    "there'd": "there would",
    "here's": "here is",
    # Other contractions
    "let's": "let us",
    "ain't": "am not",
    "'twas": "it was",
    "'tis": "it is",
}

# Build expanded form patterns for detection
# These patterns match the expanded forms that could have been contracted
EXPANDED_FORM_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b(are)\s+(not)\b", re.IGNORECASE), "aren't"),
    (re.compile(r"\b(can)\s*(?:not|n't)\b", re.IGNORECASE), "can't"),
    (re.compile(r"\b(could)\s+(not)\b", re.IGNORECASE), "couldn't"),
    (re.compile(r"\b(did)\s+(not)\b", re.IGNORECASE), "didn't"),
    (re.compile(r"\b(does)\s+(not)\b", re.IGNORECASE), "doesn't"),
    (re.compile(r"\b(do)\s+(not)\b", re.IGNORECASE), "don't"),
    (re.compile(r"\b(had)\s+(not)\b", re.IGNORECASE), "hadn't"),
    (re.compile(r"\b(has)\s+(not)\b", re.IGNORECASE), "hasn't"),
    (re.compile(r"\b(have)\s+(not)\b", re.IGNORECASE), "haven't"),
    (re.compile(r"\b(is)\s+(not)\b", re.IGNORECASE), "isn't"),
    (re.compile(r"\b(might)\s+(not)\b", re.IGNORECASE), "mightn't"),
    (re.compile(r"\b(must)\s+(not)\b", re.IGNORECASE), "mustn't"),
    (re.compile(r"\b(need)\s+(not)\b", re.IGNORECASE), "needn't"),
    (re.compile(r"\b(shall)\s+(not)\b", re.IGNORECASE), "shan't"),
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
    (re.compile(r"\b(you)\s+(have)\b", re.IGNORECASE), "you've"),
    (re.compile(r"\b(you)\s+(will)\b", re.IGNORECASE), "you'll"),
    (re.compile(r"\b(you)\s+(would)\b", re.IGNORECASE), "you'd"),
    (re.compile(r"\b(he)\s+(is)\b", re.IGNORECASE), "he's"),
    (re.compile(r"\b(he)\s+(will)\b", re.IGNORECASE), "he'll"),
    (re.compile(r"\b(he)\s+(would)\b", re.IGNORECASE), "he'd"),
    (re.compile(r"\b(she)\s+(is)\b", re.IGNORECASE), "she's"),
    (re.compile(r"\b(she)\s+(will)\b", re.IGNORECASE), "she'll"),
    (re.compile(r"\b(she)\s+(would)\b", re.IGNORECASE), "she'd"),
    (re.compile(r"\b(it)\s+(is)\b", re.IGNORECASE), "it's"),
    (re.compile(r"\b(it)\s+(will)\b", re.IGNORECASE), "it'll"),
    (re.compile(r"\b(it)\s+(would)\b", re.IGNORECASE), "it'd"),
    (re.compile(r"\b(we)\s+(are)\b", re.IGNORECASE), "we're"),
    (re.compile(r"\b(we)\s+(have)\b", re.IGNORECASE), "we've"),
    (re.compile(r"\b(we)\s+(will)\b", re.IGNORECASE), "we'll"),
    (re.compile(r"\b(we)\s+(would)\b", re.IGNORECASE), "we'd"),
    (re.compile(r"\b(they)\s+(are)\b", re.IGNORECASE), "they're"),
    (re.compile(r"\b(they)\s+(have)\b", re.IGNORECASE), "they've"),
    (re.compile(r"\b(they)\s+(will)\b", re.IGNORECASE), "they'll"),
    (re.compile(r"\b(they)\s+(would)\b", re.IGNORECASE), "they'd"),
    (re.compile(r"\b(that)\s+(is)\b", re.IGNORECASE), "that's"),
    (re.compile(r"\b(there)\s+(is)\b", re.IGNORECASE), "there's"),
    (re.compile(r"\b(here)\s+(is)\b", re.IGNORECASE), "here's"),
    (re.compile(r"\b(let)\s+(us)\b", re.IGNORECASE), "let's"),
]

# =============================================================================
# INTENSIFIERS
# =============================================================================
# Words that amplify or emphasize meaning
# Reference: Biber, D. (1988). Variation across speech and writing.

INTENSIFIERS: set[str] = {
    # Amplifiers (boosters)
    "very",
    "really",
    "extremely",
    "absolutely",
    "completely",
    "totally",
    "entirely",
    "utterly",
    "thoroughly",
    "perfectly",
    "highly",
    "deeply",
    "greatly",
    "strongly",
    "immensely",
    "incredibly",
    "remarkably",
    "exceptionally",
    "extraordinarily",
    "tremendously",
    "enormously",
    "vastly",
    "significantly",
    "substantially",
    "considerably",
    "profoundly",
    "intensely",
    "acutely",
    "severely",
    "seriously",
    # Degree modifiers
    "quite",
    "rather",
    "fairly",
    "pretty",
    "so",
    "too",
    "such",
    "much",
    "more",
    "most",
    "particularly",
    "especially",
    "decidedly",
    "definitely",
    "certainly",
    "surely",
    "indeed",
    # Informal intensifiers
    "super",
    "mega",
    "ultra",
    "way",
    "real",
    "awful",
    "awfully",
    "terribly",
    "dreadfully",
    "frightfully",
}

# =============================================================================
# HEDGES
# =============================================================================
# Words that weaken or qualify statements, showing uncertainty or politeness
# Reference: Lakoff, G. (1972). Hedges: A study in meaning criteria.

HEDGES: set[str] = {
    # Epistemic hedges (expressing uncertainty)
    "maybe",
    "perhaps",
    "possibly",
    "probably",
    "apparently",
    "seemingly",
    "supposedly",
    "allegedly",
    "presumably",
    "conceivably",
    "potentially",
    "arguably",
    "ostensibly",
    # Approximators
    "about",
    "around",
    "approximately",
    "roughly",
    "nearly",
    "almost",
    "virtually",
    "practically",
    "essentially",
    "basically",
    "generally",
    "usually",
    "typically",
    "normally",
    "ordinarily",
    # Degree hedges
    "somewhat",
    "slightly",
    "a bit",
    "a little",
    "kind of",
    "sort of",
    "more or less",
    "to some extent",
    "in a way",
    "in some ways",
    "to a degree",
    "relatively",
    "comparatively",
    "partly",
    "partially",
    # Shield expressions
    "seem",
    "seems",
    "seemed",
    "appear",
    "appears",
    "appeared",
    "suggest",
    "suggests",
    "suggested",
    "indicate",
    "indicates",
    "indicated",
    "tend",
    "tends",
    "tended",
    # Attribution hedges
    "reportedly",
    "according to",
    "i think",
    "i believe",
    "i suppose",
    "i guess",
    "i assume",
    "it seems",
    "it appears",
}

# =============================================================================
# MODAL AUXILIARIES
# =============================================================================
# Epistemic modals express possibility/probability
# Deontic modals express necessity/obligation/permission

EPISTEMIC_MODALS: set[str] = {
    "may",
    "might",
    "could",
    "can",
    "would",
    "should",
}

DEONTIC_MODALS: set[str] = {
    "must",
    "shall",
    "will",
    "should",
    "ought",
    "need",
    "have to",
    "has to",
    "had to",
    "got to",
}

ALL_MODALS: set[str] = {
    "can",
    "could",
    "may",
    "might",
    "must",
    "shall",
    "should",
    "will",
    "would",
    "ought",
    "need",
}

# =============================================================================
# NEGATION MARKERS
# =============================================================================
# Words and patterns that express negation

NEGATION_MARKERS: set[str] = {
    "not",
    "no",
    "never",
    "none",
    "nothing",
    "nobody",
    "nowhere",
    "neither",
    "nor",
    "without",
    "hardly",
    "barely",
    "scarcely",
    "rarely",
    "seldom",
}

# =============================================================================
# PUNCTUATION PATTERNS
# =============================================================================

# Patterns for punctuation detection
ELLIPSIS_PATTERN = re.compile(r"\.{3}|…")
DASH_PATTERN = re.compile(r"—|–|--")  # em-dash, en-dash, double hyphen
PARENTHETICAL_PATTERN = re.compile(r"[()]")
QUOTATION_PATTERN = re.compile(r'["""\'\']')  # Various quote styles


def _tokenize_simple(text: str) -> list[str]:
    """Simple word tokenization for marker analysis.

    Preserves contractions as single tokens while splitting on whitespace
    and basic punctuation.
    """
    # First normalize apostrophes
    text = text.replace("'", "'").replace("'", "'")

    # Split on whitespace and punctuation, keeping contractions together
    # This pattern keeps words with apostrophes intact
    tokens = re.findall(r"\b[\w']+\b", text.lower())

    return tokens


def _count_contractions(text: str) -> tuple[Counter[str], int]:
    """Count contractions in text.

    Returns:
        Tuple of (contraction_counts, expanded_form_count)
    """
    text_lower = text.lower()
    # Normalize apostrophes
    text_lower = text_lower.replace("'", "'").replace("'", "'")

    contraction_counts: Counter[str] = Counter()

    # Count each contraction
    for contraction in CONTRACTIONS:
        # Use word boundary matching
        contraction_pattern = r"\b" + re.escape(contraction) + r"\b"
        matches = re.findall(contraction_pattern, text_lower)
        if matches:
            contraction_counts[contraction] = len(matches)

    # Count expanded forms
    expanded_count = 0
    for expanded_pattern, _ in EXPANDED_FORM_PATTERNS:
        matches = expanded_pattern.findall(text_lower)
        expanded_count += len(matches)

    return contraction_counts, expanded_count


def _count_markers(tokens: list[str], marker_set: set[str]) -> Counter[str]:
    """Count occurrences of markers from a set in tokenized text."""
    counts: Counter[str] = Counter()
    for token in tokens:
        if token in marker_set:
            counts[token] += 1
    return counts


def _count_punctuation(text: str) -> dict[str, int]:
    """Count various punctuation marks in text."""
    return {
        "exclamation": text.count("!"),
        "question": text.count("?"),
        "quotation": len(QUOTATION_PATTERN.findall(text)),
        "parenthetical": len(PARENTHETICAL_PATTERN.findall(text)),
        "ellipsis": len(ELLIPSIS_PATTERN.findall(text)),
        "dash": len(DASH_PATTERN.findall(text)),
        "semicolon": text.count(";"),
        "colon": text.count(":"),
    }


def compute_stylistic_markers(text: str) -> StylisticMarkersResult:
    """
    Analyze stylistic markers for authorship attribution.

    Identifies and quantifies specific linguistic features that reveal authorial
    style. These features are often used subconsciously and remain consistent
    across an author's works, making them valuable for attribution.

    Related GitHub Issue:
        #20 - Stylistic Markers
        https://github.com/craigtrim/pystylometry/issues/20

    Why stylistic markers matter:

    Subconscious usage:
        - Authors don't deliberately vary these features
        - Remain consistent even when author tries to disguise style
        - Difficult to consciously control

    Genre-independent:
        - Used similarly across different topics
        - More stable than content words
        - Complement content-based features

    Psychologically meaningful:
        - Reveal personality traits (Pennebaker's research)
        - Indicate emotional state
        - Show cognitive patterns

    Marker Categories Analyzed:

    1. Contractions:
       - Preference for contracted vs. expanded forms
       - Examples: can't/cannot, I'm/I am, won't/will not
       - Formality indicator (more contractions = informal)

    2. Intensifiers:
       - Words that amplify meaning
       - Examples: very, really, extremely, quite, rather
       - Indicate emphatic style

    3. Hedges:
       - Words that weaken or qualify statements
       - Examples: maybe, perhaps, probably, somewhat, kind of
       - Indicate tentative or cautious style

    4. Modal Auxiliaries:
       - Express necessity, possibility, permission
       - Epistemic modals: may, might, could (possibility)
       - Deontic modals: must, should, ought (obligation)

    5. Negation:
       - Patterns of negative expression
       - not, no, never, none, neither, nowhere
       - Frequency and type vary by author

    6. Punctuation Style:
       - Exclamation marks: Emphatic, emotional
       - Question marks: Interactive, rhetorical
       - Quotation marks: Dialogue, scare quotes
       - Parentheticals: Asides, additional info
       - Ellipses: Trailing off, suspense
       - Dashes: Interruptions, emphasis
       - Semicolons/colons: Sophisticated syntax

    Args:
        text: Input text to analyze. Should contain at least 200+ words for
              reliable statistics. Shorter texts may have unstable marker ratios.

    Returns:
        StylisticMarkersResult containing extensive marker statistics.
        See _types.py for complete field list.

    Example:
        >>> result = compute_stylistic_markers("I can't believe it's really happening!")
        >>> print(f"Contraction ratio: {result.contraction_ratio * 100:.1f}%")
        >>> print(f"Intensifiers/100 words: {result.intensifier_density:.2f}")
        >>> print(f"Exclamation density: {result.exclamation_density:.2f}")

    Note:
        - Densities are per 100 words for interpretability
        - Contraction detection requires pattern matching
        - Modal auxiliaries classified as epistemic or deontic
        - Punctuation counts include all occurrences
        - Empty text returns 0.0 for ratios, 0 for counts
    """
    # Handle empty text
    if not text or not text.strip():
        return StylisticMarkersResult(
            contraction_ratio=0.0,
            contraction_count=0,
            expanded_form_count=0,
            top_contractions=[],
            intensifier_density=0.0,
            intensifier_count=0,
            top_intensifiers=[],
            hedging_density=0.0,
            hedging_count=0,
            top_hedges=[],
            modal_density=0.0,
            modal_distribution={},
            epistemic_modal_ratio=0.0,
            deontic_modal_ratio=0.0,
            negation_density=0.0,
            negation_count=0,
            negation_types={},
            exclamation_density=0.0,
            question_density=0.0,
            quotation_density=0.0,
            parenthetical_density=0.0,
            ellipsis_density=0.0,
            dash_density=0.0,
            semicolon_density=0.0,
            colon_density=0.0,
            metadata={"word_count": 0, "warning": "Empty text"},
        )

    # Tokenize
    tokens = _tokenize_simple(text)
    word_count = len(tokens)

    if word_count == 0:
        return StylisticMarkersResult(
            contraction_ratio=0.0,
            contraction_count=0,
            expanded_form_count=0,
            top_contractions=[],
            intensifier_density=0.0,
            intensifier_count=0,
            top_intensifiers=[],
            hedging_density=0.0,
            hedging_count=0,
            top_hedges=[],
            modal_density=0.0,
            modal_distribution={},
            epistemic_modal_ratio=0.0,
            deontic_modal_ratio=0.0,
            negation_density=0.0,
            negation_count=0,
            negation_types={},
            exclamation_density=0.0,
            question_density=0.0,
            quotation_density=0.0,
            parenthetical_density=0.0,
            ellipsis_density=0.0,
            dash_density=0.0,
            semicolon_density=0.0,
            colon_density=0.0,
            metadata={"word_count": 0, "warning": "No tokens found"},
        )

    # Calculate density multiplier (per 100 words)
    density_multiplier = 100.0 / word_count

    # ==========================================================================
    # CONTRACTIONS
    # ==========================================================================
    contraction_counts, expanded_form_count = _count_contractions(text)
    contraction_count = sum(contraction_counts.values())
    total_contractable = contraction_count + expanded_form_count
    contraction_ratio = contraction_count / total_contractable if total_contractable > 0 else 0.0
    top_contractions = contraction_counts.most_common(10)

    # ==========================================================================
    # INTENSIFIERS
    # ==========================================================================
    intensifier_counts = _count_markers(tokens, INTENSIFIERS)
    intensifier_count = sum(intensifier_counts.values())
    intensifier_density = intensifier_count * density_multiplier
    top_intensifiers = intensifier_counts.most_common(10)

    # ==========================================================================
    # HEDGES
    # ==========================================================================
    hedge_counts = _count_markers(tokens, HEDGES)
    hedge_count = sum(hedge_counts.values())
    hedging_density = hedge_count * density_multiplier
    top_hedges = hedge_counts.most_common(10)

    # ==========================================================================
    # MODAL AUXILIARIES
    # ==========================================================================
    modal_counts = _count_markers(tokens, ALL_MODALS)
    modal_distribution = dict(modal_counts)
    total_modals = sum(modal_counts.values())
    modal_density = total_modals * density_multiplier

    # Calculate epistemic vs deontic ratios
    epistemic_count = sum(modal_counts.get(m, 0) for m in EPISTEMIC_MODALS)
    deontic_count = sum(modal_counts.get(m, 0) for m in DEONTIC_MODALS)
    epistemic_modal_ratio = epistemic_count / total_modals if total_modals > 0 else 0.0
    deontic_modal_ratio = deontic_count / total_modals if total_modals > 0 else 0.0

    # ==========================================================================
    # NEGATION
    # ==========================================================================
    negation_counts = _count_markers(tokens, NEGATION_MARKERS)
    negation_count = sum(negation_counts.values())
    negation_density = negation_count * density_multiplier
    negation_types = dict(negation_counts)

    # ==========================================================================
    # PUNCTUATION
    # ==========================================================================
    punct_counts = _count_punctuation(text)
    exclamation_density = punct_counts["exclamation"] * density_multiplier
    question_density = punct_counts["question"] * density_multiplier
    quotation_density = punct_counts["quotation"] * density_multiplier
    parenthetical_density = punct_counts["parenthetical"] * density_multiplier
    ellipsis_density = punct_counts["ellipsis"] * density_multiplier
    dash_density = punct_counts["dash"] * density_multiplier
    semicolon_density = punct_counts["semicolon"] * density_multiplier
    colon_density = punct_counts["colon"] * density_multiplier

    # ==========================================================================
    # BUILD RESULT
    # ==========================================================================
    metadata: dict[str, Any] = {
        "word_count": word_count,
        "contraction_list": CONTRACTIONS,
        "intensifier_list": sorted(INTENSIFIERS),
        "hedge_list": sorted(HEDGES),
        "modal_list": sorted(ALL_MODALS),
        "negation_list": sorted(NEGATION_MARKERS),
        "punctuation_counts": punct_counts,
        "all_contraction_counts": dict(contraction_counts),
        "all_intensifier_counts": dict(intensifier_counts),
        "all_hedge_counts": dict(hedge_counts),
        "all_negation_counts": dict(negation_counts),
    }

    return StylisticMarkersResult(
        contraction_ratio=contraction_ratio,
        contraction_count=contraction_count,
        expanded_form_count=expanded_form_count,
        top_contractions=top_contractions,
        intensifier_density=intensifier_density,
        intensifier_count=intensifier_count,
        top_intensifiers=top_intensifiers,
        hedging_density=hedging_density,
        hedging_count=hedge_count,
        top_hedges=top_hedges,
        modal_density=modal_density,
        modal_distribution=modal_distribution,
        epistemic_modal_ratio=epistemic_modal_ratio,
        deontic_modal_ratio=deontic_modal_ratio,
        negation_density=negation_density,
        negation_count=negation_count,
        negation_types=negation_types,
        exclamation_density=exclamation_density,
        question_density=question_density,
        quotation_density=quotation_density,
        parenthetical_density=parenthetical_density,
        ellipsis_density=ellipsis_density,
        dash_density=dash_density,
        semicolon_density=semicolon_density,
        colon_density=colon_density,
        metadata=metadata,
    )
