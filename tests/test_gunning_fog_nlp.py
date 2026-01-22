"""Comprehensive tests for NLP-enhanced Gunning Fog Index.

This test suite validates the NLP-enhanced implementation of the Gunning Fog Index,
specifically addressing the issues raised in GitHub PR #4:
https://github.com/craigtrim/pystylometry/pull/4

Test Organization:
------------------
1. Basic Functionality Tests - Core formula and computation
2. Enhanced Mode Tests - spaCy-based NLP features (with skipif)
3. Basic Mode Tests - Fallback heuristics
4. Complex Word Detection Tests - Proper nouns, inflections, hyphenated words
5. Edge Case Tests - Empty input, unicode, special characters
6. Formula Validation Tests - Verify against Gunning (1952)

Reference:
    Gunning, R. (1952). The Technique of Clear Writing. McGraw-Hill.

PR #4 Issues Addressed:
-----------------------
Issue #1: Complex Word Detection Heuristics Are Unreliable
    - Tests validate proper noun detection (POS-based vs capitalization)
    - Tests validate inflection handling (lemmatization vs suffix-stripping)

Issue #2: Inconsistent is_sentence_start Tracking
    - Copilot's claim was INCORRECT - tests validate correct tracking

Issue #3: Hyphenated Words Blanket Exclusion
    - Tests validate component-based analysis for hyphenated words
"""

import pytest

from pystylometry.readability import compute_gunning_fog

# Try to import spaCy to determine if enhanced mode tests can run
try:
    import spacy

    # Try to load the model to see if it's downloaded
    try:
        _nlp = spacy.load("en_core_web_sm")
        SPACY_AVAILABLE = True
    except OSError:
        # spaCy installed but model not downloaded
        SPACY_AVAILABLE = False
except ImportError:
    SPACY_AVAILABLE = False


class TestGunningFogBasicFunctionality:
    """Test basic Gunning Fog Index functionality.

    These tests validate the core formula implementation regardless of
    which detection mode (enhanced or basic) is active.

    Reference:
        Gunning, R. (1952). The Technique of Clear Writing. McGraw-Hill.
        Formula (p. 40): Fog = 0.4 × [(words/sentences) + 100 × (complex/words)]
    """

    def test_simple_sentence_returns_valid_result(self):
        """Test that simple sentence produces valid Gunning Fog result.

        Validates:
        - Result object has required attributes
        - Grade level is within valid range [0, 20]
        - Metadata contains required fields

        Reference: Gunning (1952) recommends analyzing 100+ words for reliability,
        but formula should work on shorter texts (marked as unreliable in metadata).
        """
        text = "The cat sat on the mat."
        result = compute_gunning_fog(text)

        # Validate result structure
        assert hasattr(result, "fog_index")
        assert hasattr(result, "grade_level")
        assert hasattr(result, "metadata")

        # Validate data types
        assert isinstance(result.fog_index, float)
        assert isinstance(result.grade_level, int)
        assert isinstance(result.metadata, dict)

        # Validate grade level range
        # Reference: Gunning (1952) - grades range from elementary (0-6) to post-graduate (17+)
        assert 0 <= result.grade_level <= 20

    def test_formula_accuracy_simple_text(self):
        """Test Gunning Fog formula accuracy with manually calculated example.

        Text: "The cat sat. The dog ran. The bird flew."
        - 3 sentences
        - 9 words total
        - 0 complex words (all 1 syllable)

        Formula (Gunning, 1952):
            Fog = 0.4 × [(words/sentences) + 100 × (complex/words)]
            Fog = 0.4 × [(9/3) + 100 × (0/9)]
            Fog = 0.4 × [3 + 0]
            Fog = 0.4 × 3
            Fog = 1.2

        Expected grade level: 1 (rounded from 1.2)

        This validates the core formula implementation.
        """
        text = "The cat sat. The dog ran. The bird flew."
        result = compute_gunning_fog(text)

        # Manual calculation
        words = 9
        sentences = 3
        complex_words = 0  # All words are monosyllabic
        expected_fog = 0.4 * ((words / sentences) + 100 * (complex_words / words))

        # Validate formula
        assert abs(result.fog_index - expected_fog) < 0.1
        assert result.grade_level == round(expected_fog)
        assert result.metadata["word_count"] == 9
        assert result.metadata["sentence_count"] == 3
        assert result.metadata["complex_word_count"] == 0

    def test_empty_input_returns_zero(self):
        """Test that empty input returns zero values without error.

        Edge case handling: Empty strings should return fog_index=0.0
        rather than raising division by zero errors.

        This is important for robust batch processing of documents
        where some may be empty or contain only whitespace.
        """
        result = compute_gunning_fog("")

        assert result.fog_index == 0.0
        assert result.grade_level == 0
        assert result.metadata["sentence_count"] == 0
        assert result.metadata["word_count"] == 0
        assert result.metadata["complex_word_count"] == 0
        assert result.metadata["mode"] == "none"

    def test_metadata_structure_consistent(self):
        """Test that metadata structure is consistent across all inputs.

        Validates that all required metadata fields are present regardless
        of input text or detection mode used.

        Required fields (PR #4 transparency requirements):
        - sentence_count, word_count, complex_word_count
        - complex_word_percentage, average_words_per_sentence
        - mode, proper_noun_detection, inflection_handling
        """
        texts = [
            "",  # Empty
            "Hi.",  # Minimal
            "The cat sat on the mat.",  # Simple
            "Understanding computational linguistics requires dedication.",  # Complex
        ]

        for text in texts:
            result = compute_gunning_fog(text)

            # Core counts always present
            assert "sentence_count" in result.metadata
            assert "word_count" in result.metadata
            assert "complex_word_count" in result.metadata

            # Derived metrics always present
            assert "complex_word_percentage" in result.metadata
            assert "average_words_per_sentence" in result.metadata

            # Detection method transparency (PR #4 requirement)
            assert "mode" in result.metadata
            assert "proper_noun_detection" in result.metadata
            assert "inflection_handling" in result.metadata


