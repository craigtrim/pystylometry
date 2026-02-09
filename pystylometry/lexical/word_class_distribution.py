"""Word class distribution: descriptive statistics for the morphological classifier.

Classifies every word in a text using :func:`classify_word` and produces a
distribution table showing the percentage of words in each classification
category.  Percentages must sum to 100 %.  If they don't, it reveals
unclassified gaps in the taxonomy -- making this both an analytical tool and
a defect detector for the word-class module.

Output is a flat table sorted alphabetically by label:

    label                              count   percentage
    apostrophe.contraction.negative      203     0.3165
    lexical                            62134    96.8217

Related GitHub Issue:
    #54 -- Add word-class distribution report
    https://github.com/craigtrim/pystylometry/issues/54

Example:
    >>> from pystylometry.lexical.word_class_distribution import (
    ...     compute_word_class_distribution,
    ... )
    >>> result = compute_word_class_distribution("The cat sat on the mat.")
    >>> result.percentage_sum
    100.0
    >>> result.classifications[0].label
    'lexical'
"""

from __future__ import annotations

import re
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field

from .bnc_frequency import _normalize_apostrophes, _normalize_dashes
from .word_class import classify_word


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RunStats:
    """Descriptive statistics for contiguous run lengths of a classification.

    A "run" is a maximal contiguous sequence of tokens sharing the same label.
    For example, in ``[lexical, lexical, apostrophe, lexical]`` the label
    ``lexical`` has runs of length [2, 1] and ``apostrophe`` has runs of [1].

    Attributes:
        mean: Mean run length.
        median: Median run length.
        mode: Most frequent run length (smallest if tied).
        min: Shortest run.
        max: Longest run.
        runs: Number of distinct runs.
    """

    mean: float
    median: float
    mode: int
    min: int
    max: int
    runs: int


@dataclass(frozen=True)
class ClassificationEntry:
    """Single row in the distribution table.

    Attributes:
        label: Dot-separated classification path (e.g. ``apostrophe.contraction.negative``).
        count: Number of word tokens classified with this label.
        unique: Number of distinct word types classified with this label.
        percentage: ``count / total_words * 100``.
        run_stats: Descriptive statistics for contiguous sequence lengths.
    """

    label: str
    count: int
    unique: int
    percentage: float
    run_stats: RunStats | None = None


@dataclass(frozen=True)
class WordClassDistribution:
    """Complete distribution result.

    Attributes:
        total_words: Total tokens classified.
        unique_labels: Number of distinct classification labels.
        classifications: Entries sorted alphabetically by label.
        percentage_sum: Sum of all percentages (should be 100.0).
        max_run_examples: For labels where run_max < 10, a mapping from
            label to a list of token sequences (each a list of str) that
            achieved the maximum run length.  Useful for inspecting what
            actual words formed the longest clusters.
        tokens_by_label: Mapping from classification label to the first
            ``TOKEN_SAMPLE_LIMIT`` tokens (in order of appearance) that
            received that classification.  The ``lexical`` label is excluded
            because it typically dominates (>95 % of tokens) and would dwarf
            every other column.
    """

    total_words: int
    unique_labels: int
    classifications: list[ClassificationEntry]
    percentage_sum: float
    max_run_examples: dict[str, list[list[str]]] = field(default_factory=dict)
    tokens_by_label: dict[str, list[str]] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Punctuation-stripping regex (matches BNC tokenization)
# ---------------------------------------------------------------------------
_STRIP_PUNCT = re.compile(r"^[^\w]+|[^\w]+$")

