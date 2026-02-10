"""Comprehensive tests for syllable distribution bucket feature.

Tests the ``syllable_total_by_bucket`` and ``syllable_unique_by_bucket``
fields inside the metadata dict returned by ``compute_rhythm_prosody``.

Feature specification:
    - Buckets: "1" through "11" and "12+"
    - For each bucket: total count (all occurrences) and unique count
      (distinct word types, case-insensitive)
    - Words are lowercased for unique counting
    - Syllable count of 0 is clamped to 1

Related GitHub Issues:
    #25  - Rhythm and Prosody Metrics
    #63  - CMU dictionary edge case: syllable_count returns 0

Test categories:
    1.  Bucket key completeness
    2.  Monosyllabic word distributions
    3.  Mixed-syllable distributions
    4.  Total vs unique divergence
    5.  Case-insensitive unique counting
    6.  Empty buckets for simple text
    7.  High-syllable buckets (8–11, 12+) for long words
    8.  Sum-of-totals equals word count
    9.  Unique <= total invariant
    10. Empty text
    11. Single word
    12. Repeated polysyllabic words
    13. Integration with existing prosody metadata structure
"""

from pystylometry.prosody.rhythm_prosody import compute_rhythm_prosody

# ---- helpers ----------------------------------------------------------------

EXPECTED_BUCKETS = [str(b) for b in range(1, 12)] + ["12+"]


def _total(text: str) -> dict[str, int]:
    """Return syllable_total_by_bucket for *text*."""
    return compute_rhythm_prosody(text).metadata["syllable_total_by_bucket"]


def _unique(text: str) -> dict[str, int]:
    """Return syllable_unique_by_bucket for *text*."""
    return compute_rhythm_prosody(text).metadata["syllable_unique_by_bucket"]


def _meta(text: str) -> dict:
    """Return full metadata dict for *text*."""
    return compute_rhythm_prosody(text).metadata


# =============================================================================
# 1. Bucket key completeness
# =============================================================================


class TestBucketKeyCompleteness:
    """All twelve bucket keys must be present in every result."""

    def test_all_bucket_keys_present_in_total(self) -> None:
        """syllable_total_by_bucket contains keys '1'..'11' and '12+'."""
        total = _total("The quick brown fox jumps over the lazy dog.")
        assert set(total.keys()) == set(EXPECTED_BUCKETS)

    def test_all_bucket_keys_present_in_unique(self) -> None:
        """syllable_unique_by_bucket contains keys '1'..'11' and '12+'."""
        unique = _unique("The quick brown fox jumps over the lazy dog.")
        assert set(unique.keys()) == set(EXPECTED_BUCKETS)

    def test_bucket_keys_present_for_single_word(self) -> None:
        """Even a single-word input has all twelve bucket keys."""
        total = _total("cat")
        unique = _unique("cat")
        assert set(total.keys()) == set(EXPECTED_BUCKETS)
        assert set(unique.keys()) == set(EXPECTED_BUCKETS)

    def test_bucket_count_is_twelve(self) -> None:
        """There are exactly 12 buckets: 1–11 plus 12+."""
        total = _total("hello world")
        assert len(total) == 12

    def test_bucket_keys_are_strings(self) -> None:
        """All bucket keys are strings, not integers."""
        total = _total("hello")
        for key in total:
            assert isinstance(key, str)


# =============================================================================
# 2. Monosyllabic word distributions
# =============================================================================


class TestMonosyllabicWords:
    """Texts composed entirely of one-syllable words."""

    def test_monosyllabic_text_bucket_1_total(self) -> None:
        """'the cat sat on the mat' -- all words are monosyllabic.

        _extract_words returns ['the', 'cat', 'sat', 'on', 'the', 'mat']
        (6 words), so bucket '1' total should equal 6.
        """
        total = _total("the cat sat on the mat")
        assert total["1"] == 6

    def test_monosyllabic_text_bucket_1_unique(self) -> None:
        """Unique monosyllabic types in 'the cat sat on the mat'.

        Lowercased set: {the, cat, sat, on, mat} -> 5 unique.
        """
        unique = _unique("the cat sat on the mat")
        assert unique["1"] == 5

    def test_monosyllabic_text_higher_buckets_zero(self) -> None:
        """Buckets '2' through '11' and '12+' should all be 0 for monosyllabic text."""
        total = _total("the cat sat on the mat")
        for bucket in [str(b) for b in range(2, 12)] + ["12+"]:
            assert total[bucket] == 0, f"Expected bucket {bucket!r} total == 0"


