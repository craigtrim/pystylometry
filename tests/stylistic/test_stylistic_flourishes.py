"""Tests for stylistic flourishes and rhetorical device detection.

This module tests the stylistic flourishes analyzer functionality,
including alliteration detection, anaphora detection, epistrophe
detection, punctuation style analysis (em-dash, en-dash, ellipsis),
serial comma preference, quotation style, rhetorical questions, and
the composite flourish score.

Related GitHub Issues:
    #30 - Whonix stylometric features
    https://github.com/craigtrim/pystylometry/issues/30

Test coverage:
    - Return type validation (StylisticFlourishesResult dataclass)
    - Alliteration detection (consecutive consonant-initial words)
    - Anaphora detection (repeated sentence beginnings)
    - Epistrophe detection (repeated sentence endings)
    - Em-dash and en-dash counting
    - Ellipsis detection
    - Serial comma preference detection
    - Quotation style detection
    - Rhetorical question counting
    - Composite flourish score
    - Empty text edge case
    - Density normalization
"""

from pystylometry.stylistic.flourishes import compute_stylistic_flourishes


class TestFlourishesReturnType:
    """Test that compute_stylistic_flourishes returns the correct type."""

    def test_returns_flourishes_result(self) -> None:
        """Test that compute_stylistic_flourishes returns StylisticFlourishesResult."""
        from pystylometry._types import StylisticFlourishesResult

        text = "The quick brown fox jumps over the lazy dog."
        result = compute_stylistic_flourishes(text)
        assert isinstance(result, StylisticFlourishesResult)

    def test_has_all_required_fields(self) -> None:
        """Test that the result has all expected fields."""
        text = "A simple sentence."
        result = compute_stylistic_flourishes(text)

        assert hasattr(result, "alliteration_count")
        assert hasattr(result, "alliteration_density")
        assert hasattr(result, "anaphora_count")
        assert hasattr(result, "anaphora_density")
        assert hasattr(result, "epistrophe_count")
        assert hasattr(result, "epistrophe_density")
        assert hasattr(result, "em_dash_count")
        assert hasattr(result, "en_dash_count")
        assert hasattr(result, "ellipsis_count")
        assert hasattr(result, "serial_comma_preference")
        assert hasattr(result, "quotation_style")
        assert hasattr(result, "rhetorical_question_count")
        assert hasattr(result, "flourish_score")
        assert hasattr(result, "metadata")


class TestAlliterationDetection:
    """Test alliteration detection.

    Alliteration is defined as 3+ consecutive words starting with the
    same consonant letter. The detection is letter-based, not phonetic.
    """

    def test_detects_alliteration(self) -> None:
        """Test detection of basic alliterative sequences."""
        # "Peter Piper picked" = 3 consecutive 'p' words
        text = "Peter Piper picked a peck of pickled peppers."
        result = compute_stylistic_flourishes(text)
        assert result.alliteration_count >= 1

    def test_no_alliteration(self) -> None:
        """Test with text containing no alliteration."""
        text = "The quick brown fox jumped over a lazy dog."
        result = compute_stylistic_flourishes(text)
        assert result.alliteration_count == 0

    def test_vowel_initial_breaks_sequence(self) -> None:
        """Test that vowel-initial words break an alliterative sequence.

        Alliteration only tracks consonant-initial words. A vowel-initial
        word in the middle resets the sequence.
        """
        text = "Big bright and beautiful balloons."
        result = compute_stylistic_flourishes(text)
        # "big bright" is only 2 (under threshold), then "and" breaks it
        # "beautiful balloons" is only 2
        assert result.alliteration_count == 0

    def test_alliteration_examples_populated(self) -> None:
        """Test that alliteration examples are returned."""
        text = "She sells sea shells by the sea shore."
        result = compute_stylistic_flourishes(text)
        if result.alliteration_count > 0:
            assert len(result.alliteration_examples) > 0


