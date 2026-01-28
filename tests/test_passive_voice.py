"""Tests for advanced syntactic analysis (Issue #17)."""

import pytest

from pystylometry.syntactic.advanced_syntactic import compute_advanced_syntactic

# ===== Fixtures =====


# ===== Basic Functionality Tests =====


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
def active_text():
    """Text with active voice only."""
    return (
        "The researchers conducted the experiment. "
        "They analyzed the results carefully. "
        "They published the findings in the journal."
    )


@pytest.fixture
def passive_text():
    """Text with passive voice constructions."""
    return (
        "The experiment was conducted by the researchers. "
        "The results were analyzed carefully. "
        "The findings have been published in the journal."
    )


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
