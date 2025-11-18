#!/usr/bin/env python3
"""
ERDA CC-BY CJK Font CLI Tool

This CLI provides commands for managing the ERDA CJK font development workflow:
- Analyze dataset files to find required characters
- Check coverage against font modules
- Generate the font
- Install and cache the font

Usage:
    python font_cli.py analyze [--dataset PATH]
    python font_cli.py coverage [--dataset PATH]
    python font_cli.py generate [--install] [--refresh-cache]
    python font_cli.py build [--install] [--refresh-cache]  # Alias for generate
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Add generator directory to path for imports
GENERATOR_DIR = Path(__file__).parent
sys.path.insert(0, str(GENERATOR_DIR))

from hanzi import HANZI_KANJI
from hiragana import HIRAGANA
from katakana import (
    KATAKANA_BASE,
    SMALL_KATAKANA,
    DAKUTEN_COMBOS,
    HANDAKUTEN_COMBOS,
)
from punctuation import PUNCTUATION


class FontCLI:
    """CLI for ERDA CJK Font management."""

    def __init__(self):
        self.dataset_dir = GENERATOR_DIR.parent / "dataset"
        self.all_font_chars = self._collect_font_chars()

    def _collect_font_chars(self) -> Set[str]:
        """Collect all characters defined in font modules."""
        chars = set()
        chars.update(HANZI_KANJI.keys())
        chars.update(HIRAGANA.keys())
        chars.update(KATAKANA_BASE.keys())
        chars.update(SMALL_KATAKANA.keys())
        chars.update(DAKUTEN_COMBOS.keys())
        chars.update(HANDAKUTEN_COMBOS.keys())
        chars.update(PUNCTUATION.keys())
        return chars

    def _extract_cjk_from_text(self, text: str) -> Dict[str, Set[str]]:
        """
        Extract CJK characters from text and categorize them.

        Returns dict with keys: hanzi, hiragana, katakana, hangul, fullwidth
        """
        categories: Dict[str, Set[str]] = {
            "hanzi": set(),
            "hiragana": set(),
            "katakana": set(),
            "hangul": set(),
            "fullwidth": set(),
        }

        for char in text:
            code = ord(char)

            if 0x4E00 <= code <= 0x9FFF:
                categories["hanzi"].add(char)
            elif 0x3040 <= code <= 0x309F:
                categories["hiragana"].add(char)
            elif 0x30A0 <= code <= 0x30FF:
                categories["katakana"].add(char)
            elif 0xAC00 <= code <= 0xD7AF:
                categories["hangul"].add(char)
            elif 0xFF00 <= code <= 0xFFEF:
                categories["fullwidth"].add(char)

        return categories

    def _read_dataset_files(self, dataset_path: Path | None = None) -> str:
        """Read all markdown files from dataset directory."""
        if dataset_path:
            dataset_dir = Path(dataset_path)
        else:
            dataset_dir = self.dataset_dir

        if not dataset_dir.exists():
            print(f"❌ Dataset directory not found: {dataset_dir}")
            sys.exit(1)

        all_text = []
        md_files = list(dataset_dir.glob("*.md"))

        if not md_files:
            print(f"⚠️  No markdown files found in {dataset_dir}")
            return ""

        for md_file in sorted(md_files):
            print(f"📄 Reading: {md_file.name}")
            try:
                text = md_file.read_text(encoding="utf-8")
                all_text.append(text)
            except Exception as e:
                print(f"⚠️  Error reading {md_file.name}: {e}")

        return "\n\n".join(all_text)

    def analyze(self, dataset_path: Path | None = None) -> int:
        """
        Analyze dataset files and report required characters.

        Returns exit code (0 = success).
        """
        print("=" * 70)
        print("ERDA CJK Font Dataset Analysis")
        print("=" * 70)
        print()

        # Read all dataset files
        text = self._read_dataset_files(dataset_path)

        if not text:
            return 1

        # Extract CJK characters
        categories = self._extract_cjk_from_text(text)

        # Report findings
        print()
        print("📊 Character Analysis:")
        print()

        total_chars = 0
        for category, chars in categories.items():
            if not chars:
                continue

            count = len(chars)
            total_chars += count

            print(f"  {category.capitalize():12s}: {count:4d} unique characters")

            # Show sample (first 20)
            if count > 0:
                sample = "".join(sorted(chars)[:20])
                if count > 20:
                    sample += f"... (+{count-20} more)"
                print(f"  {'':12s}  {sample}")
                print()

        print(f"  {'TOTAL':12s}: {total_chars:4d} unique CJK characters")
        print()

        return 0

    def coverage(self, dataset_path: Path | None = None) -> int:
        """
        Check coverage of dataset characters against font modules.

        Returns exit code (0 = 100% coverage, 1 = missing characters).
        """
        print("=" * 70)
        print("ERDA CJK Font Coverage Check")
        print("=" * 70)
        print()

        # Read dataset files
        text = self._read_dataset_files(dataset_path)

        if not text:
            return 1

        # Extract CJK characters
        categories = self._extract_cjk_from_text(text)

        # Check coverage for each category
        print()
        print("🔍 Coverage Analysis:")
        print()

        all_missing: List[Tuple[str, str, int]] = []  # (category, char, code)
        all_covered = 0
        all_required = 0

        for category, chars in categories.items():
            if not chars:
                continue

            # Hangul is always 100% covered (generated algorithmically)
            if category == "hangul":
                count = len(chars)
                all_covered += count
                all_required += count
                print(
                    f"  {category.capitalize():12s}: {count:4d}/{count:4d} (100.0%) ✅ [Algorithmic]"
                )
                continue

            # Check other categories
            missing = []
            for char in sorted(chars):
                if char not in self.all_font_chars:
                    missing.append((category, char, ord(char)))

            covered = len(chars) - len(missing)
            required = len(chars)
            percentage = (covered / required * 100) if required > 0 else 0

            all_covered += covered
            all_required += required
            all_missing.extend(missing)

            status = "✅" if len(missing) == 0 else "❌"
            print(
                f"  {category.capitalize():12s}: {covered:4d}/{required:4d} ({percentage:5.1f}%) {status}"
            )

        # Overall summary
        print()
        print("─" * 70)
        overall_percentage = (
            (all_covered / all_required * 100) if all_required > 0 else 0
        )
        overall_status = "✅" if len(all_missing) == 0 else "❌"
        print(
            f"  {'TOTAL':12s}: {all_covered:4d}/{all_required:4d} ({overall_percentage:5.1f}%) {overall_status}"
        )
        print("─" * 70)
        print()

        # Report missing characters
        if all_missing:
            print()
            print("❌ Missing Characters:")
            print()

            # Group by category
            by_category: Dict[str, List[Tuple[str, int]]] = {}
            for category, char, code in all_missing:
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append((char, code))

            for category, chars_list in sorted(by_category.items()):
                print(f"  {category.capitalize()} ({len(chars_list)} missing):")
                chars_display = " ".join(
                    [f"{char}(U+{code:04X})" for char, code in chars_list[:10]]
                )
                if len(chars_list) > 10:
                    chars_display += f" ... (+{len(chars_list)-10} more)"
                print(f"    {chars_display}")
                print()

            print("💡 Next Steps:")
            print("  1. Add missing characters to respective font modules:")
            print("     - Hanzi/Kanji → generator/hanzi.py")
            print("     - Hiragana → generator/hiragana.py")
            print("     - Katakana → generator/katakana.py")
            print("     - Punctuation → generator/punctuation.py")
            print("  2. Run: python font_cli.py coverage")
            print("  3. Run: python font_cli.py generate --install --refresh-cache")
            print()

            return 1
        else:
            print("✅ All characters are covered!")
            print()
            print("💡 Ready to build:")
            print("   python font_cli.py generate --install --refresh-cache")
            print()
            return 0

    def generate(self, install: bool = False, refresh_cache: bool = False) -> int:
        """
        Generate the font using build_ccby_cjk_font.py.

        Args:
            install: Install font to system
            refresh_cache: Refresh font cache

        Returns exit code (0 = success).
        """
        print("=" * 70)
        print("ERDA CJK Font Generation")
        print("=" * 70)
        print()

        # Import build function
        try:
            from build_ccby_cjk_font import (
                build_font,
                install_font,
                refresh_font_cache,
            )
        except ImportError as e:
            print(f"❌ Failed to import build_ccby_cjk_font: {e}")
            return 1

        try:
            # Build font
            print("🔨 Building font...")
            output_path = build_font()
            print()

            # Install if requested
            if install:
                if install_font(output_path):
                    print()
                else:
                    print("⚠️  Font installation had issues")
                    print()

            # Refresh cache if requested
            if refresh_cache:
                refresh_font_cache()
                print()

            print("=" * 70)
            print("✅ Font generation completed successfully")
            print("=" * 70)
            print()

            return 0

        except Exception as e:
            print(f"❌ Font generation failed: {e}")
            import traceback

            traceback.print_exc()
            return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ERDA CC-BY CJK Font CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze dataset to see what characters are required
  python font_cli.py analyze

  # Check coverage of current font implementation
  python font_cli.py coverage

  # Generate and install font with cache refresh
  python font_cli.py generate --install --refresh-cache

  # Use custom dataset directory
  python font_cli.py analyze --dataset /path/to/dataset
  python font_cli.py coverage --dataset /path/to/dataset
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze dataset files to find required characters"
    )
    analyze_parser.add_argument(
        "--dataset",
        type=str,
        help="Path to dataset directory (default: ../dataset/)",
    )

    # Coverage command
    coverage_parser = subparsers.add_parser(
        "coverage", help="Check coverage against font modules"
    )
    coverage_parser.add_argument(
        "--dataset",
        type=str,
        help="Path to dataset directory (default: ../dataset/)",
    )

    # Generate command
    generate_parser = subparsers.add_parser(
        "generate", help="Generate the font (alias: build)"
    )
    generate_parser.add_argument(
        "--install", action="store_true", help="Install font to system"
    )
    generate_parser.add_argument(
        "--refresh-cache", action="store_true", help="Refresh font cache"
    )

    # Build command (alias for generate)
    build_parser = subparsers.add_parser("build", help="Generate the font")
    build_parser.add_argument(
        "--install", action="store_true", help="Install font to system"
    )
    build_parser.add_argument(
        "--refresh-cache", action="store_true", help="Refresh font cache"
    )

    args = parser.parse_args()

    # Show help if no command
    if not args.command:
        parser.print_help()
        return 0

    # Initialize CLI
    cli = FontCLI()

    # Execute command
    try:
        if args.command == "analyze":
            dataset_path = Path(args.dataset) if args.dataset else None
            return cli.analyze(dataset_path)

        elif args.command == "coverage":
            dataset_path = Path(args.dataset) if args.dataset else None
            return cli.coverage(dataset_path)

        elif args.command in ("generate", "build"):
            return cli.generate(install=args.install, refresh_cache=args.refresh_cache)

        else:
            print(f"❌ Unknown command: {args.command}")
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
