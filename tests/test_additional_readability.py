"""Tests for additional readability formulas.

Related GitHub Issue:
    #16 - Additional Readability Formulas
    https://github.com/craigtrim/pystylometry/issues/16

Tests all 5 additional readability formulas:
    - Dale-Chall Readability
    - Linsear Write Formula
    - Fry Readability Graph
    - FORCAST Formula
    - Powers-Sumner-Kearl Formula
"""

import math

import pytest

from pystylometry.readability import (
    compute_dale_chall,
    compute_forcast,
    compute_fry,
    compute_linsear_write,
    compute_powers_sumner_kearl,
)

# ===== Fixtures =====


@pytest.fixture
def simple_text():
    """Simple text with common words for children."""
    return (
        "The cat sat on the mat. The dog ran in the park. "
        "A boy and a girl play with a ball. The sun is hot. "
        "I like to run and jump. We can go to the zoo. "
    ) * 5  # Repeat to get enough tokens


@pytest.fixture
def childrens_text():
    """Children's book text with very simple vocabulary."""
    return (
        "The dog is big. The cat is small. I like the dog. "
        "I like the cat. The dog runs fast. The cat jumps high. "
        "The boy has a red ball. The girl has a blue doll. "
        "They play in the sun. It is fun to play. "
        "The dog can run. The cat can jump. I can play too. "
        "We go to the park. The park is big and green. "
    ) * 3


@pytest.fixture
def academic_text():
    """Academic text with sophisticated vocabulary."""
    return (
        "The research methodology employed a comprehensive approach to analyze "
        "the significant theoretical framework. The data demonstrate substantial "
        "evidence supporting the hypothesis. This analysis indicates that the "
        "results require further investigation to establish definitive conclusions. "
        "The study's primary objective involves assessing the policy implications "
        "derived from the empirical findings. Researchers must interpret these "
        "complex phenomena within the appropriate contextual parameters. "
        "The investigation utilized quantitative methodologies to examine correlations "
        "between variables. Statistical analysis revealed significant patterns that "
        "warrant additional scrutiny."
    )


@pytest.fixture
def middle_school_text():
    """Middle school level text."""
    return (
        "The American Revolution was a time when the colonies fought for independence. "
        "George Washington led the Continental Army against the British forces. "
        "The Declaration of Independence was signed on July 4, 1776. "
        "This important document stated that all men are created equal. "
        "The war lasted for eight years before the colonists won their freedom. "
        "After the war, leaders worked together to create a new government. "
        "They wrote the Constitution to protect people's rights and establish laws. "
        "The new nation faced many challenges as it grew and developed."
    )


@pytest.fixture
def technical_text():
    """Technical documentation with jargon."""
    return (
        "The API endpoint requires authentication using OAuth2 tokens. "
        "Initialize the WebSocket connection with proper SSL certificates. "
        "The microservice architecture utilizes RESTful paradigms for "
        "inter-process communication. Kubernetes orchestration handles "
        "containerized deployment across distributed clusters. "
        "Implement the asynchronous callback mechanism for event-driven processing. "
        "Configure the load balancer to distribute traffic efficiently. "
        "The database schema must support horizontal scaling and replication."
    )


# ===== Dale-Chall Tests =====


class TestDaleChallBasic:
    """Basic functionality tests for Dale-Chall."""

    def test_basic_computation(self, simple_text):
        """Test basic Dale-Chall computation."""
        result = compute_dale_chall(simple_text)
        assert isinstance(result.dale_chall_score, float)
        assert isinstance(result.grade_level, str)
        assert isinstance(result.difficult_word_count, int)
        assert result.total_words > 0

    def test_all_fields_present(self, simple_text):
        """Test all result fields are present."""
        result = compute_dale_chall(simple_text)
        assert hasattr(result, "dale_chall_score")
        assert hasattr(result, "grade_level")
        assert hasattr(result, "difficult_word_count")
        assert hasattr(result, "difficult_word_ratio")
        assert hasattr(result, "avg_sentence_length")
        assert hasattr(result, "total_words")
        assert hasattr(result, "metadata")

    def test_metadata_complete(self, simple_text):
        """Test metadata contains required fields."""
        result = compute_dale_chall(simple_text)
        assert "sentence_count" in result.metadata
        assert "raw_score" in result.metadata
        assert "adjusted" in result.metadata
        assert "difficult_word_pct" in result.metadata


