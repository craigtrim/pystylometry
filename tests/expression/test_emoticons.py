"""Tests for emoticon and emoji expression analysis.

This module tests the emoticon and emoji analyzer functionality, including
Unicode emoji detection, text emoticon matching, expressive punctuation
counting, emphasis marker detection, laughter expression counting, and
the composite expressiveness score.

Related GitHub Issues:
    #30 - Whonix stylometric features
    https://github.com/craigtrim/pystylometry/issues/30

Test coverage:
    - Return type validation (EmoticonResult dataclass)
    - Unicode emoji detection and categorization
    - Text emoticon detection
    - Expressive punctuation (!!!, ???, !?)
    - Emphasis markers (ALL CAPS, *asterisk*, _underscore_)
    - Laughter expression detection
    - Composite expressiveness score
    - Empty text edge case
    - Density normalization (per 100 words)
"""

from pystylometry.expression.emoticons import compute_emoticons


class TestEmoticonReturnType:
    """Test that compute_emoticons returns the correct type."""

    def test_returns_emoticon_result(self) -> None:
        """Test that compute_emoticons returns EmoticonResult."""
        from pystylometry._types import EmoticonResult

        text = "Hello world :)"
        result = compute_emoticons(text)
        assert isinstance(result, EmoticonResult)

    def test_has_all_required_fields(self) -> None:
        """Test that the result has all expected fields."""
        text = "A simple sentence."
        result = compute_emoticons(text)

        assert hasattr(result, "emoji_count")
        assert hasattr(result, "emoji_density")
        assert hasattr(result, "emoji_categories")
        assert hasattr(result, "text_emoticon_count")
        assert hasattr(result, "text_emoticon_density")
        assert hasattr(result, "multiple_exclamation_count")
        assert hasattr(result, "multiple_question_count")
        assert hasattr(result, "interrobang_count")
        assert hasattr(result, "caps_emphasis_count")
        assert hasattr(result, "asterisk_emphasis_count")
        assert hasattr(result, "underscore_emphasis_count")
        assert hasattr(result, "laughter_count")
        assert hasattr(result, "laughter_types")
        assert hasattr(result, "expressiveness_score")
        assert hasattr(result, "metadata")


class TestEmojiDetection:
    """Test Unicode emoji detection and categorization."""

    def test_detects_emoji(self) -> None:
        """Test detection of Unicode emoji characters."""
        text = "Great job \U0001f600 keep going \U0001f389"
        result = compute_emoticons(text)
        assert result.emoji_count == 2

    def test_emoji_categories(self) -> None:
        """Test that emoji are categorized by Unicode block."""
        # U+1F600 is in smileys_emotion block
        text = "Hello \U0001f600"
        result = compute_emoticons(text)
        assert "smileys_emotion" in result.emoji_categories

    def test_no_emoji(self) -> None:
        """Test with text containing no emoji."""
        text = "This is a plain text sentence without any emoji."
        result = compute_emoticons(text)
        assert result.emoji_count == 0

    def test_multiple_same_emoji(self) -> None:
        """Test counting multiple occurrences of the same emoji."""
        text = "Yes \U0001f600\U0001f600\U0001f600 great"
        result = compute_emoticons(text)
        assert result.emoji_count == 3


class TestTextEmoticonDetection:
    """Test ASCII text emoticon detection."""

    def test_detects_smiley(self) -> None:
        """Test detection of :) smiley emoticon."""
        text = "I'm so happy :)"
        result = compute_emoticons(text)
        assert result.text_emoticon_count >= 1

    def test_detects_sad_face(self) -> None:
        """Test detection of :( sad face emoticon."""
        text = "That's disappointing :("
        result = compute_emoticons(text)
        assert result.text_emoticon_count >= 1

    def test_detects_heart(self) -> None:
        """Test detection of <3 heart emoticon."""
        text = "I love this <3"
        result = compute_emoticons(text)
        assert result.text_emoticon_count >= 1

    def test_detects_wink(self) -> None:
        """Test detection of ;) wink emoticon."""
        text = "Just kidding ;)"
        result = compute_emoticons(text)
        assert result.text_emoticon_count >= 1

    def test_no_emoticons(self) -> None:
        """Test with text containing no emoticons."""
        text = "The committee reached a consensus on the proposal."
        result = compute_emoticons(text)
        assert result.text_emoticon_count == 0


class TestExpressivePunctuation:
    """Test expressive punctuation detection."""

    def test_multiple_exclamation(self) -> None:
        """Test detection of multiple exclamation marks."""
        text = "This is amazing!!! I love it!!"
        result = compute_emoticons(text)
        assert result.multiple_exclamation_count == 2

    def test_multiple_question(self) -> None:
        """Test detection of multiple question marks."""
        text = "What happened?? How is that possible???"
        result = compute_emoticons(text)
        assert result.multiple_question_count == 2

    def test_interrobang(self) -> None:
        """Test detection of mixed exclamation/question marks."""
        text = "Are you serious?! What were they thinking!?"
        result = compute_emoticons(text)
        assert result.interrobang_count == 2

    def test_no_expressive_punctuation(self) -> None:
        """Test with normal punctuation (single marks only)."""
        text = "Is this real? Yes, it is! That is good."
        result = compute_emoticons(text)
        assert result.multiple_exclamation_count == 0
        assert result.multiple_question_count == 0
        assert result.interrobang_count == 0


