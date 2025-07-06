"""
Image generation pipeline for the liturgical calendar project.
"""

from pathlib import Path

from liturgical_calendar.config.settings import Settings
from liturgical_calendar.core.artwork_manager import ArtworkManager
from liturgical_calendar.image_generation.font_manager import FontManager
from liturgical_calendar.image_generation.image_builder import LiturgicalImageBuilder
from liturgical_calendar.image_generation.layout_engine import LayoutEngine
from liturgical_calendar.logging import get_logger
from liturgical_calendar.services.feast_service import FeastService


class ImageGenerationPipeline:
    """Pipeline for generating liturgical calendar images from input data."""

    def __init__(self, config=None):
        self.config = config
        self.logger = get_logger(__name__)
        self.feast_service = FeastService()
        self.artwork_manager = ArtworkManager()
        self.font_manager = FontManager(
            getattr(config, "FONTS_DIR", Settings.FONTS_DIR)
        )
        self.layout_engine = LayoutEngine()
        self.builder = LiturgicalImageBuilder(config)
        self.width = getattr(config, "IMAGE_WIDTH", Settings.IMAGE_WIDTH)
        self.height = getattr(config, "IMAGE_HEIGHT", Settings.IMAGE_HEIGHT)
        self.padding = getattr(config, "PADDING", Settings.PADDING)
        self.artwork_size = getattr(config, "ARTWORK_SIZE", Settings.ARTWORK_SIZE)
        self.row_spacing = getattr(config, "ROW_SPACING", Settings.ROW_SPACING)
        self.header_font_size = getattr(
            config, "HEADER_FONT_SIZE", Settings.HEADER_FONT_SIZE
        )
        self.title_font_size = getattr(
            config, "TITLE_FONT_SIZE", Settings.TITLE_FONT_SIZE
        )
        self.title_line_height = getattr(
            config, "TITLE_LINE_HEIGHT", Settings.TITLE_LINE_HEIGHT
        )
        self.column_font_size = getattr(
            config, "COLUMN_FONT_SIZE", Settings.COLUMN_FONT_SIZE
        )
        self.bg_color = getattr(config, "BG_COLOR", Settings.BG_COLOR)
        self.text_color = getattr(config, "TEXT_COLOR", Settings.TEXT_COLOR)
        self.line_color = getattr(config, "LINE_COLOR", Settings.LINE_COLOR)

    def generate_image(
        self, date_str, out_path=None, feast_info=None, artwork_info=None
    ):
        """
        Generate an image for the given date with enhanced error handling.

        Args:
            date_str: Date string in YYYY-MM-DD format
            out_path: Optional output path for the image
            feast_info: Optional pre-prepared feast information
            artwork_info: Optional pre-prepared artwork information

        Returns:
            Path to the generated image file
        """
        try:
            self.logger.info(f"Starting image generation pipeline for {date_str}")

            # Prepare data with graceful degradation
            if feast_info and artwork_info:
                # Use pre-prepared data from service layer
                data = self._prepare_data_from_service(
                    date_str, feast_info, artwork_info
                )
            else:
                # Fallback to original data preparation (for backward compatibility)
                data = self._prepare_data(date_str)

            # Create layout and fonts
            try:
                layout, fonts = self._create_layout(data)
            except Exception as e:
                self.logger.error(f"Error creating layout for {date_str}: {e}")
                raise

            # Render image
            try:
                img = self._render_image(layout, fonts, data)
            except Exception as e:
                self.logger.error(f"Error rendering image for {date_str}: {e}")
                raise

            # Save image
            try:
                output_path = self._save_image(
                    img, date_str, layout, fonts, data, out_path
                )
            except Exception as e:
                self.logger.error(f"Error saving image for {date_str}: {e}")
                raise

            self.logger.info(f"Image generation pipeline completed for {date_str}")
            return output_path
        except Exception as e:
            self.logger.exception(
                f"Error in image generation pipeline for {date_str}: {e}"
            )
            raise

    def _prepare_data_from_service(self, date_str, feast_info, artwork_info):
        """
        Prepare data using pre-prepared feast and artwork information from service layer.

        Args:
            date_str: Date string in YYYY-MM-DD format
            feast_info: Pre-prepared feast information from service
            artwork_info: Pre-prepared artwork information from service

        Returns:
            Data dictionary for image generation
        """
        import datetime

        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        friendly_date = date.strftime("%-d %B, %Y")
        info = feast_info
        artwork = (
            artwork_info if artwork_info and artwork_info.get("cached_file") else None
        )
        next_artwork = None
        if not (artwork and artwork.get("cached_file")):
            next_artwork = self.artwork_manager.find_next_artwork(date_str)
        return {
            "date": date,
            "date_str": date_str,
            "friendly_date": friendly_date,
            "info": info,
            "artwork": artwork,
            "next_artwork": next_artwork,
        }

    def _prepare_data(self, date_str):
        """
        Original data preparation method (for backward compatibility).
        """
        import datetime

        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        friendly_date = date.strftime("%-d %B, %Y")
        info = self.feast_service.get_liturgical_info(date_str)
        artwork_candidate = self.artwork_manager.get_artwork_for_date(date_str, info)
        artwork = (
            artwork_candidate
            if artwork_candidate and artwork_candidate.get("cached_file")
            else None
        )
        next_artwork = None
        if not (artwork and artwork.get("cached_file")):
            next_artwork = self.artwork_manager.find_next_artwork(date_str)
        return {
            "date": date,
            "date_str": date_str,
            "friendly_date": friendly_date,
            "info": info,
            "artwork": artwork,
            "next_artwork": next_artwork,
        }

    def _create_layout(self, data):
        # Prepare fonts
        serif_font_36 = self.font_manager.get_font(
            "HappyTimes-Regular.otf", self.header_font_size
        )
        serif_font_96 = self.font_manager.get_font(
            "HappyTimes-Regular.otf", self.title_font_size
        )
        sans_font_36 = self.font_manager.get_font(
            "HankenGrotesk-Medium.ttf", self.column_font_size
        )
        sans_font_36_uc = self.font_manager.get_font(
            "HankenGrotesk-Medium.ttf", self.column_font_size
        )
        fonts = {
            "serif": serif_font_36,
            "serif_96": serif_font_96,
            "sans": sans_font_36,
            "sans_uc": sans_font_36_uc,
            "sans_32": self.font_manager.get_font("HankenGrotesk-Medium.ttf", 32),
            "sans_26": self.font_manager.get_font("HankenGrotesk-Medium.ttf", 26),
        }
        # Header
        season = data["info"].get("season", "").upper()
        date_text = data["friendly_date"]
        header_layout = self.layout_engine.create_header_layout(
            season,
            date_text,
            {"serif": serif_font_36, "sans_uc": sans_font_36_uc},
            self.width,
            self.padding,
            font_manager=self.font_manager,
        )
        baseline_y = header_layout["baseline_y"]
        # Artwork
        art_y = baseline_y + self.row_spacing
        artwork_layout = self.layout_engine.create_artwork_layout(
            data["artwork"],
            data["next_artwork"],
            self.width,
            self.artwork_size,
            art_y,
            fonts={
                "serif": serif_font_36,
                "sans": sans_font_36,
                "sans_32": fonts["sans_32"],
                "sans_26": fonts["sans_26"],
            },
            font_manager=self.font_manager,
        )
        # Title
        if data["artwork"] and data["artwork"].get("name", ""):
            title = data["artwork"].get("name", "")
        else:
            title = data["date"].strftime("%A")
        title = title.replace("：", ":")
        title_y = art_y + self.artwork_size + self.row_spacing
        title_layout = self.layout_engine.create_title_layout(
            title=title,
            fonts={"serif_96": serif_font_96},
            width=self.width,
            padding=self.padding,
            title_font_size=self.title_font_size,
            title_line_height=self.title_line_height,
            start_y=title_y,
            font_manager=self.font_manager,
        )
        last_title_baseline = title_layout["last_baseline"]
        # Readings
        week = data["info"].get("week", "").upper()
        readings = data["info"].get("readings", [])
        if not readings:
            readings = ["No assigned readings for this day."]
        col_y = last_title_baseline + 96 - sans_font_36_uc.getmetrics()[0]
        readings_layout = self.layout_engine.create_readings_layout(
            week=week,
            readings=readings,
            fonts={"serif": serif_font_36, "sans_uc": sans_font_36_uc},
            width=self.width,
            padding=self.padding,
            start_y=col_y,
            line_height=48,
            font_manager=self.font_manager,
        )
        layout = {
            "header": header_layout,
            "artwork": artwork_layout,
            "title": title_layout,
            "readings": readings_layout,
            "colors": {
                "text": self.text_color,
                "line": self.line_color,
            },
        }
        return layout, fonts

    def _render_image(self, layout, fonts, data):
        # Compose the image using the builder
        # Output path is handled in _save_image
        img = self.builder.create_base_image()
        # The builder's build_image expects to save, so we just return the image here for now
        # We'll use build_image for the actual save step
        return img

    def _save_image(self, img, date_str, layout, fonts, data, out_path=None):
        # Use builder to do the full build and save
        build_dir = Path(Settings.BUILD_DIR)
        build_dir.mkdir(exist_ok=True)
        if out_path is None:
            out_path = build_dir / f"liturgical_{date_str}.png"
        self.builder.build_image(
            date_str, data["info"], data["artwork"], layout, fonts, out_path
        )
        return out_path
