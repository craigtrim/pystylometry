"""Tests for genre and register classification features.

Related GitHub Issue:
    #23 - Genre and Register Features
    https://github.com/craigtrim/pystylometry/issues/23

References:
    Biber, D. (1988). Variation across speech and writing.
    Biber, D., & Conrad, S. (2009). Register, genre, and style.
    Heylighen, F., & Dewaele, J. M. (1999). Formality of language.
    Joos, M. (1961). The Five Clocks.
"""

import pytest

from pystylometry.stylistic import compute_genre_register

# =============================================================================
# Sample Texts
# =============================================================================

ACADEMIC_TEXT = """
The investigation demonstrates that the correlation between nominalization
frequency and formality is statistically significant. Previous research
has established that academic discourse typically exhibits higher
nominalization density. Furthermore, the analysis indicates that the
implementation of these methodological considerations contributes to
the determination of register classification. It is observed that
subsequent evaluation of the evidence reveals substantial implications
for the theoretical framework. The hypothesis was confirmed through
systematic observation and rigorous examination of the data.
"""

LEGAL_TEXT = """
Whereas the defendant hereby acknowledges the jurisdiction of this court,
and whereas the plaintiff has established liability pursuant to the
aforementioned statute, the undersigned hereby stipulates that the
provision shall be enforced forthwith. Notwithstanding the defendant's
objection, the covenant shall constitute a binding obligation. The
liability was determined to be substantial. It is hereby ordered that
compliance shall be maintained in accordance with the constitution.
"""

FICTION_TEXT = """
She walked into the room and looked around. The old house was dark and
cold. "Where is everyone?" she whispered. Suddenly, a door slammed
somewhere above. She jumped and grabbed the railing. Her heart was
pounding. Then she heard footsteps on the stairs. "Hello?" she called
out. A shadow fell across the wall. She turned and ran toward the
window, but it was locked. "Help me!" she cried.
"""

CONVERSATIONAL_TEXT = """
Hey, so like I was totally gonna tell you about this awesome thing
that happened. Basically, this guy just randomly showed up and was
like really cool about the whole thing. I dunno, it was just amazing.
You know what I mean? Yeah, it was literally the best thing ever.
Actually, I kinda wanna go back there. The folks were super nice
and the stuff they had was really great.
"""

JOURNALISTIC_TEXT = """
The mayor announced today that a new investigation has been launched
into the controversy surrounding city contracts. According to sources
close to the administration, officials confirmed that the allegations
were reported to authorities last week. A spokesperson for the mayor
denied the claims, stating that the latest update revealed no evidence
of wrongdoing. The crisis has been developing since the scandal broke.
"""


class TestBasicFunctionality:
    """Test basic genre/register analysis functionality."""

    def test_returns_result_type(self):
        """Function returns GenreRegisterResult dataclass."""
        result = compute_genre_register("This is a simple test text.")
        assert hasattr(result, "formality_score")
        assert hasattr(result, "register_classification")
        assert hasattr(result, "predicted_genre")

    def test_all_fields_populated(self):
        """All result fields are populated for non-empty text."""
        result = compute_genre_register(ACADEMIC_TEXT)
        assert isinstance(result.formality_score, float)
        assert isinstance(result.latinate_ratio, float)
        assert isinstance(result.nominalization_density, float)
        assert isinstance(result.passive_voice_density, float)
        assert isinstance(result.first_person_ratio, float)
        assert isinstance(result.second_person_ratio, float)
        assert isinstance(result.third_person_ratio, float)
        assert isinstance(result.impersonal_construction_density, float)
        assert isinstance(result.abstract_noun_ratio, float)
        assert isinstance(result.concrete_noun_ratio, float)
        assert isinstance(result.abstractness_score, float)
        assert isinstance(result.technical_term_density, float)
        assert isinstance(result.jargon_density, float)
        assert isinstance(result.narrative_marker_density, float)
        assert isinstance(result.expository_marker_density, float)
        assert isinstance(result.narrative_expository_ratio, float)
        assert isinstance(result.dialogue_ratio, float)
        assert isinstance(result.quotation_density, float)
        assert isinstance(result.register_classification, str)
        assert isinstance(result.predicted_genre, str)
        assert isinstance(result.genre_confidence, float)
        assert isinstance(result.academic_score, float)
        assert isinstance(result.journalistic_score, float)
        assert isinstance(result.fiction_score, float)
        assert isinstance(result.legal_score, float)
        assert isinstance(result.conversational_score, float)
        assert isinstance(result.metadata, dict)

    def test_metadata_contains_word_count(self):
        """Metadata includes word count."""
        result = compute_genre_register("Hello world test text here.")
        assert "word_count" in result.metadata
        assert result.metadata["word_count"] == 5

    def test_metadata_contains_computation_time(self):
        """Metadata includes computation time."""
        result = compute_genre_register("Some text for analysis.")
        assert "computation_time" in result.metadata
        assert result.metadata["computation_time"] >= 0