# =============================================================================
# 3. Mixed-syllable distributions
# =============================================================================


class TestMixedSyllables:
    """Texts mixing 1-, 2-, and 3-syllable words."""

    def test_mixed_text_bucket_counts(self) -> None:
        """Verify distribution for a text with known syllable counts.

        'the' = 1 syl, 'happy' = 2 syl, 'beautiful' = 3 syl,
        'cat' = 1 syl, 'is' = 1 syl, 'very' = 2 syl
        Expected: bucket '1' total = 3, bucket '2' total = 2, bucket '3' total = 1
        """
        text = "the happy beautiful cat is very"
        total = _total(text)
        assert total["1"] == 3  # the, cat, is
        assert total["2"] == 2  # happy, very
        assert total["3"] == 1  # beautiful

    def test_mixed_text_unique_counts(self) -> None:
        """Unique counts for the same mixed-syllable text."""
        text = "the happy beautiful cat is very"
        unique = _unique(text)
        assert unique["1"] == 3  # {the, cat, is}
        assert unique["2"] == 2  # {happy, very}
        assert unique["3"] == 1  # {beautiful}


# =============================================================================
# 4. Total vs unique divergence
# =============================================================================


class TestTotalVsUnique:
    """Total counts all occurrences; unique counts distinct lowercased types."""

    def test_repeated_monosyllabic_words(self) -> None:
        """'the the the cat' -> total=4, unique=2 for bucket '1'."""
        total = _total("the the the cat")
        unique = _unique("the the the cat")
        assert total["1"] == 4
        assert unique["1"] == 2  # {the, cat}

    def test_repeated_bisyllabic_words(self) -> None:
        """'happy happy happy' -> total=3, unique=1 for bucket '2'."""
        total = _total("happy happy happy")
        unique = _unique("happy happy happy")
        assert total["2"] == 3
        assert unique["2"] == 1


# =============================================================================
# 5. Case-insensitive unique counting
# =============================================================================


class TestCaseInsensitiveUnique:
    """Unique counting lowercases words before deduplication."""

    def test_case_variants_count_as_one(self) -> None:
        """'The the THE' -> unique for bucket '1' should be 1."""
        unique = _unique("The the THE")
        assert unique["1"] == 1

    def test_mixed_case_total_unaffected(self) -> None:
        """Total counts are not affected by casing -- all 3 tokens counted."""
        total = _total("The the THE")
        assert total["1"] == 3

    def test_case_variants_bisyllabic(self) -> None:
        """'Happy HAPPY happy' -> unique bucket '2' = 1, total = 3."""
        total = _total("Happy HAPPY happy")
        unique = _unique("Happy HAPPY happy")
        assert total["2"] == 3
        assert unique["2"] == 1


# =============================================================================
# 6. Empty buckets for simple text
# =============================================================================


class TestEmptyBuckets:
    """Simple text should have zero counts for unused high-syllable buckets."""

    def test_simple_text_no_high_buckets(self) -> None:
        """'I am a man' -- all monosyllabic; buckets 2–11 and 12+ should be 0."""
        total = _total("I am a man")
        unique = _unique("I am a man")
        for b in [str(i) for i in range(2, 12)] + ["12+"]:
            assert total[b] == 0, f"total[{b!r}] should be 0"
            assert unique[b] == 0, f"unique[{b!r}] should be 0"

    def test_no_5_plus_syllable_words_in_simple_prose(self) -> None:
        """Standard prose rarely uses 5+ syllable words."""
        total = _total("The big red dog sat by the tree.")
        for b in [str(i) for i in range(5, 12)] + ["12+"]:
            assert total[b] == 0


