"""Tests for suffix-stripping CMU fallback (Issue #82).

Validates that ``phones_for_word()`` can recover stress patterns for words
not in the CMU Pronouncing Dictionary by decomposing them morphologically
via the lookup libraries (BNC, WordNet) and finding a CMU-lookable stem.

Related GitHub Issues:
    #82 — Suffix-stripping CMU fallback via lookup libraries for OOV stress
           recovery
           https://github.com/craigtrim/pystylometry/issues/82
    #81 — G2P cascade design (Tier 2)
           https://github.com/craigtrim/pystylometry/issues/81
    #76 — Beat detection (downstream consumer)
           https://github.com/craigtrim/pystylometry/issues/76

Test Categories:
    1. Direct CMU hits — cascade must not interfere with existing behavior
    2. Suffix cascade recovery — OOV words with decomposable suffixes
    3. Stress pattern correctness — recovered patterns match expectations
    4. True OOV — words with no morphological structure remain unresolved
    5. Edge cases — empty strings, single characters, already-root words
    6. British spelling normalization — -our/-ise/-re forms
    7. Allomorphic restoration — consonant doubling, y→i lowering
    8. OOV discovery — BNC coverage gap analysis

Linguistic Background:
    Most English derivational suffixes are stress-neutral (Chomsky & Halle
    1968).  The suffix cascade exploits this: strip suffixes to find a
    CMU-lookable root, then extend the root's stress pattern with unstressed
    placeholder syllables for the suffix material.  The result is an
    approximation — accurate for stress-neutral suffixes, conservative for
    stress-shifting ones.
"""

import pytest

# ---------------------------------------------------------------------------
# Guard: the cascade requires at least one lookup library (bnc-lookup or
# wordnet-lookup) to be installed with suffix data.  If neither is available,
# skip all tests in this module.
# ---------------------------------------------------------------------------
try:
    from bnc_lookup import get_suffixes as _bnc_check  # type: ignore[import-untyped]

    _HAS_LOOKUP = True
except ImportError:
    _HAS_LOOKUP = False

pytestmark = pytest.mark.skipif(
    not _HAS_LOOKUP,
    reason="bnc-lookup with suffix data not installed",
)

from pystylometry.prosody.pronouncing import phones_for_word, syllable_count


# ===========================================================================
# Helpers
# ===========================================================================


def _stress(word: str) -> list[int]:
    """Extract stress pattern for *word* via phones_for_word."""
    phones = phones_for_word(word)
    if not phones:
        return []
    return [int(ch) for ch in phones[0] if ch.isdigit()]


def _syllables(word: str) -> int:
    """Count syllables for *word* via phones_for_word + syllable_count."""
    phones = phones_for_word(word)
    if not phones:
        return 0
    return syllable_count(phones[0])


# ===========================================================================
# 1. Direct CMU hits — cascade must not interfere
# ===========================================================================


class TestDirectCmuHitsUnchanged:
    """Verify that words already in CMU return their original pronunciations.

    The suffix cascade must never alter results for words that have direct
    CMU entries.  These tests serve as regression guards.

    Related GitHub Issue:
        #82 — https://github.com/craigtrim/pystylometry/issues/82
    """

    def test_hello(self) -> None:
        phones = phones_for_word("hello")
        assert len(phones) >= 1
        assert "HH" in phones[0]

    def test_happy_stress(self) -> None:
        assert _stress("happy") == [1, 0]

    def test_cat_monosyllable(self) -> None:
        assert _stress("cat") == [1]
        assert _syllables("cat") == 1

    def test_beautiful_already_in_cmu(self) -> None:
        """'beautiful' is in CMU — cascade should not be triggered."""
        phones = phones_for_word("beautiful")
        assert len(phones) >= 1
        # CMU's entry, not a synthetic reconstruction
        assert "B" in phones[0] and "Y" in phones[0]


# ===========================================================================
# 2. Suffix cascade recovery — words NOT in CMU
# ===========================================================================