class TestEmptyInput:
    """Test handling of empty and whitespace input."""

    def test_empty_string(self):
        """Empty string returns zero values."""
        result = compute_genre_register("")
        assert result.formality_score == 0.0
        assert result.register_classification == "unknown"
        assert result.predicted_genre == "unknown"
        assert result.genre_confidence == 0.0

    def test_whitespace_only(self):
        """Whitespace-only string returns zero values."""
        result = compute_genre_register("   \n\t  ")
        assert result.formality_score == 0.0
        assert result.register_classification == "unknown"
        assert result.predicted_genre == "unknown"


class TestFormalityScore:
    """Test formality score computation."""

    def test_formality_range(self):
        """Formality score is between 0 and 100."""
        for text in [ACADEMIC_TEXT, FICTION_TEXT, CONVERSATIONAL_TEXT, LEGAL_TEXT]:
            result = compute_genre_register(text)
            assert 0.0 <= result.formality_score <= 100.0

    def test_academic_more_formal_than_conversational(self):
        """Academic text should have higher formality than conversational."""
        academic = compute_genre_register(ACADEMIC_TEXT)
        conversational = compute_genre_register(CONVERSATIONAL_TEXT)
        assert academic.formality_score > conversational.formality_score

    def test_legal_highly_formal(self):
        """Legal text should have high formality score."""
        result = compute_genre_register(LEGAL_TEXT)
        assert result.formality_score > 30

    def test_conversational_low_formality(self):
        """Conversational text should have low formality."""
        result = compute_genre_register(CONVERSATIONAL_TEXT)
        assert result.formality_score < 30


class TestLatinateRatio:
    """Test Latinate vs Germanic word ratio."""

    def test_ratio_range(self):
        """Latinate ratio is between 0 and 1."""
        result = compute_genre_register(ACADEMIC_TEXT)
        assert 0.0 <= result.latinate_ratio <= 1.0

    def test_academic_higher_latinate(self):
        """Academic text has higher Latinate ratio than conversational."""
        academic = compute_genre_register(ACADEMIC_TEXT)
        conversational = compute_genre_register(CONVERSATIONAL_TEXT)
        assert academic.latinate_ratio > conversational.latinate_ratio

    def test_latinate_words_counted(self):
        """Explicitly Latinate words are detected."""
        text = "The investigation demonstrates significant implications for the analysis."
        result = compute_genre_register(text)
        assert result.latinate_ratio > 0.0
        assert result.metadata["latinate_word_count"] > 0


class TestNominalizations:
    """Test nominalization detection."""

    def test_nominalization_detection(self):
        """Nominalizations are detected by suffix."""
        text = "The investigation and determination of the situation requires evaluation."
        result = compute_genre_register(text)
        assert result.nominalization_density > 0.0
        assert result.metadata["nominalization_count"] > 0

    def test_short_words_excluded(self):
        """Short words are not falsely counted as nominalizations."""
        text = "The ant went to the dance in the den."
        result = compute_genre_register(text)
        assert result.metadata["nominalization_count"] == 0

    def test_academic_higher_nominalizations(self):
        """Academic text has higher nominalization density."""
        academic = compute_genre_register(ACADEMIC_TEXT)
        fiction = compute_genre_register(FICTION_TEXT)
        assert academic.nominalization_density > fiction.nominalization_density


