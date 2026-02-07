"""Word morphological classification for stylometric analysis.

Classifies words into a three-layer taxonomy based on orthographic properties
and curated word lists. The taxonomy is dictionary-driven for precision, with
regex fallback for structural patterns.

The novel contribution here is not the individual classifications (each is
well-established in linguistics) but assembling them into a single unified
surface-form classifier specifically designed for corpus frequency analysis.
Without this classification, contractions produce absurd overuse ratios
(e.g. 93,000x for "it's") because the BNC's CLAWS4 tagger splits them
into component tokens ("it" + "'s") and never counts them as single words.

Taxonomy layers
---------------

1. **L1 -- Orthographic class**: Deterministic, based on character inspection.
   ``lexical``, ``apostrophe``, ``hyphenated``, ``apostrophe_hyphenated``,
   ``unicode``, ``numeric``, ``other``.

2. **L2 -- Morphological category**: Pattern-matched via curated word lists
   and regex. ``contraction``, ``possessive``, ``compound``, ``prefixed``, etc.

3. **L3 -- Specific pattern**: Most granular level, e.g. ``negative``,
   ``copula``, ``auxiliary``, ``exact``, ``rhyming``, ``ablaut``.

Resolution order
----------------

1. Exact lookup against curated word lists (~200 entries)
2. Regex patterns for structural matches (prefixes, number words, ordinals)
3. L1 flags as character-inspection safety net
4. ``unclassified`` when a word triggers a flag but matches no known pattern

Related GitHub Issues:
    #51 -- Word morphological classification taxonomy
    https://github.com/craigtrim/pystylometry/issues/51

    #52 -- Linguistics literature supporting the taxonomy
    https://github.com/craigtrim/pystylometry/issues/52

References:
    Zwicky, A. M., & Pullum, G. K. (1983). Cliticization vs. Inflection:
        English N'T. Language, 59(3), 502-513.
        https://web.stanford.edu/~zwicky/ZPCliticsInfl.pdf

    Huddleston, R., & Pullum, G. K. (2002). The Cambridge Grammar of the
        English Language. Cambridge University Press. (Ch. 18: clitics and
        the possessive 's as phrasal clitic vs. verbal clitics.)

    Plag, I. (2003/2018). Word-Formation in English. Cambridge Textbooks
        in Linguistics. (Ch. 6: compound classification.)

    Bauer, L. (2003). Introducing Linguistic Morphology. Edinburgh
        University Press. (Compound headedness and productive prefixation.)

    Murray, J. A. H. (1880). Aphesis. Proceedings of the Philological
        Society. (Coined the term for unstressed initial vowel loss.)

    Schutzler, O. (2020). Aphesis and Aphaeresis in Late Modern English
        Dialects. English Studies, 102(1).
        https://doi.org/10.1080/0013838X.2020.1866306

    Sun, C. C., & Baayen, R. H. (2020). Hyphenation as a Compounding
        Technique. (Hyphen presence as orthographic signal of compound type.)
        https://quantling.org/~hbaayen/publications/SunBaayen2020.pdf

    BNC CLAWS4 tagger documentation:
        http://www.natcorp.ox.ac.uk/docs/URG/posguide.html
        (Documents how contractions are split into component tokens.)

Example:
    >>> from pystylometry.lexical.word_class import classify_word
    >>> result = classify_word("don't")
    >>> result.label
    'apostrophe.contraction.negative'
    >>> result.l1
    'apostrophe'
    >>> result.l2
    'contraction'
    >>> result.l3
    'negative'

    >>> classify_word("self-esteem").label
    'hyphenated.compound.self'

    >>> classify_word("trembling").label
    'lexical'
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WordClass:
    """Classification result for a single word.

    Attributes:
        word: The original word that was classified.
        l1: Orthographic class (always present).
            One of: ``lexical``, ``apostrophe``, ``hyphenated``,
            ``apostrophe_hyphenated``, ``unicode``, ``numeric``, ``other``.
        l2: Morphological category (may be ``None`` for ``lexical``).
        l3: Specific pattern (may be ``None`` when L2 is the deepest level).
        label: Dot-separated path combining l1, l2, and l3.
            E.g. ``apostrophe.contraction.negative``.
    """

    word: str
    l1: str
    l2: str | None = None
    l3: str | None = None

    @property
    def label(self) -> str:
        """Dot-separated classification path.

        Examples:
            >>> WordClass("don't", "apostrophe", "contraction", "negative").label
            'apostrophe.contraction.negative'
            >>> WordClass("trembling", "lexical").label
            'lexical'
        """
        parts = [self.l1]
        if self.l2:
            parts.append(self.l2)
        if self.l3:
            parts.append(self.l3)
        return ".".join(parts)


# ---------------------------------------------------------------------------
# Curated word lists
#
# These are finite, exhaustive enumerations of English forms.  The taxonomy
# is dictionary-driven (not inference-driven) for precision.  Words that
# do not appear in any list fall through to regex patterns, then to the
# ``unclassified`` label for iterative refinement against real corpora.
#
# See #52 for the linguistics literature supporting each category:
# https://github.com/craigtrim/pystylometry/issues/52
# ---------------------------------------------------------------------------

# -- Apostrophe: negative contractions (n't) --------------------------------
# Zwicky & Pullum (1983) argued that -n't is an inflectional affix on
# auxiliary verbs, not a clitic.  This makes negative contractions a
# linguistically distinct class from copula/auxiliary enclitics below.
# See: https://web.stanford.edu/~zwicky/ZPCliticsInfl.pdf
_NEGATIVE_CONTRACTIONS: set[str] = {
    "ain't",
    "aren't",
    "can't",
    "couldn't",
    "daren't",
    "didn't",
    "doesn't",
    "don't",
    "hadn't",
    "hasn't",
    "haven't",
    "isn't",
    "mayn't",
    "mightn't",
    "mustn't",
    "needn't",
    "oughtn't",
    "shan't",
    "shouldn't",
    "wasn't",
    "weren't",
    "won't",
    "wouldn't",
}

# -- Apostrophe: copula enclitics ('s=is/has, 're=are, 'm=am) --------------
# Huddleston & Pullum (2002) treat these as cliticized auxiliary verbs,
# fundamentally different from the possessive 's (which is a phrasal
# clitic attaching to the end of a noun phrase, not a specific word).
# The 's ambiguity (contraction vs. possessive) is a known unsolved
# problem in NLP without sentence context.  We resolve it by listing
# pronoun/adverb hosts here; anything else with 's falls to possessive.
# See: https://github.com/craigtrim/pystylometry/issues/52#issuecomment-2640070654
_COPULA_ENCLITICS: set[str] = {
    # 's (= is / has)
    "everybody's",
    "everyone's",
    "everything's",
    "he's",
    "here's",
    "how's",
    "it's",
    "nobody's",
    "nothing's",
    "one's",
    "she's",
    "somebody's",
    "someone's",
    "something's",
    "that's",
    "there's",
    "what's",
    "when's",
    "where's",
    "who's",
    "why's",
    # 're (= are)
    "they're",
    "we're",
    "you're",
    # 'm (= am)
    "i'm",
}

# -- Apostrophe: auxiliary enclitics ('ll, 'd, 've) -------------------------
# Also verbal clitics per Huddleston & Pullum (2002).  Note that 'd is
# ambiguous between "would" and "had" without context, but both are
# auxiliary reductions and classify identically here.
_AUXILIARY_ENCLITICS: set[str] = {
    # 'll (= will / shall)
    "he'll",
    "i'll",
    "it'll",
    "she'll",
    "that'll",
    "there'll",
    "they'll",
    "we'll",
    "what'll",
    "who'll",
    "you'll",
    # 'd (= would / had)
    "he'd",
    "how'd",
    "i'd",
    "it'd",
    "she'd",
    "that'd",
    "there'd",
    "they'd",
    "we'd",
    "what'd",
    "who'd",
    "you'd",
    # 've (= have)
    "could've",
    "i've",
    "might've",
    "must've",
    "should've",
    "they've",
    "we've",
    "who've",
    "would've",
    "you've",
}

# -- Apostrophe: enclitic (let's) -------------------------------------------
_ENCLITICS: set[str] = {
    "let's",
}

# -- Apostrophe: aphetic forms (initial elision) ----------------------------
# James Murray coined "aphesis" in 1880 for the loss of unstressed initial
# vowels (a specific subtype of the broader "aphaeresis").  Schutzler (2020)
# cataloged these forms across Late Modern English dialects.
# See: https://doi.org/10.1080/0013838X.2020.1866306
_APHETIC_ARCHAIC: set[str] = {
    "'twas",
    "'tis",
    "'twill",
    "'twould",
    "'twere",
    "'twasn't",
}

_APHETIC_POETIC: set[str] = {
    "'gainst",
    "'midst",
    "'mid",
    "'mongst",
    "'neath",
    "'pon",
    "'twixt",
}

# -- Apostrophe: dialectal / informal reductions ----------------------------
# G-dropping (alveolar substitution of /In/ for /IN/) is one of the most
# studied variables in variationist sociolinguistics.
_DIALECTAL_PRONOUN_REDUCTION: set[str] = {
    "'em",
    "'er",
    "'im",
    "'is",
}

_DIALECTAL_MEDIAL: set[str] = {
    "ma'am",
    "o'clock",
    "fo'c'sle",
    "ne'er",
    "e'er",
    "o'er",
    "ha'penny",
    "jack-o'-lantern",  # also apostrophe_hyphenated, handled separately
}

_DIALECTAL_INITIAL: set[str] = {
    "'bout",
    "'cause",
    "'cept",
    "'fore",
    "'round",
    "'fraid",
    "'nough",
    "'nuff",
    "'spose",
    "'scuse",
}

_DIALECTAL_YALL: set[str] = {
    "y'all",
    "ya'll",
}

# -- Hyphenated: reduplicated forms -----------------------------------------
# Three formally recognized subtypes in the linguistics literature.
# Ablaut reduplication has a well-known phonological constraint: the first
# vowel is almost always high/front (/I/ as in "hit"), the second low/back
# (/ae/ as in "cat" or /Q/ as in "top").  This is why English speakers say
# "tick-tock" not "tock-tick", "zig-zag" not "zag-zig".
# See: Linguistic Typology (2023), survey of 31 languages with ablaut
# reduplication; also Inkelas (UC Berkeley) on reduplication typology.
# https://github.com/craigtrim/pystylometry/issues/52#issuecomment-2640071082
_REDUPLICATED_EXACT: set[str] = {
    "boo-boo",
    "bye-bye",
    "choo-choo",
    "fifty-fifty",
    "goody-goody",
    "hush-hush",
    "knock-knock",
    "murmur-murmur",
    "no-no",
    "pom-pom",
    "so-so",
    "ta-ta",
    "tsk-tsk",
    "tut-tut",
}

_REDUPLICATED_RHYMING: set[str] = {
    "argy-bargy",
    "easy-peasy",
    "hee-haw",
    "helter-skelter",
    "higgledy-piggledy",
    "hoity-toity",
    "hokey-pokey",
    "hotch-potch",
    "hurly-burly",
    "hurry-scurry",
    "itsy-bitsy",
    "namby-pamby",
    "nitty-gritty",
    "okey-dokey",
    "razzle-dazzle",
    "teeny-weeny",
    "willy-nilly",
    "wishy-washy",
}

_REDUPLICATED_ABLAUT: set[str] = {
    "clip-clop",
    "criss-cross",
    "dilly-dally",
    "ding-dong",
    "flip-flop",
    "hip-hop",
    "kit-kat",
    "knick-knack",
    "mish-mash",
    "ping-pong",
    "pitter-patter",
    "riff-raff",
    "see-saw",
    "shilly-shally",
    "sing-song",
    "tick-tock",
    "tip-top",
    "zig-zag",
}

# -- Hyphenated: directional / compass compounds ----------------------------
_DIRECTIONAL: set[str] = {
    "north-east",
    "north-eastern",
    "north-north-east",
    "north-north-west",
    "north-south",
    "north-west",
    "north-western",
    "south-east",
    "south-eastern",
    "south-south-east",
    "south-south-west",
    "south-west",
    "south-western",
}

# -- Apostrophe + Hyphen: compound reductions --------------------------------
_APOSTROPHE_HYPHENATED: set[str] = {
    "cat-o'-nine-tails",
    "jack-o'-lantern",
    "tam-o'-shanter",
    "will-o'-the-wisp",
}

# ---------------------------------------------------------------------------
# Regex patterns (structural matches)
#
# These cover open-class categories where enumeration is impractical.
# Plag (2003/2018) Ch. 6 covers compound classification; Bauer (2003)
# distinguishes productive prefixation from compounding as a separate
# word-formation process.  Sun & Baayen (2020) validated hyphen presence
# as a systematic orthographic signal of compound type.
# https://github.com/craigtrim/pystylometry/issues/52#issuecomment-2640070893
# ---------------------------------------------------------------------------

# Hyphenated prefixes -- productive English prefixes that often appear with
# a hyphen before the root word.
_HYPHEN_PREFIXES = re.compile(
    r"^(all|anti|co|counter|cross|de|ex|extra|half|inter|mid|mini|multi|"
    r"non|out|over|pan|post|pre|pro|re|semi|sub|super|trans|ultra|under|"
    r"vice|well)-[a-z]",
    re.IGNORECASE,
)

# self- compounds (reflexive / auto-referential)
_SELF_COMPOUND = re.compile(r"^self-[a-z]", re.IGNORECASE)

# Number words: twenty-one through ninety-nine, and ordinal variants
_TENS = r"(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)"
_ONES = r"(?:one|two|three|four|five|six|seven|eight|nine)"
_ORDINAL_ONES = r"(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth)"
_NUMBER_WORD = re.compile(
    rf"^{_TENS}-(?:{_ONES}|{_ORDINAL_ONES})$", re.IGNORECASE
)

# Numeric ordinals: 1st, 2nd, 3rd, 4th, 21st, 100th, etc.
_NUMERIC_ORDINAL = re.compile(r"^\d+(?:st|nd|rd|th)$", re.IGNORECASE)

# g-dropping: words ending in in' (runnin', jumpin', somethin')
_G_DROPPING = re.compile(r"^[a-z]{2,}in'$", re.IGNORECASE)

# Phrasal modifiers: multi-hyphen chains with small connecting words
_PHRASAL_MODIFIER = re.compile(
    r"^[a-z]+-(?:of|the|to|a|an|in|on|at|for|and|or|than|as)-[a-z]",
    re.IGNORECASE,
)

# Non-ASCII character detection (unicode flag)
_HAS_NON_ASCII = re.compile(r"[^\x00-\x7f]")

# Non-a-z character detection (for 'other' flag)
_HAS_NON_AZ = re.compile(r"[^a-z]", re.IGNORECASE)

# Digit detection
_HAS_DIGIT = re.compile(r"\d")

# ---------------------------------------------------------------------------
# Classification engine
# ---------------------------------------------------------------------------


def classify_word(word: str) -> WordClass:
    """Classify a word into the morphological taxonomy.

    Uses curated word lists for exact matches, regex patterns for structural
    matches, and character-inspection flags as a safety net.  Words that
    trigger a flag but match no known pattern are labelled ``*.unclassified``
    so they can be refined iteratively.

    Args:
        word: The word to classify.  Should be a single token (no spaces).
            Case is preserved in the result but matching is case-insensitive.

    Returns:
        A :class:`WordClass` instance with ``l1``, ``l2``, ``l3``, and
        ``label`` attributes.

    Related GitHub Issue:
        #51 — Word morphological classification taxonomy
        https://github.com/craigtrim/pystylometry/issues/51

    Examples:
        >>> classify_word("don't").label
        'apostrophe.contraction.negative'
        >>> classify_word("self-esteem").label
        'hyphenated.compound.self'
        >>> classify_word("trembling").label
        'lexical'
        >>> classify_word("café").label
        'unicode.unclassified'
    """
    lower = word.lower()

    has_apostrophe = "'" in lower
    has_hyphen = "-" in lower
    has_non_ascii = bool(_HAS_NON_ASCII.search(lower))
    has_digit = bool(_HAS_DIGIT.search(lower))

    # -----------------------------------------------------------------------
    # L1: Determine orthographic class from flags
    # -----------------------------------------------------------------------

    # Apostrophe + Hyphen (check first — more specific than either alone)
    if has_apostrophe and has_hyphen:
        result = _classify_apostrophe_hyphenated(lower, word)
        if result:
            return result
        # If not a known apostrophe-hyphenated form, fall through to
        # whichever flag dominates.  Apostrophe patterns are richer,
        # so try apostrophe first, then hyphenated.
        result = _classify_apostrophe(lower, word)
        if result:
            return result
        result = _classify_hyphenated(lower, word)
        if result:
            return result
        return WordClass(word, "apostrophe_hyphenated", "unclassified")

    # Apostrophe only
    if has_apostrophe:
        result = _classify_apostrophe(lower, word)
        if result:
            return result
        return WordClass(word, "apostrophe", "unclassified")

    # Hyphenated only
    if has_hyphen:
        result = _classify_hyphenated(lower, word)
        if result:
            return result
        return WordClass(word, "hyphenated", "unclassified")

    # Unicode (non-ASCII characters)
    if has_non_ascii:
        return WordClass(word, "unicode", "unclassified")

    # Numeric (contains digits)
    if has_digit:
        result = _classify_numeric(lower, word)
        if result:
            return result
        return WordClass(word, "numeric", "unclassified")

    # Other: non-a-z characters that aren't apostrophe, hyphen, unicode,
    # or numeric.
    if bool(_HAS_NON_AZ.search(lower)):
        return WordClass(word, "other", "unclassified")

    # Pure a-z: standard lexical word
    return WordClass(word, "lexical")


# ---------------------------------------------------------------------------
# L1-specific classifiers
# ---------------------------------------------------------------------------


def _classify_apostrophe(lower: str, word: str) -> WordClass | None:
    """Classify apostrophe-containing words via word lists and patterns."""

    # Exact word-list lookups (most precise, checked first)
    if lower in _NEGATIVE_CONTRACTIONS:
        return WordClass(word, "apostrophe", "contraction", "negative")
    if lower in _COPULA_ENCLITICS:
        return WordClass(word, "apostrophe", "contraction", "copula")
    if lower in _AUXILIARY_ENCLITICS:
        return WordClass(word, "apostrophe", "contraction", "auxiliary")
    if lower in _ENCLITICS:
        return WordClass(word, "apostrophe", "enclitic")
    if lower in _APHETIC_ARCHAIC:
        return WordClass(word, "apostrophe", "aphetic", "archaic")
    if lower in _APHETIC_POETIC:
        return WordClass(word, "apostrophe", "aphetic", "poetic")
    if lower in _DIALECTAL_PRONOUN_REDUCTION:
        return WordClass(word, "apostrophe", "dialectal", "pronoun_reduction")
    if lower in _DIALECTAL_MEDIAL:
        return WordClass(word, "apostrophe", "dialectal", "medial")
    if lower in _DIALECTAL_INITIAL:
        return WordClass(word, "apostrophe", "dialectal", "initial")
    if lower in _DIALECTAL_YALL:
        return WordClass(word, "apostrophe", "dialectal", "regional")

    # Regex patterns (structural fallbacks)

    # g-dropping: runnin', jumpin', etc.
    if _G_DROPPING.match(lower):
        return WordClass(word, "apostrophe", "dialectal", "g_dropping")

    # Possessive: anything ending in 's or s' that isn't in the
    # contraction/enclitic lists above.  Classification by elimination.
    if lower.endswith("'s") or lower.endswith("s'"):
        if lower.endswith("s'"):
            return WordClass(word, "apostrophe", "possessive", "plural")
        return WordClass(word, "apostrophe", "possessive", "singular")

    return None


def _classify_hyphenated(lower: str, word: str) -> WordClass | None:
    """Classify hyphen-containing words via word lists and patterns."""

    # Exact word-list lookups
    if lower in _REDUPLICATED_EXACT:
        return WordClass(word, "hyphenated", "reduplicated", "exact")
    if lower in _REDUPLICATED_RHYMING:
        return WordClass(word, "hyphenated", "reduplicated", "rhyming")
    if lower in _REDUPLICATED_ABLAUT:
        return WordClass(word, "hyphenated", "reduplicated", "ablaut")
    if lower in _DIRECTIONAL:
        return WordClass(word, "hyphenated", "directional")

    # Regex patterns

    # self- compounds (check before general prefix)
    if _SELF_COMPOUND.match(lower):
        return WordClass(word, "hyphenated", "compound", "self")

    # Number words: twenty-one, forty-second, etc.
    if _NUMBER_WORD.match(lower):
        return WordClass(word, "hyphenated", "number_word")

    # Phrasal modifiers: state-of-the-art, run-of-the-mill, etc.
    # (checked before prefixed because "out-of-date" should be phrasal,
    # not prefixed with "out-")
    if _PHRASAL_MODIFIER.match(lower):
        return WordClass(word, "hyphenated", "phrasal_modifier")

    # Productive prefixes: re-enter, co-operate, anti-hero, etc.
    if _HYPHEN_PREFIXES.match(lower):
        return WordClass(word, "hyphenated", "prefixed")

    return None


def _classify_apostrophe_hyphenated(
    lower: str, word: str
) -> WordClass | None:
    """Classify words containing both apostrophe and hyphen."""
    if lower in _APOSTROPHE_HYPHENATED:
        return WordClass(word, "apostrophe_hyphenated", "compound_reduction")
    return None


def _classify_numeric(lower: str, word: str) -> WordClass | None:
    """Classify words containing digits."""
    if _NUMERIC_ORDINAL.match(lower):
        return WordClass(word, "numeric", "ordinal")
    return None
