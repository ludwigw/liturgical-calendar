"""
Batch processing example: Generate liturgical images for a range of dates.
"""

from datetime import date, timedelta

from liturgical_calendar.config.settings import Settings
from liturgical_calendar.services.image_service import ImageService

# Load configuration
Settings.load_from_file("config.yaml")

# Generate images for the first week of Lent 2025
start_date = date(2025, 3, 2)  # Lent 1 Sunday
for i in range(7):
    d = start_date + timedelta(days=i)
    out_path = f"output_lent1_{d}.png"
    ImageService.generate_liturgical_image(d.strftime("%Y-%m-%d"), output_path=out_path)
    print(f"Generated: {out_path}")
