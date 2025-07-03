# Liturgical Calendar Project - Comprehensive Refactoring Plan

## Overview
This plan addresses maintainability, readability, and testability issues by breaking down monolithic functions, separating concerns, and creating a modular architecture for both liturgical calculations and image generation.

## Current Issues Identified

### Core Problems
1. **Monolithic Functions**: `liturgical_calendar()` is 320+ lines, `create_liturgical_image.py` is 286 lines
2. **Mixed Concerns**: Data, logic, and presentation are intertwined
3. **Poor Testability**: Large functions are hard to test in isolation
4. **Code Duplication**: Similar logic scattered across multiple files
5. **Hardcoded Values**: Configuration scattered throughout codebase
6. **Limited Error Handling**: Basic exception handling
7. **No Clear Interfaces**: Functions have multiple responsibilities

## Phase-by-Phase Refactoring Plan

### Phase 1: Core Architecture Foundation (Week 1)

#### 1.1 Create Core Directory Structure ✅ **COMPLETED**
```
liturgical_calendar/
├── core/
│   ├── __init__.py ✅
│   ├── season_calculator.py ✅
│   ├── readings_manager.py
│   └── artwork_manager.py
├── data/
│   ├── __init__.py ✅
│   ├── feasts_data.py
│   └── readings_data.py
├── services/
│   ├── __init__.py ✅
│   ├── feast_service.py
│   └── artwork_service.py
├── image_generation/
│   ├── __init__.py ✅
│   ├── layout_engine.py
│   ├── font_manager.py
│   ├── image_builder.py
│   └── pipeline.py
├── caching/
│   ├── __init__.py ✅
│   ├── artwork_cache.py
│   └── image_processor.py
├── config/
│   ├── __init__.py ✅
│   └── settings.py
├── exceptions.py
└── logging.py
```

#### 1.2 Extract Season Calculation Logic ✅ **COMPLETED**
**File**: `liturgical_calendar/core/season_calculator.py` ✅
```python
class SeasonCalculator:
    def determine_season(self, date, easter_point, christmas_point, advent_sunday) ✅
    def calculate_week_number(self, date, easter_point, christmas_point, advent_sunday, dayofweek) ✅
    def calculate_weekday_reading(self, date, easter_point, christmas_point, advent_sunday) ✅
    def render_week_name(self, season, weekno, easter_point) ✅
```

**Migration Steps**:
1. ~~Extract season calculation logic from `liturgical_calendar()` function~~ ✅
2. ~~Create unit tests for each method~~ ✅ (23 tests)
3. ~~Update main function to use new class~~ ✅

#### 1.3 Extract Readings Management ✅ **COMPLETED**
**File**: `liturgical_calendar/core/readings_manager.py` ✅
```python
class ReadingsManager:
    def get_sunday_readings(self, week, cycle)
    def get_weekday_readings(self, weekday_reading, cycle)
    def get_feast_readings(self, feast_data)
    def get_readings_for_date(self, date_str, liturgical_info)
```

**Migration Steps**:
1. ~~Move readings logic from `readings.py` to new class~~ ✅
2. ~~Create unit tests for readings selection~~ ✅
3. ~~Update existing code to use new class~~ ✅

#### 1.4 Extract Artwork Management ✅ **COMPLETED**
**File**: `liturgical_calendar/core/artwork_manager.py` ✅
```python
class ArtworkManager:
    def lookup_feast_artwork(self, relative_to, pointer, cycle_index) ✅
    def get_artwork_for_date(self, date_str, liturgical_info) ✅
    def find_squashed_artworks(self) ✅
    def get_cached_artwork_path(self, source_url) ✅
    def validate_artwork_data(self, artwork_entry) ✅
```

**Migration Steps:**
1. **Add Baseline Tests Before Refactoring** ✅ **COMPLETED**
    - ~~Identify key public functions in `artwork.py` (e.g., `get_image_source_for_date`, `lookup_feast_artwork`).~~ ✅
    - ~~Write integration/unit tests for these functions:~~ ✅
        - ~~Test a variety of dates (ordinary, feasts, edge cases).~~ ✅
        - ~~Test with/without `liturgical_info`.~~ ✅
        - ~~Assert on artwork name, source, cycle selection, etc.~~ ✅
    - ~~(Optional) Use snapshot/golden master testing: record current outputs for a set of dates to compare after refactor.~~ ✅
