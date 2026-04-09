"""Tests for phones_for_word() organized by primary stress count.

Primary stress in ARPAbet is indicated by the digit ``1`` appended to a
vowel phoneme (e.g. ``AE1``, ``IY1``, ``OW1``).  Secondary stress uses
``2``; unstressed uses ``0``.  Counting occurrences of ``1`` across a
word's phones gives its primary-stress count — the key input to syllabic
weight computation in beat detection (Issue #76).

Each test class covers one primary-stress tier and asserts both the
expected ARPAbet phones string (first CMU pronunciation) and the derived
primary-stress count.  This locks in the CMU dict values that annotated
comments in beat-detection tests depend on (e.g.
``test_beat_detection_isocolon.py``).

Related GitHub Issues:
    #76  — Beat Detection — Phrase-Level Stress Shape Analysis
    https://github.com/craigtrim/pystylometry/issues/76
    #60  — Replace pronouncing with direct cmudict access
    https://github.com/craigtrim/pystylometry/issues/60

References:
    CMU Pronouncing Dictionary:
        Weide, R. L. (1998). The CMU Pronouncing Dictionary, release 0.6d.
        Carnegie Mellon University. http://www.speech.cs.cmu.edu/cgi-bin/cmudict
    ARPAbet stress encoding:
        0 = no stress, 1 = primary stress, 2 = secondary stress
"""

import pytest

from pystylometry.prosody.pronouncing import phones_for_word


def _primary_count(phones_str: str) -> int:
    """Count primary-stressed vowels (digit 1) in an ARPAbet phones string."""
    return sum(1 for p in phones_str.split() if p.endswith("1"))


# ============================================================
# Tier 0 — No primary stress
# ============================================================


class TestNoPrimaryStress:
    """Function words whose *first* (reduced) CMU pronunciation carries no
    primary stress.

    Note: The CMU dict has only ~82 zero-primary-stress entries; the majority
    are obscure proper nouns or OCR artifacts.  The genuine common-English set
    is limited to a handful of function words (determiners, conjunctions,
    hedges) in their reduced/unstressed form.  Many of these words have a
    second pronunciation that *does* carry primary stress (e.g. ``a`` →
    ``AH0`` reduced, ``EY1`` emphatic).  Tests assert against the first
    (default/reduced) pronunciation only.
    """

    @pytest.mark.parametrize(
        "word, expected_phones",
        [
            ("a",     "AH0"),
            ("and",   "AH0 N D"),
            ("the",   "DH AH0"),
            ("in",    "IH0 N"),
            ("er",    "ER0"),
            ("hers",  "HH ER0 Z"),
        ],
    )
    def test_first_pronunciation_has_no_primary_stress(self, word, expected_phones):
        """First pronunciation contains zero primary-stress vowels."""
        result = phones_for_word(word)
        assert result, f"'{word}' not found in CMU dict"
        assert result[0] == expected_phones, (
            f"'{word}': expected '{expected_phones}', got '{result[0]}'"
        )
        assert _primary_count(result[0]) == 0, (
            f"'{word}': expected 0 primary stresses in '{result[0]}'"
        )


# ============================================================
# Tier 1 — Exactly one primary stress
# ============================================================