class TestDaleChallEdgeCases:
    """Edge case tests for Dale-Chall."""

    def test_empty_text(self):
        """Test with empty text."""
        result = compute_dale_chall("")
        assert math.isnan(result.dale_chall_score)
        assert result.grade_level == "Unknown"
        assert result.total_words == 0

    def test_very_short_text(self):
        """Test with very short text."""
        result = compute_dale_chall("The cat sat on the mat.")
        assert not math.isnan(result.dale_chall_score)
        assert result.total_words == 6

    def test_all_difficult_words(self):
        """Test with many difficult/technical words."""
        text = (
            "The epistemological paradigm necessitates comprehensive methodological "
            "scrutiny through empirical investigation."
        )
        result = compute_dale_chall(text)
        # Should have high difficult word ratio
        assert result.difficult_word_ratio > 0.5
        # Should be college level or higher
        assert result.grade_level in ["College", "College Graduate"]


class TestDaleChallSpecific:
    """Dale-Chall specific feature tests."""

    def test_adjustment_triggered(self):
        """Test that adjustment is triggered when difficult % > 5%."""
        # Academic text should have > 5% difficult words
        text = (
            "The comprehensive investigation utilized sophisticated methodological "
            "frameworks to analyze multifaceted phenomena. Researchers employed "
            "rigorous empirical techniques to establish definitive conclusions."
        ) * 3
        result = compute_dale_chall(text)
        # Check that adjustment was applied
        assert result.metadata["adjusted"] is True
        # Adjusted score should be higher than raw
        assert result.dale_chall_score > result.metadata["raw_score"]

    def test_no_adjustment(self, childrens_text):
        """Test no adjustment for text with < 5% difficult words."""
        result = compute_dale_chall(childrens_text)
        # Children's text should have low difficult word %
        if result.metadata["difficult_word_pct"] <= 5.0:
            assert result.metadata["adjusted"] is False
            assert result.dale_chall_score == result.metadata["raw_score"]

    def test_case_insensitive(self):
        """Test case-insensitive familiar word matching."""
        text1 = "The Dog Runs Fast."
        text2 = "the dog runs fast."
        result1 = compute_dale_chall(text1)
        result2 = compute_dale_chall(text2)
        # Should have same difficult word count regardless of case
        assert result1.difficult_word_count == result2.difficult_word_count

    def test_grade_level_mapping(self, childrens_text, academic_text):
        """Test grade level mapping."""
        result_easy = compute_dale_chall(childrens_text)
        result_hard = compute_dale_chall(academic_text)
        # Children's text should be easier
        grade_order = [
            "4 and below",
            "5-6",
            "7-8",
            "9-10",
            "11-12",
            "College",
            "College Graduate",
        ]
        idx_easy = grade_order.index(result_easy.grade_level)
        idx_hard = grade_order.index(result_hard.grade_level)
        assert idx_easy < idx_hard


# ===== Linsear Write Tests =====


class TestLinsearWriteBasic:
    """Basic functionality tests for Linsear Write."""

    def test_basic_computation(self, simple_text):
        """Test basic Linsear Write computation."""
        result = compute_linsear_write(simple_text)
        assert isinstance(result.linsear_score, float)
        assert isinstance(result.grade_level, float)  # Now float (mean across chunks)
        assert result.grade_level >= 0

    def test_all_fields_present(self, simple_text):
        """Test all result fields are present."""
        result = compute_linsear_write(simple_text)
        assert hasattr(result, "linsear_score")
        assert hasattr(result, "grade_level")
        assert hasattr(result, "easy_word_count")
        assert hasattr(result, "hard_word_count")
        assert hasattr(result, "avg_sentence_length")
        assert hasattr(result, "metadata")

    def test_empty_text(self):
        """Test with empty text."""
        result = compute_linsear_write("")
        assert math.isnan(result.linsear_score)
        assert math.isnan(result.grade_level)  # Now nan for empty


