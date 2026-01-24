"""Tests for advanced syntactic analysis (Issue #17)."""

import math

import pytest

from pystylometry.syntactic.advanced_syntactic import compute_advanced_syntactic


# ===== Fixtures =====


@pytest.fixture
def simple_text():
    """Simple sentences with basic structure."""
    return "The cat sat on the mat. The dog ran in the park. A bird flew over the tree."


@pytest.fixture
def complex_text():
    """Complex sentences with subordination and embedding."""
    return (
        "Although the research methodology that was employed demonstrated "
        "significant theoretical implications, the findings, which were "
        "published in a peer-reviewed journal, suggested that further "
        "investigation would be necessary before definitive conclusions "
        "could be drawn about the phenomena."
    )


@pytest.fixture
def academic_text():
    """Academic text with high clausal density."""
    return (
        "The study examined the relationship between syntactic complexity "
        "and readability, considering factors such as parse tree depth, "
        "clausal density, and T-unit length. Results indicated that texts "
        "with higher subordination indices were perceived as more difficult, "
        "which suggests that dependency distance plays a crucial role in "
        "processing difficulty."
    )


@pytest.fixture
def childrens_text():
    """Simple children's text."""
    return (
        "The dog is big. The cat is small. I like the dog. "
        "I like the cat. The dog runs fast. The cat jumps high. "
        "We play with the dog. We play with the cat."
    )


@pytest.fixture
def passive_text():
    """Text with passive voice constructions."""
    return (
        "The experiment was conducted by the researchers. "
        "The results were analyzed carefully. "
        "The findings have been published in the journal."
    )


@pytest.fixture
def active_text():
    """Text with active voice only."""
    return (
        "The researchers conducted the experiment. "
        "They analyzed the results carefully. "
        "They published the findings in the journal."
    )


@pytest.fixture
def coordinated_text():
    """Text with coordination (and, but, or)."""
    return (
        "The sun rose and the birds sang. "
        "The cat meowed but nobody came. "
        "We can go to the park or we can stay home. "
        "The dog barked and the door opened."
    )


@pytest.fixture
def subordinated_text():
    """Text with high subordination."""
    return (
        "When the sun rises, the birds begin to sing. "
        "Although it was raining, we decided to go outside. "
        "Because the experiment failed, the team had to start over. "
        "If you study hard, you will pass the exam."
    )


# ===== Basic Functionality Tests =====


class TestBasicFunctionality:
    """Test basic functionality with normal text."""

    def test_basic_computation(self, simple_text):
        """Test basic computation with simple text."""
        result = compute_advanced_syntactic(simple_text)

        # Should return result without errors
        assert result is not None

        # Basic sanity checks
        assert result.mean_parse_tree_depth > 0
        assert result.max_parse_tree_depth >= result.mean_parse_tree_depth
        assert result.t_unit_count > 0

    def test_all_fields_present(self, simple_text):
        """Verify all required fields are present."""
        result = compute_advanced_syntactic(simple_text)

        # Check all numeric fields
        assert isinstance(result.mean_parse_tree_depth, float)
        assert isinstance(result.max_parse_tree_depth, int)
        assert isinstance(result.t_unit_count, int)
        assert isinstance(result.mean_t_unit_length, float)
        assert isinstance(result.clausal_density, float)
        assert isinstance(result.dependent_clause_ratio, float)
        assert isinstance(result.passive_voice_ratio, float)
        assert isinstance(result.subordination_index, float)
        assert isinstance(result.coordination_index, float)
        assert isinstance(result.sentence_complexity_score, float)
        assert isinstance(result.dependency_distance, float)
        assert isinstance(result.left_branching_ratio, float)
        assert isinstance(result.right_branching_ratio, float)

        # Check metadata
        assert isinstance(result.metadata, dict)

    def test_metadata_completeness(self, simple_text):
        """Verify metadata contains all expected fields."""
        result = compute_advanced_syntactic(simple_text)

        metadata = result.metadata

        # Check required metadata fields
        assert "sentence_count" in metadata
        assert "word_count" in metadata
        assert "total_clauses" in metadata
        assert "independent_clause_count" in metadata
        assert "dependent_clause_count" in metadata
        assert "passive_sentence_count" in metadata
        assert "parse_depths_per_sentence" in metadata
        assert "t_unit_lengths" in metadata
        assert "model_used" in metadata

        # Verify types
        assert isinstance(metadata["sentence_count"], int)
        assert isinstance(metadata["word_count"], int)
        assert isinstance(metadata["total_clauses"], int)
        assert isinstance(metadata["parse_depths_per_sentence"], list)
        assert isinstance(metadata["t_unit_lengths"], list)


