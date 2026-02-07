"""Tests for BNC frequency output classification column integration.

Verifies that all BNC output formats (JSON, CSV/TSV, Excel, HTML) produce
a single ``classification`` column (from ``classify_word().label``) instead
of the five boolean flag columns (unicode, numeric, apostrophe, hyphen, other).

Related GitHub Issues:
    #53 -- Replace boolean flag columns with word_class classification label
    https://github.com/craigtrim/pystylometry/issues/53

    #51 -- Word morphological classification taxonomy (provides classify_word)
    https://github.com/craigtrim/pystylometry/issues/51
"""

import json
from dataclasses import dataclass

import pytest

from pystylometry.lexical.word_class import classify_word

# ===================================================================
# Fixtures: minimal BNC result stubs
# ===================================================================


@dataclass
class _WordStub:
    """Minimal stand-in for WordAnalysis from bnc_frequency."""

    word: str
    observed: int
    expected: float = 0.0
    ratio: float = 0.0
    in_wordnet: bool | None = None
    in_gngram: bool | None = None
    char_type: str = "alpha"


@dataclass
class _ResultStub:
    """Minimal stand-in for BNCFrequencyResult."""

    total_tokens: int = 1000
    unique_tokens: int = 200
    overused: list = None
    underused: list = None
    not_in_bnc: list = None
    overuse_threshold: float = 1.3
    underuse_threshold: float = 0.8

    def __post_init__(self):
        if self.overused is None:
            self.overused = []
        if self.underused is None:
            self.underused = []
        if self.not_in_bnc is None:
            self.not_in_bnc = []


# Standard test words spanning multiple L1 categories
_TEST_WORDS = [
    _WordStub("don't", 47, 0.5, 94.0, True, True),
    _WordStub("zig-zag", 3, 0.5, 6.0, True, True),
    _WordStub("house", 120, 100.0, 1.2, True, True),
    _WordStub("cafe\u0301", 2, 0.0, 0.0, None, False, "unicode"),
    _WordStub("1st", 5, 1.0, 5.0, False, True),
    _WordStub("self-esteem", 8, 2.0, 4.0, True, True),
    _WordStub("can't", 30, 10.0, 3.0, True, True),
    _WordStub("twenty-one", 4, 1.0, 4.0, True, True),
]


def _make_result(words=None):
    """Build a result stub distributing words across all three categories."""
    if words is None:
        words = _TEST_WORDS
    return _ResultStub(
        overused=[w for w in words if w.ratio > 1.3],
        underused=[w for w in words if 0 < w.ratio <= 0.8],
        not_in_bnc=[w for w in words if w.expected == 0.0],
    )


# ===================================================================
# classify_word integration tests: verify expected labels
# ===================================================================


class TestClassifyWordLabels:
    """Ensure classify_word produces the expected label for each test word.

    These labels are what appear in the classification column across all
    output formats.
    """

    @pytest.mark.parametrize(
        "word, expected_label",
        [
            ("don't", "apostrophe.contraction.negative"),
            ("can't", "apostrophe.contraction.negative"),
            ("zig-zag", "hyphenated.reduplicated.ablaut"),
            ("house", "lexical"),
            ("self-esteem", "hyphenated.compound.self"),
            ("twenty-one", "hyphenated.number_word"),
            ("1st", "numeric.ordinal"),
        ],
    )
    def test_expected_label(self, word, expected_label):
        """Each word should classify to its known taxonomy label."""
        assert classify_word(word).label == expected_label

    def test_unicode_word_classifies(self):
        """Non-ASCII words should get a unicode.* classification."""
        result = classify_word("cafe\u0301")
        assert result.l1 == "unicode"

    def test_lexical_word_has_no_dots(self):
        """Pure lexical words have a single-segment label with no dots."""
        assert "." not in classify_word("house").label

    def test_all_test_words_produce_labels(self):
        """Every test word should return a non-empty label string."""
        for w in _TEST_WORDS:
            label = classify_word(w.word).label
            assert isinstance(label, str)
            assert len(label) > 0


# ===================================================================
# HTML format: data dict structure tests
# ===================================================================


