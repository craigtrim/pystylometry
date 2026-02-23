"""Tests for paragraph-level segmentation and statistics.

Covers:
- split_paragraphs: structure, edge cases, blank-line delimiters
- compute_paragraph_stats: all metrics, AI-tell signals
- terminal_brevity_ratio: mic drop detection signal
- single_sentence_paragraph_ratio + short_paragraph_run_length: stacked paragraph signal

Related GitHub Issues:
    #71 - Paragraph-Level Segmentation
    https://github.com/craigtrim/pystylometry/issues/71
    #69 - AI Stylistic Tell Detection
    https://github.com/craigtrim/pystylometry/issues/69
"""

import pytest

from pystylometry._utils import compute_paragraph_stats, split_paragraphs


# ============================================================
# 1. split_paragraphs — structure
# ============================================================


class TestSplitParagraphs:
    """Tests for the split_paragraphs() utility function."""

    def test_returns_list_of_lists(self):
        """Result is list[list[str]]."""
        result = split_paragraphs("One sentence.")
        assert isinstance(result, list)
        assert all(isinstance(p, list) for p in result)

    def test_single_paragraph(self):
        """Single block of text returns one paragraph."""
        result = split_paragraphs("First sentence. Second sentence.")
        assert len(result) == 1

    def test_two_paragraphs(self):
        """Blank-line separator produces two paragraphs."""
        result = split_paragraphs("First sentence.\n\nSecond sentence.")
        assert len(result) == 2

    def test_three_paragraphs(self):
        """Two blank lines produce three paragraphs."""
        text = "Para one.\n\nPara two.\n\nPara three."
        result = split_paragraphs(text)
        assert len(result) == 3

    def test_sentences_within_paragraph(self):
        """Multiple sentences in one paragraph are preserved."""
        result = split_paragraphs("First. Second. Third.")
        assert len(result) == 1
        assert len(result[0]) == 3

    def test_sentences_split_across_paragraphs(self):
        """Sentences are correctly assigned to their paragraphs."""
        text = "A. B.\n\nC. D."
        result = split_paragraphs(text)
        assert len(result) == 2
        assert len(result[0]) == 2
        assert len(result[1]) == 2

    def test_empty_string_returns_empty(self):
        """Empty input returns empty list."""
        assert split_paragraphs("") == []

    def test_whitespace_only_returns_empty(self):
        """Whitespace-only input returns empty list."""
        assert split_paragraphs("   ") == []

    def test_sentences_are_strings(self):
        """Every sentence in every paragraph is a string."""
        result = split_paragraphs("Hello world. How are you?\n\nI am fine.")
        for para in result:
            for sentence in para:
                assert isinstance(sentence, str)

    def test_each_paragraph_has_sentences(self):
        """No paragraph is empty."""
        text = "Alpha beta gamma.\n\nDelta epsilon zeta."
        result = split_paragraphs(text)
        assert all(len(p) >= 1 for p in result)


# ============================================================
# 2. compute_paragraph_stats — basic structure
# ============================================================


class TestComputeParagraphStatsStructure:
    """Tests for the shape and types of compute_paragraph_stats() output."""

    def test_returns_result_object(self):
        """Returns a ParagraphStatsResult dataclass."""
        from pystylometry._types import ParagraphStatsResult

        result = compute_paragraph_stats("One sentence here.")
        assert isinstance(result, ParagraphStatsResult)

    def test_empty_input_returns_zero_result(self):
        """Empty input returns zeroed result."""
        result = compute_paragraph_stats("")
        assert result.paragraph_count == 0
        assert result.sentences_per_paragraph == []
        assert result.terminal_brevity_ratios == []

    def test_paragraph_count_single(self):
        """Single paragraph yields count 1."""
        result = compute_paragraph_stats("One sentence.")
        assert result.paragraph_count == 1

    def test_paragraph_count_two(self):
        """Two paragraphs yields count 2."""
        result = compute_paragraph_stats("Para one.\n\nPara two.")
        assert result.paragraph_count == 2

    def test_sentences_per_paragraph_length_matches(self):
        """sentences_per_paragraph has one entry per paragraph."""
        text = "A. B.\n\nC.\n\nD. E. F."
        result = compute_paragraph_stats(text)
        assert len(result.sentences_per_paragraph) == result.paragraph_count

    def test_words_per_paragraph_length_matches(self):
        """words_per_paragraph has one entry per paragraph."""
        text = "One two three.\n\nFour five."
        result = compute_paragraph_stats(text)
        assert len(result.words_per_paragraph) == result.paragraph_count

    def test_terminal_brevity_ratios_length_matches(self):
        """terminal_brevity_ratios has one entry per paragraph."""
        text = "A long sentence here. Short.\n\nAnother paragraph."
        result = compute_paragraph_stats(text)
        assert len(result.terminal_brevity_ratios) == result.paragraph_count

    def test_metadata_contains_paragraph_count(self):
        """metadata includes paragraph_count key."""
        result = compute_paragraph_stats("A sentence here.")
        assert "paragraph_count" in result.metadata


