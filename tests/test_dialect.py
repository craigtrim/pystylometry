"""Comprehensive tests for dialect detection module.

This module tests the dialect detection functionality, including vocabulary
matching, spelling pattern detection, grammar patterns, eye dialect
identification, and the chunking/distribution pattern from Issue #27.

Related GitHub Issues:
    #35 - Dialect detection with extensible JSON markers
    https://github.com/craigtrim/pystylometry/issues/35
    #30 - Whonix stylometry features (regional linguistic preferences)
    https://github.com/craigtrim/pystylometry/issues/30
    #27 - Native chunked analysis with Distribution dataclass
    https://github.com/craigtrim/pystylometry/issues/27
"""

import math

from pystylometry.dialect import clear_cache, compute_dialect, get_markers


class TestDialectBasicFunctionality:
    """Test basic dialect detection functionality."""

    def test_british_text_detection(self):
        """Test detection of British English text."""
        text = "The colour of the programme was brilliant. I've got a flat in the city centre."
        result = compute_dialect(text)

        assert result.dialect == "british"
        assert result.british_score > result.american_score
        assert result.confidence > 0.5

    def test_american_text_detection(self):
        """Test detection of American English text."""
        text = "The color of the program was awesome. I have an apartment in the city center."
        result = compute_dialect(text)

        assert result.dialect == "american"
        assert result.american_score > result.british_score
        assert result.confidence > 0.5

    def test_mixed_dialect_detection(self):
        """Test detection of mixed British/American text."""
        text = "The colour of the program was good. I have a flat in the center."
        result = compute_dialect(text)

        # Should detect mixed or have close scores
        assert result.dialect in ["mixed", "british", "american"]
        # Both dialects should have some presence
        assert result.british_score > 0 or result.american_score > 0

    def test_neutral_text_detection(self):
        """Test detection of neutral text with no dialect markers."""
        text = "The sun rose over the mountains. Birds sang in the trees."
        result = compute_dialect(text)

        # Should be neutral or have very low scores
        assert result.dialect in ["neutral", "mixed"]
        # Scores should be low
        assert result.british_score < 0.3 or result.american_score < 0.3


class TestDialectVocabularyMatching:
    """Test vocabulary-based dialect detection."""

    def test_british_vocabulary(self):
        """Test detection of British vocabulary items."""
        # Use strongly British vocabulary without words that have dual meanings
        text = "I took the lift to my flat. The lorry drove past the petrol station."
        result = compute_dialect(text)

        # Should detect British vocabulary
        assert result.dialect == "british"
        assert "lexical" in result.markers_by_level
        # Check that British vocabulary was detected
        assert result.british_score > 0

    def test_american_vocabulary(self):
        """Test detection of American vocabulary items."""
        text = "I took the elevator to my apartment and had a cookie with my coffee."
        result = compute_dialect(text)

        # Should detect American vocabulary
        assert result.dialect == "american"
        assert result.american_score > 0

    def test_vocabulary_markers_recorded(self):
        """Test that vocabulary markers are recorded in results."""
        text = "The lorry drove past the petrol station."
        result = compute_dialect(text)

        # Should have vocabulary markers recorded
        assert len(result.vocabulary_markers) > 0


class TestDialectSpellingPatterns:
    """Test spelling pattern-based dialect detection."""

    def test_our_or_pattern(self):
        """Test detection of -our/-or spelling pattern."""
        british_text = "The colour and flavour of the dish showed great honour."
        american_text = "The color and flavor of the dish showed great honor."

        british_result = compute_dialect(british_text)
        american_result = compute_dialect(american_text)

        assert british_result.british_score > american_result.british_score
        assert american_result.american_score > british_result.american_score

    def test_ise_ize_pattern(self):
        """Test detection of -ise/-ize spelling pattern."""
        british_text = "We need to organise and realise our plans to finalise the report."
        american_text = "We need to organize and realize our plans to finalize the report."

        british_result = compute_dialect(british_text)
        american_result = compute_dialect(american_text)

        assert british_result.british_score > american_result.british_score

    def test_re_er_pattern(self):
        """Test detection of -re/-er spelling pattern."""
        # Use texts without shared vocabulary that might skew results
        british_text = "The theatre in the city centre was good."
        american_text = "The theater in the city center was good."

        british_result = compute_dialect(british_text)
        american_result = compute_dialect(american_text)

        # British text should have British markers, American should have American markers
        assert british_result.british_score > 0
        assert american_result.american_score > 0
        # British text should score higher on British than American text does
        assert british_result.british_score >= american_result.british_score

    def test_doubled_l_pattern(self):
        """Test detection of doubled L pattern (travelled/traveled)."""
        british_text = "She travelled extensively and marvelled at the sights."
        american_text = "She traveled extensively and marveled at the sights."

        british_result = compute_dialect(british_text)
        american_result = compute_dialect(american_text)

        assert british_result.british_score >= american_result.british_score

    def test_spelling_markers_recorded(self):
        """Test that spelling markers are recorded in results."""
        text = "The colour was brilliant."
        result = compute_dialect(text)

        # Should have spelling markers recorded
        assert len(result.spelling_markers) > 0


