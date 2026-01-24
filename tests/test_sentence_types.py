"""Tests for sentence type classification (Issue #18)."""

import math

import pytest

from pystylometry.syntactic.sentence_types import compute_sentence_types


# ===== Fixtures =====


@pytest.fixture
def simple_sentences():
    """Text with only simple sentences."""
    return "The cat sat. The dog ran. A bird flew."


@pytest.fixture
def compound_sentences():
    """Text with compound sentences."""
    return "I came and I saw. She laughed but he cried. We won or they lost."


@pytest.fixture
def complex_sentences():
    """Text with complex sentences."""
    return (
        "When I arrived, I saw her. "
        "Although it was raining, we went outside. "
        "Because the test failed, we had to restart."
    )


@pytest.fixture
def compound_complex_sentences():
    """Text with compound-complex sentences."""
    return (
        "When I called, she came and she stayed. "
        "Although we tried, we failed but we learned."
    )


@pytest.fixture
def mixed_structural():
    """Text with mixed structural types."""
    return (
        "The cat sat. "  # Simple
        "I came and I saw. "  # Compound
        "When I arrived, I saw her. "  # Complex
        "When I called, she came and she stayed."  # Compound-complex
    )


@pytest.fixture
def declarative_sentences():
    """Text with only declarative sentences."""
    return "The sky is blue. The grass is green. Water is wet."


@pytest.fixture
def interrogative_sentences():
    """Text with questions."""
    return "Is the sky blue? Are you ready? What is your name?"


@pytest.fixture
def imperative_sentences():
    """Text with commands."""
    return "Close the door. Look at the sky. Go to the store."


@pytest.fixture
def exclamatory_sentences():
    """Text with exclamations."""
    return "What a beautiful day! How wonderful! Amazing!"


@pytest.fixture
def mixed_functional():
    """Text with mixed functional types."""
    return (
        "The sky is blue. "  # Declarative
        "Is it raining? "  # Interrogative
        "Close the window. "  # Imperative
        "What a lovely day!"  # Exclamatory
    )


# ===== Basic Functionality Tests =====


class TestBasicFunctionality:
    """Test basic functionality with normal text."""

    def test_basic_computation(self, mixed_structural):
        """Test basic computation with mixed text."""
        result = compute_sentence_types(mixed_structural)

        # Should return result without errors
        assert result is not None
        assert result.total_sentences > 0

    def test_all_fields_present(self, mixed_structural):
        """Verify all required fields are present."""
        result = compute_sentence_types(mixed_structural)

        # Check structural ratio fields
        assert isinstance(result.simple_ratio, float)
        assert isinstance(result.compound_ratio, float)
        assert isinstance(result.complex_ratio, float)
        assert isinstance(result.compound_complex_ratio, float)

        # Check functional ratio fields
        assert isinstance(result.declarative_ratio, float)
        assert isinstance(result.interrogative_ratio, float)
        assert isinstance(result.imperative_ratio, float)
        assert isinstance(result.exclamatory_ratio, float)

        # Check count fields
        assert isinstance(result.simple_count, int)
        assert isinstance(result.compound_count, int)
        assert isinstance(result.complex_count, int)
        assert isinstance(result.compound_complex_count, int)
        assert isinstance(result.declarative_count, int)
        assert isinstance(result.interrogative_count, int)
        assert isinstance(result.imperative_count, int)
        assert isinstance(result.exclamatory_count, int)
        assert isinstance(result.total_sentences, int)

        # Check diversity metrics
        assert isinstance(result.structural_diversity, float)
        assert isinstance(result.functional_diversity, float)

        # Check metadata
        assert isinstance(result.metadata, dict)

    def test_metadata_completeness(self, mixed_structural):
        """Verify metadata contains all expected fields."""
        result = compute_sentence_types(mixed_structural)

        metadata = result.metadata

        # Check required metadata fields
        assert "sentence_count" in metadata
        assert "sentence_classifications" in metadata
        assert "clause_counts_per_sentence" in metadata
        assert "structural_counts" in metadata
        assert "functional_counts" in metadata
        assert "model_used" in metadata


