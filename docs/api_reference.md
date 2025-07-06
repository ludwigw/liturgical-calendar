# API Reference

## Core Classes

### SeasonCalculator
- `determine_season(date, easter_point, christmas_point, advent_sunday)`
  - **Description:** Determines the liturgical season (e.g., Lent, Easter, Advent) for a given date, based on its relationship to Easter, Christmas, and Advent Sunday.
  - **Parameters:**
    - `date` (datetime/date): The date to check
    - `easter_point` (int): Days from Easter
    - `christmas_point` (int): Days from Christmas
    - `advent_sunday` (date): Date of Advent Sunday
- `calculate_week_number(date, easter_point, christmas_point, advent_sunday, dayofweek)`
  - **Description:** Calculates the week number within the current liturgical season for a given date.
  - **Parameters:**
    - `date` (datetime/date)
    - `easter_point` (int)
    - `christmas_point` (int)
    - `advent_sunday` (date)
    - `dayofweek` (int): Day of week (0=Sunday, 6=Saturday)
- `calculate_weekday_reading(date, easter_point, christmas_point, advent_sunday)`
  - **Description:** Determines which weekday reading key (e.g., "Trinity 2") applies for a given date.
  - **Parameters:**
    - `date` (datetime/date)
    - `easter_point` (int)
    - `christmas_point` (int)
    - `advent_sunday` (date)
- `render_week_name(season, weekno, easter_point)`
  - **Description:** Returns the display name for the week (e.g., "Proper 7", "Lent 1") based on the season, week number, and Easter point.
  - **Parameters:**
    - `season` (str)
    - `weekno` (int)
    - `easter_point` (int)

### ReadingsManager
- `get_sunday_readings(week, cycle)`
  - **Description:** Returns the list of Sunday readings for a given week and lectionary cycle (A/B/C).
  - **Parameters:**
    - `week` (str): Week name (e.g., "Proper 7")
    - `cycle` (str): "A", "B", or "C"
- `get_weekday_readings(weekday_reading, cycle)`
  - **Description:** Returns the list of weekday readings for a given weekday reading key and cycle (1/2).
  - **Parameters:**
    - `weekday_reading` (str): e.g., "Trinity 2"
    - `cycle` (str): "1" or "2"
- `get_feast_readings(feast_data)`
  - **Description:** Returns the readings assigned to a specific feast, if any.
  - **Parameters:**
    - `feast_data` (dict): Feast information
- `get_readings_for_date(date_str, liturgical_info)`
  - **Description:** Returns the readings for a specific date, using all available context (feast, week, cycle, etc.).
  - **Parameters:**
    - `date_str` (str): "YYYY-MM-DD"
    - `liturgical_info` (dict): Info about the date's season, week, feast, etc.

### ArtworkManager
- `lookup_feast_artwork(relative_to, pointer, cycle_index=0)`
  - **Description:** Looks up the artwork entry for a given feast key (season, pointer, and cycle).
  - **Parameters:**
    - `relative_to` (str): "easter" or "christmas"
    - `pointer` (int/str): Offset or date key
    - `cycle_index` (int): Which artwork to select if multiple (default 0)
- `get_artwork_for_date(date_str, liturgical_info=None)`
  - **Description:** Returns the artwork entry for a specific date, using liturgical context if provided.
  - **Parameters:**
    - `date_str` (str): "YYYY-MM-DD"
    - `liturgical_info` (dict, optional)
- `find_squashed_artworks()`
  - **Description:** Finds artwork entries that are never selected due to precedence rules (for debugging/cleanup).
  - **Parameters:** None
- `get_cached_artwork_path(source_url)`
  - **Description:** Returns the cache file path for a given artwork source URL.
  - **Parameters:**
    - `source_url` (str)
- `validate_artwork_data(artwork_entry)`
  - **Description:** Checks if an artwork entry is valid (has required fields).
  - **Parameters:**
    - `artwork_entry` (dict)

## Service Layer

### FeastService
- `get_complete_feast_info(date_str, transferred=False)`
  - **Description:** Returns all liturgical info for a date (season, week, feast, readings, color, etc.).
  - **Parameters:**
    - `date_str` (str): "YYYY-MM-DD"
    - `transferred` (bool, optional): If transferred feasts should be considered
- `validate_feast_data(feast_data)`
  - **Description:** Checks if feast data has required fields.
  - **Parameters:**
    - `feast_data` (dict)
- `get_possible_feasts(...)`
  - **Description:** Returns all possible feasts for a date (advanced/edge use).
  - **Parameters:**
    - Multiple parameters (see code for full signature)
- `get_highest_priority_feast(possibles, transferred)`
  - **Description:** Returns the highest-priority feast from a list.
  - **Parameters:**
    - `possibles` (list of dicts)
    - `transferred` (bool)
- `get_liturgical_info(date_str)`
  - **Description:** Returns liturgical info for a date (alias for `get_complete_feast_info`).
  - **Parameters:**
    - `date_str` (str): "YYYY-MM-DD"

### ImageService
- `generate_liturgical_image(date_str, output_path=None, transferred=False)`
  - **Description:** Generates and saves a liturgical image for a date.
  - **Parameters:**
    - `date_str` (str): "YYYY-MM-DD"
    - `output_path` (str, optional): Where to save the image
    - `transferred` (bool, optional)
- `validate_image_data(image_data)`
  - **Description:** Checks if image data has required fields.
  - **Parameters:**
    - `image_data` (dict)
- `get_image_generation_stats(results)`
  - **Description:** Returns statistics about a batch of image generation results.
  - **Parameters:**
    - `results` (list of dicts)
- `get_artwork_for_date(date_str, feast_info=None)`
  - **Description:** Returns artwork info for a date, optionally using feast info.
  - **Parameters:**
    - `date_str` (str): "YYYY-MM-DD"
    - `feast_info` (dict, optional)

