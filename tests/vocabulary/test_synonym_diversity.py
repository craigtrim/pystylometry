"""Tests for synonym diversity analysis.

This module tests the synonym diversity analyzer functionality, including
token-to-cluster assignment, per-cluster diversity scoring via normalized
Shannon entropy, repetition avoidance, thesaurus indicator, vocabulary
sophistication, and the data injection pattern (custom synonym maps).

Related GitHub Issues:
    #30 - Whonix stylometric features
    https://github.com/craigtrim/pystylometry/issues/30

Test coverage:
    - Return type validation (SynonymDiversityResult dataclass)
    - Default synonym map usage
    - Custom synonym map injection
    - Per-cluster diversity scoring (Shannon entropy)
    - Repetition avoidance metric
    - Thesaurus indicator metric
    - Vocabulary sophistication metric
    - Cluster detail structure
    - Empty text edge case
    - Empty synonym map edge case
    - Mapped vs. unmapped word counts
"""

from pystylometry.vocabulary.synonym_diversity import (
    compute_synonym_diversity,
    DEFAULT_SYNONYM_MAP,
)


class TestSynonymDiversityReturnType:
    """Test that compute_synonym_diversity returns the correct type."""

    def test_returns_synonym_diversity_result(self) -> None:
        """Test that compute_synonym_diversity returns SynonymDiversityResult."""
        from pystylometry._types import SynonymDiversityResult

        text = "He said hello. She stated goodbye."
        result = compute_synonym_diversity(text)
        assert isinstance(result, SynonymDiversityResult)

    def test_has_all_required_fields(self) -> None:
        """Test that the result has all expected fields."""
        text = "The quick brown fox."
        result = compute_synonym_diversity(text)

        assert hasattr(result, "synonym_diversity_score")
        assert hasattr(result, "repetition_avoidance_score")
        assert hasattr(result, "thesaurus_indicator")
        assert hasattr(result, "vocabulary_sophistication")
        assert hasattr(result, "cluster_details")
        assert hasattr(result, "active_cluster_count")
        assert hasattr(result, "total_cluster_count")
        assert hasattr(result, "mapped_word_count")
        assert hasattr(result, "unmapped_word_count")
        assert hasattr(result, "metadata")


class TestDefaultSynonymMap:
    """Test behavior with the default synonym map."""

    def test_uses_default_map_when_none(self) -> None:
        """Test that None synonym_map uses the built-in default."""
        text = "He said hello. She stated goodbye. They mentioned it."
        result = compute_synonym_diversity(text)
        # "said", "stated", "mentioned" are all in communication_verb cluster
        assert result.active_cluster_count >= 1

    def test_default_map_has_clusters(self) -> None:
        """Test that the default map contains multiple synonym clusters."""
        cluster_ids = set(DEFAULT_SYNONYM_MAP.values())
        # Default map should have at least 10 distinct clusters
        assert len(cluster_ids) >= 10

    def test_metadata_tracks_default_map(self) -> None:
        """Test that metadata indicates when the default map is used."""
        result = compute_synonym_diversity("He said hello.")
        assert result.metadata.get("using_default_map") is True


class TestCustomSynonymMap:
    """Test behavior with custom synonym maps (data injection pattern)."""

    def test_custom_map_is_used(self) -> None:
        """Test that a custom synonym map is correctly applied."""
        custom_map = {
            "happy": "emotion",
            "glad": "emotion",
            "joyful": "emotion",
            "sad": "emotion",
        }
        text = "I am happy and glad. She is joyful."
        result = compute_synonym_diversity(text, synonym_map=custom_map)
        assert result.active_cluster_count == 1
        assert result.mapped_word_count == 3

    def test_empty_map_produces_no_clusters(self) -> None:
        """Test that an empty synonym map results in no active clusters."""
        result = compute_synonym_diversity("Hello world.", synonym_map={})
        assert result.active_cluster_count == 0
        assert result.mapped_word_count == 0

    def test_custom_map_metadata(self) -> None:
        """Test that metadata reflects the custom map size."""
        custom_map = {"fast": "speed", "quick": "speed", "rapid": "speed"}
        result = compute_synonym_diversity("Go fast.", synonym_map=custom_map)
        assert result.metadata["synonym_map_size"] == 3


