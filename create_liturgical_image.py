import sys
import datetime
from pathlib import Path
from liturgical_calendar.image_generation.pipeline import ImageGenerationPipeline

# Image settings for config
WIDTH, HEIGHT = 1404, 1872
PADDING = 48
ARTWORK_SIZE = 1080
ROW_SPACING = 48
HEADER_FONT_SIZE = 36
TITLE_FONT_SIZE = 96
TITLE_LINE_HEIGHT = 1.2
COLUMN_FONT_SIZE = 36
BG_COLOR = (255, 255, 255)
TEXT_COLOR = (74, 74, 74)
LINE_COLOR = (151, 151, 151)
FONTS_DIR = Path(__file__).parent / 'fonts'

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

    pipeline = ImageGenerationPipeline(SimpleConfig)
    out_path = pipeline.generate_image(date_str)
    print(f"Saved image to {out_path}")

if __name__ == "__main__":
    main() 