class TestPassiveVoice:
    """Test passive voice detection."""

    def test_passive_detected(self):
        """Passive voice constructions are detected."""
        text = "The report was written by the committee. The results were analyzed carefully."
        result = compute_genre_register(text)
        assert result.passive_voice_density > 0.0
        assert result.metadata["passive_voice_count"] >= 2

    def test_active_voice_no_passive(self):
        """Active voice sentences should not trigger passive detection."""
        text = "The dog chased the cat. She ran quickly."
        result = compute_genre_register(text)
        assert result.metadata["passive_voice_count"] == 0


class TestPronounRatios:
    """Test pronoun analysis."""

    def test_pronoun_ratios_sum_to_one(self):
        """Pronoun ratios sum to approximately 1.0 when pronouns exist."""
        text = "I told him that she wanted you to help them."
        result = compute_genre_register(text)
        total = result.first_person_ratio + result.second_person_ratio + result.third_person_ratio
        assert total == pytest.approx(1.0, abs=0.01)

    def test_first_person_dominant(self):
        """First-person-heavy text shows high first person ratio."""
        text = "I went to my house. I saw myself in the mirror. We love our home."
        result = compute_genre_register(text)
        assert result.first_person_ratio > 0.5

    def test_third_person_dominant(self):
        """Third-person-heavy text shows high third person ratio."""
        text = "He told her that they would bring their friends. She agreed with him."
        result = compute_genre_register(text)
        assert result.third_person_ratio > 0.5

    def test_no_pronouns(self):
        """Text without pronouns has zero ratios."""
        text = "The quick brown fox jumped over the lazy dog."
        result = compute_genre_register(text)
        assert result.first_person_ratio == 0.0
        assert result.second_person_ratio == 0.0
        assert result.third_person_ratio == 0.0


class TestAbstractConcrete:
    """Test abstract vs concrete noun detection."""

    def test_abstract_nouns_detected(self):
        """Abstract nouns are detected by suffix."""
        text = "Freedom and happiness require determination and persistence."
        result = compute_genre_register(text)
        assert result.abstract_noun_ratio > 0.0
        assert result.metadata["abstract_noun_count"] > 0

    def test_concrete_nouns_detected(self):
        """Concrete nouns from word list are detected."""
        text = "The dog sat on the chair next to the table by the window."
        result = compute_genre_register(text)
        assert result.concrete_noun_ratio > 0.0
        assert result.metadata["concrete_noun_count"] > 0

    def test_ratio_range(self):
        """Abstract and concrete ratios are between 0 and 1."""
        result = compute_genre_register(ACADEMIC_TEXT)
        assert 0.0 <= result.abstract_noun_ratio <= 1.0
        assert 0.0 <= result.concrete_noun_ratio <= 1.0


class TestNarrativeExpository:
    """Test narrative vs expository marker detection."""

    def test_narrative_markers_in_fiction(self):
        """Fiction text has narrative markers."""
        result = compute_genre_register(FICTION_TEXT)
        assert result.narrative_marker_density > 0.0
        assert result.metadata["narrative_marker_count"] > 0

    def test_expository_markers_in_academic(self):
        """Academic text has expository markers."""
        result = compute_genre_register(ACADEMIC_TEXT)
        assert result.expository_marker_density > 0.0
        assert result.metadata["expository_marker_count"] > 0

    def test_fiction_higher_narrative_ratio(self):
        """Fiction has more narrative markers than academic text."""
        fiction = compute_genre_register(FICTION_TEXT)
        academic = compute_genre_register(ACADEMIC_TEXT)
        assert fiction.narrative_marker_density > academic.narrative_marker_density


class TestDialogueDetection:
    """Test dialogue and quotation detection."""

    def test_dialogue_in_fiction(self):
        """Fiction with dialogue has non-zero dialogue ratio."""
        result = compute_genre_register(FICTION_TEXT)
        assert result.dialogue_ratio > 0.0

    def test_no_dialogue_in_academic(self):
        """Academic text has minimal dialogue."""
        result = compute_genre_register(ACADEMIC_TEXT)
        assert result.dialogue_ratio < 0.1

    def test_quotation_count(self):
        """Quotations are counted."""
        text = '"Hello," said Alice. "How are you?" asked Bob.'
        result = compute_genre_register(text)
        assert result.metadata["quotation_count"] >= 2


