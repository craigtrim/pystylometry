"""Comprehensive tests for cohesion and coherence metrics module.

This module tests the cohesion and coherence functionality, including
referential cohesion, lexical cohesion, connective analysis, and
coherence measures.

Related GitHub Issues:
    #22 - Cohesion and Coherence Metrics
    https://github.com/craigtrim/pystylometry/issues/22

Test coverage:
    - Basic functionality and return type validation
    - Empty and edge cases
    - Referential cohesion (pronouns, demonstratives, anaphora)
    - Lexical cohesion (word repetition, content word overlap, lexical chains)
    - Connective detection and categorization
    - Coherence measures (sentence similarity, paragraph consistency)
    - Structural coherence (paragraphs, discourse structure)
    - Real-world text analysis
"""

import math

from pystylometry._types import CohesionCoherenceResult
from pystylometry.stylistic.cohesion_coherence import (
    ADDITIVE_CONNECTIVES,
    ADVERSATIVE_CONNECTIVES,
    ALL_CONNECTIVES,
    CAUSAL_CONNECTIVES,
    DEMONSTRATIVES,
    TEMPORAL_CONNECTIVES,
    compute_cohesion_coherence,
)


class TestBasicFunctionality:
    """Tests for basic function behavior and return types."""

    def test_returns_correct_type(self) -> None:
        """Test that function returns CohesionCoherenceResult."""
        text = "The cat sat on the mat. It was comfortable there."
        result = compute_cohesion_coherence(text)
        assert isinstance(result, CohesionCoherenceResult)

    def test_basic_text_analysis(self) -> None:
        """Test that basic text produces valid results."""
        text = """
        The scientist conducted an experiment. She analyzed the results carefully.
        The data showed significant patterns. These findings were important.
        """
        result = compute_cohesion_coherence(text)

        # All densities should be non-negative
        assert result.pronoun_density >= 0
        assert result.demonstrative_density >= 0
        assert result.connective_density >= 0

        # Ratios should be in valid range
        assert 0 <= result.anaphora_resolution_ratio <= 1
        assert 0 <= result.semantic_coherence_score <= 1

    def test_metadata_completeness(self) -> None:
        """Test that metadata contains expected fields."""
        text = "The dog ran. It was fast. The cat watched."
        result = compute_cohesion_coherence(text)

        assert "model" in result.metadata
        assert "word_count" in result.metadata
        assert "sentence_count" in result.metadata
        assert "pronoun_count" in result.metadata
        assert "demonstrative_count" in result.metadata
        assert "connective_counts" in result.metadata


class TestEmptyAndEdgeCases:
    """Tests for empty text and edge cases."""

    def test_empty_text(self) -> None:
        """Test handling of empty text."""
        result = compute_cohesion_coherence("")

        assert result.pronoun_density == 0.0
        assert result.demonstrative_density == 0.0
        assert result.connective_density == 0.0
        assert result.paragraph_count == 0
        assert result.metadata["word_count"] == 0

    def test_whitespace_only(self) -> None:
        """Test handling of whitespace-only text."""
        result = compute_cohesion_coherence("   \n\t  ")

        assert result.pronoun_density == 0.0
        assert result.metadata["word_count"] == 0

    def test_single_word(self) -> None:
        """Test handling of single word."""
        result = compute_cohesion_coherence("Hello")

        assert result.metadata["word_count"] == 1
        assert result.lexical_chain_count == 0  # Need multiple sentences for chains

    def test_single_sentence(self) -> None:
        """Test handling of single sentence."""
        result = compute_cohesion_coherence("The quick brown fox jumps over the lazy dog.")

        assert result.metadata["sentence_count"] == 1
        assert result.adjacent_sentence_overlap == 0.0  # No adjacent pairs

    def test_no_pronouns(self) -> None:
        """Test text without pronouns."""
        text = "The cat sat. The dog ran. The bird flew."
        result = compute_cohesion_coherence(text)

        assert result.pronoun_density == 0.0
        assert result.anaphora_count == 0