# ===== Edge Case Tests =====


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_text(self):
        """Test with empty text."""
        result = compute_sentence_types("")

        # Should return NaN for ratios
        assert math.isnan(result.simple_ratio)
        assert math.isnan(result.declarative_ratio)
        assert result.total_sentences == 0
        assert result.simple_count == 0

    def test_single_sentence(self):
        """Test with single sentence."""
        text = "The cat sat on the mat."
        result = compute_sentence_types(text)

        # Should have one sentence
        assert result.total_sentences == 1

        # One type should be 100%, others 0%
        assert result.simple_ratio == 1.0
        assert result.compound_ratio == 0.0
        assert result.declarative_ratio == 1.0

    def test_very_short_text(self):
        """Test with 2-3 sentences."""
        text = "Hello. How are you? Good."
        result = compute_sentence_types(text)

        assert result.total_sentences == 3
        assert result.simple_count + result.compound_count + result.complex_count + result.compound_complex_count == 3

    def test_homogeneous_structural(self, simple_sentences):
        """Test with all same structural type."""
        result = compute_sentence_types(simple_sentences)

        # All should be simple
        assert result.simple_ratio == 1.0
        assert result.compound_ratio == 0.0
        assert result.complex_ratio == 0.0
        assert result.compound_complex_ratio == 0.0

    def test_homogeneous_functional(self, declarative_sentences):
        """Test with all same functional type."""
        result = compute_sentence_types(declarative_sentences)

        # All should be declarative
        assert result.declarative_ratio == 1.0
        assert result.interrogative_ratio == 0.0
        assert result.imperative_ratio == 0.0
        assert result.exclamatory_ratio == 0.0


# ===== Structural Classification Tests =====


class TestStructuralClassification:
    """Test structural classification (simple, compound, complex, compound-complex)."""

    def test_simple_sentences_only(self, simple_sentences):
        """Test text with only simple sentences."""
        result = compute_sentence_types(simple_sentences)

        # Should have high simple ratio
        assert result.simple_ratio >= 0.8
        assert result.simple_count >= 2

    def test_compound_sentences_only(self, compound_sentences):
        """Test text with compound sentences."""
        result = compute_sentence_types(compound_sentences)

        # Should have compound sentences
        assert result.compound_count >= 1
        assert result.compound_ratio > 0

    def test_complex_sentences_only(self, complex_sentences):
        """Test text with complex sentences."""
        result = compute_sentence_types(complex_sentences)

        # Should have complex sentences
        assert result.complex_count >= 2
        assert result.complex_ratio >= 0.5

    def test_compound_complex_sentences(self, compound_complex_sentences):
        """Test text with compound-complex sentences."""
        result = compute_sentence_types(compound_complex_sentences)

        # Should have compound-complex sentences
        assert result.compound_complex_count >= 1

    def test_mixed_structural_types(self, mixed_structural):
        """Test text with all structural types."""
        result = compute_sentence_types(mixed_structural)

        # Should have all types represented
        assert result.simple_count > 0
        assert result.compound_count > 0
        assert result.complex_count > 0

    def test_clause_counting_accuracy(self, mixed_structural):
        """Test clause counting in metadata."""
        result = compute_sentence_types(mixed_structural)

        clause_counts = result.metadata["clause_counts_per_sentence"]
        assert isinstance(clause_counts, list)
        assert len(clause_counts) == result.total_sentences
        assert all(isinstance(count, tuple) for count in clause_counts)

    def test_coordinating_conjunction_detection(self, compound_sentences):
        """Test that coordinating conjunctions are detected."""
        result = compute_sentence_types(compound_sentences)

        # Should detect compound sentences with "and", "but", "or"
        assert result.compound_count > 0

    def test_dependent_clause_detection(self, complex_sentences):
        """Test that dependent clauses are detected."""
        result = compute_sentence_types(complex_sentences)

        # Should detect complex sentences with dependent clauses
        assert result.complex_count > 0


# ===== Functional Classification Tests =====


class TestFunctionalClassification:
    """Test functional classification (declarative, interrogative, imperative, exclamatory)."""

    def test_declarative_only(self, declarative_sentences):
        """Test text with only declarative sentences."""
        result = compute_sentence_types(declarative_sentences)

        assert result.declarative_ratio == 1.0
        assert result.declarative_count == result.total_sentences

    def test_interrogative_only(self, interrogative_sentences):
        """Test text with only questions."""
        result = compute_sentence_types(interrogative_sentences)

        assert result.interrogative_count >= 2
        assert result.interrogative_ratio >= 0.8

    def test_imperative_only(self, imperative_sentences):
        """Test text with only commands."""
        result = compute_sentence_types(imperative_sentences)

        assert result.imperative_count >= 2
        assert result.imperative_ratio >= 0.5  # spaCy may not catch all

    def test_exclamatory_only(self, exclamatory_sentences):
        """Test text with only exclamations."""
        result = compute_sentence_types(exclamatory_sentences)

        assert result.exclamatory_count >= 2
        assert result.exclamatory_ratio >= 0.5

    def test_mixed_functional_types(self, mixed_functional):
        """Test text with all functional types."""
        result = compute_sentence_types(mixed_functional)

        # Should have multiple types
        types_present = sum([
            result.declarative_count > 0,
            result.interrogative_count > 0,
            result.imperative_count > 0 or result.exclamatory_count > 0,  # Either imperative or exclamatory
        ])
        assert types_present >= 2

    def test_question_mark_detection(self, interrogative_sentences):
        """Test that question marks are detected."""
        result = compute_sentence_types(interrogative_sentences)

        # All sentences end with ?, should all be interrogative
        assert result.interrogative_count >= 2

    def test_exclamation_mark_detection(self, exclamatory_sentences):
        """Test that exclamation marks are detected."""
        result = compute_sentence_types(exclamatory_sentences)

        # All sentences end with !, should be exclamatory or imperative
        assert result.exclamatory_count + result.imperative_count >= 2

    def test_imperative_structure_detection(self, imperative_sentences):
        """Test that imperative structure is detected."""
        result = compute_sentence_types(imperative_sentences)

        # Should detect some imperatives
        assert result.imperative_count >= 1


