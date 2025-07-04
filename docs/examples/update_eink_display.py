"""
Minimal e-ink update example: Generate today's image and update the e-ink display.
"""
from liturgical_calendar.services.image_service import ImageService
from liturgical_calendar.config.settings import Settings
from datetime import date
import subprocess

# Load configuration
Settings.load_from_file('config.yaml')

today = date.today().strftime('%Y-%m-%d')
out_path = f"output_eink_{today}.png"

# Generate today's image
ImageService.generate_liturgical_image(today, output_path=out_path)

# (Optional) Convert to 1-bit for e-ink display
try:
    from PIL import Image
    img = Image.open(out_path).convert('1')
    eink_path = f"output_eink_{today}_1bit.png"
    img.save(eink_path)
    out_path = eink_path
except ImportError:
    print("Pillow not installed, skipping 1-bit conversion.")

# Placeholder: Call your e-ink display update command here
# Example: subprocess.run(["python3", "waveshare_epd.py", out_path])
print(f"Image ready for e-ink display: {out_path}")
print("TODO: Insert device-specific update command here.") 