# ============================================================
# 3. terminal_brevity_ratio — mic drop signal
# ============================================================


class TestTerminalBrevityRatio:
    """Tests for the mic drop detection signal."""

    def test_single_sentence_paragraph_ratio_is_one(self):
        """A one-sentence paragraph has terminal_brevity_ratio == 1.0."""
        result = compute_paragraph_stats("Just one sentence here.")
        assert result.terminal_brevity_ratios[0] == pytest.approx(1.0)

    def test_equal_length_sentences_ratio_is_one(self):
        """Equal-length sentences produce ratio ≈ 1.0."""
        # Three sentences of roughly equal word count
        result = compute_paragraph_stats("The cat sat. The dog ran. The bird flew.")
        # ratio = last_sentence_words / mean_sentence_words ≈ 1.0
        assert result.terminal_brevity_ratios[0] == pytest.approx(1.0, abs=0.5)

    def test_mic_drop_short_closer_low_ratio(self):
        """A very short final sentence produces a ratio well below 1.0."""
        # Long sentences followed by a short mic-drop closer
        text = (
            "The analysis revealed several significant patterns in the data. "
            "Each pattern correlated strongly with the expected outcomes. "
            "Remarkable."
        )
        result = compute_paragraph_stats(text)
        # Last sentence ("Remarkable.") is much shorter than the mean
        assert result.terminal_brevity_ratios[0] < 0.5

    def test_ratio_nonnegative(self):
        """All terminal_brevity_ratios are >= 0."""
        text = "Sentence one here. Sentence two there.\n\nAnother para. Brief."
        result = compute_paragraph_stats(text)
        assert all(r >= 0.0 for r in result.terminal_brevity_ratios)

    def test_multiple_paragraphs_each_has_ratio(self):
        """Each paragraph gets its own terminal brevity ratio."""
        text = "Long sentence here. Short.\n\nAnother long sentence. Done."
        result = compute_paragraph_stats(text)
        assert len(result.terminal_brevity_ratios) == 2
        # Both should be < 1.0 (short ender relative to first sentence)
        assert result.terminal_brevity_ratios[0] < 1.0
        assert result.terminal_brevity_ratios[1] <= 1.0


# ============================================================
# 4. single_sentence_paragraph_ratio — stacked paragraph signal
# ============================================================


class TestSingleSentenceParagraphRatio:
    """Tests for the stacked short paragraph detection signal."""

    def test_all_single_sentence_paragraphs_ratio_one(self):
        """All single-sentence paragraphs yields ratio 1.0."""
        text = "One.\n\nTwo.\n\nThree."
        result = compute_paragraph_stats(text)
        assert result.single_sentence_paragraph_ratio == pytest.approx(1.0)

    def test_no_single_sentence_paragraphs_ratio_zero(self):
        """No single-sentence paragraphs yields ratio 0.0."""
        text = "One. Two.\n\nThree. Four."
        result = compute_paragraph_stats(text)
        assert result.single_sentence_paragraph_ratio == pytest.approx(0.0)

    def test_half_single_sentence_paragraphs(self):
        """Half single-sentence paragraphs yields ratio 0.5."""
        text = "One.\n\nTwo. Three."
        result = compute_paragraph_stats(text)
        assert result.single_sentence_paragraph_ratio == pytest.approx(0.5)

    def test_ratio_between_zero_and_one(self):
        """Ratio is always between 0 and 1 inclusive."""
        text = "A. B.\n\nC.\n\nD. E. F.\n\nG."
        result = compute_paragraph_stats(text)
        assert 0.0 <= result.single_sentence_paragraph_ratio <= 1.0


# ============================================================
# 5. short_paragraph_run_length — stacked paragraph signal
# ============================================================