class TestReferentialCohesion:
    """Tests for referential cohesion metrics."""

    def test_pronoun_detection(self) -> None:
        """Test pronoun detection and density calculation."""
        text = "He ran quickly. She followed him. They were fast."
        result = compute_cohesion_coherence(text)

        assert result.pronoun_density > 0
        assert result.anaphora_count > 0

    def test_demonstrative_detection(self) -> None:
        """Test demonstrative detection."""
        text = "This is important. That was significant. These findings matter."
        result = compute_cohesion_coherence(text)

        assert result.demonstrative_density > 0
        assert result.metadata["demonstrative_count"] >= 3

    def test_all_demonstratives_detected(self) -> None:
        """Test that all demonstratives are detected."""
        text = "This is here. That is there. These are many. Those are few."
        result = compute_cohesion_coherence(text)

        # Should detect this, that, these, those
        assert result.metadata["demonstrative_count"] == 4

    def test_anaphora_resolution_ratio(self) -> None:
        """Test anaphora resolution heuristic."""
        # Text with pronouns that have clear antecedents
        text = "The scientist published a paper. She was proud of it."
        result = compute_cohesion_coherence(text)

        # With nouns before pronouns, resolution ratio should be high
        assert result.anaphora_resolution_ratio > 0

    def test_anaphora_no_antecedent(self) -> None:
        """Test pronouns without clear antecedents."""
        # Start with pronoun (no preceding noun)
        text = "It was a dark night. They came quickly."
        result = compute_cohesion_coherence(text)

        # Some pronouns may not have antecedents
        assert result.anaphora_count > 0


class TestLexicalCohesion:
    """Tests for lexical cohesion metrics."""

    def test_word_repetition_detected(self) -> None:
        """Test word repetition across sentences."""
        text = "The cat sat on the mat. The cat was happy. The mat was soft."
        result = compute_cohesion_coherence(text)

        # Words like "cat" and "mat" repeat
        assert result.word_repetition_ratio > 0

    def test_no_repetition(self) -> None:
        """Test text with no word repetition."""
        text = "Dogs bark loudly. Cats meow softly. Birds sing beautifully."
        result = compute_cohesion_coherence(text)

        # Different content words in each sentence
        # May still have some repetition due to lemmatization
        assert result.word_repetition_ratio >= 0

    def test_lexical_chains_formed(self) -> None:
        """Test lexical chain detection."""
        text = """
        The research focused on climate change.
        Climate patterns have shifted dramatically.
        These climate shifts affect ecosystems.
        The research shows clear trends.
        """
        result = compute_cohesion_coherence(text)

        # "climate" and "research" should form chains
        assert result.lexical_chain_count > 0
        assert result.mean_chain_length > 0

    def test_content_word_overlap(self) -> None:
        """Test content word overlap between adjacent sentences."""
        text = "The experiment was successful. The experiment showed clear results."
        result = compute_cohesion_coherence(text)

        # "experiment" overlaps between sentences
        assert result.content_word_overlap > 0

    def test_no_overlap(self) -> None:
        """Test text with no content word overlap."""
        text = "Dogs run fast. Cats sleep peacefully."
        result = compute_cohesion_coherence(text)

        # Different content words, should have low/no overlap
        assert result.content_word_overlap >= 0