class TestOnePrimaryStress:
    """Words carrying exactly one primary-stressed syllable.

    This is the overwhelming majority of the CMU dict (124 452 entries).
    Cases span monosyllabic through polysyllabic words to confirm the count
    is stable across word lengths.  These are the building blocks of
    equal-weight (isocolon) and unequal-weight phrase comparisons in beat
    detection.
    """

    @pytest.mark.parametrize(
        "word, expected_phones",
        [
            # Monosyllabic
            ("cat",         "K AE1 T"),
            ("dog",         "D AO1 G"),
            ("run",         "R AH1 N"),
            ("jump",        "JH AH1 M P"),
            ("think",       "TH IH1 NG K"),
            ("write",       "R AY1 T"),
            ("fly",         "F L AY1"),
            ("bright",      "B R AY1 T"),
            ("strong",      "S T R AO1 NG"),
            ("soft",        "S AA1 F T"),
            ("hard",        "HH AA1 R D"),
            ("quick",       "K W IH1 K"),
            ("slow",        "S L OW1"),
            # Bisyllabic
            ("happy",       "HH AE1 P IY0"),
            ("lucky",       "L AH1 K IY0"),
            ("pretty",      "P R IH1 T IY0"),
            ("funny",       "F AH1 N IY0"),
            ("quickly",     "K W IH1 K L IY0"),
            ("slowly",      "S L OW1 L IY0"),
            ("clearly",     "K L IH1 R L IY0"),
            ("deeply",      "D IY1 P L IY0"),
            ("widely",      "W AY1 D L IY0"),
            ("running",     "R AH1 N IH0 NG"),
            ("thinking",    "TH IH1 NG K IH0 NG"),
            ("writing",     "R AY1 T IH0 NG"),
            ("reading",     "R IY1 D IH0 NG"),
            ("saying",      "S EY1 IH0 NG"),
            ("walking",     "W AO1 K IH0 NG"),
            # Trisyllabic
            ("beautiful",   "B Y UW1 T AH0 F AH0 L"),
            ("wonderful",   "W AH1 N D ER0 F AH0 L"),
            ("history",     "HH IH1 S T ER0 IY0"),
            ("carefully",   "K EH1 R F AH0 L IY0"),
            ("comfortable", "K AH1 M F ER0 T AH0 B AH0 L"),
            # Polysyllabic
            ("ordinary",    "AO1 R D AH0 N EH2 R IY0"),
            ("family",      "F AE1 M AH0 L IY0"),
            ("company",     "K AH1 M P AH0 N IY2"),
            ("similar",     "S IH1 M AH0 L ER0"),
            ("different",   "D IH1 F ER0 AH0 N T"),
            ("important",   "IH2 M P AO1 R T AH0 N T"),
            ("following",   "F AA1 L OW0 IH0 NG"),
            ("national",    "N AE1 SH AH0 N AH0 L"),
            # Expressive / pop culture — single primary stress despite length
            # supercalifragilistic: 11 syllables, yet only one primary stress
            # (Mary Poppins). CMU assigns primary to -fra- and secondary to
            # super-, cali-, -lis-, confirming the root carries the peak.
            ("supercalifragilistic", "S UW2 P ER0 K AE2 L AH0 F R AE1 JH AH0 L IH2 S T IH0 K"),
            # abracadabra: classic magic word; reduplication (cadabra mirrors
            # abra) but only one primary stress on the final -dae- syllable.
            ("abracadabra",          "AE2 B R AH0 K AH0 D AE1 B R AH0"),
            # hullabaloo: exclamatory noise word; stress falls on final -loo.
            ("hullabaloo",           "HH AH2 L AH0 B AH0 L UW1"),
            # gobbledygook: nonsense-bureaucrat compound; stress on -gook.
            ("gobbledygook",         "G AA2 B AH0 L D IY0 G UH1 K"),
            # shenanigans: Irish-English, expressive plural; stress on -nan-.
            ("shenanigans",          "SH AH0 N AE1 N IH0 G AH0 N Z"),
            # balderdash: emphatic dismissal; stress on bal-.
            ("balderdash",           "B AO1 L D ER0 D AE2 SH"),
            # poppycock: Dutch origin (pappekak), exclamatory; stress on pop-.
            ("poppycock",            "P AA1 P IY0 K AO2 K"),
            # kerfuffle: Scottish/dialectal; stress on -fuf-.
            ("kerfuffle",            "K ER0 F AH1 F AH0 L"),
            # brouhaha: French loanword, exclamatory; stress on broo-.
            ("brouhaha",             "B R UW1 HH AA0 HH AA2"),
            # nincompoop: archaic insult; stress on nin-.
            ("nincompoop",           "N IH1 NG K AH0 M P UW2 P"),
            # flabbergasted: emphatic surprise; stress on flab-.
            ("flabbergasted",        "F L AE1 B ER0 G AE2 S T IH0 D"),
            # discombobulated: comic polysyllable; stress on -bob-.
            ("discombobulated",      "D IH2 S K AH0 M B AO1 B Y UW0 L EY0 T AH0 D"),
            # thingamabob: placeholder word; stress on thing-.
            ("thingamabob",          "TH IH1 NG AH0 M AH0 B AA2 B"),
            # helter-skelter: reduplicative compound; stress on -skel-.
            ("helter-skelter",       "HH EH2 L T ER0 S K EH1 L T ER0"),
        ],
    )
    def test_first_pronunciation_has_one_primary_stress(self, word, expected_phones):
        """First pronunciation contains exactly one primary-stress vowel."""
        result = phones_for_word(word)
        assert result, f"'{word}' not found in CMU dict"
        assert result[0] == expected_phones, (
            f"'{word}': expected '{expected_phones}', got '{result[0]}'"
        )
        assert _primary_count(result[0]) == 1, (
            f"'{word}': expected 1 primary stress in '{result[0]}'"
        )