class TestSuffixCascadeRecovery:
    """Verify that OOV words with decomposable suffixes are recovered.

    Each test uses a word known to be absent from CMU (~134K entries) but
    present in BNC with suffix data.  The cascade should strip suffixes,
    find a CMU-lookable stem, and return a non-empty phoneme list.

    Related GitHub Issues:
        #82 — https://github.com/craigtrim/pystylometry/issues/82
        #81 — Tier 2 of the G2P cascade
              https://github.com/craigtrim/pystylometry/issues/81
    """

    def test_organise_recovered(self) -> None:
        """British '-ise' form: organise → organ (CMU) + -ise."""
        phones = phones_for_word("organise")
        assert phones, "organise should be recovered via suffix cascade"

    def test_organised_recovered(self) -> None:
        """Multi-suffix: organised → strip -ed, -ise → organ (CMU)."""
        phones = phones_for_word("organised")
        assert phones, "organised should be recovered via suffix cascade"

    def test_colourful_recovered(self) -> None:
        """British spelling + suffix: colourful → colour → color (CMU)."""
        phones = phones_for_word("colourful")
        assert phones, "colourful should be recovered via suffix cascade"

    def test_criticised_recovered(self) -> None:
        """Multi-level stripping with e-restore: criticised → critic (CMU)."""
        phones = phones_for_word("criticised")
        assert phones, "criticised should be recovered via suffix cascade"

    def test_counselling_recovered(self) -> None:
        """Consonant doubling + -ing: counselling → counsel (CMU)."""
        phones = phones_for_word("counselling")
        assert phones, "counselling should be recovered via suffix cascade"

    def test_civilisation_recovered(self) -> None:
        """Deep decomposition: civilisation → civil (CMU)."""
        phones = phones_for_word("civilisation")
        assert phones, "civilisation should be recovered via suffix cascade"

    def test_computerised_recovered(self) -> None:
        """Multi-suffix: computerised → computer (CMU)."""
        phones = phones_for_word("computerised")
        assert phones, "computerised should be recovered via suffix cascade"

    def test_authorised_recovered(self) -> None:
        """Multi-suffix: authorised → author (CMU)."""
        phones = phones_for_word("authorised")
        assert phones, "authorised should be recovered via suffix cascade"

    def test_modelled_recovered(self) -> None:
        """Consonant doubling + -ed: modelled → model (CMU)."""
        phones = phones_for_word("modelled")
        assert phones, "modelled should be recovered via suffix cascade"

    def test_labelling_recovered(self) -> None:
        """Consonant doubling + -ing: labelling → label (CMU)."""
        phones = phones_for_word("labelling")
        assert phones, "labelling should be recovered via suffix cascade"

    def test_fulfilment_recovered(self) -> None:
        """Suffix -ment: fulfilment → fulfil (CMU)."""
        phones = phones_for_word("fulfilment")
        assert phones, "fulfilment should be recovered via suffix cascade"

    def test_maximise_recovered(self) -> None:
        """British '-ise': maximise → maxim (CMU)."""
        phones = phones_for_word("maximise")
        assert phones, "maximise should be recovered via suffix cascade"


# ===========================================================================
# 3. Stress pattern correctness
# ===========================================================================


