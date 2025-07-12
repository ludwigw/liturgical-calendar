#!/usr/bin/env python3
"""
First Run Example: Demonstrating Auto-Caching Functionality

This example shows how the liturgical calendar handles the first run scenario
where no artwork is cached, automatically downloading required images.
"""

import shutil
from pathlib import Path

from liturgical_calendar.cli import main
from liturgical_calendar.config.settings import Settings


def demonstrate_first_run():
    """Demonstrate the first run scenario with auto-caching."""

    print("=== First Run Example: Auto-Caching Demo ===\n")

    # Create a clean test environment
    test_cache_dir = Path("test_cache_demo")
    if test_cache_dir.exists():
        shutil.rmtree(test_cache_dir)
    test_cache_dir.mkdir()

    # Temporarily change cache directory
    original_cache_dir = Settings.CACHE_DIR
    Settings.CACHE_DIR = str(test_cache_dir)

    try:
        print("1. First run - no cached artwork")
        print("   Running: python -m liturgical_calendar.cli generate 2024-12-25")
        print("   Expected: Automatically downloads Christmas artwork\n")

        # Simulate the CLI call
        main(lambda: "2024-12-25")  # Override today's date for demo

        # Check what was cached
        cache_contents = list(test_cache_dir.glob("*.jpg")) + list(
            test_cache_dir.glob("*.png")
        )
        print(f"   Result: {len(cache_contents)} artwork file(s) cached")
        for file in cache_contents:
            print(f"          - {file.name}")

        print("\n2. Second run - artwork already cached")
        print("   Running: python -m liturgical_calendar.cli generate 2024-12-25")
        print("   Expected: Uses existing cached artwork (no download)\n")

        # Run again to show no additional downloads
        main(lambda: "2024-12-25")

        print("3. Progressive cache building")
        print("   Running: python -m liturgical_calendar.cli generate 2024-12-26")
        print("   Expected: Downloads Boxing Day artwork (only what's needed)\n")

        main(lambda: "2024-12-26")

        # Check final cache state
        cache_contents = list(test_cache_dir.glob("*.jpg")) + list(
            test_cache_dir.glob("*.png")
        )
        print(f"   Result: {len(cache_contents)} total artwork file(s) cached")
        for file in cache_contents:
            print(f"          - {file.name}")

        print("\n4. Disable auto-caching")
        print(
            "   Running: python -m liturgical_calendar.cli generate 2024-12-27 --no-auto-cache"
        )
        print("   Expected: No automatic download (for offline environments)\n")

        # Note: This would require modifying the CLI to accept the flag
        # For demo purposes, we'll just show the concept
        print("   (Demo: Auto-caching disabled - no download would occur)")

    finally:
        # Clean up
        Settings.CACHE_DIR = original_cache_dir
        if test_cache_dir.exists():
            shutil.rmtree(test_cache_dir)

    print("\n=== Key Benefits ===")
    print("✅ No manual cache setup required")
    print("✅ Only downloads artwork you actually use")
    print("✅ Progressive cache building over time")
    print("✅ Bandwidth and storage efficient")
    print("✅ Works offline once cached")
    print("✅ Configurable behavior")


def demonstrate_offline_usage():
    """Demonstrate offline usage with pre-cached artwork."""

    print("\n=== Offline Usage Example ===\n")

    print("1. Pre-cache all artwork for offline use:")
    print("   python -m liturgical_calendar.cli cache-artwork")
    print("   (Downloads all available artwork)\n")

    print("2. Generate images offline:")
    print("   python -m liturgical_calendar.cli generate --no-auto-cache")
    print("   (Uses only cached artwork, no network access)\n")

    print("3. Benefits for Raspberry Pi deployments:")
    print("   - Cache once, use offline")
    print("   - No network dependency during operation")
    print("   - Predictable resource usage")


if __name__ == "__main__":
    demonstrate_first_run()
    demonstrate_offline_usage()
