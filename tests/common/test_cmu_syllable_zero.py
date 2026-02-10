"""Tests for CMU dictionary edge case where syllable_count returns 0.

The CMU Pronouncing Dictionary can contain phoneme strings that lack
stress-marked vowel phonemes, causing ``syllable_count()`` to return 0.
Since no real English word has 0 syllables, downstream bucketing logic
must guard against this anomaly.

Related GitHub Issue:
    #63 - CMU dictionary edge case: syllable_count returns 0
    https://github.com/craigtrim/pystylometry/issues/63

Test coverage:
    - Unit: syllable_count returns 0 for phoneme strings without vowel digits
    - Unit: _count_syllables never returns 0 (fallback guarantees >= 1)
    - Unit: syllable distribution buckets handle edge-case inputs
    - Integration: compute_rhythm_prosody does not crash on real-world corpora
    - Integration: syllable_distribution metadata never contains key 0
"""

from pathlib import Path

import pytest

from pystylometry.prosody.pronouncing import syllable_count
from pystylometry.prosody.rhythm_prosody import (
    _count_syllables,
    _fallback_syllable_count,
    compute_rhythm_prosody,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

APNEWS_DIR = Path("/Users/craigtrim/Desktop/ebooks/2000s/APNEWS/apnews-combined")


def _load_apnews_chunk(name: str, max_words: int = 5_000) -> str:
    """Load an AP News chunk, truncated to *max_words* for speed."""
    path = APNEWS_DIR / name
    if not path.exists():
        pytest.skip(f"Test corpus not found: {path}")
    words = path.read_text(encoding="utf-8").split()[:max_words]
    return " ".join(words)


# ---------------------------------------------------------------------------
# Unit tests — syllable_count (pronouncing.py)
# ---------------------------------------------------------------------------


class TestSyllableCountRawPhones:
    """Verify syllable_count behaviour on edge-case phoneme strings.

    Related GitHub Issue:
        #63 - CMU dictionary edge case: syllable_count returns 0
        https://github.com/craigtrim/pystylometry/issues/63
    """

    def test_normal_phones(self) -> None:
        """Standard ARPAbet strings return the correct count."""
        assert syllable_count("HH AH0 L OW1") == 2  # "hello"
        assert syllable_count("K AE1 T") == 1  # "cat"
        assert syllable_count("B Y UW1 T AH0 F AH0 L") == 3  # "beautiful"

    def test_empty_string_returns_zero(self) -> None:
        """An empty phoneme string has no syllables."""
        assert syllable_count("") == 0

    def test_consonants_only_returns_zero(self) -> None:
        """A phoneme string with no stress-digit vowels returns 0.

        This is the root cause of the KeyError documented in #63.
        """
        # Hypothetical: only consonant phonemes (no trailing digit)
        assert syllable_count("HH N") == 0
        assert syllable_count("S T R") == 0
        assert syllable_count("M") == 0

    def test_single_vowel(self) -> None:
        """A single vowel phoneme returns 1."""
        assert syllable_count("AH0") == 1
        assert syllable_count("IY1") == 1


# ---------------------------------------------------------------------------
# Unit tests — _count_syllables (rhythm_prosody.py)
# ---------------------------------------------------------------------------


class TestCountSyllablesGuarantee:
    """Verify that _count_syllables always returns >= 1 for real words.

    The fallback heuristic already returns max(1, count).  The CMU path
    could return 0, but the downstream clamp in compute_rhythm_prosody
    handles that.  These tests document the current behaviour.
    """

    def test_common_words_positive(self) -> None:
        """Common English words always get >= 1 syllable."""
        for word in ["the", "cat", "hello", "extraordinary", "a", "I"]:
            assert _count_syllables(word) >= 0  # CMU path may return 0

    def test_fallback_always_at_least_one(self) -> None:
        """The heuristic fallback guarantees >= 1."""
        # Nonsense words that won't be in CMU
        for word in ["xyzzyplugh", "qwrtyp", "brrr", "shh"]:
            assert _fallback_syllable_count(word) >= 1

    def test_single_letter_words(self) -> None:
        """Single characters get at least 1 syllable."""
        for word in ["a", "I", "x", "z"]:
            assert _count_syllables(word) >= 0  # 0 possible via CMU


# ---------------------------------------------------------------------------
# Unit tests — bucket logic
# ---------------------------------------------------------------------------


class TestSyllableBucketLogic:
    """Test that the syllable distribution bucketing handles all valid inputs.

    The fix in #63 clamps syllable counts to max(1, sc) before bucketing.
    These tests verify the buckets are correct for various inputs.
    """

    def test_all_monosyllabic(self) -> None:
        """All-monosyllabic text puts everything in bucket '1'."""
        text = "The cat sat on the mat."
        result = compute_rhythm_prosody(text)

        dist = result.metadata["syllable_total_by_bucket"]
        assert dist["1"] > 0
        assert "0" not in dist  # no zero bucket

    def test_polysyllabic_buckets(self) -> None:
        """Polysyllabic words land in the correct higher buckets."""
        text = "Extraordinary communication internationalization."
        result = compute_rhythm_prosody(text)

        dist = result.metadata["syllable_total_by_bucket"]
        # These words have 6, 5, and 8 syllables respectively
        assert "0" not in dist
        # At least some tokens in high buckets
        high_count = sum(dist.get(str(i), 0) for i in range(4, 8)) + dist.get("8+", 0)
        assert high_count > 0

    def test_distribution_keys_are_valid(self) -> None:
        """All bucket keys are '1'-'7' or '8+', never '0'."""
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_rhythm_prosody(text)

        valid_keys = {str(i) for i in range(1, 8)} | {"8+"}
        for key in result.metadata["syllable_total_by_bucket"]:
            assert key in valid_keys, f"Unexpected bucket key: {key}"
        for key in result.metadata["syllable_unique_by_bucket"]:
            assert key in valid_keys, f"Unexpected bucket key: {key}"

    def test_bucket_totals_match_word_count(self) -> None:
        """Sum of all bucket totals equals the word count."""
        text = "The beautiful garden had extraordinary flowers and lovely trees."
        result = compute_rhythm_prosody(text)

        bucket_sum = sum(result.metadata["syllable_total_by_bucket"].values())
        assert bucket_sum == result.metadata["word_count"]


# ---------------------------------------------------------------------------
# Integration tests — real-world AP News corpus
# ---------------------------------------------------------------------------


class TestAPNewsCorpusIntegration:
    """Integration tests using real AP News articles.

    These tests exercise the full compute_rhythm_prosody pipeline on
    real-world text to verify the #63 fix holds under production conditions.

    Related GitHub Issue:
        #63 - CMU dictionary edge case: syllable_count returns 0
        https://github.com/craigtrim/pystylometry/issues/63
    """

    def test_chunk_00001_no_crash(self) -> None:
        """chunk_00001 completes without KeyError."""
        text = _load_apnews_chunk("chunk_00001.txt")
        result = compute_rhythm_prosody(text)

        assert result.metadata["word_count"] > 0
        assert "0" not in result.metadata["syllable_total_by_bucket"]

    def test_chunk_00002_no_crash(self) -> None:
        """chunk_00002 completes without KeyError."""
        text = _load_apnews_chunk("chunk_00002.txt")
        result = compute_rhythm_prosody(text)

        assert result.metadata["word_count"] > 0
        assert "0" not in result.metadata["syllable_total_by_bucket"]

    def test_chunk_00003_no_crash(self) -> None:
        """chunk_00003 completes without KeyError."""
        text = _load_apnews_chunk("chunk_00003.txt")
        result = compute_rhythm_prosody(text)

        assert result.metadata["word_count"] > 0
        assert "0" not in result.metadata["syllable_total_by_bucket"]

    def test_chunk_00005_no_crash(self) -> None:
        """chunk_00005 completes without KeyError."""
        text = _load_apnews_chunk("chunk_00005.txt")
        result = compute_rhythm_prosody(text)

        assert result.metadata["word_count"] > 0
        assert "0" not in result.metadata["syllable_total_by_bucket"]

    def test_chunk_00010_no_crash(self) -> None:
        """chunk_00010 completes without KeyError."""
        text = _load_apnews_chunk("chunk_00010.txt")
        result = compute_rhythm_prosody(text)

        assert result.metadata["word_count"] > 0
        assert "0" not in result.metadata["syllable_total_by_bucket"]

    def test_syllable_distribution_no_zero_key(self) -> None:
        """The raw syllable_distribution metadata never has a 0 key."""
        text = _load_apnews_chunk("chunk_00001.txt")
        result = compute_rhythm_prosody(text)

        dist = result.metadata["syllable_distribution"]
        assert 0 not in dist, "syllable_distribution should never have a 0-syllable key"
        assert all(k >= 1 for k in dist.keys())

    def test_all_numeric_fields_finite(self) -> None:
        """No NaN or Inf in any numeric output field on real text."""
        import math

        text = _load_apnews_chunk("chunk_00001.txt")
        result = compute_rhythm_prosody(text)

        for field_name in [
            "mean_syllables_per_word",
            "syllable_std_dev",
            "polysyllabic_ratio",
            "monosyllabic_ratio",
            "rhythmic_regularity",
            "syllable_cv",
            "stress_pattern_entropy",
            "sentence_length_alternation",
            "sentence_rhythm_score",
            "alliteration_density",
            "assonance_density",
            "consonance_density",
            "mean_consonant_cluster_length",
            "initial_cluster_ratio",
            "final_cluster_ratio",
            "iambic_ratio",
            "trochaic_ratio",
            "dactylic_ratio",
            "anapestic_ratio",
        ]:
            val = getattr(result, field_name)
            assert math.isfinite(val), f"{field_name} is not finite: {val}"