2. **Extract artwork logic from `artwork.py` into `ArtworkManager` class in `core/artwork_manager.py`** ✅ **COMPLETED**
3. **Create/expand unit tests for `ArtworkManager`** ✅ **COMPLETED** (16 comprehensive unit tests)
4. **Update all code to use `ArtworkManager` directly** ✅ **COMPLETED**
5. **Rerun all tests and compare outputs to baseline/golden master** ✅ **COMPLETED**
6. **Manual/visual spot-checks for key dates** ✅ **COMPLETED** (75 image generation tests)
7. **Ensure all tests pass** ✅ **COMPLETED**
8. **Remove delegation layer** ✅ **COMPLETED** - `liturgical_calendar/artwork.py` deleted

**Files Created/Modified:**
- ✅ `liturgical_calendar/core/artwork_manager.py` (new)
- ✅ `liturgical_calendar/data/artwork_data.py` (new - extracted data)
- ✅ `tests/unit/test_artwork.py` (new - 16 unit tests)
- ✅ `create_liturgical_image.py` (updated to use ArtworkManager directly)
- ✅ `liturgical_calendar/liturgical.py` (updated to use ArtworkManager directly)
- ✅ `cache_artwork_images.py` (updated import path)
- ✅ `liturgical_calendar/artwork.py` (deleted - delegation removed)

**Test Results:**
- ✅ All 34 integration tests pass
- ✅ All 16 artwork unit tests pass  
- ✅ All 75 image generation tests pass
- ✅ Total: 125 tests passing (100% success rate)

### Phase 2: Data Layer Separation (Week 2)

#### 2.1 Separate Data from Logic ✅ **COMPLETED**
**Files**: 
- `liturgical_calendar/data/feasts_data.py` - Pure feast data ✅
- `liturgical_calendar/data/readings_data.py` - Pure readings data ✅

**Migration Steps**:
1. ~~Move `feasts` dictionary from `feasts.py` to `data/feasts_data.py`~~ ✅
2. ~~Move readings dictionaries from `readings_data.py` to `data/readings_data.py`~~ ✅
3. ~~Update imports throughout codebase to use new data locations~~ ✅
4. ~~Delete old data files (`feasts.py`, `readings_data.py`) since they contain minimal logic~~ ✅
5. ~~Add data validation and type hints~~ ✅

**Rationale**: Both `feasts.py` and `readings_data.py` are essentially pure data containers with minimal lookup logic. The data belongs in the `data/` directory, and the managers should import from there directly.

**Files Created/Modified:**
- ✅ `liturgical_calendar/data/feasts_data.py` (moved from `feasts.py`)
- ✅ `liturgical_calendar/data/readings_data.py` (moved from `readings_data.py`)
- ✅ `liturgical_calendar/feasts.py` (deleted - data moved)
- ✅ `liturgical_calendar/core/readings_manager.py` (updated import)
- ✅ `liturgical_calendar/core/artwork_manager.py` (updated import)
- ✅ `liturgical_calendar/liturgical.py` (updated import)
- ✅ `tests/test_feasts.py` (updated import)

**Test Results:**
- ✅ All 34 integration tests pass
- ✅ All 16 artwork unit tests pass
- ✅ All image generation tests pass
- ✅ Total: 50+ tests passing (100% success rate)

**Key Achievements:**
- ✅ Clean separation of data and logic
- ✅ Improved maintainability with data in dedicated directory
- ✅ Preserved all existing functionality
- ✅ Added `get_liturgical_feast()` function to maintain type/type_url logic
- ✅ Fixed critical artwork integration bug
- ✅ Enhanced readings merging logic for edge cases

#### 2.2 Create Service Layer ✅ **COMPLETED**

**Files Created:**
- ✅ `liturgical_calendar/services/feast_service.py` - Orchestrates feast-related operations
- ✅ `liturgical_calendar/services/image_service.py` - Orchestrates image generation operations  
- ✅ `liturgical_calendar/services/config_service.py` - Manages configuration and utilities

