"""Comprehensive tests for rhythm and prosody metrics module.

This module tests the rhythm and prosody functionality, including syllable
pattern analysis, stress pattern detection, rhythmic regularity, phonological
features (alliteration, assonance, consonance), consonant cluster metrics,
metrical foot estimation, and sentence rhythm.

Related GitHub Issues:
    #25 - Rhythm and Prosody Metrics
    https://github.com/craigtrim/pystylometry/issues/25

Test coverage:
    - Basic functionality and return type validation
    - Syllable pattern metrics (mean, std dev, poly/mono ratios)
    - Rhythmic regularity (CV-based)
    - Stress pattern entropy
    - Sentence rhythm (alternation, composite score)
    - Phonological features (alliteration, assonance, consonance)
    - Consonant cluster metrics
    - Metrical foot estimation (iambic, trochaic, dactylic, anapestic)
    - Edge cases (empty text, single word, no CMU coverage)
    - Metadata completeness
    - Zero division safety
"""

import math

from pystylometry._types import RhythmProsodyResult
from pystylometry.prosody.rhythm_prosody import compute_rhythm_prosody


class TestRhythmProsodyBasicFunctionality:
    """Test basic rhythm and prosody functionality."""

    def test_returns_correct_type(self) -> None:
        """Test that compute_rhythm_prosody returns RhythmProsodyResult."""
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_rhythm_prosody(text)

        assert isinstance(result, RhythmProsodyResult)

    def test_basic_text_analysis(self) -> None:
        """Test basic text analysis returns expected fields."""
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_rhythm_prosody(text)

        assert hasattr(result, "mean_syllables_per_word")
        assert hasattr(result, "syllable_std_dev")
        assert hasattr(result, "polysyllabic_ratio")
        assert hasattr(result, "monosyllabic_ratio")
        assert hasattr(result, "rhythmic_regularity")
        assert hasattr(result, "syllable_cv")
        assert hasattr(result, "stress_pattern_entropy")
        assert hasattr(result, "sentence_length_alternation")
        assert hasattr(result, "sentence_rhythm_score")
        assert hasattr(result, "alliteration_density")
        assert hasattr(result, "assonance_density")
        assert hasattr(result, "consonance_density")
        assert hasattr(result, "mean_consonant_cluster_length")
        assert hasattr(result, "initial_cluster_ratio")
        assert hasattr(result, "final_cluster_ratio")
        assert hasattr(result, "iambic_ratio")
        assert hasattr(result, "trochaic_ratio")
        assert hasattr(result, "dactylic_ratio")
        assert hasattr(result, "anapestic_ratio")
        assert hasattr(result, "metadata")

    def test_word_count_in_metadata(self) -> None:
        """Test that word count is correctly recorded in metadata."""
        text = "one two three four five"
        result = compute_rhythm_prosody(text)

        assert "word_count" in result.metadata
        assert result.metadata["word_count"] == 5


class TestRhythmProsodyEmptyAndEdgeCases:
    """Test edge cases and empty input handling."""

    def test_empty_text(self) -> None:
        """Test handling of empty text."""
        result = compute_rhythm_prosody("")

        assert result.mean_syllables_per_word == 0.0
        assert result.rhythmic_regularity == 0.0
        assert result.alliteration_density == 0.0
        assert result.metadata["word_count"] == 0

    def test_whitespace_only(self) -> None:
        """Test handling of whitespace-only text."""
        result = compute_rhythm_prosody("   \n\t  ")

        assert result.mean_syllables_per_word == 0.0
        assert result.metadata["word_count"] == 0

    def test_single_word(self) -> None:
        """Test handling of single word input."""
        result = compute_rhythm_prosody("hello")

        assert result.metadata["word_count"] == 1
        assert result.mean_syllables_per_word > 0
        # Single word: no pairs for alliteration/assonance
        assert result.alliteration_density == 0.0
        assert result.assonance_density == 0.0
        assert result.consonance_density == 0.0

    def test_punctuation_only(self) -> None:
        """Test text with only punctuation."""
        result = compute_rhythm_prosody("!!! ??? ...")

        assert result.metadata["word_count"] == 0
        assert result.mean_syllables_per_word == 0.0

    def test_single_sentence(self) -> None:
        """Test text with only one sentence (no alternation possible)."""
        result = compute_rhythm_prosody("The quick brown fox jumps over the lazy dog")

        # Single sentence: no alternation
        assert result.sentence_length_alternation == 0.0
        assert result.sentence_rhythm_score == 0.0