# ===== Clause Counting Tests =====


class TestClauseCounting:
    """Test clause counting accuracy."""

    def test_independent_clause_count(self):
        """Test counting independent clauses."""
        # Simple: 1 independent
        simple = "The cat sat."
        result = compute_sentence_types(simple)
        clause_counts = result.metadata["clause_counts_per_sentence"][0]
        assert clause_counts[0] == 1  # 1 independent

    def test_dependent_clause_count(self):
        """Test counting dependent clauses."""
        # Complex: 1 independent, 1+ dependent
        complex_text = "When I arrived, I saw her."
        result = compute_sentence_types(complex_text)
        clause_counts = result.metadata["clause_counts_per_sentence"][0]
        assert clause_counts[0] == 1  # 1 independent
        assert clause_counts[1] >= 1  # At least 1 dependent

    def test_coordinated_clauses(self):
        """Test counting coordinated independent clauses."""
        # Compound: 2+ independent
        compound = "I came and I saw."
        result = compute_sentence_types(compound)
        clause_counts = result.metadata["clause_counts_per_sentence"][0]
        assert clause_counts[0] >= 2  # 2+ independent

    def test_multiple_dependent_clauses(self):
        """Test counting multiple dependent clauses."""
        # Multiple dependent clauses
        text = "Although it was late when I arrived, I saw her."
        result = compute_sentence_types(text)
        clause_counts = result.metadata["clause_counts_per_sentence"][0]
        assert clause_counts[1] >= 1  # At least 1 dependent


# ===== Diversity Metric Tests =====


class TestDiversityMetrics:
    """Test Shannon entropy diversity metrics."""

    def test_zero_diversity_structural(self, simple_sentences):
        """Test zero diversity (all same type)."""
        result = compute_sentence_types(simple_sentences)

        # All simple sentences = zero diversity
        assert result.structural_diversity == 0.0

    def test_low_diversity_structural(self):
        """Test low diversity (mostly one type)."""
        text = "Simple. Simple. Simple. When complex, it happens."
        result = compute_sentence_types(text)

        # Mostly simple, some complex = low diversity
        assert 0 < result.structural_diversity < 1.0

    def test_high_diversity_structural(self, mixed_structural):
        """Test high diversity (balanced distribution)."""
        result = compute_sentence_types(mixed_structural)

        # Multiple types = higher diversity
        assert result.structural_diversity > 0.5

    def test_shannon_entropy_calculation(self, mixed_functional):
        """Test Shannon entropy calculation."""
        result = compute_sentence_types(mixed_functional)

        # Should have positive functional diversity
        assert result.functional_diversity > 0


# ===== Genre-Specific Tests =====


class TestGenreSpecific:
    """Test genre-specific patterns."""

    def test_academic_text(self):
        """Academic text should have high complex ratio."""
        text = (
            "The research examined the relationship between variables. "
            "Although the data were limited, the findings suggested significant trends. "
            "When analyzed further, the results indicated stronger correlations."
        )
        result = compute_sentence_types(text)

        # Academic: high complex
        assert result.complex_ratio >= 0.3

    def test_fiction_text(self):
        """Fiction should have mixed types."""
        text = (
            "She walked down the street. "
            "The rain fell and the wind blew. "
            "When she reached the corner, she stopped. "
            "What a beautiful sight!"
        )
        result = compute_sentence_types(text)

        # Fiction: mixed types
        types_present = sum([
            result.simple_count > 0,
            result.compound_count > 0,
            result.complex_count > 0,
        ])
        assert types_present >= 2

    def test_news_text(self):
        """News should have simple/compound dominant."""
        text = (
            "The mayor announced new policies yesterday. "
            "The changes will affect thousands of residents. "
            "Officials said the measures were necessary. "
            "Critics argued against the proposal."
        )
        result = compute_sentence_types(text)

        # News: mostly simple and declarative
        assert result.simple_ratio + result.compound_ratio >= 0.5
        assert result.declarative_ratio >= 0.9

    def test_instructional_text(self):
        """Instructional should have high imperative."""
        text = (
            "Open the package carefully. "
            "Remove the contents. "
            "Place the item on a flat surface. "
            "Connect the power cord."
        )
        result = compute_sentence_types(text)

        # Instructional: high imperative
        assert result.imperative_count >= 2

    def test_dialog_text(self):
        """Dialog should have interrogative/exclamatory."""
        text = (
            "Are you ready? "
            "Yes, I am! "
            "What should we do? "
            "Let's go now!"
        )
        result = compute_sentence_types(text)

        # Dialog: questions and exclamations
        assert result.interrogative_count + result.exclamatory_count >= 2