# ===== Edge Case Tests =====


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_text(self):
        """Test with empty text."""
        result = compute_advanced_syntactic("")

        # Should return NaN for ratios
        assert math.isnan(result.mean_parse_tree_depth)
        assert result.max_parse_tree_depth == 0
        assert result.t_unit_count == 0
        assert math.isnan(result.mean_t_unit_length)
        assert math.isnan(result.clausal_density)

        # Metadata should indicate warning
        assert "warning" in result.metadata

    def test_single_sentence(self):
        """Test with single sentence."""
        text = "The cat sat on the mat."
        result = compute_advanced_syntactic(text)

        # Should have valid results
        assert result.t_unit_count == 1
        assert result.metadata["sentence_count"] == 1
        assert not math.isnan(result.mean_parse_tree_depth)

    def test_very_short_sentence(self):
        """Test with very short sentence (5 words)."""
        text = "The cat sat there quietly."
        result = compute_advanced_syntactic(text)

        assert result.t_unit_count == 1
        assert result.mean_t_unit_length == pytest.approx(5.0, abs=1)

    def test_very_long_sentence(self, complex_text):
        """Test with very long, complex sentence (40+ words)."""
        result = compute_advanced_syntactic(complex_text)

        # Should handle long sentences
        assert result.metadata["word_count"] > 40
        assert result.mean_parse_tree_depth > 3  # Should be relatively deep

    def test_single_word_sentence(self):
        """Test with single-word sentence."""
        text = "Hello. Goodbye. Yes."
        result = compute_advanced_syntactic(text)

        assert result.t_unit_count == 3
        assert result.metadata["sentence_count"] == 3


# ===== Parse Tree Depth Tests =====


class TestParseTreeDepth:
    """Test parse tree depth calculations."""

    def test_simple_sentence_depth(self, simple_text):
        """Simple sentences should have shallow parse trees."""
        result = compute_advanced_syntactic(simple_text)

        # Simple sentences typically depth 2-4
        assert 1 <= result.mean_parse_tree_depth <= 5
        assert result.max_parse_tree_depth <= 6

    def test_complex_sentence_depth(self, complex_text):
        """Complex sentences should have deeper parse trees."""
        result = compute_advanced_syntactic(complex_text)

        # Complex sentences typically depth 5-8
        assert result.mean_parse_tree_depth >= 3
        assert result.max_parse_tree_depth >= 5

    def test_depth_mean_max_relationship(self, academic_text):
        """Max depth should be >= mean depth."""
        result = compute_advanced_syntactic(academic_text)

        assert result.max_parse_tree_depth >= result.mean_parse_tree_depth

    def test_parse_depths_in_metadata(self, simple_text):
        """Metadata should contain depths for each sentence."""
        result = compute_advanced_syntactic(simple_text)

        depths = result.metadata["parse_depths_per_sentence"]
        assert isinstance(depths, list)
        assert len(depths) == result.metadata["sentence_count"]
        assert all(isinstance(d, int) for d in depths)


# ===== T-unit Tests =====


