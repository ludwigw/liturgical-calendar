import sys
import datetime
from pathlib import Path
from liturgical_calendar.services.image_service import ImageService
from liturgical_calendar.config.settings import Settings
from liturgical_calendar.exceptions import LiturgicalCalendarError
from liturgical_calendar.logging import setup_logging, get_logger

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
    return date.strftime('%Y-%m-%d')

def main():
    # Parse --verbose flag
    verbose = False
    args = sys.argv[1:]
    if '--verbose' in args:
        verbose = True
        args.remove('--verbose')
    setup_logging(level='DEBUG' if verbose else 'INFO')
    logger = get_logger(__name__)
    if verbose:
        print("[INFO] Verbose mode enabled (log level: DEBUG)")
    try:
        logger.info("Starting create_liturgical_image script")
        # Optionally load config file from argument or default location
        config_path = None
        if len(args) > 1:
            config_path = args[1]
        Settings.load_from_file(config_path)  # Loads config from file/env if present
        logger.info(f"Loaded config from {config_path or 'default'}")
        # Parse date argument
        if len(args) > 0:
            try:
                date = datetime.datetime.strptime(args[0], '%Y-%m-%d').date()
            except Exception:
                logger.error('Invalid date format. Use YYYY-MM-DD.')
                print('Invalid date format. Use YYYY-MM-DD.')
                sys.exit(1)
        else:
            date = datetime.date.today()
        date_str = get_date_str(date)
        # Create ImageService with config
        image_service = ImageService(config=SimpleConfig)
        logger.info(f"Generating image for {date_str}")
        # Generate image using the service
        result = image_service.generate_liturgical_image(date_str)
        if result.get('success'):
            print(f"Saved image to {result.get('file_path')}")
            print(f"Feast: {result.get('feast_info', {}).get('name', 'Unknown')}")
            logger.info(f"Image generated successfully: {result.get('file_path')}")
        else:
            logger.error(f"Error generating image: {result.get('error', 'Unknown error')}")
            print(f"Error generating image: {result.get('error', 'Unknown error')}")
            sys.exit(1)
        logger.info("Image generation completed successfully")
    except LiturgicalCalendarError as e:
        logger.error(f"Liturgical Calendar Error: {e}")
        print(f"Liturgical Calendar Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Error in create_liturgical_image: {e}")
        print(f"Error in create_liturgical_image: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if '--help' in sys.argv or '-h' in sys.argv:
        print("Usage: python create_liturgical_image.py [YYYY-MM-DD] [config.yaml] [--verbose]")
        print("  [YYYY-MM-DD]   Optional date to generate image for (default: today)")
        print("  [config.yaml]  Optional path to config file")
        print("  --verbose      Enable verbose (DEBUG) logging output")
        sys.exit(0)
    main() 