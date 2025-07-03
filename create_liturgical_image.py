import sys
import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from liturgical_calendar.services.feast_service import FeastService
from liturgical_calendar.services.image_service import ImageService
from liturgical_calendar.image_generation.layout_engine import LayoutEngine
from liturgical_calendar.image_generation.font_manager import FontManager

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

def get_date_str(date):
    return date.strftime('%Y-%m-%d')

def get_friendly_date(date):
    return date.strftime('%-d %B, %Y')

def get_text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height

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

    # Create base image
    img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Layout engine
    layout_engine = LayoutEngine()
    fonts = {'serif': serif_font_36, 'sans_uc': sans_font_36_uc}
    # Row 1: Season (sans, uppercase) — Date (serif)
    season = info.get('season', '').upper()
    date_text = f"{friendly_date}"
    header_layout = layout_engine.create_header_layout(season, date_text, fonts, draw, WIDTH, PADDING)
    # Draw header using layout
    for part in ['season', 'dash', 'date']:
        part_info = header_layout[part]
        draw.text(part_info['pos'], part_info['text'], font=part_info['font'], fill=TEXT_COLOR)
    baseline_y = header_layout['baseline_y']

    # Row 2: Artwork (centered)
    art_y = baseline_y + ROW_SPACING
    # Ensure next_artwork is always defined
    next_artwork = None
    main_artwork_img = None
    if artwork and artwork.get('cached_file'):
        try:
            main_artwork_img = Image.open(artwork['cached_file']).convert('RGB')
        except Exception:
            main_artwork_img = None
    if not main_artwork_img:
        # Try to find the next available artwork after this date
        from datetime import timedelta
        search_date = date
        for _ in range(366):  # Search up to a year ahead
            search_date += timedelta(days=1)
            next_artwork_candidate = image_service.get_artwork_for_date(get_date_str(search_date))
            if next_artwork_candidate and next_artwork_candidate.get('cached_file'):
                next_artwork = next_artwork_candidate
                next_artwork['date'] = get_friendly_date(search_date)
                break
    # Use layout engine for artwork layout
    fonts_for_artwork = {
        'serif': serif_font_36,
        'sans': sans_font_36,
        'sans_32': font_manager.get_font(SANS_FONT, 32),
        'sans_26': font_manager.get_font(SANS_FONT, 26),
    }
    artwork_layout = layout_engine.create_artwork_layout(
        artwork, next_artwork, WIDTH, ARTWORK_SIZE, art_y, fonts=fonts_for_artwork, draw=draw
    )
    # Main artwork
    main_art = artwork_layout['main']
    main_img = None
    if main_art['artwork'] and main_art['artwork'].get('cached_file'):
        try:
            main_img = Image.open(main_art['artwork']['cached_file']).convert('RGB')
        except Exception:
            main_img = None
    if not main_img:
        main_img = Image.new('RGB', main_art['size'], (230, 230, 230))
    img.paste(main_img.resize(main_art['size']), main_art['pos'])
    # Next artwork thumbnail (if present)
    if artwork_layout.get('show_next'):
        next_art = artwork_layout['next']
        thumb_img = None
        if next_art['artwork'] and next_art['artwork'].get('cached_file'):
            try:
                thumb_img = Image.open(next_art['artwork']['cached_file']).convert('RGB').resize(next_art['size'])
            except Exception:
                thumb_img = None
        if thumb_img:
            img.paste(thumb_img, next_art['pos'])
        # Draw 'NEXT:' label and next artwork title
        if 'next_label' in artwork_layout:
            nl = artwork_layout['next_label']
            draw.text(nl['pos'], nl['text'], font=nl['font'], fill=TEXT_COLOR)
        if 'next_title' in artwork_layout:
            nt = artwork_layout['next_title']
            draw.text(nt['pos'], nt['text'], font=nt['font'], fill=TEXT_COLOR)
        if 'next_date' in artwork_layout:
            nd = artwork_layout['next_date']
            draw.text(nd['pos'], nd['text'], font=nd['font'], fill=TEXT_COLOR)

    # Row 3: Artwork title (serif, 96px, centered, wrap if too long)
    if artwork and artwork.get('name', ''):
        title = artwork.get('name', '')
    else:
        title = date.strftime('%A')  # Use weekday name if no artwork
    title_y = art_y + ARTWORK_SIZE + ROW_SPACING
    # Replace Unicode colon with sans-serif colon for rendering
    title = title.replace('：', ':')
    fonts_for_title = {
        'serif_96': serif_font_96,
    }
    title_layout = layout_engine.create_title_layout(
        title, fonts_for_title, draw, WIDTH, PADDING, TITLE_FONT_SIZE, TITLE_LINE_HEIGHT, title_y, font_manager=font_manager
    )
    for line_info in title_layout['lines']:
        draw.text(line_info['pos'], line_info['text'], font=line_info['font'], fill=TEXT_COLOR)
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
        week, readings, fonts_for_readings, draw, WIDTH, PADDING, col_y, 48, font_manager=font_manager
    )
    draw.text(readings_layout['week']['pos'], readings_layout['week']['text'], font=readings_layout['week']['font'], fill=TEXT_COLOR)
    for r in readings_layout['readings']:
        draw.text(r['pos'], r['text'], font=r['font'], fill=TEXT_COLOR)
    line_rect = readings_layout['vertical_line']['rect']
    draw.rectangle(line_rect, fill=LINE_COLOR)

    # Save image
    build_dir = Path(__file__).parent / 'build'
    build_dir.mkdir(exist_ok=True)
    if len(sys.argv) > 1:
        out_path = build_dir / f"liturgical_{date_str}.png"
    else:
        out_path = build_dir / "liturgical-today.png"
    img.save(out_path)
    print(f"Saved image to {out_path}")

if __name__ == "__main__":
    main() 