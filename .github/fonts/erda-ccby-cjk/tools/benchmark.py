#!/usr/bin/env python3
"""
Performance Benchmark Suite for ERDA CC-BY CJK Font Generator.

This tool measures and tracks build performance over time to ensure
optimizations have the desired effect and to detect performance regressions.

Metrics tracked:
- Build time (seconds)
- Memory usage (MB)
- Output file size (KB)
- Character processing rate (chars/sec)
- Index initialization time

Usage:
    python benchmark.py                  # Run single benchmark
    python benchmark.py --runs 5         # Average over 5 runs
    python benchmark.py --compare HASH   # Compare with git commit
"""

import argparse
import gc
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def get_git_info() -> Dict[str, str]:
    """Get current git commit information."""
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=Path(__file__).parent.parent,
            text=True,
        ).strip()

        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=Path(__file__).parent.parent,
            text=True,
        ).strip()

        # Check if there are uncommitted changes
        status = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=Path(__file__).parent.parent,
            text=True,
        ).strip()

        dirty = " (dirty)" if status else ""

        return {"commit": commit + dirty, "branch": branch, "dirty": bool(status)}
    except subprocess.CalledProcessError:
        return {"commit": "unknown", "branch": "unknown", "dirty": False}


def measure_build() -> Dict[str, any]:
    """Measure a single font build.

    Returns:
        Dictionary with build metrics
    """
    generator_dir = Path(__file__).parent.parent / "generator"
    build_script = generator_dir / "build_ccby_cjk_font.py"
    output_file = generator_dir.parent / "true-type" / "erda-ccby-cjk.ttf"

    if not build_script.exists():
        raise FileNotFoundError(f"Build script not found: {build_script}")

    # Remove old output file
    if output_file.exists():
        output_file.unlink()

    # Measure build time
    start_time = time.perf_counter()

    # Set UTF-8 encoding for subprocess on Windows
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    result = subprocess.run(
        [sys.executable, str(build_script)],
        cwd=generator_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )

    end_time = time.perf_counter()
    build_time = end_time - start_time

    if result.returncode != 0:
        raise RuntimeError(f"Build failed:\n{result.stderr}")

    # Get output file size
    if not output_file.exists():
        raise FileNotFoundError(f"Output file not created: {output_file}")

    file_size = output_file.stat().st_size / 1024  # KB

    # Parse output for character count
    char_count = 0
    for line in result.stdout.split("\n"):
        if "TOTAL REQUIRED CHARACTERS:" in line:
            # Extract number from "🎯 TOTAL REQUIRED CHARACTERS: 505"
            parts = line.split(":")
            if len(parts) == 2:
                char_count = int(parts[1].strip())
                break
        elif "Required characters:" in line and "INFO:" in line:
            # Fallback: "INFO: Required characters: 505"
            parts = line.split(":")
            if len(parts) >= 3:
                char_count = int(parts[2].strip())
                break

    # Calculate processing rate
    chars_per_sec = char_count / build_time if build_time > 0 else 0

    return {
        "build_time_seconds": round(build_time, 3),
        "file_size_kb": round(file_size, 2),
        "character_count": char_count,
        "chars_per_second": round(chars_per_sec, 1),
        "success": True,
    }


def run_benchmarks(runs: int = 1) -> Dict[str, any]:
    """Run multiple benchmarks and average results.

    Args:
        runs: Number of benchmark runs to average

    Returns:
        Dictionary with averaged results and statistics
    """
    print(f"Running {runs} benchmark(s)...")
    print("=" * 70)

    results = []

    for i in range(runs):
        print(f"\n📊 Run {i+1}/{runs}...")

        # Force garbage collection before each run
        gc.collect()

        try:
            result = measure_build()
            results.append(result)

            print(f"   Build time:  {result['build_time_seconds']:.3f}s")
            print(f"   File size:   {result['file_size_kb']:.2f} KB")
            print(f"   Characters:  {result['character_count']}")
            print(f"   Rate:        {result['chars_per_second']:.1f} chars/sec")

        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            return {"success": False, "error": str(e)}

    # Calculate averages
    avg_build_time = sum(r["build_time_seconds"] for r in results) / len(results)
    avg_file_size = sum(r["file_size_kb"] for r in results) / len(results)
    avg_chars_per_sec = sum(r["chars_per_second"] for r in results) / len(results)

    # Calculate standard deviation for build time
    if len(results) > 1:
        variance = sum(
            (r["build_time_seconds"] - avg_build_time) ** 2 for r in results
        ) / len(results)
        std_dev = variance**0.5
    else:
        std_dev = 0.0

    return {
        "success": True,
        "runs": len(results),
        "timestamp": datetime.now().isoformat(),
        "system": {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "processor": platform.processor(),
        },
        "git": get_git_info(),
        "metrics": {
            "build_time_seconds": round(avg_build_time, 3),
            "build_time_std_dev": round(std_dev, 3),
            "file_size_kb": round(avg_file_size, 2),
            "character_count": results[0]["character_count"],  # Same for all runs
            "chars_per_second": round(avg_chars_per_sec, 1),
        },
    }


def save_benchmark(result: Dict, filepath: Optional[Path] = None) -> Path:
    """Save benchmark result to JSON file.

    Args:
        result: Benchmark result dictionary
        filepath: Optional custom filepath (default: benchmarks/TIMESTAMP.json)

    Returns:
        Path to saved file
    """
    if filepath is None:
        benchmarks_dir = Path(__file__).parent.parent / "benchmarks"
        benchmarks_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filepath = benchmarks_dir / f"benchmark-{timestamp}.json"

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    return filepath


def print_summary(result: Dict):
    """Print human-readable benchmark summary."""
    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)

    if not result.get("success"):
        print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
        return

    metrics = result["metrics"]

    print(f"\n📈 Performance Metrics:")
    print(f"   Build Time:      {metrics['build_time_seconds']:.3f}s", end="")
    if result["runs"] > 1:
        print(f" ± {metrics['build_time_std_dev']:.3f}s")
    else:
        print()
    print(f"   File Size:       {metrics['file_size_kb']:.2f} KB")
    print(f"   Characters:      {metrics['character_count']}")
    print(f"   Processing Rate: {metrics['chars_per_second']:.1f} chars/sec")

    print(f"\n🔧 System Information:")
    sys_info = result["system"]
    print(f"   Platform:  {sys_info['platform']}")
    print(f"   Python:    {sys_info['python_version']}")

    git_info = result["git"]
    print(f"\n📦 Git Information:")
    print(f"   Commit:  {git_info['commit']}")
    print(f"   Branch:  {git_info['branch']}")

    print(f"\n⏱️  Runs: {result['runs']}")
    print(f"📅 Timestamp: {result['timestamp']}")
    print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Font Generator Performance Benchmark")
    parser.add_argument(
        "--runs", type=int, default=1, help="Number of runs to average (default: 1)"
    )
    parser.add_argument("--save", action="store_true", help="Save results to JSON file")
    parser.add_argument("--output", type=str, help="Custom output file path")

    args = parser.parse_args()

    # Run benchmarks
    result = run_benchmarks(runs=args.runs)

    # Print summary
    print_summary(result)

    # Save results if requested
    if args.save and result.get("success"):
        output_path = Path(args.output) if args.output else None
        saved_path = save_benchmark(result, output_path)
        print(f"\n💾 Results saved to: {saved_path}")

    # Return exit code
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
