"""Tests for word class distribution (descriptive statistics).

Tests the compute_word_class_distribution() function, verifying:

- Percentage sum == 100% for standard text
- Labels sorted alphabetically
- Correct classification counts
- Edge cases (empty text, single word)

Related GitHub Issue:
    #54 -- Add word-class distribution report
    https://github.com/craigtrim/pystylometry/issues/54
"""

import pytest

from pystylometry.lexical.word_class_distribution import (
    ClassificationEntry,
    RunStats,
    WordClassDistribution,
    compute_word_class_distribution,
)


# ===================================================================
# Edge cases
# ===================================================================


class TestEdgeCases:
    """Empty and minimal inputs."""

    def test_empty_string(self):
        result = compute_word_class_distribution("")
        assert result.total_words == 0
        assert result.unique_labels == 0
        assert result.classifications == []
        assert result.percentage_sum == 0.0

    def test_whitespace_only(self):
        result = compute_word_class_distribution("   \n\t  ")
        assert result.total_words == 0

    def test_single_lexical_word(self):
        result = compute_word_class_distribution("hello")
        assert result.total_words == 1
        assert result.unique_labels == 1
        assert result.classifications[0].label == "lexical"
        assert result.classifications[0].count == 1
        assert result.classifications[0].percentage == 100.0
        assert result.percentage_sum == 100.0

    def test_single_contraction(self):
        result = compute_word_class_distribution("don't")
        assert result.total_words == 1
        assert result.unique_labels == 1
        assert result.classifications[0].label == "apostrophe.contraction.negative"
        assert result.classifications[0].percentage == 100.0


# ===================================================================
# Percentage sum validation
# ===================================================================


class TestPercentageSum:
    """Percentages must sum to 100%."""

    def test_sum_equals_100_simple(self):
        text = "The cat sat on the mat"
        result = compute_word_class_distribution(text)
        assert abs(result.percentage_sum - 100.0) < 0.01

    def test_sum_equals_100_with_contractions(self):
        text = "I don't think she's going to the store and it's raining"
        result = compute_word_class_distribution(text)
        assert abs(result.percentage_sum - 100.0) < 0.01

    def test_sum_equals_100_with_hyphens(self):
        text = "The well-known self-esteem of the twenty-one year old"
        result = compute_word_class_distribution(text)
        assert abs(result.percentage_sum - 100.0) < 0.01

    def test_sum_equals_100_mixed(self):
        text = (
            "He wouldn't say that it's a well-known fact but she'll "
            "probably re-examine the self-evident truth of the matter"
        )
        result = compute_word_class_distribution(text)
        assert abs(result.percentage_sum - 100.0) < 0.01


# ===================================================================
# Sorting
# ===================================================================


class TestSorting:
    """Labels must be sorted alphabetically."""

    def test_labels_sorted(self):
        text = "She don't think it's a well-known self-evident re-examination"
        result = compute_word_class_distribution(text)
        labels = [e.label for e in result.classifications]
        assert labels == sorted(labels)

    def test_mixed_l1_categories_sorted(self):
        text = "The cat's twenty-one don't re-enter"
        result = compute_word_class_distribution(text)
        labels = [e.label for e in result.classifications]
        assert labels == sorted(labels)


# ===================================================================
# Classification correctness
# ===================================================================


class TestClassificationCorrectness:
    """Verify known words get the right labels."""

    def test_lexical_dominates(self):
        text = "The quick brown fox jumps over the lazy dog"
        result = compute_word_class_distribution(text)
        lexical = next(e for e in result.classifications if e.label == "lexical")
        assert lexical.percentage == 100.0

    def test_contractions_counted(self):
        text = "don't can't won't shouldn't"
        result = compute_word_class_distribution(text)
        assert result.total_words == 4
        neg = next(
            e for e in result.classifications
            if e.label == "apostrophe.contraction.negative"
        )
        assert neg.count == 4
        assert neg.percentage == 100.0

    def test_possessive_singular(self):
        text = "the captain's hat"
        result = compute_word_class_distribution(text)
        poss = next(
            e for e in result.classifications
            if e.label == "apostrophe.possessive.singular"
        )
        assert poss.count == 1

    def test_possessive_plural_stripped(self):
        # Trailing apostrophe in "captains'" is stripped by the BNC-style
        # punctuation regex (re.sub(r"^[^\w]+|[^\w]+$", ...)).  The token
        # becomes "captains" → lexical.  This is consistent with BNC
        # tokenization; possessive plurals are not preserved.
        text = "the captains' hats"
        result = compute_word_class_distribution(text)
        labels = {e.label for e in result.classifications}
        assert "apostrophe.possessive.plural" not in labels
        assert "lexical" in labels

    def test_hyphenated_prefixed(self):
        text = "re-enter non-stop"
        result = compute_word_class_distribution(text)
        prefixed = next(
            e for e in result.classifications
            if e.label == "hyphenated.prefixed"
        )
        assert prefixed.count == 2

    def test_multiple_categories(self):
        text = "The captain's don't re-enter the ship"
        result = compute_word_class_distribution(text)
        labels = {e.label for e in result.classifications}
        assert "lexical" in labels
        assert "apostrophe.possessive.singular" in labels
        assert "apostrophe.contraction.negative" in labels
        assert "hyphenated.prefixed" in labels


# ===================================================================
# Dataclass properties
# ===================================================================