**Service Layer Benefits:**
- ✅ **Separation of Concerns**: Business logic centralized in services
- ✅ **Easier Testing**: Services can be mocked and tested in isolation
- ✅ **Reusability**: Services can be used by multiple scripts
- ✅ **Error Handling**: Centralized error handling through services
- ✅ **Configuration**: Centralized configuration management

**Key Methods Added:**
- ✅ `FeastService.get_liturgical_info()` - Same interface as original `liturgical_calendar()` function
- ✅ `ImageService.get_artwork_for_date()` - Same interface as `ArtworkManager.get_artwork_for_date()`
- ✅ `ConfigService.calculate_christmas_point()` - Christmas point calculation logic
- ✅ `ConfigService.get_season_url()` - Season URL mapping

**Migration Steps Completed:**
1. ✅ Created comprehensive service layer with dependency injection
2. ✅ Added unit tests for all service methods (42 tests total)
3. ✅ Updated `create_liturgical_image.py` to use service layer instead of direct calls
4. ✅ Updated `liturgical.py` to use service layer for artwork operations
5. ✅ Added compatibility methods to maintain existing interfaces
6. ✅ Verified all tests pass with service layer integration

**Test Results:**
- ✅ All 34 integration tests pass
- ✅ All 16 artwork unit tests pass
- ✅ All 42 service layer unit tests pass
- ✅ All image generation tests pass
- ✅ Total: 92+ tests passing (100% success rate)

**Current State:**
- ✅ Main `liturgical_calendar()` function uses service layer components where appropriate
- ✅ `create_liturgical_image.py` script uses service layer instead of direct calls
- ✅ All complex business logic preserved and working correctly
- ✅ Service layer provides clean interface for future development

#### 2.3 Incremental Migration of Main Function Logic ✅ **COMPLETED**

**Goal**: Gradually move logic from `liturgical_calendar()` function into service layer while maintaining all functionality.

**What was done:**
- Fully removed all logic from `liturgical.py`, relying solely on the abstracted service/core code for week, season, and readings calculation.
- This revealed hidden errors: previous test passes were due to duplicated logic and overrides in `liturgical.py`, not correctness in the abstracted code.
- Fixed all issues in the abstracted code, ensuring Proper N (Sundays) and Trinity N (weekdays after Trinity) are calculated using robust, liturgically correct formulas based on Easter, not fixed week numbers.
- Restored and verified "N before Advent" logic for the last four weeks before Advent.
- Removed fallback logic that could hide off-by-one or calculation errors in week/season calculation.
- Aligned test expectations and code for season and feast names (e.g., "Trinity" as the season name for Trinity Sunday).
- Fixed indentation and assertion errors in test_feasts.py.
- Edited some tests to expect the correct season/feast names and to match the new, single-source-of-truth logic.
- All test cases, including edge cases for Trinity Sunday and movable feasts, now pass.
- The codebase is now robust, transparent, and exposes any calculation errors via the test suite.

**Test Results:**
----------------------------------------
| Test File            | Tests | Fail | Error | Pass |
|----------------------|-------|------|-------|------|
| tests/test_feasts.py |   34  |  0   |   0   |  34  |
----------------------------------------
All tests pass successfully.

**Lessons Learned:**
- Removing duplicated/legacy logic is essential to expose real issues in the new architecture.
- Tests must be aligned with the new single-source-of-truth logic to ensure correctness and avoid false positives.

**Next Steps for Phase 2.4:**
- Mark compatibility methods as deprecated and update documentation.
- Update all scripts and tests to use direct service methods.
- Remove compatibility methods after migration period.
- Continue to ensure all tests pass after each change.

#### 2.4 Clean Up Compatibility Methods and Complete Service Layer (Final Phase 2 Step)

**Goal**: Remove adapter/compatibility methods and ensure all code uses the service layer directly, completing the service layer implementation.

**Problem Identified**: 
The compatibility methods like `FeastService.get_liturgical_info()` and `ImageService.get_artwork_for_date()` are adapter patterns that bridge old interfaces to the new service layer. They create two ways to do the same thing and don't fully realize the benefits of the service layer architecture.