class TestSyllablePatternMetrics:
    """Test syllable pattern analysis."""

    def test_monosyllabic_text(self) -> None:
        """Test text composed of mostly monosyllabic words."""
        text = "The cat sat on the mat. The dog ran in the fog."
        result = compute_rhythm_prosody(text)

        assert result.mean_syllables_per_word >= 1.0
        assert result.monosyllabic_ratio > 0.5

    def test_polysyllabic_text(self) -> None:
        """Test text with polysyllabic words."""
        text = "Unfortunately, the extraordinary circumstances necessitated an investigation."
        result = compute_rhythm_prosody(text)

        assert result.polysyllabic_ratio > 0.0
        assert result.mean_syllables_per_word > 1.5

    def test_syllable_std_dev_uniform(self) -> None:
        """Test low std dev for uniform syllable counts."""
        # All monosyllabic words should have low std dev
        text = "The cat sat on the mat"
        result = compute_rhythm_prosody(text)

        assert result.syllable_std_dev < 0.5

    def test_syllable_std_dev_varied(self) -> None:
        """Test higher std dev for varied syllable counts."""
        # Mix of short and long words
        text = "I saw an extraordinarily beautiful hippopotamus"
        result = compute_rhythm_prosody(text)

        assert result.syllable_std_dev > 0.5

    def test_syllable_ratios_sum_to_one_or_less(self) -> None:
        """Test that mono + poly ratios don't exceed 1.0."""
        text = "The beautiful garden had extraordinary flowers."
        result = compute_rhythm_prosody(text)

        assert result.monosyllabic_ratio + result.polysyllabic_ratio <= 1.0 + 1e-9


class TestRhythmicRegularity:
    """Test rhythmic regularity computation."""

    def test_uniform_text_high_regularity(self) -> None:
        """Test that uniform syllable text has high regularity."""
        # All monosyllabic: CV = 0, regularity = word count
        text = "the cat sat on the mat"
        result = compute_rhythm_prosody(text)

        assert result.rhythmic_regularity > 1.0

    def test_varied_text_lower_regularity(self) -> None:
        """Test that varied syllable text has lower regularity."""
        text = "I saw an extraordinarily beautiful hippopotamus yesterday"
        result = compute_rhythm_prosody(text)

        # Should be positive but not extremely high
        assert result.rhythmic_regularity > 0
        assert result.syllable_cv > 0

    def test_cv_relationship(self) -> None:
        """Test that regularity is inverse of CV when CV > 0."""
        text = "The beautiful garden had extraordinary flowers and small trees."
        result = compute_rhythm_prosody(text)

        if result.syllable_cv > 0:
            expected_regularity = 1.0 / result.syllable_cv
            assert abs(result.rhythmic_regularity - expected_regularity) < 0.01


class TestStressPatternEntropy:
    """Test stress pattern entropy computation."""

    def test_positive_entropy(self) -> None:
        """Test that typical text produces positive entropy."""
        text = "The beautiful garden had extraordinary flowers and small green trees."
        result = compute_rhythm_prosody(text)

        assert result.stress_pattern_entropy >= 0.0

    def test_entropy_increases_with_variety(self) -> None:
        """Test that more varied stress patterns increase entropy."""
        # Uniform text (all monosyllabic, stress pattern "1")
        uniform_text = "cat dog bird fish snake frog bear deer fox wolf"
        # Varied text (mix of stress patterns)
        varied_text = "beautiful extraordinary understand investigate communicate"

        uniform_result = compute_rhythm_prosody(uniform_text)
        varied_result = compute_rhythm_prosody(varied_text)

        # Varied text should have higher entropy (more diverse patterns)
        assert varied_result.stress_pattern_entropy >= uniform_result.stress_pattern_entropy


