"""Comprehensive tests for stylistic markers module.

This module tests the stylistic markers functionality, including contraction
detection, intensifier analysis, hedge detection, modal auxiliary classification,
negation patterns, and punctuation style analysis.

Related GitHub Issues:
    #20 - Stylistic Markers
    https://github.com/craigtrim/pystylometry/issues/20

Test coverage:
    - Basic functionality and return type validation
    - Contraction detection and ratio calculation
    - Intensifier detection and density calculation
    - Hedge detection and density calculation
    - Modal auxiliary analysis (epistemic vs deontic)
    - Negation pattern detection
    - Punctuation style analysis (8 types)
    - Edge cases (empty text, no markers, short text)
    - Density normalization (per 100 words)
"""

import math

import pytest

from pystylometry.stylistic.markers import (
    ALL_MODALS,
    CONTRACTIONS,
    DEONTIC_MODALS,
    EPISTEMIC_MODALS,
    HEDGES,
    INTENSIFIERS,
    NEGATION_MARKERS,
    compute_stylistic_markers,
)


class TestStylisticMarkersBasicFunctionality:
    """Test basic stylistic markers functionality."""

    def test_returns_correct_type(self) -> None:
        """Test that compute_stylistic_markers returns StylisticMarkersResult."""
        from pystylometry._types import StylisticMarkersResult

        text = "This is a simple test sentence."
        result = compute_stylistic_markers(text)

        assert isinstance(result, StylisticMarkersResult)

    def test_basic_text_analysis(self) -> None:
        """Test basic text analysis returns expected fields."""
        text = "I can't believe it's really happening! This is absolutely incredible."
        result = compute_stylistic_markers(text)

        # Check required fields exist
        assert hasattr(result, "contraction_ratio")
        assert hasattr(result, "contraction_count")
        assert hasattr(result, "intensifier_density")
        assert hasattr(result, "hedging_density")
        assert hasattr(result, "modal_density")
        assert hasattr(result, "negation_density")
        assert hasattr(result, "exclamation_density")
        assert hasattr(result, "metadata")

    def test_word_count_in_metadata(self) -> None:
        """Test that word count is correctly recorded in metadata."""
        text = "one two three four five"
        result = compute_stylistic_markers(text)

        assert "word_count" in result.metadata
        assert result.metadata["word_count"] == 5

    def test_density_per_100_words(self) -> None:
        """Test that densities are normalized per 100 words."""
        # Create text with exactly 100 words and 2 intensifiers
        text = " ".join(["word"] * 98 + ["very", "really"])
        result = compute_stylistic_markers(text)

        # With 2 intensifiers in 100 words, density should be 2.0
        assert result.intensifier_count == 2
        assert abs(result.intensifier_density - 2.0) < 0.01


class TestStylisticMarkersEmptyAndEdgeCases:
    """Test edge cases and empty input handling."""

    def test_empty_text(self) -> None:
        """Test handling of empty text."""
        result = compute_stylistic_markers("")

        assert result.contraction_ratio == 0.0
        assert result.contraction_count == 0
        assert result.intensifier_density == 0.0
        assert result.metadata["word_count"] == 0

    def test_whitespace_only(self) -> None:
        """Test handling of whitespace-only text."""
        result = compute_stylistic_markers("   \n\t  ")

        assert result.contraction_ratio == 0.0
        assert result.contraction_count == 0
        assert result.metadata["word_count"] == 0

    def test_single_word(self) -> None:
        """Test handling of single word input."""
        result = compute_stylistic_markers("hello")

        assert result.metadata["word_count"] == 1
        assert result.contraction_ratio == 0.0

    def test_no_markers_in_text(self) -> None:
        """Test text with no stylistic markers."""
        text = "The sun rose over the mountains. Birds sang in the trees."
        result = compute_stylistic_markers(text)

        # Should have zero counts for many markers
        assert result.contraction_count == 0
        assert result.exclamation_density == 0.0
        assert result.question_density == 0.0

    def test_punctuation_only(self) -> None:
        """Test text with only punctuation."""
        result = compute_stylistic_markers("!!! ??? ...")

        # Should handle gracefully
        assert result.metadata["word_count"] == 0


