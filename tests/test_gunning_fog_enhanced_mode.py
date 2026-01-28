"""Comprehensive tests for Gunning Fog Index computation."""

from pystylometry.readability import compute_gunning_fog

# Try to import spaCy to determine if enhanced mode tests can run
try:
    import spacy

    # Try to load the model to see if it's downloaded
    try:
        spacy.load("en_core_web_sm")
        SPACY_AVAILABLE = True
    except OSError:
        # spaCy installed but model not downloaded
        SPACY_AVAILABLE = False
except ImportError:
    SPACY_AVAILABLE = False


class TestGunningFogEnhancedMode:
    """Test spaCy NLP-enhanced detection mode (PR #4).

    These tests validate the enhanced mode features added in PR #4:
    https://github.com/craigtrim/pystylometry/pull/4

    Enhanced mode provides:
    - POS tagging for accurate proper noun detection (vs capitalization heuristic)
    - Lemmatization for true morphological analysis (vs suffix stripping)
    - Better handling of irregular verbs, compound nouns, etc.

    Why Enhanced Mode:
    ------------------
    The basic mode (capitalization + suffix stripping) has limitations:
    - Fails on acronyms (NASA), mixed-case (iPhone), all-caps text
    - Can't handle irregular verbs ("was" → "be", "ran" → "run")
    - Misses complex inflections ("companies" → "company")

    Enhanced mode uses spaCy's linguistic models to address these issues.

    Note on Hyphenated Words:
    -------------------------
    Despite PR #4's component-based analysis proposal, we follow Gunning (1952)
    blanket exclusion: ALL hyphenated words are excluded regardless of complexity.
    This maintains fidelity to the original specification.

    Reference:
        Gunning, R. (1952). The Technique of Clear Writing. McGraw-Hill.
        Page 39: "Do not count compound words"

    Requirements:
        pip install spacy
        python -m spacy download en_core_web_sm
    """

    def test_enhanced_mode_active_with_spacy(self):
        """Test that enhanced mode activates when spaCy is available.

        Why this test:
        --------------
        Users need transparency about which detection mode is active.
        The metadata fields allow verification of the analysis method used.

        Validates:
        - Mode is "enhanced" (not "basic")
        - Proper noun detection is "POS-based" (not "Capitalization-based")
        - Inflection handling is "Lemmatization-based" (not "Suffix-stripping")
        - spacy_model name is included in metadata

        Reference: PR #4 - NLP-enhanced Gunning Fog Index
        https://github.com/craigtrim/pystylometry/pull/4
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

        Why this test:
        --------------
        The basic mode's capitalization heuristic fails on:
        - Organizations: "NASA" (all-caps)
        - Brands: "iPhone" (mixed-case)
        - Names with apostrophes: "O'Brien"

        spaCy's PROPN (proper noun) POS tag correctly identifies these
        using linguistic analysis rather than simple capitalization rules.

        All proper nouns should be excluded per Gunning (1952, p. 39):
        "Do not count proper names"

        Test cases:
        - "California" - standard proper noun (4 syllables)
        - "NASA" - all-caps organization (2 syllables)

        Expected: Both excluded, only common complex words counted

        Reference: PR #4 Issue #1 - Proper Noun Detection
        https://github.com/craigtrim/pystylometry/pull/4
        """
        # Standard proper noun: "California" (4 syl) excluded
        # "provides" (2 syl), "education" (4 syl) counted
        result1 = compute_gunning_fog("California provides education.")
        assert result1.metadata["complex_word_count"] == 1  # only "education"

        # Organization acronym: "NASA" excluded
        # "amazing" (3 syl), "opportunities" (5 syl) counted
        result2 = compute_gunning_fog("NASA provides amazing opportunities.")
        assert result2.metadata["complex_word_count"] == 2  # "amazing", "opportunities"

    def test_enhanced_lemmatization_accuracy(self):
        """Test enhanced lemmatization-based inflection handling.

        Why this test:
        --------------
        The basic mode's suffix stripping (-es, -ed, -ing) is incomplete:
        - Misses other suffixes (-ly, -er, -est, -tion, -ness)
        - Can't handle irregular forms
        - Doesn't understand morphology

        spaCy's lemmatizer performs true morphological analysis:
        - Reduces words to their dictionary form (lemma)
        - Handles all inflections, not just common suffixes
        - Works with irregular forms

        Example: "The companies were running operations carefully."

        Basic mode analysis:
        - "companies" → strip nothing → 3 syl → complex
        - "running" → strip "-ing" → "runn" → 1 syl → NOT complex ✓
        - "operations" → strip nothing → 4 syl → complex
        - "carefully" → strip nothing → 3 syl → complex
        Result: 3 complex words

        Enhanced mode analysis:
        - "companies" → lemma "company" → 3 syl → complex
        - "running" → lemma "run" → 1 syl → NOT complex ✓
        - "operations" → lemma "operation" → 4 syl → complex
        - "carefully" → lemma "carefully" → 3 syl → complex
          (Note: spaCy doesn't strip -ly; it's a derivational morpheme)
        Result: 3 complex words

        Gunning (1952, p. 39): "Do not count -ed, -es, -ing endings"
        Enhanced mode achieves this via lemmatization for inflectional morphemes.
        Note: -ly is derivational (creates new words), not inflectional (grammatical).

        Reference: PR #4 Issue #2 - Inflection Handling
        https://github.com/craigtrim/pystylometry/pull/4
        """
        text = "The companies were running operations carefully."
        result = compute_gunning_fog(text)

        # With lemmatization, should correctly identify complex words:
        # - "companies" (lemma=company, 3 syl) → complex
        # - "operations" (lemma=operation, 4 syl) → complex
        # - "carefully" (lemma=carefully, 3 syl, ADV) → complex
        #   Note: spaCy doesn't strip -ly (derivational morpheme, not inflectional)
        #   Gunning (1952) specified "-ed, -es, -ing" but not "-ly"
        assert result.metadata["complex_word_count"] == 3

    def test_enhanced_handles_irregular_verbs(self):
        """Test that enhanced mode handles irregular verb forms correctly.

        Why this test:
        --------------
        English has many irregular verbs where suffix stripping fails:
        - "was" → has no suffix to strip, but lemma is "be" (1 syl)
        - "were" → has no suffix to strip, but lemma is "be" (1 syl)
        - "ran" → has no suffix to strip, but lemma is "run" (1 syl)
        - "went" → has no suffix to strip, but lemma is "go" (1 syl)

        Basic mode incorrectly treats these as potential complex words.
        Enhanced mode correctly reduces them to simple base forms.

        Example: "Understanding was necessary."

        Basic mode:
        - "Understanding" (4 syl) → strip nothing → complex
        - "was" (1 syl) → strip nothing → NOT complex (< 3 syl)
        - "necessary" (4 syl) → strip nothing → complex
        Result: 2 complex (happens to be correct)

        Enhanced mode:
        - "Understanding" (4 syl) → lemma "understand" (3 syl) → complex
        - "was" (1 syl) → lemma "be" (1 syl) → NOT complex
        - "necessary" (4 syl) → lemma "necessary" (4 syl) → complex
        Result: 2 complex (correct via proper analysis)

        The enhanced mode arrives at the right answer through correct
        morphological analysis rather than coincidence.

        Reference: PR #4 Issue #2 - Inflection Handling (Irregular Forms)
        https://github.com/craigtrim/pystylometry/pull/4
        """
        text = "Understanding was necessary."
        result = compute_gunning_fog(text)

        # "Understanding" (4 syl → lemma "understand" 3 syl) → complex
        # "necessary" (4 syl) → complex
        # "was" (→ lemma "be" 1 syl) → NOT complex
        assert result.metadata["complex_word_count"] == 2

    def test_enhanced_mode_metadata_completeness(self):
        """Test that enhanced mode provides complete metadata.

        Why this test:
        --------------
        Metadata transparency allows users to:
        1. Verify which analysis method was used
        2. Reproduce results with the same spaCy model
        3. Debug unexpected results
        4. Cite the analysis method in research

        Required metadata fields:
        - mode: "enhanced"
        - proper_noun_detection: "POS-based"
        - inflection_handling: "Lemmatization-based"
        - spacy_model: Model name (e.g., "en_core_web_sm")

        Reference: PR #4 - Metadata Transparency
        https://github.com/craigtrim/pystylometry/pull/4
        """
        text = "The researchers analyzed comprehensive datasets systematically."
        result = compute_gunning_fog(text)

        # Verify all enhanced mode metadata is present
        assert "mode" in result.metadata
        assert "proper_noun_detection" in result.metadata
        assert "inflection_handling" in result.metadata
        assert "spacy_model" in result.metadata

        # Verify correct values
        assert result.metadata["mode"] == "enhanced"
        assert result.metadata["proper_noun_detection"] == "POS-based"
        assert result.metadata["inflection_handling"] == "Lemmatization-based"
        assert isinstance(result.metadata["spacy_model"], str)
        assert len(result.metadata["spacy_model"]) > 0