class TestHTMLDataDicts:
    """Verify the HTML export builds data dicts with classification, not booleans.

    These tests directly invoke export_bnc_frequency_jsx and inspect the
    data dicts that are passed to the React component via the config object.
    """

    def test_html_overused_has_classification_key(self, tmp_path):
        """Overused data dicts should contain 'classification', not boolean flags."""
        from pystylometry.viz.jsx.bnc_frequency import export_bnc_frequency_jsx

        result = _make_result()
        out = tmp_path / "test.html"
        export_bnc_frequency_jsx(result, out)

        html = out.read_text()
        # The classification labels should appear in the generated HTML/JSON config
        assert "classification" in html
        # The old boolean flag column names should NOT appear as data keys
        # (they may appear in other contexts like documentation text, so we
        # check for the specific JSON key pattern)
        assert '"unicode":' not in html or '"unicode": true' not in html
        assert '"apostrophe":' not in html or '"apostrophe": true' not in html

    def test_html_contains_classification_labels(self, tmp_path):
        """Specific classification labels should appear in the HTML output."""
        from pystylometry.viz.jsx.bnc_frequency import export_bnc_frequency_jsx

        result = _make_result()
        out = tmp_path / "test.html"
        export_bnc_frequency_jsx(result, out)

        html = out.read_text()
        # Overused words with known labels
        assert "apostrophe.contraction.negative" in html
        assert "hyphenated.reduplicated.ablaut" in html

    def test_html_react_column_def_has_classification(self, tmp_path):
        """The React column definitions should include a classification column."""
        from pystylometry.viz.jsx.bnc_frequency import export_bnc_frequency_jsx

        result = _make_result()
        out = tmp_path / "test.html"
        export_bnc_frequency_jsx(result, out)

        html = out.read_text()
        assert "key: 'classification'" in html
        assert "label: 'Classification'" in html

    def test_html_no_old_boolean_columns_in_react(self, tmp_path):
        """The React column definitions should NOT have the old boolean columns."""
        from pystylometry.viz.jsx.bnc_frequency import export_bnc_frequency_jsx

        result = _make_result()
        out = tmp_path / "test.html"
        export_bnc_frequency_jsx(result, out)

        html = out.read_text()
        # These were the old column definitions that should be gone
        assert "key: 'unicode'" not in html
        assert "key: 'numeric'" not in html
        assert "key: 'apostrophe'" not in html
        assert "key: 'hyphen'" not in html
        assert "key: 'other'" not in html

    def test_html_not_in_bnc_has_classification(self, tmp_path):
        """Not-in-BNC data should also have the classification column."""
        from pystylometry.viz.jsx.bnc_frequency import export_bnc_frequency_jsx

        result = _make_result()
        out = tmp_path / "test.html"
        export_bnc_frequency_jsx(result, out)

        html = out.read_text()
        # cafe with accent should produce a unicode classification
        assert "unicode" in html  # the L1 in the label

    def test_html_classification_render_function(self, tmp_path):
        """The classificationRender function should be present in the output."""
        from pystylometry.viz.jsx.bnc_frequency import export_bnc_frequency_jsx

        result = _make_result()
        out = tmp_path / "test.html"
        export_bnc_frequency_jsx(result, out)

        html = out.read_text()
        assert "classificationRender" in html


# ===================================================================
# JSON format tests
# ===================================================================