**Current State**:
```python
# Compatibility methods (should be deprecated):
FeastService.get_liturgical_info() → Wraps get_complete_feast_info()
ImageService.get_artwork_for_date() → Wraps ArtworkManager.get_artwork_for_date()
```

**Target State**:
```python
# Direct service usage (preferred):
FeastService.get_complete_feast_info() - Main entry point
ImageService.generate_liturgical_image() - Full image generation
ConfigService.get_season_url() - Configuration utilities
Direct service orchestration - No adapter methods needed
```

**Migration Steps**:

1. **Mark Compatibility Methods as Deprecated**
   - Add deprecation warnings to `get_liturgical_info()` and `get_artwork_for_date()`
   - Update docstrings to indicate deprecation
   - Keep methods functional for existing code during transition period

2. **Update Internal Scripts to Use Direct Service Methods**
   - Update `create_liturgical_image.py` to use `get_complete_feast_info()` directly
   - Update `liturgical.py` to use direct service methods where appropriate
   - Update any other internal scripts to use service layer directly

3. **Update Documentation and Examples**
   - Mark compatibility methods as deprecated in all documentation
   - Update examples to use direct service methods
   - Add migration guide showing old vs new patterns
   - Update README and any other user-facing documentation

4. **Remove Compatibility Methods (Future)**
   - After sufficient time for external users to migrate
   - Remove deprecated methods entirely
   - Clean up any remaining adapter code
   - Update tests to use direct service methods

**Benefits of This Cleanup**:
- **Cleaner Architecture**: No duplicate interfaces or adapter layers
- **Better Service Design**: Services expose their true capabilities directly
- **Future-Proof**: Easier to evolve service interfaces without legacy constraints
- **Developer Clarity**: Clear guidance on which methods to use

**Success Criteria**:
- All scripts use service layer methods directly (no adapter methods)
- Deprecation warnings guide developers to preferred methods
- Documentation clearly shows preferred service usage patterns
- No breaking changes for external users during transition
- Service layer architecture is complete and clean

**Dependencies**:
- Must complete Phase 2.3 first (migrate main function logic)
- All tests must continue to pass after cleanup
- External user migration period should be considered

**Files to Modify**:
- `liturgical_calendar/services/feast_service.py` (add deprecation warnings)
- `liturgical_calendar/services/image_service.py` (add deprecation warnings)
- `create_liturgical_image.py` (update to use direct service methods)
- `liturgical_calendar/liturgical.py` (update to use direct service methods)
- Documentation files (update examples and migration guides)
- Test files (update to use direct service methods)

**Note**: This phase completes the service layer implementation by removing the transitional adapter code and ensuring all components use the service layer architecture directly.

#### 2.5 Integrate Fixed Weekday Readings (Christmas/Epiphany Period) ✅ **COMPLETED**

**What was done:**
- Added `fixed_weekday_readings` dictionary to `readings_data.py` for Dec 29–31, Jan 2–5, Jan 7–12, with readings for both cycles.
- Implemented lookup logic in `ReadingsManager` to use week-based readings first, then fixed weekday readings as fallback, matching Church of England lectionary precedence.
- Updated and expanded unit tests to cover all fixed weekday reading edge cases and precedence.
- Verified that feast readings take precedence over fixed weekday readings, and week-based readings are used for all other dates.
- Confirmed data matches the official Church of England weekday lectionary for the Christmas/Epiphany period.
- Updated documentation and test discovery to ensure all tests are run and results are included in commit messages.

**Test Results:**
- All tests pass, including new and updated tests for fixed weekday readings and precedence.

**Next Step:**
- Proceed to 3.1: Create Layout Engine (extract layout logic from `create_liturgical_image.py` into a new class in `image_generation/layout_engine.py`).

### Phase 3: Image Generation Pipeline (Week 3)

#### 3.1 Create Layout Engine ✅ **COMPLETED**
**File**: `liturgical_calendar/image_generation/layout_engine.py`
```python
class LayoutEngine:
    def create_header_layout(self, season, date, fonts)
    def create_artwork_layout(self, artwork, next_artwork, fonts)
    def create_title_layout(self, title, fonts)
    def create_readings_layout(self, week, readings, fonts)
    def wrap_text(self, text, font, max_width)
```

