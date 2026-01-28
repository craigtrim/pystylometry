"""Tests for abbreviation pattern analysis.

This module tests the abbreviation analyzer functionality, including
contraction detection, acronym classification, Latin abbreviation
counting, informal shortenings, text-speak patterns, title abbreviations,
and the composite informality score.

Related GitHub Issues:
    #30 - Whonix stylometric features
    https://github.com/craigtrim/pystylometry/issues/30

Test coverage:
    - Return type validation (AbbreviationResult dataclass)
    - Contraction detection and ratio calculation
    - Expanded form detection and contraction ratio
    - Acronym detection and style classification
    - Latin abbreviation detection
    - Informal shortening detection
    - Text-speak detection
    - Title abbreviation detection
    - Composite informality score computation
    - Empty text edge case
    - Density normalization (per 100 words)
"""

from pystylometry.expression.abbreviations import compute_abbreviations


class TestAbbreviationReturnType:
    """Test that compute_abbreviations returns the correct type."""

    def test_returns_abbreviation_result(self) -> None:
        """Test that compute_abbreviations returns AbbreviationResult."""
        from pystylometry._types import AbbreviationResult

        text = "I can't believe this is happening."
        result = compute_abbreviations(text)
        assert isinstance(result, AbbreviationResult)

    def test_has_all_required_fields(self) -> None:
        """Test that the result has all expected fields."""
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_abbreviations(text)

        assert hasattr(result, "contraction_ratio")
        assert hasattr(result, "contraction_count")
        assert hasattr(result, "expanded_form_count")
        assert hasattr(result, "acronym_count")
        assert hasattr(result, "acronym_style")
        assert hasattr(result, "latin_abbreviation_count")
        assert hasattr(result, "informal_shortening_count")
        assert hasattr(result, "text_speak_count")
        assert hasattr(result, "title_abbreviation_count")
        assert hasattr(result, "informality_score")
        assert hasattr(result, "metadata")


class TestContractionDetection:
    """Test contraction detection and ratio calculation."""

    def test_detects_negative_contractions(self) -> None:
        """Test that common negative contractions are detected."""
        text = "I can't believe she didn't call. He won't come."
        result = compute_abbreviations(text)
        # "can't", "didn't", "won't" = 3 contractions
        assert result.contraction_count == 3

    def test_detects_pronoun_contractions(self) -> None:
        """Test that pronoun contractions are detected."""
        text = "I'm going to say that it's fine and we're ready."
        result = compute_abbreviations(text)
        # "I'm", "it's", "we're" = 3
        assert result.contraction_count == 3

    def test_contraction_ratio_all_contracted(self) -> None:
        """Test contraction ratio when all forms are contracted.

        When text uses only contracted forms with no expanded equivalents,
        the contraction ratio should be 1.0 (always contracts).
        """
        text = "I can't do it and I don't want to try."
        result = compute_abbreviations(text)
        # All contractions, no expanded forms
        assert result.contraction_ratio == 1.0

    def test_contraction_ratio_mixed(self) -> None:
        """Test contraction ratio with both contracted and expanded forms.

        The ratio should reflect the proportion of opportunities where the
        contracted form was used. Note that expanded form patterns can
        overlap — "I will not" matches both "will not" (→ won't) and
        "I will" (→ I'll), so the expanded count may be higher than
        a naive manual count suggests.
        """
        text = "I can't believe it, but I do not care. I will not go."
        result = compute_abbreviations(text)
        # "can't" = 1 contraction
        # "do not" (→don't), "will not" (→won't), "I will" (→I'll) = 3 expanded
        # ratio = 1 / (1 + 3) = 0.25
        assert result.contraction_count == 1
        assert result.expanded_form_count == 3
        assert abs(result.contraction_ratio - 0.25) < 0.01

    def test_no_contractions(self) -> None:
        """Test with text containing no contractions."""
        text = "The cat sat on the mat. The dog ran in the park."
        result = compute_abbreviations(text)
        assert result.contraction_count == 0
        assert result.contraction_ratio == 0.0


class TestAcronymDetection:
    """Test acronym detection and style classification."""

    def test_detects_no_period_acronyms(self) -> None:
        """Test detection of no-period style acronyms (e.g., NASA, FBI)."""
        text = "NASA launched the rocket. The FBI investigated the case."
        result = compute_abbreviations(text)
        assert result.acronym_count >= 2
        assert result.acronym_style == "no_periods"

    def test_detects_period_style_acronyms(self) -> None:
        """Test detection of period-style acronyms (e.g., U.S.A.)."""
        text = "The U.S.A. delegation met with the N.A.T.O. committee."
        result = compute_abbreviations(text)
        assert result.acronym_count >= 2
        assert result.acronym_style == "with_periods"

    def test_no_acronyms(self) -> None:
        """Test with text containing no acronyms."""
        text = "The small cat sat on a warm mat in the sun."
        result = compute_abbreviations(text)
        assert result.acronym_count == 0
        assert result.acronym_style == "none"

    def test_excludes_common_words(self) -> None:
        """Test that common short caps words (I, A, OK) are excluded."""
        text = "I am OK with it. A good plan."
        result = compute_abbreviations(text)
        # "I", "A", "OK" should all be excluded from acronym count
        assert result.acronym_count == 0