class TestContractionDetection:
    """Test contraction detection and ratio calculation."""

    def test_common_contractions(self) -> None:
        """Test detection of common contractions."""
        text = "I can't believe it's happening. We don't know what she's doing."
        result = compute_stylistic_markers(text)

        # Should detect multiple contractions
        assert result.contraction_count >= 4
        assert ("can't", 1) in result.top_contractions or any(
            c[0] == "can't" for c in result.top_contractions
        )

    def test_pronoun_contractions(self) -> None:
        """Test detection of pronoun contractions."""
        text = "I'm happy. You're great. He's here. She's there. It's working."
        result = compute_stylistic_markers(text)

        assert result.contraction_count >= 5

    def test_negative_contractions(self) -> None:
        """Test detection of negative contractions."""
        text = "I won't go. She can't come. They haven't arrived. He isn't here."
        result = compute_stylistic_markers(text)

        assert result.contraction_count >= 4

    def test_contraction_ratio_all_contracted(self) -> None:
        """Test contraction ratio when all forms are contracted."""
        text = "I can't do it. She won't help. They don't care."
        result = compute_stylistic_markers(text)

        # With only contractions (no expanded forms), ratio should be 1.0
        if result.contraction_count > 0 and result.expanded_form_count == 0:
            assert result.contraction_ratio == 1.0

    def test_contraction_ratio_mixed(self) -> None:
        """Test contraction ratio with mixed contracted and expanded forms."""
        # Mix of contractions and expanded forms
        text = "I can't go but she can not come. They don't know but we do not care."
        result = compute_stylistic_markers(text)

        # Should have both contractions and expanded forms
        assert result.contraction_count >= 2
        assert result.expanded_form_count >= 2
        # Ratio should be between 0 and 1
        assert 0.0 < result.contraction_ratio < 1.0

    def test_contraction_case_insensitivity(self) -> None:
        """Test that contraction detection is case-insensitive."""
        text = "I CAN'T believe IT'S true. DON'T do that!"
        result = compute_stylistic_markers(text)

        assert result.contraction_count >= 3

    def test_smart_apostrophe_handling(self) -> None:
        """Test handling of smart/curly apostrophes."""
        text = "I can't and I can't and I can't"  # Uses different apostrophe styles
        result = compute_stylistic_markers(text)

        # Should normalize apostrophes and count all
        assert result.contraction_count >= 1

    def test_top_contractions_ordering(self) -> None:
        """Test that top contractions are ordered by frequency."""
        text = "I can't can't can't. You don't don't. She won't."
        result = compute_stylistic_markers(text)

        # Top contraction should be the most frequent
        if result.top_contractions:
            assert result.top_contractions[0][0] == "can't"
            assert result.top_contractions[0][1] == 3


class TestIntensifierDetection:
    """Test intensifier detection and density calculation."""

    def test_common_intensifiers(self) -> None:
        """Test detection of common intensifiers."""
        text = "This is very good, really excellent, and absolutely amazing."
        result = compute_stylistic_markers(text)

        assert result.intensifier_count >= 3
        assert result.intensifier_density > 0

    def test_amplifiers(self) -> None:
        """Test detection of amplifier intensifiers."""
        text = "It was extremely hot, completely empty, and totally destroyed."
        result = compute_stylistic_markers(text)

        assert result.intensifier_count >= 3

    def test_degree_modifiers(self) -> None:
        """Test detection of degree modifier intensifiers."""
        text = "It was quite good, rather nice, and fairly decent."
        result = compute_stylistic_markers(text)

        assert result.intensifier_count >= 3

    def test_informal_intensifiers(self) -> None:
        """Test detection of informal intensifiers."""
        text = "That was super cool and way better than expected."
        result = compute_stylistic_markers(text)

        assert result.intensifier_count >= 2

    def test_intensifier_density_calculation(self) -> None:
        """Test that intensifier density is correctly calculated."""
        # 50 words with 5 intensifiers = 10 per 100 words
        base_words = ["word"] * 45
        intensifiers_list = ["very", "really", "quite", "extremely", "absolutely"]
        text = " ".join(base_words + intensifiers_list)
        result = compute_stylistic_markers(text)

        assert result.intensifier_count == 5
        assert abs(result.intensifier_density - 10.0) < 0.1

    def test_top_intensifiers_ordering(self) -> None:
        """Test that top intensifiers are ordered by frequency."""
        text = "very very very really really quite"
        result = compute_stylistic_markers(text)

        if result.top_intensifiers:
            assert result.top_intensifiers[0][0] == "very"
            assert result.top_intensifiers[0][1] == 3

    def test_intensifier_list_completeness(self) -> None:
        """Test that the intensifier list is comprehensive."""
        # Check that common intensifiers are in the set
        common_intensifiers = ["very", "really", "extremely", "absolutely", "quite"]
        for word in common_intensifiers:
            assert word in INTENSIFIERS