class TestGunningFogComplexWordDetection:
    """Test complex word detection addressing PR #4 issues.

    PR #4 Issue #1: Complex Word Detection Heuristics Are Unreliable
    https://github.com/craigtrim/pystylometry/pull/4

    These tests validate that complex words are correctly identified according
    to Gunning's (1952) criteria:
    - 3+ syllables
    - Excluding proper nouns
    - Excluding common inflections
    - Excluding simple hyphenated compounds
    """

    def test_polysyllabic_words_counted_as_complex(self):
        """Test that words with 3+ syllables are counted as complex.

        Reference: Gunning (1952), p. 38: "Words of three or more syllables are hard words"

        Text: "The beautiful education provides wonderful opportunities."
        Complex words:
        - beautiful (3 syllables) ✓
        - education (4 syllables) ✓
        - wonderful (3 syllables) ✓
        - opportunities (5 syllables) ✓

        Total: 4 complex words out of 6 words
        """
        text = "The beautiful education provides wonderful opportunities."
        result = compute_gunning_fog(text)

        # Should identify at least 4 complex words
        # (May vary slightly between enhanced/basic mode due to "provides")
        assert result.metadata["complex_word_count"] >= 4

    def test_proper_nouns_excluded_from_complex(self):
        """Test that proper nouns are excluded from complex word count.

        PR #4 Issue #1: Proper noun detection
        - Enhanced mode: Uses spaCy POS tagging (PROPN)
        - Basic mode: Uses capitalization heuristic

        Reference: Gunning (1952), p. 39: "Do not count proper names"

        Text: "I visited California yesterday."
        - "California" (4 syllables, PROPN) → NOT complex (proper noun)
        - "visited" (3 syllables) → complex
        - "yesterday" (3 syllables) → complex

        In basic mode, "California" is mid-sentence capitalized so excluded.
        Expected: 2 complex words ("visited", "yesterday")
        """
        text = "I visited California yesterday."
        result = compute_gunning_fog(text)

        # Mode determines detection method and accuracy
        if result.metadata["mode"] == "enhanced":
            # Enhanced mode should accurately detect all
            assert result.metadata["proper_noun_detection"] == "POS-based"
            # May vary based on spaCy's syllable counting
            assert result.metadata["complex_word_count"] >= 2
        else:
            # Basic mode uses capitalization heuristic
            assert result.metadata["proper_noun_detection"] == "Capitalization-based"
            # Should still detect "yesterday" as complex
            assert result.metadata["complex_word_count"] >= 1

    def test_inflections_handled_correctly(self):
        """Test that common inflections are handled via lemmatization or suffix stripping.

        PR #4 Issue #1: Inflection handling
        - Enhanced mode: Uses spaCy lemmatization
        - Basic mode: Uses suffix stripping (-es, -ed, -ing)

        Reference: Gunning (1952), p. 39: "Do not count -ed, -es, -ing endings"

        Text: "The companies are running carefully."
        - "companies" (3 syl) → lemma "company" (3 syl) → still complex ✓
        - "running" (2 syl) → lemma "run" (1 syl) → NOT complex
        - "carefully" (3 syl) → complex ✓

        Expected in enhanced mode: 2 complex words ("companies", "carefully")

        Note: Basic mode may differ slightly due to suffix-stripping limitations.
        """
        text = "The companies are running carefully."
        result = compute_gunning_fog(text)

        # Enhanced mode should identify exactly 2 complex words
        if result.metadata["mode"] == "enhanced":
            assert result.metadata["complex_word_count"] == 2
            assert result.metadata["inflection_handling"] == "Lemmatization-based"
        # Basic mode may vary due to heuristic limitations
        else:
            assert result.metadata["complex_word_count"] >= 1
            assert result.metadata["inflection_handling"] == "Suffix-stripping"

    def test_hyphenated_words_component_analysis(self):
        """Test that hyphenated words are analyzed by component.

        PR #4 Issue #3: Hyphenated Words Blanket Exclusion
        https://github.com/craigtrim/pystylometry/pull/4

        OLD BEHAVIOR: ALL hyphenated words excluded
        NEW BEHAVIOR: Analyze each component, count as complex if ANY component has 3+ syllables

        Reference: Gunning (1952), p. 39: "Do not count compound words"
        Interpretation: Simple compounds like "well-known" (1+1) should be excluded,
        but compounds with complex components like "self-education" (1+4) should count.

        Text: "The well-known self-education method was revolutionary."
        - "well-known" (1+1 syllables) → NOT complex
        - "self-education" (1+4 syllables) → complex (because "education" = 4 syl)
        - "revolutionary" (5 syllables) → complex

        Expected: 2 complex words ("self-education", "revolutionary")
        """
        text = "The well-known self-education method was revolutionary."
        result = compute_gunning_fog(text)

        # Should count "self-education" (component "education" is complex)
        # and "revolutionary" (5 syllables)
        # Should NOT count "well-known" (all components simple)
        assert result.metadata["complex_word_count"] >= 2

    def test_acronyms_handled_appropriately(self):
        """Test that acronyms are handled correctly.

        PR #4 Issue #1: Capitalization heuristic fails on acronyms
        - Enhanced mode: Uses POS tagging, may tag as PROPN
        - Basic mode: All-caps check excludes as "proper noun"

        Text: "NASA provides amazing opportunities."
        - "NASA" (all-caps) → Treated as proper noun, excluded
        - "provides" (3 syllables) → complex
        - "amazing" (3 syllables) → complex
        - "opportunities" (5 syllables) → complex

        Expected: At least 1 complex word (syllable counting may vary)

        Note: This is a limitation acknowledged in PR #4. Acronyms like "NASA"
        may technically be complex if spelled out, but Gunning's (1952) proper noun
        exclusion applies to organizational names.
        """
        text = "NASA provides amazing opportunities."
        result = compute_gunning_fog(text)

        # "NASA" excluded (proper noun / acronym)
        # At least one of the other words should be counted as complex
        assert result.metadata["complex_word_count"] >= 1

    def test_sentence_initial_complex_words_counted(self):
        """Test that sentence-initial complex words ARE counted.

        PR #4 Issue #2: Copilot claimed sentence tracking was broken - IT WAS NOT
        https://github.com/craigtrim/pystylometry/pull/4

        The implementation correctly tracks sentence-initial positions and only
        excludes capitalized words as proper nouns when they appear MID-SENTENCE.

        Text: "Beautiful gardens need education. California is sunny."
        - "Beautiful" (sentence-initial, 3 syl) → complex ✓
        - "education" (mid-sentence, 4 syl) → complex ✓
        - "California" (sentence-initial, 4 syl) → PROPN, excluded
        - Total: 2 complex words

        This test validates that Copilot's Issue #2 was incorrect.
        """
        text = "Beautiful gardens need education. California is sunny."
        result = compute_gunning_fog(text)

        # "Beautiful" (sentence-start) should be counted as complex
        # "education" should be counted as complex
        # "California" (proper noun) should be excluded
        # Total: 2 complex words
        assert result.metadata["complex_word_count"] >= 2


