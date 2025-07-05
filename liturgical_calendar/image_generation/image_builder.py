from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os
from liturgical_calendar.config.settings import Settings
from liturgical_calendar.logging import get_logger

class LiturgicalImageBuilder:
    def __init__(self, config=None):
        self.config = config
        self.logger = get_logger(__name__)
        self.width = getattr(config, 'IMAGE_WIDTH', Settings.IMAGE_WIDTH)
        self.height = getattr(config, 'IMAGE_HEIGHT', Settings.IMAGE_HEIGHT)
        self.bg_color = getattr(config, 'BG_COLOR', Settings.BG_COLOR)

    def create_base_image(self, width=None, height=None, bg_color=None):
        w = width if width is not None else self.width
        h = height if height is not None else self.height
        color = bg_color if bg_color is not None else self.bg_color
        img = Image.new('RGB', (w, h), color)
        return img

    def paste_artwork(self, image, artwork_path, position, size, artwork_info=None):
        """
        Paste artwork at the given position and size.
        
        Args:
            image: PIL Image to paste artwork onto
            artwork_path: Path to the artwork file
            position: (x, y) position to paste
            size: (width, height) size to resize artwork to
            artwork_info: Optional artwork information dict
        """
        if not artwork_path or not isinstance(artwork_path, str) or not os.path.isfile(artwork_path):
            self.logger.warning(f"Artwork file not found: {artwork_path}")
            # Create a simple gray placeholder
            art_img = Image.new('RGB', size, Settings.PLACEHOLDER_COLOR)
        else:
            try:
                art_img = Image.open(artwork_path).convert('RGB')
                art_img = art_img.resize(size, Image.LANCZOS)
                self.logger.debug(f"Successfully loaded artwork: {artwork_path}")
            except Exception as e:
                self.logger.error(f"Error loading artwork {artwork_path}: {e}")
                # Create a simple gray placeholder on error
                art_img = Image.new('RGB', size, Settings.PLACEHOLDER_COLOR)
        
        image.paste(art_img, position)
        return image



    def draw_text(self, image, text, position, font, color):
        draw = ImageDraw.Draw(image)
        draw.text(position, text, font=font, fill=color)
        return image

    def build_image(self, date_str, liturgical_info, artwork_info, layout, fonts, out_path):
        """
        Orchestrate the full image build given all layout info and resources with enhanced error handling.
        layout: dict with keys for header, artwork, title, readings, etc.
        fonts: dict of loaded fonts
        out_path: where to save the image
        """
        try:
            self.logger.info(f"Building image for {date_str}")
            img = self.create_base_image()
            draw = ImageDraw.Draw(img)

            # Header
            for part in ['season', 'dash', 'date']:
                part_info = layout['header'][part]
                self.draw_text(img, part_info['text'], part_info['pos'], part_info['font'], layout['colors']['text'])

            # Artwork with enhanced error handling
            main_art = layout['artwork']['main']
            main_artwork = main_art.get('artwork')
            main_art_path = main_artwork.get('cached_file') if isinstance(main_artwork, dict) else None
            
            # Log artwork status
            if main_artwork and isinstance(main_artwork, dict):
                if main_artwork.get('fallback'):
                    self.logger.info(f"Using fallback artwork for {date_str}: {main_artwork.get('fallback_type', 'unknown')}")
                elif main_artwork.get('placeholder'):
                    self.logger.info(f"Using placeholder artwork for {date_str}")
                else:
                    self.logger.info(f"Using primary artwork for {date_str}")
            
            self.paste_artwork(img, main_art_path, main_art['pos'], main_art['size'], main_artwork)
            
            if layout['artwork'].get('show_next'):
                next_art = layout['artwork']['next']
                next_artwork = next_art.get('artwork')
                next_art_path = next_artwork.get('cached_file') if isinstance(next_artwork, dict) else None
                self.paste_artwork(img, next_art_path, next_art['pos'], next_art['size'], next_artwork)
                
                # Next artwork text elements
                for text_element in ['next_label', 'next_title', 'next_date']:
                    if text_element in layout['artwork']:
                        text_info = layout['artwork'][text_element]
                        self.draw_text(img, text_info['text'], text_info['pos'], text_info['font'], layout['colors']['text'])

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

            # Save with error handling
            try:
                img.save(out_path, quality=95)
                self.logger.info(f"Image build completed for {date_str}: {out_path}")
            except Exception as e:
                self.logger.error(f"Error saving image for {date_str}: {e}")
                # Try saving with different format
                try:
                    out_path_png = str(out_path).replace('.jpg', '.png')
                    img.save(out_path_png)
                    self.logger.info(f"Image saved as PNG for {date_str}: {out_path_png}")
                    return out_path_png
                except Exception as e2:
                    self.logger.error(f"Failed to save image in any format for {date_str}: {e2}")
                    raise
            
            return out_path
        except Exception as e:
            self.logger.exception(f"Error building image for {date_str}: {e}")
            raise 