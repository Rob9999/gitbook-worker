#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo: Smart Merge Font Configuration System

This script demonstrates how the hierarchical font configuration merge works:
1. Load base configuration from fonts.yml
2. Apply manifest overrides from publish.yml
3. Show final merged configuration
"""

import sys
from pathlib import Path

# Add gitbook_worker to path
sys.path.insert(0, str(Path(__file__).parent.parent / "gitbook_worker"))

from tools.publishing.font_config import get_font_config


def demo_smart_merge():
    """Demonstrate the smart merge system."""

    print("=" * 70)
    print("SMART MERGE FONT CONFIGURATION DEMO")
    print("=" * 70)
    print()

    # Step 1: Load base configuration
    print("📁 STEP 1: Load base configuration from fonts.yml")
    print("-" * 70)
    base_config = get_font_config()

    print(f"✓ Loaded {len(base_config.get_all_font_keys())} font configurations")
    print()

    print("CJK Font (before merge):")
    print(f"  Name: {base_config.get_font_name('CJK')}")
    print(f"  Paths: {base_config.get_font_paths('CJK')}")
    print()

    # Step 2: Simulate publish.yml manifest override
    print("📝 STEP 2: Apply publish.yml manifest override")
    print("-" * 70)

    # This simulates: fonts: [{ name: "ERDA CC-BY CJK", path: "..." }]
    manifest_fonts = [
        {
            "name": "ERDA CC-BY CJK",
            "path": ".github/fonts/erda-ccby-cjk/true-type/erda-ccby-cjk.ttf",
        }
    ]

    print("Manifest override:")
    print(f"  - name: {manifest_fonts[0]['name']}")
    print(f"    path: {manifest_fonts[0]['path']}")
    print()

    merged_config = base_config.merge_manifest_fonts(manifest_fonts)

    # Step 3: Show merged result
    print("✨ STEP 3: Merged configuration result")
    print("-" * 70)

    print("CJK Font (after merge):")
    print(f"  Name: {merged_config.get_font_name('CJK')}")
    print(f"  Paths: {merged_config.get_font_paths('CJK')}")
    print()

    # Verify other fonts unchanged
    print("Other fonts (unchanged):")
    for key in ["SERIF", "SANS", "MONO", "EMOJI"]:
        font = merged_config.get_font(key)
        if font:
            print(f"  {key}: {font.name}")
            if font.paths:
                print(f"    Paths: {font.paths}")
            else:
                print(f"    Paths: [] (system font)")

    print()

    # Step 4: Demonstrate hierarchy
    print("🔄 HIERARCHY DEMONSTRATION")
    print("-" * 70)
    print()
    print("Configuration Precedence:")
    print("  1. fonts.yml          → System defaults (lowest priority)")
    print("  2. publish.yml fonts: → Project overrides (medium priority)")
    print("  3. pdf_options:       → Output overrides (highest priority)")
    print()

    print("In this example:")
    print("  ├─ fonts.yml defines 3 fallback paths for CJK")
    print("  ├─ publish.yml overrides with single specific path")
    print("  └─ Result: CJK uses publish.yml path (precedence wins)")
    print()

    # Step 5: Show metadata preservation
    print("🔐 METADATA PRESERVATION")
    print("-" * 70)

    cjk_font = merged_config.get_font("CJK")
    print("License metadata (preserved from fonts.yml):")
    print(f"  License: {cjk_font.license}")
    print(f"  License URL: {cjk_font.license_url}")
    if cjk_font.source_url:
        print(f"  Source: {cjk_font.source_url}")
    print()

    print("=" * 70)
    print("✓ Demo complete!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        demo_smart_merge()
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
