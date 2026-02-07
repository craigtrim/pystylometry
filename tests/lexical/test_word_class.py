"""Comprehensive tests for word morphological classification.

Tests the classify_word() function and WordClass dataclass from
pystylometry.lexical.word_class, covering:

- Every curated word list entry
- Every regex pattern
- Edge cases (empty strings, mixed case, unusual input)
- The unclassified fallback for each L1 category
- Label formatting

Related GitHub Issue:
    #51 — Word morphological classification taxonomy
    https://github.com/craigtrim/pystylometry/issues/51
"""

import pytest

from pystylometry.lexical.word_class import WordClass, classify_word

# ===================================================================
# WordClass dataclass tests
# ===================================================================


class TestWordClassDataclass:
    """Tests for the WordClass dataclass and label property."""

    def test_label_l1_only(self):
        wc = WordClass("hello", "lexical")
        assert wc.label == "lexical"

    def test_label_l1_l2(self):
        wc = WordClass("let's", "apostrophe", "enclitic")
        assert wc.label == "apostrophe.enclitic"

    def test_label_l1_l2_l3(self):
        wc = WordClass("don't", "apostrophe", "contraction", "negative")
        assert wc.label == "apostrophe.contraction.negative"

    def test_frozen(self):
        wc = WordClass("hello", "lexical")
        with pytest.raises(AttributeError):
            wc.l1 = "changed"  # type: ignore[misc]

    def test_word_preserved(self):
        wc = classify_word("Don't")
        assert wc.word == "Don't"

    def test_equality(self):
        a = WordClass("don't", "apostrophe", "contraction", "negative")
        b = WordClass("don't", "apostrophe", "contraction", "negative")
        assert a == b

    def test_label_none_l3(self):
        wc = WordClass("word", "hyphenated", "prefixed", None)
        assert wc.label == "hyphenated.prefixed"


# ===================================================================
# L1: lexical — Standard lexical words (all flags false)
# ===================================================================


class TestLexical:
    """Pure a-z words should classify as 'lexical'."""

    @pytest.mark.parametrize(
        "word",
        [
            "hello",
            "trembling",
            "exhaled",
            "avalanche",
            "quivering",
            "blew",
            "the",
            "a",
            "x",
            "abcdefghijklmnopqrstuvwxyz",
        ],
    )
    def test_standard_words(self, word):
        result = classify_word(word)
        assert result.l1 == "lexical"
        assert result.l2 is None
        assert result.l3 is None
        assert result.label == "lexical"

    def test_case_insensitive_still_lexical(self):
        """Uppercase letters are still a-zA-Z, so lexical."""
        result = classify_word("Hello")
        assert result.l1 == "lexical"

    def test_all_caps(self):
        result = classify_word("HELLO")
        assert result.l1 == "lexical"


# ===================================================================
# L1: apostrophe — Negative contractions
# ===================================================================


class TestNegativeContractions:
    """Every negative contraction should classify correctly."""

    @pytest.mark.parametrize(
        "word",
        [
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
        ],
    )
    def test_negative_contraction(self, word):
        result = classify_word(word)
        assert result.label == "apostrophe.contraction.negative"

    def test_case_insensitive(self):
        result = classify_word("Don't")
        assert result.label == "apostrophe.contraction.negative"

    def test_all_caps(self):
        result = classify_word("DON'T")
        assert result.label == "apostrophe.contraction.negative"


# ===================================================================
# L1: apostrophe — Copula enclitics
# ===================================================================


class TestCopulaEnclitics:
    """Copula contractions ('s=is/has, 're=are, 'm=am)."""

    @pytest.mark.parametrize(
        "word",
        [
            "it's",
            "he's",
            "she's",
            "that's",
            "what's",
            "who's",
            "there's",
            "here's",
            "where's",
            "how's",
            "why's",
            "when's",
            "one's",
            "everybody's",
            "everyone's",
            "everything's",
            "nobody's",
            "nothing's",
            "somebody's",
            "someone's",
            "something's",
        ],
    )
    def test_s_copula(self, word):
        result = classify_word(word)
        assert result.label == "apostrophe.contraction.copula"

    @pytest.mark.parametrize("word", ["they're", "we're", "you're"])
    def test_re_copula(self, word):
        result = classify_word(word)
        assert result.label == "apostrophe.contraction.copula"

    def test_m_copula(self):
        result = classify_word("i'm")
        assert result.label == "apostrophe.contraction.copula"

    def test_case_insensitive(self):
        result = classify_word("It's")
        assert result.label == "apostrophe.contraction.copula"