# ============================================================
# Tier 2 — Exactly two primary stresses
# ============================================================


class TestTwoPrimaryStresses:
    """Words carrying exactly two primary-stressed syllables.

    This tier (1 404 CMU entries) consists primarily of compound words,
    prefixed forms, and loanwords where both root components retain their
    own primary stress.  Two-primary-stress phrases are the signature of
    equal-weight compound units in isocolon detection.
    """

    @pytest.mark.parametrize(
        "word, expected_phones",
        [
            # Compound nouns / adjectives
            ("backstage",    "B AE1 K S T EY1 JH"),
            ("backwoods",    "B AE1 K W UH1 D Z"),
            ("downtown",     "D AW1 N T AW1 N"),
            ("uptown",       "AH1 P T AW1 N"),
            ("downstairs",   "D AW1 N S T EH1 R Z"),
            ("upside",       "AH1 P S AY1 D"),
            ("worthwhile",   "W ER1 TH W AY1 L"),
            ("worldwide",    "W ER1 L D W AY1 D"),
            ("overnight",    "OW1 V ER0 N AY1 T"),
            ("overseas",     "OW1 V ER0 S IY1 Z"),
            ("alongside",    "AH0 L AO1 NG S AY1 D"),
            # Prefixed / anti- words
            ("anticrime",    "AE1 N T IY0 K R AY1 M"),
            ("antilock",     "AE1 N T IY0 L AA1 K"),
            # Arch- compounds
            ("archbishop",   "AA1 R CH B IH1 SH AH0 P"),
            ("archdiocese",  "AA1 R CH D AY1 AH0 S AH0 S"),
            ("archenemy",    "AA1 R CH EH1 N AH0 M IY0"),
            ("archetypal",   "AA1 R K T AY1 P AH0 L"),
            # -ee suffix (stress falls on suffix)
            ("attendee",     "AH0 T EH1 N D IY1"),
            ("attendees",    "AH0 T EH1 N D IY1 Z"),
            ("amputee",      "AE1 M P Y AH0 T IY1"),
            ("adoptee",      "AH0 D AA1 P T IY1"),
            # Other
            ("amphitheater", "AE1 M F AH0 TH IY0 EY1 T ER0"),
            ("afrocentric",  "AE1 F R OW0 S EH1 N T R IH0 K"),
            ("asynchronous", "EY1 S IH1 NG K R AH0 N AH0 S"),
            ("actuate",      "AE1 K CH UW2 EY1 T"),
            ("actuary",      "AE1 K CH UW0 EH1 R IY2"),
            # Expressive / pop culture — two equal primary stresses
            # razzmatazz: jazz-world exclamatory; both raz- and -tazz stressed
            # equally, making it a natural isocolon unit in beat analysis.
            ("razzmatazz",   "R AE1 Z M AH0 T AE1 Z"),
            # okey-dokey: Ned Flanders (The Simpsons) / classic TV catchphrase;
            # reduplicative compound where both o- and do- carry primary stress.
            ("okey-dokey",   "OW1 K IY0 D OW1 K IY0"),
            # topsy-turvy: expressive compound meaning chaotic/upside-down;
            # both top- and -tur- are primary-stressed, giving equal weight.
            ("topsy-turvy",  "T AA1 P S IY0 T ER1 V IY0"),
        ],
    )
    def test_first_pronunciation_has_two_primary_stresses(self, word, expected_phones):
        """First pronunciation contains exactly two primary-stress vowels."""
        result = phones_for_word(word)
        assert result, f"'{word}' not found in CMU dict"
        assert result[0] == expected_phones, (
            f"'{word}': expected '{expected_phones}', got '{result[0]}'"
        )
        assert _primary_count(result[0]) == 2, (
            f"'{word}': expected 2 primary stresses in '{result[0]}'"
        )