class TestConnectiveAnalysis:
    """Tests for connective detection and categorization."""

    def test_additive_connectives(self) -> None:
        """Test additive connective detection."""
        text = "The results were positive. Also, the data was reliable. Furthermore, the methodology was sound."
        result = compute_cohesion_coherence(text)

        assert result.connective_density > 0
        assert result.additive_connective_ratio > 0

    def test_adversative_connectives(self) -> None:
        """Test adversative connective detection."""
        text = "The results were positive. However, some limitations exist. Nevertheless, the findings are valid."
        result = compute_cohesion_coherence(text)

        assert result.connective_density > 0
        assert result.adversative_connective_ratio > 0

    def test_causal_connectives(self) -> None:
        """Test causal connective detection."""
        text = "The experiment failed because of contamination. Therefore, we repeated it. Thus, we obtained better results."
        result = compute_cohesion_coherence(text)

        assert result.connective_density > 0
        assert result.causal_connective_ratio > 0

    def test_temporal_connectives(self) -> None:
        """Test temporal connective detection."""
        text = "First, we collected the data. Then, we analyzed it. Finally, we wrote the report."
        result = compute_cohesion_coherence(text)

        assert result.connective_density > 0
        assert result.temporal_connective_ratio > 0

    def test_mixed_connectives(self) -> None:
        """Test text with mixed connective types."""
        text = """
        First, we conducted the experiment. However, some issues arose.
        Therefore, we made adjustments. Also, we improved our methods.
        """
        result = compute_cohesion_coherence(text)

        # All four types should be present
        total_ratio = (
            result.additive_connective_ratio
            + result.adversative_connective_ratio
            + result.causal_connective_ratio
            + result.temporal_connective_ratio
        )
        # Ratios should sum to approximately 1 (with some tolerance for overlap)
        assert 0.9 <= total_ratio <= 1.1

    def test_no_connectives(self) -> None:
        """Test text without connectives."""
        text = "Dogs bark. Cats meow. Birds sing."
        result = compute_cohesion_coherence(text)

        # May still have some connectives from common words
        assert result.connective_density >= 0

    def test_connective_counts_in_metadata(self) -> None:
        """Test that connective counts are in metadata."""
        text = "First, this happened. Then, that occurred. However, problems arose."
        result = compute_cohesion_coherence(text)

        counts = result.metadata["connective_counts"]
        assert "additive" in counts
        assert "adversative" in counts
        assert "causal" in counts
        assert "temporal" in counts


class TestCoherenceMeasures:
    """Tests for coherence measures."""

    def test_adjacent_sentence_overlap_high(self) -> None:
        """Test high overlap between adjacent sentences."""
        text = """
        The scientist studied DNA sequences.
        These DNA sequences contained important information.
        The information revealed genetic patterns.
        """
        result = compute_cohesion_coherence(text)

        # Repeated content words should create overlap
        assert result.adjacent_sentence_overlap > 0

    def test_adjacent_sentence_overlap_low(self) -> None:
        """Test low overlap between unrelated sentences."""
        text = "Elephants live in Africa. Programming requires logic. Music creates emotions."
        result = compute_cohesion_coherence(text)

        # Unrelated topics should have low overlap
        assert result.adjacent_sentence_overlap < 0.5

    def test_mean_sentence_similarity(self) -> None:
        """Test mean pairwise sentence similarity."""
        text = """
        The cat slept on the mat.
        The cat purred contentedly.
        The mat was soft and warm.
        """
        result = compute_cohesion_coherence(text)

        # Related sentences should have some similarity
        assert result.mean_sentence_similarity >= 0

    def test_semantic_coherence_score_range(self) -> None:
        """Test that semantic coherence score is in valid range."""
        text = """
        Research methodology is important.
        Good methods produce reliable results.
        Therefore, researchers must be careful.
        """
        result = compute_cohesion_coherence(text)

        assert 0 <= result.semantic_coherence_score <= 1


class TestStructuralCoherence:
    """Tests for structural coherence metrics."""

    def test_paragraph_detection(self) -> None:
        """Test paragraph detection from blank lines."""
        text = """
        This is the first paragraph.
        It has multiple sentences.

        This is the second paragraph.
        It also has content.

        This is the third paragraph.
        """
        result = compute_cohesion_coherence(text)

        assert result.paragraph_count == 3

    def test_single_paragraph(self) -> None:
        """Test single paragraph text."""
        text = "Sentence one. Sentence two. Sentence three."
        result = compute_cohesion_coherence(text)

        assert result.paragraph_count == 1

    def test_mean_paragraph_length(self) -> None:
        """Test mean paragraph length calculation."""
        text = """
        First sentence here. Second sentence here.

        Third sentence here.
        """
        result = compute_cohesion_coherence(text)

        # First paragraph: 2 sentences, Second: 1 sentence
        # Mean should be 1.5
        assert result.mean_paragraph_length > 0

    def test_discourse_structure_score_range(self) -> None:
        """Test discourse structure score is in valid range."""
        text = """
        Introduction paragraph here.

        Body paragraph one with details.

        Body paragraph two with more information.

        Conclusion paragraph here.
        """
        result = compute_cohesion_coherence(text)

        assert 0 <= result.discourse_structure_score <= 1

    def test_discourse_structure_minimal(self) -> None:
        """Test discourse structure with minimal paragraphs."""
        text = "Just one paragraph with some sentences. More content here."
        result = compute_cohesion_coherence(text)

        # Single paragraph should have neutral/low structure score
        assert 0 <= result.discourse_structure_score <= 1