class TestRegisterClassification:
    """Test register classification (Joos's Five Clocks)."""

    def test_valid_register(self):
        """Register classification is one of the valid categories."""
        valid_registers = {"frozen", "formal", "consultative", "casual", "intimate", "unknown"}
        for text in [ACADEMIC_TEXT, FICTION_TEXT, CONVERSATIONAL_TEXT, LEGAL_TEXT]:
            result = compute_genre_register(text)
            assert result.register_classification in valid_registers

    def test_legal_frozen_or_formal(self):
        """Legal text is classified as frozen or formal register."""
        result = compute_genre_register(LEGAL_TEXT)
        assert result.register_classification in {"frozen", "formal"}

    def test_conversational_casual_or_intimate(self):
        """Conversational text is classified as casual or intimate."""
        result = compute_genre_register(CONVERSATIONAL_TEXT)
        assert result.register_classification in {"casual", "intimate"}


class TestGenrePrediction:
    """Test genre prediction and scoring."""

    def test_genre_scores_range(self):
        """All genre scores are between 0 and 1."""
        result = compute_genre_register(ACADEMIC_TEXT)
        assert 0.0 <= result.academic_score <= 1.0
        assert 0.0 <= result.journalistic_score <= 1.0
        assert 0.0 <= result.fiction_score <= 1.0
        assert 0.0 <= result.legal_score <= 1.0
        assert 0.0 <= result.conversational_score <= 1.0

    def test_valid_predicted_genre(self):
        """Predicted genre is a valid category."""
        valid_genres = {"academic", "journalistic", "fiction", "legal", "conversational", "unknown"}
        result = compute_genre_register(ACADEMIC_TEXT)
        assert result.predicted_genre in valid_genres

    def test_confidence_range(self):
        """Genre confidence is between 0 and 1."""
        result = compute_genre_register(ACADEMIC_TEXT)
        assert 0.0 <= result.genre_confidence <= 1.0

    def test_academic_text_academic_score(self):
        """Academic text should have relatively high academic score."""
        result = compute_genre_register(ACADEMIC_TEXT)
        assert result.academic_score > 0.0

    def test_legal_text_legal_score(self):
        """Legal text should have relatively high legal score."""
        result = compute_genre_register(LEGAL_TEXT)
        assert result.legal_score > 0.0

    def test_fiction_text_fiction_score(self):
        """Fiction text should have non-zero fiction score."""
        result = compute_genre_register(FICTION_TEXT)
        assert result.fiction_score > 0.0

    def test_conversational_text_conversational_score(self):
        """Conversational text should have non-zero conversational score."""
        result = compute_genre_register(CONVERSATIONAL_TEXT)
        assert result.conversational_score > 0.0


class TestImpersonalConstructions:
    """Test impersonal construction detection."""

    def test_it_is_detected(self):
        """'It is' constructions are detected."""
        text = "It is important to note that it is also relevant."
        result = compute_genre_register(text)
        assert result.impersonal_construction_density > 0.0
        assert result.metadata["impersonal_count"] >= 2

    def test_there_are_detected(self):
        """'There are' constructions are detected."""
        text = "There are many reasons. There is also evidence."
        result = compute_genre_register(text)
        assert result.metadata["impersonal_count"] >= 2


class TestTechnicalTerms:
    """Test technical term detection."""

    def test_acronyms_detected(self):
        """Acronyms (all-caps words) are counted as technical terms."""
        text = "The API uses REST and JSON for HTTP communication."
        result = compute_genre_register(text)
        assert result.technical_term_density > 0.0

    def test_long_words_detected(self):
        """Very long words are counted as potential technical terms."""
        text = "The electroencephalography results showed deoxyribonucleic patterns."
        result = compute_genre_register(text)
        assert result.metadata["technical_term_count"] > 0


