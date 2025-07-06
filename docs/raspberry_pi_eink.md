# Raspberry Pi & E-Ink Integration Guide

## System Requirements
- Raspberry Pi 3 or newer (recommended)
- Raspberry Pi OS (32-bit or 64-bit)
- Python 3.8+
- At least 512MB RAM
- E-ink display (Waveshare or similar) with Python driver

## Installation
1. Update system and install Python dependencies:
   ```sh
   sudo apt-get update
   sudo apt-get install python3-pip python3-pil python3-yaml libjpeg-dev zlib1g-dev libfreetype6-dev
   ```
2. Clone this repo and install Python packages:
   ```sh
   git clone <repo-url>
   cd <repo-dir>
   pip3 install -r requirements.txt
   ```
3. (Optional) Install e-ink display Python library (see your device's docs).

## Running a Basic Example
- Edit `config.yaml` as needed (see sample).
- Run:
   ```sh
   python3 docs/examples/basic_usage.py
   ```
- Check that the output image is created.

## Scheduling Regular Updates
- Use `cron` to run the update script daily:
   ```sh
   crontab -e
   # Add a line like:
   0 6 * * * /usr/bin/python3 /path/to/docs/examples/update_eink_display.py
   ```

## E-Ink Display Notes
- Most e-ink displays require grayscale or 1-bit PNGs. Use config settings to set image size and colors.
- You may need to convert the output image:
   ```python
   from PIL import Image
   img = Image.open('output.png').convert('1')  # 1-bit
   img.save('output_eink.png')
   ```
- Adjust image size in `config.yaml` to match your display (e.g., 800x600).

## Minimal E-Ink Update Example
See `docs/examples/update_eink_display.py` for a script that generates today's image and calls a shell command to update the display.

## Performance Tips
- Use smaller image sizes and avoid upsampling on Pi Zero/older models.
- Limit batch processing to a few images at a time.
- Use lightweight fonts.

## Troubleshooting
- **Pillow install errors:** Install system dependencies as above.
- **Image not displaying:** Check file format, permissions, and device wiring.
- **Slow performance:** Reduce image size, avoid upsampling, and use fewer colors.
- **Font errors:** Ensure fonts are present and paths are correct in config.

## Cross-References
- [README.md](../README.md)
- [docs/examples/update_eink_display.py](examples/update_eink_display.py)
- [docs/api_reference.md](api_reference.md)
- [docs/testing.md](testing.md)
- [docs/image_generation.md](image_generation.md)
- [docs/caching.md](caching.md)
- [docs/liturgical_logic.md](liturgical_logic.md)