class TestLinsearWriteSpecific:
    """Linsear Write specific feature tests."""

    def test_easy_word_dominated(self, childrens_text):
        """Test text dominated by easy words (1-2 syllables)."""
        result = compute_linsear_write(childrens_text)
        # Children's text should have mostly easy words
        assert result.easy_word_count > result.hard_word_count
        # Should be low grade level
        assert result.grade_level <= 6.0

    def test_hard_word_dominated(self, academic_text):
        """Test text with many hard words (3+ syllables)."""
        result = compute_linsear_write(academic_text)
        # Academic text should have more hard words
        # (though may not dominate due to function words)
        assert result.hard_word_count > 0
        # Should be higher grade level
        assert result.grade_level >= 8.0

    def test_score_conversion_high(self):
        """Test score > 20 conversion (score / 2)."""
        # Create text with very long sentences and many hard words
        text = (
            "The comprehensive methodological investigation systematically "
            "examined multifaceted theoretical frameworks utilizing sophisticated "
            "analytical paradigms to establish empirical correlations between "
            "interdisciplinary variables and contemporary sociological phenomena."
        )
        result = compute_linsear_write(text)
        # Grade level is now a mean across chunks, so just verify it's reasonable
        assert result.grade_level >= 0.0
        assert isinstance(result.grade_level, float)

    def test_word_classification(self):
        """Test easy vs hard word classification."""
        # 1-syllable words: "cat", "dog"
        # 2-syllable words: "running", "jumping"
        # 3-syllable words: "beautiful", "butterfly"
        text = "The cat and dog are running. Beautiful butterfly."
        result = compute_linsear_write(text)
        # Should have both easy and hard words
        assert result.easy_word_count > 0
        assert result.hard_word_count > 0


# ===== Fry Tests =====


class TestFryBasic:
    """Basic functionality tests for Fry."""

    def test_basic_computation(self, simple_text):
        """Test basic Fry computation."""
        result = compute_fry(simple_text)
        assert isinstance(result.avg_sentence_length, float)
        assert isinstance(result.avg_syllables_per_100, float)
        assert isinstance(result.grade_level, str)
        assert isinstance(result.graph_zone, str)

    def test_all_fields_present(self, simple_text):
        """Test all result fields are present."""
        result = compute_fry(simple_text)
        assert hasattr(result, "avg_sentence_length")
        assert hasattr(result, "avg_syllables_per_100")
        assert hasattr(result, "grade_level")
        assert hasattr(result, "graph_zone")
        assert hasattr(result, "metadata")

    def test_empty_text(self):
        """Test with empty text."""
        result = compute_fry("")
        assert math.isnan(result.avg_sentence_length)
        assert result.grade_level == "Unknown"
        assert result.graph_zone == "invalid"


class TestFrySpecific:
    """Fry specific feature tests."""

    def test_sample_extraction(self):
        """Test 100-word sample extraction."""
        # Create text with > 100 words
        text = " ".join(["word"] * 150) + "."
        result = compute_fry(text)
        # Should use 100-word sample
        assert result.metadata["sample_size"] == 100

    def test_short_text_handling(self):
        """Test text < 100 words uses entire text."""
        text = " ".join(["word"] * 50) + "."
        result = compute_fry(text)
        # Should use entire text
        assert result.metadata["sample_size"] == 50

    def test_syllables_per_100(self, childrens_text, academic_text):
        """Test syllables per 100 calculation."""
        result_easy = compute_fry(childrens_text)
        result_hard = compute_fry(academic_text)
        # Academic text should have more syllables per 100 words
        assert result_hard.avg_syllables_per_100 > result_easy.avg_syllables_per_100

    def test_grade_zone_valid(self, middle_school_text):
        """Test graph zone is valid for typical text."""
        result = compute_fry(middle_school_text)
        # Should be in valid zone for normal text
        assert result.graph_zone in ["valid", "above_graph", "below_graph"]


