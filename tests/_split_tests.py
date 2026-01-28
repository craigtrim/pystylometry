#!/usr/bin/env python3
"""Split multi-class test files into one file per class.

Each output file gets:
  - The original module docstring (adapted)
  - All imports from the original
  - All module-level code (constants, fixtures, helper functions)
  - Exactly one test class

Usage:
    python tests/_split_tests.py [--dry-run]
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).parent


def class_name_to_filename(class_name: str, prefix: str = "") -> str:
    """Convert TestFooBar to test_foo_bar.py, with optional prefix."""
    # Remove 'Test' prefix
    name = class_name
    if name.startswith("Test"):
        name = name[4:]
    # CamelCase to snake_case
    name = re.sub(r"(?<=[a-z0-9])([A-Z])", r"_\1", name)
    name = re.sub(r"(?<=[A-Z])([A-Z][a-z])", r"_\1", name)
    base = name.lower()
    if prefix:
        return f"test_{prefix}_{base}.py"
    return f"test_{base}.py"


def find_classes(source: str) -> list[tuple[str, int, int]]:
    """Find all top-level classes and their line ranges (1-indexed)."""
    tree = ast.parse(source)
    classes = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            end_line = node.end_lineno or node.lineno
            classes.append((node.name, node.lineno, end_line))
    return classes


def find_header_end(source: str, classes: list[tuple[str, int, int]]) -> int:
    """Find the last line before the first class (1-indexed)."""
    if not classes:
        return len(source.splitlines())
    return classes[0][1] - 1


def get_fixture_names_used_by_class(source_lines: list[str], start: int, end: int) -> set[str]:
    """Extract fixture names from method signatures in a class.

    Uses AST parsing to reliably handle multi-line signatures.
    """
    fixtures: set[str] = set()
    class_text = "\n".join(source_lines[start - 1 : end])
    try:
        tree = ast.parse(class_text)
    except SyntaxError:
        return fixtures

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for arg in node.args.args:
                if arg.arg != "self":
                    fixtures.add(arg.arg)
    return fixtures


def get_header_fixtures(header_lines: list[str]) -> dict[str, tuple[int, int]]:
    """Find fixture function definitions in the header and their line ranges (0-indexed into header_lines)."""
    fixtures: dict[str, tuple[int, int]] = {}
    i = 0
    while i < len(header_lines):
        line = header_lines[i]
        # Check for @pytest.fixture decorator
        if "@pytest.fixture" in line:
            # Find the def line
            j = i + 1
            while j < len(header_lines) and not header_lines[j].strip().startswith("def "):
                j += 1
            if j < len(header_lines):
                def_line = header_lines[j]
                match = re.match(r"def\s+(\w+)\s*\(", def_line)
                if match:
                    func_name = match.group(1)
                    # Find end of function (next non-indented line or next decorator)
                    k = j + 1
                    while k < len(header_lines):
                        next_line = header_lines[k]
                        if next_line.strip() == "":
                            k += 1
                            continue
                        # If next non-empty line is not indented (and not blank), function ended
                        if not next_line.startswith(" ") and not next_line.startswith("\t"):
                            break
                        k += 1
                    # Trim trailing blank lines
                    while k > j + 1 and header_lines[k - 1].strip() == "":
                        k -= 1
                    fixtures[func_name] = (i, k)
        i += 1
    return fixtures


def split_header_into_parts(header_lines: list[str]) -> tuple[list[str], dict[str, list[str]]]:
    """Split header into non-fixture lines and fixture blocks.

    Returns:
        (non_fixture_lines, {fixture_name: [lines]})
    """
    fixture_ranges = get_header_fixtures(header_lines)

    # Collect all fixture line indices
    fixture_line_indices: set[int] = set()
    fixture_blocks: dict[str, list[str]] = {}
    for name, (start, end) in fixture_ranges.items():
        for idx in range(start, end):
            fixture_line_indices.add(idx)
        fixture_blocks[name] = header_lines[start:end]

    # Non-fixture lines
    non_fixture = [line for i, line in enumerate(header_lines) if i not in fixture_line_indices]

    # Clean up excessive blank lines in non-fixture section
    cleaned: list[str] = []
    blank_count = 0
    for line in non_fixture:
        if line.strip() == "":
            blank_count += 1
            if blank_count <= 2:
                cleaned.append(line)
        else:
            blank_count = 0
            cleaned.append(line)

    return cleaned, fixture_blocks


def build_split_file(
    non_fixture_header: list[str],
    fixture_blocks: dict[str, list[str]],
    needed_fixtures: set[str],
    class_lines: list[str],
) -> str:
    """Build content for a split test file."""
    parts: list[str] = []

    # Header (imports, constants, etc.)
    parts.append("\n".join(non_fixture_header))

    # Only include needed fixtures
    for name in sorted(needed_fixtures):
        if name in fixture_blocks:
            parts.append("")  # blank separator
            parts.append("")
            parts.append("\n".join(fixture_blocks[name]))

    # The class itself
    parts.append("")
    parts.append("")
    parts.append("\n".join(class_lines))

    content = "\n".join(parts)

    # Ensure file ends with single newline
    content = content.rstrip("\n") + "\n"

    return content


def get_used_names_in_lines(lines: list[str]) -> set[str]:
    """Get all identifier-like names used in lines of code."""
    names: set[str] = set()
    for line in lines:
        names.update(re.findall(r"\b([A-Za-z_]\w*)\b", line))
    return names


def filter_imports(
    non_fixture_header: list[str], class_lines: list[str], fixture_lines: list[str]
) -> list[str]:
    """Filter imports to only include those used by the class and its fixtures."""
    # Get all names used in the class and fixture code
    all_code_lines = class_lines + fixture_lines
    used_names = get_used_names_in_lines(all_code_lines)

    # Also include names used in the header (constants etc.)
    # We'll be conservative and keep all non-import header lines
    result: list[str] = []
    i = 0
    header = non_fixture_header

    while i < len(header):
        line = header[i]
        stripped = line.strip()

        # Keep blank lines, comments, docstrings, constants
        if not stripped.startswith(("import ", "from ")):
            result.append(line)
            i += 1
            continue

        # Handle multi-line imports (with parentheses)
        if "(" in stripped and ")" not in stripped:
            # Collect the full import block
            import_lines = [line]
            i += 1
            while i < len(header) and ")" not in header[i]:
                import_lines.append(header[i])
                i += 1
            if i < len(header):
                import_lines.append(header[i])

            # Check if any imported name is used
            import_text = "\n".join(import_lines)
            # Extract imported names
            imported_names = set()
            for match in re.finditer(r"(\w+)(?:\s+as\s+(\w+))?", import_text):
                if match.group(2):
                    imported_names.add(match.group(2))
                else:
                    imported_names.add(match.group(1))

            # Always keep pytest, Path, math, etc. (common utilities)
            keep = bool(imported_names & used_names) or any(
                n in imported_names for n in ("pytest", "Path", "math", "re", "os", "sys")
            )
            if keep:
                result.extend(import_lines)
            i += 1
            continue

        # Simple single-line import
        # Extract what's being imported
        if stripped.startswith("from "):
            # from X import Y, Z
            match = re.match(r"from\s+\S+\s+import\s+(.+)", stripped)
            if match:
                names_str = match.group(1).strip().rstrip(",")
                imported = set()
                for part in names_str.split(","):
                    part = part.strip()
                    if " as " in part:
                        imported.add(part.split(" as ")[1].strip())
                    else:
                        imported.add(part.split("(")[0].strip())  # handle trailing (

                if imported & used_names or any(n in imported for n in ("pytest", "Path")):
                    result.append(line)
            else:
                result.append(line)
        elif stripped.startswith("import "):
            # import X
            module_name = stripped.split()[1].split(".")[0]
            if module_name in used_names or module_name in ("pytest", "math", "re"):
                result.append(line)

        i += 1

    return result


def module_prefix(filepath: Path) -> str:
    """Derive a prefix from the test file name.

    test_vocabulary_overlap.py -> vocab_overlap
    test_additional_authorship.py -> additional_authorship
    """
    name = filepath.stem  # e.g. test_vocabulary_overlap
    name = name.removeprefix("test_")
    # Shorten common long prefixes
    name = name.replace("vocabulary_", "vocab_")
    name = name.replace("additional_", "")
    name = name.replace("advanced_", "adv_")
    name = name.replace("word_frequency_", "word_freq_")
    return name


def collect_all_output_names(test_files: list[Path]) -> dict[str, list[Path]]:
    """First pass: collect all potential output filenames to detect conflicts."""
    name_to_sources: dict[str, list[Path]] = {}
    for tf in test_files:
        source = tf.read_text()
        classes = find_classes(source)
        if len(classes) <= 1:
            continue
        for class_name, _, _ in classes:
            out_name = class_name_to_filename(class_name)
            name_to_sources.setdefault(out_name, []).append(tf)
    return name_to_sources


def process_file(filepath: Path, conflicting_names: set[str], dry_run: bool = False) -> list[str]:
    """Process a single test file, splitting it into per-class files.

    Returns list of created file paths (as strings).
    """
    source = filepath.read_text()
    lines = source.splitlines()

    classes = find_classes(source)
    if len(classes) <= 1:
        return []

    prefix = module_prefix(filepath)
    header_end = find_header_end(source, classes)
    header_lines = lines[:header_end]

    # Split header into non-fixture parts and fixture blocks
    non_fixture_header, fixture_blocks = split_header_into_parts(header_lines)

    created_files: list[str] = []

    for class_name, start, end in classes:
        class_lines = lines[start - 1 : end]

        # Determine which fixtures this class needs
        needed_fixtures = get_fixture_names_used_by_class(lines, start, end)

        # Also check if fixtures reference other fixtures
        all_fixture_lines: list[str] = []
        for fname in list(needed_fixtures):
            if fname in fixture_blocks:
                all_fixture_lines.extend(fixture_blocks[fname])

        # Build output - keep full header (imports, constants) for safety
        content = build_split_file(non_fixture_header, fixture_blocks, needed_fixtures, class_lines)

        # Determine output filename - use prefix if name conflicts
        base_name = class_name_to_filename(class_name)
        if base_name in conflicting_names:
            out_name = class_name_to_filename(class_name, prefix=prefix)
        else:
            out_name = base_name
        out_path = filepath.parent / out_name

        if dry_run:
            print(f"  Would create: {out_name} ({class_name})")
        else:
            out_path.write_text(content)
            print(f"  Created: {out_name} ({class_name})")

        created_files.append(str(out_path))

    # Delete original file
    if not dry_run and created_files:
        filepath.unlink()
        print(f"  Deleted: {filepath.name}")

    return created_files


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("DRY RUN - no files will be modified\n")

    # Find all test files with multiple classes
    test_files = sorted(TESTS_DIR.glob("test_*.py"))

    # First pass: detect naming conflicts
    name_to_sources = collect_all_output_names(test_files)
    conflicting_names = {name for name, sources in name_to_sources.items() if len(sources) > 1}

    if conflicting_names:
        print(f"Detected {len(conflicting_names)} naming conflicts (will add module prefix):")
        for name in sorted(conflicting_names):
            sources = [p.name for p in name_to_sources[name]]
            print(f"  {name} <- {', '.join(sources)}")
        print()

    total_created = 0
    total_split = 0

    for tf in test_files:
        source = tf.read_text()
        classes = find_classes(source)
        if len(classes) <= 1:
            continue

        print(f"\n{tf.name} ({len(classes)} classes):")
        created = process_file(tf, conflicting_names, dry_run=dry_run)
        total_created += len(created)
        total_split += 1

    print(f"\nDone: split {total_split} files into {total_created} new files")


if __name__ == "__main__":
    main()