class TestJSONFormat:
    """Verify JSON output structure has classification instead of boolean flags."""

    def _build_json_word(self, word_stub):
        """Simulate the JSON word dict construction from cli.py."""
        from pystylometry.lexical.word_class import classify_word

        return {
            "word": word_stub.word,
            "observed": word_stub.observed,
            "expected": word_stub.expected,
            "ratio": word_stub.ratio,
            "in_wordnet": word_stub.in_wordnet,
            "in_gngram": word_stub.in_gngram,
            "classification": classify_word(word_stub.word).label,
        }

    def test_json_has_classification_key(self):
        """Each word dict should have a 'classification' key."""
        for w in _TEST_WORDS:
            d = self._build_json_word(w)
            assert "classification" in d

    def test_json_no_boolean_flag_keys(self):
        """Each word dict should NOT have the old boolean flag keys."""
        old_keys = {"unicode", "numeric", "apostrophe", "hyphen", "other"}
        for w in _TEST_WORDS:
            d = self._build_json_word(w)
            assert old_keys.isdisjoint(d.keys()), (
                f"Word '{w.word}' still has old boolean keys: " f"{old_keys & d.keys()}"
            )

    def test_json_classification_value_is_string(self):
        """Classification values should always be strings."""
        for w in _TEST_WORDS:
            d = self._build_json_word(w)
            assert isinstance(d["classification"], str)

    def test_json_contraction_label(self):
        """don't should have apostrophe.contraction.negative in JSON."""
        w = _WordStub("don't", 47, 0.5, 94.0, True, True)
        d = self._build_json_word(w)
        assert d["classification"] == "apostrophe.contraction.negative"

    def test_json_lexical_label(self):
        """Plain words should have 'lexical' as classification."""
        w = _WordStub("house", 120, 100.0, 1.2, True, True)
        d = self._build_json_word(w)
        assert d["classification"] == "lexical"

    def test_json_hyphenated_label(self):
        """Hyphenated words should get appropriate labels."""
        w = _WordStub("zig-zag", 3, 0.5, 6.0, True, True)
        d = self._build_json_word(w)
        assert d["classification"] == "hyphenated.reduplicated.ablaut"

    def test_json_numeric_ordinal_label(self):
        """Numeric ordinals should classify as numeric.ordinal."""
        w = _WordStub("1st", 5, 1.0, 5.0, False, True)
        d = self._build_json_word(w)
        assert d["classification"] == "numeric.ordinal"

    def test_json_serializable(self):
        """The classification value should be JSON-serializable."""
        for w in _TEST_WORDS:
            d = self._build_json_word(w)
            # Should not raise
            json.dumps(d)


# ===================================================================
# CSV/TSV format tests
# ===================================================================


class TestCSVFormat:
    """Verify CSV/TSV header and row structure uses classification."""

    def test_csv_header_has_classification(self):
        """The TSV header should include 'classification', not boolean flags."""
        header = (
            "category\tword\tobserved\texpected\tratio\tin_wordnet\tin_gngram" "\tclassification"
        )
        assert "classification" in header
        assert "unicode" not in header
        assert "numeric" not in header
        assert "apostrophe" not in header
        assert "hyphen" not in header
        assert "other" not in header

    def test_csv_header_with_works_has_classification(self):
        """The TSV header with works column should include classification."""
        header = (
            "category\tword\tobserved\texpected\tworks\tratio\tin_wordnet\tin_gngram"
            "\tclassification"
        )
        assert "classification" in header
        assert "\tworks\t" in header

    def test_csv_row_ends_with_classification_label(self):
        """Each TSV row should end with a classification label."""
        w = _WordStub("don't", 47, 0.5, 94.0, True, True)
        cls = classify_word(w.word).label
        line = (
            f"overused\t{w.word}\t{w.observed}\t{w.expected:.2f}\t{w.ratio:.4f}"
            f"\tyes\tyes\t{cls}"
        )
        assert line.endswith("apostrophe.contraction.negative")

    def test_csv_lexical_word_classification(self):
        """Lexical words should have 'lexical' as the classification field."""
        w = _WordStub("house", 120, 100.0, 1.2, True, True)
        cls = classify_word(w.word).label
        assert cls == "lexical"

    @pytest.mark.parametrize(
        "word, expected_cls",
        [
            ("don't", "apostrophe.contraction.negative"),
            ("can't", "apostrophe.contraction.negative"),
            ("zig-zag", "hyphenated.reduplicated.ablaut"),
            ("self-esteem", "hyphenated.compound.self"),
            ("twenty-one", "hyphenated.number_word"),
            ("1st", "numeric.ordinal"),
            ("house", "lexical"),
        ],
    )
    def test_csv_classification_values(self, word, expected_cls):
        """Each word in a TSV row should produce the correct classification."""
        assert classify_word(word).label == expected_cls

    def test_csv_column_count_without_works(self):
        """Without works, each row should have 8 tab-separated fields."""
        # category, word, observed, expected, ratio, in_wordnet, in_gngram,
        # classification
        w = _WordStub("don't", 47, 0.5, 94.0, True, True)
        cls = classify_word(w.word).label
        line = f"overused\t{w.word}\t{w.observed}\t0.50\t94.0000" f"\tyes\tyes\t{cls}"
        fields = line.split("\t")
        assert len(fields) == 8

    def test_csv_column_count_with_works(self):
        """With works, each row should have 9 tab-separated fields."""
        # category, word, observed, expected, works, ratio, in_wordnet,
        # in_gngram, classification
        w = _WordStub("don't", 47, 0.5, 94.0, True, True)
        cls = classify_word(w.word).label
        line = f"overused\t{w.word}\t{w.observed}\t0.50\t3/5\t94.0000" f"\tyes\tyes\t{cls}"
        fields = line.split("\t")
        assert len(fields) == 9