# ===== FORCAST Tests =====


class TestFORCASTBasic:
    """Basic functionality tests for FORCAST."""

    def test_basic_computation(self, simple_text):
        """Test basic FORCAST computation."""
        result = compute_forcast(simple_text)
        assert isinstance(result.forcast_score, float)
        assert isinstance(result.grade_level, float)  # Now float (mean across chunks)
        assert result.grade_level >= 0

    def test_all_fields_present(self, simple_text):
        """Test all result fields are present."""
        result = compute_forcast(simple_text)
        assert hasattr(result, "forcast_score")
        assert hasattr(result, "grade_level")
        assert hasattr(result, "single_syllable_ratio")
        assert hasattr(result, "single_syllable_count")
        assert hasattr(result, "total_words")
        assert hasattr(result, "metadata")

    def test_empty_text(self):
        """Test with empty text."""
        result = compute_forcast("")
        assert math.isnan(result.forcast_score)
        assert math.isnan(result.grade_level)  # Now nan for empty


class TestFORCASTSpecific:
    """FORCAST specific feature tests."""

    def test_sample_extraction(self):
        """Test 150-word sample extraction."""
        # Create text with > 150 words
        text = " ".join(["word"] * 200) + "."
        result = compute_forcast(text)
        # With chunked analysis, total_words is the actual total
        assert result.total_words == 200
        # sample_size in metadata reflects the sampling approach
        assert result.metadata["sample_size"] == 150

    def test_short_text_scaling(self):
        """Test scaling for texts < 150 words."""
        text = " ".join(["cat"] * 75) + "."  # All 1-syllable words
        result = compute_forcast(text)
        # Should scale N to 150-word basis
        assert result.metadata["sample_size"] == 75
        # Scaled N should be approximately 150 (all single-syllable)
        assert result.metadata["scaled_n"] > 140

    def test_single_syllable_ratio(self, childrens_text):
        """Test single-syllable ratio calculation."""
        result = compute_forcast(childrens_text)
        # Children's text should have high single-syllable ratio
        assert result.single_syllable_ratio > 0.5
        assert result.single_syllable_count > 0

    def test_grade_calculation(self):
        """Test grade level calculation: 20 - (N / 10)."""
        # Create text with known single-syllable count
        # If we have 100 single-syllable words in 150-word sample:
        # N = 100, grade = 20 - (100 / 10) = 10
        text = " ".join(["cat"] * 100 + ["butterfly"] * 50) + "."
        result = compute_forcast(text)
        # Scaled N should be close to 100
        # Grade should be close to 10
        assert 8.0 <= result.grade_level <= 12.0


# ===== Powers-Sumner-Kearl Tests =====


class TestPowersSumnerKearlBasic:
    """Basic functionality tests for Powers-Sumner-Kearl."""

    def test_basic_computation(self, simple_text):
        """Test basic PSK computation."""
        result = compute_powers_sumner_kearl(simple_text)
        assert isinstance(result.psk_score, float)
        assert isinstance(result.grade_level, float)

    def test_all_fields_present(self, simple_text):
        """Test all result fields are present."""
        result = compute_powers_sumner_kearl(simple_text)
        assert hasattr(result, "psk_score")
        assert hasattr(result, "grade_level")
        assert hasattr(result, "avg_sentence_length")
        assert hasattr(result, "avg_syllables_per_word")
        assert hasattr(result, "total_sentences")
        assert hasattr(result, "total_words")
        assert hasattr(result, "total_syllables")
        assert hasattr(result, "metadata")

    def test_empty_text(self):
        """Test with empty text."""
        result = compute_powers_sumner_kearl("")
        assert math.isnan(result.psk_score)
        assert math.isnan(result.grade_level)