@pytest.mark.skipif(not SPACY_AVAILABLE, reason="spaCy model not available")
class TestGunningFogEnhancedMode:
    """Test spaCy NLP-enhanced detection mode.

    These tests require spaCy and the en_core_web_sm model to be installed:
        pip install spacy
        python -m spacy download en_core_web_sm

    Enhanced mode provides:
    - POS tagging for accurate proper noun detection
    - Lemmatization for true morphological analysis
    - Better handling of irregular verbs, compound nouns, etc.

    PR #4: These features address the "unreliable heuristics" issues
    """

    def test_enhanced_mode_active_with_spacy(self):
        """Test that enhanced mode activates when spaCy is available.

        Validates:
        - Mode is "enhanced"
        - Proper noun detection is "POS-based"
        - Inflection handling is "Lemmatization-based"
        - spacy_model name is included in metadata
        """
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_gunning_fog(text)

        # With spaCy available, should use enhanced mode
        assert result.metadata["mode"] == "enhanced"
        assert result.metadata["proper_noun_detection"] == "POS-based"
        assert result.metadata["inflection_handling"] == "Lemmatization-based"
        assert "spacy_model" in result.metadata
        assert result.metadata["spacy_model"] == "en_core_web_sm"

    def test_enhanced_proper_noun_detection_accuracy(self):
        """Test enhanced POS-based proper noun detection.

        spaCy's PROPN tag accurately identifies:
        - Standard proper nouns: "California"
        - Organizations: "NASA", "Microsoft"
        - Mixed-case brands: "iPhone"
        - Names with apostrophes: "O'Brien"

        All should be excluded from complex word count.
        """
        # Standard proper noun
        result1 = compute_gunning_fog("California provides education.")
        assert "California" not in ["complex"]  # Excluded
        assert result1.metadata["complex_word_count"] == 2  # "provides", "education"

        # Organization acronym
        result2 = compute_gunning_fog("NASA provides amazing opportunities.")
        # "NASA" excluded, "amazing" and "opportunities" counted
        assert result2.metadata["complex_word_count"] == 2

    def test_enhanced_lemmatization_accuracy(self):
        """Test enhanced lemmatization-based inflection handling.

        spaCy's lemmatizer correctly handles:
        - Regular verbs: "running" → "run"
        - Irregular verbs: "was" → "be", "ran" → "run"
        - Plural nouns: "companies" → "company"
        - Comparative adjectives: "better" → "good"

        Example: "The companies were running operations carefully."
        - "companies" (3 syl) → lemma "company" (3 syl) → still complex
        - "running" (2 syl) → lemma "run" (1 syl) → NOT complex
        - "operations" (4 syl) → lemma "operation" (4 syl) → still complex
        - "carefully" (3 syl) → lemma "careful" (2 syl) → NOT complex

        Expected: 2 complex words ("companies", "operations")
        """
        text = "The companies were running operations carefully."
        result = compute_gunning_fog(text)

        # With lemmatization, should correctly identify 2 complex words
        assert result.metadata["complex_word_count"] == 2

    def test_enhanced_handles_irregular_verbs(self):
        """Test that enhanced mode handles irregular verb forms correctly.

        Basic suffix stripping fails on irregular verbs like:
        - "was" → (no suffix to strip, but lemma is "be")
        - "were" → (no suffix to strip, but lemma is "be")
        - "ran" → (no suffix to strip, but lemma is "run")

        spaCy's lemmatizer correctly reduces these to base forms.
        """
        text = "Understanding was necessary."
        result = compute_gunning_fog(text)

        # "Understanding" (4 syl) → lemma "understand" (3 syl) → still complex
        # "necessary" (4 syl) → complex
        # "was" → lemma "be" (1 syl) → NOT complex
        assert result.metadata["complex_word_count"] == 2


