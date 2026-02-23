"""Tests for sentence-level syllable analysis.

Related GitHub Issue:
    #66 - Sentence-level syllable analysis
    https://github.com/craigtrim/pystylometry/issues/66
"""

import pytest

from pystylometry.prosody import compute_sentence_syllable_patterns


def test_basic_sentence_analysis():
    """Test basic per-sentence syllable counting."""
    text = "The cat sat. The dog ran quickly."
    result = compute_sentence_syllable_patterns(text)

    assert len(result.sentences) == 2
    assert result.sentences[0].word_count == 3
    assert result.sentences[0].syllable_count == 3  # The(1) cat(1) sat(1)
    assert result.sentences[1].word_count == 4
    assert result.sentences[1].syllable_count == 5  # The(1) dog(1) ran(1) quickly(2)


def test_per_word_syllable_breakdown():
    """Test that per-word syllable counts are captured correctly."""
    text = "For the AI detection feature."
    result = compute_sentence_syllable_patterns(text)

    assert len(result.sentences) == 1
    sent = result.sentences[0]
    assert sent.word_count == 5
    # For(1), the(1), AI(1), detection(3), feature(2)
    assert sent.syllables_per_word == [1, 1, 1, 3, 2]
    assert sent.syllable_count == 8


def test_uniformity_score_calculation():
    """Test complexity uniformity scoring."""
    # Uniform complexity (AI-like) - all sentences have similar syllables/word
    uniform_text = "The cat sat. The dog ran. The bird flew."
    uniform_result = compute_sentence_syllable_patterns(uniform_text)

    # Varied complexity (human-like) - sentences vary widely in syllables/word
    varied_text = "Go. The cat sat on the mat. Nevertheless, the magnificent bird soared majestically."
    varied_result = compute_sentence_syllable_patterns(varied_text)

    # Uniform text should have higher uniformity score
    assert uniform_result.complexity_uniformity_score > varied_result.complexity_uniformity_score

    # Uniform text should have lower complexity variance
    assert uniform_result.std_sentence_complexity < varied_result.std_sentence_complexity


def test_empty_text():
    """Test handling of empty input."""
    result = compute_sentence_syllable_patterns("")

    assert len(result.sentences) == 0
    assert result.mean_syllables_per_sentence == 0.0
    assert result.complexity_uniformity_score == 0.0
    assert "warning" in result.metadata


def test_single_sentence():
    """Test with single sentence."""
    text = "The quick brown fox jumps over the lazy dog."
    result = compute_sentence_syllable_patterns(text)

    assert len(result.sentences) == 1
    assert result.sentences[0].word_count == 9
    # The(1) quick(1) brown(1) fox(1) jumps(1) over(2) the(1) lazy(2) dog(1)
    assert result.sentences[0].syllable_count == 11


def test_varying_sentence_lengths():
    """Test with varying sentence lengths."""
    text = "Go. The cat sat on the mat. Nevertheless, the magnificent feline demonstrated extraordinary capabilities."
    result = compute_sentence_syllable_patterns(text)

    assert len(result.sentences) == 3
    # First sentence: shortest
    assert result.sentences[0].word_count == 1
    # Second sentence: medium
    assert result.sentences[1].word_count == 6
    # Third sentence: longest (7 words)
    assert result.sentences[2].word_count == 7

    # Complexity should vary
    assert result.std_sentence_complexity > 0.0


def test_sentence_cv_calculation():
    """Test coefficient of variation for sentence syllables."""
    # All sentences have similar syllable counts
    uniform_text = "The cat sat. The dog ran. The bird flew."
    uniform_result = compute_sentence_syllable_patterns(uniform_text)

    # Sentences have very different syllable counts
    varied_text = "Go! The cat enthusiastically demonstrated extraordinary capabilities. Run!"
    varied_result = compute_sentence_syllable_patterns(varied_text)

    # Varied text should have higher CV
    assert varied_result.sentence_syllable_cv > uniform_result.sentence_syllable_cv