class TestResultProperties:
    """Verify result dataclass attributes."""

    def test_total_words_matches_token_count(self):
        text = "one two three four five"
        result = compute_word_class_distribution(text)
        assert result.total_words == 5

    def test_unique_labels_count(self):
        text = "don't can't hello world"
        result = compute_word_class_distribution(text)
        # "don't" and "can't" share apostrophe.contraction.negative
        # "hello" and "world" share lexical
        assert result.unique_labels == 2

    def test_frozen_result(self):
        result = compute_word_class_distribution("hello world")
        with pytest.raises(AttributeError):
            result.total_words = 99  # type: ignore[misc]

    def test_frozen_entry(self):
        result = compute_word_class_distribution("hello")
        with pytest.raises(AttributeError):
            result.classifications[0].count = 99  # type: ignore[misc]


# ===================================================================
# Apostrophe normalization
# ===================================================================


class TestApostropheNormalization:
    """Smart quotes should be normalized to ASCII apostrophe."""

    def test_smart_quote_contraction(self):
        # U+2019 RIGHT SINGLE QUOTATION MARK (common in ebooks)
        text = "don\u2019t"
        result = compute_word_class_distribution(text)
        labels = {e.label for e in result.classifications}
        assert "apostrophe.contraction.negative" in labels

    def test_backtick_contraction(self):
        # U+0060 GRAVE ACCENT
        text = "don\u0060t"
        result = compute_word_class_distribution(text)
        labels = {e.label for e in result.classifications}
        assert "apostrophe.contraction.negative" in labels


# ===================================================================
# Run-length statistics
# ===================================================================


class TestRunStats:
    """Contiguous sequence (run) statistics per classification."""

    def test_single_run(self):
        # All lexical → one run of length 5
        text = "the cat sat on mat"
        result = compute_word_class_distribution(text)
        lexical = next(e for e in result.classifications if e.label == "lexical")
        rs = lexical.run_stats
        assert rs.runs == 1
        assert rs.mean == 5.0
        assert rs.median == 5.0
        assert rs.mode == 5
        assert rs.min == 5
        assert rs.max == 5

    def test_broken_runs(self):
        # lexical lexical CONTRACTION lexical lexical lexical
        # → lexical runs: [2, 3], contraction runs: [1]
        text = "the cat don't sit on mat"
        result = compute_word_class_distribution(text)
        lexical = next(e for e in result.classifications if e.label == "lexical")
        rs = lexical.run_stats
        assert rs.runs == 2
        assert rs.min == 2
        assert rs.max == 3
        assert rs.mean == 2.5

    def test_contraction_isolated(self):
        # Each contraction is surrounded by lexical words → runs of [1, 1]
        text = "he don't know and can't go"
        result = compute_word_class_distribution(text)
        neg = next(
            e for e in result.classifications
            if e.label == "apostrophe.contraction.negative"
        )
        rs = neg.run_stats
        assert rs.runs == 2
        assert rs.min == 1
        assert rs.max == 1
        assert rs.mean == 1.0
        assert rs.mode == 1

    def test_consecutive_contractions(self):
        # Two contractions back-to-back → one run of length 2
        text = "don't can't go"
        result = compute_word_class_distribution(text)
        neg = next(
            e for e in result.classifications
            if e.label == "apostrophe.contraction.negative"
        )
        rs = neg.run_stats
        assert rs.runs == 1
        assert rs.min == 2
        assert rs.max == 2

    def test_run_stats_present_on_all_entries(self):
        text = "The captain's don't re-enter the ship"
        result = compute_word_class_distribution(text)
        for entry in result.classifications:
            assert entry.run_stats is not None
            assert entry.run_stats.runs >= 1
            assert entry.run_stats.min >= 1
            assert entry.run_stats.max >= entry.run_stats.min

    def test_single_word_run_stats(self):
        result = compute_word_class_distribution("hello")
        rs = result.classifications[0].run_stats
        assert rs.runs == 1
        assert rs.mean == 1.0
        assert rs.median == 1.0
        assert rs.mode == 1
        assert rs.min == 1
        assert rs.max == 1

    def test_mode_picks_smallest_on_tie(self):
        # lexical(2) contraction(1) lexical(3) contraction(1) lexical(1)
        # lexical runs: [2, 3, 1] → mode should be smallest (1) since all unique
        text = "one two don't one two three can't go"
        result = compute_word_class_distribution(text)
        lexical = next(e for e in result.classifications if e.label == "lexical")
        rs = lexical.run_stats
        # Runs: [2, 3, 1] — all unique, multimode returns all → min picks 1
        assert rs.mode == 1


# ===================================================================
# Tokens by label
# ===================================================================


class TestTokensByLabel:
    """Per-label token sample collection (excludes lexical)."""

    def test_lexical_excluded(self):
        text = "The quick brown fox"
        result = compute_word_class_distribution(text)
        assert "lexical" not in result.tokens_by_label

    def test_contractions_collected(self):
        text = "he don't know and can't go"
        result = compute_word_class_distribution(text)
        neg_tokens = result.tokens_by_label.get("apostrophe.contraction.negative", [])
        assert neg_tokens == ["don't", "can't"]

    def test_order_preserved(self):
        text = "don't can't won't shouldn't"
        result = compute_word_class_distribution(text)
        neg_tokens = result.tokens_by_label["apostrophe.contraction.negative"]
        assert neg_tokens == ["don't", "can't", "won't", "shouldn't"]

    def test_empty_text_returns_empty(self):
        result = compute_word_class_distribution("")
        assert result.tokens_by_label == {}

    def test_mixed_labels_collected(self):
        text = "The captain's don't re-enter the ship"
        result = compute_word_class_distribution(text)
        assert "apostrophe.possessive.singular" in result.tokens_by_label
        assert "apostrophe.contraction.negative" in result.tokens_by_label
        assert "hyphenated.prefixed" in result.tokens_by_label
        assert "lexical" not in result.tokens_by_label
