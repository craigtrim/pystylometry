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
) -> None:
    """Write comparative mega meta-analysis to an Excel workbook.

    Creates sheets:
      - ``N-grams``: entropy and perplexity per author (authors as rows)
      - ``Prosody``: rhythm and prosody metrics per author (if available)
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

    wb.save(output_path)
