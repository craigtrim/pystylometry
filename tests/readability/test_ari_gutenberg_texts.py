"""Comprehensive tests for Automated Readability Index (ARI) computation."""

from pathlib import Path

import pytest

from pystylometry.readability import compute_ari


class TestARIGutenbergTexts:
    """Test with real literary texts from Project Gutenberg."""

    @pytest.fixture
    def fixtures_dir(self) -> Path:
        """Get path to test fixtures directory."""
        return Path(__file__).parent.parent / "fixtures"

    def test_hound_of_baskervilles(self, fixtures_dir: Path):
        """Test with The Hound of the Baskervilles."""
        text_path = fixtures_dir / "doyle-the-hound-of-the-baskervilles.txt"
        if not text_path.exists():
            pytest.skip(f"Fixture not found: {text_path}")

        with open(text_path) as f:
            text = f.read()

        result = compute_ari(text)

        # Doyle's writing style
        assert result.grade_level >= 5
        assert result.grade_level <= 15
        assert result.metadata["reliable"]
        assert result.metadata["word_count"] > 10000

    def test_sign_of_four(self, fixtures_dir: Path):
        """Test with The Sign of the Four."""
        text_path = fixtures_dir / "doyle-the-sign-of-the-four.txt"
        if not text_path.exists():
            pytest.skip(f"Fixture not found: {text_path}")

        with open(text_path) as f:
            text = f.read()

        result = compute_ari(text)

        assert result.grade_level >= 5
        assert result.metadata["reliable"]

    def test_valley_of_fear(self, fixtures_dir: Path):
        """Test with The Valley of Fear."""
        text_path = fixtures_dir / "doyle-the-valley-of-fear.txt"
        if not text_path.exists():
            pytest.skip(f"Fixture not found: {text_path}")

        with open(text_path) as f:
            text = f.read()

        result = compute_ari(text)

        assert result.grade_level >= 5
        assert result.metadata["reliable"]

    def test_gutenberg_consistency(self, fixtures_dir: Path):
        """Test that Doyle texts show consistent grade levels."""
        texts = [
            "doyle-the-hound-of-the-baskervilles.txt",
            "doyle-the-sign-of-the-four.txt",
            "doyle-the-valley-of-fear.txt",
        ]

        results = []
        for filename in texts:
            text_path = fixtures_dir / filename
            if not text_path.exists():
                continue

            with open(text_path) as f:
                text = f.read()

            result = compute_ari(text)
            results.append((filename, result.grade_level))

        if len(results) < 2:
            pytest.skip("Not enough fixtures for consistency test")

        # All should be within a reasonable range (same author, similar era)
        grade_levels = [r[1] for r in results]
        assert max(grade_levels) - min(grade_levels) <= 4  # Within 4 grade levels
