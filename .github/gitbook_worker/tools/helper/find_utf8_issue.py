#!/usr/bin/env python3
"""Find UTF-8 encoding issues in markdown files around line 6193."""

import sys
from pathlib import Path


def find_invalid_utf8_in_file(filepath):
    """Check a file for invalid UTF-8 sequences."""
    issues = []
    try:
        with open(filepath, "rb") as f:
            content = f.read()

        # Try to decode as UTF-8
        try:
            content.decode("utf-8")
        except UnicodeDecodeError as e:
            issues.append({"file": filepath, "position": e.start, "reason": str(e)})
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

    return issues


def scan_content_dir(content_dir):
    """Scan all markdown files in content directory."""
    content_path = Path(content_dir)
    all_issues = []

    for md_file in content_path.rglob("*.md"):
        issues = find_invalid_utf8_in_file(md_file)
        if issues:
            all_issues.extend(issues)
            print(f"\n❌ Found issues in: {md_file}")
            for issue in issues:
                print(f"   Position: {issue['position']}")
                print(f"   Reason: {issue['reason']}")

                # Show context
                with open(md_file, "rb") as f:
                    f.seek(max(0, issue["position"] - 100))
                    context = f.read(200)
                    print(f"   Context (bytes): {context}")

    return all_issues


if __name__ == "__main__":
    # Navigate from .github/gitbook_worker/tools/helper to repository root
    repo_root = Path(__file__).parent.parent.parent.parent.parent
    content_dir = repo_root / "content"
    print(f"Scanning for UTF-8 issues in: {content_dir}")

    issues = scan_content_dir(content_dir)

    if issues:
        print(f"\n\n⚠️  Total issues found: {len(issues)}")
        sys.exit(1)
    else:
        print("\n\n✅ No UTF-8 encoding issues found!")
        sys.exit(0)