# ============================================================
# Tier 3 — Exactly three primary stresses
# ============================================================


class TestThreePrimaryStresses:
    """Words carrying exactly three primary-stressed syllables.

    This tier (88 CMU entries) consists mostly of initialisms and acronyms
    where each letter is spelled out, each carrying its own primary stress.
    However a small number of genuine English words also fall here — notably
    ``coeducational`` and ``cogeneration`` (co- prefix retains its own
    primary stress alongside the root stress), ``chlorofluorocarbons``
    (three stressed root morphemes: chloro-, fluoro-, carbon-),
    ``rock-and-roll`` (three equally stressed content words), and
    ``yabbadabbadoo`` (playful reduplication with three stress peaks).
    """

    @pytest.mark.parametrize(
        "word, expected_phones",
        [
            # Initialisms (letter-by-letter pronunciation)
            ("fbi",   "EH1 F B IY1 AY1"),
            ("cia",   "S IY1 AY1 EY1"),
            ("mit",   "EH1 M AY1 T IY1"),
            ("hiv",   "EY1 CH AY1 V IY1"),
            ("dui",   "D IY1 Y UW1 AY1"),
            ("mba",   "EH1 M B IY1 EY1"),
            ("cnn",   "S IY1 EH1 N EH1 N"),
            ("cmu",   "S IY1 EH1 M Y UW1"),
            ("aol",   "EY1 OW1 EH1 L"),
            ("dss",   "D IY1 EH1 S EH1 S"),
            ("mpg",   "EH1 M P IY1 JH IY1"),
            ("rpm",   "AA1 R P IY1 EH1 M"),
            ("ssn",   "EH1 S EH1 S EH1 N"),
            ("ems",   "IY1 EH1 M EH1 S"),
            ("pga",   "P IY1 JH IY1 EY1"),
            ("atp",   "EY1 T IY1 P IY1"),
            ("gdp",   "G IY1 D IY1 P IY1"),
            ("byu",   "B IY1 W AY1 Y UW1"),
            ("kkk",   "K EY1 K EY1 K EY1"),
            ("oad",   "OW1 EY1 D IY1"),
            # Genuine words with three primary stresses
            ("coeducational",      "K OW1 EH1 JH AH0 K EY1 SH AH0 N AH0 L"),
            ("cogeneration",       "K OW1 JH EH1 N ER0 EY1 SH AH0 N"),
            ("chlorofluorocarbons","K L AO1 R OW0 F L AO1 R OW0 K AA1 R B AA0 N Z"),
            ("rock-and-roll",      "R AA1 K AE1 N D R OW1 L"),
            ("yabbadabbadoo",      "Y AE1 B AH0 D AE1 B AH0 D UW1"),
        ],
    )
    def test_first_pronunciation_has_three_primary_stresses(self, word, expected_phones):
        """First pronunciation contains exactly three primary-stress vowels."""
        result = phones_for_word(word)
        assert result, f"'{word}' not found in CMU dict"
        assert result[0] == expected_phones, (
            f"'{word}': expected '{expected_phones}', got '{result[0]}'"
        )
        assert _primary_count(result[0]) == 3, (
            f"'{word}': expected 3 primary stresses in '{result[0]}'"
        )