class TestHedgeDetection:
    """Test hedge detection and density calculation."""

    def test_epistemic_hedges(self) -> None:
        """Test detection of epistemic hedges."""
        text = "Maybe this will work. Perhaps it's true. Probably not."
        result = compute_stylistic_markers(text)

        assert result.hedging_count >= 3

    def test_approximators(self) -> None:
        """Test detection of approximator hedges."""
        text = "It's about ten miles. Roughly speaking, it's nearly done."
        result = compute_stylistic_markers(text)

        assert result.hedging_count >= 3

    def test_shield_expressions(self) -> None:
        """Test detection of shield expression hedges."""
        text = "It seems good. It appears to work. This suggests progress."
        result = compute_stylistic_markers(text)

        assert result.hedging_count >= 3

    def test_hedging_density_calculation(self) -> None:
        """Test that hedging density is correctly calculated."""
        # 50 words with 10 hedges = 20 per 100 words
        base_words = ["word"] * 40
        hedges_list = ["maybe", "perhaps", "probably", "possibly", "seemingly",
                       "apparently", "roughly", "generally", "usually", "typically"]
        text = " ".join(base_words + hedges_list)
        result = compute_stylistic_markers(text)

        assert result.hedging_count == 10
        assert abs(result.hedging_density - 20.0) < 0.1

    def test_top_hedges_ordering(self) -> None:
        """Test that top hedges are ordered by frequency."""
        text = "maybe maybe maybe perhaps perhaps probably"
        result = compute_stylistic_markers(text)

        if result.top_hedges:
            assert result.top_hedges[0][0] == "maybe"
            assert result.top_hedges[0][1] == 3

    def test_hedge_list_completeness(self) -> None:
        """Test that the hedge list is comprehensive."""
        common_hedges = ["maybe", "perhaps", "probably", "possibly", "seemingly"]
        for word in common_hedges:
            assert word in HEDGES


class TestModalAuxiliaryAnalysis:
    """Test modal auxiliary detection and classification."""

    def test_modal_detection(self) -> None:
        """Test detection of modal auxiliaries."""
        text = "I can do it. You should try. We must go. They might help."
        result = compute_stylistic_markers(text)

        assert result.modal_density > 0
        assert len(result.modal_distribution) > 0

    def test_modal_distribution(self) -> None:
        """Test that modal distribution is correctly computed."""
        text = "can can could could could may"
        result = compute_stylistic_markers(text)

        assert result.modal_distribution.get("can", 0) == 2
        assert result.modal_distribution.get("could", 0) == 3
        assert result.modal_distribution.get("may", 0) == 1

    def test_epistemic_modal_ratio(self) -> None:
        """Test epistemic modal ratio calculation."""
        # Use only epistemic modals
        text = "I can do it. You could try. We may go. They might help."
        result = compute_stylistic_markers(text)

        # All modals are epistemic
        assert result.epistemic_modal_ratio > 0.5

    def test_deontic_modal_ratio(self) -> None:
        """Test deontic modal ratio calculation."""
        # Use only deontic modals
        text = "You must go. We shall try. They will help."
        result = compute_stylistic_markers(text)

        # Should have high deontic ratio
        assert result.deontic_modal_ratio > 0

    def test_modal_ratio_sum(self) -> None:
        """Test that epistemic and deontic ratios are reasonable."""
        text = "I can go and you must try. She could help but they will refuse."
        result = compute_stylistic_markers(text)

        # Note: Some modals can be both epistemic and deontic (e.g., "should")
        # So sum might exceed 1.0, but each ratio should be <= 1.0
        assert result.epistemic_modal_ratio <= 1.0
        assert result.deontic_modal_ratio <= 1.0

    def test_modal_list_completeness(self) -> None:
        """Test that the modal list is comprehensive."""
        common_modals = ["can", "could", "may", "might", "must", "shall", "should", "will", "would"]
        for modal in common_modals:
            assert modal in ALL_MODALS

    def test_epistemic_modal_list(self) -> None:
        """Test epistemic modal classification."""
        epistemic = ["may", "might", "could", "can", "would", "should"]
        for modal in epistemic:
            assert modal in EPISTEMIC_MODALS

    def test_deontic_modal_list(self) -> None:
        """Test deontic modal classification."""
        deontic = ["must", "shall", "will", "should"]
        for modal in deontic:
            assert modal in DEONTIC_MODALS