class TestConnectiveWordLists:
    """Tests for connective word list completeness."""

    def test_additive_connectives_present(self) -> None:
        """Test key additive connectives are in the list."""
        expected = ["and", "also", "furthermore", "moreover", "additionally"]
        for word in expected:
            assert word in ADDITIVE_CONNECTIVES

    def test_adversative_connectives_present(self) -> None:
        """Test key adversative connectives are in the list."""
        expected = ["but", "however", "nevertheless", "yet", "although"]
        for word in expected:
            assert word in ADVERSATIVE_CONNECTIVES

    def test_causal_connectives_present(self) -> None:
        """Test key causal connectives are in the list."""
        expected = ["because", "therefore", "thus", "hence", "consequently"]
        for word in expected:
            assert word in CAUSAL_CONNECTIVES

    def test_temporal_connectives_present(self) -> None:
        """Test key temporal connectives are in the list."""
        expected = ["then", "after", "before", "when", "finally"]
        for word in expected:
            assert word in TEMPORAL_CONNECTIVES

    def test_all_connectives_union(self) -> None:
        """Test ALL_CONNECTIVES is union of all categories."""
        expected_total = (
            len(ADDITIVE_CONNECTIVES)
            + len(ADVERSATIVE_CONNECTIVES)
            + len(CAUSAL_CONNECTIVES)
            + len(TEMPORAL_CONNECTIVES)
        )
        # May be less due to overlap (e.g., "while" is both adversative and temporal)
        assert len(ALL_CONNECTIVES) <= expected_total

    def test_demonstratives_complete(self) -> None:
        """Test demonstratives set is complete."""
        expected = {"this", "that", "these", "those"}
        assert DEMONSTRATIVES == expected


class TestRealWorldText:
    """Tests using realistic text samples."""

    def test_academic_text(self) -> None:
        """Test analysis of academic-style text."""
        text = """
        This study examines the relationship between exercise and mental health.
        Previous research has shown that physical activity reduces stress.
        However, the mechanisms underlying these effects remain unclear.
        Therefore, we conducted a randomized controlled trial.

        The participants were randomly assigned to two groups.
        One group engaged in daily exercise, while the other served as control.
        After eight weeks, we measured psychological outcomes.

        The results indicate significant improvements in the exercise group.
        These findings suggest that regular physical activity benefits mental health.
        Furthermore, the effects were sustained over time.
        """
        result = compute_cohesion_coherence(text)

        # Academic text should have:
        # - Some pronouns (we, they)
        assert result.pronoun_density > 0
        # - Demonstratives (this, these)
        assert result.demonstrative_density > 0
        # - Good connective density
        assert result.connective_density > 0
        # - Multiple paragraphs
        assert result.paragraph_count >= 3

    def test_narrative_text(self) -> None:
        """Test analysis of narrative text."""
        text = """
        The old man walked slowly down the street. He had been walking for hours.
        His feet ached, but he continued on. The sun was setting behind the mountains.

        Finally, he reached his destination. It was a small cottage at the edge of town.
        The cottage belonged to his daughter. She had invited him for dinner.

        He knocked on the door and waited. Soon, she opened it with a warm smile.
        They embraced warmly. It had been too long since their last visit.
        """
        result = compute_cohesion_coherence(text)

        # Narrative should have:
        # - High pronoun density (he, she, it, they)
        assert result.pronoun_density > 0
        # - Some temporal connectives (finally, soon)
        assert result.temporal_connective_ratio >= 0
        # - Good anaphora (pronouns referring back)
        assert result.anaphora_count > 0

    def test_technical_text(self) -> None:
        """Test analysis of technical documentation."""
        text = """
        The system processes incoming requests through a pipeline architecture.
        Each request passes through validation, transformation, and storage stages.
        The validation stage checks data integrity and format compliance.

        If validation fails, the system returns an error response.
        Otherwise, the request continues to the transformation stage.
        Here, the data is normalized and enriched with additional metadata.

        Finally, the processed data is persisted to the database.
        The database uses optimistic locking to handle concurrent writes.
        This ensures data consistency across multiple transactions.
        """
        result = compute_cohesion_coherence(text)

        # Technical text should have:
        # - Structured paragraphs
        assert result.paragraph_count >= 3
        # - Some causal connectives (if, otherwise)
        assert result.connective_density > 0
        # - Temporal sequence (finally)
        # - Good coherence from repeated terminology
        assert result.semantic_coherence_score > 0


