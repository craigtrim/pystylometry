"""Tests for phrase-level beat detection and stress-shape analysis.

This test module is written **ahead of implementation** to specify the expected
public API and behaviour of the forthcoming ``compute_beat`` function.  All
tests are marked ``xfail`` — they are expected to fail until the feature is
built and the import is satisfiable.

Related GitHub Issue:
    #76 - Feature: Beat Detection — Phrase-Level Stress Shape Analysis
    https://github.com/craigtrim/pystylometry/issues/76

Background:
    Beat in prose is the perceived rhythmic pulse when reading aloud — the
    pattern of stressed and unstressed syllables across a phrase or sentence.
    This is distinct from aggregate stress statistics (which already exist in
    ``rhythm_prosody.py``) and refers specifically to the **sequential stress
    shape** across parallel units (words, phrases, or clauses).

    The key insight driving this feature (from the issue):
        LLMs default to *isocolon* — parallel units of roughly equal syllabic
        weight — because it is the statistically safest pattern.  Skilled human
        writers tend toward *climactic* structure, where the final member
        carries more rhetorical weight.  That asymmetry is an AI-tell signal
        *within* tricolon, not merely in tricolon detection.

Existing Infrastructure (do NOT re-implement):
    ``rhythm_prosody._get_stress_pattern(word)``  → list[int] of CMU stress values
    ``pronouncing.phones_for_word(word)``         → ARPAbet strings with stress digits

Dependency Graph:
    #76 (this) → blocks → #73 Tricolon Detector
    #76 (this) → feeds   → #69 AI Stylistic Tell Detection

Expected Output Type ``BeatResult``:
    units           list[BeatUnit]   — per-unit analysis
      .text         str
      .stress_sequence  list[int]    — e.g. [1, 0, 1, 0]
      .syllabic_weight  int          — count of primary-stressed syllables (digit == 1)
      .beat_string  str              — human-readable: "da-DUM-da"
    weight_sequence list[int]        — syllabic_weight across all units
    weight_cv       float            — CV of weight_sequence (isocolon indicator)
    beat_shape      str              — "isocolon" | "climactic" | "anti-climactic" | "irregular"
    cmu_coverage    float            — fraction of words found in CMU dict

Shape Classification Rules (from issue):
    isocolon        CV < 0.2
    climactic       last unit weight > mean of preceding units AND CV >= 0.2
    anti-climactic  last unit weight < mean of preceding units AND CV >= 0.2
    irregular       high CV, no monotonic trend
"""

import pytest

# ---------------------------------------------------------------------------
# Import guard — the module does not exist yet.
# ``compute_beat`` is set to None so that all tests are collected; each test
# is individually marked @pytest.mark.xfail(strict=True) so pytest reports
# them as XFAIL (expected failure) rather than ERROR.
#
# Once ``pystylometry/prosody/beat_detection.py`` is implemented and
# ``compute_beat`` is exported from ``pystylometry.prosody``, remove the
# try/except and the ``_BEAT_AVAILABLE`` guards and let the import stand bare.
#
# Related GitHub Issue:
#     #76 — https://github.com/craigtrim/pystylometry/issues/76
# ---------------------------------------------------------------------------
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


# ===========================================================================
# Fixtures
# ===========================================================================

#: Classic tricolon with clear climactic weight: "I came, I saw, I conquered."
#: Stress weights rise across the three members — prototypical human pattern.
CLIMACTIC_TRICOLON = ["I came", "I saw", "I conquered"]

#: Flat isocolon: three metrically identical monosyllabic chunks.
#: Prototypical LLM-generated pattern (equal-weight parallelism).
ISOCOLON_UNITS = ["cats run", "dogs bark", "birds sing"]

#: Two-unit pair — not a tricolon, but beat shape still meaningful.
PAIR_UNITS = ["swift and sure", "bold and bright"]

#: Single unit — degenerate case; cross-unit metrics are undefined.
SINGLE_UNIT = ["swiftly and silently and alone"]

#: Empty list — must not raise.
EMPTY_UNITS: list[str] = []


# ===========================================================================
# 1. Return type and top-level structure
# ===========================================================================