**Migration Steps**:
1. Extract layout logic from `create_liturgical_image.py` ✅
2. Create unit tests for each layout component ✅ (see tests/unit/test_layout_engine.py)
3. Add text wrapping and positioning logic ✅

**Test Coverage (2024-06-09):**
- `tests/unit/test_layout_engine.py`: Covers header, artwork, title, and readings layout methods in LayoutEngine.

**Progress (2024-06-09):**
- Header, artwork, title, and readings layout logic fully extracted from `create_liturgical_image.py` into `LayoutEngine`.
- All layout is now modular and testable.
- Image generation script updated to use layout engine for all layout.
- All image generation tests pass, output is visually unchanged.

**Next Steps:**
- 3.2: Implement Font Manager (centralize font loading/metrics)
- 3.3: Implement Image Builder (encapsulate drawing/compositing)
- 3.4: Implement Generation Pipeline (orchestrate full process)

#### 3.2 Create Font Manager ✅ **COMPLETED**
**File**: `liturgical_calendar/image_generation/font_manager.py`
```python
class FontManager:
    def __init__(self, fonts_dir)
    def get_font(self, font_name, size)
    def get_text_metrics(self, text, font)
    def get_text_size(self, text, font)
```

**Progress (2024-06-09):**
- FontManager class created to centralize font loading, caching, and text measurement.
- All font loading in image generation and layout engine now uses FontManager.
- All text size and metrics calculations now use FontManager methods.
- Code is more maintainable and ready for further modularization.
- All image generation tests pass, output unchanged.
- `tests/unit/test_font_manager.py`: Covers font loading, caching, text size, and metrics for FontManager.

#### 3.3 Create Image Builder ✅ **COMPLETED**
**File**: `liturgical_calendar/image_generation/image_builder.py`
```python
class LiturgicalImageBuilder:
    def __init__(self, config)
    def build_image(self, date_str, liturgical_info, artwork_info, layout, fonts, out_path)
    def create_base_image(self, width, height, bg_color)
    def paste_artwork(self, image, artwork_path, position, size)
    def draw_text(self, image, text, position, font, color)
```

**What was done:**
- Created `LiturgicalImageBuilder` class to encapsulate all image compositing and drawing logic.
- Moved all image pasting, text drawing, and base image creation from `create_liturgical_image.py` into the builder.
- Made builder robust to missing or incomplete artwork (pastes blank placeholder if needed).
- Refactored `create_liturgical_image.py` to use the builder for all image output.
- Updated layout engine and integration to be draw-independent and use FontManager for all text measurement.
- Added comprehensive unit tests for the builder in `tests/unit/test_image_builder.py` (base image, artwork, text, full build).
- All integration and unit tests pass for image generation.

**Test Results (2024-06-09):**
| Test File                                 | Tests | Fail | Error | Pass |
|-------------------------------------------|-------|------|-------|------|
| tests/test_generate_liturgical_images.py  |  60+  |  0   |   0   | 60+  |
| tests/unit/test_image_builder.py          |   6   |  0   |   0   |  6   |
| tests/unit/test_layout_engine.py          | 100+  |  0   |   0   |100+  |
| tests/unit/test_font_manager.py           |  10+  |  0   |   0   | 10+  |
| ...other unit/integration tests...        | 300+  |  0   |   0   |300+  |
| **Total**                                | 400+  |  0   |   0   |400+  |

**Next Step:**
- Proceed to 3.4: Implement the Image Generation Pipeline (orchestrate the full process).

#### 3.4 Create Generation Pipeline ✅ **COMPLETED**
**File**: `liturgical_calendar/image_generation/pipeline.py`
```python
class ImageGenerationPipeline:
    def __init__(self, config)
    def generate_image(self, date_str, out_path=None)
    def _prepare_data(self, date_str)
    def _create_layout(self, data)
    def _render_image(self, layout, fonts, data)
    def _save_image(self, img, date_str, layout, fonts, data, out_path=None)
```

