"""Comprehensive tests for Automated Readability Index (ARI) computation."""

from pystylometry.readability import compute_ari


class TestARISpecialCases:
    """Test special input cases."""

    def test_urls_and_emails(self):
        """Test handling of URLs and email addresses."""
        text = "Visit https://example.com or email user@example.com for info."
        result = compute_ari(text)

        # Should complete without error
        assert result.ari_score is not None
        assert result.grade_level >= 0

    def test_numbers_in_text(self):
        """Test handling of numbers."""
        text = "In 2023, the company had 500 employees and revenue of $1,000,000."
        result = compute_ari(text)

        # Should complete without error
        assert result.ari_score is not None

    def test_contractions(self):
        """Test handling of contractions."""
        text = "I can't believe it's already over. They're leaving soon."
        result = compute_ari(text)

        # Should handle contractions naturally
        assert result.metadata["word_count"] >= 1
        assert result.grade_level >= 0

    def test_hyphenated_words(self):
        """Test handling of hyphenated compounds."""
        text = "The well-known twenty-first-century state-of-the-art solution."
        result = compute_ari(text)

        # Should count characters regardless of hyphenation
        assert result.metadata["character_count"] > 40
