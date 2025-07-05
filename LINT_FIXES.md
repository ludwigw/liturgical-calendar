# Lint Fixes Plan

## Overview
This document outlines the plan to fix all pylint issues identified in the GitHub Actions workflow. The goal is to achieve a clean pylint score and ensure consistent code quality.

## Current Status
- **Tests**: ✅ All 42 tests pass
- **Dependencies**: ✅ All packages install correctly
- **CLI**: ✅ All functionality works
- **Pylint**: ❌ Multiple style and quality issues

## Issue Categories and Fix Plan

### Phase 1: Quick Fixes (1-2 hours) - HIGH PRIORITY

#### 1.1 Missing Final Newlines (C0304)
**Files to fix:**
- `liturgical_calendar/logging.py`
- `liturgical_calendar/exceptions.py`
- `liturgical_calendar/data/feasts_data.py`
- `liturgical_calendar/data/artwork_data.py`
- `liturgical_calendar/image_generation/layout_engine.py`
- `liturgical_calendar/image_generation/pipeline.py`
- `liturgical_calendar/image_generation/font_manager.py`
- `liturgical_calendar/image_generation/image_builder.py`
- `liturgical_calendar/core/readings_manager.py`
- `liturgical_calendar/core/season_calculator.py`
- `liturgical_calendar/core/artwork_manager.py`
- `liturgical_calendar/utils/__init__.py`
- `liturgical_calendar/utils/file_system.py`
- `liturgical_calendar/caching/artwork_cache.py`
- `liturgical_calendar/caching/image_processor.py`
- `liturgical_calendar/services/image_service.py`
- `liturgical_calendar/services/feast_service.py`
- `liturgical_calendar/services/config_service.py`

**Action:** Add `\n` at end of each file

#### 1.2 Trailing Whitespace (C0303)
**Files to fix:** All files with trailing whitespace
**Action:** Remove trailing spaces from all lines

#### 1.3 Import Order (C0411)
**Files to fix:**
- `liturgical_calendar/cli.py`
- `liturgical_calendar/image_generation/font_manager.py`
- `liturgical_calendar/image_generation/image_builder.py`
- `liturgical_calendar/core/artwork_manager.py`
- `liturgical_calendar/caching/artwork_cache.py`
- `liturgical_calendar/caching/image_processor.py`
- `liturgical_calendar/services/image_service.py`
- `liturgical_calendar/services/feast_service.py`
- `liturgical_calendar/services/config_service.py`

**Order:** Standard library → Third party → First party → Local imports

#### 1.4 Unused Imports (W0611)
**Files to fix:**
- `liturgical_calendar/cli.py` - Remove unused imports
- `liturgical_calendar/image_generation/image_builder.py` - Remove unused imports
- `liturgical_calendar/core/readings_manager.py` - Remove unused imports
- `liturgical_calendar/core/season_calculator.py` - Remove unused imports
- `liturgical_calendar/caching/artwork_cache.py` - Remove unused imports
- `liturgical_calendar/caching/image_processor.py` - Remove unused imports
- `liturgical_calendar/services/image_service.py` - Remove unused imports
- `liturgical_calendar/services/feast_service.py` - Remove unused imports
- `liturgical_calendar/services/config_service.py` - Remove unused imports

### Phase 2: Medium Effort (3-4 hours) - MEDIUM PRIORITY

#### 2.1 Missing Docstrings (C0114, C0115, C0116)
**Files to fix:**
- `liturgical_calendar/cli.py` - Add module and function docstrings
- `liturgical_calendar/logging.py` - Add module docstring
- `liturgical_calendar/data/readings_data.py` - Add module docstring
- `liturgical_calendar/data/feasts_data.py` - Add module docstring
- `liturgical_calendar/data/artwork_data.py` - Add module docstring
- `liturgical_calendar/image_generation/layout_engine.py` - Add module docstring
- `liturgical_calendar/image_generation/pipeline.py` - Add module and class docstrings
- `liturgical_calendar/image_generation/font_manager.py` - Add module and class docstrings
- `liturgical_calendar/image_generation/image_builder.py` - Add module and class docstrings
- `liturgical_calendar/caching/artwork_cache.py` - Add module and function docstrings
- `liturgical_calendar/caching/image_processor.py` - Add module and function docstrings