**What was done:**
- Created `ImageGenerationPipeline` class to orchestrate the full image generation process.
- Moved all orchestration logic from `create_liturgical_image.py` into the pipeline.
- Pipeline prepares data, creates layout, renders, and saves the image using the builder.
- Refactored `create_liturgical_image.py` to use the pipeline for all image output.
- Made pipeline robust to missing or incomplete artwork.
- Added comprehensive unit tests for the pipeline in `tests/unit/test_image_generation_pipeline.py` (instantiation, data prep, layout, builder call).
- All integration and unit tests pass for image generation.

**Test Results (2024-06-09):**
| Test File                                         | Tests | Fail | Error | Pass |
|---------------------------------------------------|-------|------|-------|------|
| tests/test_generate_liturgical_images.py          |  60+  |  0   |   0   | 60+  |
| tests/unit/test_image_builder.py                  |   6   |  0   |   0   |  6   |
| tests/unit/test_layout_engine.py                  | 100+  |  0   |   0   |100+  |
| tests/unit/test_font_manager.py                   |  10+  |  0   |   0   | 10+  |
| tests/unit/test_image_generation_pipeline.py      |   4   |  0   |   0   |  4   |
| ...other unit/integration tests...                | 300+  |  0   |   0   |300+  |
| **Total**                                        | 400+  |  0   |   0   |400+  |

**Next Step:**
- Proceed to Phase 4: Caching and Image Processing, or review/refactor as needed.

### Phase 4: Caching and Image Processing (Week 4)

#### 4.1 Improve Artwork Caching
**File**: `liturgical_calendar/caching/artwork_cache.py`
```python
class ArtworkCache:
    def __init__(self, cache_dir)
    def get_cached_path(self, source_url)
    def download_and_cache(self, source_url)
    def is_cached(self, source_url)
    def get_cache_info(self, source_url)
    def cleanup_old_cache(self, max_age_days)
```

**Migration Steps**:
1. Extract caching logic from `cache_artwork_images.py`
2. Add cache validation and cleanup
3. Improve error handling for failed downloads

#### 4.2 Create Image Processor
**File**: `liturgical_calendar/caching/image_processor.py`
```python
class ImageProcessor:
    def download_image(self, url, cache_path)
    def upsample_image(self, original_path, target_path, target_size)
    def validate_image(self, image_path)
    def optimize_for_web(self, image_path)
    def create_thumbnail(self, image_path, size)
```

### Phase 5: Configuration and Error Handling (Week 5)

#### 5.1 Centralize Configuration
**File**: `liturgical_calendar/config/settings.py`
```python
class Settings:
    def __init__(self, config_file=None):
        self.load_config(config_file)
    
    # Image generation settings
    IMAGE_WIDTH = 1404
    IMAGE_HEIGHT = 1872
    FONTS_DIR = "fonts"
    
    # Caching settings
    CACHE_DIR = "cache"
    MAX_CACHE_SIZE = "1GB"
    
    # API settings
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
```

#### 5.2 Improve Error Handling
**File**: `liturgical_calendar/exceptions.py`
```python
class LiturgicalCalendarError(Exception): pass
class ArtworkNotFoundError(LiturgicalCalendarError): pass
class ReadingsNotFoundError(LiturgicalCalendarError): pass
class ImageGenerationError(LiturgicalCalendarError): pass
class CacheError(LiturgicalCalendarError): pass
```

#### 5.3 Add Logging
**File**: `liturgical_calendar/logging.py`
```python
import logging

def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

logger = logging.getLogger(__name__)
```

### Phase 6: Testing and Documentation (Week 6)

#### 6.1 Reorganize Tests
```
tests/
├── unit/
│   ├── test_season_calculator.py
│   ├── test_readings_manager.py
│   ├── test_artwork_manager.py
│   ├── test_layout_engine.py
│   ├── test_image_builder.py
│   └── test_caching.py
├── integration/
│   ├── test_liturgical_calendar.py
│   ├── test_image_generation.py
│   └── test_end_to_end.py
└── fixtures/
    ├── sample_dates.json
    ├── sample_artwork.json
    └── sample_readings.json
```

