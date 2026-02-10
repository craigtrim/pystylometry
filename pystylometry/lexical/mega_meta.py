"""Mega meta-analysis: comparative summary across multiple mega Excel files.

Reads the N-grams and Prosody sheets from each per-author mega Excel file
(as produced by ``mega``) and aggregates metrics into side-by-side
comparative tables.

Usage (via CLI):
    mega-meta --input-dir ~/Desktop/mega-output --output-file /tmp/mega-comparison.xlsx
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
NGRAM_METRIC_LABELS = [
    "Char Bigram Entropy",
    "Char Bigram Perplexity",
    "Word Bigram Entropy",
    "Word Bigram Perplexity",
]

PROSODY_METRIC_LABELS = [
    "Mean Syllables/Word",
    "Syllable Std Dev",
    "Polysyllabic Ratio (3+)",
    "Monosyllabic Ratio",
    "Rhythmic Regularity",
    "Alliteration Density",
    "Assonance Density",
    "Consonance Density",
    "Sentence Rhythm Score",
    "Avg Consonant Cluster",
]

# Syllable distribution buckets written by mega's Prosody sheet (1–11, 12+)
SYLLABLE_BUCKETS = [str(b) for b in range(1, 12)] + ["12+"]

CHARACTER_METRIC_LABELS = [
    "Avg Word Length",
    "Avg Sentence Length (chars)",
    "Punctuation Density",
    "Punctuation Variety",
    "Vowel:Consonant Ratio",
    "Digit Ratio",
    "Uppercase Ratio",
    "Whitespace Ratio",
]

_ALIGN = Alignment(horizontal="center", vertical="center")
_ALIGN_LEFT = Alignment(horizontal="left", vertical="center")
_FONT_HEADER = Font(bold=True, size=14)
_FILL_HEADER = PatternFill(start_color="D9E2F3", end_color="D9E2F3", fill_type="solid")


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
@dataclass
class NgramSummary:
    """N-gram entropy/perplexity stats for one author."""

    author: str
    char_bigram_entropy: float
    char_bigram_perplexity: float
    word_bigram_entropy: float
    word_bigram_perplexity: int


@dataclass
class ProsodySummary:
    """Prosody metrics for one author."""

    author: str
    mean_syllables_per_word: float
    syllable_std_dev: float
    polysyllabic_ratio: float
    monosyllabic_ratio: float
    rhythmic_regularity: float
    alliteration_density: float
    assonance_density: float
    consonance_density: float
    sentence_rhythm_score: float
    avg_consonant_cluster: float


@dataclass
class SyllableSummary:
    """Total syllable counts per bucket for one author.

    Buckets are "1" through "11" and "12+", matching the syllable
    distribution section of the mega Prosody sheet.
    """

    author: str
    totals: dict[str, int]  # bucket -> total count


@dataclass
class CharacterSummary:
    """Character-level metrics for one author."""

    author: str
    avg_word_length: float
    avg_sentence_length_chars: float
    punctuation_density: float
    punctuation_variety: float
    vowel_consonant_ratio: float
    digit_ratio: float
    uppercase_ratio: float
    whitespace_ratio: float


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------
_EXPECTED_METRICS = {
    "Char Bigram Entropy": "char_bigram_entropy",
    "Char Bigram Perplexity": "char_bigram_perplexity",
    "Word Bigram Entropy": "word_bigram_entropy",
    "Word Bigram Perplexity": "word_bigram_perplexity",
}


def read_ngram_summary(xlsx_path: Path) -> NgramSummary | None:
    """Read N-gram stats from a single mega Excel file.

    Returns ``None`` if the file cannot be parsed (missing N-grams sheet,
    unexpected layout, etc.).
    """
    wb = load_workbook(xlsx_path, read_only=True, data_only=True)
    try:
        if "N-grams" not in wb.sheetnames:
            return None
        ws = wb["N-grams"]

        values: dict[str, float] = {}
        for row in ws.iter_rows(min_row=1, max_row=10, min_col=1, max_col=2):
            label = row[0].value
            val = row[1].value if len(row) > 1 else None
            if label and str(label).strip() in _EXPECTED_METRICS and val is not None:
                try:
                    field = _EXPECTED_METRICS[str(label).strip()]
                    v = float(val)
                    values[field] = round(v) if field == "word_bigram_perplexity" else v
                except (ValueError, TypeError):
                    pass

        if len(values) != len(_EXPECTED_METRICS):
            return None

        return NgramSummary(author=xlsx_path.stem, **values)
    finally:
        wb.close()


def read_ngram_summaries(input_dir: Path) -> list[NgramSummary]:
    """Read all mega Excel files from a directory tree and return sorted summaries.

    Walks subdirectories (e.g. decade folders) to find all .xlsx files.
    """
    summaries: list[NgramSummary] = []
    for xlsx_path in sorted(input_dir.rglob("*.xlsx")):
        if xlsx_path.name.startswith("~$"):
            continue
        result = read_ngram_summary(xlsx_path)
        if result is not None:
            summaries.append(result)
    return sorted(summaries, key=lambda s: s.author.lower())


# ---------------------------------------------------------------------------
# Read – Prosody
# ---------------------------------------------------------------------------
_EXPECTED_PROSODY = {
    "Mean Syllables/Word": "mean_syllables_per_word",
    "Syllable Std Dev": "syllable_std_dev",
    "Polysyllabic Ratio (3+)": "polysyllabic_ratio",
    "Monosyllabic Ratio": "monosyllabic_ratio",
    "Rhythmic Regularity": "rhythmic_regularity",
    "Alliteration Density": "alliteration_density",
    "Assonance Density": "assonance_density",
    "Consonance Density": "consonance_density",
    "Sentence Rhythm Score": "sentence_rhythm_score",
    "Avg Consonant Cluster": "avg_consonant_cluster",
}


def read_prosody_summary(xlsx_path: Path) -> ProsodySummary | None:
    """Read Prosody stats from a single mega Excel file.

    Returns ``None`` if the Prosody sheet is missing or incomplete.
    """
    wb = load_workbook(xlsx_path, read_only=True, data_only=True)
    try:
        if "Prosody" not in wb.sheetnames:
            return None
        ws = wb["Prosody"]

        values: dict[str, float] = {}
        for row in ws.iter_rows(min_row=1, max_row=20, min_col=1, max_col=2):
            label = row[0].value
            val = row[1].value if len(row) > 1 else None
            if label and str(label).strip() in _EXPECTED_PROSODY and val is not None:
                try:
                    field = _EXPECTED_PROSODY[str(label).strip()]
                    values[field] = float(val)
                except (ValueError, TypeError):
                    pass

        if len(values) != len(_EXPECTED_PROSODY):
            return None

        return ProsodySummary(author=xlsx_path.stem, **values)
    finally:
        wb.close()


def read_prosody_summaries(input_dir: Path) -> list[ProsodySummary]:
    """Read Prosody sheets from all mega Excel files in a directory tree."""
    summaries: list[ProsodySummary] = []
    for xlsx_path in sorted(input_dir.rglob("*.xlsx")):
        if xlsx_path.name.startswith("~$"):
            continue
        result = read_prosody_summary(xlsx_path)
        if result is not None:
            summaries.append(result)
    return sorted(summaries, key=lambda s: s.author.lower())


# ---------------------------------------------------------------------------
# Read – Syllable Distribution
# ---------------------------------------------------------------------------
def read_syllable_summary(xlsx_path: Path) -> SyllableSummary | None:
    """Read syllable-count totals from the Prosody sheet's distribution table.

    The mega Prosody sheet contains a "Syllable Distribution" section with
    rows like::

        Syllables | Total | Unique
        1         | 54321 | 890
        2         | 23456 | 567
        ...
        12+       | 3     | 2

    We extract the "Total" column (column B) keyed by the bucket label
    (column A).  Returns ``None`` if no distribution data is found.

    Note:
        Backwards-compatible: also accepts the older "8+" overflow bucket
        from mega files generated before the extension to 12+.
    """
    wb = load_workbook(xlsx_path, read_only=True, data_only=True)
    try:
        if "Prosody" not in wb.sheetnames:
            return None
        ws = wb["Prosody"]

        # Scan for the "Syllables" sub-header row, then read data rows below it
        in_distribution = False
        totals: dict[str, int] = {}
        for row in ws.iter_rows(min_col=1, max_col=3):
            label = str(row[0].value).strip() if row[0].value is not None else ""

            if label == "Syllables":
                in_distribution = True
                continue

            if in_distribution:
                if label in {str(b) for b in range(1, 12)} | {"12+", "8+"}:
                    val = row[1].value if len(row) > 1 else None
                    try:
                        totals[label] = int(val) if val is not None else 0
                    except (ValueError, TypeError):
                        totals[label] = 0
                elif label and label not in {"", "None"}:
                    # Past the distribution section
                    break

        if not totals:
            return None

        return SyllableSummary(author=xlsx_path.stem, totals=totals)
    finally:
        wb.close()


def read_syllable_summaries(input_dir: Path) -> list[SyllableSummary]:
    """Read syllable distributions from all mega Excel files in a directory tree."""
    summaries: list[SyllableSummary] = []
    for xlsx_path in sorted(input_dir.rglob("*.xlsx")):
        if xlsx_path.name.startswith("~$"):
            continue
        result = read_syllable_summary(xlsx_path)
        if result is not None:
            summaries.append(result)
    return sorted(summaries, key=lambda s: s.author.lower())


# ---------------------------------------------------------------------------
# Read – Character Metrics
# ---------------------------------------------------------------------------
_EXPECTED_CHARACTER = {
    "Avg Word Length": "avg_word_length",
    "Avg Sentence Length (chars)": "avg_sentence_length_chars",
    "Punctuation Density": "punctuation_density",
    "Punctuation Variety": "punctuation_variety",
    "Vowel:Consonant Ratio": "vowel_consonant_ratio",
    "Digit Ratio": "digit_ratio",
    "Uppercase Ratio": "uppercase_ratio",
    "Whitespace Ratio": "whitespace_ratio",
}


def read_character_summary(xlsx_path: Path) -> CharacterSummary | None:
    """Read character-level metrics from a single mega Excel file.

    The Character sheet uses a two-column Metric/Value layout.
    Returns ``None`` if the sheet is missing or incomplete.
    """
    wb = load_workbook(xlsx_path, read_only=True, data_only=True)
    try:
        if "Character" not in wb.sheetnames:
            return None
        ws = wb["Character"]

        values: dict[str, float] = {}
        for row in ws.iter_rows(min_row=1, max_row=20, min_col=1, max_col=2):
            label = row[0].value
            val = row[1].value if len(row) > 1 else None
            if label and str(label).strip() in _EXPECTED_CHARACTER and val is not None:
                try:
                    field = _EXPECTED_CHARACTER[str(label).strip()]
                    values[field] = float(val)
                except (ValueError, TypeError):
                    pass

        if len(values) != len(_EXPECTED_CHARACTER):
            return None

        return CharacterSummary(author=xlsx_path.stem, **values)
    finally:
        wb.close()


def read_character_summaries(input_dir: Path) -> list[CharacterSummary]:
    """Read Character sheets from all mega Excel files in a directory tree."""
    summaries: list[CharacterSummary] = []
    for xlsx_path in sorted(input_dir.rglob("*.xlsx")):
        if xlsx_path.name.startswith("~$"):
            continue
        result = read_character_summary(xlsx_path)
        if result is not None:
            summaries.append(result)
    return sorted(summaries, key=lambda s: s.author.lower())


# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------
def _auto_width(ws: object, min_w: int = 15, max_w: int = 40) -> None:
    """Set reasonable column widths."""
    for col in ws.columns:
        letter = col[0].column_letter
        lengths = [len(str(c.value)) for c in col if c.value is not None]
        best = max(lengths) if lengths else min_w
        ws.column_dimensions[letter].width = min(max(best + 2, min_w), max_w)


def _style_sheet(ws: object) -> None:
    """Apply consistent header + data styling to a sheet."""
    for cell in ws[1]:
        cell.font = _FONT_HEADER
        cell.fill = _FILL_HEADER
        cell.alignment = _ALIGN

    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = _ALIGN
        row[0].alignment = _ALIGN_LEFT

    ws.row_dimensions[1].height = 25
    for r in range(2, ws.max_row + 1):
        ws.row_dimensions[r].height = 20

    _auto_width(ws)


def write_mega_meta_excel(
    summaries: list[NgramSummary],
    output_path: Path,
    prosody_summaries: list[ProsodySummary] | None = None,
    syllable_summaries: list[SyllableSummary] | None = None,
    character_summaries: list[CharacterSummary] | None = None,
) -> None:
    """Write comparative mega meta-analysis to an Excel workbook.

    Creates sheets:
      - ``N-grams``: entropy and perplexity per author (authors as rows)
      - ``Prosody``: rhythm and prosody metrics per author (if available)
      - ``Syllables``: total syllable counts per bucket (if available)
      - ``Character``: character-level metrics per author (if available)
    """
    wb = Workbook()
    wb.remove(wb.active)

    # ── N-grams tab ───────────────────────────────────────────────────────
    ws = wb.create_sheet("N-grams")
    ws.append(["Author"] + NGRAM_METRIC_LABELS)

    for s in summaries:
        ws.append([
            s.author,
            s.char_bigram_entropy,
            s.char_bigram_perplexity,
            s.word_bigram_entropy,
            s.word_bigram_perplexity,
        ])

    _style_sheet(ws)

    # Number formats: per-column (col 5 = Word Bigram Perplexity is integer)
    _NGRAM_COL_FORMATS = {2: "#,##0.0000", 3: "#,##0.0000", 4: "#,##0.0000", 5: "#,##0"}
    for col_idx, fmt in _NGRAM_COL_FORMATS.items():
        for row_idx in range(2, ws.max_row + 1):
            ws.cell(row=row_idx, column=col_idx).number_format = fmt

    # ── Prosody tab ───────────────────────────────────────────────────────
    if prosody_summaries:
        ws_p = wb.create_sheet("Prosody")
        ws_p.append(["Author"] + PROSODY_METRIC_LABELS)

        for p in prosody_summaries:
            ws_p.append([
                p.author,
                p.mean_syllables_per_word,
                p.syllable_std_dev,
                p.polysyllabic_ratio,
                p.monosyllabic_ratio,
                p.rhythmic_regularity,
                p.alliteration_density,
                p.assonance_density,
                p.consonance_density,
                p.sentence_rhythm_score,
                p.avg_consonant_cluster,
            ])

        _style_sheet(ws_p)

        # Number formats: all prosody metrics are floats
        for col_idx in range(2, len(PROSODY_METRIC_LABELS) + 2):
            for row_idx in range(2, ws_p.max_row + 1):
                ws_p.cell(row=row_idx, column=col_idx).number_format = "#,##0.0000"

    # ── Syllables tab ──────────────────────────────────────────────────────
    # Authors as rows, syllable buckets (1–7, 8+) as columns, total counts
    if syllable_summaries:
        ws_s = wb.create_sheet("Syllables")
        ws_s.append(["Author"] + SYLLABLE_BUCKETS)

        for s in syllable_summaries:
            ws_s.append(
                [s.author] + [s.totals.get(b, 0) for b in SYLLABLE_BUCKETS]
            )

        _style_sheet(ws_s)

        # Number formats: integer with thousand separators
        for col_idx in range(2, len(SYLLABLE_BUCKETS) + 2):
            for row_idx in range(2, ws_s.max_row + 1):
                ws_s.cell(row=row_idx, column=col_idx).number_format = "#,##0"

    # ── Character tab ──────────────────────────────────────────────────────
    if character_summaries:
        ws_c = wb.create_sheet("Character")
        ws_c.append(["Author"] + CHARACTER_METRIC_LABELS)

        for c in character_summaries:
            ws_c.append([
                c.author,
                c.avg_word_length,
                c.avg_sentence_length_chars,
                c.punctuation_density,
                c.punctuation_variety,
                c.vowel_consonant_ratio,
                c.digit_ratio,
                c.uppercase_ratio,
                c.whitespace_ratio,
            ])

        _style_sheet(ws_c)

        for col_idx in range(2, len(CHARACTER_METRIC_LABELS) + 2):
            for row_idx in range(2, ws_c.max_row + 1):
                ws_c.cell(row=row_idx, column=col_idx).number_format = "#,##0.0000"

    wb.save(output_path)