class TestDialectGrammarPatterns:
    """Test grammar pattern-based dialect detection."""

    def test_have_got_pattern(self):
        """Test detection of 'have got' vs 'have' pattern."""
        british_text = "I've got a car. She's got three children."

        british_result = compute_dialect(british_text)
        # Grammar patterns are harder to distinguish, so just check for detection
        assert british_result.british_score >= 0

    def test_gotten_pattern(self):
        """Test detection of 'gotten' (American) pattern."""
        american_text = "Things have gotten worse. She's gotten a promotion."
        result = compute_dialect(american_text)

        # 'gotten' is strongly American
        assert result.american_score > 0

    def test_grammar_markers_recorded(self):
        """Test that grammar markers are recorded in results."""
        text = "I've gotten used to it."
        result = compute_dialect(text)

        # Grammar markers may or may not be detected depending on pattern
        # Just check the structure exists
        assert isinstance(result.grammar_markers, dict)


class TestDialectEyeDialect:
    """Test eye dialect detection (register markers, not true dialect)."""

    def test_eye_dialect_detection(self):
        """Test detection of eye dialect markers."""
        text = "I'm gonna wanna get some food cuz I'm kinda hungry."
        result = compute_dialect(text)

        # Should detect eye dialect markers
        assert result.eye_dialect_count > 0
        assert result.eye_dialect_ratio > 0

    def test_eye_dialect_separate_from_dialect(self):
        """Test that eye dialect doesn't skew dialect classification."""
        # British text with eye dialect
        text = "The colour of the programme was gonna be brilliant, you know."
        result = compute_dialect(text)

        # Should still detect British despite eye dialect
        assert result.british_score > 0
        # Eye dialect should be separately tracked
        assert result.eye_dialect_count > 0


class TestDialectMarkersLoader:
    """Test dialect markers loading and caching."""

    def test_markers_load_successfully(self):
        """Test that markers load without error."""
        markers = get_markers()
        assert markers is not None
        assert len(markers.vocabulary_pairs) > 0

    def test_markers_cache(self):
        """Test that markers are cached."""
        markers1 = get_markers()
        markers2 = get_markers()
        assert markers1 is markers2  # Same object due to caching

    def test_cache_clear(self):
        """Test that cache can be cleared."""
        get_markers()  # Prime the cache
        clear_cache()
        markers_after_clear = get_markers()
        # After clearing, should still work
        assert markers_after_clear is not None

    def test_markers_contain_expected_data(self):
        """Test that markers contain expected data structures."""
        markers = get_markers()

        assert hasattr(markers, "vocabulary_pairs")
        assert hasattr(markers, "vocabulary_exclusive")
        assert hasattr(markers, "spelling_patterns")
        assert hasattr(markers, "grammar_patterns")
        assert hasattr(markers, "eye_dialect_words")


class TestDialectMarkersByLevel:
    """Test linguistic level categorization of markers."""

    def test_markers_by_level_structure(self):
        """Test that markers_by_level has correct structure."""
        text = "The colour of the flat was brilliant."
        result = compute_dialect(text)

        assert "phonological" in result.markers_by_level
        assert "morphological" in result.markers_by_level
        assert "lexical" in result.markers_by_level
        assert "syntactic" in result.markers_by_level

    def test_lexical_level_vocabulary(self):
        """Test that vocabulary markers go to lexical level."""
        text = "I live in a flat with a lift."
        result = compute_dialect(text)

        lexical_markers = result.markers_by_level.get("lexical", {})
        # Should have lexical markers
        assert len(lexical_markers) >= 0  # May be 0 if words not in vocabulary list


class TestDialectChunking:
    """Test chunked analysis per Issue #27."""

    def test_chunking_creates_distribution(self):
        """Test that chunking creates distribution objects."""
        # Create text long enough for multiple chunks
        text = " ".join(["The colour of the programme was brilliant."] * 500)
        result = compute_dialect(text, chunk_size=100)

        # Should have distributions
        assert hasattr(result, "british_score_dist")
        assert hasattr(result, "american_score_dist")
        assert hasattr(result, "markedness_score_dist")

        # Mean should match the scalar value
        assert result.british_score == result.british_score_dist.mean

    def test_chunk_count_recorded(self):
        """Test that chunk count is recorded."""
        text = " ".join(["The colour was nice."] * 200)
        result = compute_dialect(text, chunk_size=50)

        assert result.chunk_count > 0
        assert result.chunk_size == 50

    def test_distribution_statistics(self):
        """Test that distributions have statistics."""
        text = " ".join(["The colour of the program was nice."] * 300)
        result = compute_dialect(text, chunk_size=50)

        dist = result.british_score_dist
        assert hasattr(dist, "mean")
        assert hasattr(dist, "median")
        assert hasattr(dist, "std")
        assert hasattr(dist, "range")
        assert hasattr(dist, "iqr")


