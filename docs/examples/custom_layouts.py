"""
Custom layout example: Subclass LayoutEngine to change header color and font size.
"""
from liturgical_calendar.services.image_service import ImageService
from liturgical_calendar.config.settings import Settings
from liturgical_calendar.image_generation.layout_engine import LayoutEngine

class CustomLayoutEngine(LayoutEngine):
    def create_header_layout(self, season, date, fonts, draw, width, padding, font_manager=None):
        layout = super().create_header_layout(season, date, fonts, draw, width, padding, font_manager)
        # Change header color and font size (example)
        layout['season']['font'] = fonts['serif_96']  # Use a larger font
        layout['season']['color'] = (0, 100, 200)     # Custom blue
        return layout

# Use the custom layout engine in the pipeline
Settings.load_from_file('config.yaml')

# Patch the pipeline to use the custom layout engine
from liturgical_calendar.image_generation.pipeline import ImageGenerationPipeline

class CustomPipeline(ImageGenerationPipeline):
    def __init__(self, config):
        super().__init__(config)
        self.layout_engine = CustomLayoutEngine()

# Generate an image with the custom layout
pipeline = CustomPipeline(Settings)
pipeline.generate_image('2025-12-25', out_path='output_christmas_custom.png')

print("Custom layout image generated: output_christmas_custom.png")
