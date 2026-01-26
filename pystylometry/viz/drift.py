"""Drift detection visualizations (matplotlib).

This module provides matplotlib-based visualizations for Kilgarriff chi-squared
drift detection results. For interactive HTML exports, see pystylometry.viz.jsx.

Related GitHub Issues:
    #36 - Kilgarriff Chi-Squared drift detection
    #38 - Visualization Options for Style Drift Detection
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from .._types import KilgarriffDriftResult


class _ScatterDataPoint(TypedDict):
    """Type for scatter plot data points."""

    label: str
    mean_chi: float
    cv: float
    pattern: str


# Reference bounds for zone classification (empirically derived)
MEAN_CHI_LOW = 100  # Below: AI-like baseline
MEAN_CHI_HIGH = 250  # Above: Human-like baseline
CV_LOW = 0.08  # Below: Very stable
CV_HIGH = 0.20  # Above: Volatile (potential discontinuity)


def plot_drift_timeline(
    result: "KilgarriffDriftResult",
    output: str | Path | None = None,
    title: str | None = None,
    figsize: tuple[float, float] = (12, 6),
    show_spike_threshold: bool = True,
    show_ai_threshold: bool = True,
) -> None:
    """
    Plot chi-squared values as a timeline showing drift patterns.

    Creates a line chart with window pair index on x-axis and chi-squared
    value on y-axis. Highlights spike locations and shows reference thresholds.

    Args:
        result: KilgarriffDriftResult from compute_kilgarriff_drift()
        output: Path to save figure (shows interactively if None)
        title: Custom title (auto-generated if None)
        figsize: Figure size in inches (width, height)
        show_spike_threshold: Show horizontal line at spike detection threshold
        show_ai_threshold: Show horizontal line at AI baseline threshold

    Example:
        >>> result = compute_kilgarriff_drift(text)
        >>> plot_drift_timeline(result, output="timeline.png")
    """
    from . import _check_viz_available

    _check_viz_available()

    import matplotlib.pyplot as plt
    import seaborn as sns  # type: ignore[import-untyped]

    # Extract data
    chi_values = [s["chi_squared"] for s in result.pairwise_scores]
    x = list(range(len(chi_values)))

    # Set up style
    sns.set_theme(style="whitegrid", palette="muted")

    fig, ax = plt.subplots(figsize=figsize)

    # Main line plot
    ax.plot(x, chi_values, linewidth=2, color="#2563eb", marker="o", markersize=4, alpha=0.8)

    # Fill under curve
    ax.fill_between(x, chi_values, alpha=0.2, color="#2563eb")

    # Mark spike location
    if result.max_location is not None and result.max_location < len(chi_values):
        ax.axvline(
            x=result.max_location,
            color="#dc2626",
            linestyle="--",
            linewidth=2,
            alpha=0.7,
            label=f"Max χ² at window {result.max_location}",
        )
        ax.scatter(
            [result.max_location],
            [chi_values[result.max_location]],
            color="#dc2626",
            s=150,
            zorder=5,
            edgecolors="white",
            linewidth=2,
        )

    # Reference thresholds
    if show_ai_threshold:
        ax.axhline(
            y=50,
            color="#f59e0b",
            linestyle=":",
            linewidth=1.5,
            alpha=0.7,
            label="AI baseline threshold (~50)",
        )

    if show_spike_threshold and result.mean_chi_squared > 0:
        spike_threshold = result.mean_chi_squared + 2 * result.std_chi_squared
        ax.axhline(
            y=spike_threshold,
            color="#10b981",
            linestyle=":",
            linewidth=1.5,
            alpha=0.7,
            label=f"Spike threshold (μ+2σ = {spike_threshold:.0f})",
        )

    # Mean line
    ax.axhline(
        y=result.mean_chi_squared,
        color="#6b7280",
        linestyle="-",
        linewidth=1,
        alpha=0.5,
        label=f"Mean χ² = {result.mean_chi_squared:.1f}",
    )

    # Labels and title
    ax.set_xlabel("Window Pair Index", fontsize=12)
    ax.set_ylabel("Chi-squared (χ²)", fontsize=12)

    if title is None:
        pattern_label = result.pattern.replace("_", " ").title()
        title = f"Stylistic Drift Timeline — Pattern: {pattern_label}"
    ax.set_title(title, fontsize=14, fontweight="bold")

    # Legend
    ax.legend(loc="upper right", framealpha=0.9)

    # Stats annotation
    stats_text = (
        f"Mean: {result.mean_chi_squared:.1f}\n"
        f"Std: {result.std_chi_squared:.1f}\n"
        f"Windows: {result.window_count}"
    )
    ax.annotate(
        stats_text,
        xy=(0.02, 0.98),
        xycoords="axes fraction",
        verticalalignment="top",
        fontsize=10,
        family="monospace",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.8),
    )

    plt.tight_layout()

    if output:
        plt.savefig(output, dpi=150, bbox_inches="tight")
        plt.close()
    else:
        plt.show()


def plot_drift_scatter(
    results: list[tuple[str, "KilgarriffDriftResult"]],
    output: str | Path | None = None,
    title: str = "Style Drift Detection — Reference Zone Plot",
    figsize: tuple[float, float] = (10, 8),
    show_zones: bool = True,
    annotate_points: bool = True,
) -> None:
    """
    Plot multiple documents on a scatter plot with reference zones.

    Creates a tic-tac-toe style visualization where:
    - X-axis: Mean chi-squared (baseline stylistic variation)
    - Y-axis: Coefficient of variation (volatility)
    - Zones indicate expected classifications (human, AI, splice, etc.)

    Args:
        results: List of (label, KilgarriffDriftResult) tuples
        output: Path to save figure (shows interactively if None)
        title: Chart title
        figsize: Figure size in inches
        show_zones: Show reference zone boundaries and labels
        annotate_points: Label each point with its name

    Example:
        >>> results = [
        ...     ("Document A", compute_kilgarriff_drift(text_a)),
        ...     ("Document B", compute_kilgarriff_drift(text_b)),
        ... ]
        >>> plot_drift_scatter(results, output="scatter.png")
    """
    from . import _check_viz_available

    _check_viz_available()

    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt
    import seaborn as sns  # type: ignore[import-untyped]

    # Extract data
    data: list[_ScatterDataPoint] = []
    for label, result in results:
        mean_chi = result.mean_chi_squared
        cv = result.std_chi_squared / mean_chi if mean_chi > 0 else 0
        data.append(
            {
                "label": label,
                "mean_chi": mean_chi,
                "cv": cv,
                "pattern": result.pattern,
            }
        )

    # Set up style
    sns.set_theme(style="whitegrid")

    fig, ax = plt.subplots(figsize=figsize)

    # Define zone colors
    zone_colors = {
        "human_normal": "#dcfce7",  # Light green
        "human_tight": "#d1fae5",  # Lighter green
        "ai_uniform": "#fee2e2",  # Light red
        "ai_like": "#fef3c7",  # Light yellow
        "splice": "#fecaca",  # Light red-orange
        "transition": "#f3f4f6",  # Light gray
    }

    if show_zones:
        # Draw zone backgrounds
        # Bottom-right: Human zones
        ax.axvspan(
            MEAN_CHI_HIGH, 450, ymin=0, ymax=CV_HIGH, alpha=0.3, color=zone_colors["human_normal"]
        )
        ax.axvspan(
            MEAN_CHI_HIGH,
            450,
            ymin=0,
            ymax=CV_LOW / 1.0,
            alpha=0.4,
            color=zone_colors["human_tight"],
        )

        # Bottom-left: AI zone
        ax.axvspan(
            0, MEAN_CHI_LOW, ymin=0, ymax=CV_HIGH, alpha=0.3, color=zone_colors["ai_uniform"]
        )

        # Top zones: Splice/volatile
        ax.axvspan(
            MEAN_CHI_HIGH, 450, ymin=CV_HIGH, ymax=1.0, alpha=0.3, color=zone_colors["splice"]
        )

        # Middle: Transition
        ax.axvspan(
            MEAN_CHI_LOW,
            MEAN_CHI_HIGH,
            ymin=0,
            ymax=1.0,
            alpha=0.2,
            color=zone_colors["transition"],
        )

        # Draw reference lines
        ax.axvline(x=MEAN_CHI_LOW, color="#9ca3af", linestyle="--", linewidth=1.5, alpha=0.7)
        ax.axvline(x=MEAN_CHI_HIGH, color="#9ca3af", linestyle="--", linewidth=1.5, alpha=0.7)
        ax.axhline(y=CV_LOW, color="#9ca3af", linestyle="--", linewidth=1.5, alpha=0.7)
        ax.axhline(y=CV_HIGH, color="#9ca3af", linestyle="--", linewidth=1.5, alpha=0.7)

        # Zone labels
        ax.text(
            50, 0.04, "AI-UNIFORM", fontsize=9, ha="center", va="center", color="#6b7280", alpha=0.8
        )
        ax.text(
            50, 0.5, "ANOMALOUS", fontsize=9, ha="center", va="center", color="#6b7280", alpha=0.8
        )
        ax.text(
            175,
            0.14,
            "TRANSITION",
            fontsize=9,
            ha="center",
            va="center",
            color="#6b7280",
            alpha=0.8,
        )
        ax.text(
            350,
            0.04,
            "HUMAN-TIGHT",
            fontsize=9,
            ha="center",
            va="center",
            color="#6b7280",
            alpha=0.8,
        )
        ax.text(
            350, 0.14, "HUMAN", fontsize=9, ha="center", va="center", color="#059669", alpha=0.9
        )
        ax.text(
            350, 0.5, "SPLICE", fontsize=9, ha="center", va="center", color="#dc2626", alpha=0.9
        )

    # Color points by pattern
    pattern_colors = {
        "consistent": "#22c55e",  # Green
        "sudden_spike": "#ef4444",  # Red
        "gradual_drift": "#f59e0b",  # Amber
        "suspiciously_uniform": "#8b5cf6",  # Purple
        "unknown": "#6b7280",  # Gray
    }

    # Plot points
    for d in data:
        color = pattern_colors.get(d["pattern"], "#6b7280")
        ax.scatter(
            d["mean_chi"],
            d["cv"],
            s=200,
            c=color,
            edgecolors="white",
            linewidth=2,
            zorder=5,
            alpha=0.9,
        )

        if annotate_points:
            ax.annotate(
                d["label"],
                (d["mean_chi"], d["cv"]),
                xytext=(8, 8),
                textcoords="offset points",
                fontsize=9,
                fontweight="bold",
                color="#1f2937",
            )

    # Axis labels and limits
    ax.set_xlabel("Mean χ² (Baseline Stylistic Variation)", fontsize=12)
    ax.set_ylabel("CV (Coefficient of Variation)", fontsize=12)
    ax.set_xlim(0, max(450, max(d["mean_chi"] for d in data) * 1.1))
    ax.set_ylim(0, max(1.0, max(d["cv"] for d in data) * 1.1))

    ax.set_title(title, fontsize=14, fontweight="bold", pad=20)

    # Legend for patterns
    legend_handles = [
        mpatches.Patch(color=pattern_colors["consistent"], label="Consistent"),
        mpatches.Patch(color=pattern_colors["sudden_spike"], label="Sudden Spike"),
        mpatches.Patch(color=pattern_colors["gradual_drift"], label="Gradual Drift"),
        mpatches.Patch(color=pattern_colors["suspiciously_uniform"], label="Suspiciously Uniform"),
    ]
    ax.legend(handles=legend_handles, loc="upper right", title="Detected Pattern", framealpha=0.9)

    # Reference bounds annotation
    bounds_text = (
        f"Reference Bounds:\n"
        f"  Mean χ² < {MEAN_CHI_LOW}: AI baseline\n"
        f"  Mean χ² > {MEAN_CHI_HIGH}: Human baseline\n"
        f"  CV < {CV_LOW}: Very stable\n"
        f"  CV > {CV_HIGH}: Volatile"
    )
    ax.annotate(
        bounds_text,
        xy=(0.02, 0.98),
        xycoords="axes fraction",
        verticalalignment="top",
        fontsize=8,
        family="monospace",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.8),
    )

    plt.tight_layout()

    if output:
        plt.savefig(output, dpi=150, bbox_inches="tight")
        plt.close()
    else:
        plt.show()


def plot_drift_report(
    result: "KilgarriffDriftResult",
    label: str = "Document",
    output: str | Path | None = None,
    figsize: tuple[float, float] = (14, 10),
) -> None:
    """
    Generate a comprehensive drift analysis report with multiple panels.

    Creates a multi-panel figure with:
    - Timeline of chi-squared values
    - Histogram of chi-squared distribution
    - Summary statistics panel
    - Top contributing words at spike location

    Args:
        result: KilgarriffDriftResult from compute_kilgarriff_drift()
        label: Document label for title
        output: Path to save figure (shows interactively if None)
        figsize: Figure size in inches

    Example:
        >>> result = compute_kilgarriff_drift(text)
        >>> plot_drift_report(result, label="My Document", output="report.png")
    """
    from . import _check_viz_available

    _check_viz_available()

    import matplotlib.pyplot as plt
    import seaborn as sns  # type: ignore[import-untyped]

    # Extract data
    chi_values = [s["chi_squared"] for s in result.pairwise_scores]
    cv = result.std_chi_squared / result.mean_chi_squared if result.mean_chi_squared > 0 else 0

    # Set up style
    sns.set_theme(style="whitegrid")

    fig = plt.figure(figsize=figsize, constrained_layout=True)

    # Create grid layout
    gs = fig.add_gridspec(3, 2, height_ratios=[2, 1, 1], hspace=0.3, wspace=0.3)

    # Panel 1: Timeline (spans full width)
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(chi_values, linewidth=2, color="#2563eb", marker="o", markersize=4, alpha=0.8)
    ax1.fill_between(range(len(chi_values)), chi_values, alpha=0.2, color="#2563eb")

    if result.max_location is not None and result.max_location < len(chi_values):
        ax1.axvline(x=result.max_location, color="#dc2626", linestyle="--", linewidth=2, alpha=0.7)
        ax1.scatter(
            [result.max_location],
            [chi_values[result.max_location]],
            color="#dc2626",
            s=150,
            zorder=5,
            edgecolors="white",
            linewidth=2,
        )

    ax1.axhline(y=result.mean_chi_squared, color="#6b7280", linestyle="-", linewidth=1, alpha=0.5)
    ax1.set_xlabel("Window Pair Index")
    ax1.set_ylabel("Chi-squared (χ²)")
    ax1.set_title("Chi-squared Timeline", fontsize=12, fontweight="bold")

    # Panel 2: Histogram
    ax2 = fig.add_subplot(gs[1, 0])
    sns.histplot(chi_values, kde=True, ax=ax2, color="#2563eb", alpha=0.6)
    ax2.axvline(x=result.mean_chi_squared, color="#dc2626", linestyle="--", linewidth=2)
    ax2.set_xlabel("Chi-squared (χ²)")
    ax2.set_ylabel("Count")
    ax2.set_title("Distribution", fontsize=12, fontweight="bold")

    # Panel 3: Summary statistics
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.axis("off")

    pattern_label = result.pattern.replace("_", " ").title()
    stats_text = (
        f"Pattern: {pattern_label}\n"
        f"Confidence: {result.pattern_confidence:.1%}\n"
        f"─────────────────────\n"
        f"Mean χ²: {result.mean_chi_squared:.1f}\n"
        f"Std χ²: {result.std_chi_squared:.1f}\n"
        f"CV: {cv:.3f}\n"
        f"Min χ²: {result.min_chi_squared:.1f}\n"
        f"Max χ²: {result.max_chi_squared:.1f}\n"
        f"─────────────────────\n"
        f"Windows: {result.window_count}\n"
        f"Window Size: {result.window_size}\n"
        f"Stride: {result.stride}\n"
        f"Overlap: {result.overlap_ratio:.0%}"
    )

    ax3.text(
        0.1,
        0.9,
        stats_text,
        transform=ax3.transAxes,
        fontsize=11,
        family="monospace",
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#f8fafc", edgecolor="#e2e8f0"),
    )
    ax3.set_title("Summary Statistics", fontsize=12, fontweight="bold")

    # Panel 4: Top contributing words at spike
    ax4 = fig.add_subplot(gs[2, 0])
    if result.max_location is not None and result.max_location < len(result.pairwise_scores):
        spike_data = result.pairwise_scores[result.max_location]
        if "top_words" in spike_data and spike_data["top_words"]:
            words = spike_data["top_words"][:10]
            word_labels = [w[0] for w in words]
            word_values = [w[1] for w in words]

            ax4.barh(word_labels[::-1], word_values[::-1], color="#2563eb", alpha=0.7)
            ax4.set_xlabel("χ² Contribution")
            ax4.set_title(
                f"Top Contributors at Spike (Window {result.max_location})",
                fontsize=12,
                fontweight="bold",
            )
        else:
            ax4.text(
                0.5,
                0.5,
                "No word data available",
                ha="center",
                va="center",
                transform=ax4.transAxes,
            )
            ax4.set_title("Top Contributors at Spike", fontsize=12, fontweight="bold")
    else:
        ax4.text(0.5, 0.5, "No spike detected", ha="center", va="center", transform=ax4.transAxes)
        ax4.set_title("Top Contributors at Spike", fontsize=12, fontweight="bold")

    # Panel 5: Zone classification
    ax5 = fig.add_subplot(gs[2, 1])
    ax5.axis("off")

    # Determine zone
    if result.mean_chi_squared < MEAN_CHI_LOW:
        baseline_zone = "AI-like baseline"
    elif result.mean_chi_squared > MEAN_CHI_HIGH:
        baseline_zone = "Human-like baseline"
    else:
        baseline_zone = "Transition zone"

    if cv < CV_LOW:
        volatility_zone = "Very stable"
    elif cv > CV_HIGH:
        volatility_zone = "Volatile"
    else:
        volatility_zone = "Normal volatility"

    zone_text = (
        f"Zone Classification\n"
        f"═══════════════════════\n\n"
        f"Baseline: {baseline_zone}\n"
        f"  Mean χ² = {result.mean_chi_squared:.1f}\n\n"
        f"Volatility: {volatility_zone}\n"
        f"  CV = {cv:.3f}\n\n"
        f"═══════════════════════\n"
        f"Reference Bounds:\n"
        f"  AI: Mean χ² < {MEAN_CHI_LOW}\n"
        f"  Human: Mean χ² > {MEAN_CHI_HIGH}\n"
        f"  Stable: CV < {CV_LOW}\n"
        f"  Volatile: CV > {CV_HIGH}"
    )

    ax5.text(
        0.1,
        0.9,
        zone_text,
        transform=ax5.transAxes,
        fontsize=10,
        family="monospace",
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#f8fafc", edgecolor="#e2e8f0"),
    )
    ax5.set_title("Zone Classification", fontsize=12, fontweight="bold")

    # Main title
    fig.suptitle(
        f"Drift Analysis Report: {label}",
        fontsize=16,
        fontweight="bold",
        y=0.98,
    )

    if output:
        plt.savefig(output, dpi=150, bbox_inches="tight")
        plt.close()
    else:
        plt.show()