def test_metadata_fields():
    """Test that metadata contains expected fields."""
    text = "The cat sat. The dog ran."
    result = compute_sentence_syllable_patterns(text)

    assert "sentence_count" in result.metadata
    assert "total_words" in result.metadata
    assert "total_syllables" in result.metadata
    # Note: "spacy_model" removed in Issue #68 (replaced spaCy with built-in utils)
    # Related GitHub Issue:
    #     #68 - Replace spaCy with built-in utilities
    #     https://github.com/craigtrim/pystylometry/issues/68
    assert "complexity_cv" in result.metadata

    assert result.metadata["sentence_count"] == 2


def test_distribution_objects():
    """Test that distribution objects are created correctly."""
    text = "The cat sat. The dog ran quickly. The bird flew."
    result = compute_sentence_syllable_patterns(text)

    # Check syllables_per_sentence_dist
    assert hasattr(result.syllables_per_sentence_dist, "values")
    assert hasattr(result.syllables_per_sentence_dist, "mean")
    assert hasattr(result.syllables_per_sentence_dist, "std")
    assert len(result.syllables_per_sentence_dist.values) == 3

    # Check complexity_dist
    assert hasattr(result.complexity_dist, "values")
    assert len(result.complexity_dist.values) == 3


def test_sentence_with_punctuation():
    """Test handling of sentences with various punctuation."""
    text = "Hello! How are you? I'm doing well. Great, thanks."
    result = compute_sentence_syllable_patterns(text)

    # Should recognize 4 sentences
    assert len(result.sentences) == 4


def test_high_uniformity_score_threshold():
    """Test that perfectly uniform sentences have high uniformity score."""
    # All sentences have identical structure: 3 words, 3 syllables
    uniform_text = "The cat sat. The dog ran. The bird flew."
    result = compute_sentence_syllable_patterns(uniform_text)

    # Should have very high uniformity (close to 1.0)
    assert result.complexity_uniformity_score > 0.9


def test_low_uniformity_score_threshold():
    """Test that varied sentences have low uniformity score."""
    # Sentences vary wildly in complexity
    varied_text = (
        "Go! "
        "The enthusiastic feline demonstrated extraordinary capabilities. "
        "Run quickly! "
        "Nevertheless, the magnificent bird majestically soared."
    )
    result = compute_sentence_syllable_patterns(varied_text)

    # Should have lower uniformity
    assert result.complexity_uniformity_score < 0.8


def test_sentence_pattern_fields():
    """Test that SentenceSyllablePattern has all expected fields."""
    text = "The quick brown fox."
    result = compute_sentence_syllable_patterns(text)

    sent = result.sentences[0]
    assert hasattr(sent, "sentence_index")
    assert hasattr(sent, "word_count")
    assert hasattr(sent, "syllable_count")
    assert hasattr(sent, "syllables_per_word")
    assert hasattr(sent, "mean_syllables")
    assert hasattr(sent, "syllable_cv")

    assert sent.sentence_index == 0
    assert isinstance(sent.syllables_per_word, list)
    assert all(isinstance(s, int) for s in sent.syllables_per_word)


@pytest.mark.skipif(
    True,  # Skip by default since it requires fixture files
    reason="Requires AI/human fixture files"
)
def test_ai_vs_human_fixtures():
    """Test with AI vs human text from fixtures.

    AI text should show higher uniformity than human text.
    """
    from pathlib import Path

    ai_text = Path("tests/fixtures/kilgarriff/05-ai-chatgpt.txt").read_text()
    human_text = Path("tests/fixtures/kilgarriff/01-single-author-doyle.txt").read_text()

    ai_result = compute_sentence_syllable_patterns(ai_text)
    human_result = compute_sentence_syllable_patterns(human_text)

    # AI should have higher uniformity
    assert ai_result.complexity_uniformity_score > human_result.complexity_uniformity_score

    # AI should have lower complexity variance
    assert ai_result.std_sentence_complexity < human_result.std_sentence_complexity


def test_aggregate_statistics():
    """Test that aggregate statistics are calculated correctly."""
    text = "The cat sat. The dog ran quickly. Go!"
    result = compute_sentence_syllable_patterns(text)

    # Should compute means correctly
    assert result.mean_syllables_per_sentence > 0
    assert result.mean_sentence_complexity > 0

    # Should compute standard deviations
    assert result.std_syllables_per_sentence >= 0
    assert result.std_sentence_complexity >= 0

    # Should compute CVs
    assert result.sentence_syllable_cv >= 0
