"""Concrete isocolon beat-shape classification test.

Uses real prose input with explicit unit extraction and a direct
assertion on the classified beat shape.

Related GitHub Issue:
    #76 — Feature: Beat Detection — Phrase-Level Stress Shape Analysis
    https://github.com/craigtrim/pystylometry/issues/76
"""

import pytest

try:
    from pystylometry.prosody.beat_detection import compute_beat

    _BEAT_AVAILABLE = True
except ImportError:
    compute_beat = None  # type: ignore[assignment]
    _BEAT_AVAILABLE = False

_XFAIL = pytest.mark.xfail(
    not _BEAT_AVAILABLE,
    reason=(
        "pystylometry.prosody.beat_detection not yet implemented — "
        "https://github.com/craigtrim/pystylometry/issues/76"
    ),
    strict=True,
)


@_XFAIL
def test_parallel_imperatives_classify_as_isocolon():
    """Three equal-weight verb-adverb imperatives are classified as isocolon.

    Related GitHub Issue:
        #76 — https://github.com/craigtrim/pystylometry/issues/76
    """

    # Three verb-adverb imperatives, each carrying exactly two primary stresses:
    #   "Read"    R IY1 D     → stress 1
    #   "widely"  W AY1 D L IY0 → stress 1   total weight = 2
    #   "Think"   TH IH1 NG K  → stress 1
    #   "deeply"  D IY1 P L IY0 → stress 1   total weight = 2
    #   "Write"   R AY1 T     → stress 1
    #   "clearly" K L IH1 R L IY0 → stress 1  total weight = 2
    #
    # All three units share the same syllabic weight → CV = 0.0 → isocolon.
    # This is the structural pattern LLMs default to when generating parallel
    # imperatives or list items — a candidate AI-tell signal.
    input_lines: list[str] = [
        "Read widely.",
        "Think deeply.",
        "Write clearly."
    ]

    result = compute_beat(input_lines)
    assert result.beat_shape == "isocolon"
