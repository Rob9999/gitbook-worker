#!/usr/bin/env python3
"""Find potential issues in emphasis/italic markdown blocks."""

import re
import sys
from pathlib import Path


def check_emphasis_blocks(filepath):
    """Check for problematic characters in emphasis blocks."""
    issues = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")

        # Find all emphasis blocks: *text* or _text_ or **text** or __text__
        emphasis_patterns = [
            (r"\*([^\*\n]+)\*", "asterisk"),
            (r"_([^_\n]+)_", "underscore"),
            (r"\*\*([^\*\n]+)\*\*", "double-asterisk"),
            (r"__([^_\n]+)__", "double-underscore"),
        ]

        for line_num, line in enumerate(lines, 1):
            for pattern, pattern_name in emphasis_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    text = match.group(1)

                    # Check for non-ASCII or problematic characters
                    try:
                        # Try to encode as latin-1 (what LaTeX might expect)
                        text.encode("latin-1")
                    except UnicodeEncodeError as e:
                        issues.append(
                            {
                                "file": filepath,
                                "line": line_num,
                                "pattern": pattern_name,
                                "text": text[:100],  # First 100 chars
                                "full_line": line,
                                "char": text[e.start : e.end],
                                "position": e.start,
                            }
                        )

                    # Check for specific problematic sequences
                    if "\u200b" in text:  # Zero-width space
                        issues.append(
                            {
                                "file": filepath,
                                "line": line_num,
                                "pattern": pattern_name,
                                "text": text[:100],
                                "issue": "Zero-width space found",
                            }
                        )

                    if "\ufeff" in text:  # BOM
                        issues.append(
                            {
                                "file": filepath,
                                "line": line_num,
                                "pattern": pattern_name,
                                "text": text[:100],
                                "issue": "BOM character found",
                            }
                        )

    except Exception as e:
        print(f"Error reading {filepath}: {e}")

    return issues


def scan_content_dir(content_dir):
    """Scan all markdown files."""
    content_path = Path(content_dir)
    all_issues = []

    for md_file in content_path.rglob("*.md"):
        issues = check_emphasis_blocks(md_file)
        if issues:
            all_issues.extend(issues)
            print(f"\n❌ Found issues in: {md_file}")
            for issue in issues:
                print(f"   Line {issue['line']}: {issue.get('pattern', '')}")
                if "char" in issue:
                    print(
                        f"   Problematic char: {repr(issue['char'])} at position {issue['position']}"
                    )
                if "issue" in issue:
                    print(f"   Issue: {issue['issue']}")
                print(f"   Text: {issue['text']}")
                print(f"   Full line: {issue.get('full_line', '')[:200]}")
                print()

    return all_issues


if __name__ == "__main__":
    repo_root = Path(__file__).parent.parent.parent.parent.parent
    content_dir = repo_root / "content"
    print(f"Scanning for emphasis issues in: {content_dir}\n")

    issues = scan_content_dir(content_dir)

    if issues:
        print(f"\n\n⚠️  Total issues found: {len(issues)}")
        sys.exit(1)
    else:
        print("\n\n✅ No emphasis/italic issues found!")
        sys.exit(0)