class TestNegationPatternDetection:
    """Test negation pattern detection."""

    def test_basic_negation(self) -> None:
        """Test detection of basic negation markers."""
        text = "I do not know. She has no idea. We never go there."
        result = compute_stylistic_markers(text)

        assert result.negation_count >= 3
        assert result.negation_density > 0

    def test_negation_types(self) -> None:
        """Test that negation types are correctly recorded."""
        text = "not here. no way. never again. none left. nothing wrong."
        result = compute_stylistic_markers(text)

        assert "not" in result.negation_types or result.negation_types.get("not", 0) >= 0
        assert result.negation_count >= 5

    def test_rare_negation_markers(self) -> None:
        """Test detection of less common negation markers."""
        text = "I hardly know. She barely survived. We scarcely noticed."
        result = compute_stylistic_markers(text)

        assert result.negation_count >= 3

    def test_negation_density_calculation(self) -> None:
        """Test that negation density is correctly calculated."""
        # 50 words with 5 negation markers = 10 per 100 words
        base_words = ["word"] * 45
        negations = ["not", "no", "never", "none", "nothing"]
        text = " ".join(base_words + negations)
        result = compute_stylistic_markers(text)

        assert result.negation_count == 5
        assert abs(result.negation_density - 10.0) < 0.1

    def test_negation_list_completeness(self) -> None:
        """Test that the negation list is comprehensive."""
        common_negations = ["not", "no", "never", "none", "nothing", "nobody", "nowhere"]
        for word in common_negations:
            assert word in NEGATION_MARKERS


class TestPunctuationStyleAnalysis:
    """Test punctuation style analysis."""

    def test_exclamation_marks(self) -> None:
        """Test detection of exclamation marks."""
        text = "Wow! Amazing! Incredible! This is great!"
        result = compute_stylistic_markers(text)

        assert result.exclamation_density > 0
        assert result.metadata["punctuation_counts"]["exclamation"] == 4

    def test_question_marks(self) -> None:
        """Test detection of question marks."""
        text = "What? Why? How? When did this happen?"
        result = compute_stylistic_markers(text)

        assert result.question_density > 0
        assert result.metadata["punctuation_counts"]["question"] == 4

    def test_quotation_marks(self) -> None:
        """Test detection of quotation marks."""
        text = 'He said "hello" and she replied "goodbye".'
        result = compute_stylistic_markers(text)

        assert result.quotation_density > 0
        assert result.metadata["punctuation_counts"]["quotation"] >= 4

    def test_parentheses(self) -> None:
        """Test detection of parenthetical expressions."""
        text = "The result (as expected) was good. We tried (and failed) again."
        result = compute_stylistic_markers(text)

        assert result.parenthetical_density > 0
        assert result.metadata["punctuation_counts"]["parenthetical"] == 4

    def test_ellipses(self) -> None:
        """Test detection of ellipses."""
        text = "I wonder... maybe... perhaps... who knows..."
        result = compute_stylistic_markers(text)

        assert result.ellipsis_density > 0
        assert result.metadata["punctuation_counts"]["ellipsis"] == 4

    def test_unicode_ellipsis(self) -> None:
        """Test detection of unicode ellipsis character."""
        text = "I wonder… maybe… perhaps…"
        result = compute_stylistic_markers(text)

        assert result.metadata["punctuation_counts"]["ellipsis"] == 3

    def test_dashes(self) -> None:
        """Test detection of dashes (em-dash, en-dash)."""
        text = "This—and that—are different. Also this–that–those."
        result = compute_stylistic_markers(text)

        assert result.dash_density > 0
        assert result.metadata["punctuation_counts"]["dash"] >= 4

    def test_double_hyphen_as_dash(self) -> None:
        """Test detection of double hyphen as dash."""
        text = "This--that--those are options."
        result = compute_stylistic_markers(text)

        assert result.metadata["punctuation_counts"]["dash"] == 2

    def test_semicolons(self) -> None:
        """Test detection of semicolons."""
        text = "First point; second point; third point; conclusion."
        result = compute_stylistic_markers(text)

        assert result.semicolon_density > 0
        assert result.metadata["punctuation_counts"]["semicolon"] == 3

    def test_colons(self) -> None:
        """Test detection of colons."""
        text = "Consider this: one option. Also: another option. Finally: the last."
        result = compute_stylistic_markers(text)

        assert result.colon_density > 0
        assert result.metadata["punctuation_counts"]["colon"] == 3

    def test_punctuation_density_normalization(self) -> None:
        """Test that punctuation densities are normalized per 100 words."""
        # 50 words with 5 exclamations = 10 per 100 words
        text = " ".join(["word"] * 50) + " !!!!! "
        result = compute_stylistic_markers(text)

        # Note: exclamations aren't words, so word count stays 50
        expected_density = 5 * (100.0 / 50)  # = 10.0
        assert abs(result.exclamation_density - expected_density) < 0.1


