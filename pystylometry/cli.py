"""Command-line interface for pystylometry.

Usage:
    pystylometry-drift <file> [--window-size=N] [--stride=N] [--mode=MODE] [--json]
    pystylometry-drift <file> --plot [output.png]
    pystylometry-tokenize <file> [--json] [--metadata] [--stats]
    bnc --input-file <file> [--output-file <file>] [--format csv|html|json]

Example:
    pystylometry-drift manuscript.txt
    pystylometry-drift manuscript.txt --window-size=500 --stride=250
    pystylometry-drift manuscript.txt --json
    pystylometry-drift manuscript.txt --plot
    pystylometry-drift manuscript.txt --plot drift_report.png
    pystylometry-tokenize manuscript.txt
    pystylometry-tokenize manuscript.txt --json --metadata
    pystylometry-tokenize manuscript.txt --stats
    bnc --input-file manuscript.txt
    bnc --input-file manuscript.txt --output-file report.html --format html
    bnc -i manuscript.txt --format json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def drift_cli() -> None:
    """CLI entry point for Kilgarriff drift detection."""
    parser = argparse.ArgumentParser(
        prog="pystylometry-drift",
        description="Detect stylistic drift within a document using Kilgarriff chi-squared.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pystylometry-drift manuscript.txt
  pystylometry-drift manuscript.txt --window-size=500 --stride=250
  pystylometry-drift manuscript.txt --mode=all_pairs --json
  pystylometry-drift manuscript.txt --plot
  pystylometry-drift manuscript.txt --plot report.png
  pystylometry-drift manuscript.txt --plot timeline.png --plot-type=timeline
  pystylometry-drift manuscript.txt --jsx report.html --plot-type=report
  pystylometry-drift manuscript.txt --viz-all ./output  # All PNG + HTML

Pattern Signatures:
  consistent          Low, stable χ² across pairs (natural human writing)
  gradual_drift       Slowly increasing trend (author fatigue, topic shift)
  sudden_spike        One pair has high χ² (pasted content, different author)
  suspiciously_uniform Near-zero variance (possible AI generation)
""",
    )

    parser.add_argument(
        "file",
        type=Path,
        help="Path to text file to analyze",
    )
    parser.add_argument(
        "--window-size",
        type=int,
        default=1000,
        help="Number of tokens per window (default: 1000)",
    )
    parser.add_argument(
        "--stride",
        type=int,
        default=500,
        help="Tokens to advance between windows (default: 500)",
    )
    parser.add_argument(
        "--mode",
        choices=["sequential", "all_pairs", "fixed_lag"],
        default="sequential",
        help="Comparison mode (default: sequential)",
    )
    parser.add_argument(
        "--n-words",
        type=int,
        default=500,
        help="Most frequent words to analyze (default: 500)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--plot",
        nargs="?",
        const="",
        default=None,
        metavar="OUTPUT",
        help="Generate visualization (optional: path to save, otherwise displays interactively)",
    )
    parser.add_argument(
        "--plot-type",
        choices=["report", "timeline"],
        default="report",
        help="Visualization type: report (multi-panel) or timeline (line chart)",
    )
    parser.add_argument(
        "--jsx",
        metavar="OUTPUT_FILE",
        help="Export interactive visualization as standalone HTML (uses --plot-type)",
    )
    parser.add_argument(
        "--viz-all",
        metavar="OUTPUT_DIR",
        type=Path,
        help="Generate ALL visualizations (PNG + HTML) to directory for testing",
    )

    args = parser.parse_args()

    # Validate file exists
    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    # Read file
    try:
        text = args.file.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Determine output mode
    if args.viz_all:
        output_mode = "All Visualizations (PNG + HTML)"
        output_dest = str(args.viz_all)
    elif args.jsx:
        output_mode = f"Interactive HTML ({args.plot_type})"
        output_dest = args.jsx
    elif args.plot is not None:
        output_mode = f"Plot ({args.plot_type})"
        output_dest = args.plot if args.plot else "interactive display"
    elif args.json:
        output_mode = "JSON"
        output_dest = "stdout"
    else:
        output_mode = "Text Report"
        output_dest = "stdout"

    # Calculate file stats
    token_count = len(text.split())
    char_count = len(text)

    # Print professional intro banner
    print()
    print("  PYSTYLOMETRY — Kilgarriff Chi-Squared Drift Detection")
    print("  ═══════════════════════════════════════════════════════════════════════")
    print()
    print("  INPUT")
    print("  ───────────────────────────────────────────────────────────────────────")
    print(f"    File:              {args.file}")
    print(f"    Size:              {char_count:,} characters / {token_count:,} tokens")
    print()
    print("  PARAMETERS")
    print("  ───────────────────────────────────────────────────────────────────────")
    print(f"    Window size:       {args.window_size} tokens")
    print(f"    Stride:            {args.stride} tokens")
    print(
        f"    Overlap:           {((args.window_size - args.stride) / args.window_size) * 100:.0f}%"
    )
    print(f"    Comparison mode:   {args.mode}")
    print(f"    Top N words:       {args.n_words}")
    print()
    print("  OUTPUT")
    print("  ───────────────────────────────────────────────────────────────────────")
    print(f"    Format:            {output_mode}")
    print(f"    Destination:       {output_dest}")
    print()
    print("  Running analysis...")
    print()

    # Import here to avoid slow startup
    from pystylometry.consistency import compute_kilgarriff_drift

    # Run analysis
    result = compute_kilgarriff_drift(
        text,
        window_size=args.window_size,
        stride=args.stride,
        comparison_mode=args.mode,
        n_words=args.n_words,
    )

    # Handle --viz-all: generate all visualizations for testing
    if args.viz_all:
        output_dir = args.viz_all
        output_dir.mkdir(parents=True, exist_ok=True)
        label = args.file.stem

        from pystylometry.viz.jsx import export_drift_timeline_jsx

        generated = []

        # Write chunks to subdirectory
        chunks_dir = output_dir / "chunks"
        chunks_dir.mkdir(parents=True, exist_ok=True)

        # Re-create windows to get chunk text (simple word-based chunking)
        words = text.split()
        chunk_texts = []
        start = 0
        chunk_idx = 0
        while start + args.window_size <= len(words):
            chunk_words = words[start : start + args.window_size]
            chunk_text = " ".join(chunk_words)
            chunk_texts.append(chunk_text)

            # Write chunk file
            chunk_path = chunks_dir / f"chunk_{chunk_idx:03d}.txt"
            chunk_path.write_text(chunk_text, encoding="utf-8")
            chunk_idx += 1
            start += args.stride

        print(f"  Created: {chunks_dir}/ ({len(chunk_texts)} chunks)")

        # Generate timeline HTML with chunk content
        out_path = output_dir / "drift-detection.html"
        export_drift_timeline_jsx(
            result,
            output_file=out_path,
            title=f"Drift Timeline: {label}",
            chunks=chunk_texts,
        )
        generated.append(out_path)
        print(f"  Created: {out_path}")

        print()
        n_viz, n_chunks = len(generated), len(chunk_texts)
        print(f"Generated {n_viz} visualizations + {n_chunks} chunks to: {output_dir.resolve()}")
        sys.exit(0)

    # Handle JSX export (generates standalone HTML)
    if args.jsx:
        from pystylometry.viz.jsx import (
            export_drift_report_jsx,
            export_drift_timeline_jsx,
        )

        label = args.file.stem

        if args.plot_type == "timeline":
            output_path = export_drift_timeline_jsx(
                result,
                output_file=args.jsx,
                title=f"Drift Timeline: {label}",
            )
        else:  # report (default)
            output_path = export_drift_report_jsx(
                result,
                output_file=args.jsx,
                label=label,
            )

        abs_path = output_path.resolve()
        file_url = f"file://{abs_path}"
        print(f"Interactive visualization saved to: {output_path}")
        print(f"Open in browser: {file_url}")
        sys.exit(0)

    # Handle plot output
    if args.plot is not None:
        try:
            from pystylometry.viz import plot_drift_report, plot_drift_timeline
        except ImportError:
            print(
                "Error: Visualization requires optional dependencies.",
                file=sys.stderr,
            )
            print(
                "Install with: pip install pystylometry[viz] or poetry install --with viz",
                file=sys.stderr,
            )
            sys.exit(1)

        plot_output: str | None = args.plot if args.plot else None
        label = args.file.stem

        if args.plot_type == "timeline":
            plot_drift_timeline(result, output=plot_output, title=f"Drift Timeline: {label}")
        else:  # report (default)
            plot_drift_report(result, label=label, output=plot_output)

        if plot_output:
            print(f"Visualization saved to: {plot_output}")
        sys.exit(0)

    if args.json:
        # JSON output
        output = {
            "status": result.status,
            "status_message": result.status_message,
            "pattern": result.pattern,
            "pattern_confidence": result.pattern_confidence,
            "mean_chi_squared": result.mean_chi_squared,
            "std_chi_squared": result.std_chi_squared,
            "max_chi_squared": result.max_chi_squared,
            "min_chi_squared": result.min_chi_squared,
            "max_location": result.max_location,
            "trend": result.trend,
            "window_size": result.window_size,
            "stride": result.stride,
            "overlap_ratio": result.overlap_ratio,
            "window_count": result.window_count,
            "comparison_mode": result.comparison_mode,
        }
        print(json.dumps(output, indent=2))
    else:
        # Human-readable output
        print("=" * 60)
        print("STYLISTIC DRIFT ANALYSIS")
        print("=" * 60)
        print(f"File: {args.file}")
        print(f"Status: {result.status}")
        print()

        if result.status == "insufficient_data":
            print(f"⚠️  {result.status_message}")
            print()
            print(f"Windows created: {result.window_count}")
            print("Minimum required: 3")
            print()
            print("Try reducing --window-size or --stride to create more windows.")
            sys.exit(0)

        print("PATTERN DETECTED")
        print("-" * 40)
        print(f"  Pattern: {result.pattern}")
        print(f"  Confidence: {result.pattern_confidence:.1%}")
        print()

        if result.pattern == "consistent":
            print("  ✓ Text shows consistent writing style throughout.")
        elif result.pattern == "gradual_drift":
            print("  ↗ Text shows gradual stylistic drift over its length.")
            print("    Possible causes: author fatigue, topic evolution, revision.")
        elif result.pattern == "sudden_spike":
            print("  ⚡ Text contains a sudden stylistic discontinuity.")
            loc = result.max_location
            print(f"    Location: Between windows {loc} and {loc + 1}")
            print("    Possible causes: pasted content, different author, major edit.")
        elif result.pattern == "suspiciously_uniform":
            print("  ⚠️  Text shows unusually uniform style (near-zero variance).")
            print("    Possible causes: AI-generated content, heavy editing, templated text.")

        print()
        print("CHI-SQUARED STATISTICS")
        print("-" * 40)
        print(f"  Mean χ²:  {result.mean_chi_squared:.2f}")
        print(f"  Std χ²:   {result.std_chi_squared:.2f}")
        print(f"  Min χ²:   {result.min_chi_squared:.2f}")
        print(f"  Max χ²:   {result.max_chi_squared:.2f}")
        print(f"  Trend:    {result.trend:+.4f}")
        print()

        print("WINDOW CONFIGURATION")
        print("-" * 40)
        print(f"  Window size:    {result.window_size} tokens")
        print(f"  Stride:         {result.stride} tokens")
        print(f"  Overlap:        {result.overlap_ratio:.1%}")
        print(f"  Windows:        {result.window_count}")
        print(f"  Comparisons:    {len(result.pairwise_scores)}")
        print()

        if result.status == "marginal_data":
            print(f"⚠️  {result.status_message}")
            print()


