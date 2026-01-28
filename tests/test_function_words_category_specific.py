"""Tests for function word analysis.

Related GitHub Issue:
    #13 - Function Word Analysis
    https://github.com/craigtrim/pystylometry/issues/13

Function words (determiners, prepositions, conjunctions, pronouns, auxiliary
verbs, particles) are closed-class words that authors use subconsciously and
consistently, making them powerful markers for authorship attribution.

This test suite covers:
    - Basic functionality with normal prose
    - Edge cases (empty text, no function words, only function words)
    - Constraints and invariants (ratios in [0,1], counts logical)
    - Category-specific tests (each function word type)
    - Overlapping word handling (words in multiple categories)
    - Distribution and frequency accuracy
    - Diversity metric validation
    - Case insensitivity
    - Punctuation handling
    - Real-world text samples
    - Authorship attribution scenarios

References:
    Mosteller, F., & Wallace, D. L. (1964). Inference and disputed authorship:
        The Federalist. Addison-Wesley.
    Burrows, J. (2002). 'Delta': A measure of stylistic difference and a guide
        to likely authorship. Literary and Linguistic Computing, 17(3), 267-287.
"""

from pystylometry.lexical import compute_function_words

# ==============================================================================
# Fixtures
# ==============================================================================


# ==============================================================================
# Basic Functionality Tests
# ==============================================================================


class TestFunctionWordsCategorySpecific:
    """Category-specific tests."""

    def test_determiner_only_text(self):
        """Test text with only determiners."""
        text = "the a an this that these those"
        result = compute_function_words(text)

        # Determiner ratio should be 1.0 (all words are determiners)
        assert result.determiner_ratio == 1.0
        assert result.metadata["determiner_count"] == 7

        # Other categories should be 0 (or low if overlaps exist)
        # Note: "that" is also a pronoun/conjunction, so we might have overlaps

    def test_preposition_only_text(self):
        """Test text with only prepositions."""
        text = "in on at by for with from to of"
        result = compute_function_words(text)

        # Preposition ratio should be 1.0
        assert result.preposition_ratio == 1.0
        assert result.metadata["preposition_count"] == 9

    def test_conjunction_only_text(self):
        """Test text with only conjunctions."""
        text = "and but or nor for yet so"
        result = compute_function_words(text)

        # Conjunction ratio should be high (but "for" is also a preposition)
        assert result.conjunction_ratio > 0.8
        assert result.metadata["conjunction_count"] == 7

    def test_pronoun_only_text(self):
        """Test text with only pronouns."""
        text = "i you he she it we they me him her us them"
        result = compute_function_words(text)

        # Pronoun ratio should be 1.0
        assert result.pronoun_ratio == 1.0
        assert result.metadata["pronoun_count"] == 12  # 12 pronouns in the text

    def test_auxiliary_only_text(self):
        """Test text with only auxiliaries."""
        text = "can could may might must will would is are was were"
        result = compute_function_words(text)

        # Auxiliary ratio should be 1.0
        assert result.auxiliary_ratio == 1.0
        assert result.metadata["auxiliary_count"] == 11

    def test_particle_only_text(self):
        """Test text with only particles."""
        text = "up down out off over in away back"
        result = compute_function_words(text)

        # Particle ratio should be high (but "in" is also preposition)
        assert result.particle_ratio > 0.8
        assert result.metadata["particle_count"] == 8