# ===== Ratio Validation Tests =====


class TestRatioValidation:
    """Test that ratios are valid and sum correctly."""

    def test_structural_ratios_sum(self, mixed_structural):
        """Structural ratios should sum to 1.0."""
        result = compute_sentence_types(mixed_structural)

        total_structural = (
            result.simple_ratio
            + result.compound_ratio
            + result.complex_ratio
            + result.compound_complex_ratio
        )
        assert total_structural == pytest.approx(1.0, abs=0.01)

    def test_functional_ratios_sum(self, mixed_functional):
        """Functional ratios should sum to 1.0."""
        result = compute_sentence_types(mixed_functional)

        total_functional = (
            result.declarative_ratio
            + result.interrogative_ratio
            + result.imperative_ratio
            + result.exclamatory_ratio
        )
        assert total_functional == pytest.approx(1.0, abs=0.01)

    def test_all_ratios_in_range(self, mixed_structural):
        """All ratios should be between 0.0 and 1.0."""
        result = compute_sentence_types(mixed_structural)

        # Structural ratios
        assert 0.0 <= result.simple_ratio <= 1.0
        assert 0.0 <= result.compound_ratio <= 1.0
        assert 0.0 <= result.complex_ratio <= 1.0
        assert 0.0 <= result.compound_complex_ratio <= 1.0

        # Functional ratios
        assert 0.0 <= result.declarative_ratio <= 1.0
        assert 0.0 <= result.interrogative_ratio <= 1.0
        assert 0.0 <= result.imperative_ratio <= 1.0
        assert 0.0 <= result.exclamatory_ratio <= 1.0


# ===== Real-World Text Tests =====


class TestRealWorldTexts:
    """Test with real-world text samples."""

    def test_academic_abstract(self):
        """Test with academic journal abstract."""
        text = (
            "This study investigated the effects of syntactic complexity on readability. "
            "The results demonstrated that parse tree depth correlates with perceived difficulty, "
            "which aligns with previous findings. "
            "These findings suggest that syntactic analysis provides valuable insights into text complexity."
        )
        result = compute_sentence_types(text)

        # Academic: mostly declarative, some complex
        assert result.declarative_ratio >= 0.9
        assert result.complex_ratio > 0

    def test_news_article(self):
        """Test with news article text."""
        text = (
            "The government announced new policies yesterday. "
            "The policies will affect thousands of citizens. "
            "Officials said the changes were necessary for economic growth. "
            "Critics argued that the measures would harm vulnerable populations."
        )
        result = compute_sentence_types(text)

        # News: declarative dominant, mix of simple/complex
        assert result.declarative_ratio >= 0.9
        assert result.simple_count + result.complex_count >= 2

    def test_fiction_narrative(self):
        """Test with fiction narrative."""
        text = (
            "She walked slowly down the dark street. "
            "The rain fell and the wind howled. "
            "When she reached the corner, she stopped. "
            "What should she do now?"
        )
        result = compute_sentence_types(text)

        # Fiction: variety of types
        assert result.total_sentences == 4
        assert result.structural_diversity > 0

    def test_instruction_manual(self):
        """Test with instruction manual."""
        text = (
            "Read all instructions before beginning. "
            "Remove all parts from the packaging. "
            "Place the base on a flat surface. "
            "Tighten all screws firmly."
        )
        result = compute_sentence_types(text)

        # Instructions: high imperative ratio
        assert result.imperative_count >= 2

    def test_conversational_dialog(self):
        """Test with conversational dialog."""
        text = (
            "How are you today? "
            "I'm doing well, thank you! "
            "What have you been up to? "
            "Just working on some projects."
        )
        result = compute_sentence_types(text)

        # Dialog: questions and variety
        assert result.interrogative_count >= 1
        assert result.total_sentences == 4