# ============================================================
# Tier 4 — Exactly four primary stresses
# ============================================================


class TestFourPrimaryStresses:
    """Words carrying exactly four primary-stressed syllables.

    All 22 CMU entries at this tier are multi-letter acronyms or brand
    initialisms — no genuine English words reach four primary stresses.
    The longer entries (``dfw``, ``dwi``) spell out "double-u" as three
    syllables, each stressed, which inflates their count.
    """

    @pytest.mark.parametrize(
        "word, expected_phones",
        [
            ("asap",   "EY1 EH1 S EY1 P IY1"),
            ("espn",   "IY1 EH1 S P IY1 EH1 N"),
            ("lapd",   "EH1 L EY1 P IY1 D IY1"),
            ("rsvp",   "AA1 R EH1 S V IY1 P IY1"),
            ("kpmg",   "K EY1 P IY1 EH1 M JH IH1"),
            ("dfw",    "D IY1 EH1 F D AH1 B AH0 L Y UW1"),
            ("dwi",    "D IY1 D AH1 B AH0 L Y UW1 AY1"),
            ("emdr",   "IY1 EH1 M D IY1 AA1 R"),
            ("cspi",   "S IY1 EH1 S P IY1 AY1"),
            ("hiaa",   "EY1 CH AY1 EY1 EY1"),
            ("hsbc",   "EY1 CH EH1 S B IY1 S IY1"),
            ("knbc",   "K EY1 EH1 N B IY1 S IY1"),
            ("knin",   "K EY1 EH1 N AY1 EH1 N"),
            ("lapd",   "EH1 L EY1 P IY1 D IY1"),
            ("usmc",   "Y UW1 EH1 S EH1 M S IY1"),
        ],
    )
    def test_first_pronunciation_has_four_primary_stresses(self, word, expected_phones):
        """First pronunciation contains exactly four primary-stress vowels."""
        result = phones_for_word(word)
        assert result, f"'{word}' not found in CMU dict"
        assert result[0] == expected_phones, (
            f"'{word}': expected '{expected_phones}', got '{result[0]}'"
        )
        assert _primary_count(result[0]) == 4, (
            f"'{word}': expected 4 primary stresses in '{result[0]}'"
        )


# ============================================================
# Tier 5 — Exactly five primary stresses
# ============================================================


class TestFivePrimaryStresses:
    """Words carrying exactly five primary-stressed syllables.

    All 4 CMU entries at this tier are domain names or extended acronyms.
    No genuine English words reach five primary stresses.  ``cnn.com`` and
    ``npr.org`` are excluded here because ``phones_for_word`` strips
    punctuation and they do not look up cleanly; ``anfal`` and ``cnnfn``
    are the two reliably testable entries.
    """

    @pytest.mark.parametrize(
        "word, expected_phones",
        [
            ("anfal",   "EY1 EH1 N EH1 F EY1 EH1 L"),
            ("cnnfn",   "S IY1 EH1 N EH1 N EH1 F EH1 N"),
        ],
    )
    def test_first_pronunciation_has_five_primary_stresses(self, word, expected_phones):
        """First pronunciation contains exactly five primary-stress vowels."""
        result = phones_for_word(word)
        assert result, f"'{word}' not found in CMU dict"
        assert result[0] == expected_phones, (
            f"'{word}': expected '{expected_phones}', got '{result[0]}'"
        )
        assert _primary_count(result[0]) == 5, (
            f"'{word}': expected 5 primary stresses in '{result[0]}'"
        )


