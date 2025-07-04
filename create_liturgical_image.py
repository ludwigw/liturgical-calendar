import sys
import datetime
from pathlib import Path
from liturgical_calendar.services.image_service import ImageService
from liturgical_calendar.config.settings import Settings

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
    # Optionally load config file from argument or default location
    config_path = None
    if len(sys.argv) > 2:
        config_path = sys.argv[2]
    Settings.load_from_file(config_path)  # Loads config from file/env if present
    # Parse date argument
    if len(sys.argv) > 1:
        try:
            date = datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
        except Exception:
            print('Invalid date format. Use YYYY-MM-DD.')
            sys.exit(1)
    else:
        date = datetime.date.today()
    date_str = get_date_str(date)

    # Create ImageService with config
    image_service = ImageService(config=SimpleConfig)
    
    # Generate image using the service
    result = image_service.generate_liturgical_image(date_str)
    
    if result.get('success'):
        print(f"Saved image to {result.get('file_path')}")
        print(f"Feast: {result.get('feast_info', {}).get('name', 'Unknown')}")
    else:
        print(f"Error generating image: {result.get('error', 'Unknown error')}")
        sys.exit(1)

if __name__ == "__main__":
    main() 