#### 2.2 Exception Handling (W0707, W0718)
**Files to fix:**
- `liturgical_calendar/cli.py` - Use specific exceptions, add `from e`
- `liturgical_calendar/caching/artwork_cache.py` - Add `from e` to re-raises
- `liturgical_calendar/caching/image_processor.py` - Add `from e` to re-raises
- `liturgical_calendar/core/readings_manager.py` - Add `from e` to re-raises
- `liturgical_calendar/utils/file_system.py` - Add `from e` to re-raises
- `liturgical_calendar/services/config_service.py` - Add `from e` to re-raises
- `liturgical_calendar/services/image_service.py` - Add `from e` to re-raises

#### 2.3 Unused Variables and Arguments (W0612, W0613)
**Files to fix:**
- `liturgical_calendar/cli.py` - Remove unused variables
- `liturgical_calendar/services/feast_service.py` - Remove unused arguments
- `liturgical_calendar/image_generation/layout_engine.py` - Remove unused arguments
- `liturgical_calendar/image_generation/pipeline.py` - Remove unused arguments
- `liturgical_calendar/image_generation/image_builder.py` - Remove unused arguments
- `liturgical_calendar/caching/artwork_cache.py` - Remove unused arguments
- `liturgical_calendar/caching/image_processor.py` - Remove unused arguments

### Phase 3: Complex Refactoring (6-8 hours) - LOW PRIORITY

#### 3.1 Function Complexity (R0913, R0917)
**Files to fix:**
- `liturgical_calendar/cli.py` - Reduce nested blocks
- `liturgical_calendar/image_generation/layout_engine.py` - Reduce function arguments
- `liturgical_calendar/image_generation/pipeline.py` - Reduce function arguments
- `liturgical_calendar/image_generation/image_builder.py` - Reduce function arguments
- `liturgical_calendar/caching/artwork_cache.py` - Reduce function arguments
- `liturgical_calendar/caching/image_processor.py` - Reduce function arguments
- `liturgical_calendar/services/image_service.py` - Reduce return statements
- `liturgical_calendar/services/feast_service.py` - Reduce function arguments
- `liturgical_calendar/core/season_calculator.py` - Reduce return statements

#### 3.2 Code Duplication (R0801)
**Files to fix:**
- Extract common season URL logic
- Extract common error handling patterns
- Extract common logging patterns

#### 3.3 Other Issues
- `liturgical_calendar/funcs.py` - Fix indentation issues
- `liturgical_calendar/exceptions.py` - Remove unnecessary pass statements
- `liturgical_calendar/data/feasts_data.py` - Fix duplicate dictionary key
- `liturgical_calendar/config/settings.py` - Add encoding to file operations

## Implementation Strategy

### Step 1: Quick Fixes (Start Here)
1. Fix missing final newlines
2. Remove trailing whitespace
3. Fix import order
4. Remove unused imports

### Step 2: Test After Each Phase
- Run `pylint --rcfile=.pylintrc liturgical_calendar` after each phase
- Ensure tests still pass: `python -m unittest discover -s tests -p 'test*.py' -v`
- Commit changes after each phase

### Step 3: Gradual Improvement
- Focus on one category at a time
- Use `autopep8` for automatic formatting where possible
- Manual fixes for complex issues

## Success Criteria
- Pylint score: 8.0+/10
- All tests passing
- No critical issues (C, F, E categories)
- Minimal warnings (W category)

## Tools to Use
- `autopep8` for automatic formatting
- `pylint` for static analysis
- Manual review for complex issues

## Notes
- The code is functionally correct - these are quality/style improvements
- Focus on Phase 1 first for immediate impact
- Phase 2 and 3 can be done incrementally
- Consider using pre-commit hooks to prevent regression 