# Liturgical Calendar Architecture

## Overview

The liturgical calendar project follows a layered architecture with clear separation of concerns:

- **Core Layer**: Low-level business logic (calculations, data management)
- **Service Layer**: High-level orchestration and business logic
- **Pipeline Layer**: Technical implementation and rendering
- **Data Layer**: Pure data storage and access

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

#### readings_data.py
- **Purpose**: Pure readings data storage
- **Content**: Sunday readings, weekday readings, fixed readings

#### artwork_data.py
- **Purpose**: Pure artwork data storage
- **Content**: Artwork dictionaries, source URLs, metadata

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

## Migration Strategy

### Current State
- ImageGenerationPipeline bypasses service layer
- Compatibility methods exist for backward compatibility
- Some orchestration logic is duplicated

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