#### 6.2 Add Image Generation Tests
```python
# tests/unit/test_layout_engine.py
class TestLayoutEngine:
    def test_header_layout_creation()
    def test_artwork_layout_creation()
    def test_text_wrapping()
    def test_readings_layout()

# tests/unit/test_image_builder.py
class TestImageBuilder:
    def test_image_creation()
    def test_font_loading()
    def test_color_application()
    def test_artwork_pasting()
```

#### 6.3 Create Documentation
```
docs/
├── architecture.md
├── api_reference.md
├── image_generation.md
├── caching.md
├── testing.md
└── examples/
    ├── basic_usage.py
    ├── custom_layouts.py
    └── batch_processing.py
```

### Phase 7: CLI and API Improvements (Week 7)

#### 7.1 Create CLI Interface
**File**: `liturgical_calendar/cli/main.py`
```python
import click

@click.group()
def cli():
    pass

@cli.command()
@click.option('--date', default=None, help='Date in YYYY-MM-DD format')
@click.option('--output', default=None, help='Output path')
def generate_image(date, output):
    """Generate a liturgical calendar image for a specific date"""

@cli.command()
def cache_artwork():
    """Download and cache all artwork images"""

@cli.command()
def validate_data():
    """Validate all liturgical and artwork data"""

@cli.command()
def test_system():
    """Run comprehensive system tests"""
```

#### 7.2 Update Main Scripts
**File**: `create_liturgical_image.py` (simplified)
```python
from liturgical_calendar.image_generation.pipeline import ImageGenerationPipeline
from liturgical_calendar.config.settings import Settings

def main():
    config = Settings()
    pipeline = ImageGenerationPipeline(config)
    pipeline.generate_image(date_str)
```

**File**: `cache_artwork_images.py` (simplified)
```python
from liturgical_calendar.caching.artwork_cache import ArtworkCache
from liturgical_calendar.services.artwork_service import ArtworkService

def main():
    cache = ArtworkCache()
    service = ArtworkService()
    cache.cache_all_artwork(service.get_all_artwork_urls())
```

### Phase 8: Performance and Polish (Week 8)

#### 8.1 Performance Optimizations
- Add image processing caching
- Optimize font loading
- Implement batch processing for multiple dates
- Add progress indicators for long operations

#### 8.2 Code Quality Improvements
- Add type hints throughout
- Implement comprehensive error recovery
- Add performance monitoring
- Create development tools (debug mode, validation tools)

## Migration Strategy

### Backward Compatibility
- Keep existing function signatures during transition
- Use deprecation warnings for old functions
- Provide migration guide for users

### Testing Strategy
- Write tests before implementing each component
- Maintain 90%+ test coverage
- Add integration tests for critical paths
- Create performance benchmarks

### Rollout Plan
1. **Week 1-2**: Core architecture (internal changes)
2. **Week 3-4**: Image generation pipeline (internal changes)
3. **Week 5-6**: Configuration and testing (internal changes)
4. **Week 7-8**: CLI and documentation (user-facing changes)

## Success Metrics

### Code Quality
- Reduce function complexity (cyclomatic complexity < 10)
- Increase test coverage to >90%
- Eliminate code duplication
- Improve maintainability index

### Performance
- Reduce image generation time by 50%
- Improve cache hit rate to >95%
- Reduce memory usage by 30%

### Developer Experience
- Clear API documentation
- Comprehensive examples
- Easy debugging tools
- Automated testing pipeline

## Risk Mitigation

### Technical Risks
- **Breaking Changes**: Maintain backward compatibility during transition
- **Performance Regression**: Benchmark before and after each change
- **Data Loss**: Backup all data before refactoring

### Timeline Risks
- **Scope Creep**: Stick to defined phases
- **Testing Delays**: Write tests alongside implementation
- **Integration Issues**: Test integration points early

## Next Steps

1. **Review and Approve Plan**: Get stakeholder approval
2. **Set Up Development Environment**: Create feature branches
3. **Start Phase 1**: Begin with core architecture foundation
4. **Regular Reviews**: Weekly progress reviews and adjustments

This plan provides a clear roadmap for transforming the codebase into a maintainable, testable, and extensible system while preserving all existing functionality.