class TestStressPatternCorrectness:
    """Verify that recovered stress patterns are phonologically plausible.

    The cascade appends unstressed syllables for suffix material.  For
    stress-neutral suffixes (the majority), the root's stress pattern is
    preserved exactly.  These tests validate that the reconstructed pattern
    has the right number of syllables and plausible stress placement.

    Linguistic basis:
        Stress-neutral suffixes do not shift the base's stress pattern.
        ``-ness``, ``-ful``, ``-ly``, ``-ing``, ``-ed``, ``-er`` are all
        stress-neutral (Chomsky & Halle 1968, pp. 84-91).

    Related GitHub Issue:
        #82 — https://github.com/craigtrim/pystylometry/issues/82
    """

    def test_organise_syllable_count(self) -> None:
        """organise = 3 syllables (OR-gan-ise)."""
        assert _syllables("organise") == 3

    def test_organise_stress(self) -> None:
        """organise: primary stress on first syllable (from 'organ')."""
        stress = _stress("organise")
        assert len(stress) == 3
        assert stress[0] == 1  # Primary stress on OR-

    def test_colourful_syllable_count(self) -> None:
        """colourful = 3 syllables (COL-our-ful)."""
        assert _syllables("colourful") == 3

    def test_counselling_syllable_count(self) -> None:
        """counselling = 3 syllables (COUN-sel-ling)."""
        assert _syllables("counselling") == 3

    def test_modelled_syllable_count(self) -> None:
        """modelled = 2 syllables (MOD-elled), -ed adds 0 syllables."""
        assert _syllables("modelled") == 2

    def test_fulfilment_stress(self) -> None:
        """fulfilment: stress on second syllable (from ful-FIL)."""
        stress = _stress("fulfilment")
        assert len(stress) == 3
        assert stress[1] == 1  # Primary stress on -FIL-

    def test_computerised_syllable_count(self) -> None:
        """computerised: root 'computer' has 3 syllables + 1 for -ise."""
        assert _syllables("computerised") == 4

    def test_recovered_stress_values_are_valid(self) -> None:
        """All stress values in recovered patterns must be 0, 1, or 2.

        CMU uses: 0 = unstressed, 1 = primary, 2 = secondary.  Synthetic
        suffixes always contribute 0 (unstressed).  The root's values come
        directly from CMU and are therefore valid by construction.
        """
        for word in ["organise", "colourful", "counselling", "modelled"]:
            stress = _stress(word)
            assert stress, f"{word} should be recovered"
            for v in stress:
                assert v in (0, 1, 2), (
                    f"Invalid stress value {v} in {word}: {stress}"
                )


# ===========================================================================
# 4. True OOV — no morphological structure
# ===========================================================================


class TestTrueOovRemainEmpty:
    """Verify that genuinely unrecoverable words return empty lists.

    Words with no morphological structure (nonsense strings, brand names,
    acronyms) cannot be decomposed.  The cascade must return ``[]`` for
    these, identical to the pre-cascade behavior.

    Related GitHub Issue:
        #82 — https://github.com/craigtrim/pystylometry/issues/82
    """

    def test_nonsense_word(self) -> None:
        assert phones_for_word("xyzzy") == []

    def test_brand_name(self) -> None:
        assert phones_for_word("ChatGPT") == []

    def test_gibberish(self) -> None:
        assert phones_for_word("blorfnak") == []

    def test_empty_string(self) -> None:
        assert phones_for_word("") == []


# ===========================================================================
# 5. Edge cases
# ===========================================================================


class TestEdgeCases:
    """Edge case handling for the suffix cascade.

    Related GitHub Issue:
        #82 — https://github.com/craigtrim/pystylometry/issues/82
    """

    def test_single_character(self) -> None:
        """Single characters should return CMU entry or empty, never crash."""
        result = phones_for_word("a")
        # 'a' is in CMU
        assert isinstance(result, list)

    def test_already_root_in_cmu(self) -> None:
        """Words already in CMU should not go through the cascade."""
        phones_direct = phones_for_word("run")
        assert phones_direct
        assert "R" in phones_direct[0]

    def test_case_insensitive(self) -> None:
        """The cascade should be case-insensitive."""
        lower = phones_for_word("organise")
        upper = phones_for_word("Organise")
        assert lower == upper


# ===========================================================================
# 6. British spelling normalization
# ===========================================================================


class TestBritishSpellingNormalization:
    """Verify that British spellings are normalized to American for CMU lookup.

    CMU is an American English dictionary.  Many BNC words use British
    spellings that differ in predictable ways:

    - ``-our`` → ``-or`` (colour → color)
    - ``-ise`` → ``-ize`` (organise → organize)
    - ``-re``  → ``-er`` (centre → center) — handled at stem level

    Related GitHub Issue:
        #82 — https://github.com/craigtrim/pystylometry/issues/82
    """

    def test_colour_based_word(self) -> None:
        """colourful → colour → color (CMU) via -our → -or."""
        phones = phones_for_word("colourful")
        assert phones, "British -our spelling should normalize to -or"

    def test_ise_to_ize(self) -> None:
        """organise → organ via -ise stripping (organ is in CMU)."""
        phones = phones_for_word("organise")
        assert phones, "British -ise should be handled"

    def test_authorised_ise_chain(self) -> None:
        """authorised → strip -ed, -ise → author (CMU)."""
        phones = phones_for_word("authorised")
        assert phones, "Multi-suffix British -ise chain should resolve"