@_XFAIL
def test_return_type_is_beat_result():
    """``compute_beat`` must return an object with the expected top-level fields.

    Related GitHub Issue:
        #76 — Output Type specification
        https://github.com/craigtrim/pystylometry/issues/76
    """
    result = compute_beat(CLIMACTIC_TRICOLON)

    assert hasattr(result, "units")
    assert hasattr(result, "weight_sequence")
    assert hasattr(result, "weight_cv")
    assert hasattr(result, "beat_shape")
    assert hasattr(result, "cmu_coverage")


@_XFAIL
def test_units_length_matches_input():
    """The ``units`` list must have the same length as the input.

    Related GitHub Issue:
        #76 — Per-unit analysis
        https://github.com/craigtrim/pystylometry/issues/76
    """
    result = compute_beat(CLIMACTIC_TRICOLON)
    assert len(result.units) == len(CLIMACTIC_TRICOLON)


@_XFAIL
def test_weight_sequence_length_matches_units():
    """``weight_sequence`` must contain exactly one value per unit.

    Related GitHub Issue:
        #76 — Cross-unit analysis
        https://github.com/craigtrim/pystylometry/issues/76
    """
    result = compute_beat(CLIMACTIC_TRICOLON)
    assert len(result.weight_sequence) == len(CLIMACTIC_TRICOLON)


# ===========================================================================
# 2. Per-unit BeatUnit fields
# ===========================================================================


@_XFAIL
def test_beat_unit_fields():
    """Each BeatUnit must expose text, stress_sequence, syllabic_weight, beat_string.

    Related GitHub Issue:
        #76 — Per-unit analysis / BeatUnit dataclass
        https://github.com/craigtrim/pystylometry/issues/76
    """
    result = compute_beat(CLIMACTIC_TRICOLON)
    for unit in result.units:
        assert hasattr(unit, "text")
        assert hasattr(unit, "stress_sequence")
        assert hasattr(unit, "syllabic_weight")
        assert hasattr(unit, "beat_string")


@_XFAIL
def test_beat_unit_text_preserved():
    """Each BeatUnit.text must echo the original input string exactly.

    Related GitHub Issue:
        #76 — Per-unit analysis
        https://github.com/craigtrim/pystylometry/issues/76
    """
    result = compute_beat(CLIMACTIC_TRICOLON)
    for original, unit in zip(CLIMACTIC_TRICOLON, result.units):
        assert unit.text == original


@_XFAIL
def test_stress_sequence_values_are_0_1_2():
    """Stress values in each sequence must be CMU digit values: 0, 1, or 2.

    Related GitHub Issue:
        #76 — Reuse _get_stress_pattern from rhythm_prosody
        https://github.com/craigtrim/pystylometry/issues/76

    Note:
        CMU digit meanings — 0: unstressed, 1: primary stress, 2: secondary stress.
        Source: ARPAbet / cmudict convention, reused from rhythm_prosody.py.
    """
    result = compute_beat(CLIMACTIC_TRICOLON)
    for unit in result.units:
        for val in unit.stress_sequence:
            assert val in (0, 1, 2), f"Unexpected stress value {val} in {unit.text!r}"


@_XFAIL
def test_syllabic_weight_counts_primary_stress():
    """syllabic_weight must equal the count of primary-stress (digit == 1) syllables.

    Related GitHub Issue:
        #76 — Syllabic weight definition
        https://github.com/craigtrim/pystylometry/issues/76
    """
    result = compute_beat(CLIMACTIC_TRICOLON)
    for unit in result.units:
        expected = sum(1 for v in unit.stress_sequence if v == 1)
        assert unit.syllabic_weight == expected, (
            f"Unit {unit.text!r}: weight {unit.syllabic_weight} != "
            f"primary-stress count {expected}"
        )


@_XFAIL
def test_beat_string_uses_dum_da_tokens():
    """beat_string must be a hyphen-joined sequence of 'DUM' and 'da' tokens.

    Related GitHub Issue:
        #76 — Beat string renderer
        https://github.com/craigtrim/pystylometry/issues/76

    Examples:
        [1, 0] → "DUM-da"
        [0, 1] → "da-DUM"
        [0, 0, 1] → "da-da-DUM"
    """
    result = compute_beat(CLIMACTIC_TRICOLON)
    for unit in result.units:
        tokens = unit.beat_string.split("-")
        for tok in tokens:
            assert tok in ("DUM", "da"), (
                f"Unexpected token {tok!r} in beat_string {unit.beat_string!r}"
            )