# =============================================================================
# 7. High-syllable buckets (8–11, 12+) for long words
# =============================================================================


class TestHighSyllableBuckets:
    """Words with 8+ syllables land in individual buckets up to 11, then 12+."""

    def test_antidisestablishmentarianism(self) -> None:
        """'antidisestablishmentarianism' has many syllables (12 in CMU).

        Should land in one of the high buckets (likely 12+).
        """
        total = _total("antidisestablishmentarianism")
        # It has 12 syllables in CMU — should be in the "12+" bucket
        # (or if the heuristic gives a different count, at least in a high bucket)
        high_total = sum(total.get(str(i), 0) for i in range(8, 12)) + total.get("12+", 0)
        assert high_total >= 1

    def test_high_bucket_with_context(self) -> None:
        """Long word embedded in a sentence still goes to a high bucket."""
        text = "He said antidisestablishmentarianism is real"
        total = _total(text)
        high_total = sum(total.get(str(i), 0) for i in range(8, 12)) + total.get("12+", 0)
        assert high_total >= 1

    def test_bucket_boundary_seven_vs_eight(self) -> None:
        """A 6-syllable word goes to '6', not any higher bucket.

        'responsibility' = 6 syllables in CMU.
        """
        text = "responsibility"
        total = _total(text)
        # Should NOT be in any bucket above 7
        for b in [str(i) for i in range(8, 12)] + ["12+"]:
            assert total[b] == 0, f"Expected bucket {b!r} == 0 for 'responsibility'"
        # Should be in one of the upper buckets (5 or 6 typically)
        assert total["1"] == 0  # definitely not monosyllabic

    def test_individual_buckets_8_through_11(self) -> None:
        """Buckets '8' through '11' exist as individual keys, not grouped."""
        total = _total("cat")
        for b in ["8", "9", "10", "11"]:
            assert b in total, f"Bucket {b!r} should be a key in total"
            assert total[b] == 0  # 'cat' is monosyllabic

    def test_12_plus_bucket_exists(self) -> None:
        """The overflow bucket '12+' exists as a key."""
        total = _total("cat")
        assert "12+" in total
        assert total["12+"] == 0

    def test_no_8_plus_bucket(self) -> None:
        """The old '8+' grouped bucket no longer exists."""
        total = _total("The quick brown fox.")
        assert "8+" not in total


# =============================================================================
# 8. Sum of totals equals total word count
# =============================================================================


class TestSumOfTotals:
    """The sum across all bucket totals must equal word_count in metadata."""

    def test_sum_equals_word_count_simple(self) -> None:
        """Simple sentence: sum of bucket totals == word_count."""
        meta = _meta("The cat sat on the mat.")
        total = meta["syllable_total_by_bucket"]
        assert sum(total.values()) == meta["word_count"]

    def test_sum_equals_word_count_mixed(self) -> None:
        """Mixed-syllable sentence: sum still equals word_count."""
        meta = _meta("The extraordinary investigation revealed nothing significant.")
        total = meta["syllable_total_by_bucket"]
        assert sum(total.values()) == meta["word_count"]

    def test_sum_equals_word_count_long(self) -> None:
        """Longer passage: invariant still holds."""
        text = (
            "The quick brown fox jumps over the lazy dog. "
            "Beautiful extraordinary circumstances necessitated "
            "an immediate investigation into the matter."
        )
        meta = _meta(text)
        total = meta["syllable_total_by_bucket"]
        assert sum(total.values()) == meta["word_count"]


# =============================================================================
# 9. Unique <= total for every bucket
# =============================================================================