def viewer_cli() -> None:
    """CLI entry point for generating a standalone drift viewer."""
    parser = argparse.ArgumentParser(
        prog="pystylometry-viewer",
        description="Generate a standalone HTML drift analysis viewer.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This generates a self-contained HTML file that users can open in any browser
to analyze their own text files. No Python or server required - just share
the HTML file and anyone can use it.

Examples:
  pystylometry-viewer drift_analyzer.html
  pystylometry-viewer ~/Desktop/analyzer.html --title "My Drift Analyzer"

The generated viewer includes:
  - Drag-and-drop file upload
  - Configurable analysis parameters
  - Interactive timeline visualization
  - Client-side Kilgarriff chi-squared implementation
""",
    )

    parser.add_argument(
        "output",
        type=Path,
        help="Path to write the HTML viewer file",
    )
    parser.add_argument(
        "--title",
        default="Stylistic Drift Analyzer",
        help="Page title (default: 'Stylistic Drift Analyzer')",
    )

    args = parser.parse_args()

    from pystylometry.viz.jsx import export_drift_viewer

    output_path = export_drift_viewer(args.output, title=args.title)

    abs_path = output_path.resolve()
    file_url = f"file://{abs_path}"

    print()
    print("  PYSTYLOMETRY — Standalone Drift Viewer")
    print("  ═══════════════════════════════════════════════════════════════════════")
    print()
    print(f"  Generated: {output_path}")
    print(f"  Open in browser: {file_url}")
    print()
    print("  This viewer can be shared with anyone. Users can:")
    print("    • Drag-and-drop or upload .txt files")
    print("    • Configure analysis parameters")
    print("    • View interactive drift timeline")
    print("    • Click points to see chunk comparisons")
    print()


def tokenize_cli() -> None:
    """CLI entry point for stylometric tokenization."""
    parser = argparse.ArgumentParser(
        prog="pystylometry-tokenize",
        description="Tokenize text for stylometric analysis.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pystylometry-tokenize manuscript.txt
  pystylometry-tokenize manuscript.txt --json
  pystylometry-tokenize manuscript.txt --json --metadata
  pystylometry-tokenize manuscript.txt --stats
  pystylometry-tokenize manuscript.txt -U --expand-contractions
  pystylometry-tokenize manuscript.txt --min-length 3 --strip-numbers
""",
    )

    parser.add_argument(
        "file",
        type=Path,
        help="Path to text file to tokenize",
    )

    # Output mode
    output_group = parser.add_argument_group("output")
    output_group.add_argument(
        "-j",
        "--json",
        action="store_true",
        help="Output as JSON (list of strings, or list of objects with --metadata)",
    )
    output_group.add_argument(
        "-m",
        "--metadata",
        action="store_true",
        help="Include token type and position metadata (implies --json)",
    )
    output_group.add_argument(
        "-s",
        "--stats",
        action="store_true",
        help="Show tokenization statistics instead of tokens",
    )

    # Core behavior
    behavior_group = parser.add_argument_group("behavior")
    behavior_group.add_argument(
        "-U",
        "--no-lowercase",
        action="store_true",
        help="Preserve original case (default: lowercase)",
    )
    behavior_group.add_argument(
        "-e",
        "--expand-contractions",
        action="store_true",
        help="Expand contractions (it's -> it is)",
    )
    behavior_group.add_argument(
        "-n",
        "--strip-numbers",
        action="store_true",
        help="Remove numeric tokens",
    )
    behavior_group.add_argument(
        "--keep-punctuation",
        action="store_true",
        help="Keep punctuation tokens (default: stripped)",
    )

    # Filtering
    filter_group = parser.add_argument_group("filtering")
    filter_group.add_argument(
        "--min-length",
        type=int,
        default=1,
        metavar="N",
        help="Minimum token length (default: 1)",
    )
    filter_group.add_argument(
        "--max-length",
        type=int,
        default=None,
        metavar="N",
        help="Maximum token length (default: unlimited)",
    )
    filter_group.add_argument(
        "--preserve-urls",
        action="store_true",
        help="Keep URL tokens",
    )
    filter_group.add_argument(
        "--preserve-emails",
        action="store_true",
        help="Keep email tokens",
    )
    filter_group.add_argument(
        "--preserve-hashtags",
        action="store_true",
        help="Keep hashtag tokens",
    )
    filter_group.add_argument(
        "--preserve-mentions",
        action="store_true",
        help="Keep @mention tokens",
    )

    # Advanced
    advanced_group = parser.add_argument_group("advanced")
    advanced_group.add_argument(
        "--expand-abbreviations",
        action="store_true",
        help="Expand abbreviations (Dr. -> Doctor)",
    )
    advanced_group.add_argument(
        "--strip-accents",
        action="store_true",
        help="Remove accents from characters",
    )
    advanced_group.add_argument(
        "--no-clean",
        action="store_true",
        help="Skip text cleaning (italics, brackets, page markers)",
    )
    advanced_group.add_argument(
        "--no-unicode-normalize",
        action="store_true",
        help="Skip unicode normalization",
    )

    args = parser.parse_args()

    # --- ANSI colors ---
    use_color = sys.stderr.isatty()

    def _c(code: str, text: str) -> str:
        return f"\033[{code}m{text}\033[0m" if use_color else text

    bold = lambda t: _c("1", t)  # noqa: E731
    dim = lambda t: _c("2", t)  # noqa: E731
    cyan = lambda t: _c("36", t)  # noqa: E731
    green = lambda t: _c("32", t)  # noqa: E731
    yellow = lambda t: _c("33", t)  # noqa: E731

    # --- Validate file ---
    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    try:
        text = args.file.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Build Tokenizer kwargs ---
    tokenizer_kwargs = {
        "lowercase": not args.no_lowercase,
        "min_length": args.min_length,
        "max_length": args.max_length,
        "strip_numbers": args.strip_numbers,
        "strip_punctuation": not args.keep_punctuation,
        "preserve_urls": args.preserve_urls,
        "preserve_emails": args.preserve_emails,
        "preserve_hashtags": args.preserve_hashtags,
        "preserve_mentions": args.preserve_mentions,
        "expand_contractions": args.expand_contractions,
        "expand_abbreviations": args.expand_abbreviations,
        "strip_accents": args.strip_accents,
        "normalize_unicode": not args.no_unicode_normalize,
        "clean_text": not args.no_clean,
    }

    # Collect active options for banner
    active_opts = []
    if args.no_lowercase:
        active_opts.append("preserve case")
    if args.expand_contractions:
        active_opts.append("expand contractions")
    if args.expand_abbreviations:
        active_opts.append("expand abbreviations")
    if args.strip_numbers:
        active_opts.append("strip numbers")
    if args.keep_punctuation:
        active_opts.append("keep punctuation")
    if args.strip_accents:
        active_opts.append("strip accents")
    if args.no_clean:
        active_opts.append("skip cleaning")
    if args.no_unicode_normalize:
        active_opts.append("skip unicode normalization")
    if args.preserve_urls:
        active_opts.append("preserve URLs")
    if args.preserve_emails:
        active_opts.append("preserve emails")
    if args.preserve_hashtags:
        active_opts.append("preserve hashtags")
    if args.preserve_mentions:
        active_opts.append("preserve mentions")
    if args.min_length > 1:
        active_opts.append(f"min length {args.min_length}")
    if args.max_length is not None:
        active_opts.append(f"max length {args.max_length}")

    # Determine output format
    if args.stats:
        output_format = "Statistics"
    elif args.metadata:
        output_format = "JSON (with metadata)"
    elif args.json:
        output_format = "JSON"
    else:
        output_format = "One token per line"

    # --- Banner (to stderr so stdout stays pipeable) ---
    char_count = len(text)
    line_count = text.count("\n") + 1

    banner = sys.stderr
    print(file=banner)
    print(f"  {bold('PYSTYLOMETRY')} {dim('—')} {cyan('Stylometric Tokenizer')}", file=banner)
    print(f"  {dim('═' * 71)}", file=banner)
    print(file=banner)
    print(f"  {bold('INPUT')}", file=banner)
    print(f"  {dim('─' * 71)}", file=banner)
    print(f"    File:              {args.file}", file=banner)
    print(f"    Size:              {char_count:,} characters / {line_count:,} lines", file=banner)
    print(file=banner)
    print(f"  {bold('CONFIGURATION')}", file=banner)
    print(f"  {dim('─' * 71)}", file=banner)
    print(f"    Case:              {'preserve' if args.no_lowercase else 'lowercase'}", file=banner)
    print(
        f"    Punctuation:       {'keep' if args.keep_punctuation else 'strip'}",
        file=banner,
    )
    print(
        f"    Contractions:      {'expand' if args.expand_contractions else 'preserve'}",
        file=banner,
    )
    print(f"    Numbers:           {'strip' if args.strip_numbers else 'keep'}", file=banner)
    if active_opts:
        print(f"    Active options:    {', '.join(active_opts)}", file=banner)
    print(file=banner)
    print(f"  {bold('OUTPUT')}", file=banner)
    print(f"  {dim('─' * 71)}", file=banner)
    print(f"    Format:            {output_format}", file=banner)
    print(file=banner)

    # --- Tokenize ---
    from pystylometry.tokenizer import Tokenizer

    tokenizer = Tokenizer(**tokenizer_kwargs)

    if args.stats:
        stats = tokenizer.get_statistics(text)
        print(f"  {bold('RESULTS')}", file=banner)
        print(f"  {dim('─' * 71)}", file=banner)
        print(f"    Total tokens:      {green(f'{stats.total_tokens:,}')}", file=banner)
        print(f"    Unique tokens:     {green(f'{stats.unique_tokens:,}')}", file=banner)
        print(f"    Word tokens:       {stats.word_tokens:,}", file=banner)
        print(f"    Number tokens:     {stats.number_tokens:,}", file=banner)
        print(f"    Punctuation:       {stats.punctuation_tokens:,}", file=banner)
        print(f"    URLs:              {stats.url_tokens:,}", file=banner)
        print(f"    Emails:            {stats.email_tokens:,}", file=banner)
        print(f"    Hashtags:          {stats.hashtag_tokens:,}", file=banner)
        print(f"    Mentions:          {stats.mention_tokens:,}", file=banner)
        print(f"    Avg length:        {stats.average_token_length:.1f}", file=banner)
        print(f"    Min length:        {stats.min_token_length}", file=banner)
        print(f"    Max length:        {stats.max_token_length}", file=banner)
        print(file=banner)

        if args.json:
            import dataclasses

            print(json.dumps(dataclasses.asdict(stats), indent=2))

    elif args.metadata or (args.json and args.metadata):
        metadata_list = tokenizer.tokenize_with_metadata(text)
        count = len(metadata_list)
        print(
            f"  {yellow('Tokenizing...')} {green(f'{count:,}')} tokens extracted",
            file=banner,
        )
        print(file=banner)
        output = [
            {
                "token": m.token,
                "start": m.start,
                "end": m.end,
                "type": m.token_type,
            }
            for m in metadata_list
        ]
        print(json.dumps(output, indent=2))

    elif args.json:
        tokens = tokenizer.tokenize(text)
        count = len(tokens)
        print(
            f"  {yellow('Tokenizing...')} {green(f'{count:,}')} tokens extracted",
            file=banner,
        )
        print(file=banner)
        print(json.dumps(tokens, indent=2))

    else:
        tokens = tokenizer.tokenize(text)
        count = len(tokens)
        print(
            f"  {yellow('Tokenizing...')} {green(f'{count:,}')} tokens extracted",
            file=banner,
        )
        print(file=banner)
        for token in tokens:
            print(token)