# ===========================================================================
# 3. Beat shape classification
# ===========================================================================


@_XFAIL
def test_beat_shape_valid_values():
    """beat_shape must be one of the four defined classification strings.

    Related GitHub Issue:
        #76 — Shape classifier
        https://github.com/craigtrim/pystylometry/issues/76
    """
    valid_shapes = {"isocolon", "climactic", "anti-climactic", "irregular"}
    result = compute_beat(CLIMACTIC_TRICOLON)
    assert result.beat_shape in valid_shapes, (
        f"Unexpected beat_shape value: {result.beat_shape!r}"
    )


@_XFAIL
def test_isocolon_classification_for_flat_units():
    """Metrically identical units should classify as 'isocolon' (CV < 0.2).

    Related GitHub Issue:
        #76 — Isocolon: equal-weight parallel units, CV < 0.2
        https://github.com/craigtrim/pystylometry/issues/76

    Why this matters:
        LLMs disproportionately generate isocolon because balanced parallelism
        is the statistically dominant pattern in training data.  A low CV across
        units is a measurable AI-tell when found within tricolon candidates.
    """
    result = compute_beat(ISOCOLON_UNITS)
    assert result.beat_shape == "isocolon", (
        f"Expected 'isocolon' for flat units, got {result.beat_shape!r}. "
        f"weight_sequence={result.weight_sequence}, weight_cv={result.weight_cv:.3f}"
    )


@_XFAIL
def test_climactic_classification_for_rising_weight():
    """Units with rising syllabic weight should classify as 'climactic'.

    Related GitHub Issue:
        #76 — Climactic: third unit heavier than first two
        https://github.com/craigtrim/pystylometry/issues/76

    Example:
        "I came, I saw, I conquered" — the third member carries more stressed
        syllables than the two preceding it, producing a rhetorical crescendo.

    Why this matters:
        Climactic tricolon is the canonical human rhetorical structure.  Its
        presence (or absence, as in AI isocolon) discriminates authorship.
    """
    result = compute_beat(CLIMACTIC_TRICOLON)
    assert result.beat_shape == "climactic", (
        f"Expected 'climactic' for {CLIMACTIC_TRICOLON!r}, "
        f"got {result.beat_shape!r}. "
        f"weight_sequence={result.weight_sequence}"
    )


@_XFAIL
def test_weight_cv_low_for_isocolon():
    """weight_cv must be below 0.2 for isocolon classification.

    Related GitHub Issue:
        #76 — CV threshold for isocolon
        https://github.com/craigtrim/pystylometry/issues/76
    """
    result = compute_beat(ISOCOLON_UNITS)
    assert result.weight_cv < 0.2, (
        f"Expected weight_cv < 0.2 for isocolon, got {result.weight_cv:.4f}"
    )


# ===========================================================================
# 4. weight_sequence and weight_cv numerics
# ===========================================================================


@_XFAIL
def test_weight_sequence_type():
    """weight_sequence must be a list of non-negative integers.

    Related GitHub Issue:
        #76 — Cross-unit weight sequence
        https://github.com/craigtrim/pystylometry/issues/76
    """
    result = compute_beat(CLIMACTIC_TRICOLON)
    assert isinstance(result.weight_sequence, list)
    for w in result.weight_sequence:
        assert isinstance(w, int)
        assert w >= 0


@_XFAIL
def test_weight_cv_non_negative():
    """weight_cv must always be >= 0.0 (CV is always non-negative by definition).

    Related GitHub Issue:
        #76 — CV of weight_sequence
        https://github.com/craigtrim/pystylometry/issues/76
    """
    result = compute_beat(CLIMACTIC_TRICOLON)
    assert result.weight_cv >= 0.0


@_XFAIL
def test_weight_sequence_matches_unit_weights():
    """weight_sequence[i] must equal units[i].syllabic_weight for all i.

    Related GitHub Issue:
        #76 — Consistency between per-unit and cross-unit data
        https://github.com/craigtrim/pystylometry/issues/76
    """
    result = compute_beat(CLIMACTIC_TRICOLON)
    for i, (w, unit) in enumerate(zip(result.weight_sequence, result.units)):
        assert w == unit.syllabic_weight, (
            f"weight_sequence[{i}]={w} != units[{i}].syllabic_weight={unit.syllabic_weight}"
        )