# ===================================================================
# L1: apostrophe — Auxiliary enclitics
# ===================================================================


class TestAuxiliaryEnclitics:
    """Auxiliary contractions ('ll, 'd, 've)."""

    @pytest.mark.parametrize(
        "word",
        [
            "i'll",
            "you'll",
            "he'll",
            "she'll",
            "it'll",
            "we'll",
            "they'll",
            "that'll",
            "there'll",
            "what'll",
            "who'll",
        ],
    )
    def test_ll_auxiliary(self, word):
        result = classify_word(word)
        assert result.label == "apostrophe.contraction.auxiliary"

    @pytest.mark.parametrize(
        "word",
        [
            "i'd",
            "you'd",
            "he'd",
            "she'd",
            "it'd",
            "we'd",
            "they'd",
            "that'd",
            "there'd",
            "what'd",
            "who'd",
            "how'd",
        ],
    )
    def test_d_auxiliary(self, word):
        result = classify_word(word)
        assert result.label == "apostrophe.contraction.auxiliary"

    @pytest.mark.parametrize(
        "word",
        [
            "i've",
            "you've",
            "we've",
            "they've",
            "who've",
            "could've",
            "should've",
            "would've",
            "might've",
            "must've",
        ],
    )
    def test_ve_auxiliary(self, word):
        result = classify_word(word)
        assert result.label == "apostrophe.contraction.auxiliary"


# ===================================================================
# L1: apostrophe — Enclitic (let's)
# ===================================================================


class TestEnclitic:
    """Special-case enclitic: let's."""

    def test_lets(self):
        assert classify_word("let's").label == "apostrophe.enclitic"

    def test_lets_case_insensitive(self):
        assert classify_word("Let's").label == "apostrophe.enclitic"


# ===================================================================
# L1: apostrophe — Aphetic forms
# ===================================================================


class TestApheticForms:
    """Words with initial elision (apostrophe at start)."""

    @pytest.mark.parametrize(
        "word",
        ["'twas", "'tis", "'twill", "'twould", "'twere", "'twasn't"],
    )
    def test_aphetic_archaic(self, word):
        result = classify_word(word)
        assert result.label == "apostrophe.aphetic.archaic"

    @pytest.mark.parametrize(
        "word",
        ["'gainst", "'midst", "'mid", "'mongst", "'neath", "'pon", "'twixt"],
    )
    def test_aphetic_poetic(self, word):
        result = classify_word(word)
        assert result.label == "apostrophe.aphetic.poetic"


# ===================================================================
# L1: apostrophe — Dialectal forms
# ===================================================================


class TestDialectalForms:
    """Dialectal / informal reductions."""

    @pytest.mark.parametrize("word", ["'em", "'er", "'im", "'is"])
    def test_pronoun_reduction(self, word):
        result = classify_word(word)
        assert result.label == "apostrophe.dialectal.pronoun_reduction"

    @pytest.mark.parametrize(
        "word", ["ma'am", "o'clock", "ne'er", "e'er", "o'er", "ha'penny"]
    )
    def test_medial(self, word):
        result = classify_word(word)
        assert result.label == "apostrophe.dialectal.medial"

    @pytest.mark.parametrize(
        "word",
        [
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
        ],
    )
    def test_initial_dialectal(self, word):
        result = classify_word(word)
        assert result.label == "apostrophe.dialectal.initial"

    @pytest.mark.parametrize("word", ["y'all", "ya'll"])
    def test_regional(self, word):
        result = classify_word(word)
        assert result.label == "apostrophe.dialectal.regional"

    @pytest.mark.parametrize(
        "word",
        ["runnin'", "jumpin'", "somethin'", "nothin'", "goin'", "comin'"],
    )
    def test_g_dropping(self, word):
        result = classify_word(word)
        assert result.label == "apostrophe.dialectal.g_dropping"