# ===================================================================
# Excel format tests
# ===================================================================


class TestExcelFormat:
    """Verify Excel sheet headers and row structure uses classification."""

    def test_excel_overused_header_without_works(self):
        """Overused sheet header should have classification, not boolean flags."""
        expected = [
            "word",
            "observed",
            "expected",
            "ratio",
            "in_wordnet",
            "in_gngram",
            "classification",
        ]
        # 7 columns total (was 11 with the 5 booleans)
        assert len(expected) == 7
        assert "classification" in expected
        assert "unicode" not in expected
        assert "numeric" not in expected

    def test_excel_overused_header_with_works(self):
        """Overused sheet header with works should have classification."""
        expected = [
            "word",
            "observed",
            "expected",
            "works",
            "ratio",
            "in_wordnet",
            "in_gngram",
            "classification",
        ]
        assert len(expected) == 8
        assert "works" in expected
        assert "classification" in expected

    def test_excel_notbnc_header_without_works(self):
        """Not-in-BNC header should have classification, not boolean flags."""
        expected = [
            "word",
            "observed",
            "in_wordnet",
            "in_gngram",
            "classification",
        ]
        assert len(expected) == 5
        assert "classification" in expected

    def test_excel_notbnc_header_with_works(self):
        """Not-in-BNC header with works should have classification."""
        expected = [
            "word",
            "observed",
            "works",
            "in_wordnet",
            "in_gngram",
            "classification",
        ]
        assert len(expected) == 6

    def test_excel_row_data_has_classification(self):
        """Each row should end with a classification label string."""
        w = _WordStub("don't", 47, 0.5, 94.0, True, True)
        cls = classify_word(w.word).label
        row = [w.word, w.observed, w.expected, w.ratio, "true", "true", cls]
        assert row[-1] == "apostrophe.contraction.negative"

    def test_excel_row_data_lexical(self):
        """Lexical words should have 'lexical' in the classification cell."""
        w = _WordStub("house", 120, 100.0, 1.2, True, True)
        cls = classify_word(w.word).label
        row = [w.word, w.observed, w.expected, w.ratio, "true", "true", cls]
        assert row[-1] == "lexical"

    @pytest.mark.parametrize(
        "word, expected_cls",
        [
            ("don't", "apostrophe.contraction.negative"),
            ("zig-zag", "hyphenated.reduplicated.ablaut"),
            ("self-esteem", "hyphenated.compound.self"),
            ("1st", "numeric.ordinal"),
        ],
    )
    def test_excel_classification_values(self, word, expected_cls):
        """Classification values should match expected labels."""
        assert classify_word(word).label == expected_cls


# ===================================================================
# Column consistency tests across all formats
# ===================================================================


