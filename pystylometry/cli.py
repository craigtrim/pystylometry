"""Command-line interface for pystylometry.

Usage:
    pystylometry-drift <file> [--window-size=N] [--stride=N] [--mode=MODE] [--json]
    pystylometry-drift <file> --plot [output.png]
    pystylometry-tokenize <file> [--json] [--metadata] [--stats]

Example:
    pystylometry-drift manuscript.txt
    pystylometry-drift manuscript.txt --window-size=500 --stride=250
    pystylometry-drift manuscript.txt --json
    pystylometry-drift manuscript.txt --plot
    pystylometry-drift manuscript.txt --plot drift_report.png
    pystylometry-tokenize manuscript.txt
    pystylometry-tokenize manuscript.txt --json --metadata
    pystylometry-tokenize manuscript.txt --stats
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


if __name__ == "__main__":
    drift_cli()