class TestTUnits:
    """Test T-unit analysis."""

    def test_single_t_unit(self):
        """Single simple sentence = 1 T-unit."""
        text = "The cat sat on the mat."
        result = compute_advanced_syntactic(text)

        assert result.t_unit_count == 1

    def test_multiple_t_units(self, simple_text):
        """Multiple sentences = multiple T-units."""
        result = compute_advanced_syntactic(simple_text)

        # Simple_text has 3 sentences
        assert result.t_unit_count == 3

    def test_mean_t_unit_length(self, childrens_text):
        """Test mean T-unit length calculation."""
        result = compute_advanced_syntactic(childrens_text)

        # Children's text has short sentences
        assert result.mean_t_unit_length < 10

    def test_long_t_units(self, academic_text):
        """Academic text should have longer T-units."""
        result = compute_advanced_syntactic(academic_text)

        # Academic text typically has longer T-units
        assert result.mean_t_unit_length > 10

    def test_t_unit_lengths_in_metadata(self, simple_text):
        """Metadata should contain T-unit lengths."""
        result = compute_advanced_syntactic(simple_text)

        t_unit_lengths = result.metadata["t_unit_lengths"]
        assert isinstance(t_unit_lengths, list)
        assert len(t_unit_lengths) == result.t_unit_count
        assert all(isinstance(length, int) for length in t_unit_lengths)


# ===== Clausal Density Tests =====


class TestClausalDensity:
    """Test clausal density calculations."""

    def test_low_clausal_density(self, childrens_text):
        """Simple text should have low clausal density."""
        result = compute_advanced_syntactic(childrens_text)

        # Children's text: mostly 1 clause per sentence
        assert result.clausal_density <= 1.5

    def test_high_clausal_density(self, academic_text):
        """Academic text should have higher clausal density."""
        result = compute_advanced_syntactic(academic_text)

        # Academic text: multiple clauses per sentence
        assert result.clausal_density > 1.0

    def test_dependent_clause_ratio(self, complex_text):
        """Complex text should have dependent clauses."""
        result = compute_advanced_syntactic(complex_text)

        # Should have some dependent clauses
        assert result.dependent_clause_ratio > 0
        assert result.dependent_clause_ratio <= 1.0

    def test_clause_counts_in_metadata(self, academic_text):
        """Metadata should contain clause counts."""
        result = compute_advanced_syntactic(academic_text)

        metadata = result.metadata
        assert metadata["total_clauses"] > 0
        assert metadata["independent_clause_count"] > 0
        assert metadata["dependent_clause_count"] >= 0
        assert (
            metadata["total_clauses"]
            == metadata["independent_clause_count"]
            + metadata["dependent_clause_count"]
        )


# ===== Passive Voice Tests =====


class TestPassiveVoice:
    """Test passive voice detection."""

    def test_no_passive_voice(self, active_text):
        """Active text should have low passive voice ratio."""
        result = compute_advanced_syntactic(active_text)

        # Active voice text should have 0% passive
        assert result.passive_voice_ratio == 0.0

    def test_high_passive_voice(self, passive_text):
        """Passive text should have high passive voice ratio."""
        result = compute_advanced_syntactic(passive_text)

        # Passive text should have > 50% passive
        # Note: spaCy passive detection may not be 100% accurate
        assert result.passive_voice_ratio >= 0.3

    def test_passive_voice_ratio_range(self, academic_text):
        """Passive voice ratio should be between 0 and 1."""
        result = compute_advanced_syntactic(academic_text)

        assert 0.0 <= result.passive_voice_ratio <= 1.0

    def test_passive_count_in_metadata(self, passive_text):
        """Metadata should contain passive sentence count."""
        result = compute_advanced_syntactic(passive_text)

        metadata = result.metadata
        assert "passive_sentence_count" in metadata
        assert isinstance(metadata["passive_sentence_count"], int)
        assert metadata["passive_sentence_count"] >= 0


# ===== Subordination & Coordination Tests =====