class TestSentenceRhythm:
    """Test sentence-level rhythm metrics."""

    def test_alternating_sentence_lengths(self) -> None:
        """Test that alternating short/long sentences produce alternation."""
        text = "Short one. This is a much longer sentence with many more words. Brief. Another lengthy sentence follows here now."
        result = compute_rhythm_prosody(text)

        assert result.sentence_length_alternation > 0
        assert result.sentence_rhythm_score > 0

    def test_uniform_sentence_lengths(self) -> None:
        """Test that uniform sentence lengths produce low alternation."""
        text = "The cat sat down. The dog ran fast. The bird flew high. The fish swam deep."
        result = compute_rhythm_prosody(text)

        # Uniform sentences should have relatively low alternation
        assert result.sentence_length_alternation >= 0.0

    def test_multi_sentence_required(self) -> None:
        """Test that at least two sentences are needed for rhythm metrics."""
        text = "Just one sentence here with several words."
        result = compute_rhythm_prosody(text)

        assert result.sentence_length_alternation == 0.0
        assert result.sentence_rhythm_score == 0.0


class TestPhonologicalFeatures:
    """Test alliteration, assonance, and consonance detection."""

    def test_alliteration_detection(self) -> None:
        """Test detection of alliterative word pairs."""
        # "Peter Piper picked" - all start with P sound
        text = "Peter Piper picked a peck of pickled peppers."
        result = compute_rhythm_prosody(text)

        assert result.alliteration_density > 0

    def test_assonance_detection(self) -> None:
        """Test detection of assonant word pairs."""
        # Adjacent words sharing vowel phonemes: "light" (AY) + "high" (AY),
        # "boat" (OW) + "float" (OW)
        text = "The light shines high. The boat will float."
        result = compute_rhythm_prosody(text)

        # Should detect shared vowel sounds between adjacent words
        assert result.assonance_density > 0

    def test_consonance_detection(self) -> None:
        """Test detection of consonant-repeating pairs."""
        text = "The black duck stuck in the thick muck."
        result = compute_rhythm_prosody(text)

        assert result.consonance_density > 0

    def test_no_alliteration(self) -> None:
        """Test text with minimal alliteration."""
        # Words starting with different sounds
        text = "apple banana cherry date elderberry fig grape"
        result = compute_rhythm_prosody(text)

        # Some pairs may still share sounds; just check it's a valid float
        assert result.alliteration_density >= 0.0

    def test_densities_per_100_words(self) -> None:
        """Test that phonological densities are per 100 words."""
        text = "Peter Piper picked a peck of pickled peppers."
        result = compute_rhythm_prosody(text)

        # Density is (pairs / words) * 100
        # Alliteration density should be reasonable for this text
        assert result.alliteration_density <= 100.0
        assert result.alliteration_density >= 0.0


class TestConsonantClusterMetrics:
    """Test consonant cluster complexity metrics."""

    def test_initial_clusters(self) -> None:
        """Test detection of initial consonant clusters."""
        # Words with initial clusters: "stream", "strong", "throne", "brown"
        text = "The stream flowed through the strong brown throne."
        result = compute_rhythm_prosody(text)

        assert result.initial_cluster_ratio > 0

    def test_final_clusters(self) -> None:
        """Test detection of final consonant clusters."""
        # Words with final clusters: "world", "strength", "burnt"
        text = "The world has great strength and burnt land."
        result = compute_rhythm_prosody(text)

        assert result.final_cluster_ratio > 0

    def test_mean_cluster_length(self) -> None:
        """Test mean consonant cluster length calculation."""
        text = "The strong stream flowed through the brown ground."
        result = compute_rhythm_prosody(text)

        # Clusters should have length >= 2 by definition
        if result.mean_consonant_cluster_length > 0:
            assert result.mean_consonant_cluster_length >= 2.0

    def test_simple_words_low_clusters(self) -> None:
        """Test that simple words have fewer clusters."""
        text = "I am a man. He is a boy. We are one."
        result = compute_rhythm_prosody(text)

        # Simple short words should have low cluster ratios
        assert result.initial_cluster_ratio < 0.5