class TestShortParagraphRunLength:
    """Tests for the consecutive single-sentence paragraph run signal."""

    def test_no_single_sentence_paragraphs_run_zero(self):
        """No single-sentence paragraphs yields run length 0."""
        text = "One two. Three four.\n\nFive six. Seven eight."
        result = compute_paragraph_stats(text)
        assert result.short_paragraph_run_length == 0

    def test_single_isolated_one_sentence_para_run_one(self):
        """One single-sentence paragraph among multi-sentence ones yields run 1."""
        text = "A. B.\n\nC.\n\nD. E."
        result = compute_paragraph_stats(text)
        assert result.short_paragraph_run_length == 1

    def test_consecutive_two_single_sentence_paras_run_two(self):
        """Two consecutive single-sentence paragraphs yields run 2."""
        text = "A. B.\n\nC.\n\nD.\n\nE. F."
        result = compute_paragraph_stats(text)
        assert result.short_paragraph_run_length == 2

    def test_all_single_sentence_paragraphs_run_equals_count(self):
        """All single-sentence paragraphs: run length == paragraph count."""
        text = "A.\n\nB.\n\nC.\n\nD."
        result = compute_paragraph_stats(text)
        assert result.short_paragraph_run_length == 4

    def test_longest_run_selected(self):
        """The longest run is returned, not the first."""
        # run of 1, then break, then run of 3
        text = "A.\n\nB. C.\n\nD.\n\nE.\n\nF."
        result = compute_paragraph_stats(text)
        assert result.short_paragraph_run_length == 3

    def test_run_nonnegative(self):
        """Run length is always >= 0."""
        result = compute_paragraph_stats("Hello world.")
        assert result.short_paragraph_run_length >= 0


# ============================================================
# 6. Aggregate statistics
# ============================================================


class TestAggregateStats:
    """Tests for mean/std sentence and word counts."""

    def test_mean_sentences_per_paragraph_single(self):
        """Single paragraph, single sentence: mean == 1."""
        result = compute_paragraph_stats("One sentence.")
        assert result.mean_sentences_per_paragraph == pytest.approx(1.0)

    def test_mean_sentences_per_paragraph_two_paras(self):
        """Two paragraphs: mean is average of their sentence counts."""
        text = "A. B.\n\nC."  # 2 sentences, then 1 → mean = 1.5
        result = compute_paragraph_stats(text)
        assert result.mean_sentences_per_paragraph == pytest.approx(1.5)

    def test_std_sentences_single_paragraph_is_zero(self):
        """Single paragraph: std dev is 0."""
        result = compute_paragraph_stats("Just one sentence.")
        assert result.std_sentences_per_paragraph == pytest.approx(0.0)

    def test_words_per_paragraph_positive(self):
        """All word counts are positive for non-empty text."""
        text = "Hello world.\n\nGoodbye world."
        result = compute_paragraph_stats(text)
        assert all(w > 0 for w in result.words_per_paragraph)

    def test_mean_words_positive(self):
        """Mean word count is positive for non-empty input."""
        result = compute_paragraph_stats("Three words here.\n\nTwo words.")
        assert result.mean_words_per_paragraph > 0


# ============================================================
# 7. AI-tell integration scenario
# ============================================================


class TestAITellScenario:
    """Integration tests simulating AI-tell patterns from Issue #69."""

    def test_mic_drop_pattern(self):
        """Classic LLM mic drop: substantive sentences then a punchy closer."""
        text = (
            "The data showed clear trends across all measured variables. "
            "Statistical significance was confirmed at p < 0.001. "
            "The implications are profound.\n\n"
            "Further analysis is warranted."
        )
        result = compute_paragraph_stats(text)
        # First paragraph should have a low terminal brevity ratio (mic drop)
        assert result.terminal_brevity_ratios[0] < 0.8
        assert result.paragraph_count == 2

    def test_stacked_short_paragraph_pattern(self):
        """Classic LLM stacked short paragraphs."""
        text = (
            "Here is the context.\n\n"
            "This is important.\n\n"
            "This matters too.\n\n"
            "And this changes everything.\n\n"
            "The rest of the analysis follows in detail here."
        )
        result = compute_paragraph_stats(text)
        # 4 of 5 paragraphs are single-sentence
        assert result.single_sentence_paragraph_ratio >= 0.6
        # Run of 4 consecutive single-sentence paragraphs
        assert result.short_paragraph_run_length >= 3

    def test_normal_human_prose_low_signals(self):
        """Normal multi-sentence paragraphs produce low AI-tell signal."""
        text = (
            "The study examined cognitive biases in decision-making contexts. "
            "Participants were drawn from three distinct demographic groups. "
            "Each group completed a standardised battery of reasoning tasks.\n\n"
            "Results indicated significant variation across groups on abstract tasks. "
            "No significant difference was found on concrete problem-solving items. "
            "These findings align with previous research by Kahneman and colleagues."
        )
        result = compute_paragraph_stats(text)
        assert result.single_sentence_paragraph_ratio == pytest.approx(0.0)
        assert result.short_paragraph_run_length == 0
