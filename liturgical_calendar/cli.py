"""
Command-line interface for the liturgical calendar project. Supports image generation, artwork caching, and info queries.
"""

import argparse
import datetime
import sys
from pathlib import Path

from liturgical_calendar.caching.artwork_cache import ArtworkCache
from liturgical_calendar.config.settings import Settings
from liturgical_calendar.data.artwork_data import feasts as artwork_feasts
from liturgical_calendar.exceptions import LiturgicalCalendarError
from liturgical_calendar.liturgical import liturgical_calendar
from liturgical_calendar.logging import get_logger, setup_logging
from liturgical_calendar.services.config_service import ConfigService
from liturgical_calendar.services.image_service import ImageService

# Placeholder imports for future integration
# from liturgical_calendar.services.image_service import ImageService
# from liturgical_calendar.caching.artwork_cache import ArtworkCache
# from liturgical_calendar.services.config_service import ConfigService
# from liturgical_calendar.liturgical import liturgical_calendar
# from liturgical_calendar.config.settings import Settings
# from liturgical_calendar.logging import setup_logging, get_logger

VERSION = "1.0.0"  # Update as needed

# Image settings for config
WIDTH, HEIGHT = Settings.IMAGE_WIDTH, Settings.IMAGE_HEIGHT
PADDING = Settings.PADDING
ARTWORK_SIZE = Settings.ARTWORK_SIZE
ROW_SPACING = Settings.ROW_SPACING
HEADER_FONT_SIZE = Settings.HEADER_FONT_SIZE
TITLE_FONT_SIZE = Settings.TITLE_FONT_SIZE
TITLE_LINE_HEIGHT = Settings.TITLE_LINE_HEIGHT
COLUMN_FONT_SIZE = Settings.COLUMN_FONT_SIZE
BG_COLOR = Settings.BG_COLOR
TEXT_COLOR = Settings.TEXT_COLOR
LINE_COLOR = Settings.LINE_COLOR
FONTS_DIR = Settings.FONTS_DIR


class SimpleConfig:
    """Simple configuration holder for image generation settings."""

    IMAGE_WIDTH = WIDTH
    IMAGE_HEIGHT = HEIGHT
    BG_COLOR = BG_COLOR
    TEXT_COLOR = TEXT_COLOR
    LINE_COLOR = LINE_COLOR
    FONTS_DIR = FONTS_DIR
    PADDING = PADDING
    ARTWORK_SIZE = ARTWORK_SIZE
    ROW_SPACING = ROW_SPACING
    HEADER_FONT_SIZE = HEADER_FONT_SIZE
    TITLE_FONT_SIZE = TITLE_FONT_SIZE
    TITLE_LINE_HEIGHT = TITLE_LINE_HEIGHT
    COLUMN_FONT_SIZE = COLUMN_FONT_SIZE


def get_date_str(date):
    """Return a date string in YYYY-MM-DD format from a date object."""
    return date.strftime("%Y-%m-%d")


