"""
Basic usage example: Generate a liturgical calendar image for a single date.
"""

from liturgical_calendar.config.settings import Settings
from liturgical_calendar.services.image_service import ImageService

# Load configuration (from YAML or environment variables)
Settings.load_from_file("config.yaml")

# Generate an image for Easter 2025
ImageService.generate_liturgical_image(
    "2025-04-20", output_path="output_easter_2025.png"
)

print("Image generated: output_easter_2025.png")