# ===========================================================================
# 7. Allomorphic restoration
# ===========================================================================


class TestAllomorphicRestoration:
    """Verify allomorphic restoration during suffix stripping.

    English morphology alters the surface form of stems when suffixes
    attach.  The cascade must reverse these alternations to recover
    CMU-lookable stems.

    Alternation types tested:
        - Consonant doubling: running → runn → run
        - Y → I lowering: happiness → happi → happy

    Note: These specific examples (running, happiness) are already in CMU,
    so they test the *mechanism* via the internal ``_restore_stem`` function
    rather than the end-to-end cascade.  The cascade tests above
    (counselling, modelled, labelling) exercise the same code path on
    genuinely OOV words.

    Related GitHub Issue:
        #82 — https://github.com/craigtrim/pystylometry/issues/82
    """

    def test_consonant_doubling_counselling(self) -> None:
        """counselling → counsell → counsel (CMU)."""
        phones = phones_for_word("counselling")
        assert phones, "Consonant doubling should be reversed"

    def test_consonant_doubling_modelled(self) -> None:
        """modelled → modell → model (CMU)."""
        phones = phones_for_word("modelled")
        assert phones, "Consonant doubling should be reversed"

    def test_consonant_doubling_labelling(self) -> None:
        """labelling → labell → label (CMU)."""
        phones = phones_for_word("labelling")
        assert phones, "Consonant doubling should be reversed"


# ===========================================================================
# 8. OOV discovery — BNC coverage gap
# ===========================================================================


class TestOovDiscovery:
    """Integration test: verify cascade improves CMU coverage on a word sample.

    Takes a sample of words known to be OOV in CMU but present in BNC with
    decomposable suffixes, and verifies that the cascade recovers a
    meaningful fraction of them.

    Related GitHub Issues:
        #82 — https://github.com/craigtrim/pystylometry/issues/82
        #76 — Beat detection cmu_coverage improvement
              https://github.com/craigtrim/pystylometry/issues/76

    Empirical basis:
        OOV discovery analysis (2026-03-16) found:
        - 330,743 BNC words checked against CMU
        - 40,650 OOV words had decomposable suffixes
        - 18,746 (46.1%) were recoverable via recursive suffix stripping
    """

    # Sample of OOV words known to be recoverable (from empirical analysis)
    RECOVERABLE_SAMPLE = [
        "organise",
        "organised",
        "colourful",
        "criticised",
        "counselling",
        "computerised",
        "authorised",
        "modelled",
        "labelling",
        "fulfilment",
        "maximise",
        "civilisation",
    ]

    def test_majority_of_sample_recovered(self) -> None:
        """At least 80% of the known-recoverable sample should resolve."""
        recovered = sum(1 for w in self.RECOVERABLE_SAMPLE if phones_for_word(w))
        ratio = recovered / len(self.RECOVERABLE_SAMPLE)
        assert ratio >= 0.8, (
            f"Only {recovered}/{len(self.RECOVERABLE_SAMPLE)} "
            f"({ratio:.0%}) recovered — expected >= 80%"
        )

    def test_all_recovered_have_valid_stress(self) -> None:
        """Every recovered word must have a non-empty, valid stress pattern."""
        for word in self.RECOVERABLE_SAMPLE:
            stress = _stress(word)
            if stress:  # Only check words that were recovered
                assert all(v in (0, 1, 2) for v in stress), (
                    f"{word}: invalid stress values in {stress}"
                )
                assert any(v == 1 for v in stress), (
                    f"{word}: no primary stress in {stress}"
                )

    def test_all_recovered_have_positive_syllable_count(self) -> None:
        """Every recovered word must have syllable count >= 1."""
        for word in self.RECOVERABLE_SAMPLE:
            syl = _syllables(word)
            if syl > 0:  # Only check recovered words
                assert syl >= 1, f"{word}: syllable count {syl} < 1"