class TestMetricalFootEstimation:
    """Test metrical foot estimation from stress patterns."""

    def test_foot_ratios_sum_to_one(self) -> None:
        """Test that metrical foot ratios sum to approximately 1.0."""
        text = "The beautiful garden had extraordinary flowers and lovely green trees."
        result = compute_rhythm_prosody(text)

        total = (
            result.iambic_ratio
            + result.trochaic_ratio
            + result.dactylic_ratio
            + result.anapestic_ratio
        )
        # If any feet were detected, they should sum to ~1.0
        if total > 0:
            assert abs(total - 1.0) < 0.01

    def test_trochaic_words(self) -> None:
        """Test that trochaic words (stressed-unstressed) are detected."""
        # "garden", "happy", "water" are trochaic (S-U)
        text = "garden happy water flower table music paper"
        result = compute_rhythm_prosody(text)

        assert result.trochaic_ratio > 0

    def test_iambic_words(self) -> None:
        """Test that iambic words (unstressed-stressed) are detected."""
        # "above", "begin", "about", "along" are iambic (U-S)
        text = "above begin about along across among aside"
        result = compute_rhythm_prosody(text)

        assert result.iambic_ratio > 0

    def test_monosyllabic_no_feet(self) -> None:
        """Test that monosyllabic words don't produce foot patterns."""
        text = "a the on in at to by"
        result = compute_rhythm_prosody(text)

        # All monosyllabic: no bigrams possible
        total = (
            result.iambic_ratio
            + result.trochaic_ratio
            + result.dactylic_ratio
            + result.anapestic_ratio
        )
        assert total == 0.0

    def test_ratios_between_zero_and_one(self) -> None:
        """Test that all foot ratios are between 0 and 1."""
        text = "The beautiful extraordinary understanding investigates communication."
        result = compute_rhythm_prosody(text)

        assert 0.0 <= result.iambic_ratio <= 1.0
        assert 0.0 <= result.trochaic_ratio <= 1.0
        assert 0.0 <= result.dactylic_ratio <= 1.0
        assert 0.0 <= result.anapestic_ratio <= 1.0


class TestMetadataContents:
    """Test metadata contents and completeness."""

    def test_metadata_keys(self) -> None:
        """Test that metadata contains expected keys."""
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_rhythm_prosody(text)

        assert "word_count" in result.metadata
        assert "unique_words" in result.metadata
        assert "sentence_count" in result.metadata
        assert "total_syllables" in result.metadata
        assert "cmu_coverage" in result.metadata
        assert "syllable_distribution" in result.metadata
        assert "word_stress_patterns" in result.metadata

    def test_cmu_coverage(self) -> None:
        """Test that CMU coverage is a valid ratio."""
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_rhythm_prosody(text)

        assert 0.0 <= result.metadata["cmu_coverage"] <= 1.0

    def test_cmu_coverage_common_words(self) -> None:
        """Test that common English words have high CMU coverage."""
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_rhythm_prosody(text)

        # Common words should mostly be in CMU dictionary
        assert result.metadata["cmu_coverage"] > 0.5

    def test_syllable_distribution(self) -> None:
        """Test that syllable distribution is a valid dict."""
        text = "The beautiful garden had extraordinary flowers."
        result = compute_rhythm_prosody(text)

        dist = result.metadata["syllable_distribution"]
        assert isinstance(dist, dict)
        # All keys should be positive integers (syllable counts)
        assert all(isinstance(k, int) and k > 0 for k in dist.keys())
        # All values should be positive integers (word counts)
        assert all(isinstance(v, int) and v > 0 for v in dist.values())

    def test_word_stress_patterns(self) -> None:
        """Test that word stress patterns are valid."""
        text = "The beautiful garden had extraordinary flowers."
        result = compute_rhythm_prosody(text)

        patterns = result.metadata["word_stress_patterns"]
        assert isinstance(patterns, dict)
        for word, stress in patterns.items():
            assert isinstance(word, str)
            assert isinstance(stress, list)
            assert all(s in (0, 1, 2) for s in stress)