def main(today_func=datetime.date.today):
    """Main CLI entry point for parsing arguments and dispatching commands."""
    parser = argparse.ArgumentParser(
        prog="litcal",
        description="Liturgical Calendar CLI: generate images, cache artwork, query info, and more.",
    )
    parser.add_argument(
        "--config", type=str, help="Path to config file (optional)", default=None
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose (DEBUG) logging output"
    )

    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Subcommand to run"
    )

    # generate
    gen_parser = subparsers.add_parser(
        "generate", help="Generate a liturgical image for a date"
    )
    gen_parser.add_argument(
        "date", nargs="?", type=str, help="Date (YYYY-MM-DD), default: today"
    )
    gen_parser.add_argument("--output", type=str, help="Output file path (optional)")

    # cache-artwork
    cache_parser = subparsers.add_parser(
        "cache-artwork", help="Download/cache all artwork images"
    )
    cache_parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retry attempts for failed downloads (default: 3)",
    )
    cache_parser.add_argument(
        "--retry-delay",
        type=float,
        default=5.0,
        help="Base delay between retries in seconds (default: 5.0)",
    )

    # info
    info_parser = subparsers.add_parser("info", help="Show liturgical info for a date")
    info_parser.add_argument(
        "date", nargs="?", type=str, help="Date (YYYY-MM-DD), default: today"
    )

    # validate-config
    subparsers.add_parser(
        "validate-config", help="Validate the config file and print issues"
    )

    # version
    subparsers.add_parser("version", help="Show CLI version and exit")

    args = parser.parse_args()

    # Setup logging and config
    setup_logging(level="DEBUG" if args.verbose else "INFO")
    logger = get_logger(__name__)
    if args.verbose:
        print("[INFO] Verbose mode enabled (log level: DEBUG)")
    if args.config:
        print(f"[INFO] Using config file: {args.config}")
    Settings.load_from_file(args.config)
    logger.info("Loaded config from %s", args.config or "default")

    if args.command == "generate":
        # Parse date
        if args.date:
            try:
                date = datetime.datetime.strptime(args.date, "%Y-%m-%d").date()
            except ValueError:
                logger.error("Invalid date format. Use YYYY-MM-DD.")
                print("Invalid date format. Use YYYY-MM-DD.")
                sys.exit(1)
        else:
            date = today_func()
        date_str = get_date_str(date)
        # Create ImageService with config
        image_service = ImageService(config=SimpleConfig)
        logger.info("Generating image for %s", date_str)
        try:
            result = image_service.generate_liturgical_image(date_str)
            if result.get("success"):
                # Save to output path if provided, else use default
                file_path = result.get("file_path")
                if args.output:
                    # Move or copy the generated file to the requested output path
                    dest = Path(args.output)
                    Path(file_path).replace(dest)
                    file_path = str(dest)
                print(f"Saved image to {file_path}")
                print(f"Feast: {result.get('feast_info', {}).get('name', 'Unknown')}")
                logger.info("Image generated successfully: %s", file_path)
            else:
                logger.error(
                    "Error generating image: %s", result.get("error", "Unknown error")
                )
                print(f"Error generating image: {result.get('error', 'Unknown error')}")
                sys.exit(1)
            logger.info("Image generation completed successfully")
        except LiturgicalCalendarError as e:
            logger.error("Liturgical Calendar Error: %s", e)
            print(f"Liturgical Calendar Error: {e}")
            sys.exit(1)
        except (OSError, RuntimeError, ValueError) as e:
            logger.exception("Error in generate: %s", e)
            print(f"Error in generate: {e}")
            sys.exit(1)
    elif args.command == "cache-artwork":
        logger.info("Starting cache-artwork command")
        try:
            # Collect all unique source URLs from artwork_feasts
            urls = set()
            for season_dict in artwork_feasts.values():
                for entry_list in season_dict.values():
                    if isinstance(entry_list, list):
                        for entry in entry_list:
                            url = entry.get("source")
                            if url:
                                urls.add(url)
                    elif isinstance(entry_list, dict):
                        url = entry_list.get("source")
                        if url:
                            urls.add(url)

            cache = ArtworkCache()
            total = len(urls)

            print(f"Found {total} unique artwork URLs to cache")
            print(
                f"Retry settings: max_retries={args.max_retries}, retry_delay={args.retry_delay}s"
            )

            # Use batch caching with retry logic
            result = cache.cache_multiple_artwork(
                sorted(urls), max_retries=args.max_retries, retry_delay=args.retry_delay
            )

            # Report results
            print(
                f"\nSummary: {result['success']} cached, {result['failed']} failed, {result['total']} total."
            )
            if result["failed_urls"]:
                print(f"Failed URLs: {len(result['failed_urls'])}")
                if args.verbose:
                    for url in result["failed_urls"]:
                        print(f"  - {url}")

            logger.info(
                "Cache-artwork completed: %s cached, %s failed, %s total.",
                result["success"],
                result["failed"],
                result["total"],
            )

            # Exit with error code if any failed
            if result["failed"] > 0:
                print(f"Warning: {result['failed']} artwork items failed to cache")
                # Don't exit with error code for partial failures - this allows the system to continue

        except (OSError, RuntimeError, ValueError) as e:
            logger.exception("Error in cache-artwork: %s", e)
            print(f"Error in cache-artwork: {e}")
            sys.exit(1)
    elif args.command == "info":
        logger.info("Starting info command")

        if args.date:
            date_str = args.date
        else:
            date_str = today_func().strftime("%Y-%m-%d")
        try:
            result = liturgical_calendar(date_str)
            print(f"Date: {date_str}")
            print(f"Season: {result.get('season', 'Unknown')}")
            print(f"Week: {result.get('week', 'Unknown')}")
            print(f"Name: {result.get('name', 'Unknown')}")
            print(f"Colour: {result.get('colour', 'Unknown')}")
            logger.info("Info for %s: %s", date_str, result)
        except (ValueError, OSError, RuntimeError) as e:
            logger.exception("Error in info: %s", e)
            print(f"Error in info: {e}")
            sys.exit(1)
    elif args.command == "validate-config":
        logger.info("Starting validate-config command")
        try:
            config_service = ConfigService(args.config)
            result = config_service.validate_config()
            if result.get("valid", False):
                print("Config is valid.")
                if result.get("warnings"):
                    print("Warnings:")
                    for w in result["warnings"]:
                        print(f"  - {w}")
            else:
                print("Config is invalid.")
                if result.get("errors"):
                    print("Errors:")
                    for err in result["errors"]:
                        print(f"  - {err}")
                sys.exit(1)
        except (OSError, RuntimeError, ValueError) as e:
            logger.exception("Error in validate-config: %s", e)
            print(f"Error in validate-config: {e}")
            sys.exit(1)
    elif args.command == "version":
        print(f"litcal version {VERSION}")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