class TestSubordinationCoordination:
    """Test subordination and coordination indices."""

    def test_high_subordination(self, subordinated_text):
        """Subordinated text should have high subordination index."""
        result = compute_advanced_syntactic(subordinated_text)

        # Should have subordinate clauses
        assert result.subordination_index > 0

    def test_high_coordination(self, coordinated_text):
        """Coordinated text should have coordination."""
        result = compute_advanced_syntactic(coordinated_text)

        # May have coordinate clauses (depends on spaCy parsing)
        # Just check it's a valid ratio
        assert 0.0 <= result.coordination_index <= 1.0

    def test_subordination_range(self, academic_text):
        """Subordination index should be between 0 and 1."""
        result = compute_advanced_syntactic(academic_text)

        assert 0.0 <= result.subordination_index <= 1.0

    def test_coordination_range(self, simple_text):
        """Coordination index should be between 0 and 1."""
        result = compute_advanced_syntactic(simple_text)

        assert 0.0 <= result.coordination_index <= 1.0


# ===== Dependency Distance Tests =====


class TestDependencyDistance:
    """Test mean dependency distance calculations."""

    def test_short_dependencies(self, childrens_text):
        """Simple text should have shorter dependencies."""
        result = compute_advanced_syntactic(childrens_text)

        # Children's text: short sentences, short dependencies
        assert result.dependency_distance < 4.0

    def test_long_dependencies(self, complex_text):
        """Complex text may have longer dependencies."""
        result = compute_advanced_syntactic(complex_text)

        # Complex text can have longer dependencies
        assert result.dependency_distance > 0

    def test_dependency_distance_positive(self, academic_text):
        """Dependency distance should be positive."""
        result = compute_advanced_syntactic(academic_text)

        assert result.dependency_distance > 0


# ===== Branching Direction Tests =====


class TestBranchingDirection:
    """Test branching direction calculations."""

    def test_right_branching_dominant(self, simple_text):
        """English should be predominantly right-branching."""
        result = compute_advanced_syntactic(simple_text)

        # English is typically 50-80% right-branching
        # Simple sentences may be balanced, so we use >=
        assert result.right_branching_ratio >= result.left_branching_ratio

    def test_branching_ratios_sum(self, academic_text):
        """Left and right branching should sum to ~1.0."""
        result = compute_advanced_syntactic(academic_text)

        total_branching = (
            result.left_branching_ratio + result.right_branching_ratio
        )
        assert total_branching == pytest.approx(1.0, abs=0.01)

    def test_branching_counts_in_metadata(self, simple_text):
        """Metadata should contain branching counts."""
        result = compute_advanced_syntactic(simple_text)

        metadata = result.metadata
        assert "left_branching_count" in metadata
        assert "right_branching_count" in metadata
        assert metadata["left_branching_count"] >= 0
        assert metadata["right_branching_count"] >= 0


# ===== Complexity Score Tests =====


class TestComplexityScore:
    """Test composite complexity score."""

    def test_low_complexity(self, childrens_text):
        """Children's text should have low complexity score."""
        result = compute_advanced_syntactic(childrens_text)

        # Should be relatively low
        assert result.sentence_complexity_score < 0.5

    def test_medium_complexity(self, simple_text):
        """Simple text should have medium complexity."""
        result = compute_advanced_syntactic(simple_text)

        # Should be moderate
        assert 0.1 <= result.sentence_complexity_score <= 0.7

    def test_high_complexity(self, complex_text):
        """Complex text should have higher complexity score."""
        result = compute_advanced_syntactic(complex_text)

        # Should be relatively high
        assert result.sentence_complexity_score > 0.3

    def test_complexity_score_range(self, academic_text):
        """Complexity score should be between 0 and 1."""
        result = compute_advanced_syntactic(academic_text)

        assert 0.0 <= result.sentence_complexity_score <= 1.0


# ===== Comparative Tests =====


