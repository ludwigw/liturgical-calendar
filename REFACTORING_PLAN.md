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

#### 2.3 Incremental Migration of Main Function Logic (Next Phase)

**Goal**: Gradually move logic from `liturgical_calendar()` function into service layer while maintaining all functionality.

**Current Approach**: Hybrid approach where main function uses service layer components but retains complex orchestration logic.

**Next Steps for Full Service Layer Migration:**

1. **Week/Season Naming Logic Migration**
   - Move week name calculation logic from main function to `FeastService`
   - Handle Sunday vs weekday week naming differences
   - Preserve special cases like "N before Advent" logic
   - Test each migration step to ensure no regressions

2. **Readings Merging Logic Migration**
   - Move feast + weekday readings merging logic to `FeastService`
   - Handle precedence rules for readings selection
   - Preserve complex merging logic for lower precedence feasts
   - Test readings coverage for all liturgical cycles

3. **Color Determination Logic Migration**
   - Move color determination logic from main function to `ImageService`
   - Handle special cases like rose Sundays
   - Preserve feast day vs season color logic
   - Test color accuracy across all liturgical seasons

4. **Season Transition Logic Migration**
   - Move Pre-Lent/Pre-Advent to Ordinary Time conversion to `FeastService`
   - Handle week number normalization logic
   - Preserve edge cases for Christmas and Lent seasons
   - Test season transitions across multiple years

5. **Final Main Function Simplification**
   - Once all logic is migrated, simplify main function to orchestration only
   - Main function becomes thin wrapper around service calls
   - Maintain backward compatibility for existing scripts
   - Comprehensive testing to ensure no functionality loss

**Migration Strategy:**
- **Incremental**: Move one logical block at a time
- **Test-Driven**: Verify each step with existing test suite
- **Backward Compatible**: Maintain existing interfaces throughout
- **Documented**: Update refactoring plan after each completed step

**Success Criteria:**
- All 34 integration tests continue to pass
- All image generation tests continue to pass
- No changes required to existing scripts using `liturgical_calendar()`
- Service layer provides clean, testable interfaces
- Main function becomes simple orchestration layer

### Phase 3: Image Generation Pipeline (Week 3)

#### 3.1 Create Layout Engine
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
1. Extract layout logic from `create_liturgical_image.py`
2. Create unit tests for each layout component
3. Add text wrapping and positioning logic

#### 3.2 Create Font Manager
**File**: `liturgical_calendar/image_generation/font_manager.py`
```python
class FontManager:
    def __init__(self, fonts_dir)
    def get_font(self, font_name, size)
    def get_text_metrics(self, text, font)
    def get_text_size(self, text, font)
```

#### 3.3 Create Image Builder
**File**: `liturgical_calendar/image_generation/image_builder.py`
```python
class LiturgicalImageBuilder:
    def __init__(self, config)
    def build_image(self, date_str, liturgical_info, artwork_info)
    def create_base_image(self, width, height, bg_color)
    def paste_artwork(self, image, artwork_path, position, size)
    def draw_text(self, image, text, position, font, color)
```

#### 3.4 Create Generation Pipeline
**File**: `liturgical_calendar/image_generation/pipeline.py`
```python
class ImageGenerationPipeline:
    def __init__(self, config)
    def generate_image(self, date_str)
    
    def _prepare_data(self, date_str)
    def _create_layout(self, data)
    def _render_image(self, layout)
    def _save_image(self, image, output_path)
```

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
│   ├── test_season_calculator.py ✅
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

## Current Status and Next Steps

### ✅ Completed
- **Phase 1.1**: Core directory structure created
- **Phase 1.2**: SeasonCalculator extracted and integrated with 23 unit tests
- **Phase 1.3**: ReadingsManager extracted and integrated with 22 unit tests
- **Phase 1.4**: ArtworkManager extracted and integrated with 16 unit tests
- **Integration**: All managers successfully integrated into liturgical.py
- **Testing**: All 125 tests passing (34 integration + 16 artwork unit + 75 image generation)
- **Delegation Removal**: All delegation layers removed, direct manager usage throughout

### 🔄 Next Priority: Phase 2 - Data Layer Separation
**Immediate Tasks**:
1. Move feast data from `feasts.py` to `liturgical_calendar/data/feasts_data.py`
2. Move readings data from `readings_data.py` to `liturgical_calendar/data/readings_data.py`
3. Create data validation functions
4. Update all imports to use new data locations
5. Ensure all existing tests continue to pass

**Files to work on**:
- `liturgical_calendar/data/feasts_data.py` (new)
- `liturgical_calendar/data/readings_data.py` (new)
- `liturgical_calendar/feasts.py` (refactor to use new data files)
- `liturgical_calendar/readings_data.py` (refactor to use new data files)
- Update imports in all affected files

**Phase 1 Summary:**
- ✅ All core logic extracted into manager classes
- ✅ All data separated from logic
- ✅ All delegation layers removed
- ✅ Comprehensive test coverage (125 tests)
- ✅ No regressions in functionality
- ✅ Clean, maintainable architecture established

This plan provides a clear roadmap for transforming the codebase into a maintainable, testable, and extensible system while preserving all existing functionality. 