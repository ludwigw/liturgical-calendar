import sys
import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from liturgical_calendar.services.feast_service import FeastService
from liturgical_calendar.services.image_service import ImageService
from liturgical_calendar.image_generation.layout_engine import LayoutEngine
from liturgical_calendar.image_generation.font_manager import FontManager
from liturgical_calendar.image_generation.image_builder import LiturgicalImageBuilder

# Font paths
FONTS_DIR = Path(__file__).parent / 'fonts'

SERIF_FONT = 'HappyTimes-Regular.otf'
SANS_FONT = 'HankenGrotesk-Medium.ttf'

# Image settings
WIDTH, HEIGHT = 1404, 1872
PADDING = 48
ARTWORK_SIZE = 1080
ROW_SPACING = 48

# Font sizes
HEADER_FONT_SIZE = 36
TITLE_FONT_SIZE = 96
TITLE_LINE_HEIGHT = 1.2
COLUMN_FONT_SIZE = 36

# Colors
BG_COLOR = (255, 255, 255)
TEXT_COLOR = (74, 74, 74)  # #4A4A4A
LINE_COLOR = (151, 151, 151)

# Create service instances
feast_service = FeastService()
image_service = ImageService()
font_manager = FontManager(FONTS_DIR)

class SimpleConfig:
    IMAGE_WIDTH = WIDTH
    IMAGE_HEIGHT = HEIGHT
    BG_COLOR = BG_COLOR


def get_date_str(date):
    return date.strftime('%Y-%m-%d')

def get_friendly_date(date):
    return date.strftime('%-d %B, %Y')

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
    friendly_date = get_friendly_date(date)

    # Get liturgical info
    info = feast_service.get_liturgical_info(date_str)
    artwork = image_service.get_artwork_for_date(date_str, info)

    # Prepare fonts
    serif_font_36 = font_manager.get_font(SERIF_FONT, HEADER_FONT_SIZE)
    serif_font_96 = font_manager.get_font(SERIF_FONT, TITLE_FONT_SIZE)
    sans_font_36 = font_manager.get_font(SANS_FONT, COLUMN_FONT_SIZE)
    sans_font_36_uc = font_manager.get_font(SANS_FONT, COLUMN_FONT_SIZE)

    # Layout engine
    layout_engine = LayoutEngine()
    fonts = {'serif': serif_font_36, 'sans_uc': sans_font_36_uc}
    # Row 1: Season (sans, uppercase) — Date (serif)
    season = info.get('season', '').upper()
    date_text = f"{friendly_date}"
    header_layout = layout_engine.create_header_layout(season, date_text, fonts, None, WIDTH, PADDING, font_manager=font_manager)
    baseline_y = header_layout['baseline_y']

    # Row 2: Artwork (centered)
    art_y = baseline_y + ROW_SPACING
    next_artwork = None
    main_artwork_img = None
    if artwork and artwork.get('cached_file'):
        try:
            main_artwork_img = Image.open(artwork['cached_file']).convert('RGB')
        except Exception:
            main_artwork_img = None
    if not main_artwork_img:
        from datetime import timedelta
        search_date = date
        for _ in range(366):
            search_date += timedelta(days=1)
            next_artwork_candidate = image_service.get_artwork_for_date(get_date_str(search_date))
            if next_artwork_candidate and next_artwork_candidate.get('cached_file'):
                next_artwork = next_artwork_candidate
                next_artwork['date'] = get_friendly_date(search_date)
                break
    fonts_for_artwork = {
        'serif': serif_font_36,
        'sans': sans_font_36,
        'sans_32': font_manager.get_font(SANS_FONT, 32),
        'sans_26': font_manager.get_font(SANS_FONT, 26),
    }
    artwork_layout = layout_engine.create_artwork_layout(
        artwork, next_artwork, WIDTH, ARTWORK_SIZE, art_y, fonts=fonts_for_artwork, draw=None, font_manager=font_manager
    )

    # Row 3: Artwork title
    if artwork and artwork.get('name', ''):
        title = artwork.get('name', '')
    else:
        title = date.strftime('%A')
    title_y = art_y + ARTWORK_SIZE + ROW_SPACING
    title = title.replace('：', ':')
    fonts_for_title = {
        'serif_96': serif_font_96,
    }
    title_layout = layout_engine.create_title_layout(
        title, fonts_for_title, None, WIDTH, PADDING, TITLE_FONT_SIZE, TITLE_LINE_HEIGHT, title_y, font_manager=font_manager
    )
    last_title_baseline = title_layout['last_baseline']

    # Row 4: Two columns (week name, readings)
    week = info.get('week', '').upper()
    readings = info.get('readings', [])
    if not readings:
        readings = ['No assigned readings for this day.']
    col_y = last_title_baseline + 96 - sans_font_36_uc.getmetrics()[0]
    fonts_for_readings = {
        'serif': serif_font_36,
        'sans_uc': sans_font_36_uc,
    }
    readings_layout = layout_engine.create_readings_layout(
        week, readings, fonts_for_readings, None, WIDTH, PADDING, col_y, 48, font_manager=font_manager
    )

    # Compose layout dict for builder
    layout = {
        'header': header_layout,
        'artwork': artwork_layout,
        'title': title_layout,
        'readings': readings_layout,
        'colors': {
            'text': TEXT_COLOR,
            'line': LINE_COLOR,
        },
    }
    fonts_dict = {
        'serif': serif_font_36,
        'serif_96': serif_font_96,
        'sans': sans_font_36,
        'sans_uc': sans_font_36_uc,
        'sans_32': font_manager.get_font(SANS_FONT, 32),
        'sans_26': font_manager.get_font(SANS_FONT, 26),
    }

    # Output path
    build_dir = Path(__file__).parent / 'build'
    build_dir.mkdir(exist_ok=True)
    if len(sys.argv) > 1:
        out_path = build_dir / f"liturgical_{date_str}.png"
    else:
        out_path = build_dir / "liturgical-today.png"

    # Use the builder
    builder = LiturgicalImageBuilder(SimpleConfig)
    builder.build_image(date_str, info, artwork, layout, fonts_dict, out_path)
    print(f"Saved image to {out_path}")

if __name__ == "__main__":
    main() 