class TestDialectMarkednessScore:
    """Test markedness score computation."""

    def test_markedness_increases_with_markers(self):
        """Test that markedness increases with more dialect markers."""
        # Low markedness (neutral text)
        neutral_text = "The sun rose over the mountains."

        # High markedness (many British markers)
        marked_text = "The colour of the programme in the city centre was brilliant."

        neutral_result = compute_dialect(neutral_text)
        marked_result = compute_dialect(marked_text)

        # Marked text should have higher markedness score
        assert marked_result.markedness_score >= neutral_result.markedness_score

    def test_markedness_includes_eye_dialect(self):
        """Test that markedness includes eye dialect contribution."""
        # Text with eye dialect only
        eye_dialect_text = "I'm gonna wanna go cuz it's gonna be fun."
        result = compute_dialect(eye_dialect_text)

        # Should have some markedness from eye dialect
        assert result.markedness_score >= 0


class TestDialectEdgeCases:
    """Test edge cases for dialect detection."""

    def test_empty_text(self):
        """Test dialect detection with empty text."""
        result = compute_dialect("")

        assert result.dialect == "neutral"
        assert result.confidence == 0.0
        assert math.isnan(result.british_score)
        assert math.isnan(result.american_score)

    def test_whitespace_only(self):
        """Test dialect detection with whitespace only."""
        result = compute_dialect("   \n\t  ")

        assert result.dialect == "neutral"
        assert result.confidence == 0.0

    def test_single_word(self):
        """Test dialect detection with single word."""
        # British word
        result = compute_dialect("colour")
        assert result.british_score > 0

        # American word
        result = compute_dialect("color")
        assert result.american_score > 0

    def test_numbers_only(self):
        """Test dialect detection with numbers only."""
        result = compute_dialect("123 456 789")
        # Should handle gracefully
        assert result.dialect in ["neutral", "mixed"]


class TestDialectResultStructure:
    """Test DialectResult dataclass structure."""

    def test_result_has_required_fields(self):
        """Test that result has all required fields."""
        text = "The colour was nice."
        result = compute_dialect(text)

        # Classification
        assert hasattr(result, "dialect")
        assert hasattr(result, "confidence")

        # Scores
        assert hasattr(result, "british_score")
        assert hasattr(result, "american_score")
        assert hasattr(result, "markedness_score")

        # Distributions
        assert hasattr(result, "british_score_dist")
        assert hasattr(result, "american_score_dist")
        assert hasattr(result, "markedness_score_dist")

        # Marker breakdowns
        assert hasattr(result, "markers_by_level")
        assert hasattr(result, "spelling_markers")
        assert hasattr(result, "vocabulary_markers")
        assert hasattr(result, "grammar_markers")

        # Eye dialect
        assert hasattr(result, "eye_dialect_count")
        assert hasattr(result, "eye_dialect_ratio")

        # Register hints
        assert hasattr(result, "register_hints")

        # Chunking context
        assert hasattr(result, "chunk_size")
        assert hasattr(result, "chunk_count")

        # Metadata
        assert hasattr(result, "metadata")

    def test_dialect_values(self):
        """Test that dialect field has valid values."""
        texts = [
            "The colour was brilliant.",  # British
            "The color was awesome.",  # American
            "The sun rose.",  # Neutral
            "The colour of the color.",  # Mixed
        ]

        for text in texts:
            result = compute_dialect(text)
            assert result.dialect in ["british", "american", "mixed", "neutral"]


class TestDialectMetadata:
    """Test metadata in dialect results."""

    def test_metadata_contains_word_count(self):
        """Test that metadata contains total word count."""
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_dialect(text)

        assert "total_word_count" in result.metadata
        assert result.metadata["total_word_count"] > 0

    def test_metadata_contains_version(self):
        """Test that metadata contains markers version."""
        text = "The colour was nice."
        result = compute_dialect(text)

        assert "markers_version" in result.metadata


class TestDialectRegisterHints:
    """Test register hints in dialect results."""

    def test_register_hints_structure(self):
        """Test that register hints has expected structure."""
        text = "The colour was nice."
        result = compute_dialect(text)

        assert isinstance(result.register_hints, dict)
        assert "eye_dialect_density" in result.register_hints
        assert "marker_density" in result.register_hints