def bnc_frequency_cli() -> None:
    """CLI entry point for BNC word frequency analysis."""
    parser = argparse.ArgumentParser(
        prog="bnc",
        description="Analyze word frequencies against the British National Corpus (BNC).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  bnc --input-file manuscript.txt
  bnc --input-file manuscript.txt --output-file report.html
  bnc --input-file manuscript.txt --format json
  bnc --input-file manuscript.txt --overuse-threshold 2.0 --min-mentions 3
  bnc --input-file manuscript.txt --no-wordnet
  bnc --input-dir ~/ebooks/Author --format excel --output-file author.xlsx

Output:
  Generates a report with three sections:
  - Not in BNC: Words not found in the corpus (with WordNet status, character type)
  - Most Underused: Words appearing less frequently than expected
  - Most Overused: Words appearing more frequently than expected

Thresholds:
  Words with ratio > overuse-threshold are "overused"
  Words with ratio < underuse-threshold are "underused"
  Ratio = observed_count / expected_count (based on BNC frequencies)
""",
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--input-file",
        "-i",
        type=Path,
        metavar="FILE",
        help="Path to text file to analyze",
    )
    input_group.add_argument(
        "--input-dir",
        "-d",
        type=Path,
        metavar="DIR",
        help="Directory of .txt files to analyze as a single corpus (requires --output-file)",
    )
    parser.add_argument(
        "--output-file",
        "-o",
        type=Path,
        default=None,
        metavar="FILE",
        help="Output file (default: <input>_bnc_frequency.<ext> based on --format)",
    )
    parser.add_argument(
        "--overuse-threshold",
        type=float,
        default=1.3,
        metavar="N",
        help="Ratio above which words are considered overused (default: 1.3)",
    )
    parser.add_argument(
        "--underuse-threshold",
        type=float,
        default=0.8,
        metavar="N",
        help="Ratio below which words are considered underused (default: 0.8)",
    )
    parser.add_argument(
        "--min-mentions",
        type=int,
        default=1,
        metavar="N",
        help="Minimum word occurrences to include (default: 1)",
    )
    parser.add_argument(
        "--no-wordnet",
        action="store_true",
        help="Skip WordNet lookup for unknown words",
    )
    parser.add_argument(
        "--format",
        choices=["csv", "html", "json", "excel"],
        default="csv",
        help="Output format: csv (tab-delimited), html (interactive), json, excel (default: csv)",
    )
    parser.add_argument(
        "--combinatoric",
        action="store_true",
        help="Pairwise comparison of all files in --input-dir (requires --input-dir)",
    )

    args = parser.parse_args()

    # Import rich for colored output
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    console = Console(stderr=True)

    # ── Validation ──
    if args.combinatoric and not args.input_dir:
        console.print("[red]Error:[/red] --combinatoric requires --input-dir")
        sys.exit(1)

    # ── Input loading ──
    file_count: int = 1
    txt_files: list[Path] = []

    if args.input_dir:
        if not args.input_dir.is_dir():
            console.print(f"[red]Error:[/red] Directory not found: {args.input_dir}")
            sys.exit(1)
        if not args.output_file:
            console.print("[red]Error:[/red] --output-file is required when using --input-dir")
            sys.exit(1)

        txt_files = sorted(args.input_dir.glob("*.txt"))
        if not txt_files:
            console.print(f"[red]Error:[/red] No .txt files found in: {args.input_dir}")
            sys.exit(1)

        # Read all files (used for both standard and combinatoric modes)
        parts: list[str] = []
        for tf in txt_files:
            try:
                parts.append(tf.read_text(encoding="utf-8"))
            except Exception as e:
                console.print(f"[red]Error reading {tf.name}:[/red] {e}")
                sys.exit(1)
        text = "\n".join(parts)
        file_count = len(txt_files)
    else:
        # --input-file mode (existing behavior)
        if not args.input_file.exists():
            console.print(f"[red]Error:[/red] File not found: {args.input_file}")
            sys.exit(1)
        try:
            text = args.input_file.read_text(encoding="utf-8")
        except Exception as e:
            console.print(f"[red]Error reading file:[/red] {e}")
            sys.exit(1)

    # Determine output path (extension based on format)
    suffix_map = {"csv": ".tsv", "html": ".html", "json": ".json", "excel": ".xlsx"}
    if args.output_file:
        output_path = args.output_file
    else:
        suffix = suffix_map[args.format]
        output_path = args.input_file.with_name(f"{args.input_file.stem}_bnc_frequency{suffix}")

    # Calculate file stats
    token_count = len(text.split())
    char_count = len(text)

    # Print header
    console.print()
    header = Text()
    header.append("PYSTYLOMETRY", style="bold cyan")
    header.append(" — ", style="dim")
    header.append("BNC Word Frequency Analysis", style="bold white")
    console.print(Panel(header, border_style="cyan"))

    # Input section
    console.print()
    console.print("[bold]INPUT[/bold]", style="cyan")
    console.print("─" * 60, style="dim")
    if args.input_dir:
        console.print(f"  Dir:     [white]{args.input_dir}[/white]")
        console.print(f"  Files:   [green]{file_count}[/green] .txt files")
    else:
        console.print(f"  File:    [white]{args.input_file}[/white]")
    _sz = f"[green]{char_count:,}[/green] chars / [green]{token_count:,}[/green] tokens"
    console.print(f"  Size:    {_sz}")

    # Probe optional dependency availability for banner
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import version as _pkg_ver

    try:
        _bnc_ver: str = _pkg_ver("bnc-lookup")
    except PackageNotFoundError:
        _bnc_ver = "[red]not installed[/red]"

    try:
        _gn_ver: str = _pkg_ver("gngram-lookup")
    except PackageNotFoundError:
        _gn_ver = "[dim]not installed[/dim]"

    try:
        _wn_ver: str = _pkg_ver("wordnet-lookup")
    except PackageNotFoundError:
        _wn_ver = "[dim]not installed[/dim]"

    # Parameters section
    console.print()
    console.print("[bold]PARAMETERS[/bold]", style="cyan")
    console.print("─" * 60, style="dim")
    console.print(f"  Overuse threshold:   [yellow]{args.overuse_threshold}x[/yellow]")
    console.print(f"  Underuse threshold:  [yellow]{args.underuse_threshold}x[/yellow]")
    console.print(f"  Min mentions:        [yellow]{args.min_mentions}[/yellow]")
    console.print(f"  BNC lookup:          [yellow]{_bnc_ver}[/yellow]")
    _wn_display = "disabled" if args.no_wordnet else _wn_ver
    console.print(f"  WordNet lookup:      [yellow]{_wn_display}[/yellow]")
    console.print(f"  Ngram lookup:        [yellow]{_gn_ver}[/yellow]")
    if args.combinatoric:
        console.print(f"  Combinatoric:        [yellow]yes ({file_count} files)[/yellow]")

    # Output section
    console.print()
    console.print("[bold]OUTPUT[/bold]", style="cyan")
    console.print("─" * 60, style="dim")
    fmt_display = {
        "csv": "Tab-delimited CSV",
        "html": "Interactive HTML",
        "json": "JSON",
        "excel": "Excel (.xlsx)",
    }
    console.print(f"  Format:      [magenta]{fmt_display[args.format]}[/magenta]")
    console.print(f"  Destination: [white]{output_path}[/white]")

    # Run analysis with spinner
    console.print()
    with console.status("[bold cyan]Running analysis...[/bold cyan]", spinner="dots"):
        from pystylometry.lexical.bnc_frequency import compute_bnc_frequency

        result = compute_bnc_frequency(
            text,
            overuse_threshold=args.overuse_threshold,
            underuse_threshold=args.underuse_threshold,
            include_wordnet=not args.no_wordnet,
            min_mentions=args.min_mentions,
        )

    # ── Combinatoric: per-file works counts ──
    works_overused: dict[str, int] = {}
    works_underused: dict[str, int] = {}
    works_notbnc: dict[str, int] = {}
    works_total: int = 0

    if args.combinatoric:
        works_total = len(txt_files)
        console.print()
        for tf in txt_files:
            console.print(
                f"  [dim]Scanning[/dim] [white]{tf.name}[/white]...",
                end="",
            )
            file_text = tf.read_text(encoding="utf-8")
            fr = compute_bnc_frequency(
                file_text,
                overuse_threshold=args.overuse_threshold,
                underuse_threshold=args.underuse_threshold,
                include_wordnet=not args.no_wordnet,
                min_mentions=args.min_mentions,
            )
            for w in fr.overused:
                works_overused[w.word] = works_overused.get(w.word, 0) + 1
            for w in fr.underused:
                works_underused[w.word] = works_underused.get(w.word, 0) + 1
            for w in fr.not_in_bnc:
                works_notbnc[w.word] = works_notbnc.get(w.word, 0) + 1
            console.print(" [green]✓[/green]")

    # Output results
    if args.format == "json":
        # classify_word provides the three-layer morphological taxonomy label
        # that replaces the five boolean flag columns.
        # See: https://github.com/craigtrim/pystylometry/issues/53
        from pystylometry.lexical.word_class import classify_word as _classify_json

        def _json_word(w_obj: object, cat_counts: dict[str, int]) -> dict[str, object]:
            """Build a JSON-serializable dict for a WordAnalysis."""
            from pystylometry.lexical.bnc_frequency import WordAnalysis

            assert isinstance(w_obj, WordAnalysis)
            d: dict[str, object] = {
                "word": w_obj.word,
                "observed": w_obj.observed,
                "expected": w_obj.expected,
            }
            if cat_counts:
                d["works"] = f"{cat_counts.get(w_obj.word, 0)}/{works_total}"
            d["ratio"] = w_obj.ratio
            d["in_wordnet"] = w_obj.in_wordnet
            d["in_gngram"] = w_obj.in_gngram
            d["classification"] = _classify_json(w_obj.word).label
            return d

        stats: dict[str, object] = {
            "total_tokens": result.total_tokens,
            "unique_tokens": result.unique_tokens,
            "overused_count": len(result.overused),
            "underused_count": len(result.underused),
            "not_in_bnc_count": len(result.not_in_bnc),
        }
        if works_total:
            stats["works_total"] = works_total

        def _sort_key(w_obj: object, cat_counts: dict[str, int]) -> tuple[int, float]:
            from pystylometry.lexical.bnc_frequency import WordAnalysis

            assert isinstance(w_obj, WordAnalysis)
            return (cat_counts.get(w_obj.word, 0), w_obj.ratio or 0)

        _over_sorted = sorted(
            result.overused, key=lambda x: _sort_key(x, works_overused), reverse=True
        ) if works_total else result.overused
        _under_sorted = sorted(
            result.underused, key=lambda x: _sort_key(x, works_underused), reverse=True
        ) if works_total else result.underused
        _notbnc_sorted = sorted(
            result.not_in_bnc, key=lambda x: _sort_key(x, works_notbnc), reverse=True
        ) if works_total else result.not_in_bnc

        output = {
            "stats": stats,
            "overused": [_json_word(w, works_overused) for w in _over_sorted],
            "underused": [_json_word(w, works_underused) for w in _under_sorted],
            "not_in_bnc": [
                _json_word(w, works_notbnc) for w in _notbnc_sorted
            ],
        }
        output_path.write_text(json.dumps(output, indent=2))
        console.print(f'[green]✓[/green] JSON saved to: [white]"{output_path}"[/white]')

    elif args.format == "csv":
        # classify_word provides the three-layer morphological taxonomy label
        # that replaces the five boolean flag columns.
        # See: https://github.com/craigtrim/pystylometry/issues/53
        from pystylometry.lexical.word_class import classify_word as _classify_csv

        # Tab-delimited output with category column
        if works_total:
            _hdr = (
                "category\tword\tobserved\texpected\tworks\tratio\tin_wordnet\tin_gngram"
                "\tclassification"
            )
        else:
            _hdr = (
                "category\tword\tobserved\texpected\tratio\tin_wordnet\tin_gngram"
                "\tclassification"
            )
        lines = [_hdr]

        def fmt_wordnet(val: bool | None) -> str:
            if val is True:
                return "yes"
            elif val is False:
                return "no"
            return ""

        def fmt_gngram(val: bool | None) -> str:
            if val is True:
                return "yes"
            elif val is False:
                return "no"
            return ""

        _csv_over = sorted(
            result.overused,
            key=lambda x: (works_overused.get(x.word, 0), x.ratio or 0),
            reverse=True,
        ) if works_total else result.overused
        for w in _csv_over:
            expected = f"{w.expected:.2f}" if w.expected else ""
            ratio = f"{w.ratio:.4f}" if w.ratio else ""
            in_wn = fmt_wordnet(w.in_wordnet)
            in_gn = fmt_gngram(w.in_gngram)
            cls = _classify_csv(w.word).label
            if works_total:
                wk = f"{works_overused.get(w.word, 0)}/{works_total}"
                line = (
                    f"overused\t{w.word}\t{w.observed}\t{expected}\t{wk}\t{ratio}"
                    f"\t{in_wn}\t{in_gn}\t{cls}"
                )
            else:
                line = (
                    f"overused\t{w.word}\t{w.observed}\t{expected}\t{ratio}"
                    f"\t{in_wn}\t{in_gn}\t{cls}"
                )
            lines.append(line)

        _csv_under = sorted(
            result.underused,
            key=lambda x: (works_underused.get(x.word, 0), x.ratio or 0),
            reverse=True,
        ) if works_total else result.underused
        for w in _csv_under:
            expected = f"{w.expected:.2f}" if w.expected else ""
            ratio = f"{w.ratio:.4f}" if w.ratio else ""
            in_wn = fmt_wordnet(w.in_wordnet)
            in_gn = fmt_gngram(w.in_gngram)
            cls = _classify_csv(w.word).label
            if works_total:
                wk = f"{works_underused.get(w.word, 0)}/{works_total}"
                line = (
                    f"underused\t{w.word}\t{w.observed}\t{expected}\t{wk}\t{ratio}"
                    f"\t{in_wn}\t{in_gn}\t{cls}"
                )
            else:
                line = (
                    f"underused\t{w.word}\t{w.observed}\t{expected}\t{ratio}"
                    f"\t{in_wn}\t{in_gn}\t{cls}"
                )
            lines.append(line)

        _csv_notbnc = sorted(
            result.not_in_bnc,
            key=lambda x: (works_notbnc.get(x.word, 0), x.observed or 0),
            reverse=True,
        ) if works_total else result.not_in_bnc
        for w in _csv_notbnc:
            in_wn = fmt_wordnet(w.in_wordnet)
            in_gn = fmt_gngram(w.in_gngram)
            cls = _classify_csv(w.word).label
            if works_total:
                wk = f"{works_notbnc.get(w.word, 0)}/{works_total}"
                line = (
                    f"not-in-bnc\t{w.word}\t{w.observed}\t\t{wk}\t"
                    f"\t{in_wn}\t{in_gn}\t{cls}"
                )
            else:
                line = (
                    f"not-in-bnc\t{w.word}\t{w.observed}\t\t\t{in_wn}\t{in_gn}"
                    f"\t{cls}"
                )
            lines.append(line)

        output_path.write_text("\n".join(lines))
        console.print(f'[green]✓[/green] TSV saved to: [white]"{output_path}"[/white]')

    elif args.format == "excel":
        try:
            from openpyxl import Workbook  # type: ignore[import-untyped]
            from openpyxl.styles import (  # type: ignore[import-untyped]
                Alignment,
                Font,
                PatternFill,
            )
        except ImportError:
            console.print("[red]Error:[/red] Excel export requires openpyxl.")
            console.print("  Install with: [yellow]pip install pystylometry[excel][/yellow]")
            console.print("  Or for pipx: [yellow]pipx inject pystylometry openpyxl[/yellow]")
            sys.exit(1)

        wb = Workbook()

        # Remove default sheet
        wb.remove(wb.active)

        # Cell styles
        align = Alignment(horizontal="center", vertical="center")
        font_header = Font(bold=True, size=14)
        fill_header = PatternFill(
            start_color="D9E2F3", end_color="D9E2F3", fill_type="solid"
        )  # Soft blue-gray

        # ── Summary sheet (first tab) ──
        ws_summary = wb.create_sheet("summary")

        # Headers: 3 columns side by side
        headers = ["Top 10 Overused", "Top 10 Underused", "Top 10 Not in BNC"]
        for ci, hdr in enumerate(headers, start=1):
            c = ws_summary.cell(row=1, column=ci, value=hdr)
            c.font = font_header
            c.fill = fill_header

        # Top 10 words from each category (words only, no numbers)
        top_overused = [w.word for w in result.overused[:10]]
        top_underused = [w.word for w in result.underused[:10]]
        top_not_in_bnc = [w.word for w in result.not_in_bnc[:10]]

        for i in range(10):
            row = i + 2
            if i < len(top_overused):
                ws_summary.cell(row=row, column=1, value=top_overused[i])
            if i < len(top_underused):
                ws_summary.cell(row=row, column=2, value=top_underused[i])
            if i < len(top_not_in_bnc):
                ws_summary.cell(row=row, column=3, value=top_not_in_bnc[i])

        # ── Descriptive stats below the top-10 table ──
        stats_start = 14  # row 12 = last word row, 13 = blank, 14 = header
        stat_headers = ["Metric", "Count", "% of Total Tokens"]
        for ci, hdr in enumerate(stat_headers, start=1):
            c = ws_summary.cell(row=stats_start, column=ci, value=hdr)
            c.font = font_header
            c.fill = fill_header

        total = result.total_tokens or 1  # avoid division by zero
        stats_rows = [
            ("Total Tokens", f"{result.total_tokens:,}", ""),
            (
                "Unique Tokens",
                f"{result.unique_tokens:,}",
                f"{result.unique_tokens / total * 100:.2f}%",
            ),
            ("Overused", f"{len(result.overused):,}", f"{len(result.overused) / total * 100:.2f}%"),
            (
                "Underused",
                f"{len(result.underused):,}",
                f"{len(result.underused) / total * 100:.2f}%",
            ),
            (
                "Not in BNC",
                f"{len(result.not_in_bnc):,}",
                f"{len(result.not_in_bnc) / total * 100:.2f}%",
            ),
        ]
        for ri, (label, count, pct) in enumerate(stats_rows, start=stats_start + 1):
            ws_summary.cell(row=ri, column=1, value=label)
            ws_summary.cell(row=ri, column=2, value=count)
            ws_summary.cell(row=ri, column=3, value=pct)

        # Format summary sheet
        for col_letter in ("A", "B", "C"):
            ws_summary.column_dimensions[col_letter].width = 25
        for r in ws_summary.iter_rows():
            for cell in r:
                cell.alignment = align

        def fmt_wordnet_excel(val: bool | None) -> str:
            if val is True:
                return "true"
            elif val is False:
                return "false"
            return ""

        def fmt_gngram_excel(val: bool | None) -> str:
            if val is True:
                return "true"
            elif val is False:
                return "false"
            return ""

        # classify_word provides the three-layer morphological taxonomy label
        # that replaces the five boolean flag columns.
        # See: https://github.com/craigtrim/pystylometry/issues/53
        from pystylometry.lexical.word_class import classify_word as _classify_xl

        # Overused sheet (sorted by works desc, ratio desc when combinatoric)
        ws_over = wb.create_sheet("overused")
        if works_total:
            _over_hdr = [
                "word", "observed", "expected", "works", "ratio", "in_wordnet",
                "in_gngram", "classification",
            ]
        else:
            _over_hdr = [
                "word", "observed", "expected", "ratio", "in_wordnet", "in_gngram",
                "classification",
            ]
        ws_over.append(_over_hdr)
        _xl_over = sorted(
            result.overused,
            key=lambda x: (works_overused.get(x.word, 0), x.ratio or 0),
            reverse=True,
        ) if works_total else sorted(result.overused, key=lambda x: x.ratio or 0, reverse=True)
        for w in _xl_over:
            in_wn = fmt_wordnet_excel(w.in_wordnet)
            in_gn = fmt_gngram_excel(w.in_gngram)
            cls = _classify_xl(w.word).label
            if works_total:
                row_data = [
                    w.word, w.observed, w.expected,
                    f"{works_overused.get(w.word, 0)}/{works_total}",
                    w.ratio, in_wn, in_gn, cls,
                ]
            else:
                row_data = [
                    w.word, w.observed, w.expected, w.ratio, in_wn, in_gn, cls,
                ]
            ws_over.append(row_data)

        # Underused sheet (sorted by works desc, ratio desc when combinatoric)
        ws_under = wb.create_sheet("underused")
        if works_total:
            _under_hdr = [
                "word", "observed", "expected", "works", "ratio", "in_wordnet",
                "in_gngram", "classification",
            ]
        else:
            _under_hdr = [
                "word", "observed", "expected", "ratio", "in_wordnet", "in_gngram",
                "classification",
            ]
        ws_under.append(_under_hdr)
        _xl_under = sorted(
            result.underused,
            key=lambda x: (works_underused.get(x.word, 0), x.ratio or 0),
            reverse=True,
        ) if works_total else sorted(result.underused, key=lambda x: x.ratio or 0, reverse=True)
        for w in _xl_under:
            in_wn = fmt_wordnet_excel(w.in_wordnet)
            in_gn = fmt_gngram_excel(w.in_gngram)
            cls = _classify_xl(w.word).label
            if works_total:
                row_data = [
                    w.word, w.observed, w.expected,
                    f"{works_underused.get(w.word, 0)}/{works_total}",
                    w.ratio, in_wn, in_gn, cls,
                ]
            else:
                row_data = [
                    w.word, w.observed, w.expected, w.ratio, in_wn, in_gn, cls,
                ]
            ws_under.append(row_data)

        # Not in BNC sheet
        ws_notbnc = wb.create_sheet("not-in-bnc")
        if works_total:
            _notbnc_hdr = [
                "word", "observed", "works", "in_wordnet", "in_gngram",
                "classification",
            ]
        else:
            _notbnc_hdr = [
                "word", "observed", "in_wordnet", "in_gngram",
                "classification",
            ]
        ws_notbnc.append(_notbnc_hdr)

        _xl_notbnc = sorted(
            result.not_in_bnc,
            key=lambda x: (works_notbnc.get(x.word, 0), x.observed or 0),
            reverse=True,
        ) if works_total else result.not_in_bnc
        for w in _xl_notbnc:
            in_wn = fmt_wordnet_excel(w.in_wordnet)
            in_gn = fmt_gngram_excel(w.in_gngram)
            cls = _classify_xl(w.word).label
            if works_total:
                row_data = [
                    w.word, w.observed,
                    f"{works_notbnc.get(w.word, 0)}/{works_total}",
                    in_wn, in_gn, cls,
                ]
            else:
                row_data = [
                    w.word, w.observed, in_wn, in_gn, cls,
                ]
            ws_notbnc.append(row_data)

        # Apply header styling to data sheets (match summary headers)
        for ws in [ws_over, ws_under, ws_notbnc]:
            for cell in ws[1]:
                cell.font = font_header
                cell.fill = fill_header

        # Apply formatting to all sheets
        for ws in [ws_over, ws_under, ws_notbnc]:
            for col in ws.columns:
                col_letter = col[0].column_letter
                # Word column (A) and classification (last col) get 30, others 15
                ws.column_dimensions[col_letter].width = 30 if col_letter == "A" else 15
            for row in ws.iter_rows():
                for cell in row:
                    cell.alignment = align

        # Classification column is wider to accommodate dot-separated labels
        # like "apostrophe.contraction.negative"
        # Overused/underused: col H (with works) or G (without)
        _cls_col_freq = "H" if works_total else "G"
        for ws in [ws_over, ws_under]:
            ws.column_dimensions[_cls_col_freq].width = 35
        # Not-in-BNC: col F (with works) or E (without)
        _cls_col_notbnc = "F" if works_total else "E"
        ws_notbnc.column_dimensions[_cls_col_notbnc].width = 35

        # Apply number formatting to expected and ratio columns
        # With works: C=expected, E=ratio; without works: C=expected, D=ratio
        _ratio_col = "E" if works_total else "D"
        for ws in [ws_over, ws_under]:
            for row in range(2, ws.max_row + 1):  # Skip header row
                ws[f"C{row}"].number_format = "0.00"
                ws[f"{_ratio_col}{row}"].number_format = "0.00"

        # Boolean flag colors (true/false) for in_wordnet and in_gngram columns.
        # The old five boolean columns (unicode, numeric, apostrophe, hyphen,
        # other) have been replaced by the classification string column (#53).
        fill_flag_true = PatternFill(
            start_color="BDD7EE", end_color="BDD7EE", fill_type="solid"
        )  # Light blue
        fill_flag_false = PatternFill(
            start_color="FCE4D6", end_color="FCE4D6", fill_type="solid"
        )  # Light peach

        # Boolean columns: in_wordnet and in_gngram only
        # Overused/underused: with works F,G; without E,F
        _over_flags = ("F", "G") if works_total else ("E", "F")
        for ws in [ws_over, ws_under]:
            for row in range(2, ws.max_row + 1):
                for col_letter in _over_flags:
                    cell = ws[f"{col_letter}{row}"]
                    if cell.value == "true":
                        cell.fill = fill_flag_true
                    elif cell.value == "false":
                        cell.fill = fill_flag_false

        # Not-in-bnc: with works D,E; without C,D
        _notbnc_flags = ("D", "E") if works_total else ("C", "D")
        for row in range(2, ws_notbnc.max_row + 1):
            for col_letter in _notbnc_flags:
                cell = ws_notbnc[f"{col_letter}{row}"]
                if cell.value == "true":
                    cell.fill = fill_flag_true
                elif cell.value == "false":
                    cell.fill = fill_flag_false

        # Row heights: 25 for headers, 20 for data rows — all sheets
        for ws in [ws_summary, ws_over, ws_under, ws_notbnc]:
            for row_num in range(1, ws.max_row + 1):
                ws.row_dimensions[row_num].height = 20
            # Header rows get 25
            ws.row_dimensions[1].height = 25
        # Summary has a second header row for stats
        ws_summary.row_dimensions[stats_start].height = 25

        wb.save(output_path)
        console.print(f'[green]✓[/green] Excel saved to: [white]"{output_path}"[/white]')

    else:  # html
        from pystylometry.viz.jsx import export_bnc_frequency_jsx

        if args.input_dir:
            html_title = f"BNC Frequency Analysis: {args.input_dir.name} ({file_count} files)"
            html_source = str(args.input_dir)
        else:
            html_title = f"BNC Frequency Analysis: {args.input_file.name}"
            html_source = str(args.input_file)

        export_bnc_frequency_jsx(
            result,
            output_file=output_path,
            title=html_title,
            source_file=html_source,
        )

        abs_path = output_path.resolve()
        file_url = f"file://{abs_path}"
        console.print(f'[green]✓[/green] HTML report saved to: [white]"{output_path}"[/white]')
        console.print(f"  Open in browser: [link={file_url}]{file_url}[/link]")

    # Summary table
    console.print()
    table = Table(title="Summary", border_style="cyan", header_style="bold cyan")
    table.add_column("Metric", style="white")
    table.add_column("Count", justify="right", style="green")

    table.add_row("Total tokens", f"{result.total_tokens:,}")
    table.add_row("Unique words", f"{result.unique_tokens:,}")
    table.add_row("Not in BNC", f"[dim]{len(result.not_in_bnc):,}[/dim]")
    table.add_row("Underused", f"[blue]{len(result.underused):,}[/blue]")
    table.add_row("Overused", f"[red]{len(result.overused):,}[/red]")

    console.print(table)
    console.print()


if __name__ == "__main__":
    drift_cli()