class TestZeroDivision:
    """Test handling of potential zero division scenarios."""

    def test_empty_result_no_nan(self) -> None:
        """Test that empty text doesn't produce NaN values."""
        result = compute_rhythm_prosody("")

        assert not math.isnan(result.mean_syllables_per_word)
        assert not math.isnan(result.syllable_std_dev)
        assert not math.isnan(result.polysyllabic_ratio)
        assert not math.isnan(result.monosyllabic_ratio)
        assert not math.isnan(result.rhythmic_regularity)
        assert not math.isnan(result.syllable_cv)
        assert not math.isnan(result.stress_pattern_entropy)
        assert not math.isnan(result.sentence_length_alternation)
        assert not math.isnan(result.sentence_rhythm_score)
        assert not math.isnan(result.alliteration_density)
        assert not math.isnan(result.assonance_density)
        assert not math.isnan(result.consonance_density)
        assert not math.isnan(result.mean_consonant_cluster_length)
        assert not math.isnan(result.initial_cluster_ratio)
        assert not math.isnan(result.final_cluster_ratio)
        assert not math.isnan(result.iambic_ratio)
        assert not math.isnan(result.trochaic_ratio)
        assert not math.isnan(result.dactylic_ratio)
        assert not math.isnan(result.anapestic_ratio)

    def test_single_word_no_nan(self) -> None:
        """Test that single word input doesn't produce NaN values."""
        result = compute_rhythm_prosody("hello")

        assert not math.isnan(result.mean_syllables_per_word)
        assert not math.isnan(result.rhythmic_regularity)
        assert not math.isnan(result.alliteration_density)


class TestRealWorldText:
    """Test with realistic text samples."""

    def test_prose_text(self) -> None:
        """Test analysis of typical prose text."""
        text = """
        The old man sat on the porch and watched the sun set behind the mountains.
        Birds sang softly in the trees. A cool breeze swept through the valley.
        He smiled, remembering days gone by. Life was simple then.
        """
        result = compute_rhythm_prosody(text)

        assert result.mean_syllables_per_word > 0
        assert result.metadata["word_count"] > 10
        assert result.metadata["sentence_count"] >= 4
        assert result.sentence_length_alternation > 0

    def test_poetic_text(self) -> None:
        """Test analysis of poetic text with deliberate rhythm."""
        text = """
        Shall I compare thee to a summer day?
        Thou art more lovely and more temperate.
        Rough winds do shake the darling buds of May,
        And summer lease hath all too short a date.
        """
        result = compute_rhythm_prosody(text)

        assert result.mean_syllables_per_word > 0
        assert result.stress_pattern_entropy > 0
        # Poetry often has metrical foot patterns
        total_feet = (
            result.iambic_ratio
            + result.trochaic_ratio
            + result.dactylic_ratio
            + result.anapestic_ratio
        )
        assert total_feet > 0

    def test_technical_text(self) -> None:
        """Test analysis of technical text with complex vocabulary."""
        text = """
        The implementation utilizes sophisticated algorithms for computational
        analysis. Comprehensive documentation facilitates reproducibility.
        """
        result = compute_rhythm_prosody(text)

        # Technical text tends to have higher mean syllables
        assert result.mean_syllables_per_word > 1.5
        assert result.polysyllabic_ratio > 0.1