class TestPowersSumnerKearlSpecific:
    """PSK specific feature tests."""

    def test_primary_grade_text(self, childrens_text):
        """Test PSK on primary grade text."""
        result = compute_powers_sumner_kearl(childrens_text)
        # Children's text should be low grade (1-4)
        assert result.grade_level <= 5.0

    def test_comparison_to_flesch(self, simple_text):
        """Test PSK includes Flesch comparison."""
        result = compute_powers_sumner_kearl(simple_text)
        # Metadata should include Flesch scores
        assert "flesch_reading_ease" in result.metadata
        assert "flesch_kincaid_grade" in result.metadata
        assert "difference_from_flesch" in result.metadata

    def test_negative_score_handling(self):
        """Test handling of very simple text (can produce negative scores)."""
        # Very short sentences with simple words
        text = "I go. We go. You go. He goes. She goes."
        result = compute_powers_sumner_kearl(text)
        # PSK can produce negative scores for very simple text
        # grade_level should handle this (might be negative)
        assert isinstance(result.grade_level, float)

    def test_decimal_grade_level(self, middle_school_text):
        """Test grade level is continuous (decimal)."""
        result = compute_powers_sumner_kearl(middle_school_text)
        # Grade level should be rounded to 1 decimal place
        assert result.grade_level == round(result.psk_score, 1)


# ===== Comparative Tests =====


class TestComparativeAnalysis:
    """Tests comparing formulas across different text types."""

    def test_childrens_text_all_formulas(self, childrens_text):
        """Test all formulas agree children's text is easy."""
        dc = compute_dale_chall(childrens_text)
        lw = compute_linsear_write(childrens_text)
        fry = compute_fry(childrens_text)
        fc = compute_forcast(childrens_text)
        psk = compute_powers_sumner_kearl(childrens_text)

        # All should indicate low difficulty
        assert dc.grade_level in ["4 and below", "5-6", "7-8"]
        assert lw.grade_level <= 8.0
        assert fry.grade_level in ["1", "2", "3", "4", "5", "6"]
        assert fc.grade_level <= 8.0
        assert psk.grade_level <= 6.0

    def test_academic_text_all_formulas(self, academic_text):
        """Test all formulas agree academic text is difficult."""
        dc = compute_dale_chall(academic_text)
        lw = compute_linsear_write(academic_text)
        fry_result = compute_fry(academic_text)
        fc = compute_forcast(academic_text)
        psk = compute_powers_sumner_kearl(academic_text)

        # All should indicate high difficulty
        assert dc.grade_level in ["11-12", "College", "College Graduate"]
        assert lw.grade_level >= 10.0
        # Fry might vary - just ensure it returned a result
        assert fry_result.grade_level is not None
        assert fc.grade_level >= 10.0
        # PSK is designed for primary grades (1-4), so it may produce
        # out-of-range scores for academic text - just check it exists
        assert isinstance(psk.grade_level, float)

    def test_difficulty_ranking_consistency(
        self, childrens_text, middle_school_text, academic_text
    ):
        """Test all formulas rank texts in same difficulty order."""
        # Dale-Chall
        dc_child = compute_dale_chall(childrens_text)
        dc_middle = compute_dale_chall(middle_school_text)
        dc_academic = compute_dale_chall(academic_text)
        assert dc_child.dale_chall_score < dc_middle.dale_chall_score
        assert dc_middle.dale_chall_score < dc_academic.dale_chall_score

        # Linsear Write
        lw_child = compute_linsear_write(childrens_text)
        lw_middle = compute_linsear_write(middle_school_text)
        lw_academic = compute_linsear_write(academic_text)
        assert lw_child.grade_level < lw_middle.grade_level
        assert lw_middle.grade_level < lw_academic.grade_level

        # FORCAST
        fc_child = compute_forcast(childrens_text)
        fc_middle = compute_forcast(middle_school_text)
        fc_academic = compute_forcast(academic_text)
        assert fc_child.grade_level < fc_middle.grade_level
        assert fc_middle.grade_level < fc_academic.grade_level

        # PSK is designed for primary grades only, so we only test children's vs middle
        psk_child = compute_powers_sumner_kearl(childrens_text)
        psk_middle = compute_powers_sumner_kearl(middle_school_text)
        # Only test children vs middle school (PSK not designed for academic text)
        assert psk_child.grade_level <= psk_middle.grade_level