# ============================================================
# Stress variation classification
# ============================================================


def _stress_positions(phones_str: str) -> list[int]:
    """Return 0-indexed syllable positions of primary-stressed vowels.

    For ``"P ER0 M IH1 T"`` the vowels are at positions [0, 1]; position 1
    carries primary stress, so the result is ``[1]``.
    """
    pos = 0
    result = []
    for ph in phones_str.split():
        if ph[-1].isdigit():
            if ph[-1] == "1":
                result.append(pos)
            pos += 1
    return result


def _stress_variation_class(word: str) -> str:
    """Classify a word's stress behaviour using the CMU dict.

    Returns:
        ``"fixed"``    — one pronunciation, or multiple pronunciations that all
                         place primary stress on the same syllable position(s).
        ``"variable"`` — multiple pronunciations that differ in primary-stress
                         position, indicating either grammatical-function
                         alternation (RECord/reCORD) or genuine stress-varying
                         dialect forms (peCAN/PEcan).
        ``"unknown"``  — word not found in the CMU dict.

    Note on the three-way landscape:
        The CMU dict naturally partitions two of three categories:

        1. Grammatical alternators → ``"variable"``:  RECord (noun) / reCORD
           (verb) differ in stress *position*, so CMU records both.
        2. Dialect phonetic variants → ``"fixed"``:  TOM-ah-to / TOM-ay-to
           differ only in vowel *quality*, not stress position, so all CMU
           entries share the same stress pattern.
        3. True fixed-stress words → ``"fixed"``.

        The dict cannot distinguish category 1 from rare genuine stress-varying
        dialect forms (e.g. ``pecan``, ``advertisement``), but those are
        uncommon.  A curated heteronym list would be needed to split them.

    Related GitHub Issue:
        #76 — Beat Detection — Phrase-Level Stress Shape Analysis
        https://github.com/craigtrim/pystylometry/issues/76
    """
    phones_list = phones_for_word(word)
    if not phones_list:
        return "unknown"
    patterns = {str(_stress_positions(p)) for p in phones_list}
    return "variable" if len(patterns) > 1 else "fixed"