# ===================================================================
# L1: apostrophe — Possessives (by elimination)
# ===================================================================


class TestPossessives:
    """Words with 's or s' not in contraction/enclitic lists."""

    @pytest.mark.parametrize(
        "word",
        ["dog's", "john's", "mother's", "children's", "world's"],
    )
    def test_singular_possessive(self, word):
        result = classify_word(word)
        assert result.label == "apostrophe.possessive.singular"

    @pytest.mark.parametrize(
        "word",
        ["dogs'", "parents'", "teachers'", "boys'", "workers'"],
    )
    def test_plural_possessive(self, word):
        result = classify_word(word)
        assert result.label == "apostrophe.possessive.plural"

    def test_not_confused_with_contraction(self):
        """'it's' should be copula, not possessive."""
        result = classify_word("it's")
        assert result.l2 == "contraction"
        assert result.l2 != "possessive"


# ===================================================================
# L1: apostrophe — Unclassified
# ===================================================================


class TestApostropheUnclassified:
    """Apostrophe words that don't match any known pattern."""

    def test_unusual_apostrophe_word(self):
        result = classify_word("x'z")
        assert result.l1 == "apostrophe"
        assert result.l2 == "unclassified"
        assert result.label == "apostrophe.unclassified"


# ===================================================================
# L1: hyphenated — self- compounds
# ===================================================================


class TestSelfCompounds:
    """self-* compounds."""

    @pytest.mark.parametrize(
        "word",
        [
            "self-esteem",
            "self-care",
            "self-aware",
            "self-made",
            "self-taught",
            "self-portrait",
            "self-respect",
            "self-control",
        ],
    )
    def test_self_compound(self, word):
        result = classify_word(word)
        assert result.label == "hyphenated.compound.self"


# ===================================================================
# L1: hyphenated — Prefixed forms
# ===================================================================


class TestPrefixedForms:
    """Productive prefix + hyphen patterns."""

    @pytest.mark.parametrize(
        "word,prefix",
        [
            ("re-enter", "re"),
            ("re-examine", "re"),
            ("co-operate", "co"),
            ("co-author", "co"),
            ("pre-war", "pre"),
            ("pre-existing", "pre"),
            ("post-war", "post"),
            ("post-mortem", "post"),
            ("anti-hero", "anti"),
            ("anti-war", "anti"),
            ("non-fiction", "non"),
            ("non-stop", "non"),
            ("ex-husband", "ex"),
            ("ex-wife", "ex"),
            ("semi-final", "semi"),
            ("semi-circle", "semi"),
            ("mid-morning", "mid"),
            ("mid-century", "mid"),
            ("over-react", "over"),
            ("under-estimate", "under"),
            ("cross-examine", "cross"),
            ("cross-reference", "cross"),
            ("half-hearted", "half"),
            ("half-brother", "half"),
            ("all-purpose", "all"),
            ("all-knowing", "all"),
            ("counter-attack", "counter"),
            ("inter-connect", "inter"),
            ("multi-layered", "multi"),
            ("sub-committee", "sub"),
            ("super-hero", "super"),
            ("trans-atlantic", "trans"),
            ("ultra-modern", "ultra"),
            ("vice-president", "vice"),
            ("well-known", "well"),
            ("out-perform", "out"),
        ],
    )
    def test_prefixed(self, word, prefix):
        result = classify_word(word)
        assert result.label == "hyphenated.prefixed", (
            f"{word} (prefix={prefix}) should be hyphenated.prefixed"
        )


# ===================================================================
# L1: hyphenated — Number words
# ===================================================================