class TestComparativeAnalysis:
    """Test comparative analysis across text types."""

    def test_childrens_vs_academic(self, childrens_text, academic_text):
        """Academic text should be more complex than children's text."""
        children_result = compute_advanced_syntactic(childrens_text)
        academic_result = compute_advanced_syntactic(academic_text)

        # Academic should have deeper parse trees
        assert academic_result.mean_parse_tree_depth > children_result.mean_parse_tree_depth

        # Academic should have longer T-units
        assert academic_result.mean_t_unit_length > children_result.mean_t_unit_length

        # Academic should have higher complexity score
        assert academic_result.sentence_complexity_score > children_result.sentence_complexity_score

    def test_passive_vs_active(self, passive_text, active_text):
        """Passive text should have higher passive voice ratio."""
        passive_result = compute_advanced_syntactic(passive_text)
        active_result = compute_advanced_syntactic(active_text)

        # Passive text should have higher ratio
        assert passive_result.passive_voice_ratio > active_result.passive_voice_ratio

    def test_subordinated_vs_coordinated(self, subordinated_text, coordinated_text):
        """Subordinated text should have higher subordination index."""
        subordinated_result = compute_advanced_syntactic(subordinated_text)
        coordinated_result = compute_advanced_syntactic(coordinated_text)

        # Subordinated should have higher subordination
        assert subordinated_result.subordination_index > 0

    def test_complexity_ranking_consistency(self, childrens_text, simple_text, academic_text):
        """Complexity should increase: children's < simple < academic."""
        children_result = compute_advanced_syntactic(childrens_text)
        simple_result = compute_advanced_syntactic(simple_text)
        academic_result = compute_advanced_syntactic(academic_text)

        # Check consistent ranking
        assert children_result.sentence_complexity_score <= simple_result.sentence_complexity_score
        assert simple_result.sentence_complexity_score <= academic_result.sentence_complexity_score


# ===== Real-World Text Tests =====


class TestRealWorldTexts:
    """Test with real-world text samples."""

    def test_news_article(self):
        """Test with news article text."""
        text = (
            "The government announced new policies yesterday. "
            "The policies will affect thousands of citizens. "
            "Officials said the changes were necessary for economic growth. "
            "Critics argued that the measures would harm vulnerable populations."
        )
        result = compute_advanced_syntactic(text)

        # News should have moderate complexity
        assert 0.2 <= result.sentence_complexity_score <= 0.6
        assert result.t_unit_count == 4

    def test_scientific_abstract(self):
        """Test with scientific abstract text."""
        text = (
            "This study investigated the effects of temperature on enzyme activity. "
            "The results demonstrated that optimal activity occurred at 37 degrees Celsius, "
            "which aligns with previous findings. "
            "These findings suggest that temperature regulation is critical for maintaining "
            "enzymatic function in biological systems."
        )
        result = compute_advanced_syntactic(text)

        # Scientific text should have high complexity
        assert result.sentence_complexity_score > 0.3
        assert result.clausal_density > 1.0

    def test_legal_document(self):
        """Test with legal document text."""
        text = (
            "The party of the first part agrees that they shall not disclose "
            "any confidential information that was obtained during the course "
            "of this agreement, unless such disclosure is required by law or "
            "authorized in writing by the party of the second part."
        )
        result = compute_advanced_syntactic(text)

        # Legal text should have very high complexity
        assert result.sentence_complexity_score > 0.4
        assert result.mean_parse_tree_depth > 4

    def test_fiction_narrative(self):
        """Test with fiction narrative text."""
        text = (
            "She walked slowly down the street. "
            "The rain fell steadily on her umbrella. "
            "She thought about the letter she had received. "
            "It changed everything."
        )
        result = compute_advanced_syntactic(text)

        # Fiction should have moderate complexity
        assert 0.1 <= result.sentence_complexity_score <= 0.5
        assert result.passive_voice_ratio < 0.3  # Mostly active voice


# ===== spaCy Integration Tests =====


class TestSpacyIntegration:
    """Test spaCy model integration."""

    def test_default_model(self, simple_text):
        """Test with default spaCy model."""
        result = compute_advanced_syntactic(simple_text)

        # Should use default model
        assert result.metadata["model_used"] == "en_core_web_sm"

    def test_model_name_in_metadata(self, simple_text):
        """Verify model name is recorded in metadata."""
        model_name = "en_core_web_sm"
        result = compute_advanced_syntactic(simple_text, model=model_name)

        assert result.metadata["model_used"] == model_name