class TestAnaphoraDetection:
    """Test anaphora detection (repeated sentence beginnings).

    Anaphora is a rhetorical device where consecutive sentences begin
    with the same word or phrase. The detector checks 1-4 word prefixes.
    """

    def test_detects_anaphora(self) -> None:
        """Test detection of anaphoric patterns.

        Churchill's famous speech uses "We shall fight" at the start
        of consecutive sentences — a classic anaphora. The detector
        uses greedy longest-prefix matching, so "we shall fight on"
        (4 words) matches sentences 1-2, while sentence 3 has a
        different 4th word ("in" vs "on") and is unmatched at that
        prefix length.
        """
        text = (
            "We shall fight on the beaches. We shall fight on the landing "
            "grounds. We shall fight in the fields."
        )
        result = compute_stylistic_flourishes(text)
        assert result.anaphora_count >= 2
        assert len(result.anaphora_patterns) >= 1

    def test_no_anaphora(self) -> None:
        """Test with text containing no anaphora."""
        text = (
            "The sun was shining brightly. Birds were singing in the trees. "
            "Children played in the park."
        )
        result = compute_stylistic_flourishes(text)
        assert result.anaphora_count == 0

    def test_anaphora_patterns_list(self) -> None:
        """Test that anaphora patterns include the repeated phrase."""
        text = (
            "Every day I wake up. Every day I go to work. "
            "Every day I come home."
        )
        result = compute_stylistic_flourishes(text)
        if result.anaphora_count > 0:
            assert len(result.anaphora_patterns) > 0
            # Each pattern is a (phrase, count) tuple
            phrase, count = result.anaphora_patterns[0]
            assert isinstance(phrase, str)
            assert isinstance(count, int)


class TestEpistropheDetection:
    """Test epistrophe detection (repeated sentence endings)."""

    def test_detects_epistrophe(self) -> None:
        """Test detection of epistrophe patterns."""
        text = (
            "I spoke as a child. I understood as a child. "
            "I thought as a child."
        )
        result = compute_stylistic_flourishes(text)
        assert result.epistrophe_count >= 3

    def test_no_epistrophe(self) -> None:
        """Test with text containing no epistrophe."""
        text = (
            "The morning was cold. She walked to the store. "
            "He waited at the corner."
        )
        result = compute_stylistic_flourishes(text)
        assert result.epistrophe_count == 0


class TestPunctuationAnalysis:
    """Test em-dash, en-dash, and ellipsis detection."""

    def test_em_dash_unicode(self) -> None:
        """Test detection of Unicode em-dash (U+2014)."""
        text = "The result\u2014though surprising\u2014was conclusive."
        result = compute_stylistic_flourishes(text)
        assert result.em_dash_count == 2

    def test_em_dash_double_hyphen(self) -> None:
        """Test detection of double-hyphen as em-dash."""
        text = "The result--though surprising--was conclusive."
        result = compute_stylistic_flourishes(text)
        assert result.em_dash_count == 2

    def test_en_dash(self) -> None:
        """Test detection of Unicode en-dash (U+2013)."""
        text = "Pages 10\u201320 cover the introduction."
        result = compute_stylistic_flourishes(text)
        assert result.en_dash_count == 1

    def test_ellipsis_three_dots(self) -> None:
        """Test detection of three-dot ellipsis."""
        text = "Well... I suppose... that could work..."
        result = compute_stylistic_flourishes(text)
        assert result.ellipsis_count == 3

    def test_ellipsis_unicode(self) -> None:
        """Test detection of Unicode ellipsis character (U+2026)."""
        text = "Well\u2026 I suppose\u2026"
        result = compute_stylistic_flourishes(text)
        assert result.ellipsis_count == 2

    def test_no_special_punctuation(self) -> None:
        """Test with text containing only standard punctuation."""
        text = "This is a simple sentence. And another one."
        result = compute_stylistic_flourishes(text)
        assert result.em_dash_count == 0
        assert result.en_dash_count == 0
        assert result.ellipsis_count == 0