class TestNumberWords:
    """Spelled-out number words with hyphens."""

    @pytest.mark.parametrize(
        "word",
        [
            "twenty-one",
            "twenty-two",
            "twenty-three",
            "thirty-four",
            "forty-five",
            "fifty-six",
            "sixty-seven",
            "seventy-eight",
            "eighty-nine",
            "ninety-nine",
        ],
    )
    def test_cardinal_number_word(self, word):
        result = classify_word(word)
        assert result.label == "hyphenated.number_word"

    @pytest.mark.parametrize(
        "word",
        [
            "twenty-first",
            "thirty-second",
            "forty-third",
            "fifty-fourth",
            "sixty-fifth",
            "seventy-sixth",
            "eighty-seventh",
            "ninety-eighth",
            "twenty-ninth",
        ],
    )
    def test_ordinal_number_word(self, word):
        result = classify_word(word)
        assert result.label == "hyphenated.number_word"


# ===================================================================
# L1: hyphenated — Reduplicated forms
# ===================================================================


class TestReduplicated:
    """Reduplicated, rhyming, and ablaut compounds."""

    @pytest.mark.parametrize(
        "word",
        [
            "so-so",
            "no-no",
            "fifty-fifty",
            "bye-bye",
            "boo-boo",
            "hush-hush",
            "knock-knock",
            "tut-tut",
            "tsk-tsk",
            "ta-ta",
            "choo-choo",
            "goody-goody",
            "pom-pom",
            "murmur-murmur",
        ],
    )
    def test_exact_reduplication(self, word):
        result = classify_word(word)
        assert result.label == "hyphenated.reduplicated.exact"

    @pytest.mark.parametrize(
        "word",
        [
            "helter-skelter",
            "hurly-burly",
            "nitty-gritty",
            "willy-nilly",
            "wishy-washy",
            "hoity-toity",
            "itsy-bitsy",
            "easy-peasy",
            "okey-dokey",
            "namby-pamby",
            "razzle-dazzle",
            "teeny-weeny",
            "argy-bargy",
            "higgledy-piggledy",
            "hokey-pokey",
            "hotch-potch",
            "hurry-scurry",
            "hee-haw",
        ],
    )
    def test_rhyming_reduplication(self, word):
        result = classify_word(word)
        assert result.label == "hyphenated.reduplicated.rhyming"

    @pytest.mark.parametrize(
        "word",
        [
            "zig-zag",
            "flip-flop",
            "ping-pong",
            "tick-tock",
            "hip-hop",
            "clip-clop",
            "criss-cross",
            "dilly-dally",
            "ding-dong",
            "kit-kat",
            "knick-knack",
            "mish-mash",
            "pitter-patter",
            "riff-raff",
            "see-saw",
            "shilly-shally",
            "sing-song",
            "tip-top",
        ],
    )
    def test_ablaut_reduplication(self, word):
        result = classify_word(word)
        assert result.label == "hyphenated.reduplicated.ablaut"


# ===================================================================
# L1: hyphenated — Phrasal modifiers
# ===================================================================


class TestPhrasalModifiers:
    """Multi-hyphen chains with connecting words."""

    @pytest.mark.parametrize(
        "word",
        [
            "state-of-the-art",
            "run-of-the-mill",
            "matter-of-fact",
            "out-of-date",
            "up-to-date",
            "man-of-war",
            "out-of-order",
            "tongue-in-cheek",
            "down-to-earth",
            "face-to-face",
            "hand-to-hand",
            "back-to-back",
            "larger-than-life",
            "better-than-average",
        ],
    )
    def test_phrasal_modifier(self, word):
        result = classify_word(word)
        assert result.label == "hyphenated.phrasal_modifier"


# ===================================================================
# L1: hyphenated — Directional compounds
# ===================================================================


class TestDirectional:
    """Compass / directional compounds."""

    @pytest.mark.parametrize(
        "word",
        [
            "north-east",
            "north-west",
            "south-east",
            "south-west",
            "north-eastern",
            "south-western",
            "north-north-east",
            "south-south-west",
        ],
    )
    def test_directional(self, word):
        result = classify_word(word)
        assert result.label == "hyphenated.directional"


# ===================================================================
# L1: hyphenated — Unclassified
# ===================================================================


class TestHyphenatedUnclassified:
    """Hyphenated words that don't match any known pattern."""

    def test_novel_compound(self):
        """An unusual compound not in any word list or regex."""
        result = classify_word("banana-phone")
        assert result.l1 == "hyphenated"
        assert result.l2 == "unclassified"
        assert result.label == "hyphenated.unclassified"