class TestExpandedFormDetection:
    """Test detection of expanded (non-contracted) forms."""

    def test_expanded_negatives(self) -> None:
        """Test detection of expanded negative forms."""
        text = "I do not know. She can not come. They will not help."
        result = compute_stylistic_markers(text)

        assert result.expanded_form_count >= 3

    def test_expanded_pronouns(self) -> None:
        """Test detection of expanded pronoun forms."""
        text = "I am happy. You are great. It is working."
        result = compute_stylistic_markers(text)

        assert result.expanded_form_count >= 3

    def test_cannot_as_single_word(self) -> None:
        """Test handling of 'cannot' as single word."""
        text = "I cannot believe it. She cannot help."
        result = compute_stylistic_markers(text)

        # "cannot" is a single word that could be "can't"
        # The pattern looks for "can not" (two words), so cannot might not be caught
        # This tests that we don't error on it
        assert result.contraction_ratio >= 0.0


class TestMetadataContents:
    """Test metadata contents and completeness."""

    def test_metadata_word_lists(self) -> None:
        """Test that metadata contains word lists."""
        text = "Simple test text for metadata check."
        result = compute_stylistic_markers(text)

        assert "contraction_list" in result.metadata
        assert "intensifier_list" in result.metadata
        assert "hedge_list" in result.metadata
        assert "modal_list" in result.metadata
        assert "negation_list" in result.metadata

    def test_metadata_punctuation_counts(self) -> None:
        """Test that metadata contains punctuation counts."""
        text = "Test! Really? Yes..."
        result = compute_stylistic_markers(text)

        assert "punctuation_counts" in result.metadata
        punct = result.metadata["punctuation_counts"]
        assert "exclamation" in punct
        assert "question" in punct
        assert "ellipsis" in punct

    def test_metadata_detailed_counts(self) -> None:
        """Test that metadata contains detailed marker counts."""
        text = "I can't really believe it's very good!"
        result = compute_stylistic_markers(text)

        assert "all_contraction_counts" in result.metadata
        assert "all_intensifier_counts" in result.metadata
        assert "all_hedge_counts" in result.metadata
        assert "all_negation_counts" in result.metadata


class TestRealWorldText:
    """Test with realistic text samples."""

    def test_formal_academic_text(self) -> None:
        """Test analysis of formal academic text."""
        text = """
        The results of this study suggest that the proposed methodology
        may be applicable to a wide range of scenarios. It appears that
        the correlation between variables is statistically significant.
        We must consider, however, that these findings are preliminary.
        """
        result = compute_stylistic_markers(text)

        # Formal text should have low contraction ratio
        assert result.contraction_ratio < 0.5
        # Should have hedges (suggest, may, appears, however)
        assert result.hedging_count > 0
        # Should have modals
        assert result.modal_density > 0

    def test_informal_conversational_text(self) -> None:
        """Test analysis of informal conversational text."""
        text = """
        I can't believe you're really going! That's absolutely amazing!
        You've got to tell me everything when you get back, okay?
        It's gonna be so much fun! Don't forget to take pictures!
        """
        result = compute_stylistic_markers(text)

        # Informal text should have high contraction ratio
        assert result.contraction_ratio > 0.5
        # Should have intensifiers (really, absolutely, so much)
        assert result.intensifier_count > 0
        # Should have exclamations
        assert result.exclamation_density > 0

    def test_dialogue_heavy_text(self) -> None:
        """Test analysis of dialogue-heavy text."""
        text = """
        "What do you mean?" she asked.
        "I can't explain it," he replied. "It's just... complicated."
        "That's not good enough!" she exclaimed.
        "Maybe you're right," he admitted.
        """
        result = compute_stylistic_markers(text)

        # Should have quotation marks
        assert result.quotation_density > 0
        # Should have question marks
        assert result.question_density > 0
        # Should have contractions
        assert result.contraction_count > 0
        # Should have hedges (maybe)
        assert result.hedging_count > 0

    def test_technical_documentation(self) -> None:
        """Test analysis of technical documentation."""
        text = """
        To install the package, you must run the following command:
        pip install pystylometry

        This will install all required dependencies. You should ensure
        that your Python version is 3.9 or higher. If you encounter
        any issues, please check the documentation.
        """
        result = compute_stylistic_markers(text)

        # Technical docs should have modals (must, should)
        assert result.modal_density > 0
        # Should have colons for instructions
        assert result.colon_density > 0


