"""Command-line interface for pystylometry.

Usage:
    pystylometry-drift <file> [--window-size=N] [--stride=N] [--mode=MODE] [--json]
    pystylometry-drift <file> --plot [output.png]

Example:
    pystylometry-drift manuscript.txt
    pystylometry-drift manuscript.txt --window-size=500 --stride=250
    pystylometry-drift manuscript.txt --json
    pystylometry-drift manuscript.txt --plot
    pystylometry-drift manuscript.txt --plot drift_report.png
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
        help="Export interactive visualization as standalone HTML (uses --plot-type: timeline or report)",
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
    print(f"    Overlap:           {((args.window_size - args.stride) / args.window_size) * 100:.0f}%")
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

        # Re-create windows to get chunk text
        from pystylometry._utils import tokenize

        tokens = [t for t in tokenize(text) if t.isalpha() or not t.strip()]
        # Simple tokenization for chunk extraction (preserve spaces for readability)
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
        print(f"Generated {len(generated)} visualizations + {len(chunk_texts)} chunks to: {output_dir.resolve()}")
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

        output_path = args.plot if args.plot else None
        label = args.file.stem

        if args.plot_type == "timeline":
            plot_drift_timeline(result, output=output_path, title=f"Drift Timeline: {label}")
        else:  # report (default)
            plot_drift_report(result, label=label, output=output_path)

        if output_path:
            print(f"Visualization saved to: {output_path}")
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


if __name__ == "__main__":
    drift_cli()
