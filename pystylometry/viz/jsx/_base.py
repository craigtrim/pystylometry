"""Shared utilities for JSX/HTML visualization exports.

This module provides the HTML wrapper template and common utilities
used by all JSX-based visualizations.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def generate_html_document(
    title: str,
    config: dict[str, Any],
    react_component: str,
    component_name: str,
    extra_styles: str = "",
) -> str:
    """
    Generate a self-contained HTML document with React via CDN.

    Args:
        title: Page title
        config: Configuration object to embed as JSON
        react_component: The React component code (JSX)
        component_name: Name of the root component to render
        extra_styles: Additional CSS styles to include

    Returns:
        Complete HTML document as string
    """
    config_json = json.dumps(config, indent=2)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <script src="https://unpkg.com/react@18/umd/react.production.min.js" crossorigin></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js" crossorigin></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <style>
    * {{
      box-sizing: border-box;
    }}
    body {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      margin: 0;
      padding: 20px;
      background: #f8fafc;
      color: #1f2937;
    }}
    #root {{
      max-width: 1100px;
      margin: 0 auto;
    }}
    {extra_styles}
  </style>
</head>
<body>
  <div id="root"></div>
  <script type="text/babel">
    const CONFIG = {config_json};

    {react_component}

    ReactDOM.createRoot(document.getElementById('root')).render(<{component_name} />);
  </script>
</body>
</html>"""


def write_html_file(path: str | Path, content: str) -> Path:
    """Write HTML content to file, creating parent directories as needed."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content)
    return output_path


# Shared color interpolation function as a JavaScript string
COLOR_INTERPOLATION_JS = """
    // Color interpolation: blue -> amber -> red based on distance
    function getPointColor(distance) {
      const colors = [
        { r: 147, g: 197, b: 253 }, // #93c5fd (blue)
        { r: 251, g: 191, b: 36 },  // #fbbf24 (amber)
        { r: 239, g: 68, b: 68 },   // #ef4444 (red)
      ];

      const t = Math.min(1, Math.max(0, distance));
      let c1, c2, localT;

      if (t < 0.5) {
        c1 = colors[0];
        c2 = colors[1];
        localT = t * 2;
      } else {
        c1 = colors[1];
        c2 = colors[2];
        localT = (t - 0.5) * 2;
      }

      const r = Math.round(c1.r + (c2.r - c1.r) * localT);
      const g = Math.round(c1.g + (c2.g - c1.g) * localT);
      const b = Math.round(c1.b + (c2.b - c1.b) * localT);

      return `rgb(${r}, ${g}, ${b})`;
    }
"""


# Common CSS for cards and panels
CARD_STYLES = """
    .card {
      background: white;
      border-radius: 8px;
      border: 1px solid #e2e8f0;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
      padding: 16px;
    }
    .card-title {
      margin: 0 0 12px;
      font-size: 14px;
      font-weight: 600;
      color: #1f2937;
    }
    .stat-row {
      display: flex;
      justify-content: space-between;
      padding: 4px 0;
      font-size: 13px;
      color: #4b5563;
    }
    .stat-label {
      font-weight: 500;
    }
    .stat-value {
      font-family: ui-monospace, monospace;
    }
"""