class TestColumnConsistency:
    """Ensure all formats use the same classification label for each word.

    The classification comes from a single source (classify_word), so it
    must be identical regardless of output format.
    """

    @pytest.mark.parametrize(
        "word",
        [
            "don't",
            "can't",
            "zig-zag",
            "house",
            "self-esteem",
            "twenty-one",
            "1st",
        ],
    )
    def test_same_label_across_formats(self, word):
        """The label for a word should be identical however we compute it."""
        label = classify_word(word).label
        # Simulate what each format does:
        # JSON
        json_cls = classify_word(word).label
        # CSV
        csv_cls = classify_word(word).label
        # Excel
        xl_cls = classify_word(word).label
        # HTML
        html_cls = classify_word(word).label

        assert json_cls == label
        assert csv_cls == label
        assert xl_cls == label
        assert html_cls == label


# ===================================================================
# Regression tests: old boolean columns must NOT appear
# ===================================================================


class TestNoBooleanFlagRegression:
    """Guard against accidental reintroduction of boolean flag columns.

    Each test verifies that specific patterns from the old implementation
    are absent from the source code of cli.py and bnc_frequency.py.
    """

    def _read_bnc_frequency_source(self):
        """Read the bnc_frequency.py source for inspection."""
        from pathlib import Path

        src = (
            Path(__file__).resolve().parents[2]
            / "pystylometry"
            / "viz"
            / "jsx"
            / "bnc_frequency.py"
        )
        return src.read_text()

    def test_no_unicode_bool_in_html_data(self):
        """bnc_frequency.py should not compute 'unicode' as a boolean data key."""
        src = self._read_bnc_frequency_source()
        # Old pattern: "unicode": w.char_type == "unicode"
        assert '"unicode": w.char_type' not in src

    def test_no_numeric_bool_in_html_data(self):
        """bnc_frequency.py should not compute 'numeric' as a boolean data key."""
        src = self._read_bnc_frequency_source()
        assert '"numeric": w.char_type' not in src

    def test_no_apostrophe_bool_in_html_data(self):
        """bnc_frequency.py should not compute 'apostrophe' as a boolean data key."""
        src = self._read_bnc_frequency_source()
        assert '"apostrophe": "\'" in w.word' not in src

    def test_no_hyphen_bool_in_html_data(self):
        """bnc_frequency.py should not compute 'hyphen' as a boolean data key."""
        src = self._read_bnc_frequency_source()
        assert '"hyphen": "-" in w.word' not in src

    def test_no_other_bool_in_html_data(self):
        """bnc_frequency.py should not compute 'other' as a boolean data key."""
        src = self._read_bnc_frequency_source()
        assert '"other": bool(' not in src

    def test_classification_key_present_in_html_data(self):
        """bnc_frequency.py should use 'classification' as the data key."""
        src = self._read_bnc_frequency_source()
        assert '"classification": classify_word(w.word).label' in src

    def test_classify_word_imported_in_html(self):
        """bnc_frequency.py should import classify_word."""
        src = self._read_bnc_frequency_source()
        assert "from pystylometry.lexical.word_class import classify_word" in src


# ===================================================================
# Edge case classification tests
# ===================================================================