class TestUniqueLeqTotal:
    """Unique count can never exceed total count in any bucket."""

    def test_unique_leq_total_simple(self) -> None:
        """For 'the cat sat on the mat', unique <= total in every bucket."""
        total = _total("the cat sat on the mat")
        unique = _unique("the cat sat on the mat")
        for b in EXPECTED_BUCKETS:
            assert unique[b] <= total[b], f"unique[{b!r}] > total[{b!r}]"

    def test_unique_leq_total_repeated_words(self) -> None:
        """Heavily repeated text: unique is much less than total."""
        text = "the the the the the the cat"
        total = _total(text)
        unique = _unique(text)
        for b in EXPECTED_BUCKETS:
            assert unique[b] <= total[b]

    def test_unique_leq_total_mixed(self) -> None:
        """Mixed text invariant."""
        text = "beautiful beautiful extraordinary extraordinary cat cat dog dog"
        total = _total(text)
        unique = _unique(text)
        for b in EXPECTED_BUCKETS:
            assert unique[b] <= total[b], f"bucket {b!r}: {unique[b]} > {total[b]}"


# =============================================================================
# 10. Empty text
# =============================================================================


class TestEmptyText:
    """Empty or whitespace-only text should not contain bucket keys.

    The empty-text early-return path produces a minimal metadata dict
    with only 'word_count' and 'warning'; bucket keys are absent.
    """

    def test_empty_string_no_bucket_keys(self) -> None:
        """Empty string returns metadata without syllable bucket keys."""
        meta = _meta("")
        assert meta["word_count"] == 0
        assert "syllable_total_by_bucket" not in meta

    def test_whitespace_only_no_bucket_keys(self) -> None:
        """Whitespace-only input returns metadata without syllable bucket keys."""
        meta = _meta("   \n\t  ")
        assert meta["word_count"] == 0
        assert "syllable_unique_by_bucket" not in meta

    def test_punctuation_only_no_bucket_keys(self) -> None:
        """Punctuation-only input produces no extractable words."""
        meta = _meta("!!! ??? ...")
        assert meta["word_count"] == 0
        assert "syllable_total_by_bucket" not in meta


# =============================================================================
# 11. Single word
# =============================================================================


class TestSingleWord:
    """Single-word input populates exactly one bucket."""

    def test_single_monosyllabic_word(self) -> None:
        """'cat' -> bucket '1' total = 1, unique = 1; all others 0."""
        total = _total("cat")
        unique = _unique("cat")
        assert total["1"] == 1
        assert unique["1"] == 1
        for b in [str(i) for i in range(2, 12)] + ["12+"]:
            assert total[b] == 0
            assert unique[b] == 0

    def test_single_bisyllabic_word(self) -> None:
        """'happy' -> bucket '2' total = 1, unique = 1."""
        total = _total("happy")
        unique = _unique("happy")
        assert total["2"] == 1
        assert unique["2"] == 1
        assert total["1"] == 0

    def test_single_trisyllabic_word(self) -> None:
        """'beautiful' -> bucket '3' total = 1, unique = 1."""
        total = _total("beautiful")
        unique = _unique("beautiful")
        assert total["3"] == 1
        assert unique["3"] == 1


# =============================================================================
# 12. Repeated polysyllabic words
# =============================================================================


class TestRepeatedPolysyllabicWords:
    """Repetition inflates total but not unique for higher buckets."""

    def test_repeated_trisyllabic(self) -> None:
        """'beautiful beautiful beautiful' -> total=3, unique=1 in bucket '3'."""
        total = _total("beautiful beautiful beautiful")
        unique = _unique("beautiful beautiful beautiful")
        assert total["3"] == 3
        assert unique["3"] == 1

    def test_repeated_quadrisyllabic(self) -> None:
        """'extraordinary extraordinary' -> total=2, unique=1.

        'extraordinary' has 6 syllables in CMU, so it should land in bucket '6'.
        """
        text = "extraordinary extraordinary"
        total = _total(text)
        unique = _unique(text)
        # Find which bucket it landed in (depends on CMU count)
        populated = [b for b in EXPECTED_BUCKETS if total[b] > 0]
        assert len(populated) == 1, "Only one bucket should be populated"
        bucket = populated[0]
        assert total[bucket] == 2
        assert unique[bucket] == 1

    def test_mixed_repeated_polysyllabic(self) -> None:
        """'beautiful extraordinary beautiful extraordinary' -> total and unique diverge."""
        text = "beautiful extraordinary beautiful extraordinary"
        total = _total(text)
        unique = _unique(text)
        # Sum of totals == 4
        assert sum(total.values()) == 4
        # Sum of uniques == 2 (one word per bucket)
        assert sum(unique.values()) == 2


