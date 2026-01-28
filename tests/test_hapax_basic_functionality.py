"""Comprehensive tests for hapax legomena and vocabulary richness metrics."""

from pystylometry.lexical import compute_hapax_ratios


class TestHapaxBasicFunctionality:
    """Test basic hapax legomena functionality."""

    def test_basic_hapax_detection(self):
        """Test detection of hapax legomena (words appearing once)."""
        # "quick", "brown", "fox", "jumps", "over", "lazy", "dog" appear once
        # "the" appears twice (lowercased: "The" and "the")
        text = "The quick brown fox jumps over the lazy dog"
        result = compute_hapax_ratios(text)

        # 7 words appear once (hapax legomena)
        assert result.hapax_count == 7, "Should detect 7 hapax legomena"

        # 1 word appears twice (dis-hapax legomena)
        assert result.dis_hapax_count == 1, "Should detect 1 dis-hapax legomenon (the)"

        # Vocabulary size should be 8 unique words
        assert result.metadata["total_vocabulary_size"] == 8

    def test_hapax_ratio_calculation(self):
        """Test hapax ratio = hapax_count / token_count."""
        text = "The quick brown fox jumps over the lazy dog"
        result = compute_hapax_ratios(text)

        # 9 total tokens, 7 hapax
        expected_ratio = 7.0 / 9.0
        assert abs(result.hapax_ratio - expected_ratio) < 0.001

    def test_dis_hapax_ratio_calculation(self):
        """Test dis-hapax ratio = dis_hapax_count / token_count."""
        text = "The quick brown fox jumps over the lazy dog"
        result = compute_hapax_ratios(text)

        # 9 total tokens, 1 dis-hapax ("the" appears twice)
        expected_ratio = 1.0 / 9.0
        assert abs(result.dis_hapax_ratio - expected_ratio) < 0.001