# ===========================================================================
# 5. cmu_coverage
# ===========================================================================


@_XFAIL
def test_cmu_coverage_range():
    """cmu_coverage must be a float in [0.0, 1.0].

    Related GitHub Issue:
        #76 — CMU dict coverage fraction
        https://github.com/craigtrim/pystylometry/issues/76
    """
    result = compute_beat(CLIMACTIC_TRICOLON)
    assert isinstance(result.cmu_coverage, float)
    assert 0.0 <= result.cmu_coverage <= 1.0


@_XFAIL
def test_cmu_coverage_high_for_common_words():
    """Common English words should yield cmu_coverage >= 0.8.

    Related GitHub Issue:
        #76 — CMU dict coverage fraction
        https://github.com/craigtrim/pystylometry/issues/76
    """
    result = compute_beat(ISOCOLON_UNITS)  # "cats run", "dogs bark", "birds sing"
    assert result.cmu_coverage >= 0.8, (
        f"Expected high CMU coverage for common words, got {result.cmu_coverage:.2f}"
    )


# ===========================================================================
# 6. Edge cases
# ===========================================================================


@_XFAIL
def test_empty_input_does_not_raise():
    """An empty unit list must return gracefully, not raise.

    Related GitHub Issue:
        #76 — Edge case handling
        https://github.com/craigtrim/pystylometry/issues/76
    """
    result = compute_beat(EMPTY_UNITS)
    assert result is not None
    assert result.units == []
    assert result.weight_sequence == []


@_XFAIL
def test_single_unit_does_not_raise():
    """A single unit must not raise; cross-unit metrics are undefined / zero.

    Related GitHub Issue:
        #76 — Edge case handling
        https://github.com/craigtrim/pystylometry/issues/76
    """
    result = compute_beat(SINGLE_UNIT)
    assert result is not None
    assert len(result.units) == 1
    # CV of a single value is undefined; implementation should return 0.0 or None
    assert result.weight_cv in (0.0, None)


@_XFAIL
def test_pair_units_returns_valid_shape():
    """Two-unit input must produce a valid beat_shape (not crash).

    Related GitHub Issue:
        #76 — Edge case handling / non-tricolon inputs
        https://github.com/craigtrim/pystylometry/issues/76
    """
    valid_shapes = {"isocolon", "climactic", "anti-climactic", "irregular"}
    result = compute_beat(PAIR_UNITS)
    assert result.beat_shape in valid_shapes


@_XFAIL
def test_unknown_words_handled_gracefully():
    """Units containing OOV words must not raise; cmu_coverage reflects the gap.

    Related GitHub Issue:
        #76 — CMU coverage, OOV handling
        https://github.com/craigtrim/pystylometry/issues/76
    """
    oov_units = ["xyzzyplugh blorf", "glorbnak sneet", "wumple crisk"]
    result = compute_beat(oov_units)
    assert result is not None
    # Coverage should be low (OOV words)
    assert result.cmu_coverage < 0.5


# ===========================================================================
# 7. AI-tell signal — isocolon discrimination
# ===========================================================================


@_XFAIL
def test_isocolon_cv_lower_than_climactic():
    """Flat units must produce a lower weight_cv than rising-weight units.

    Related GitHub Issue:
        #76 — AI-tell: LLMs default to isocolon (low CV)
        https://github.com/craigtrim/pystylometry/issues/76
        #69 — AI Stylistic Tell Detection
        https://github.com/craigtrim/pystylometry/issues/69

    Theoretical basis (from issue #76):
        LLMs generate isocolon because balanced parallelism dominates training
        data.  Skilled human writers tend toward climactic structure.  The CV
        gap between these patterns is the discriminating signal this feature
        exposes for downstream use by the Tricolon Detector (#73).
    """
    iso_result = compute_beat(ISOCOLON_UNITS)
    climactic_result = compute_beat(CLIMACTIC_TRICOLON)

    assert iso_result.weight_cv < climactic_result.weight_cv, (
        f"Isocolon CV ({iso_result.weight_cv:.4f}) should be < "
        f"climactic CV ({climactic_result.weight_cv:.4f})"
    )