class TestLatinAbbreviations:
    """Test Latin abbreviation detection."""

    def test_detects_common_latin_abbreviations(self) -> None:
        """Test detection of etc., e.g., i.e., and other Latin abbrevs."""
        text = "There are many fruits, e.g., apples, oranges, etc. Also, i.e., the best ones."
        result = compute_abbreviations(text)
        # Should detect "e.g.", "etc.", "i.e."
        assert result.latin_abbreviation_count >= 3
        assert "e.g." in result.latin_abbreviations
        assert "etc." in result.latin_abbreviations
        assert "i.e." in result.latin_abbreviations

    def test_detects_vs(self) -> None:
        """Test detection of vs. abbreviation."""
        text = "In the case of apples vs. oranges we prefer apples."
        result = compute_abbreviations(text)
        assert "vs." in result.latin_abbreviations

    def test_no_latin_abbreviations(self) -> None:
        """Test with text containing no Latin abbreviations."""
        text = "The sky is blue and the grass is green."
        result = compute_abbreviations(text)
        assert result.latin_abbreviation_count == 0


class TestInformalShortenings:
    """Test informal shortening detection."""

    def test_detects_common_shortenings(self) -> None:
        """Test detection of informal word shortenings like 'info', 'intro'."""
        text = "Check the info in the intro section. Take a photo at the gym."
        result = compute_abbreviations(text)
        # "info", "intro", "photo", "gym"
        assert result.informal_shortening_count >= 4

    def test_no_shortenings(self) -> None:
        """Test with text containing no informal shortenings."""
        text = "The comprehensive information revealed remarkable insights."
        result = compute_abbreviations(text)
        assert result.informal_shortening_count == 0


class TestTextSpeak:
    """Test text-speak pattern detection."""

    def test_detects_text_speak(self) -> None:
        """Test detection of text-speak tokens."""
        text = "thx for the info btw. pls check it out imo."
        result = compute_abbreviations(text)
        # "thx", "btw", "pls", "imo" (and possibly "info" as shortening)
        assert result.text_speak_count >= 4

    def test_no_text_speak(self) -> None:
        """Test with text containing no text-speak."""
        text = "Thank you for the information. Please check it."
        result = compute_abbreviations(text)
        assert result.text_speak_count == 0


class TestTitleAbbreviations:
    """Test title abbreviation detection."""

    def test_detects_title_abbreviations(self) -> None:
        """Test detection of Mr., Dr., Prof., etc."""
        text = "Mr. Smith and Dr. Jones met with Prof. Williams."
        result = compute_abbreviations(text)
        assert result.title_abbreviation_count == 3

    def test_no_title_abbreviations(self) -> None:
        """Test with text containing no title abbreviations."""
        text = "The teacher and the doctor discussed the results."
        result = compute_abbreviations(text)
        assert result.title_abbreviation_count == 0


class TestInformalityScore:
    """Test composite informality score computation."""

    def test_informal_text_scores_high(self) -> None:
        """Test that informal text with contractions and text-speak scores high.

        Text with heavy contraction usage and text-speak should produce
        an informality score above 0.3.
        """
        text = "I can't believe u didn't tell me thx btw. I'm so done lol."
        result = compute_abbreviations(text)
        assert result.informality_score > 0.3

    def test_formal_text_scores_low(self) -> None:
        """Test that formal text without contractions scores low.

        Text with no contractions, no text-speak, and Latin abbreviations
        should produce a low informality score.
        """
        text = (
            "The committee determined that the proposal, i.e., the revised "
            "draft, was not acceptable. The analysis revealed, e.g., significant "
            "discrepancies in the methodology. Furthermore, the data demonstrated "
            "substantial variations across all conditions. The committee resolved "
            "to revisit the proposal at a subsequent meeting."
        )
        result = compute_abbreviations(text)
        assert result.informality_score < 0.2

    def test_informality_score_bounded(self) -> None:
        """Test that informality score is always between 0.0 and 1.0."""
        texts = [
            "Hello world.",
            "I can't don't won't shouldn't wouldn't",
            "u r thx pls btw imo tbh idk nvm",
            "The committee, i.e., the board, determined etc. e.g.",
        ]
        for text in texts:
            result = compute_abbreviations(text)
            assert 0.0 <= result.informality_score <= 1.0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string(self) -> None:
        """Test that empty string returns zero-valued result."""
        result = compute_abbreviations("")
        assert result.contraction_count == 0
        assert result.contraction_ratio == 0.0
        assert result.informality_score == 0.0
        assert result.metadata["word_count"] == 0

    def test_whitespace_only(self) -> None:
        """Test that whitespace-only text returns zero-valued result."""
        result = compute_abbreviations("   \n\t  ")
        assert result.contraction_count == 0
        assert result.metadata["word_count"] == 0

    def test_single_word(self) -> None:
        """Test with a single word."""
        result = compute_abbreviations("hello")
        assert result.contraction_count == 0
        assert result.metadata["word_count"] == 1

    def test_curly_apostrophes(self) -> None:
        """Test that curly apostrophes are normalized for contraction matching.

        Many text editors and word processors replace straight apostrophes
        with curly (smart) quotes. The analyzer should handle both.
        """
        text = "I can\u2019t believe it\u2019s true."
        result = compute_abbreviations(text)
        # Should detect "can't" and "it's" despite curly apostrophes
        assert result.contraction_count == 2


class TestDensityNormalization:
    """Test that densities are correctly normalized per 100 words."""

    def test_latin_abbreviation_density(self) -> None:
        """Test that Latin abbreviation density is per 100 words.

        Latin abbreviations are detected via regex on the raw text,
        so they must appear in natural context (not as bare tokens).
        """
        filler = " ".join(["word"] * 96)
        text = f"We checked the data, etc. We also reviewed, e.g., the results. {filler}"
        result = compute_abbreviations(text)
        assert result.latin_abbreviation_count == 2
        assert result.latin_abbreviation_density > 0.0

    def test_metadata_contains_word_count(self) -> None:
        """Test that metadata includes the word count."""
        text = "one two three four five"
        result = compute_abbreviations(text)
        assert "word_count" in result.metadata
        assert result.metadata["word_count"] == 5
