from PIL import Image, ImageDraw
from pathlib import Path
import os
from liturgical_calendar.config.settings import Settings

class LiturgicalImageBuilder:
    def __init__(self, config):
        self.config = config
        self.width = getattr(config, 'IMAGE_WIDTH', Settings.IMAGE_WIDTH)
        self.height = getattr(config, 'IMAGE_HEIGHT', Settings.IMAGE_HEIGHT)
        self.bg_color = getattr(config, 'BG_COLOR', Settings.BG_COLOR)

    def create_base_image(self, width=None, height=None, bg_color=None):
        w = width if width is not None else self.width
        h = height if height is not None else self.height
        color = bg_color if bg_color is not None else self.bg_color
        img = Image.new('RGB', (w, h), color)
        return img

    def paste_artwork(self, image, artwork_path, position, size):
        """Paste artwork at the given position and size. Handles missing/corrupt images gracefully."""
        if not artwork_path or not isinstance(artwork_path, str) or not os.path.isfile(artwork_path):
            art_img = Image.new('RGB', size, (230, 230, 230))
        else:
            try:
                art_img = Image.open(artwork_path).convert('RGB')
                art_img = art_img.resize(size)
            except Exception:
                art_img = Image.new('RGB', size, (230, 230, 230))
        image.paste(art_img, position)
        return image

    def draw_text(self, image, text, position, font, color):
        draw = ImageDraw.Draw(image)
        draw.text(position, text, font=font, fill=color)
        return image

    def build_image(self, date_str, liturgical_info, artwork_info, layout, fonts, out_path):
        """
        Orchestrate the full image build given all layout info and resources.
        layout: dict with keys for header, artwork, title, readings, etc.
        fonts: dict of loaded fonts
        out_path: where to save the image
        """
        img = self.create_base_image()
        draw = ImageDraw.Draw(img)

        # Header
        for part in ['season', 'dash', 'date']:
            part_info = layout['header'][part]
            self.draw_text(img, part_info['text'], part_info['pos'], part_info['font'], layout['colors']['text'])

        # Artwork
        main_art = layout['artwork']['main']
        main_artwork = main_art.get('artwork')
        main_art_path = main_artwork.get('cached_file') if isinstance(main_artwork, dict) else None
        self.paste_artwork(img, main_art_path, main_art['pos'], main_art['size'])
        if layout['artwork'].get('show_next'):
            next_art = layout['artwork']['next']
            next_artwork = next_art.get('artwork')
            next_art_path = next_artwork.get('cached_file') if isinstance(next_artwork, dict) else None
            self.paste_artwork(img, next_art_path, next_art['pos'], next_art['size'])
            if 'next_label' in layout['artwork']:
                nl = layout['artwork']['next_label']
                self.draw_text(img, nl['text'], nl['pos'], nl['font'], layout['colors']['text'])
            if 'next_title' in layout['artwork']:
                nt = layout['artwork']['next_title']
                self.draw_text(img, nt['text'], nt['pos'], nt['font'], layout['colors']['text'])
            if 'next_date' in layout['artwork']:
                nd = layout['artwork']['next_date']
                self.draw_text(img, nd['text'], nd['pos'], nd['font'], layout['colors']['text'])

        # Title
        for line_info in layout['title']['lines']:
            self.draw_text(img, line_info['text'], line_info['pos'], line_info['font'], layout['colors']['text'])

        # Readings/Week
        self.draw_text(img, layout['readings']['week']['text'], layout['readings']['week']['pos'], layout['readings']['week']['font'], layout['colors']['text'])
        for r in layout['readings']['readings']:
            self.draw_text(img, r['text'], r['pos'], r['font'], layout['colors']['text'])
        # Vertical line
        line_rect = layout['readings']['vertical_line']['rect']
        draw.rectangle(line_rect, fill=layout['colors']['line'])

        # Save
        img.save(out_path)
        return out_path 