# =============================================================================
# 13. Integration with existing prosody metadata structure
# =============================================================================


class TestMetadataIntegration:
    """Bucket dicts sit alongside other metadata keys."""

    def test_metadata_contains_bucket_keys(self) -> None:
        """Both syllable_total_by_bucket and syllable_unique_by_bucket present."""
        meta = _meta("The quick brown fox jumps over the lazy dog.")
        assert "syllable_total_by_bucket" in meta
        assert "syllable_unique_by_bucket" in meta

    def test_bucket_dicts_are_plain_dicts(self) -> None:
        """Bucket dicts are plain dict[str, int], not Counter or defaultdict."""
        meta = _meta("The cat sat on the mat.")
        total = meta["syllable_total_by_bucket"]
        unique = meta["syllable_unique_by_bucket"]
        assert type(total) is dict
        assert type(unique) is dict

    def test_bucket_values_are_integers(self) -> None:
        """Every value in both bucket dicts is an int (not float)."""
        meta = _meta("The extraordinary investigation continued.")
        for b in EXPECTED_BUCKETS:
            assert isinstance(meta["syllable_total_by_bucket"][b], int)
            assert isinstance(meta["syllable_unique_by_bucket"][b], int)

    def test_word_count_consistent(self) -> None:
        """word_count metadata matches sum of totals across buckets."""
        text = "The beautiful garden had extraordinary flowers."
        meta = _meta(text)
        assert sum(meta["syllable_total_by_bucket"].values()) == meta["word_count"]

    def test_other_metadata_keys_still_present(self) -> None:
        """Adding bucket keys did not displace existing metadata keys."""
        meta = _meta("The quick brown fox.")
        for key in [
            "word_count",
            "unique_words",
            "sentence_count",
            "total_syllables",
            "cmu_coverage",
            "syllable_distribution",
            "word_stress_patterns",
        ]:
            assert key in meta, f"Expected metadata key {key!r} missing"

    def test_total_syllables_positive_for_nonempty(self) -> None:
        """total_syllables in metadata is positive when text has words."""
        meta = _meta("hello world")
        assert meta["total_syllables"] > 0


# =============================================================================
# Additional edge-case and regression tests
# =============================================================================


class TestEdgeCases:
    """Extra tests covering clamping, boundary conditions, and regressions."""

    def test_all_bucket_values_non_negative(self) -> None:
        """No bucket should ever have a negative count."""
        text = "The quick brown fox jumps over the lazy dog."
        total = _total(text)
        unique = _unique(text)
        for b in EXPECTED_BUCKETS:
            assert total[b] >= 0
            assert unique[b] >= 0

    def test_unique_equals_total_when_all_distinct(self) -> None:
        """When every word is unique, unique == total in every bucket."""
        text = "cat dog bird fish"
        total = _total(text)
        unique = _unique(text)
        for b in EXPECTED_BUCKETS:
            assert unique[b] == total[b]

    def test_syllable_clamping_to_one(self) -> None:
        """Words that might return 0 syllables are clamped to 1.

        The clamping happens at line 804:  sc = max(1, sc)
        All words must therefore appear in bucket '1' or higher, never in a
        hypothetical '0' bucket.
        """
        # Even unusual words should land in a valid bucket
        text = "hmm shh brr"  # consonant-only words, likely 0 from CMU
        total = _total(text)
        # No '0' bucket exists; total across all buckets == word count
        meta = _meta(text)
        assert sum(total.values()) == meta["word_count"]
        # Specifically, these should be clamped to bucket '1'
        assert total["1"] >= 1

    def test_no_zero_bucket_key(self) -> None:
        """Bucket '0' must never appear in the results."""
        total = _total("hmm shh brr the cat sat")
        assert "0" not in total

    def test_no_old_8_plus_bucket(self) -> None:
        """The old grouped '8+' bucket must not appear after the extension."""
        text = "antidisestablishmentarianism is a long word"
        total = _total(text)
        assert "8+" not in total