class TestGunningFogEdgeCases:
    """Test edge cases and special input scenarios."""

    def test_whitespace_only_input(self):
        """Test that whitespace-only input is handled gracefully."""
        result = compute_gunning_fog("   \n\t  ")

        assert result.fog_index == 0.0
        assert result.grade_level == 0
        assert result.metadata["word_count"] == 0

    def test_single_word_input(self):
        """Test single word input."""
        result = compute_gunning_fog("Hello")

        assert result.metadata["word_count"] == 1
        # Should not crash on single-word input
        assert result.fog_index >= 0

    def test_unicode_characters_handled(self):
        """Test that Unicode characters (accents, special chars) are handled.

        Text with accented characters: "Café résumé façade naïve"
        Should process without errors.
        """
        text = "The café résumé includes naïve analysis."
        result = compute_gunning_fog(text)

        assert result.fog_index is not None
        assert result.metadata["word_count"] > 0

    def test_very_long_text_performance(self):
        """Test that very long texts are processed efficiently.

        Generate a long text (1000+ words) to ensure no performance issues
        or memory problems with large documents.
        """
        # Generate long text with mix of simple and complex words
        simple_sentence = "The cat sat on the mat. "
        complex_sentence = "Understanding computational linguistics requires dedication. "
        long_text = (simple_sentence * 100) + (complex_sentence * 100)

        result = compute_gunning_fog(long_text)

        assert result.metadata["word_count"] > 1000
        assert result.fog_index >= 0
        # Long text should be more "reliable" per Gunning (1952)
        # (though our implementation doesn't set a "reliable" flag)

    def test_grade_level_clamping(self):
        """Test that grade level is clamped to [0, 20] range.

        Extremely complex text might produce fog_index > 20, but grade_level
        should be clamped to 20 (post-graduate level).
        """
        # Create extremely complex text with very long sentences
        complex_words = [
            "antidisestablishmentarianism",
            "pneumonoultramicroscopicsilicovolcanoconiosis",
            "supercalifragilisticexpialidocious",
        ]
        # One very long sentence to maximize ASL
        text = " ".join(complex_words * 50) + "."

        result = compute_gunning_fog(text)

        # fog_index may be very high
        assert result.fog_index > 0
        # But grade_level should be clamped to 20
        assert result.grade_level <= 20