class TestDiversityScoring:
    """Test per-cluster diversity via normalized Shannon entropy."""

    def test_single_word_cluster_has_zero_diversity(self) -> None:
        """Test that a cluster with only one unique word has diversity 0.0.

        Shannon entropy is zero when the distribution is concentrated
        on a single outcome.
        """
        custom_map = {"said": "verb", "stated": "verb"}
        text = "He said hello. He said goodbye. He said thanks."
        result = compute_synonym_diversity(text, synonym_map=custom_map)

        # Only "said" appears, so diversity within the cluster = 0.0
        assert len(result.cluster_details) == 1
        assert result.cluster_details[0]["diversity"] == 0.0

    def test_evenly_distributed_cluster_has_high_diversity(self) -> None:
        """Test that a cluster with evenly distributed words has high diversity.

        When each synonym is used equally often, normalized Shannon
        entropy should approach 1.0.
        """
        custom_map = {"said": "verb", "stated": "verb", "mentioned": "verb"}
        text = "He said hello. She stated goodbye. They mentioned it."
        result = compute_synonym_diversity(text, synonym_map=custom_map)

        # Three different words, one occurrence each: maximum diversity
        assert len(result.cluster_details) == 1
        assert result.cluster_details[0]["diversity"] == 1.0

    def test_overall_diversity_score(self) -> None:
        """Test that overall synonym_diversity_score is the mean of cluster diversities."""
        custom_map = {
            "said": "comm", "stated": "comm", "mentioned": "comm",
            "big": "size", "large": "size",
        }
        text = "He said hello. She stated goodbye. They mentioned it. The big house. The big car."
        result = compute_synonym_diversity(text, synonym_map=custom_map)

        # comm cluster: 3 unique words, 1 each → diversity = 1.0
        # size cluster: "big" x2 → diversity = 0.0
        # Mean = (1.0 + 0.0) / 2 = 0.5
        assert abs(result.synonym_diversity_score - 0.5) < 0.01


class TestRepetitionAvoidance:
    """Test repetition avoidance metric."""

    def test_high_repetition_has_low_avoidance(self) -> None:
        """Test that repeated use of one synonym gives low avoidance score.

        When an author uses the same word repeatedly from a cluster,
        the dominant ratio is high and avoidance is low.
        """
        custom_map = {"said": "verb", "stated": "verb", "mentioned": "verb"}
        text = "He said hello. He said goodbye. He said thanks. He said yes."
        result = compute_synonym_diversity(text, synonym_map=custom_map)
        # dominant_ratio = 1.0, avoidance = 0.0
        assert result.repetition_avoidance_score == 0.0

    def test_varied_usage_has_high_avoidance(self) -> None:
        """Test that varied synonym usage gives high avoidance score."""
        custom_map = {"said": "verb", "stated": "verb", "mentioned": "verb"}
        text = "He said hello. She stated goodbye. They mentioned it."
        result = compute_synonym_diversity(text, synonym_map=custom_map)
        # Each word used once: dominant_ratio = 1/3, avoidance = 2/3
        assert result.repetition_avoidance_score > 0.5


class TestThesaurusIndicator:
    """Test thesaurus usage indicator metric."""

    def test_high_coverage_indicates_thesaurus(self) -> None:
        """Test that using all available synonyms gives high indicator.

        When an author uses every word available in a synonym cluster,
        the coverage ratio is 1.0, suggesting possible thesaurus use.
        """
        custom_map = {"said": "verb", "stated": "verb", "mentioned": "verb"}
        text = "He said hello. She stated goodbye. They mentioned it."
        result = compute_synonym_diversity(text, synonym_map=custom_map)
        # All 3/3 available words used: coverage = 1.0
        assert result.thesaurus_indicator == 1.0

    def test_low_coverage_indicates_natural(self) -> None:
        """Test that using few synonyms gives low indicator.

        Natural writing typically favors one or two words per cluster.
        """
        custom_map = {"said": "verb", "stated": "verb", "mentioned": "verb",
                       "noted": "verb", "declared": "verb", "announced": "verb"}
        text = "He said hello. He said goodbye. He said thanks."
        result = compute_synonym_diversity(text, synonym_map=custom_map)
        # Only 1/6 available words used: coverage = 1/6
        assert result.thesaurus_indicator < 0.2