### ConfigService
- `get_artwork_settings()`
  - **Description:** Returns artwork-related config settings.
  - **Parameters:** None
- `get_readings_settings()`
  - **Description:** Returns readings-related config settings.
  - **Parameters:** None
- `get_output_settings()`
  - **Description:** Returns output-related config settings.
  - **Parameters:** None
- `validate_config()`
  - **Description:** Validates the current configuration.
  - **Parameters:** None

## Pipeline Layer

### ImageGenerationPipeline
- `generate_image(date_str, out_path=None, feast_info=None, artwork_info=None)`
  - **Description:** Orchestrates the full image generation process for a date.
  - **Parameters:**
    - `date_str` (str): "YYYY-MM-DD"
    - `out_path` (str, optional)
    - `feast_info` (dict, optional)
    - `artwork_info` (dict, optional)

### LayoutEngine
- `create_header_layout(season, date, fonts, draw, width, padding, font_manager=None)`
  - **Description:** Calculates layout for the header row (season, date).
  - **Parameters:**
    - `season` (str)
    - `date` (str)
    - `fonts` (dict)
    - `draw` (drawing context)
    - `width` (int)
    - `padding` (int)
    - `font_manager` (optional)
- `create_artwork_layout(artwork, next_artwork, width, art_size, y, fonts=None, next_title_y_offset=16, draw=None, font_manager=None)`
  - **Description:** Calculates layout for the main and next artwork.
  - **Parameters:**
    - `artwork` (dict)
    - `next_artwork` (dict)
    - `width` (int)
    - `art_size` (int)
    - `y` (int)
    - `fonts` (dict, optional)
    - `next_title_y_offset` (int, optional)
    - `draw` (drawing context, optional)
    - `font_manager` (optional)
- `create_title_layout(title, fonts, draw, width, padding, title_font_size, title_line_height, start_y, font_manager=None)`
  - **Description:** Calculates layout for the title text.
  - **Parameters:**
    - `title` (str)
    - `fonts` (dict)
    - `draw` (drawing context)
    - `width` (int)
    - `padding` (int)
    - `title_font_size` (int)
    - `title_line_height` (float)
    - `start_y` (int)
    - `font_manager` (optional)
- `create_readings_layout(week, readings, fonts, draw, width, padding, start_y, line_height, font_manager=None)`
  - **Description:** Calculates layout for the readings section.
  - **Parameters:**
    - `week` (str)
    - `readings` (list of str)
    - `fonts` (dict)
    - `draw` (drawing context)
    - `width` (int)
    - `padding` (int)
    - `start_y` (int)
    - `line_height` (int)
    - `font_manager` (optional)

### ImageBuilder (LiturgicalImageBuilder)
- `build_image(date_str, liturgical_info, artwork_info, layout, fonts, out_path)`
  - **Description:** Orchestrates the full image build and saves the file.
  - **Parameters:**
    - `date_str` (str)
    - `liturgical_info` (dict)
    - `artwork_info` (dict)
    - `layout` (dict)
    - `fonts` (dict)
    - `out_path` (str)
- `create_base_image()`
  - **Description:** Creates a blank base image with the configured size and background color.
  - **Parameters:** None
- `paste_artwork(img, art_path, pos, size)`
  - **Description:** Pastes an artwork image onto the base image at the given position and size.
  - **Parameters:**
    - `img` (PIL.Image)
    - `art_path` (str)
    - `pos` (tuple)
    - `size` (tuple)
- `draw_text(img, text, pos, font, color)`
  - **Description:** Draws text onto the image at the given position, font, and color.
  - **Parameters:**
    - `img` (PIL.Image)
    - `text` (str)
    - `pos` (tuple)
    - `font` (PIL.ImageFont)
    - `color` (tuple or str)

### FontManager
- `get_font(font_name, size)`
  - **Description:** Loads and returns a font object by name and size.
  - **Parameters:**
    - `font_name` (str)
    - `size` (int)
- `get_text_metrics(font)`
  - **Description:** Returns font metrics (ascent, descent).
  - **Parameters:**
    - `font` (PIL.ImageFont)
- `get_text_size(text, font)`
  - **Description:** Returns the width and height of the given text in the given font.
  - **Parameters:**
    - `text` (str)
    - `font` (PIL.ImageFont)

## Caching

### ArtworkCache
- `download_and_cache_artwork(url, feast_info)`
  - **Description:** Downloads and caches an artwork image for a feast.
  - **Parameters:**
    - `url` (str)
    - `feast_info` (dict)
- `validate_cache()`
  - **Description:** Checks the cache for missing or invalid files.
  - **Parameters:** None
- `cleanup_old_cache()`
  - **Description:** Removes old files from the cache based on age/config.
  - **Parameters:** None
- `get_cache_info()`
  - **Description:** Returns information about the current cache contents.
  - **Parameters:** None

### ImageProcessor
- `download_image(url, out_path)`
  - **Description:** Downloads an image from a URL to a local path.
  - **Parameters:**
    - `url` (str)
    - `out_path` (str)
- `validate_image(path)`
  - **Description:** Checks if an image file is valid and readable.
  - **Parameters:**
    - `path` (str)
- `upsample_image(path, target_size)`
  - **Description:** Upsamples an image to the target size.
  - **Parameters:**
    - `path` (str)
    - `target_size` (tuple or int)
- `archive_original(path)`
  - **Description:** Archives the original image before upsampling.
  - **Parameters:**
    - `path` (str)

## Usage

- For detailed usage and examples, see `docs/examples/` and the respective module docstrings.
- For architectural context, see `docs/architecture.md`.
- For logic and edge cases, see `docs/liturgical_logic.md`.

(Work in progress)