# ===================================================================
# L1: apostrophe_hyphenated — Compound reductions
# ===================================================================


class TestApostropheHyphenated:
    """Words with both apostrophe and hyphen."""

    @pytest.mark.parametrize(
        "word",
        [
            "jack-o'-lantern",
            "will-o'-the-wisp",
            "cat-o'-nine-tails",
            "tam-o'-shanter",
        ],
    )
    def test_compound_reduction(self, word):
        result = classify_word(word)
        assert result.label == "apostrophe_hyphenated.compound_reduction"

    def test_unknown_apostrophe_hyphen(self):
        """An unknown word with both should fallback gracefully."""
        result = classify_word("foo-bar's-baz")
        # Should try apostrophe patterns, then hyphen patterns,
        # then fall through to unclassified
        assert result.l1 in (
            "apostrophe_hyphenated",
            "apostrophe",
            "hyphenated",
        )


# ===================================================================
# L1: unicode
# ===================================================================


class TestUnicode:
    """Words with non-ASCII characters."""

    @pytest.mark.parametrize(
        "word",
        ["café", "naïve", "résumé", "fiancée", "cliché", "über", "jalapeño"],
    )
    def test_unicode_words(self, word):
        result = classify_word(word)
        assert result.l1 == "unicode"
        # Currently all go to unclassified (word lists TBD)
        assert result.l2 == "unclassified"


# ===================================================================
# L1: numeric
# ===================================================================


class TestNumeric:
    """Words containing digits."""

    @pytest.mark.parametrize(
        "word,expected_label",
        [
            ("1st", "numeric.ordinal"),
            ("2nd", "numeric.ordinal"),
            ("3rd", "numeric.ordinal"),
            ("4th", "numeric.ordinal"),
            ("21st", "numeric.ordinal"),
            ("100th", "numeric.ordinal"),
            ("42nd", "numeric.ordinal"),
            ("53rd", "numeric.ordinal"),
        ],
    )
    def test_ordinal(self, word, expected_label):
        result = classify_word(word)
        assert result.label == expected_label

    @pytest.mark.parametrize(
        "word",
        ["mp3", "h2o", "b2b", "3d", "4k"],
    )
    def test_numeric_unclassified(self, word):
        """Alphanumeric words not matching ordinal → numeric.unclassified."""
        result = classify_word(word)
        assert result.l1 == "numeric"
        assert result.l2 == "unclassified"


# ===================================================================
# L1: other
# ===================================================================


class TestOther:
    """Words with non-a-z characters not covered by other flags."""

    @pytest.mark.parametrize(
        "word",
        ["c#", "f#", "rock&roll", "user@domain"],
    )
    def test_other_symbols(self, word):
        result = classify_word(word)
        assert result.l1 == "other"
        assert result.l2 == "unclassified"


# ===================================================================
# Edge cases
# ===================================================================


class TestEdgeCases:
    """Boundary conditions and unusual inputs."""

    def test_single_letter(self):
        result = classify_word("a")
        assert result.label == "lexical"

    def test_single_apostrophe(self):
        """A lone apostrophe."""
        result = classify_word("'")
        assert result.l1 == "apostrophe"

    def test_single_hyphen(self):
        """A lone hyphen."""
        result = classify_word("-")
        assert result.l1 == "hyphenated"

    def test_empty_string(self):
        """Empty string should still return a result."""
        result = classify_word("")
        assert result.l1 == "lexical"

    def test_mixed_case_preserved_in_word(self):
        """Original case should be preserved in result.word."""
        result = classify_word("Don't")
        assert result.word == "Don't"
        assert result.label == "apostrophe.contraction.negative"

    def test_all_caps_contraction(self):
        result = classify_word("WON'T")
        assert result.label == "apostrophe.contraction.negative"

    def test_number_with_apostrophe(self):
        """e.g. '90s — has apostrophe and is short."""
        result = classify_word("'90s")
        # Has apostrophe but also non-a-z chars (digits)
        # Apostrophe takes precedence in current logic
        assert result.l1 == "apostrophe"

    def test_self_hyphen_not_confused_with_prefix(self):
        """'self-' should be compound.self, not prefixed."""
        result = classify_word("self-esteem")
        assert result.label == "hyphenated.compound.self"
        assert result.l2 == "compound"
        assert result.l3 == "self"

    def test_phrasal_modifier_priority_over_prefix(self):
        """'out-of-date' should be phrasal_modifier, not prefixed with 'out-'."""
        result = classify_word("out-of-date")
        assert result.label == "hyphenated.phrasal_modifier"

    def test_its_vs_possessive(self):
        """'it's' is in the copula list, not possessive."""
        assert classify_word("it's").l2 == "contraction"
        assert classify_word("it's").l3 == "copula"

    def test_hes_vs_possessive(self):
        """'he's' is in the copula list, not possessive."""
        assert classify_word("he's").l2 == "contraction"

    def test_dogs_is_possessive(self):
        """'dog's' is NOT in any contraction list, so it's possessive."""
        assert classify_word("dog's").l2 == "possessive"
        assert classify_word("dog's").l3 == "singular"

    def test_dogs_plural_possessive(self):
        """'dogs'' should be plural possessive."""
        assert classify_word("dogs'").l2 == "possessive"
        assert classify_word("dogs'").l3 == "plural"


