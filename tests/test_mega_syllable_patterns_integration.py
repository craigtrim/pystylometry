"""Integration test for syllable pattern repetition in mega pipeline.

Related GitHub Issue:
    #67 - Syllable pattern repetition analysis
    https://github.com/craigtrim/pystylometry/issues/67
"""

import tempfile
from pathlib import Path

import pytest

# Only run these tests if all dependencies are available
pytest.importorskip("openpyxl")
# Note: No longer requires spaCy (Issue #68: replaced with built-in utilities)
# Related GitHub Issue:
#     #68 - Replace spaCy with built-in utilities
#     https://github.com/craigtrim/pystylometry/issues/68

from pystylometry.mega import run_mega, write_mega_excel
from rich.console import Console


def test_mega_includes_syllable_patterns():
    """Test that mega pipeline includes syllable pattern analysis.

    Related GitHub Issue:
        #67 - Mega integration for syllable pattern repetition
        https://github.com/craigtrim/pystylometry/issues/67
    """
    # Sample text with some repeated patterns (must be 100+ tokens for voc-D)
    text = """
    The cat sat down on the mat. The dog ran fast through the park. The bird flew away into the sky.
    The fish swam slowly in the pond. The mouse ran quickly across the floor. The horse galloped swiftly through the field.
    The elephant walked heavily through the jungle. The monkey jumped playfully between the trees. The lion roared loudly in the savanna.
    The tiger stalked silently through the grass. The bear climbed carefully up the mountain. The rabbit hopped quickly through the meadow.
    The snake slithered smoothly across the rocks. The frog jumped happily near the water. The deer ran gracefully through the forest.
    The owl hooted softly in the darkness. The bat flew swiftly through the night. The wolf howled mournfully at the moon.
    """

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_output.xlsx"

        # Run mega analysis
        console = Console()
        results = run_mega(text, console)
        write_mega_excel(results, output_path)

        # Verify output file was created
        assert output_path.exists()

        # Note: Syllable Patterns tab removed from Excel output (per user request)
        # Analysis still runs in pipeline but tabs are not created
        # Related GitHub Issue:
        #     #68 - Replace spaCy with built-in utilities
        #     https://github.com/craigtrim/pystylometry/issues/68

        # Verify results dict contains the data
        assert "sentence_syllables" in results
        assert "syllable_patterns" in results

        # Verify data structure
        assert results["sentence_syllables"] is not None
        assert results["syllable_patterns"] is not None


def test_mega_syllable_patterns_depends_on_sentence_syllables():
    """Test that syllable patterns only runs if sentence syllables succeeds.

    Related GitHub Issue:
        #67 - Syllable pattern repetition depends on sentence syllables
        https://github.com/craigtrim/pystylometry/issues/67
        #68 - Replace spaCy with built-in utilities (tabs removed from Excel)
        https://github.com/craigtrim/pystylometry/issues/68
    """
    # Text with sufficient length for voc-D (100+ tokens)
    text = """
    The cat sat down on the mat. The dog ran fast through the park. The bird flew away into the sky.
    The fish swam slowly in the pond. The mouse ran quickly across the floor. The horse galloped swiftly through the field.
    The elephant walked heavily through the jungle. The monkey jumped playfully between the trees. The lion roared loudly in the savanna.
    The tiger stalked silently through the grass. The bear climbed carefully up the mountain. The rabbit hopped quickly through the meadow.
    The snake slithered smoothly across the rocks. The frog jumped happily near the water. The deer ran gracefully through the forest.
    """

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_output.xlsx"

        console = Console()
        results = run_mega(text, console)
        write_mega_excel(results, output_path)

        # Note: Excel tabs removed, checking results dict instead
        # If sentence syllables succeeded, syllable patterns should also exist
        if "sentence_syllables" in results:
            assert "syllable_patterns" in results
        # If sentence syllables was skipped, syllable patterns should also be skipped
        else:
            assert "syllable_patterns" not in results


def test_mega_dashboard_includes_syllable_patterns():
    """Test that syllable pattern analysis runs successfully.

    Related GitHub Issue:
        #67 - Dashboard integration for syllable pattern metrics
        https://github.com/craigtrim/pystylometry/issues/67
        #68 - Replace spaCy with built-in utilities (tabs/dashboard removed)
        https://github.com/craigtrim/pystylometry/issues/68
    """
    # Text with sufficient length for voc-D (100+ tokens)
    text = """
    The cat sat down on the mat. The dog ran fast through the park. The bird flew away into the sky.
    The fish swam slowly in the pond. The mouse ran quickly across the floor. The horse galloped swiftly through the field.
    The elephant walked heavily through the jungle. The monkey jumped playfully between the trees. The lion roared loudly in the savanna.
    The tiger stalked silently through the grass. The bear climbed carefully up the mountain. The rabbit hopped quickly through the meadow.
    The snake slithered smoothly across the rocks. The frog jumped happily near the water. The deer ran gracefully through the forest.
    """

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_output.xlsx"

        console = Console()
        results = run_mega(text, console)
        write_mega_excel(results, output_path)

        # Note: Dashboard metrics and Excel tabs removed per user request
        # Just verify the analysis ran successfully
        if "syllable_patterns" in results:
            pattern_result = results["syllable_patterns"]
            # Verify key metrics exist
            assert hasattr(pattern_result, "pattern_diversity_ratio")
            assert hasattr(pattern_result, "repetition_ratio")
            assert hasattr(pattern_result, "pattern_entropy")