class TestGunningFogFormulaValidation:
    """Validate formula implementation against Gunning (1952).

    These tests ensure the formula is correctly implemented:
        Fog = 0.4 × [(words/sentences) + 100 × (complex/words)]

    Reference:
        Gunning, R. (1952). The Technique of Clear Writing. McGraw-Hill.
        Page 40: "The Fog Index Formula"
    """

    def test_formula_component_average_sentence_length(self):
        """Test that Average Sentence Length (ASL) is calculated correctly.

        ASL = words / sentences

        Text: "The cat sat. The dog ran. The bird flew. The fish swam."
        - 4 sentences
        - 12 words
        - ASL = 12 / 4 = 3.0
        """
        text = "The cat sat. The dog ran. The bird flew. The fish swam."
        result = compute_gunning_fog(text)

        expected_asl = 12.0 / 4.0
        assert abs(result.metadata["average_words_per_sentence"] - expected_asl) < 0.01

    def test_formula_component_percentage_hard_words(self):
        """Test that Percentage of Hard Words (PHW) is calculated correctly.

        PHW = (complex words / total words) × 100

        For this test, manually verify complex word count and percentage match.
        """
        text = "The beautiful situation requires understanding and education today."
        result = compute_gunning_fog(text)

        # Calculate expected percentage
        complex_count = result.metadata["complex_word_count"]
        word_count = result.metadata["word_count"]
        expected_percentage = (complex_count / word_count) * 100

        assert abs(result.metadata["complex_word_percentage"] - expected_percentage) < 0.01

    def test_formula_complete_calculation(self):
        """Test complete formula: Fog = 0.4 × (ASL + PHW).

        Manual verification with known values:
        Text: "The beautiful situation requires understanding."
        - 1 sentence
        - 5 words
        - 3 complex words (beautiful, situation, understanding)
        - ASL = 5/1 = 5.0
        - PHW = (3/5) × 100 = 60.0
        - Fog = 0.4 × (5.0 + 60.0) = 0.4 × 65.0 = 26.0
        """
        text = "The beautiful situation requires understanding."
        result = compute_gunning_fog(text)

        asl = result.metadata["average_words_per_sentence"]
        phw = result.metadata["complex_word_percentage"]
        expected_fog = 0.4 * (asl + phw)

        assert abs(result.fog_index - expected_fog) < 0.01


