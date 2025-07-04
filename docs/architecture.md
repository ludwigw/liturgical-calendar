# Liturgical Calendar Architecture

## Overview

The liturgical calendar project follows a layered architecture with clear separation of concerns:

- **Core Layer**: Low-level business logic (calculations, data management)
- **Service Layer**: High-level orchestration and business logic
- **Pipeline Layer**: Technical implementation and rendering
- **Data Layer**: Pure data storage and access

See also: api_reference.md for method details, image_generation.md for pipeline, caching.md for cache, testing.md for test structure, and examples/ for runnable code.

## Component Roles

### Core Layer

#### ArtworkManager
- **Purpose**: Low-level artwork selection and management
- **Key Method**: `get_artwork_for_date(date_str, liturgical_info)`
- **Responsibilities**:
  - Artwork lookup by date with liturgical context
  - Cycle-based artwork selection
  - Cached file path management
  - Artwork validation

#### SeasonCalculator
- **Purpose**: Liturgical season and week calculations
- **Key Methods**: `determine_season()`, `calculate_week_number()`, `week_info()`
- **Responsibilities**:
  - Easter-based calculations
  - Season determination
  - Week numbering logic
  - Week name rendering

#### ReadingsManager
- **Purpose**: Liturgical readings management
- **Key Methods**: `get_readings_for_date()`, `get_yearly_cycle()`
- **Responsibilities**:
  - Sunday and weekday readings lookup
  - Cycle management (A, B, C years)
  - Fixed weekday readings for special periods
  - Readings precedence logic

### Service Layer

#### FeastService
- **Purpose**: High-level feast information orchestration
- **Key Method**: `get_complete_feast_info(date_str, transferred=False)`
- **Responsibilities**:
  - Feast lookup and precedence rules
  - Color determination
  - Feast validation
  - Service coordination

#### ImageService
- **Purpose**: High-level image generation orchestration
- **Key Method**: `generate_liturgical_image(date_str, output_path=None, transferred=False)`
- **Responsibilities**:
  - Complete image generation workflow
  - Business logic coordination
  - Error handling and validation
  - Service interface

#### ConfigService
- **Purpose**: Configuration and utility management
- **Key Methods**: `get_season_url()`, `validate_config()`
- **Responsibilities**:
  - Configuration management
  - Utility functions
  - Settings validation

### Pipeline Layer

#### ImageGenerationPipeline
- **Purpose**: Technical image rendering implementation
- **Key Method**: `generate_image(date_str, out_path=None, feast_info=None, artwork_info=None)`
- **Responsibilities**:
  - Image rendering and composition
  - Layout coordination
  - File I/O operations
  - Technical implementation details

See image_generation.md for a detailed breakdown of the image generation process.

#### LayoutEngine
- **Purpose**: Layout calculation and positioning
- **Key Methods**: `create_header_layout()`, `create_artwork_layout()`, `create_title_layout()`, `create_readings_layout()`
- **Responsibilities**:
  - Text positioning and wrapping
  - Layout calculations
  - Font metrics integration

#### ImageBuilder
- **Purpose**: Image composition and drawing
- **Key Methods**: `build_image()`, `paste_artwork()`, `draw_text()`
- **Responsibilities**:
  - Image compositing
  - Text rendering
  - Artwork pasting
  - File saving

#### FontManager
- **Purpose**: Font loading and management
- **Key Methods**: `get_font()`, `get_text_size()`, `get_text_metrics()`
- **Responsibilities**:
  - Font loading and caching
  - Text measurement
  - Font metrics

### Data Layer

#### feasts_data.py
- **Purpose**: Pure feast data storage
- **Content**: Feast dictionaries, precedence rules, liturgical data

See liturgical_logic.md for the rationale and rules behind the data.

#### readings_data.py
- **Purpose**: Pure readings data storage
- **Content**: Sunday readings, weekday readings, fixed readings

#### artwork_data.py
- **Purpose**: Pure artwork data storage
- **Content**: Artwork dictionaries, source URLs, metadata

### Utility Layer

#### ImageProcessor (Planned)
- **Purpose**: Low-level image file operations (download, validate, upsample, optimize)
- **Key Methods**: `download_image()`, `validate_image()`, `upsample_image()`, `optimize_for_web()`, `archive_original()`
- **Used by**: `ArtworkCache`
- **Responsibilities**:
  - Download images from URLs with correct headers
  - Validate image files (format, integrity)
  - Upsample images to required size, archive originals
  - Optimize images for web use (compression, format)
  - Archive original images before upsampling

## Architecture Principles

### 1. Separation of Concerns
- Each component has a single, well-defined responsibility
- Business logic is separated from technical implementation
- Data is separated from logic

### 2. Service Layer Pattern
- Services provide high-level orchestration
- Services coordinate between core components
- Services handle business logic and error handling

### 3. Dependency Injection
- Components receive dependencies through constructor injection
- Enables testing and flexibility
- Reduces tight coupling

### 4. Single Responsibility
- Each class has one reason to change
- Methods have clear, focused purposes
- Components are cohesive and focused

## Data Flow

### Image Generation Flow
```
Script → ImageService.generate_liturgical_image()
  ↓
ImageService → FeastService.get_complete_feast_info()
  ↓
ImageService → ArtworkManager.get_artwork_for_date()
  ↓
ImageService → ImageGenerationPipeline.generate_image()
  ↓
ImageGenerationPipeline → LayoutEngine (layout calculation)
  ↓
ImageGenerationPipeline → ImageBuilder (image composition)
  ↓
ImageBuilder → File System (save image)
```

### Feast Information Flow
```
Script → FeastService.get_complete_feast_info()
  ↓
FeastService → SeasonCalculator.week_info()
  ↓
FeastService → ReadingsManager.get_readings_for_date()
  ↓
FeastService → ArtworkManager.get_artwork_for_date()
  ↓
FeastService → Return complete feast information
```