class TestClusterDetails:
    """Test cluster detail structure."""

    def test_cluster_detail_fields(self) -> None:
        """Test that each cluster detail dict has all expected keys."""
        custom_map = {"said": "verb", "stated": "verb"}
        text = "He said hello. She stated goodbye."
        result = compute_synonym_diversity(text, synonym_map=custom_map)

        assert len(result.cluster_details) == 1
        detail = result.cluster_details[0]

        assert "cluster_id" in detail
        assert "words_used" in detail
        assert "total_occurrences" in detail
        assert "unique_words_used" in detail
        assert "diversity" in detail
        assert "most_common" in detail
        assert "dominant_ratio" in detail
        assert "word_frequencies" in detail

    def test_cluster_details_sorted_by_id(self) -> None:
        """Test that cluster details are sorted by cluster_id."""
        custom_map = {"big": "size", "said": "comm", "fast": "speed"}
        text = "He said something big and fast."
        result = compute_synonym_diversity(text, synonym_map=custom_map)

        cluster_ids = [d["cluster_id"] for d in result.cluster_details]
        assert cluster_ids == sorted(cluster_ids)


class TestMappedUnmappedCounts:
    """Test mapped vs. unmapped word counting."""

    def test_mapped_count(self) -> None:
        """Test that mapped_word_count reflects words found in synonym map."""
        custom_map = {"said": "verb", "stated": "verb"}
        text = "He said hello. She stated goodbye."
        result = compute_synonym_diversity(text, synonym_map=custom_map)
        assert result.mapped_word_count == 2  # "said" and "stated"

    def test_unmapped_count(self) -> None:
        """Test that unmapped_word_count reflects words not in synonym map."""
        custom_map = {"said": "verb"}
        text = "He said hello."
        result = compute_synonym_diversity(text, synonym_map=custom_map)
        # "he" and "hello" are unmapped (3 tokens total, 1 mapped)
        assert result.unmapped_word_count == 2


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string(self) -> None:
        """Test that empty string returns zero-valued result."""
        result = compute_synonym_diversity("")
        assert result.synonym_diversity_score == 0.0
        assert result.active_cluster_count == 0
        assert result.mapped_word_count == 0
        assert result.metadata["word_count"] == 0

    def test_whitespace_only(self) -> None:
        """Test that whitespace-only text returns zero-valued result."""
        result = compute_synonym_diversity("   \n\t  ")
        assert result.synonym_diversity_score == 0.0
        assert result.metadata["word_count"] == 0

    def test_no_mapped_words(self) -> None:
        """Test with text where no words are in the synonym map."""
        text = "The quick brown fox jumps over the lazy dog."
        custom_map = {"said": "verb", "stated": "verb"}
        result = compute_synonym_diversity(text, synonym_map=custom_map)
        assert result.active_cluster_count == 0
        assert result.mapped_word_count == 0
        assert result.synonym_diversity_score == 0.0

    def test_scores_bounded(self) -> None:
        """Test that all scores are between 0.0 and 1.0."""
        text = "He said hello. She stated goodbye. They mentioned it."
        result = compute_synonym_diversity(text)
        assert 0.0 <= result.synonym_diversity_score <= 1.0
        assert 0.0 <= result.repetition_avoidance_score <= 1.0
        assert 0.0 <= result.thesaurus_indicator <= 1.0
        assert 0.0 <= result.vocabulary_sophistication <= 1.0