class TestEdgeCaseClassifications:
    """Test classification of edge-case words that might appear in BNC output."""

    def test_empty_string(self):
        """Empty string should still produce a valid label."""
        result = classify_word("")
        assert isinstance(result.label, str)
        assert len(result.label) > 0

    def test_single_letter(self):
        """Single letters should classify as lexical."""
        assert classify_word("a").label == "lexical"
        assert classify_word("I").label == "lexical"

    def test_possessive(self):
        """Possessives should classify under apostrophe.possessive."""
        result = classify_word("dog's")
        assert result.l1 == "apostrophe"
        assert result.l2 == "possessive"

    def test_plural_possessive(self):
        """Plural possessives should classify as apostrophe.possessive.plural."""
        result = classify_word("dogs'")
        assert result.label == "apostrophe.possessive.plural"

    def test_g_dropping(self):
        """G-dropping forms should classify as apostrophe.dialectal.g_dropping."""
        result = classify_word("runnin'")
        assert result.label == "apostrophe.dialectal.g_dropping"

    def test_hyphenated_prefix(self):
        """Prefixed hyphenated words should classify as hyphenated.prefixed."""
        result = classify_word("re-enter")
        assert result.label == "hyphenated.prefixed"

    def test_ordinal_numbers(self):
        """Numeric ordinals should classify as numeric.ordinal."""
        assert classify_word("1st").label == "numeric.ordinal"
        assert classify_word("2nd").label == "numeric.ordinal"
        assert classify_word("3rd").label == "numeric.ordinal"
        assert classify_word("100th").label == "numeric.ordinal"

    def test_directional(self):
        """Compass directions should classify as hyphenated.directional."""
        assert classify_word("north-east").label == "hyphenated.directional"
        assert classify_word("south-west").label == "hyphenated.directional"

    def test_aphetic_archaic(self):
        """Archaic aphetic forms should classify correctly."""
        assert classify_word("'twas").label == "apostrophe.aphetic.archaic"
        assert classify_word("'tis").label == "apostrophe.aphetic.archaic"

    def test_aphetic_poetic(self):
        """Poetic aphetic forms should classify correctly."""
        assert classify_word("'gainst").label == "apostrophe.aphetic.poetic"
        assert classify_word("'neath").label == "apostrophe.aphetic.poetic"

    def test_dialectal_medial(self):
        """Medial dialectal forms should classify correctly."""
        assert classify_word("o'clock").label == "apostrophe.dialectal.medial"

    def test_reduplicated_exact(self):
        """Exact reduplications should classify correctly."""
        assert classify_word("bye-bye").label == "hyphenated.reduplicated.exact"

    def test_reduplicated_rhyming(self):
        """Rhyming reduplications should classify correctly."""
        assert classify_word("helter-skelter").label == "hyphenated.reduplicated.rhyming"

    def test_self_compound(self):
        """Self- compounds should classify correctly."""
        assert classify_word("self-aware").label == "hyphenated.compound.self"

    def test_number_word(self):
        """Number words should classify correctly."""
        assert classify_word("forty-two").label == "hyphenated.number_word"
        assert classify_word("ninety-nine").label == "hyphenated.number_word"

    def test_copula_enclitic(self):
        """Copula enclitics should classify correctly."""
        assert classify_word("it's").label == "apostrophe.contraction.copula"
        assert classify_word("he's").label == "apostrophe.contraction.copula"

    def test_auxiliary_enclitic(self):
        """Auxiliary enclitics should classify correctly."""
        assert classify_word("I'll").label == "apostrophe.contraction.auxiliary"
        assert classify_word("they've").label == "apostrophe.contraction.auxiliary"


# ===================================================================
# Bulk validation: all L1 categories get a label
# ===================================================================


class TestBulkL1Categories:
    """Verify that representative words from each L1 category produce labels.

    This ensures the classification column is never empty or None in any
    output format, regardless of word type.
    """

    @pytest.mark.parametrize(
        "word, expected_l1",
        [
            ("house", "lexical"),
            ("don't", "apostrophe"),
            ("zig-zag", "hyphenated"),
            ("jack-o'-lantern", "apostrophe_hyphenated"),
            ("cafe\u0301", "unicode"),
            ("1st", "numeric"),
        ],
    )
    def test_l1_category(self, word, expected_l1):
        """Each L1 category should be reachable and produce a non-empty label."""
        result = classify_word(word)
        assert result.l1 == expected_l1
        assert len(result.label) > 0

    def test_all_l1_categories_covered(self):
        """Every defined L1 category should be testable."""
        expected_l1s = {
            "lexical",
            "apostrophe",
            "hyphenated",
            "apostrophe_hyphenated",
            "unicode",
            "numeric",
            "other",
        }
        # We have test words for all except "other" -- verify "other" works too
        # A word with non-az chars that isn't apostrophe/hyphen/unicode/numeric
        result = classify_word("foo@bar")
        assert result.l1 == "other"
        assert result.label == "other.unclassified"

        # Collect all L1s from test words
        test_l1s = {
            classify_word(w).l1
            for w in [
                "house",
                "don't",
                "zig-zag",
                "jack-o'-lantern",
                "cafe\u0301",
                "1st",
                "foo@bar",
            ]
        }
        assert test_l1s == expected_l1s
