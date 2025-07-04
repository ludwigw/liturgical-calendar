# Image Generation

## Overview
- The image generation pipeline creates liturgical calendar images for any date, combining season, feast, readings, and artwork.
- The process is modular, with clear separation between data preparation, layout, and rendering.

## Pipeline Steps
1. **Entry Point**: Script or CLI calls `ImageService.generate_liturgical_image(date_str, output_path)`
2. **Feast & Data Lookup**: `FeastService` and `ArtworkManager` provide liturgical info and artwork.
3. **Pipeline Orchestration**: `ImageGenerationPipeline` prepares data, calculates layout, and renders the image.
4. **Layout Calculation**: `LayoutEngine` computes positions for text, artwork, and readings.
5. **Image Composition**: `ImageBuilder` draws the image, pastes artwork, and saves the file.

## Configuration
- All image settings (size, fonts, colors, padding, etc.) are in `Settings` (see `config.yaml`).
- You can override settings via YAML or environment variables.

## Customization
- To customize layout, fonts, or colors, edit `config.yaml` or extend `LayoutEngine`/`ImageBuilder`.
- For advanced use, subclass pipeline components or provide custom layout functions.

## Example Usage
```python
from liturgical_calendar.services.image_service import ImageService
from liturgical_calendar.config.settings import Settings

Settings.load_from_file('config.yaml')
ImageService.generate_liturgical_image('2025-04-20', output_path='output.png')
```

## See Also
- `docs/architecture.md` for system overview
- `docs/api_reference.md` for class/method details
- `docs/examples/` for runnable scripts 