## Benefits

### Maintainability
- Clear component boundaries
- Single responsibility principle
- Reduced coupling between components

### Testability
- Components can be tested in isolation
- Business logic separated from technical implementation
- Dependency injection enables mocking

### Flexibility
- Components can be swapped or extended independently
- Service layer provides stable interface
- Pipeline can be replaced without affecting business logic

### Clarity
- Clear data flow and responsibilities
- Well-defined interfaces
- Consistent patterns throughout codebase 

## Configuration, Error Handling, and Logging

### Configuration Management

All configuration for the liturgical calendar project is centralized in `liturgical_calendar/config/settings.py`. This includes:

- **Image generation settings:** (width, height, fonts, padding, colors)
- **Caching settings:** (cache directory, max cache size, cleanup policy)
- **API/network settings:** (timeouts, retries, user-agent)
- **Feature toggles:** (enable/disable upsampling, logging level)

**How it works:**
- The `Settings` class (or module-level constants) provides a single source of truth for all configuration.
- All modules import settings from this file, ensuring consistency and easy updates.
- Optionally, settings can be loaded or overridden from a config file (YAML, JSON, or .env) for deployment flexibility.

**Best Practices:**
- Never hardcode values in scripts or services—always use the settings module.
- Document each config option with comments for maintainability.

### Error Handling

Error handling is structured and robust, using custom exception classes defined in `liturgical_calendar/exceptions.py`:

- `LiturgicalCalendarError` (base class)
- `ArtworkNotFoundError`
- `ReadingsNotFoundError`
- `ImageGenerationError`
- `CacheError`
- (Extend as needed for new error types)

**How it works:**
- Code raises specific exceptions for known error conditions (e.g., missing artwork, invalid image, failed download).
- Exceptions are caught and handled at service or CLI boundaries, providing user-friendly messages and clean error reporting.
- Print statements for errors are replaced with logging and/or exception raising.
- Tests assert on specific exceptions for error conditions.

**Best Practices:**
- Raise the most specific exception possible.
- Catch exceptions at the highest level where recovery or user feedback is possible.
- Avoid catching broad exceptions unless re-raising or logging.

### Logging

The project uses a centralized logging system to provide consistent, configurable, and robust logging across all modules and scripts.

### Setup
- Logging is initialized at the entry point of all CLI scripts using `setup_logging()` from `liturgical_calendar.logging`.
- Each module or class obtains a logger via `get_logger(__name__)`.
- Log messages are written to the console by default, with log level and format configurable via the `Settings` class or environment variables.

### Usage in Code
- Use `logger.info()` for key events (e.g., image generation start/completion, cache hits/misses).
- Use `logger.error()` or `logger.exception()` for error reporting and stack traces.
- Avoid `print()` for operational or error messages; use logging instead.
- Example:
  ```python
  from liturgical_calendar.logging import get_logger
  logger = get_logger(__name__)
  logger.info("Starting image generation...")
  try:
      ...
  except Exception as e:
      logger.exception(f"Error: {e}")
  ```

### Configuration
- Logging level, format, and output can be configured via the `Settings` class, YAML config, or environment variables (e.g., `LOG_LEVEL`).
- By default, logs are output to the console. For advanced setups, modify `setup_logging()` in `liturgical_calendar/logging.py`.

### Troubleshooting
- If you do not see log output, ensure `setup_logging()` is called before any logging statements.
- Check the configured log level; set `LOG_LEVEL=DEBUG` for verbose output.
- For issues with log formatting or output, review `liturgical_calendar/logging.py` and your config settings.
- For deployment (e.g., on Raspberry Pi), ensure the user running the script has permission to write logs if you change the output destination.

### CLI/Script Error Reporting

- All CLI scripts (e.g., `create_liturgical_image.py`, `cache_artwork_images.py`) wrap their main entry points in try/except blocks.
- On error, scripts print a user-friendly message and exit with a non-zero code.
- Optionally, a `--verbose` or `--debug` flag can enable more detailed logging output for troubleshooting.

### Configuration Loading

All configuration is centralized in the `Settings` class (`liturgical_calendar/config/settings.py`).

- **Defaults**: All config values have sensible defaults in code.
- **YAML file**: Optionally, a `config.yaml` file can be provided in the project root or specified as an argument to main scripts (e.g., `create_liturgical_image.py`).
- **Environment variables**: Any config value can be overridden by setting an environment variable with the same name.

Main scripts (such as `create_liturgical_image.py`) now call `Settings.load_from_file()` at startup, ensuring config is loaded from file/env if present.

See the README for usage examples and more details.

---

**See also:**  
- `REFACTORING_PLAN.md` Phase 5 for implementation details and migration steps.

## Test Organization

The test suite is organized for clarity and maintainability:

- `tests/unit/`: Unit tests for individual modules/classes (fast, isolated, use mocks/stubs)
- `tests/integration/`: Integration and end-to-end tests (full workflows, real data, script entry points)
- `tests/fixtures/`: Sample data for use in tests

**How to run tests:**
- All tests: `PYTHONPATH=. python -m unittest discover -s tests -p 'test*.py' -v`
- Only unit: `PYTHONPATH=. python -m unittest discover -s tests/unit -p 'test*.py' -v`
- Only integration: `PYTHONPATH=. python -m unittest discover -s tests/integration -p 'test*.py' -v`

**Rationale:**
- Clear separation of test types makes it easy to find, run, and maintain tests.
- Enables targeted testing (e.g., run only fast unit tests during development).
- Fixtures directory supports reusable sample data for robust testing.

See testing.md for test suite structure and commands. 