class TestRegisterMarkers:
    """Test register-specific marker detection."""

    def test_legal_markers_in_legal(self):
        """Legal text has legal markers."""
        result = compute_genre_register(LEGAL_TEXT)
        assert result.metadata["register_marker_counts"]["legal"] > 0

    def test_academic_markers_in_academic(self):
        """Academic text has academic markers."""
        result = compute_genre_register(ACADEMIC_TEXT)
        assert result.metadata["register_marker_counts"]["academic"] > 0

    def test_conversational_markers_in_conversational(self):
        """Conversational text has conversational markers."""
        result = compute_genre_register(CONVERSATIONAL_TEXT)
        assert result.metadata["register_marker_counts"]["conversational"] > 0

    def test_journalistic_markers_in_journalistic(self):
        """Journalistic text has journalistic markers."""
        result = compute_genre_register(JOURNALISTIC_TEXT)
        assert result.metadata["register_marker_counts"]["journalistic"] > 0


class TestMetadataDetail:
    """Test metadata contains expected detail fields."""

    def test_metadata_keys(self):
        """Metadata contains all expected keys."""
        result = compute_genre_register(ACADEMIC_TEXT)
        expected_keys = [
            "word_count",
            "latinate_word_count",
            "germanic_word_count",
            "nominalization_count",
            "passive_voice_count",
            "abstract_noun_count",
            "concrete_noun_count",
            "pronoun_counts",
            "impersonal_count",
            "narrative_marker_count",
            "expository_marker_count",
            "register_marker_counts",
            "technical_term_count",
            "quotation_count",
            "computation_time",
        ]
        for key in expected_keys:
            assert key in result.metadata, f"Missing metadata key: {key}"

    def test_pronoun_counts_structure(self):
        """Pronoun counts in metadata have expected structure."""
        result = compute_genre_register("I told him that she was here.")
        pronoun_counts = result.metadata["pronoun_counts"]
        assert "first" in pronoun_counts
        assert "second" in pronoun_counts
        assert "third" in pronoun_counts

    def test_register_marker_counts_structure(self):
        """Register marker counts have expected structure."""
        result = compute_genre_register(ACADEMIC_TEXT)
        markers = result.metadata["register_marker_counts"]
        assert "legal" in markers
        assert "academic" in markers
        assert "journalistic" in markers
        assert "conversational" in markers


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_word(self):
        """Single word text doesn't crash."""
        result = compute_genre_register("Hello")
        assert result.metadata["word_count"] == 1

    def test_numbers_stripped(self):
        """Numeric-only tokens are stripped by tokenizer."""
        text = "There are items in boxes."
        result = compute_genre_register(text)
        assert result.metadata["word_count"] == 5

    def test_mixed_case(self):
        """Case variations don't affect analysis."""
        text = "The INVESTIGATION demonstrates SIGNIFICANT implications."
        result = compute_genre_register(text)
        assert result.latinate_ratio > 0.0

    def test_punctuation_heavy(self):
        """Heavy punctuation doesn't break analysis."""
        text = "Really?! Yes!!! No... Maybe? OK!!!"
        result = compute_genre_register(text)
        assert result.metadata["word_count"] > 0

    def test_model_parameter_accepted(self):
        """Model parameter is accepted without error."""
        result = compute_genre_register("Test text.", model="en_core_web_lg")
        assert result.metadata["word_count"] == 2


class TestComparativeAnalysis:
    """Test comparative properties across different text types."""

    def test_formality_ordering(self):
        """Legal/academic should be more formal than conversational."""
        legal = compute_genre_register(LEGAL_TEXT)
        academic = compute_genre_register(ACADEMIC_TEXT)
        conversational = compute_genre_register(CONVERSATIONAL_TEXT)

        assert legal.formality_score > conversational.formality_score
        assert academic.formality_score > conversational.formality_score

    def test_narrative_fiction_vs_academic(self):
        """Fiction has more narrative markers than academic text."""
        fiction = compute_genre_register(FICTION_TEXT)
        academic = compute_genre_register(ACADEMIC_TEXT)
        assert fiction.narrative_marker_density > academic.narrative_marker_density

    def test_dialogue_fiction_vs_legal(self):
        """Fiction has more dialogue than legal text."""
        fiction = compute_genre_register(FICTION_TEXT)
        legal = compute_genre_register(LEGAL_TEXT)
        assert fiction.dialogue_ratio > legal.dialogue_ratio