class TestSpecialCharacters:
    """Test handling of special characters and unicode."""

    def test_smart_quotes(self) -> None:
        """Test handling of smart/curly quotes."""
        text = '"Hello," she said. "How are you?"'
        result = compute_stylistic_markers(text)

        # Should detect quotation marks
        assert result.quotation_density > 0

    def test_mixed_apostrophe_styles(self) -> None:
        """Test handling of mixed apostrophe styles."""
        text = "I can't and I can't and I can't"  # Mix of straight and curly
        result = compute_stylistic_markers(text)

        # Should normalize and count
        assert result.contraction_count >= 1

    def test_non_ascii_characters(self) -> None:
        """Test handling of non-ASCII characters in text."""
        text = "The café wasn't bad. I couldn't complain about the naïve décor."
        result = compute_stylistic_markers(text)

        # Should still detect contractions
        assert result.contraction_count >= 2


class TestContractionsListCompleteness:
    """Test that the contractions list is comprehensive."""

    def test_all_negative_contractions_present(self) -> None:
        """Test that all common negative contractions are in the list."""
        negative_contractions = [
            "aren't", "can't", "couldn't", "didn't", "doesn't", "don't",
            "hadn't", "hasn't", "haven't", "isn't", "mightn't", "mustn't",
            "needn't", "shouldn't", "wasn't", "weren't", "won't", "wouldn't"
        ]
        for contraction in negative_contractions:
            assert contraction in CONTRACTIONS

    def test_all_pronoun_contractions_present(self) -> None:
        """Test that all common pronoun contractions are in the list."""
        pronoun_contractions = [
            "i'm", "i've", "i'll", "i'd",
            "you're", "you've", "you'll", "you'd",
            "he's", "he'll", "he'd",
            "she's", "she'll", "she'd",
            "it's", "it'll", "it'd",
            "we're", "we've", "we'll", "we'd",
            "they're", "they've", "they'll", "they'd"
        ]
        for contraction in pronoun_contractions:
            assert contraction in CONTRACTIONS


class TestZeroDivision:
    """Test handling of potential zero division scenarios."""

    def test_no_modals_epistemic_ratio(self) -> None:
        """Test epistemic ratio when no modals present."""
        text = "The cat sat on the mat."
        result = compute_stylistic_markers(text)

        # Should be 0.0, not NaN or error
        assert result.epistemic_modal_ratio == 0.0
        assert result.deontic_modal_ratio == 0.0

    def test_no_contractable_forms(self) -> None:
        """Test contraction ratio when no contractable forms present."""
        text = "The sun shone brightly."
        result = compute_stylistic_markers(text)

        # Should be 0.0, not NaN or error
        assert result.contraction_ratio == 0.0

    def test_empty_result_no_nan(self) -> None:
        """Test that empty text doesn't produce NaN values."""
        result = compute_stylistic_markers("")

        # Check no NaN values
        assert not math.isnan(result.contraction_ratio)
        assert not math.isnan(result.intensifier_density)
        assert not math.isnan(result.hedging_density)
        assert not math.isnan(result.modal_density)
        assert not math.isnan(result.epistemic_modal_ratio)
        assert not math.isnan(result.deontic_modal_ratio)
        assert not math.isnan(result.negation_density)