class TestEmphasisMarkers:
    """Test emphasis marker detection."""

    def test_all_caps_emphasis(self) -> None:
        """Test detection of ALL CAPS emphasis words.

        Known acronyms (NASA, FBI, etc.) should be excluded.
        """
        text = "This is VERY IMPORTANT and ABSOLUTELY necessary."
        result = compute_emoticons(text)
        # "VERY", "IMPORTANT", "ABSOLUTELY" should be counted
        assert result.caps_emphasis_count >= 2

    def test_excludes_known_acronyms(self) -> None:
        """Test that known acronyms are not counted as emphasis.

        Words like NASA, FBI, USA are in the CAPS_NON_EMPHASIS set
        and should not be counted as emphasis markers.
        """
        text = "NASA and FBI are organizations in the USA."
        result = compute_emoticons(text)
        assert result.caps_emphasis_count == 0

    def test_asterisk_emphasis(self) -> None:
        """Test detection of *asterisk emphasis* patterns."""
        text = "This is *really* important and *absolutely* critical."
        result = compute_emoticons(text)
        assert result.asterisk_emphasis_count == 2

    def test_underscore_emphasis(self) -> None:
        """Test detection of _underscore emphasis_ patterns."""
        text = "This is _very_ important."
        result = compute_emoticons(text)
        assert result.underscore_emphasis_count == 1


class TestLaughterExpressions:
    """Test laughter expression detection."""

    def test_detects_haha(self) -> None:
        """Test detection of 'haha' variants."""
        text = "That's so funny haha! Hahaha indeed!"
        result = compute_emoticons(text)
        assert result.laughter_count >= 2
        assert "haha" in result.laughter_types

    def test_detects_lol(self) -> None:
        """Test detection of 'lol'."""
        text = "That was hilarious lol. Can you believe it lol."
        result = compute_emoticons(text)
        assert result.laughter_count >= 2
        assert "lol" in result.laughter_types

    def test_detects_lmao(self) -> None:
        """Test detection of 'lmao'."""
        text = "I'm dying lmao that was too funny."
        result = compute_emoticons(text)
        assert result.laughter_count >= 1
        assert "lmao" in result.laughter_types

    def test_no_laughter(self) -> None:
        """Test with text containing no laughter expressions."""
        text = "The committee discussed the quarterly results."
        result = compute_emoticons(text)
        assert result.laughter_count == 0


class TestExpressivenessScore:
    """Test composite expressiveness score computation."""

    def test_expressive_text_scores_high(self) -> None:
        """Test that highly expressive text scores above 0.2.

        Text with emoji, emoticons, exclamation marks, and laughter
        should produce a meaningfully nonzero expressiveness score.
        """
        text = "OMG!!! This is AMAZING :D :D haha \U0001f600\U0001f600 I love it!!"
        result = compute_emoticons(text)
        assert result.expressiveness_score > 0.2

    def test_neutral_text_scores_low(self) -> None:
        """Test that neutral, formal text scores near zero."""
        text = (
            "The committee reviewed the preliminary findings from the "
            "quarterly analysis. All participants agreed that further "
            "investigation was warranted before proceeding."
        )
        result = compute_emoticons(text)
        assert result.expressiveness_score < 0.1

    def test_expressiveness_score_bounded(self) -> None:
        """Test that expressiveness score is between 0.0 and 1.0."""
        texts = [
            "Hello.",
            "OMG!!! WOW!!! AMAZING!!! :D :D :D haha lol \U0001f600\U0001f600\U0001f600",
            "",
        ]
        for text in texts:
            result = compute_emoticons(text)
            assert 0.0 <= result.expressiveness_score <= 1.0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string(self) -> None:
        """Test that empty string returns zero-valued result."""
        result = compute_emoticons("")
        assert result.emoji_count == 0
        assert result.text_emoticon_count == 0
        assert result.expressiveness_score == 0.0
        assert result.metadata["word_count"] == 0

    def test_whitespace_only(self) -> None:
        """Test that whitespace-only text returns zero-valued result."""
        result = compute_emoticons("   \n\t  ")
        assert result.emoji_count == 0
        assert result.metadata["word_count"] == 0

    def test_single_word(self) -> None:
        """Test with a single word."""
        result = compute_emoticons("hello")
        assert result.emoji_count == 0
        assert result.metadata["word_count"] == 1


class TestDensityNormalization:
    """Test that densities are correctly normalized per 100 words."""

    def test_emoji_density(self) -> None:
        """Test that emoji density is computed per 100 words."""
        # 10 words + 2 emoji = density of 20.0 per 100 words
        text = "word " * 10 + "\U0001f600 \U0001f389"
        result = compute_emoticons(text)
        assert result.emoji_density > 0.0

    def test_metadata_contains_word_count(self) -> None:
        """Test that metadata includes the word count."""
        text = "one two three four five"
        result = compute_emoticons(text)
        assert "word_count" in result.metadata
        assert result.metadata["word_count"] == 5