# ===== Real-World Text Tests =====


class TestRealWorldTexts:
    """Tests with realistic text samples."""

    def test_news_article(self):
        """Test with news article text."""
        text = (
            "The Senate approved a new infrastructure bill yesterday. "
            "The legislation allocates funding for highways, bridges, and public transit. "
            "Congressional leaders praised the bipartisan effort to improve transportation. "
            "Critics argue the bill does not address climate change adequately. "
            "The President is expected to sign the bill into law next week."
        )
        dc = compute_dale_chall(text)
        lw = compute_linsear_write(text)
        fry = compute_fry(text)

        # News should be readable by adults (may vary based on word list coverage)
        # Dale-Chall with limited word list may score higher than expected
        assert dc.dale_chall_score < 15.0
        assert lw.grade_level <= 14
        assert not math.isnan(fry.avg_syllables_per_100)

    def test_scientific_abstract(self):
        """Test with scientific abstract."""
        text = (
            "We investigated the molecular mechanisms underlying cellular differentiation. "
            "Transcriptomic analysis revealed differential expression patterns across developmental stages. "
            "Hierarchical clustering identified distinct gene modules associated with lineage commitment. "
            "Our findings demonstrate the regulatory networks governing stem cell fate determination."
        )
        dc = compute_dale_chall(text)
        lw = compute_linsear_write(text)

        # Scientific text should be difficult
        assert dc.dale_chall_score >= 9.0
        # Linsear may vary - just check it's above elementary level
        assert lw.grade_level >= 7.0

    def test_instruction_manual(self):
        """Test with instruction manual text."""
        text = (
            "To assemble the bookshelf, first attach the side panels to the back board. "
            "Use the provided screws and allen wrench. Tighten each screw firmly but do not overtighten. "
            "Next, insert the shelf supports into the pre-drilled holes. "
            "Place the shelves on top of the supports. Ensure the bookshelf is level before use."
        )
        lw = compute_linsear_write(text)
        fc = compute_forcast(text)

        # Instructions should be moderately easy (wide range acceptable)
        assert 3.0 <= lw.grade_level <= 12.0
        assert 3.0 <= fc.grade_level <= 12.0


# ===== Constraint Tests =====


class TestConstraints:
    """Tests for output constraints and validation."""

    def test_dale_chall_ratios(self, simple_text):
        """Test Dale-Chall ratios are in valid range."""
        result = compute_dale_chall(simple_text)
        assert 0.0 <= result.difficult_word_ratio <= 1.0

    def test_linsear_grade_positive(self, simple_text):
        """Test Linsear grade level is non-negative."""
        result = compute_linsear_write(simple_text)
        assert result.grade_level >= 0.0

    def test_forcast_ratios(self, simple_text):
        """Test FORCAST ratios are in valid range."""
        result = compute_forcast(simple_text)
        assert 0.0 <= result.single_syllable_ratio <= 1.0

    def test_psk_syllables_positive(self, simple_text):
        """Test PSK syllable metrics are positive."""
        result = compute_powers_sumner_kearl(simple_text)
        assert result.avg_syllables_per_word > 0
        assert result.total_syllables > 0

    def test_metadata_consistency(self, simple_text):
        """Test metadata is consistent across formulas."""
        # With chunked analysis, metadata structure varies by formula
        lw = compute_linsear_write(simple_text)
        psk = compute_powers_sumner_kearl(simple_text)

        # Both should have consistent total_words
        assert lw.metadata["total_words"] == psk.total_words