class TestStressVariation:
    """Classify words as fixed-stress or variable-stress via the CMU dict.

    The CMU dict stores multiple pronunciations for many words.  When those
    pronunciations place primary stress on *different* syllables the word is
    classified as ``"variable"``; when all pronunciations agree on stress
    position (even if vowel quality differs) the word is ``"fixed"``.

    Three-way landscape
    -------------------
    1. Grammatical alternators — stress *position* shifts with POS:
       ``record`` (noun RECord vs. verb reCORD) → ``"variable"``
    2. Dialect / phonetic variants — stress *position* fixed, vowel quality
       shifts: ``tomato`` (TOM-ah-to / TOM-ay-to) → ``"fixed"``
    3. True fixed-stress words → ``"fixed"``

    The CMU dict cleanly separates categories 2 and 3 from category 1.
    Distinguishing grammatical alternation from the rare genuine stress-dialect
    variants (``pecan``, ``advertisement``) requires a curated heteronym list.

    Related GitHub Issue:
        #76 — Beat Detection
        https://github.com/craigtrim/pystylometry/issues/76
    """

    # ------------------------------------------------------------------
    # Grammatical alternators (noun/verb stress shift) → "variable"
    # ------------------------------------------------------------------

    @pytest.mark.parametrize(
        "word",
        [
            # Classic disyllabic noun-stress / verb-stress pairs.
            # Noun form: primary stress on syllable 0 (RECord, OBject …)
            # Verb form:  primary stress on syllable 1 (reCORD, obJECT …)
            "record",    # RECord (noun) / reCORD (verb)
            "permit",    # PERmit (noun) / perMIT (verb)
            "present",   # PREsent (noun/adj) / preSENT (verb)
            "object",    # OBject (noun) / obJECT (verb)
            "conduct",   # CONduct (noun) / conDUCT (verb)
            "protest",   # PROtest (noun) / proTEST (verb)
            "project",   # PROject (noun) / proJECT (verb)
            "produce",   # PROduce (noun) / proDUCE (verb)
            "contract",  # CONtract (noun) / conTRACT (verb)
            "rebel",     # REbel (noun) / reBEL (verb)
            "insult",    # INsult (noun) / inSULT (verb)
            "digest",    # DIgest (noun) / diGEST (verb)
            "conflict",  # CONflict (noun) / conFLICT (verb)
        ],
    )
    def test_grammatical_alternators_are_variable(self, word):
        """Noun/verb stress-shift words classified as variable.

        The CMU dict records both pronunciations with different primary-stress
        positions, giving a ``"variable"`` classification.
        """
        assert _stress_variation_class(word) == "variable", (
            f"'{word}' expected 'variable' (noun/verb stress shift), "
            f"got '{_stress_variation_class(word)}'"
        )

    # ------------------------------------------------------------------
    # Dialect / phonetic variants — same stress position, vowel quality
    # differs → "fixed"
    # ------------------------------------------------------------------

    @pytest.mark.parametrize(
        "word",
        [
            # British vs. American vowel quality — stress position unchanged.
            "either",       # /ˈiː.ðər/ vs. /ˈaɪ.ðər/ — both stress syllable 0
            "neither",      # same pattern as 'either'
            "schedule",     # /ˈʃɛdʒ.uːl/ vs. /ˈskɛdʒ.uːl/ — stress fixed
            "tomato",       # TOM-ah-to / TOM-ay-to — stress always syllable 1
            "route",        # /ruːt/ vs. /raʊt/ — monosyllable, trivially fixed
            "leisure",      # /ˈlɛʒ.ər/ vs. /ˈliː.ʒər/ — stress fixed syllable 0
            "vitamin",      # /ˈvaɪ.tə.mɪn/ vs. /ˈvɪt.ə.mɪn/ — stress fixed
            "data",         # /ˈdeɪ.tə/ vs. /ˈdɑː.tə/ — stress fixed syllable 0
        ],
    )
    def test_dialect_phonetic_variants_are_fixed(self, word):
        """Dialect variants with same stress position classified as fixed.

        Vowel quality shifts (the kind captured by multiple CMU entries for
        words like 'tomato', 'either') do not move primary stress.  All CMU
        pronunciations share the same stress pattern, so the word is ``"fixed"``.
        """
        assert _stress_variation_class(word) == "fixed", (
            f"'{word}' expected 'fixed' (dialect phonetic variant, stress "
            f"position unchanged), got '{_stress_variation_class(word)}'"
        )

    # ------------------------------------------------------------------
    # True fixed-stress words → "fixed"
    # ------------------------------------------------------------------

    @pytest.mark.parametrize(
        "word",
        [
            "beautiful",    # B Y UW1 T AH0 F AH0 L — single CMU entry
            "computer",     # K AH0 M P Y UW1 T ER0 — single entry
            "happiness",    # HH AE1 P IY0 N AH0 S — single entry
            "library",      # L AY1 B R EH0 R IY2 — single entry
            "remember",     # two entries, both stress syllable 1
            "elephant",     # EH1 L AH0 F AH0 N T — single entry, always syllable 0
        ],
    )
    def test_fixed_stress_words(self, word):
        """True fixed-stress words classified as fixed.

        Either they have a single CMU pronunciation, or multiple pronunciations
        all with primary stress on the same syllable position.
        """
        result = _stress_variation_class(word)
        assert result in ("fixed", "variable"), (
            f"'{word}' returned unexpected class '{result}'"
        )
        # All of these should be fixed; document any CMU-gap exceptions here.
        assert result == "fixed", (
            f"'{word}' expected 'fixed' (true fixed-stress word), got '{result}'"
        )