# Maximum number of tokens to collect per label in tokens_by_label.
TOKEN_SAMPLE_LIMIT = 5_000


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_word_class_distribution(text: str) -> WordClassDistribution:
    """Classify every word and produce a distribution table.

    Tokenization matches the BNC frequency pipeline:

    1. Normalize apostrophe variants to ASCII ``'``
    2. Normalize dashes/hyphens (em-dashes → space, Unicode hyphens → ASCII ``-``)
    3. Split on whitespace
    4. Strip leading / trailing non-word characters
    5. Lowercase
    6. Classify with :func:`classify_word`

    Args:
        text: The full text to analyse.  May be empty.

    Returns:
        A :class:`WordClassDistribution` with entries sorted a-z by label.

    Related GitHub Issue:
        #54 -- Add word-class distribution report
        https://github.com/craigtrim/pystylometry/issues/54
    """
    if not text or not text.strip():
        return WordClassDistribution(
            total_words=0,
            unique_labels=0,
            classifications=[],
            percentage_sum=0.0,
        )

    # -- Tokenize (mirrors bnc_frequency.py pipeline) -----------------------
    normalized = _normalize_dashes(_normalize_apostrophes(text))
    tokens: list[str] = []
    for raw in normalized.split():
        cleaned = _STRIP_PUNCT.sub("", raw).lower()
        if cleaned:
            tokens.append(cleaned)

    total = len(tokens)
    if total == 0:
        return WordClassDistribution(
            total_words=0,
            unique_labels=0,
            classifications=[],
            percentage_sum=0.0,
        )

    # -- Classify every token and keep the label sequence --------------------
    labels_seq: list[str] = []
    label_counts: Counter[str] = Counter()
    unique_by_label: dict[str, set[str]] = defaultdict(set)
    tokens_by_label: dict[str, list[str]] = defaultdict(list)
    for token in tokens:
        lbl = classify_word(token).label
        labels_seq.append(lbl)
        label_counts[lbl] += 1
        unique_by_label[lbl].add(token)
        # Collect token samples for every label except lexical (too large).
        if lbl != "lexical" and len(tokens_by_label[lbl]) < TOKEN_SAMPLE_LIMIT:
            tokens_by_label[lbl].append(token)

    # -- Compute contiguous run lengths per label ---------------------------
    # Each run is stored as (start_index, length) so we can extract tokens.
    run_records: dict[str, list[tuple[int, int]]] = defaultdict(list)
    if labels_seq:
        current_label = labels_seq[0]
        current_start = 0
        current_len = 1
        for i, lbl in enumerate(labels_seq[1:], start=1):
            if lbl == current_label:
                current_len += 1
            else:
                run_records[current_label].append((current_start, current_len))
                current_label = lbl
                current_start = i
                current_len = 1
        run_records[current_label].append((current_start, current_len))

    # -- Build sorted entries -----------------------------------------------
    max_run_examples: dict[str, list[list[str]]] = {}

    entries: list[ClassificationEntry] = []
    for label in sorted(label_counts):
        count = label_counts[label]
        pct = (count / total) * 100
        records = run_records.get(label, [(0, 1)])
        lengths = [length for _, length in records]
        rs = RunStats(
            mean=round(statistics.mean(lengths), 4),
            median=round(statistics.median(lengths), 4),
            mode=min(statistics.multimode(lengths)),
            min=min(lengths),
            max=max(lengths),
            runs=len(lengths),
        )
        entries.append(ClassificationEntry(
            label=label, count=count, unique=len(unique_by_label[label]),
            percentage=pct, run_stats=rs,
        ))

        # Collect token sequences for max-length runs when max < 10
        # (lexical runs can be hundreds of tokens — not useful to display)
        if rs.max > 1 and rs.max < 10:
            examples: list[list[str]] = []
            for start, length in records:
                if length == rs.max:
                    examples.append(tokens[start : start + length])
            max_run_examples[label] = examples

    pct_sum = sum(e.percentage for e in entries)

    return WordClassDistribution(
        total_words=total,
        unique_labels=len(entries),
        classifications=entries,
        percentage_sum=round(pct_sum, 4),
        max_run_examples=max_run_examples,
        tokens_by_label=dict(tokens_by_label),
    )
