"""Concrete beat-shape classification test.

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
def test_equal_weight_phrases_classify_as_isocolon():
    """Three phrases of identical syllabic weight classify as isocolon.

    "cats run"   → 2 primary stresses (one per word)
    "dogs bark"  → 2 primary stresses (one per word)
    "birds sing" → 2 primary stresses (one per word)

    All three units carry the same weight → CV = 0.0 → isocolon.

    Related GitHub Issue:
        #76 — https://github.com/craigtrim/pystylometry/issues/76
    """
    result = compute_beat(["cats run", "dogs bark", "birds sing"])
    assert result.beat_shape == "isocolon"