class TestSerialComma:
    """Test serial comma (Oxford comma) detection.

    The serial comma is the comma before the final conjunction in a list
    (e.g., "red, white, and blue"). Its usage is one of the most
    consistent stylistic habits across authors.
    """

    def test_detects_serial_comma(self) -> None:
        """Test detection of serial comma usage."""
        text = "I bought apples, oranges, and bananas."
        result = compute_stylistic_flourishes(text)
        assert result.serial_comma_count >= 1

    def test_detects_no_serial_comma(self) -> None:
        """Test detection of missing serial comma."""
        text = "I bought apples, oranges and bananas."
        result = compute_stylistic_flourishes(text)
        assert result.no_serial_comma_count >= 1

    def test_oxford_preference(self) -> None:
        """Test that consistent serial comma usage is classified as 'oxford'."""
        text = (
            "I like apples, oranges, and bananas. "
            "She bought red, blue, and green shirts. "
            "He visited Paris, London, and Rome."
        )
        result = compute_stylistic_flourishes(text)
        assert result.serial_comma_preference == "oxford"

    def test_no_oxford_preference(self) -> None:
        """Test that consistent missing serial comma is classified as 'no_oxford'."""
        text = (
            "I like apples, oranges and bananas. "
            "She bought red, blue and green shirts. "
            "He visited Paris, London and Rome."
        )
        result = compute_stylistic_flourishes(text)
        assert result.serial_comma_preference == "no_oxford"

    def test_insufficient_data(self) -> None:
        """Test classification when no list patterns are found."""
        text = "The sky is blue. The grass is green."
        result = compute_stylistic_flourishes(text)
        assert result.serial_comma_preference == "insufficient_data"


class TestQuotationStyle:
    """Test quotation mark style detection."""

    def test_double_quotes(self) -> None:
        """Test detection of double quotation mark preference."""
        text = 'She said "hello" and "goodbye" to them.'
        result = compute_stylistic_flourishes(text)
        assert result.double_quote_count >= 4
        assert result.quotation_style == "double"

    def test_no_quotes(self) -> None:
        """Test with text containing no quotation marks."""
        text = "The sky is blue and the grass is green."
        result = compute_stylistic_flourishes(text)
        assert result.quotation_style == "none"


class TestRhetoricalQuestions:
    """Test rhetorical question detection."""

    def test_detects_questions(self) -> None:
        """Test detection of question-ending sentences."""
        text = (
            "Is this really the best we can do? Can we not try harder? "
            "The answer is clear."
        )
        result = compute_stylistic_flourishes(text)
        assert result.rhetorical_question_count == 2

    def test_no_questions(self) -> None:
        """Test with text containing no questions."""
        text = "The answer is clear. We must proceed. Time is running out."
        result = compute_stylistic_flourishes(text)
        assert result.rhetorical_question_count == 0


class TestFlourishScore:
    """Test composite flourish score computation."""

    def test_literary_text_scores_higher(self) -> None:
        """Test that text with rhetorical devices scores higher than plain text."""
        literary = (
            "We shall fight on the beaches. We shall fight on the landing "
            "grounds. We shall fight in the fields\u2014and we shall never "
            "surrender. Is this not our finest hour? The battle... the "
            "glory... the triumph..."
        )
        plain = (
            "The meeting was held on Tuesday. Attendance was recorded. "
            "Minutes were distributed. The next meeting is Thursday."
        )
        literary_result = compute_stylistic_flourishes(literary)
        plain_result = compute_stylistic_flourishes(plain)
        assert literary_result.flourish_score > plain_result.flourish_score

    def test_flourish_score_bounded(self) -> None:
        """Test that flourish score is between 0.0 and 1.0."""
        texts = [
            "Hello.",
            "We fight! We fight! We fight! Is this... the end--really?",
            "",
        ]
        for text in texts:
            result = compute_stylistic_flourishes(text)
            assert 0.0 <= result.flourish_score <= 1.0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string(self) -> None:
        """Test that empty string returns zero-valued result."""
        result = compute_stylistic_flourishes("")
        assert result.alliteration_count == 0
        assert result.anaphora_count == 0
        assert result.em_dash_count == 0
        assert result.flourish_score == 0.0
        assert result.metadata["word_count"] == 0
        assert result.metadata["sentence_count"] == 0

    def test_whitespace_only(self) -> None:
        """Test that whitespace-only text returns zero-valued result."""
        result = compute_stylistic_flourishes("   \n\t  ")
        assert result.alliteration_count == 0
        assert result.metadata["word_count"] == 0

    def test_single_sentence(self) -> None:
        """Test with a single sentence (no anaphora/epistrophe possible)."""
        result = compute_stylistic_flourishes("Just one sentence here.")
        assert result.anaphora_count == 0
        assert result.epistrophe_count == 0

    def test_metadata_has_counts(self) -> None:
        """Test that metadata includes word and sentence counts."""
        text = "First sentence. Second sentence. Third one."
        result = compute_stylistic_flourishes(text)
        assert "word_count" in result.metadata
        assert "sentence_count" in result.metadata
        assert result.metadata["word_count"] > 0