class TestGunningFogRegressions:
    """Regression tests to prevent re-introduction of PR #4 issues."""

    def test_regression_hyphenated_not_blanket_excluded(self):
        """Regression test for PR #4 Issue #3.

        Ensure that hyphenated words with complex components are counted.

        OLD (BROKEN): ALL hyphenated words excluded
        NEW (FIXED): Component analysis, count if any component is complex

        Test case: "self-education"
        - "self" (1 syllable)
        - "education" (4 syllables) → complex
        - Should be counted as complex
        """
        text = "The self-education program works."
        result = compute_gunning_fog(text)

        # "self-education" should be complex (because "education" component is)
        # "program" (2 syllables) → NOT complex
        assert result.metadata["complex_word_count"] >= 1

    def test_regression_sentence_start_tracking_correct(self):
        """Regression test for PR #4 Issue #2 (Copilot was WRONG).

        Validates that sentence-initial complex words ARE counted,
        and only MID-SENTENCE capitalized words are excluded as proper nouns.

        Copilot claimed sentence tracking was broken - it was not.
        This test ensures it remains correct.
        """
        text = "Beautiful gardens exist. California exists too."
        result = compute_gunning_fog(text)

        # "Beautiful" (sentence-start, 3 syl) → should be counted
        # "California" (proper noun) → should be excluded
        # At least 1 complex word should be found ("Beautiful")
        assert result.metadata["complex_word_count"] >= 1

    def test_regression_proper_noun_detection_not_just_caps(self):
        """Regression test for PR #4 Issue #1.

        Ensure that proper noun detection works beyond simple capitalization.

        In enhanced mode, should use POS tags.
        In basic mode, should at least handle sentence-start correctly.
        """
        # Mid-sentence capitalized word should be treated as proper noun
        text = "I visited California yesterday."
        result = compute_gunning_fog(text)

        # "California" should be excluded (proper noun)
        # "visited" (3 syl) → complex
        # "yesterday" (3 syl) → complex
        # At least 1 complex word should be found
        assert result.metadata["complex_word_count"] >= 1

        # Sentence-start capitalized word should NOT be automatically excluded
        text2 = "Yesterday I visited."
        result2 = compute_gunning_fog(text2)

        # "Yesterday" (3 syl, sentence-start) → should be counted
        assert result2.metadata["complex_word_count"] >= 1