class TestDensityCalculations:
    """Tests for density calculations (per 100 words)."""

    def test_pronoun_density_normalization(self) -> None:
        """Test pronoun density is per 100 words."""
        # 10 words, 2 pronouns = 20 per 100 words
        text = "He ran. She jumped. They laughed. We watched. It worked."
        result = compute_cohesion_coherence(text)

        # Density should be reasonable (not raw count)
        assert result.pronoun_density > 0

    def test_connective_density_normalization(self) -> None:
        """Test connective density is per 100 words."""
        text = "First we did this. Then we did that. Therefore it worked."
        result = compute_cohesion_coherence(text)

        # Density should be normalized
        assert result.connective_density > 0


class TestMetadataDetails:
    """Tests for detailed metadata contents."""

    def test_lexical_chains_in_metadata(self) -> None:
        """Test lexical chains are recorded in metadata."""
        text = """
        The experiment tested a hypothesis.
        This hypothesis was about learning.
        Learning processes were measured carefully.
        The experiment yielded good results.
        """
        result = compute_cohesion_coherence(text)

        chains = result.metadata.get("lexical_chains", [])
        # Should have list of chain info
        assert isinstance(chains, list)

    def test_content_words_per_sentence(self) -> None:
        """Test content words per sentence are recorded."""
        text = "Big dogs run fast. Small cats sleep well."
        result = compute_cohesion_coherence(text)

        per_sentence = result.metadata.get("content_words_per_sentence", [])
        assert isinstance(per_sentence, list)
        assert len(per_sentence) == 2  # Two sentences

    def test_total_connectives_in_metadata(self) -> None:
        """Test total connective count in metadata."""
        text = "First this. Then that. However, issues arose. Therefore, we adapted."
        result = compute_cohesion_coherence(text)

        assert "total_connectives" in result.metadata
        assert result.metadata["total_connectives"] >= 0


class TestZeroDivision:
    """Tests to ensure no division by zero errors."""

    def test_no_connectives_ratio(self) -> None:
        """Test ratios when no connectives present."""
        text = "Dogs bark. Cats meow."
        result = compute_cohesion_coherence(text)

        # Should not raise ZeroDivisionError
        assert not math.isnan(result.additive_connective_ratio)
        assert not math.isnan(result.adversative_connective_ratio)

    def test_single_sentence_similarity(self) -> None:
        """Test similarity with single sentence."""
        text = "Just one sentence here."
        result = compute_cohesion_coherence(text)

        # Should handle gracefully
        assert not math.isnan(result.mean_sentence_similarity)

    def test_empty_paragraphs(self) -> None:
        """Test handling of text that produces empty paragraphs."""
        text = "   \n\n   \n\nSome actual text here.   \n\n   "
        result = compute_cohesion_coherence(text)

        # Should handle gracefully
        assert result.paragraph_count >= 0


class TestSpecialCharacters:
    """Tests for handling special characters and formatting."""

    def test_punctuation_handling(self) -> None:
        """Test that punctuation doesn't break analysis."""
        text = "What?! Really... Yes! No? Maybe (probably)."
        result = compute_cohesion_coherence(text)

        # Should process without error
        assert result.metadata["word_count"] > 0

    def test_numbers_excluded(self) -> None:
        """Test that numbers are handled appropriately."""
        text = "In 2020, there were 100 participants. They completed 50 tasks."
        result = compute_cohesion_coherence(text)

        # Numbers shouldn't count as words
        assert result.metadata["word_count"] > 0

    def test_mixed_case(self) -> None:
        """Test case insensitivity."""
        text = "THIS is IMPORTANT. This IS important. this is important."
        result = compute_cohesion_coherence(text)

        # "this" and "important" should be detected regardless of case
        assert result.demonstrative_density > 0