# ===================================================================
# Regression: ensure no false positives
# ===================================================================


class TestNoFalsePositives:
    """Words that should NOT match various categories."""

    def test_self_not_classified_as_compound(self):
        """The word 'self' alone (no hyphen) is lexical."""
        assert classify_word("self").label == "lexical"

    def test_non_not_classified_as_prefixed(self):
        """The word 'non' alone (no hyphen) is lexical."""
        assert classify_word("non").label == "lexical"

    def test_re_not_classified_as_prefixed(self):
        """The word 're' alone is lexical."""
        assert classify_word("re").label == "lexical"

    def test_twenty_not_classified_as_number_word(self):
        """'twenty' alone (no hyphen) is lexical."""
        assert classify_word("twenty").label == "lexical"

    def test_digits_only_not_ordinal(self):
        """Pure digits like '42' are numeric.unclassified, not ordinal."""
        result = classify_word("42")
        assert result.l1 == "numeric"
        assert result.l2 == "unclassified"


# ===================================================================
# Bulk validation: all word lists are reachable
# ===================================================================


class TestAllWordListsReachable:
    """Verify that every entry in every curated word list actually classifies
    to the expected label when passed through classify_word()."""

    def test_all_negative_contractions(self):
        from pystylometry.lexical.word_class import _NEGATIVE_CONTRACTIONS

        for word in _NEGATIVE_CONTRACTIONS:
            result = classify_word(word)
            assert result.label == "apostrophe.contraction.negative", (
                f"'{word}' should be apostrophe.contraction.negative, "
                f"got {result.label}"
            )

    def test_all_copula_enclitics(self):
        from pystylometry.lexical.word_class import _COPULA_ENCLITICS

        for word in _COPULA_ENCLITICS:
            result = classify_word(word)
            assert result.label == "apostrophe.contraction.copula", (
                f"'{word}' should be apostrophe.contraction.copula, "
                f"got {result.label}"
            )

    def test_all_auxiliary_enclitics(self):
        from pystylometry.lexical.word_class import _AUXILIARY_ENCLITICS

        for word in _AUXILIARY_ENCLITICS:
            result = classify_word(word)
            assert result.label == "apostrophe.contraction.auxiliary", (
                f"'{word}' should be apostrophe.contraction.auxiliary, "
                f"got {result.label}"
            )

    def test_all_enclitics(self):
        from pystylometry.lexical.word_class import _ENCLITICS

        for word in _ENCLITICS:
            result = classify_word(word)
            assert result.label == "apostrophe.enclitic", (
                f"'{word}' should be apostrophe.enclitic, got {result.label}"
            )

    def test_all_aphetic_archaic(self):
        from pystylometry.lexical.word_class import _APHETIC_ARCHAIC

        for word in _APHETIC_ARCHAIC:
            result = classify_word(word)
            assert result.label == "apostrophe.aphetic.archaic", (
                f"'{word}' should be apostrophe.aphetic.archaic, "
                f"got {result.label}"
            )

    def test_all_aphetic_poetic(self):
        from pystylometry.lexical.word_class import _APHETIC_POETIC

        for word in _APHETIC_POETIC:
            result = classify_word(word)
            assert result.label == "apostrophe.aphetic.poetic", (
                f"'{word}' should be apostrophe.aphetic.poetic, "
                f"got {result.label}"
            )

    def test_all_dialectal_pronoun_reduction(self):
        from pystylometry.lexical.word_class import _DIALECTAL_PRONOUN_REDUCTION

        for word in _DIALECTAL_PRONOUN_REDUCTION:
            result = classify_word(word)
            assert result.label == "apostrophe.dialectal.pronoun_reduction", (
                f"'{word}' should be apostrophe.dialectal.pronoun_reduction, "
                f"got {result.label}"
            )

    def test_all_dialectal_medial(self):
        from pystylometry.lexical.word_class import _DIALECTAL_MEDIAL

        for word in _DIALECTAL_MEDIAL:
            result = classify_word(word)
            # jack-o'-lantern is in both _DIALECTAL_MEDIAL and
            # _APOSTROPHE_HYPHENATED; it should classify as the
            # apostrophe_hyphenated form because it has both flags
            if "'" in word and "-" in word:
                continue  # skip dual-flag entries
            assert result.label == "apostrophe.dialectal.medial", (
                f"'{word}' should be apostrophe.dialectal.medial, "
                f"got {result.label}"
            )

    def test_all_dialectal_initial(self):
        from pystylometry.lexical.word_class import _DIALECTAL_INITIAL

        for word in _DIALECTAL_INITIAL:
            result = classify_word(word)
            assert result.label == "apostrophe.dialectal.initial", (
                f"'{word}' should be apostrophe.dialectal.initial, "
                f"got {result.label}"
            )

    def test_all_dialectal_yall(self):
        from pystylometry.lexical.word_class import _DIALECTAL_YALL

        for word in _DIALECTAL_YALL:
            result = classify_word(word)
            assert result.label == "apostrophe.dialectal.regional", (
                f"'{word}' should be apostrophe.dialectal.regional, "
                f"got {result.label}"
            )

    def test_all_reduplicated_exact(self):
        from pystylometry.lexical.word_class import _REDUPLICATED_EXACT

        for word in _REDUPLICATED_EXACT:
            result = classify_word(word)
            assert result.label == "hyphenated.reduplicated.exact", (
                f"'{word}' should be hyphenated.reduplicated.exact, "
                f"got {result.label}"
            )

    def test_all_reduplicated_rhyming(self):
        from pystylometry.lexical.word_class import _REDUPLICATED_RHYMING

        for word in _REDUPLICATED_RHYMING:
            result = classify_word(word)
            assert result.label == "hyphenated.reduplicated.rhyming", (
                f"'{word}' should be hyphenated.reduplicated.rhyming, "
                f"got {result.label}"
            )

    def test_all_reduplicated_ablaut(self):
        from pystylometry.lexical.word_class import _REDUPLICATED_ABLAUT

        for word in _REDUPLICATED_ABLAUT:
            result = classify_word(word)
            assert result.label == "hyphenated.reduplicated.ablaut", (
                f"'{word}' should be hyphenated.reduplicated.ablaut, "
                f"got {result.label}"
            )

    def test_all_directional(self):
        from pystylometry.lexical.word_class import _DIRECTIONAL

        for word in _DIRECTIONAL:
            result = classify_word(word)
            assert result.label == "hyphenated.directional", (
                f"'{word}' should be hyphenated.directional, "
                f"got {result.label}"
            )

    def test_all_apostrophe_hyphenated(self):
        from pystylometry.lexical.word_class import _APOSTROPHE_HYPHENATED

        for word in _APOSTROPHE_HYPHENATED:
            result = classify_word(word)
            assert (
                result.label == "apostrophe_hyphenated.compound_reduction"
            ), (
                f"'{word}' should be "
                f"apostrophe_hyphenated.compound_reduction, "
                f"got {result.label}"
            )
